"""Regression checks for the ClawHub findings; all network/model calls are mocked."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/value-pricing/scripts'
sys.path.insert(0, str(SCRIPTS))
from common import Study, evaluate_expr, git_sha
import code_features
import kappa
import llm_batch
from crawl_site import Fetcher
from conjoint_fit import Data
from ingest_corpus import read

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = {'segments': {'bands': [{'id': 'a', 'share': .25}, {'id': 'b', 'share': .75}]},
                    'archetypes': [{'id': 'x', 'share': 1}, {'id': 'y', 'share': 3}]}
        self.save()
    def tearDown(self): self.tmp.cleanup()
    def save(self):
        (self.root/'study.yaml').write_text(yaml.safe_dump(self.cfg))
        return Study(self.root)

class Shares(Fixture):
    def test_no_archetypes_preserves_unstratified_value_simulation(self):
        from value_mc import generate
        self.cfg['archetypes']=[]
        self.cfg['scenarios']={'variables': {'quantity': {'dist':'uniform','low':1,'high':2}}}
        st=self.save()
        self.assertEqual(st.archetype_share('a'),{})
        result=generate(st,20,1)
        self.assertEqual(len(result),20)
        self.assertEqual(set(result.archetype),{'generic'})
    def test_valid_explicit_shares(self):
        st=self.save()
        self.assertEqual(st.segment_share(), {'a': .25, 'b': .75})
        self.assertEqual(st.archetype_share('a'), {'x': .25, 'y': .75})
    def test_invalid_segment_shares_never_imputed(self):
        for value in (None, -1, float('nan'), float('inf')):
            with self.subTest(value=value):
                self.cfg['segments']['bands'][0]['share']=value
                with self.assertRaises(ValueError): self.save().segment_share()
    def test_missing_archetype_share(self):
        del self.cfg['archetypes'][0]['share']
        with self.assertRaises(ValueError): self.save().archetype_share('a')
    def test_missing_segment_in_archetype_map(self):
        self.cfg['archetypes'][0]['share']={'a': 1}
        with self.assertRaises(ValueError): self.save().archetype_share('b')
    def test_zero_total_rejected(self):
        for band in self.cfg['segments']['bands']: band['share']=0
        with self.assertRaises(ValueError): self.save().segment_share()

class Coding(Fixture):
    def test_missing_unclear_and_absent_remain_distinct(self):
        (self.root/'taxonomy.yaml').write_text(yaml.safe_dump({'features': [{'id': f} for f in ('yes','no','unclear','omitted')]}))
        d=self.root/'market/coding1'; (d/'responses').mkdir(parents=True)
        pd.DataFrame([{'rid':'one','vendor':'one'},{'rid':'missing','vendor':'missing'}]).to_csv(d/'manifest.csv', index=False)
        (d/'responses/one.json').write_text(json.dumps({'response': {'features': {'yes':1,'no':0,'unclear':'unclear'}}}))
        with patch.object(sys,'argv',['code_features','--study',str(self.root),'collect']), contextlib.redirect_stdout(io.StringIO()): code_features.main()
        result=pd.read_csv(self.root/'market/data/vendor_features.csv').set_index('vendor')
        self.assertEqual(result.loc['one','no'],0)
        self.assertEqual(result.loc['one','yes'],1)
        self.assertTrue(pd.isna(result.loc['one','unclear']))
        self.assertTrue(pd.isna(result.loc['one','omitted']))
        self.assertEqual(result.loc['one','unclear__unclear'],1)
        self.assertEqual(result.loc['missing','yes__missing'],1)
    def test_kappa_excludes_historical_unclear_zero(self):
        d=self.root/'market/data'; d.mkdir(parents=True)
        for name in ('vendor_features.csv','vendor_features2.csv'):
            pd.DataFrame({'vendor':['a','b','c'],'f':[0,1,0],'f__unclear':[1,0,0]}).to_csv(d/name,index=False)
        with patch.object(sys,'argv',['kappa','--study',str(self.root)]),contextlib.redirect_stdout(io.StringIO()): kappa.main()
        result=pd.read_csv(d/'kappa.csv').iloc[0]
        self.assertEqual(result['n'],2); self.assertEqual(result['n_unresolved'],1)

class Execution(Fixture):
    def test_expression_rejects_callable_namespace(self):
        with self.assertRaises(ValueError): evaluate_expr('f()', {'f': lambda: 42})
    def test_positional_numpy_out_cannot_mutate(self):
        x=np.array([2.0])
        with self.assertRaises(ValueError): evaluate_expr('np.clip(x, 0, 1, x)',{'x':x})
        self.assertEqual(x[0],2)
    def test_cli_fixed_args_filtered_environment(self):
        response=SimpleNamespace(returncode=0,stdout=json.dumps({'result':'{}','usage':{}}),stderr='')
        with patch.dict(os.environ,{'UNRELATED_SECRET':'secret','ANTHROPIC_API_KEY':'secret'}),patch('llm_batch.subprocess.run',return_value=response) as run:
            self.assertEqual(llm_batch.call_cli('untrusted $(payload)','system','chosen')[0],'{}')
        args=run.call_args
        self.assertIsInstance(args.args[0],list)
        self.assertNotIn('UNRELATED_SECRET',args.kwargs['env'])
        self.assertNotIn('ANTHROPIC_API_KEY',args.kwargs['env'])
        self.assertNotIn('shell',args.kwargs)
        self.assertEqual(args.kwargs['input'],'untrusted $(payload)')
        self.assertIn('--strict-mcp-config',args.args[0])
    def test_cli_error_is_not_a_success(self):
        with patch('llm_batch.subprocess.run',return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(RuntimeError): llm_batch.call_cli('p','s','m')
    def test_transfer_requires_explicit_confirmation(self):
        with patch.object(sys,'argv',['runner','--dir','panel']),patch('llm_batch.call_api') as api,contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit): llm_batch.main()
        api.assert_not_called()
    def test_paths_cannot_escape(self):
        for name in ('../outside','/etc'):
            with self.assertRaises(ValueError): llm_batch.study_path(self.root,name)
        (self.root/'link').symlink_to('/etc')
        with self.assertRaises(ValueError): llm_batch.confined_path(self.root,'link/passwd')
    def test_decimal_anchor_ids_remain_supported(self):
        self.assertIsNotNone(llm_batch.RID_RE.fullmatch('p001_a12.5_v1'))
    def test_git_provenance_without_subprocess(self):
        g=self.root/'.git'; g.mkdir(); (g/'HEAD').write_text('a'*40)
        self.assertEqual(git_sha(self.root),'a'*40)
        (g/'HEAD').write_text('ref: refs/heads/main')
        (g/'packed-refs').write_text('b'*40+' refs/heads/main\n')
        self.assertEqual(git_sha(self.root),'b'*40)
    def test_plain_text_ingestion(self):
        p=self.root/'sample.txt'; p.write_text('sample')
        self.assertEqual(read(p),'sample')
    def test_conjoint_attribute_names_are_dict_keys(self):
        self.cfg['conjoint']={'attributes':{'price':[10,20],'service-level':['basic','premium']}}
        d=self.root/'panel'; d.mkdir()
        pd.DataFrame([{'version':1,'task':1,'alt':1,'task_type':'random','price_lvl':0,'service-level_lvl':1}]).to_csv(d/'design.csv',index=False)
        data=Data(self.save()); vector,price=data.alt(1,1,1)
        self.assertEqual(vector.tolist(),[1]); self.assertEqual(price,10)

class BrowserPolicy(unittest.TestCase):
    def setUp(self):
        self.fetcher=Fetcher(0,False,'test@example.com'); self.fetcher.origin=('https','example.com',443)
    def tearDown(self): self.fetcher.close()
    def test_every_browser_resource_checks_robots_and_waits(self):
        route=MagicMock(); route.request.url='https://example.com/resource'; route.request.method='GET'
        with patch.object(self.fetcher,'allowed',return_value=True) as allowed,patch.object(self.fetcher,'_wait_for_host') as wait:
            self.fetcher._guard_route(route)
        allowed.assert_called_once_with(route.request.url); wait.assert_called_once(); route.continue_.assert_called_once()
    def test_disallowed_resource_aborted(self):
        route=MagicMock(); route.request.method='GET'
        with patch.object(self.fetcher,'allowed',return_value=False): self.fetcher._guard_route(route)
        route.abort.assert_called_once(); route.continue_.assert_not_called()
    def test_browser_posts_are_blocked(self):
        route=MagicMock(); route.request.method='POST'
        self.fetcher._guard_route(route); route.abort.assert_called_once()
    def test_unknown_robots_policy_fails_closed(self):
        response=SimpleNamespace(status_code=503)
        with patch.object(self.fetcher,'safe_url',return_value=True),patch.object(self.fetcher.s,'get',return_value=response):
            self.assertFalse(self.fetcher.allowed('https://example.com/path'))
    def test_delay_validation(self):
        for delay in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError): Fetcher(delay,False,'test')


class PublishedPayload(Fixture):
    def test_api_preserves_prompt_and_has_no_tools(self):
        reply=SimpleNamespace(content=[SimpleNamespace(type='text',text='{}')],
                              usage=SimpleNamespace(input_tokens=1,output_tokens=1))
        sdk=MagicMock(); sdk.Anthropic.return_value.messages.create.return_value=reply
        with patch.object(llm_batch,'anthropic',sdk):
            text,_=llm_batch.call_api('exact instrument','system','selected-model',.5)
        request=sdk.Anthropic.return_value.messages.create.call_args.kwargs
        self.assertEqual(text,'{}'); self.assertEqual(request['messages'][0]['content'],'exact instrument')
        self.assertNotIn('tools',request)
    def test_pdf_ingestion_without_external_executable(self):
        from pypdf import PdfWriter
        writer=PdfWriter(); writer.add_blank_page(width=72,height=72)
        p=self.root/'sample.pdf'
        with p.open('wb') as f: writer.write(f)
        self.assertEqual(read(p),'')
    def test_text_ingestion_does_not_require_optional_pdf_import(self):
        p=self.root/'sample.txt'; p.write_text('sample')
        with patch('ingest_corpus.PdfReader',None): self.assertEqual(read(p),'sample')
    def test_no_hidden_unicode_controls_or_non_ascii_identifiers(self):
        import tokenize
        import unicodedata
        for path in (ROOT/'skills/value-pricing').rglob('*'):
            if path.is_file() and path.suffix in ('.py','.md','.yaml','.txt','.csv'):
                text=path.read_text()
                self.assertFalse(any(unicodedata.category(c)=='Cf' for c in text),str(path))
                if path.suffix=='.py':
                    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
                        if tok.type==tokenize.NAME: self.assertTrue(tok.string.isascii(),(str(path),tok))
    def test_runtime_metadata_matches_optional_credentials(self):
        meta=yaml.safe_load((ROOT/'skills/value-pricing/SKILL.md').read_text().split('---',2)[1])
        env=meta['metadata']['openclaw']['envVars']
        self.assertEqual({e['name'] for e in env},{'ANTHROPIC_API_KEY','CLAUDE_CONFIG_DIR'})
        self.assertTrue(all(e['required'] is False for e in env))

if __name__=='__main__': unittest.main()

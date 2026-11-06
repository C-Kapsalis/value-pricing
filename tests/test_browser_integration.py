"""Optional real Chromium check against an isolated local HTTP server."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/value-pricing/scripts'))
from crawl_site import Fetcher, web_origin

@unittest.skipUnless(os.environ.get('RUN_PRICING_BROWSER_TESTS')=='1','requires installed Chromium')
class BrowserIntegration(unittest.TestCase):
    def test_browser_subresources_obey_policy(self):
        seen=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self):
                seen.append((self.path,time.monotonic()))
                body = (b'User-agent: *\nDisallow: /blocked\n' if self.path=='/robots.txt' else
                        b'''<html><body>fixture<script>
                        fetch('/one'); fetch('/two'); fetch('/blocked').catch(()=>{});
                        fetch('/post', {method:'POST'}).catch(()=>{});
                        new WebSocket('ws://'+location.host+'/socket');
                        navigator.serviceWorker.register('/worker.js').catch(()=>{});
                        </script></body></html>''' if self.path=='/' else b'ok')
                self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(body)
            def do_POST(self):
                seen.append((self.path,time.monotonic())); self.send_response(200); self.end_headers()
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
        f=Fetcher(.06,True,'test@example.com')
        url=f'http://127.0.0.1:{server.server_port}/'; f.origin=web_origin(url)
        try:
            # The test-only override permits the isolated loopback fixture; production blocks it.
            with patch.object(f,'safe_url',side_effect=lambda u:web_origin(u)==f.origin):
                self.assertTrue(f.allowed(url))
                code,_=f.get(url); self.assertEqual(code,200)
            paths=[p for p,_ in seen]
            self.assertIn('/one',paths); self.assertIn('/two',paths)
            for forbidden in ('/blocked','/post','/socket','/worker.js'): self.assertNotIn(forbidden,paths)
            stamps=[t for _,t in seen]
            self.assertTrue(all(b-a >= .045 for a,b in zip(stamps,stamps[1:])),seen)
        finally:
            f.close(); server.shutdown(); server.server_close()

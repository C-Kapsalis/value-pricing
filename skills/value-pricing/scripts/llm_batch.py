#!/usr/bin/env python3
"""Run a folder of prompts, one isolated LLM call each, idempotently. Used for the panel and feature coding.

Layout under <study>/<dir>/: manifest.csv (a `rid` column, optional `run_order`), prompts/<rid>.txt,
optional system_prompt.txt. Writes responses/<rid>.json = {"rid", "response": <parsed JSON or null>,
"raw", "meta"}; a second failure writes responses/<rid>.failed.json. Re-running skips answered rids.

Runners:
  cli  (default) `claude -p` on the user's Claude plan: no tools, no MCP, no settings, no session
       persistence, a fixed system prompt; ANTHROPIC_API_KEY is stripped so no API spend happens.
       Temperature is not settable here; the model default applies and is recorded.
  api  the Anthropic SDK with ANTHROPIC_API_KEY (only when the owner chose API spend); --temperature applies.
A third route needs no runner: the orchestrating agent dispatches one subagent per prompt and writes
responses/<rid>.json itself in the same shape (costlier per call: the subagent's own context rides along).

--free-text keeps replies that are not JSON (response = null, raw kept): the calibration needs this.

  llm_batch.py --study S --dir panel --workers 6 [--limit 20] [--expect choices,vw,gg] [--runner cli]
Run long batches detached (setsid nohup ... &): a closed session or a tool timeout then can't kill them.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import re
import subprocess
import time

import pandas as pd

from common import Study, study_arg


def parse(text: str):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j + 1])


def call_cli(prompt, system, model):
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
    p = subprocess.run(["claude", "-p", "--model", model, "--output-format", "json", "--tools", "", "--system-prompt", system,
                        "--no-session-persistence", "--setting-sources", "", "--strict-mcp-config"],
                       input=prompt, capture_output=True, text=True, timeout=900, env=env, cwd="/tmp")
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude CLI gave no JSON: {p.stderr[-300:] or p.stdout[-300:]}")
    u = out.get("usage", {})
    meta = {"input_tokens": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
            "output_tokens": u.get("output_tokens", 0), "temperature": "model default"}
    return out["result"], meta


def call_api(prompt, system, model, temperature):
    import anthropic
    r = anthropic.Anthropic().messages.create(model=model, max_tokens=8000, system=system, temperature=temperature,
                                              messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in r.content if b.type == "text"), {"input_tokens": r.usage.input_tokens,
                                                                     "output_tokens": r.usage.output_tokens, "temperature": temperature}


def main():
    ap = study_arg(__doc__.splitlines()[0])
    ap.add_argument("--dir", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model")
    ap.add_argument("--runner", choices=["cli", "api"], default="cli")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--expect", default="", help="comma list of top-level keys a valid JSON reply must have")
    ap.add_argument("--free-text", action="store_true")
    a = ap.parse_args()
    st = Study(a.study)
    d = st.root / a.dir
    model = a.model or st.cfg.get("conjoint", {}).get("model", "claude-opus-5-5")
    resp = d / "responses"
    resp.mkdir(parents=True, exist_ok=True)
    system = (d / "system_prompt.txt").read_text() if (d / "system_prompt.txt").exists() else "Reply with the JSON object requested and nothing else."
    man = pd.read_csv(d / "manifest.csv")
    if "run_order" in man:
        man = man.sort_values("run_order")
    expect = [k for k in a.expect.split(",") if k]

    def done(rid):
        try:
            return "raw" in json.loads((resp / f"{rid}.json").read_text())
        except Exception:
            return False

    def one(rid):
        prompt = (d / "prompts" / f"{rid}.txt").read_text()
        err = ""
        for attempt in (1, 2):
            t0 = time.time()
            try:
                raw, meta = call_cli(prompt, system, model) if a.runner == "cli" else call_api(prompt, system, model, a.temperature)
                try:
                    body = parse(raw)
                except Exception:
                    if not a.free_text:
                        raise
                    body = None
                missing = [k for k in expect if body is None or k not in body]
                if missing and not a.free_text:
                    raise ValueError(f"missing keys {missing}")
                meta.update({"attempt": attempt, "seconds": round(time.time() - t0, 1), "model": model, "runner": a.runner})
                (resp / f"{rid}.json").write_text(json.dumps({"rid": rid, "response": body, "raw": raw, "meta": meta}, ensure_ascii=False, indent=1))
                return rid, True, meta
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:300]}"
                if "limit" in err.lower():
                    time.sleep(120)
        (resp / f"{rid}.failed.json").write_text(json.dumps({"rid": rid, "error": err}, indent=1))
        return rid, False, {"error": err}

    todo = [r for r in man.rid if not done(r)]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(todo)} to run, {len(man) - len(todo)} already answered; model {model}, runner {a.runner}", flush=True)
    tok_in = tok_out = 0
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for k, (rid, ok, meta) in enumerate(ex.map(one, todo), 1):
            tok_in += meta.get("input_tokens", 0)
            tok_out += meta.get("output_tokens", 0)
            if not ok or k % 20 == 0:
                print(f"{k}/{len(todo)} {rid} ok={ok} {meta.get('error', '')}", flush=True)
    print(f"done; tokens in {tok_in:,} out {tok_out:,}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Self-test: run every analysis script on a synthetic study with planted ground truth, and check recovery.

Builds <dir> from templates/ (small settings), plants:
  market   260 vendors, log-price premia ad_platform_connectors +0.50, ai_prescriptive_insights +0.45,
           multi_touch_attribution +0.60; half the vendors scale on monthly_orders with elasticity 0.75
  panel    simulated respondents with known WTP per level (no LLM calls)
then runs value_mc, kappa, hedonic, value_metric, cost_model, conjoint_design, panel_build,
panel_analyze, conjoint_fit (fallback, and HB unless --no-hb), synthesize, optimize_packages, and
reports PASS/FAIL per check. Takes 5–20 minutes depending on the machine (HB is most of it).

  selftest.py [--dir /tmp/value-pricing-selftest] [--no-hb]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
TPL = HERE.parent / "templates"
PLANTED = {"ad_platform_connectors": 0.5, "ai_prescriptive_insights": 0.45, "multi_touch_attribution": 0.6}
ELASTICITY = 0.75
PANEL_WTP = {"sources": 25, "ai_depth": 30, "onboarding": 8, "support": 5}
SEG_K = {"micro": 0.6, "small": 1.0, "mid": 1.6, "large": 2.4}


def run(T, script, *args):
    p = subprocess.run([sys.executable, str(HERE / script), "--study", str(T), *args], capture_output=True, text=True, cwd=HERE)
    if p.returncode:
        raise SystemExit(f"{script} failed:\n{p.stdout[-2000:]}\n{p.stderr[-3000:]}")
    return p.stdout


def build(T: Path):
    if T.exists():
        shutil.rmtree(T)
    (T / "synthesis").mkdir(parents=True)
    for f in ("study.yaml", "value_drivers.yaml", "taxonomy.yaml", "costs.yaml"):
        shutil.copy(TPL / f, T / f)
    shutil.copy(TPL / "proposals.yaml", T / "synthesis/proposals.yaml")
    cfg = yaml.safe_load((T / "study.yaml").read_text())
    cfg["conjoint"].update(versions=6, personas_per_segment=12, min_personas_per_archetype=2)
    cfg["scenarios"]["n"] = 3000
    (T / "study.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
    fids = [f["id"] for f in yaml.safe_load((T / "taxonomy.yaml").read_text())["features"]]
    rng = np.random.default_rng(1)
    V, P, F = [], [], []
    for i in range(260):
        v, tier = f"vendor{i}.com", ("direct" if rng.random() < 0.3 else "adjacent")
        f = {k: int(rng.random() < 0.35) for k in fids}
        base = np.log(30) + sum(PLANTED.get(k, 0) * x for k, x in f.items()) + 0.2 * (tier == "direct") + rng.normal(0, 0.6)
        priced, scales = rng.random() < 0.8, rng.random() < 0.5
        V.append({"vendor": v, "url": f"https://{v}", "tier": tier, "category": rng.choice(["ecom analytics", "bi", "attribution"]),
                  "target_customer": rng.choice(["smb", "mid", "enterprise"]), "ctl_log_popularity": rng.normal(5, 1)})
        F.append({"vendor": v, **f})
        for j, (lim, seat) in enumerate([(500, 1), (3000, 5), (15000, 20)]):
            price = np.exp(base) * (lim / 3000) ** (ELASTICITY if scales else 0) * (1 + 0.4 * j * (not scales))
            P.append({"vendor": v, "plan": f"t{j}", "price": round(price) if priced else None, "currency": "USD", "period": "month",
                      "is_recommended": int(j == 1 and rng.random() < 0.5), "is_free": 0, "is_quote": int(not priced),
                      "limit_seats": None if scales else seat, "limit_sources": None, "limit_monthly_orders": lim if scales else None})
    V.append({"vendor": "__ours__", "url": "https://example.com", "tier": "direct", "category": "ecom analytics", "target_customer": "smb", "ctl_log_popularity": 4.8})
    (T / "market/data").mkdir(parents=True)
    pd.DataFrame(V).to_csv(T / "market/data/vendors.csv", index=False)
    pd.DataFrame(P).to_csv(T / "market/data/plans.csv", index=False)
    pd.DataFrame(F).to_csv(T / "market/data/vendor_features.csv", index=False)
    F2 = pd.DataFrame(F)
    for c in fids:
        flip = rng.random(len(F2)) < 0.05
        F2.loc[flip, c] = 1 - F2.loc[flip, c]
    F2.sample(120, random_state=1).to_csv(T / "market/data/vendor_features2.csv", index=False)


def simulate_panel(T: Path):
    cfg = yaml.safe_load((T / "study.yaml").read_text())["conjoint"]
    A, names = cfg["attributes"], list(cfg["attributes"])
    des, man = pd.read_csv(T / "panel/design.csv"), pd.read_csv(T / "panel/manifest.csv")
    TT, rng = int(des[des.task_type == "random"].task.max()), np.random.default_rng(0)
    (T / "panel/responses").mkdir(exist_ok=True)
    for r in man.itertuples():
        k = SEG_K[r.segment] * (1.1 if r.anchor == max(cfg["anchors"]) else 1.0)
        beta = {n: np.linspace(0, 1, len(A[n])) * PANEL_WTP[n] * k for n in names[1:]}
        ch = {}
        for pos, t in enumerate(json.loads(r.task_order), 1):
            opts = des[(des.version == (0 if t > TT else r.version)) & (des.task == t)].sort_values("alt")
            u = np.array([sum(beta[n][o[f"{n}_lvl"]] for n in names[1:]) - o["price"] for _, o in opts.iterrows()] + [15 * k]) / 10
            u += rng.gumbel(size=len(u))
            ch[str(pos)] = "ABC"[u.argmax()] if u.argmax() < 3 else "NONE"
        w = 40 * k
        body = {"choices": ch, "vw": {"too_cheap": w * .3, "cheap": w * .6, "expensive": w * 1.2, "too_expensive": w * 2},
                "gg": [{"price": p, "would_buy": bool(p < w), "likelihood": max(0, 100 - p / w * 60)} for p in json.loads(r.gg_order)], "rationale": "simulated"}
        (T / f"panel/responses/{r.rid}.json").write_text(json.dumps({"rid": r.rid, "response": body, "raw": "simulated", "meta": {}}))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="/tmp/value-pricing-selftest")
    ap.add_argument("--no-hb", action="store_true")
    a = ap.parse_args()
    T = Path(a.dir)
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    build(T)
    checks = []
    run(T, "value_mc.py", "--perms", "60", "--sobol-n", "256")
    vs = json.loads((T / "value/results/summary.json").read_text())
    gate = {f["feature_id"]: f for f in vs["feature_value"]}["ad_platform_connectors"]
    checks.append(("value: the ad connector is flagged as a gate", gate["is_gate"]))
    run(T, "kappa.py")
    run(T, "hedonic.py")
    ms = json.loads((T / "market/results/summary.json").read_text())
    fv = {f["feature_id"]: f for f in ms["feature_values"]}
    for k, b in PLANTED.items():
        checks.append((f"market: planted premium {k} {b:+.2f} inside the 90% CI {[round(x, 2) for x in fv[k]['ci90']]}", fv[k]["ci90"][0] <= b <= fv[k]["ci90"][1]))
    run(T, "value_metric.py", "--boot", "500")
    m = {r["axis"]: r for r in json.loads((T / "market/results/summary.json").read_text())["meters"]}["monthly_orders"]
    checks.append((f"market: orders elasticity {m['elasticity']:.2f} within 0.05 of planted {ELASTICITY}", abs(m["elasticity"] - ELASTICITY) < 0.05))
    run(T, "cost_model.py")
    run(T, "conjoint_design.py", "--starts", "1")
    run(T, "panel_build.py")
    simulate_panel(T)
    run(T, "panel_analyze.py")
    fits = [("fallback", ["--fallback"])] + ([] if a.no_hb else [("HB", ["--warmup", "400", "--samples", "400"])])
    for name, args in fits:
        run(T, "conjoint_fit.py", *args)
        lv = {(r["attribute"], r["level"]): r["pooled"]["mean"] for r in json.loads((T / "panel/results/conjoint.json").read_text())["wtp_per_level"]}
        got = lv[("ai_depth", "dashboards + AI chat + recommended actions")]
        checks.append((f"panel ({name}): top AI-depth WTP {got:.1f} within 25% of planted ≈{PANEL_WTP['ai_depth'] * 1.03:.1f}", abs(got / (PANEL_WTP["ai_depth"] * 1.03) - 1) < 0.25))
    run(T, "synthesize.py")
    fvt = pd.read_csv(T / "synthesis/data/feature_value.csv").set_index("feature_id")
    checks.append(("synthesis: multi_touch_attribution (ours: no, planted premium) classed roadmap", fvt.loc["multi_touch_attribution", "class"] == "roadmap"))
    run(T, "optimize_packages.py")
    pe = pd.read_csv(T / "synthesis/data/proposals_eval.csv")
    checks.append(("packages: every proposal scored under every lens", pe.groupby("proposal").lens.nunique().min() == pe.lens.nunique()))
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"study left in {T}")
    sys.exit(0 if all(ok for _, ok in checks) else 1)


if __name__ == "__main__":
    main()

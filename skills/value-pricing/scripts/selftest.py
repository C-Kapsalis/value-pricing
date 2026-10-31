#!/usr/bin/env python3
"""Self-test: run every analysis script on a synthetic study with planted ground truth, and check recovery.

Builds <dir> from templates/ (small settings), plants:
  market   260 vendors, log-price premia ad_platform_connectors +0.50, ai_prescriptive_insights +0.45,
           multi_touch_attribution +0.60; half the vendors scale on monthly_orders with elasticity 0.75
  demand   synthetic Second Read Studio audience labels, transaction elasticity -0.80
  panel    simulated respondents with known WTP per level (no LLM calls)
then runs value_mc, kappa, hedonic, value_metric, demand_elasticity, cost_model, conjoint_design,
panel_build, panel_analyze, conjoint_fit (fallback, and HB unless --no-hb), synthesize,
optimize_packages, and reports PASS/FAIL per check. Takes 5–20 minutes depending on the machine (HB is most of it).

  selftest.py [--dir NEW_DIRECTORY] [--no-hb]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from demand_elasticity import fit_product, load_transactions, price_variation_diagnostics

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
    (T / "synthesis").mkdir(parents=True, exist_ok=True)
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


def simulate_transactions(T: Path):
    rng = np.random.default_rng(51)
    rows = []
    # Entirely synthetic Second Read Studio example: these audience labels come
    # from its product brief; prices and quantities are planted test values.
    for segment, n_customers in (("technical_writers", 36), ("product_marketers", 36)):
        for customer_i in range(n_customers):
            customer = f"{segment}-{customer_i}"
            cust_effect = rng.normal(0, 0.25)
            for month in range(1, 13):
                date = pd.Timestamp(2025, month, 15)
                price = rng.choice([5.0, 7.0, 9.0, 12.0, 16.0, 22.0]) * rng.lognormal(0, 0.05)
                promo = int(rng.random() < 0.2)
                mu = np.exp(3.1 + cust_effect - 0.8 * np.log(price / 11)
                            + 0.25 * promo + 0.15 * np.sin(2 * np.pi * (month - 1) / 12))
                lam = rng.gamma(shape=4.0, scale=mu / 4.0)
                rows.append({"date": date, "product": "second_read_studio_synthetic", "customer": customer,
                             "segment": segment, "realised_unit_price": price,
                             "quantity": max(1, rng.poisson(lam)), "promotion": promo,
                             "channel": "online" if customer_i % 2 else "sales",
                             "contract_duration": 12 if customer_i % 3 else 1})
    d = pd.DataFrame(rows)
    (T / "demand/data").mkdir(parents=True, exist_ok=True)
    d.to_csv(T / "demand/data/transactions.csv", index=False)
    # Bad rows exercise validation and are excluded from estimation.
    bad = d.iloc[[0, 1]].copy()
    bad["date"] = bad["date"].astype("string")
    bad.loc[bad.index[0], "realised_unit_price"] = 0
    bad.loc[bad.index[1], "date"] = "not-a-date"
    pd.concat([d, bad], ignore_index=True).to_csv(T / "demand/data/transactions_with_bad_rows.csv", index=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", help="new output directory; must not already exist")
    ap.add_argument("--no-hb", action="store_true")
    a = ap.parse_args()
    if a.dir:
        T = Path(a.dir).expanduser().resolve()
        try:
            T.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            ap.error(f"--dir already exists; choose a new empty path to protect its contents: {T}")
    else:
        T = Path(tempfile.mkdtemp(prefix="value-pricing-selftest-"))
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
    simulate_transactions(T)
    tx, tx_counts = load_transactions(T / "demand/data/transactions_with_bad_rows.csv")
    checks.append(("demand: malformed and non-positive transaction rows are counted and dropped",
                   len(tx) == 36 * 12 * 2 and tx_counts["rows_dropped_missing_or_invalid"] == 2))
    low_variation = tx.copy()
    low_variation["realised_unit_price"] = 10.0
    edge = fit_product(low_variation, warmup=10, samples=10, chains=1, seed=19)
    checks.append(("demand: insufficient price variation blocks estimation", edge["status"] == "insufficient_price_variation"))
    segment_edge = tx.copy()
    segment_edge.loc[segment_edge.segment == "product_marketers", "realised_unit_price"] = 10.0
    seg_support = price_variation_diagnostics(segment_edge)
    checks.append(("demand: segment-specific price support flags a flat segment",
                   seg_support["n_unique_prices"] >= 3 and
                   seg_support["by_segment"]["product_marketers"]["n_unique_prices"] == 1))
    run(T, "demand_elasticity.py", "--warmup", "400", "--samples", "800", "--chains", "2")
    ds = json.loads((T / "demand/results/summary.json").read_text())["demand_elasticity"]["products"]["second_read_studio_synthetic"]
    est = {e["segment"]: e for e in ds["estimates"]}
    recovery = all(e["ci90"][0] <= -0.8 <= e["ci90"][1] and abs(e["elasticity"] + 0.8) < 0.35 for e in est.values())
    checks.append(("demand: segment elasticities recover planted -0.80 and 90% intervals cover it", recovery))
    checks.append(("demand: NUTS convergence diagnostics pass", ds["diagnostics"]["converged"]))
    demand_summary = json.loads((T / "demand/results/summary.json").read_text())["demand_elasticity"]
    checks.append(("demand: results are explicitly observational", demand_summary["identification"]["causal"] is False))
    ppc = ds["model_fit"]["posterior_predictive_check"]
    checks.append(("demand: posterior predictive mean and p90 cover synthetic observations",
                   ppc["observed_mean_inside_rep_ci90"] and ppc["observed_p90_inside_rep_ci90"]))
    checks.append(("demand: a 20% price increase reduces predicted transaction quantity",
                   all(e["scenarios"][2]["expected_quantity"] < e["scenarios"][1]["expected_quantity"] for e in est.values())))
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
    sy = json.loads((T / "synthesis/results/summary.json").read_text())
    checks.append(("synthesis: demand elasticity remains a separate evidence source",
                   sy["demand_elasticity"]["identification"]["causal"] is False and
                   (T / "synthesis/data/demand_elasticity.json").exists()))
    run(T, "optimize_packages.py")
    pe = pd.read_csv(T / "synthesis/data/proposals_eval.csv")
    checks.append(("packages: every proposal scored under every lens", pe.groupby("proposal").lens.nunique().min() == pe.lens.nunique()))
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"study left in {T}")
    sys.exit(0 if all(ok for _, ok in checks) else 1)


if __name__ == "__main__":
    main()

# Phase 2 · Market (the reference)

Estimate what the market charges for each feature (hedonic regression: price as a sum of implicit
feature prices, Rosen 1974), and so what it would charge for this offering's feature vector, per
segment. Also read off **what the market meters on**, which decides the packaging axis in phase 6.

The assumption this phase rests on, stated in every output: **listed prices reflect delivered value.**
They don't fully. Prices are set strategically, markets are out of equilibrium, and only surviving
listed products are observed. The result is a market reference, not value.

## 0. Terms check, before any crawl

Read the target site's or marketplace's terms of service and `robots.txt`. Record what you read and the
verdict in `market/REPORT.md §0`. A marketplace that forbids automated access (app stores often do) is
the owner's call: lay out the options (skip it, use only vendors' own sites, a manual sample, crawl
anyway at the owner's risk) and stop until the owner rules. Never work around a refusal silently.

## 1. Corpus

Breadth first: the identifiability of feature effects needs many products, not just close rivals.

- Seed: the user's named competitors, the marketplace category if there is one, "alternatives to X" and
  comparison pages, review-site category pages. Use web search for discovery.
- Target several hundred products; ≥100 priced is the floor for a stable model (the script refuses
  below 30).
- Tier each: `direct` (same purchase) vs `adjacent` (same stack, different purchase). Robustness runs
  on direct-only (`hedonic.py --direct-only`).
- Write `market/data/vendors.csv` (template in `templates/vendors.csv`); numeric controls go in `ctl_*`
  columns (popularity, review count, age). Add a `__ours__` row with our own controls.

```bash
$PY $K/crawl_site.py --study pricing-study --vendors market/data/vendors.csv --pricing-only
```

## 2. Plan cards

Parse every vendor's pricing page into `market/data/plans.csv` (template `templates/plans.csv`): vendor,
plan, price, currency, period, recommended flag, free, quote-only, and **every stated limit on a scale
axis** as `limit_<axis>` columns (seats, sources, projects, the segment axis). LLM extraction is fine;
spot-check 20 by hand. Every vendor gets a `price_state` ∈ {priced, free_only, quote_only, undisclosed}
and the four counts are reported: a market where most rivals hide prices is itself a finding.

Currency: one rate per run in `study.yaml fx` (1 unit of the listed currency = x study currency); record
its date and source.

**Reference price per vendor** (the rule `hedonic.py` applies): the plan marked recommended; else the
middle paid tier; for plans with limits on the segment axis, the cheapest plan whose limit covers each
segment's `reference_volume` (so a vendor yields one price per segment). Free-only and quote-only
vendors stay in the corpus as hurdle states.

## 3. Feature coding

```bash
$PY $K/code_features.py --study pricing-study build --ours example.com
$PY $K/llm_batch.py     --study pricing-study --dir market/coding1 --expect features
$PY $K/code_features.py --study pricing-study collect
# blind double-code with an independently worded codebook on ≥100 vendors
$PY $K/code_features.py --study pricing-study build --codebook 2 --sample 120
$PY $K/llm_batch.py     --study pricing-study --dir market/coding2 --expect features --model <a different model>
$PY $K/code_features.py --study pricing-study collect --codebook 2
$PY $K/kappa.py         --study pricing-study
```

Drop or merge any id with Cohen's κ < 0.6 before modelling (`hedonic.py` reads `kappa.csv`); list the
drops in `gaps`. Our own site is coded the same way: if that vector differs from `offering.yaml`, the
site oversells or undersells the product; report both.

## 4. Model

```bash
$PY $K/hedonic.py --study pricing-study [--with-partial] [--direct-only]
```

- Spec: `log(reference price) ~ feature dummies + category fixed effects + controls`.
- Lasso selects features; **post-double-selection** (Belloni, Chernozhukov & Hansen 2014) gives honest
  90% intervals on each feature.
- 20% holdout: out-of-sample R² and MAPE. An R² of 0.2 is normal for list prices; say so, don't hide it.
- Robustness: direct-only, `--with-partial`, the per-segment prices.

## 5. Price the offering

The script reports three implied prices per segment; synthesis reads all three as a corridor:

| Estimate | When it is the one to trust |
|---|---|
| OLS on the selected features | when our feature count sits inside the corpus's range |
| **lasso shrinkage** | when we have more features than almost any priced rival: OLS extrapolates and reads high |
| **coverage neighbours** (the 15 priced rivals covering most of our features, coverage-weighted geometric mean) | always, as the in-support check |

Rank neighbours by **coverage of our features**, not Jaccard: Jaccard penalises broad suites. Features
no priced rival has are out of sample (`out_of_sample_features`); say so and leave them to phase 3.

## 6. Meters (the packaging axis)

```bash
$PY $K/value_metric.py --study pricing-study
```

For each `limit_<axis>` on plan cards: the share of vendors (all / direct) that scale on it and the
**within-vendor elasticity** (slope of log price on log quantity across a vendor's own plans) with a
vendor-bootstrap interval and R². Elasticity 0.8 means doubling the quantity raises price ~74%.

Read `co_moves` before trusting a slope: when two axes step up together across a vendor's tiers (seats
and orders both rise with every tier), their slopes are confounded and belong to the bundle. The meter
is the axis vendors scale on alone.

This table decides the meter. The quantity value scales with is often one almost no rival meters on;
value scaling tells you the segment axis, the meter table tells you what buyers are used to being
charged for. The same elasticities price extra units and extra seats/stores in phase 6.

Done when `market/results/summary.json` follows the contract and `market/REPORT.md` covers §0 terms,
corpus, coding agreement, model fit, implied prices, nearest competitors, meters and threats.

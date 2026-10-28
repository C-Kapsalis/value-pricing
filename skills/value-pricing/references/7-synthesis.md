# Phase 6 · Synthesis and packages

Combine the phases into one evidence-backed recommendation: a **price corridor** per segment, a
**feature-value table**, and **≥3 proposals** scored on contribution, each with what would prove it wrong.
Synthesis adds no new measurement; every input is a phase result.

```bash
$PY $K/synthesize.py         --study pricing-study   # synthesis/data/{corridor,feature_value}.csv
$PY $K/optimize_packages.py  --study pricing-study   # synthesis/data/proposals_eval.csv, synthesis/results/packages.json
```

## 1. Corridor per segment

- **Floor** = variable + people + channel cost at the target margin (phase 5).
- **Reference** = the market's implied price (phase 2): OLS, lasso, coverage neighbours as a band.
- **Ceiling** = value: EVC × 10–30% capture, beside the panel's reservation price p25–p75. Where they
  disagree, say which you believe and why (the panel is optimistic in level).
- **Working window** = from what buyers said (panel VW OPP, else EVC × 10%) up to the reference, never
  below the floor or above the EVC ceiling. The simulated panel p75 is shown as context, not substituted
  for a missing or lower EVC ceiling.

Flag every segment where the order breaks, and read it:
- floor > ceiling → don't serve the segment at that cost, or serve it fully self-serve;
- reference > ceiling → either the market model is unscaled for small buyers (most plans don't scale
  with volume, so the reference is a mid-tier price for everyone) or the value model is too
  conservative; say which, with evidence (nearest rivals' prices settle it).

## 2. Feature-value table

Join market premium (phase 2) and value (phase 3: share valued, median €, Shapley share, leave-one-out;
phase 4b: WTP per level) on the taxonomy id. Classes:

| Class | Rule | Action |
|---|---|---|
| headline | high on market AND value | in every paid tier's copy; lead with it |
| underpriced differentiator | high value, low market premium | communicate it; fence it in a higher tier |
| market premium | high premium, we have it, value modest | say so on the listing |
| roadmap | high premium, we lack it | roadmap signal, not a pricing input |
| gate | low direct value, high leave-one-out | fence on it (it decides what else works) |
| low both | — | don't lead with it, whatever the category's habit |

`synthesize.py` states its thresholds (`--premium 0.15 --valued 0.30 --shapley 0.10`); quote them in
the report. A `partial` feature is never in tier copy, whatever its class.

## 3. Proposals (≥3) — `synthesis/proposals.yaml`

Cover at least: **good-better-best on capability** (fence on the gate the market and value agree on);
**usage-scaled on the meter** phase 2 found; **base plus add-ons** for the lines that carry real
marginal cost (people time, crawl/compute) — bundle the zero-marginal-cost features (Bakos &
Brynjolfsson), price separately what costs (Adams & Yellen); a **managed tier** beside self-serve if
there is a done-for-you layer. Add what the council proposed.

Each tier lists `config` (conjoint levels, for the panel lenses) and `features` (taxonomy ids, for the
value lens), a `price_grid`, optional `segments` (a usage fence) and `people_hours`. The optimiser
searches the grids and reports, per proposal:
- prices per tier and the mix per segment (share of preference vs NONE, and vs mapped competitors);
- revenue and **contribution after people time and channel cut** per 100 addressable customers;
- the best prices under **every level lens** — panel as estimated, panel ÷ calibration ratio, EVC ×
  capture — and a **robust** pick that maximises the worst ratio to each lens's own best. A proposal
  that wins only under the optimistic lens is not a winner;
- customers needed to carry fixed cost.

Then write, per proposal: anchor and decoy logic (Simonson compromise effect; Huber et al. decoy; lead
the listing with the headline tier, never the cheapest), trial / free plan handling (Shampanier et al.:
a free plan pulls in the segment you can least afford to serve), margin per tier, the main risk, and
**"proven wrong if"** — an observable result of the validation survey.

## 4. Extras, multi-unit and coherence

- **Extra units on the meter** (seats, sources, accounts): price ∝ quantity^elasticity from phase 2's
  meter table (`unit_multipliers`). Dividing a feature's premium across unit types instead badly
  understates what the market charges per unit.
- **Multiple stores / brands / workspaces**: the market's elasticity for that axis (an elasticity of 0.6
  gives ~1.5× for two units and ~1.9× for three). Decide whether it applies to the largest unit's price or the sum.
- **Cap the extras** or switch to a sales-assisted quote above a threshold: count the real distribution
  of units per customer first; the tail is usually longer than expected.
- **Coherence across channels.** If the product sells in two channels (app store and direct), price the
  same buyer in both and explain every gap: what only the dearer channel delivers.
- **Seasonality.** A volume meter needs a trailing average (3 months) and a rule for moving bands.

## 5. Recommend, then let the owner pick

Recommend one proposal with the reasons in three bullets and what it gives up. Then hand the pick to
the owner. Structures often tie within a few percent; when they do, the owner holds information the
synthesis does not. Present
the trade and the survey result that would separate them, not a verdict.

Deliver `synthesis/PROPOSALS.md` (≤10 pages), the CSVs, and a report page (an HTML artifact when
available: corridor chart, feature scatter, proposal ladders, robustness by lens). Done when each
proposal states prices per tier, mix, contribution after people time under every lens, anchor/decoy
logic, main risk and "proven wrong if".

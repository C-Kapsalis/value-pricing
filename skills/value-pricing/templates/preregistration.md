# Pre-registration · panel for <PRODUCT>

Registered <DATE>. **Binding rule:** this file is committed (or its SHA-256 recorded in `DECISIONS.md`)
before the first file exists under `panel/responses/`. Any later change to the analysis is a
**deviation**, logged in §11 with its reason; the registered analysis is still reported.

## 1. Question

What will <BUYER, e.g. "a marketing lead at a company like our customers"> pay per month for <PRODUCT>,
by segment (<AXIS>: <BANDS>), and which attributes carry that willingness to pay? Measured on a silicon
sample (Argyle et al. 2023) conditioned on <FRAME: real buyer rows / inferred archetypes>. The result is a
hypothesis for real-buyer validation (Brand, Israeli & Ngwe; Horton 2023), never a measurement of buyers.

## 2. Hypotheses

| | Hypothesis | Test (posterior of the primary HB-MNL unless stated) | Supported if |
|---|---|---|---|
| H1 | WTP for our configuration rises with the segment | segment median reservation price p*, monotone across segments | P(all adjacent differences > 0) ≥ 0.90 |
| H2 | <ATTR A> and <ATTR B> carry the largest part-worths | attribute importance = WTP range across levels, pooled | both in the top two with P ≥ 0.80 |
| H3 | <SERVICE ATTR> has positive WTP that grows with segment | WTP of its top level vs base, per segment; slope | > 0 with P ≥ 0.95 in every segment; top > bottom segment with P ≥ 0.90 |
| H4 | The anchor shifts stated instruments more than choice-based WTP | log(median at high anchor / median at low), paired within persona, for VW "expensive", GG revenue-max price and conjoint p* | VW and GG log ratios exceed conjoint's, bootstrap 90% CI of the difference above 0 |

Add one hypothesis per meter if the design tests meters (WTP monotone in units; WTP per unit vs its cost).
A failed hypothesis is reported as failed. None is re-tested by a second analysis.

## 3. Outcomes

- **Primary:** segment median reservation price p* for our configuration (`study.yaml conjoint.our_config`),
  post-stratified to archetype shares, pooled over arm cells.
- **Secondary:** WTP per level; price coefficient; holdout hit rate; VW points (PMC, OPP, IPP, PME); GG curve
  and revenue-maximising price; anchor and paraphrase effects on each instrument; WTP-space median p*;
  never-buyer share; the calibration ratio (§9).

## 4. Design

Attributes and levels: <TABLE from study.yaml>. Price levels log-spaced, top level above the largest
segment's expected WTP. <V> versions × <T> random tasks × <A> alternatives + NONE ("keep my current
setup"), coordinate exchange minimising MNL D-error under mild priors (Huber & Zwerina 1996), no identical
or dominated alternatives within a task; plus 2 fixed holdouts and 1 dominance check. Task order and
attribute order randomised per persona and fixed across its cells. D-error, balance and the parameter
recovery check: Appendix A.

**Arms** (within persona): anchor <LOW>/<HIGH> as the stated listing price × <P> paraphrases of the
instructions. Persona text, version and orders are byte-identical across a persona's cells; only the
manipulated element differs (Gui & Toubia).

## 5. Sample

<N_SEG> segments × <PERSONAS> personas = <N_PERSONAS> personas × <CELLS> cells = <N_CALLS> calls (floor 30
per segment × cell). Each archetype gets max(<MIN>, proportional) personas per segment; estimates are
post-stratified. Model <MODEL> via <claude -p / subagents / API>, one respondent per call, no tools, a fixed
system prompt; temperature <value or "model default">. **Stopping rule:** run to <N_CALLS>; if stopped
early, analyse whole personas if every cell has ≥ 30 kept respondents, else report the shortfall and do
not estimate.

## 6. Exclusions (applied mechanically by panel_analyze.py)

| Rule | Condition | Scope |
|---|---|---|
| E1 dominance | did not choose the dominant option (B) in the check task | all |
| E2 straightlining | the same letter in every random task (always-NONE is a legitimate non-buyer, kept) | all |
| E3 GG monotonicity | would_buy at a higher price and not at a lower one, or likelihood rising > 10 points with price | GG only; a binary-only variant is secondary |
| E4 malformed | no parseable reply after one retry, or fewer valid choices than tasks | all |
| E5 VW order | not too_cheap ≤ cheap ≤ expensive ≤ too_expensive | VW only |

## 7. Estimation

HB-MNL in preference space (numpyro NUTS, 2 chains × 800 warmup × 800 draws, target accept 0.85):
U = β_i′x − exp(θ_i)·price/s; NONE: U = asc_i; (β_i, θ_i, asc_i) ~ MVN(μ0 + Γ′z_i, Σ), z_i = segment,
high-anchor and paraphrase dummies; Σ = diag(τ) Ω diag(τ), Ω ~ LKJ(2), τ ~ HalfNormal(1); non-centred.
Convergence: R-hat ≤ 1.05, bulk ESS ≥ 200 on μ0, Γ, τ; else 4 chains × 1,500; else the conditional-logit
fallback with segment/arm interactions and a persona bootstrap. WTP per level = s·β/exp(θ); reservation
price p* = max(0, s·(β′x_ours − asc)/exp(θ)). WTP-space check (Sonnier, Ainslie & Otter 2007). Holdout
hit rate vs chance. VW and GG per segment, pooled and per arm.

## 8. Value cue

Each persona is shown what the value model (phase 3) flagged for its representative scenario. It is a
deliberate part of the instrument and a declared threat (§10).

## 9. Level-bias calibration

Replicate <BENCHMARK, e.g. Brand, Israeli & Ngwe's toothpaste pilot and Study 1A, verbatim templates> on the
same model and settings; MNL WTP for the benchmark attribute vs the published human figure. Reported as a
silicon/human ratio range, never applied to the headline numbers.

## 10. Threats declared in advance

Level bias; variance compression; the persona is the respondent's only knowledge of its budget; the value
cue; repeated calls per persona are not independent people; the segment proxy; censoring above the top
price level.

## 11. Deviations

| # | When | What | Why | Effect on registered results |
|---|---|---|---|---|

## Appendix A · design statistics and recovery

<paste panel/design_stats.json and the conjoint_fit.py --recovery-check output>

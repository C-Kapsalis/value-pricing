# Phase 7 · Validation and hand-over

The proposals are hypotheses built on simulated buyers. This phase designs the test on real ones and
records what the owner decides.

## 1. Real-buyer survey

This is a study plan, not a survey sender. Before contacting anyone, the owner must approve the frame,
message, lawful basis/consent, suppression rules, vendor access, retention period and data minimisation.
Do not put contact lists or identifiable responses in the skill workspace or in model prompts. The pilot
invite count is a planning assumption, not an instruction to send invitations.

- **Sample** from a real frame (CRM, lead base, newsletter, marketplace census), excluding current
  customers and staff, **stratified** by segment × the gate (e.g. with / without the key integration).
  ~150 completes per cell gives ±7 points on an acceptance share at 90% confidence; run a pilot wave
  (~2,000 invites) to measure response rate before sizing the full wave. Incentive-aligned where the
  owner allows (BDM or incentive-aligned conjoint: Wertenbroch & Skiera 2002; Ding 2007).
- **Questionnaire, ~8 minutes, in this order:**
  1. screener: volume on the segment axis, the gate, current tools and spend on them, role;
  2. **behaviour first**: show 3 real insights with their € effect; ask how often they would act and
     how much of the effect they expect to land (this calibrates the parameters that carried most of
     the value variance);
  3. **structure arm** (between subjects): one proposal's plan cards; "which would you choose after a
     trial?" — the discriminator;
  4. **anchor arm**, crossed with it: the listing leads with the top or the bottom tier;
  5. Van Westendorp on the plan they chose;
  6. Gabor-Granger with a randomised start;
  7. add-ons at one of three randomised prices.
- **Decision rules, fixed before the data comes in** — one row per contested choice, each naming a
  threshold that switches the pick (e.g. "if buyers with the gate accept the headline price less than
  1.2× as often as buyers without it, drop the capability fence"; "if action × realisation is under
  half the simulated value, halve the ceilings before pricing the top tiers"; "if two proposals differ
  by under 10% in contribution per respondent, pick the simpler one to operate").
- After the survey, confirm on live sign-ups with time-split cohorts: to confirm the choice, not to make it.

Measure alongside: people minutes per customer during the first trials (the cost phase's usual gap) and
any capacity limit per customer.

## 2. Rulings ledger

Write every open ruling as a row: id, the ruling, status (ratified / open · recommended / open), who.
Typical ones: the meter, the tier prices, currency rounding for each listing, trial length, launch
offer, extras cap, multi-unit rule, band-move rule, what each channel withholds, tax position on channel
payouts. Ratified rows go into `DECISIONS.md`.

## 3. Hand-over

- `REPORT.md` at the study root: the decision, the corridor, the feature table, the proposals, the
  validation plan, the gaps, provenance (which script produced which number).
- If the owner ratified a price list: a one-page price list with the rules behind it, and a setup
  runbook — what must be configured in billing, what needs a build before a fence is real, in the order
  it must happen, with the read-only checks first.
- The token cost of the study.

Done when the owner's pick and every open ruling are in `DECISIONS.md` and the report is delivered.

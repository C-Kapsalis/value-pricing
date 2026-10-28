# Phase 3 · Value (the ceiling, and each feature's added value)

Estimate the economic value the offering delivers per segment (**EVC**, Forbis & Mehta 1981):

> EVC = reference alternative cost + differentiation value

Then split that value across features, so the study can say what each feature contributes. This is the
number the owner usually wants most and trusts least, so every formula is a named parameter a reviewer
can move.

## 1. Value drivers (`value_drivers.yaml`)

For each feature in `offering.yaml` with `status: yes` (and `partial`, flagged), write one or more value
lines. Each line has a **value type**, the scenario **quantity** it acts on, a **trigger** (when it fires
for a given customer) and the features it **needs**. Value types (conservative formulas, all in
`templates/value_drivers.yaml`):

| Type | € per month |
|---|---|
| `reallocate` | quantity × share_moved × efficiency_delta |
| `waste` | quantity × waste_share |
| `revenue_retained` | quantity × at_risk × recovery_share × gross_margin |
| `margin` | quantity × excess × protect_share |
| `risk` | loss × probability |
| `hours` | views or tasks replaced × hours_per_view × hourly_rate |
| `cost_replaced` | a cost the buyer stops paying |
| `delivered_work` | hours of done-for-you service × the buyer's alternative rate |

Insight types (anything that depends on the buyer acting) are multiplied by **action rate × realisation
rate**; delivered work and replaced cost are not. Per-scenario **caps** stop overlapping lines
double-counting (e.g. reallocation plus waste ≤ 10% of spend). Defaults are conservative on purpose.

Where to get triggers and formulas, best first:
1. **The product's own logic.** If it has rules, alerts or recommendations in code, replay them on
   generated scenarios, and check the replay agrees with the real engine rule by rule. A replay beats any
   hand-written trigger.
2. **Case studies and the vault.** Quoted outcomes ("cut reporting from 6 h to 1 h") become parameters
   with a source.
3. **The council** (phase 4a): ask each buyer persona what they would do with each insight. Record the
   answer as a parameter range, not a point.

Gate every line on its `needs`: an insight that rests on data the scenario would not have does not
count. Whether a gate is in use for a given customer (has ads, has a CRM) is
`study.yaml scenarios.feature_in_use`.

## 2. Scenarios

`study.yaml scenarios` describes the variables per segment and archetype (volume on the segment axis,
economics, connected features, hourly rate). Variables are drawn in order from distributions or
computed from expressions; any parameter may be a per-segment map. N ≥ 5,000; seeded.

```bash
$PY $K/value_mc.py --study pricing-study [--n 10000] [--perms 200] [--sobol-n 1024]
```

## 3. What the script computes

- **Value per segment**: p10 / p50 / p90 of monthly delivered value and EVC, and the share by value type.
- **Per-feature added value**, three ways, because they answer different questions:
  - `share_of_scenarios_valued` and `median_eur_when_valued`: how often and how much;
  - **Shapley share** of total value (permutation sampling over features, caps applied inside every
    coalition): the fair split when features interact through caps and gates. This is the "estimated
    added-value contribution" of each feature;
  - **leave-one-out**: what the customer loses if the feature (and everything it gates) is removed —
    the fence test for tiers.
- **WTP band** = EVC × capture share 10 / 20 / 30% (Nagle): what a seller can usually expect to capture.
- **Sobol indices** (Saltelli) on every parameter with a range. Expect the behavioural multipliers
  (action rate, realisation, capture share) to explain most of the variance and the formulas' own
  coefficients very little; it tells the validation survey to measure behaviour first.
  Below N = 1024 the first-order indices are noisy (they can go negative); raise `--sobol-n` before
  quoting them.

Gates (connectors, integrations, a data source) produce little direct value but unlock most of the rest.
The script flags them (`is_gate`: lost far more often without it than valued on its own). Report each
gate's leave-one-out loss beside its Shapley share; leave-one-out is the number that justifies fencing
on it.

## 4. Write up

`value/results/summary.json` per the contract, and `value/REPORT.md`: method, value by segment and type,
the feature table, Sobol, the assumptions that carry the most variance, threats (scenario priors are
industry-typical, not measured; value is modelled, not observed).

Done when every feature has a share of scenarios valued, a median €, a Shapley share and a
leave-one-out loss, and Sobol indices name the parameters that move the ceiling.

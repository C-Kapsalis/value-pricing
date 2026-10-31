---
name: value-pricing
description: Value-based pricing study for a product or service, from its website and knowledge base to a ratified price list. Use when someone wants to price or re-price an offering, design tiers or packages, estimate what each feature is worth to customers, analyze transaction-based demand response, or find willingness to pay. Demand estimates are observational unless a defensible causal design is supplied. Triggers on "price my product", "what should we charge", "pricing tiers", "packaging", "price elasticity from transactions", "willingness to pay", "value of each feature", "/value-pricing".
---

# Value-based pricing

Price an offering from **three sides** and let the gaps between them do the arguing:

| Side | Question | Method | Gives |
|---|---|---|---|
| **Market** | What do rivals charge for this feature set? | hedonic regression over competitor plan cards | the **reference** price and each feature's market premium |
| **Cost** | What does one more customer cost to serve? | cost-driver model + people time | the **floor**, and the volume needed to carry fixed cost |
| **Value** | What is it worth to the buyer? | economic value to the customer (EVC) Monte Carlo + a pre-registered conjoint on a persona panel | the **ceiling**, and each feature's added value |
| **Demand behavior (separate evidence)** | How does observed transaction quantity vary with realised price? | hierarchical Bayesian demand model on historical transactions | segment-level observational price associations and scenario responses; causal only with a defensible identification design |

A **council** of persona agents (buyers per segment, plus pricing experts) argues the proposals; the
synthesis scores them; the cost interview turns them into packages that make money; a real-buyer
validation plan says what would prove them wrong. The owner rules at every fork.

Every number is a **hypothesis** until real buyers confirm it. Simulated buyers get direction right and
level wrong; say so on every page that quotes them.
Demand elasticity is separate from competitor listed-price meter elasticity. Transaction rows without
zero-purchase periods estimate quantity conditional on an observed purchase, not purchase incidence or
total market demand.

## Ground rules (every phase)

- **The current list price is not a corridor input.** Do not feed today's price list to the market, cost,
  or value phases; it anchors the corridor on a number nobody ratified. The optional demand phase is the
  separate exception: it requires realised transaction prices from historical purchases to estimate
  behavioral response, and its results do not set the corridor by themselves. Compare the current list
  price against the finished corridor at the end.
- **Unknown is `null` plus a stated gap,** never a plausible number. Every assumption is one sentence in
  the phase's `summary.json.assumptions`, so the owner can disagree with it.
- **The owner rules.** Judgement calls (segment axis, crawl permission, archetypes, anchors, which proposal)
  go to the user as a question with a recommendation, then into `DECISIONS.md`
  (`YYYY-MM-DD · phase · decision · why · who ruled`).
- **Read-only** against anything in production. Raw crawls and transcripts stay outside git.
- **Money** in one currency per study, per month, ex VAT; intervals are 90%.
- Before any expensive step (a crawl of hundreds of pages, LLM coding of a corpus, a panel of hundreds of
  calls) post a token and time estimate to the user and wait for a go.

## Workspace

Create `pricing-study/` in the user's working directory (or where they say) from `templates/`:

```
pricing-study/
  study.yaml          product, currency, segments, archetypes, scenarios, conjoint, lenses
  offering.yaml       the capability vector, every feature with evidence (quote + source)
  taxonomy.yaml       the ONE feature vocabulary, phrased the way the market advertises
  value_drivers.yaml  feature → value line → formula (the valuation rubric)
  costs.yaml          the cost structure, from the cost interview
  DECISIONS.md        append-only rulings
  corpus/             crawled pages and ingested notes (gitignore it)
  market/ cost/ value/ council/ panel/ synthesis/    one folder per phase; each writes results/summary.json
```

Scripts live in this skill's `scripts/` and take `--study pricing-study`. Set up the environment once:
`uv venv .venv-pricing && uv pip install --python .venv-pricing/bin/python -r <skill>/scripts/requirements.txt`
(add `playwright` and run `playwright install chromium` for JS-heavy sites). Every script has `--help`.
Run `scripts/selftest.py` once on a new machine: it checks every script against planted ground truth.
Keep the study folder on persistent disk, not `/tmp`: a machine or VM restart clears `/tmp`.

Parallel work: market, cost and value are independent. When they run as separate sessions or subagents,
each writes only inside its own folder, and changes to the shared files (`taxonomy.yaml`, `study.yaml`)
are proposals logged in `DECISIONS.md`.

## The sequence

Each phase ends on a completion criterion. Read the phase's reference file when you start it.

1. **Intake** — crawl, ingest, build the offering and the taxonomy. → [`references/1-intake.md`](references/1-intake.md)
   Done when every feature in `offering.yaml` carries a quote and a source, `taxonomy.yaml` has an id
   for every offering feature and every competitor feature seen so far, and the owner has ruled the
   segment axis and the archetypes.
2. **Market** — competitor corpus, plan cards, feature coding, hedonic model, meter elasticities.
   → [`references/2-market.md`](references/2-market.md)
   Done when `market/results/summary.json` holds the implied price per segment (OLS, lasso and coverage
   neighbours), a premium per feature with its interval, κ per feature, and the meter table.
2b. **Demand behavior (optional)** — import transactions and estimate Bayesian quantity-price associations.
   → [`references/9-demand-elasticity.md`](references/9-demand-elasticity.md)
   Done when diagnostics and price variation are reviewed, each product and segment has a posterior
   estimate or explicit data gap, and observational identification limits are recorded.
3. **Value** — value drivers, scenarios, Monte Carlo, per-feature added value, sensitivity.
   → [`references/3-value.md`](references/3-value.md)
   Done when every feature has a share of scenarios it valued, a median €, a Shapley share and a
   leave-one-out loss, and Sobol indices name the parameters that move the ceiling.
4. **Council** — persona agents consult on value, objections and fences; then the pre-registered panel.
   → [`references/4-council.md`](references/4-council.md) and [`references/5-panel.md`](references/5-panel.md)
   Done when `council/minutes.md` records each member's verdict on each draft structure, and the panel's
   pre-registration is committed before its first response file exists.
5. **Cost** — interview the owner on the cost structure, then the floor. → [`references/6-cost.md`](references/6-cost.md)
   Done when `costs.yaml` splits every line into variable / fixed / people / channel with a source or a
   stated gap, and people time per customer has a number or an explicit range.
6. **Synthesis and packages** — corridor, feature-value table, ≥3 proposals scored on contribution,
   extras and multi-unit curves, coherence across channels. → [`references/7-synthesis.md`](references/7-synthesis.md)
   Done when each proposal states prices per tier, expected mix, contribution after people time under
   every level lens, anchor and decoy logic, the main risk, and what would prove it wrong.
7. **Validation and hand-over** — real-buyer survey with decision rules fixed before data; the owner picks.
   → [`references/8-validation.md`](references/8-validation.md)
   Done when the owner's pick and every open ruling are in `DECISIONS.md` and the report is delivered.

Phases 2 and 3 can run in parallel; 5 can run any time before 6. The owner asked for a fast pass? Run
1 → 3 → 4 (council only) → 5 → 6 and label the result "market side unmeasured".

## Reference

- [`references/lessons.md`](references/lessons.md) — what went wrong or surprised in the studies this
  method came from. Read it before phase 2 and again before phase 6.
- [`references/output-contract.md`](references/output-contract.md) — the `summary.json` shape per phase.
- [`references/9-demand-elasticity.md`](references/9-demand-elasticity.md) — transaction schema, model, diagnostics and identification limits.
- [`references/literature.md`](references/literature.md) — the basis for each method. Verify a citation
  before it goes into a deck.
- The council personas ship as this plugin's agents: `buyer-persona`, `pricing-strategist`,
  `cfo-unit-economics`, `behavioral-economist`, `competitive-analyst`, `gtm-sales-lead`, `devils-advocate`.

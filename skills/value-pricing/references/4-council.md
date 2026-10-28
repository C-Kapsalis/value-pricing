# Phase 4a · The council

A **Delphi** round of persona agents: buyers who would pay, and experts who would set the price. The
council does two jobs the numbers cannot: it finds the objections, fences and framings the models miss,
and it supplies behavioural parameter ranges (how often a buyer acts on an insight, how much of the
modelled gain they believe) that phase 3 needs. It does **not** produce willingness-to-pay numbers;
that is the panel's job (phase 4b), on an instrument built to measure it.

## Members

**Buyers.** One `buyer-persona` agent per segment × archetype that carries real weight (3–5 archetypes ×
4 segments; merge thin cells). Each gets a **persona card** built from `study.yaml`: role, company, team,
volume on the segment axis, economics, what they use today and what it costs, and what the value model
flagged for them this month (the fired lines of their representative scenario: the scenario in
`value/data/mc_results.parquet` whose EVC is nearest its cell's median; `value/data/fire_matrix.parquet`
names the lines). User-defined personas from `study.yaml council.personas` join as written.

**Experts** (this plugin's agents):

| Agent | Brings |
|---|---|
| `pricing-strategist` | value metric, fences, tier architecture, capture share |
| `cfo-unit-economics` | contribution margin, payback, fixed-cost coverage, people time |
| `behavioral-economist` | anchors, decoys, compromise effect, zero price, framing, fairness |
| `competitive-analyst` | the market reference, nearest rivals, positioning, how rivals meter |
| `gtm-sales-lead` | sellability, objections, discount pressure, channel rules and cuts |
| `devils-advocate` | the red team: what proves each proposal wrong, which number is weakest |

## Protocol

1. **Dossier.** Write `council/dossier.md`: the offering (with `partial` and `no` marked), the feature
   value table so far, the market table if phase 2 has run, the segment grid, and 2–4 **draft
   structures** (e.g. tiers on capability, tiers on the meter, base plus add-ons, a managed tier).
   No current prices.
2. **Round 1, blind.** Spawn every member in parallel (one message, many Agent calls) with the dossier
   and its own card. Each answers the questions in its agent file and returns the structured verdict.
   Members never see each other in round 1.
3. **Collate.** Write `council/round1.md`: where they agree, where they split, and every claim that cites
   no dossier number (flag it as judgement).
4. **Round 2.** Send each member the collation (SendMessage to the same agent, or a fresh call carrying
   its round-1 answer) and ask it to revise or defend, in under 200 words. Stop after round 2; more
   rounds converge on the loudest voice, not the truth.
5. **Minutes.** `council/minutes.md`: per draft structure, each member's verdict (adopt / adapt /
   reject) with the one reason that carried it; the objection list by segment; the behavioural
   parameter ranges the buyers gave (write them into `value_drivers.yaml` as ranges and rerun phase 3's
   Sobol); and any new structure the council proposed (it goes to phase 6 as a proposal).

Every member's agent file already carries the rules: cite the dossier or label a claim as judgement;
never invent a market price or a statistic; say "I don't know" for anything outside the persona.

Budget: ~15–25 members × 2 rounds. Estimate tokens and tell the user before round 1.

Done when `council/minutes.md` records each member's verdict on each draft structure and the buyers'
behavioural ranges are written into `value_drivers.yaml`.

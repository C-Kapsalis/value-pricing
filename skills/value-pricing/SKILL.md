---
name: value-pricing
description: Evidence-led pricing research for products, services, and other offerings. Use when someone needs to investigate a pricing decision, pricing structure, value metric, or customer evidence. Supports configurable business models, units, segments, and methods; outputs hypotheses and validation plans, not guaranteed prices.
---

# Value Pricing

Help the user investigate a pricing decision using methods suited to the offering, market, available evidence, and constraints. The research may examine market references, customer value, delivery economics, price sensitivity, or pricing structures. These are optional lenses, not mandatory phases.

## 1. Discover before choosing methods

Begin with the decision and gather the minimum context needed to scope it. Establish, when relevant:

- what is sold and what problem or job it addresses;
- who buys, who uses, and which segments matter;
- current alternatives, including the status quo or no-purchase option;
- the business and revenue model, including billing unit, period, terms, and channel;
- customer value drivers and how value could be measured;
- delivery and cost-to-serve drivers;
- current pricing and the decision under consideration;
- geographic and competitive market;
- available evidence, its source, date, and quality;
- constraints such as capacity, regulation, contracts, margin, or timing.

Do not ask every question by default. Ask only what is relevant to a candidate method. Mark unknowns as unknown and record how they affect the decision.

## 2. Scope and select research

Agree the study question, audience, unit of analysis, time horizon, evidence standard, and decision constraints. For every selected method, explain its purpose, required inputs, assumptions, and limitations. If essential evidence is missing or a method does not fit, say so and choose a suitable alternative or leave the question unresolved.

Possible methods include:

- market and competitor references, when offers and commercial terms are comparable;
- offering or attribute comparison, when meaningful attributes can be observed;
- Economic Value to the Customer (EVC) and value-driver scenarios;
- cost-to-serve, contribution, and margin analysis;
- observed transaction analysis, when suitable price and quantity records exist; interpret ordinary historical data as association, not causation or purchase incidence;
- qualitative interviews, price sensitivity questions, Van Westendorp, or Gabor-Granger;
- choice-based conjoint when buyers face realistic trade-offs among configurable attributes;
- simulated buyer research for exploration and question development;
- real-customer research or observed market tests for validation.

Do not infer a business model, unit, segment, attribute, cost, sample, or result from an example. Configure them from user-provided evidence. Report synthetic or simulated material as illustrative and never as empirical findings.

## Ground rules

- Treat listed prices as dated market references, not verified transaction prices. Record currency, billing unit, period, scope, conditions, and source.
- Separate observations, estimates, and assumptions. Unknown is `null` plus a stated gap, never a plausible invented number.
- Keep business-derived inputs private in the study workspace. Minimize personal or confidential data before any external model call and disclose the provider receiving prompts.
- User judgment governs scope, research choices, interpretation, and decisions. Present consequential assumptions and trade-offs clearly.
- Read-only against production systems. Store raw source material and research records outside version control.
- Do not promise an optimal price or actual willingness-to-pay prediction. Every model output is conditional on its data and assumptions.
- Loading the skill does not start scripts, crawls, or model calls. Run scripts only when explicitly invoked. Before an expensive step, explain its expected resource use and obtain the user's go-ahead.
- Use one currency and a clearly specified billing unit and period within each monetary analysis. Do not assume monthly billing.

## Configure a study

Copy relevant files from `templates/` to a study workspace. Configure only fields needed by selected methods. Templates are blank schemas, not empirical examples; dependent scripts should not be run until their required inputs are supplied.

Typical files:

```
pricing-study/
  study.yaml          decision, market, segments, methods, scenarios, and pricing basis
  offering.yaml       offering, buyers, outcomes, alternatives, evidence and gaps
  taxonomy.yaml       optional custom comparison vocabulary
  value_drivers.yaml  optional value model with units, dependencies and assumptions
  costs.yaml          optional cost-to-serve inputs with sources and gaps
  DECISIONS.md        study rulings and rationale
  corpus/             source material, kept out of version control
  market/ cost/ value/ panel/ synthesis/   outputs for selected phases
```

Python scripts are in `scripts/` and accept `--help`. Create an isolated environment and install `scripts/requirements.txt` only when a selected method needs the scripts. Some optional model-assisted steps require a locally available `claude` command or an explicitly selected API runner. Check data handling, costs, and provider terms before use.

## Workflow

1. **Intake and evidence:** describe the offer and buyer context. Collect sources and record what is known, uncertain, and unavailable. Use an attribute taxonomy only if comparisons need one.
2. **Market references (optional):** gather comparable offers and normalize terms. Use regression or price-per-unit analysis only when coverage, comparability, and sample support it; otherwise report a descriptive comparison.
3. **Customer value (optional):** define outcomes, counterfactuals, units, dependencies, and defensible ranges. Prevent double counting and show sensitivity.
4. **Buyer research (optional):** select interview, sensitivity, conjoint, or exploratory simulation methods to match the question. Preregister material design choices where appropriate. Simulated responses are hypotheses only.
5. **Delivery economics (optional):** estimate relevant variable, fixed, labor, channel, fulfillment, support, and other cost drivers from evidence. Keep gaps visible.
6. **Synthesis:** compare evidence and uncertainty, explain conflicts, and produce conditional pricing or packaging hypotheses only if the evidence supports them.
7. **Validation and handover:** propose a real-customer or market test, with decision criteria, risks, and unresolved assumptions.

The optional `demand_elasticity.py` script expects historical transaction rows with date, product, customer, segment, realized unit price, and quantity. It models quantity among observed transactions. It cannot estimate purchase incidence from transaction-only data, and non-experimental price variation does not establish causality.

Phases can be skipped, reordered, or scoped down. A study can end with an evidence gap or a recommendation to collect data rather than a price.

## Completion standard

The handover states the decision studied, business and pricing configuration, methods selected and why, sources and dates, assumptions and gaps, findings with uncertainty, sensitivity to key inputs, limitations, and next validation steps. Do not present synthetic examples or model outputs as observed customer behavior.

## References

Read only relevant guidance from `references/`: intake, market references, value, buyer research, cost, synthesis, validation, output contract, lessons, and literature. Academic references are methodological context; verify citations and applicability before external use.

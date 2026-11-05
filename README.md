# Value Pricing

Value Pricing is an evidence-led pricing research workflow that helps businesses evaluate market references, customer value, delivery economics and pricing structures. It adapts its research methods to the offering, business model, available evidence and decision being investigated.

The workflow is designed for products and services across B2B and B2C markets. It can be configured for recurring, one-off, tiered, usage-based, transaction-based, project, retainer, licence and hybrid pricing. Those are options, not assumptions: define the units, segments, value drivers, alternatives and commercial terms that fit the study.

## What it does

The skill helps a team:

- clarify the pricing decision, offering, buyers, market and constraints;
- select relevant research methods and document why they fit;
- compare market references when credible, comparable evidence exists;
- model customer value and delivery economics from stated inputs;
- design optional price sensitivity, choice or scenario research;
- turn evidence into pricing hypotheses, risks and a real-customer validation plan.

Methods can include competitor research, offering comparisons, Economic Value to the Customer (EVC), value-driver scenarios, cost and contribution analysis, Van Westendorp, Gabor-Granger, choice-based conjoint, simulated buyer research, and interviews or tests with real customers. The workflow does not require every method. Each selected method should state its inputs, rationale and limitations. Do not substitute invented inputs when evidence is unavailable.

## Who can use it

Teams researching software, professional services, agencies, physical or digital products, marketplaces, platforms and other offerings can use the workflow. The templates support custom customer segments, buyer archetypes, units of value, attributes, cost drivers and pricing structures. Feature comparison and conjoint are optional; skip them when buyers do not choose among meaningful attributes or bundles.

## How the workflow operates

1. **Discover and scope:** establish what is sold, who buys it, the problem solved, alternatives, business model, value and cost drivers, current pricing, market, available evidence and decision constraints. Ask only what the chosen study needs.
2. **Configure:** copy the templates and define the offering, segments, units, assumptions, relevant methods and required inputs.
3. **Research and model:** run only the phases supported by the evidence and decision. Keep unknowns explicit and separate observed facts, estimates and assumptions.
4. **Synthesize:** present evidence, uncertainty, sensitivity, trade-offs and testable price or package hypotheses.
5. **Validate:** specify how real customers or market behavior can test the hypotheses before a decision is treated as established.

Outputs may include an evidence-backed offering description, market reference analysis, value and cost models, optional research results, scenario comparisons, pricing hypotheses, assumptions and gaps, and a validation plan. Results are conditional on the supplied inputs and methods; they do not guarantee an optimal price or predict actual willingness to pay.

## Information to provide

Start with the pricing decision and a concise description of the offering and buyers. Depending on the selected methods, useful inputs may include alternatives and market references, customer segments, value drivers and units, current commercial terms, cost-to-serve drivers, price or package candidates, research constraints, and source material. Unknown information can remain unknown and be recorded as a gap.

## Install

### Claude Code plugin

Add the marketplace and install the plugin:

```text
/plugin marketplace add C-Kapsalis/value-pricing
/plugin install value-pricing@value-pricing
```

You can also download `value-pricing-plugin.zip` from the [latest GitHub release](https://github.com/C-Kapsalis/value-pricing/releases/latest) and install it locally.

### Codex or another Agent Skills client

Install the skill from the public repository:

```sh
npx skills add C-Kapsalis/value-pricing
```

Alternatively, download the skill archive from a GitHub release and place its `value-pricing/` folder in the client's skills directory. Codex users can add the repository marketplace with `codex plugin marketplace add C-Kapsalis/value-pricing`.

### Local analysis environment

The Python analysis scripts require Python 3.11 or later. Create an environment and install the included requirements:

```sh
uv venv .venv-pricing
uv pip install --python .venv-pricing/bin/python -r <path>/skills/value-pricing/scripts/requirements.txt
```

For JavaScript-heavy sites, install Playwright and its Chromium browser as described in the skill documentation. Some optional language-model workflows use a locally available `claude` command; an API runner is an explicit alternative. Review data-handling notes before sending any business-derived material to a model provider.

## Run

Invoke `/value-pricing [offering context] [source paths…]` or ask, “Help me research pricing for this offering.” Provide relevant source material or paths when available. The skill begins with discovery, scopes the study, and explains method choices and evidence gaps. Scripts are run explicitly by the user or agent after configuration; loading the skill does not start network or model jobs.

## Documentation

- [`skills/value-pricing/SKILL.md`](skills/value-pricing/SKILL.md) — workflow and operating rules.
- [`skills/value-pricing/references/`](skills/value-pricing/references/) — method guidance, evidence standards and output contract.
- [`skills/value-pricing/templates/`](skills/value-pricing/templates/) — configurable study, offering, taxonomy, cost and research templates.
- [`skills/value-pricing/scripts/`](skills/value-pricing/scripts/) — reproducible analysis tools and command help.
- [`PUBLISHING.md`](PUBLISHING.md) — packaging and distribution instructions.

## Limitations

Market listings may be incomplete or incomparable. Models depend on evidence and assumptions, and extrapolation beyond observed data is uncertain. The included analysis scripts implement specific structured methods and may assume a particular data shape, feature comparison, or billing basis; use them only when those assumptions fit, and use a suitable manual analysis otherwise. Simulated buyers are exploratory and are not a substitute for representative human research or observed purchasing behavior. Cost models depend on complete cost-to-serve inputs. Treat estimates as hypotheses, report uncertainty, and validate material decisions with relevant customers and business data.

## Licence

MIT. See [`LICENSE`](LICENSE).

# value-pricing

A Claude Code plugin for a rigorous value-based pricing study of any product or service. Give it a
website (and optionally an Obsidian vault, a docs folder, decks or past artifacts); it builds the
capability vector with evidence, prices it from three sides, estimates each feature's added value,
convenes a council of persona agents, runs a pre-registered simulated-buyer panel, interviews you about
your cost structure, and scores packaging proposals on contribution after people time.

Every price it produces is a **hypothesis** to validate with real buyers. It says so, and phase 7 designs
that validation.

## What's inside

| Path | What |
|---|---|
| `skills/value-pricing/SKILL.md` | the orchestrator: ground rules, workspace, the seven phases with completion criteria |
| `skills/value-pricing/references/` | one file per phase, plus `lessons.md`, `literature.md`, `output-contract.md` |
| `skills/value-pricing/templates/` | `study.yaml`, `offering.yaml`, `taxonomy.yaml`, `value_drivers.yaml`, `costs.yaml`, `proposals.yaml`, `plans.csv`, `vendors.csv`, `preregistration.md`, `DECISIONS.md` |
| `skills/value-pricing/scripts/` | the analysis code (Python 3.11+), each script with `--help` |
| `agents/` | the council: `buyer-persona`, `pricing-strategist`, `cfo-unit-economics`, `behavioral-economist`, `competitive-analyst`, `gtm-sales-lead`, `devils-advocate` |
| `commands/value-pricing.md` | `/value-pricing <url> [paths…]` |

## The method

| Phase | Script(s) | Output |
|---|---|---|
| 1 Intake | `crawl_site.py`, `ingest_corpus.py` | `offering.yaml` with evidence, `taxonomy.yaml`, segments and archetypes ruled by the owner |
| 2 Market | `crawl_site.py --vendors`, `code_features.py`, `llm_batch.py`, `kappa.py`, `hedonic.py`, `value_metric.py` | implied price per segment, market premium per feature, what rivals meter on |
| 3 Value | `value_mc.py` | EVC per segment, **per-feature added value** (share valued, Shapley share, leave-one-out), Sobol |
| 4a Council | the agents | objections, fences, behavioural parameter ranges, verdicts per structure |
| 4b Panel | `conjoint_design.py`, `panel_build.py`, `llm_batch.py`, `panel_analyze.py`, `conjoint_fit.py`, `calibration.py` | pre-registered conjoint WTP, Van Westendorp, Gabor-Granger, anchor effect, level-bias ratio |
| 5 Cost | `cost_model.py` | floor per segment, people time, fixed-cost carry, support minutes per price |
| 6 Synthesis | `synthesize.py`, `optimize_packages.py` | price corridor, feature-value classes, proposals tuned on contribution under every level lens |
| 7 Validation | — | real-buyer survey with decision rules fixed in advance; the owner's rulings |

It grew out of real pricing work; `references/lessons.md` records what that work taught.

## Install

As a plugin: unzip so that `value-pricing/` sits where your Claude Code loads plugins from (or add it
through a local marketplace), then restart Claude Code.

As a bare skill: copy `skills/value-pricing/` to `~/.claude/skills/value-pricing/` and `agents/*.md` to
`~/.claude/agents/`.

Python environment (once per machine):

```bash
uv venv .venv-pricing
uv pip install --python .venv-pricing/bin/python -r <path>/skills/value-pricing/scripts/requirements.txt
# JavaScript-heavy sites: uv pip install playwright && .venv-pricing/bin/playwright install chromium
```

The panel and feature coding call `claude -p` on your Claude plan by default (no API key spend);
`--runner api` uses the Anthropic API when you choose to.

## Use

```
/value-pricing https://yourproduct.com ~/Obsidian/YourVault ./sales-decks
```

or just ask: "price my product", "what should we charge", "design our tiers", "what is each feature
worth to customers". The skill asks before every expensive step and every judgement call.

## Tested

`scripts/selftest.py` runs every analysis script on a synthetic study with planted ground truth (feature
premia, a meter elasticity, simulated buyers with known willingness to pay) and prints PASS/FAIL per
check. Run it once after installing: `.venv-pricing/bin/python <path>/scripts/selftest.py`.

At packaging time the hedonic model recovered all three planted premia inside its 90% intervals, the
meter table recovered the planted elasticity (0.73 vs 0.75), and the HB conjoint recovered the planted
willingness to pay per level within a few euros. The crawler and corpus ingest were run on real material.
A full live study (hundreds of LLM calls for feature coding and the panel) was not run as part of
packaging.

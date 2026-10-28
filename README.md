# value-pricing

[![GitHub stars](https://img.shields.io/github/stars/C-Kapsalis/value-pricing?style=flat-square&label=Stars)](https://github.com/C-Kapsalis/value-pricing/stargazers)
[![Follow C-Kapsalis on GitHub](https://img.shields.io/github/followers/C-Kapsalis?style=flat-square&label=Follow%20C-Kapsalis)](https://github.com/C-Kapsalis)

An open-source agent skill and plugin for a rigorous value-based pricing study of any product or service. Give it a
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

### Claude Code plugin

Add the GitHub marketplace and install the plugin:

```text
/plugin marketplace add C-Kapsalis/value-pricing
/plugin install value-pricing@value-pricing
```

You can also download `value-pricing-plugin.zip` from the
[latest GitHub release](https://github.com/C-Kapsalis/value-pricing/releases/latest)
and install it as a local plugin.

### Codex or another Agent Skills client

Install the skill from the public repository with:

```sh
npx skills add C-Kapsalis/value-pricing
```

Or download `value-pricing-skill.zip` from the
[latest GitHub release](https://github.com/C-Kapsalis/value-pricing/releases/latest)
and place the `value-pricing/` folder in that client's skills directory.
Codex users can also add this repository marketplace with
`codex plugin marketplace add C-Kapsalis/value-pricing` and install the
Value Pricing plugin from the marketplace.

ChatGPT and Codex public directory review uses the
`value-pricing-openai.zip` archive; a public listing is available only after
vendor review and publication.

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
check. Run it once after installing: `.venv-pricing/bin/python <path>/scripts/selftest.py --no-hb`.
It writes to a new temporary directory by default; a supplied `--dir` must not already exist.

At packaging time the hedonic model recovered all three planted premia inside its 90% intervals, the
meter table recovered the planted elasticity (0.73 vs 0.75), and the HB conjoint recovered the planted
willingness to pay per level within a few euros. The crawler and corpus ingest were run on real material.
A full live study (hundreds of LLM calls for feature coding and the panel) was not run as part of
packaging.

## Distribution

See [PUBLISHING.md](PUBLISHING.md) for archive contents, release instructions,
marketplace setup and vendor-directory submission steps.

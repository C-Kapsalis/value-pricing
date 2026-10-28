---
description: Run a value-based pricing study for a product — website and knowledge base in, priced packages out.
argument-hint: <website-url> [vault or docs paths…] [--phase intake|market|value|council|panel|cost|synthesis|validation]
---

Run the `value-pricing` skill for: $ARGUMENTS

Load the skill first and follow its sequence. If a `pricing-study/` folder already exists in the working
directory, read its `DECISIONS.md` and every `*/results/summary.json` first and resume at the first phase
whose completion criterion is not met (or at `--phase` if given). Otherwise start at phase 1 (intake)
with the URL and paths given.

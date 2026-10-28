# Phase 1 · Intake

Turn the business's own material into three files every later phase reads: `offering.yaml` (what is
sold, with evidence), `taxonomy.yaml` (the vocabulary the market uses) and `study.yaml` (who buys, on
which axis they differ).

## 1. Ask for the inputs

One question to the user, with defaults filled in:

- the website URL (required);
- knowledge bases: an Obsidian vault, a docs folder, a Notion/Drive export, past artifacts, sales decks,
  call notes. Any folder of `.md`/`.txt`/`.html`/`.pdf` works;
- known competitors, and the marketplace or category the product is listed in, if any;
- the currency, and whether the product is sold through a channel that takes a cut (app store, marketplace);
- the owner's subjective price anchors, if they have any (two numbers: a low and a high). These become
  **experimental manipulations** in the panel, never price candidates;
- the token budget the owner is willing to spend.

Do not ask for today's prices. If the user volunteers them, record them in `DECISIONS.md` as "known, not
an input".

## 2. Crawl and ingest

```bash
PY=.venv-pricing/bin/python; K=<skill>/scripts
$PY $K/crawl_site.py --study pricing-study --url https://example.com --max-pages 150 --contact you@company.com
$PY $K/ingest_corpus.py --study pricing-study --path ~/Vault --path ./decks
```

- `crawl_site.py` honours robots.txt, waits ≥1 s between requests, sends an identifying user agent,
  resumes from its state file, and prioritises pricing, features, product, integrations, docs,
  customers and case-study pages. It uses Playwright when installed (`--browser`), else plain HTTP.
  An agent with its own browser tool (Playwright MCP, a web-fetch agent) can feed pages in instead:
  save each as `corpus/site/<host>/<slug>.md` with a `url:` front-matter line.
- `ingest_corpus.py` chunks notes into `corpus/index.jsonl` and keeps front matter, headings, tags and
  `[[wikilinks]]`, so a vault's own structure (a "Pricing" folder, a "Customers" tag) survives.
  `corpus/index_stats.json` shows its shape; read that first, then grep the index.

## 3. Build the offering (`offering.yaml`)

Read the corpus and list every capability a buyer could be charged for. Per feature:

- `id` (snake_case, phrased as a listing would advertise it, not an internal name);
- `status`: `yes` | `partial` (gated, managed-only, limited, beta) | `no` (on the roadmap or absent);
- `evidence`: a verbatim quote and its source path or URL;
- `scale_axis: true` when the feature is naturally sold by quantity (seats, sources, projects, orders,
  credits) — record the quantity, not just presence;
- `gates`: ids of features this one unlocks (an integration that makes a report possible). Gates score
  low on direct value and high on market premium; synthesis needs to know which they are.

**The marketing site overstates.** For every `yes` that rests on marketing copy alone, look for a
second source (docs, changelog, the vault, a case study). With none, mark it `partial` and say why in
`evidence`. A pricing study that sells a feature the product cannot deliver today poisons the tier copy.

Also infer and list, each as a sentence the owner can correct:
- the **reference alternative** per buyer type: what they do today instead (a rival, spreadsheets, an
  agency, nothing) and what it costs. EVC is built on it;
- the **moats and weak points**, each with evidence.

## 4. Build the taxonomy (`taxonomy.yaml`)

Start from `templates/taxonomy.yaml`. One list of feature ids that **both** the market coding (phase 2)
and the value drivers (phase 3) use; synthesis joins on the id. Include features the product lacks but
competitors advertise, marked `ours: no`: they are needed to price the market correctly and they are the
roadmap signal. Phase 2 may add ids found on ≥2% of competitors; never rename or delete an id, deprecate it.

Add a `conjoint:` list of the 5–7 attributes buyers would actually trade off (phase 4b's panel). Price
is always one of them.

## 5. Segments and archetypes (`study.yaml`) — owner rules

- **Segment axis.** The quantity that value scales with (orders, ad spend, revenue, seats, sources,
  employees). Propose 4 bands with a `reference_volume` each. The axis that drives value is not always
  the one the market meters on; phase 2 measures the latter and phase 6 picks the meter.
- **Segment shares.** From a real frame if one exists (a CRM, a lead database, a marketplace census);
  otherwise a stated assumption.
- **Archetypes.** 3–5 buyer shapes inside each segment (business model × role). Infer them from case
  studies, customer logos and the vault; give each a role, team, reference alternative (text and
  monthly cost) and the economics that drive value (margin, order value, churn, spend, hourly rate).

Ask the owner to rule the axis, the bands and the archetypes in one question, with your recommendation
first. Record the ruling in `DECISIONS.md`.

Done when every feature in `offering.yaml` carries a quote and a source, `taxonomy.yaml` covers every
offering feature and every competitor feature seen so far, and the owner has ruled the axis and the
archetypes.

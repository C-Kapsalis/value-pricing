# Phase 4b · The silicon panel (pre-registered)

Willingness to pay measured the way marketing science measures it: a **choice-based conjoint** on
respondents conditioned on realistic buyer attributes (a silicon sample, Argyle et al. 2023), estimated
with **hierarchical Bayes MNL**, with **Van Westendorp** and **Gabor-Granger** as secondary instruments,
an **anchor** arm, a **paraphrase** arm, holdout tasks, attention checks and a **level-bias
calibration**. The result is a hypothesis for real buyers, never a measurement of them.

Asking a simulated buyer "what is the most you would pay" is the weakest instrument there is (Miller et
al. 2011 on stated maxima). Use the conjoint.

## 1. Pre-register — before the first respondent

Copy `templates/preregistration.md` to `panel/preregistration.md` and fill it: question, hypotheses with
their tests and pass marks, primary outcome (segment median reservation price for **our**
configuration), attributes and levels, design, sample, stopping rule, exclusion rules, estimation, the
calibration, threats. Commit it (or record its SHA-256 in `DECISIONS.md` when there is no git). Any later
change is a **deviation**, logged with its reason, and the registered analysis is still reported.

## 2. Design

Attributes come from `study.yaml conjoint.attributes` (price first, then 4–6 others, 2–5 levels each,
worst → best). Price levels log-spaced (ratio ≈ 2) and **wide**: put the top level above where you think
the largest segment's WTP is, or that segment is censored and its estimate becomes an extrapolation of the
linear price term.

When the packaging question is *what to meter on*, test the meters directly as attributes (e.g. "3 / 6
/ 12 / 24 integrations connected", "0 / 2 / 5 / 10 / 20 hours of expert time a month") instead of proxies; replace the
proxy attribute, never show both.

```bash
$PY $K/conjoint_design.py --study pricing-study        # panel/design.csv + panel/design_stats.json
$PY $K/panel_build.py     --study pricing-study        # panel/prompts/, panel/manifest.csv (needed by the next line)
$PY $K/conjoint_fit.py    --study pricing-study --recovery-check   # synthetic respondents with known part-worths
```

Default 60 versions × 12 tasks × 3 options + NONE ("keep my current setup"), plus 2 fixed holdouts and a
dominance check (option B is cheapest and best on everything). Paste `design_stats.json` and the
recovery result into the pre-registration's appendix, then commit it.

## 3. Instrument and sample

```bash
$PY $K/llm_batch.py --study pricing-study --dir panel --workers 6 --expect choices,vw,gg
```

- One respondent per call, with nothing else in its context. `llm_batch.py` uses `claude -p` with no
  tools, no MCP, no settings and a one-line system prompt, on the user's plan (≈9k tokens a respondent
  vs ≈60k as a subagent). It strips `ANTHROPIC_API_KEY` unless `--runner api` is chosen by the owner.
- Each persona is asked in every arm cell (anchor low/high × paraphrase 1/2) with byte-identical text
  except the manipulated element (Gui & Toubia), so arm effects are within-persona.
- The prompt shows the persona what the value model flagged for its scenario this month. That is the EVC
  cue, deliberate, and a declared threat: it invites pricing against value.
- Sample: 4 segments × 4 cells × ≥30 = 480 floor; 60 personas per segment (960 calls) target.
- Run long batches detached (`setsid nohup … &`) so a closed session or tool timeout doesn't kill them;
  re-running resumes.

## 4. Analyse

```bash
$PY $K/panel_analyze.py --study pricing-study     # exclusions E1–E5, Van Westendorp, Gabor-Granger
$PY $K/conjoint_fit.py  --study pricing-study [--wtp-space]   # HB-MNL, WTP per level, reservation price, posteriors
```

Report: WTP per level and segment; reservation price for our configuration (median, p25–p75); holdout
hit rate vs chance; WTP-space check; VW points (PMC, OPP, IPP, PME); GG curve and revenue-maximising
price; anchor and paraphrase effects; never-buyer share per segment; every exclusion with its rule.
HB on 960 respondents takes 30–60 min of CPU; without numpyro the script falls back to a conditional
logit with a persona bootstrap and says so.

## 5. Calibrate the level, never apply it

```bash
$PY $K/calibration.py --study pricing-study build --sets sets.csv --template template.txt --reps 20
$PY $K/llm_batch.py   --study pricing-study --dir panel/calibration
$PY $K/calibration.py --study pricing-study fit --attribute fluoride --human 3.27
```

Re-run a published human study with known results on the same model and settings. The reference is
Brand, Israeli & Ngwe's toothpaste conjoint (fluoride WTP $3.27 in the pilot, $2.60 in Study 1A);
reproduce **their** choice sets and **their** verbatim prompt from the paper's appendix (a paraphrase is
a different instrument). The paper itself finds the ratio
unstable across prompts and models (1.04–3.2), so report it as a range and carry its upper end into
`study.yaml lenses.calibration_ratio`: phase 6 scores every proposal at ×1 and ÷ratio. Never divide the
headline numbers by it silently.

## What to expect (and say)

- Silicon respondents tend to price close to the value they were shown, far above the 10–30% a seller can
  usually capture. Read the conjoint level as an optimistic ceiling; the EVC × 10–30% band is the
  conservative one.
- Expect the anchor to move choice-based WTP too, not only the stated instruments. Lead listings with the
  headline tier.
- The paraphrase effect is a floor on instrument noise; report it beside every WTP.
- No never-buyers at any price is **variance compression**, not a finding. Real populations hold a tail
  that never pays.
- Gabor-Granger monotonicity rules can wrongly exclude respondents who read a low price as "too cheap to
  be serious", and this hits the largest segments hardest. `panel_analyze.py` writes a
  binary-only variant beside the registered one; label it exploratory.

Done when every panel key of the output contract is filled, every exclusion is in
`panel/data/exclusions.csv` with its rule, and every deviation is logged against the pre-registration.

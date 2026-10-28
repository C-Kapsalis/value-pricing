# Lessons

What running this method on real pricing studies taught. Each lesson changed what the method does.
Read it before phase 2 and again before phase 6.

## Inputs and setup

- **Today's prices stay out.** When current prices and old draft tiers are inputs to nothing, the
  corridor lands where the evidence puts it, not where an unratified number pulled it.
- **Terms before crawl.** Marketplaces often forbid automated access in their terms. Stop, lay out the
  options, and let the owner make the risk call; a silent workaround is the agent making a call that
  isn't its to make.
- **One worktree (or folder) per parallel stream.** Two sessions in one git checkout share one HEAD and
  commit onto each other's branches.
- **Marketing copy overstates.** Features a site advertises are often partial in the product: a metric
  that computes but returns nothing useful, alerts that are on-demand rather than pushed, a capability
  that exists only through an integration. Tier copy built on them promises what doesn't ship.

## Market

- **List prices explain little.** Out-of-sample R² around 0.2 is normal. Report it; the model is a
  reference, not a price.
- **More features than any rival breaks OLS.** A broad product can carry more coded features than every
  priced competitor; OLS then extrapolates and reads high. Lasso shrinkage and coverage neighbours bound it.
- **Rank rivals by coverage, not Jaccard.** Jaccard punishes broad suites that cover everything you do.
- **The reference doesn't scale with volume** when most rivals' plans don't. For the smallest buyers
  the reference is the feature set's price at a typical middle tier, not what a small buyer pays.
- **Model-to-model κ is acceptable** when hundreds of vendors × dozens of features can't be hand-coded
  honestly: two models, independently written codebooks.

## Value

- **Behaviour carries the ceiling.** Action rate, realisation and capture share usually explain most of
  the value variance; the value formulas' own coefficients very little. Validate behaviour before price.
- **Value scales far more than price does.** Delivered value can span two orders of magnitude from the
  smallest to the largest segment while the market reference barely moves. One flat price can't fit that.
- **Gates look worthless on direct value.** An integration that every valuable insight depends on can
  fire almost no value of its own yet carry the largest market premium. Leave-one-out shows it;
  share-of-scenarios hides it.
- **Value differs in kind by segment.** Small buyers tend to buy time saved; larger buyers buy revenue
  retained and margin protected. That split writes the tier copy.

## Panel

- **Stated maximum is the weakest instrument.** Asking a simulated buyer for their maximum price is
  what the conjoint replaces.
- **Silicon buyers are optimistic in level.** They price close to the value they are shown, far above the
  10–30% sellers usually capture. Calibrate on a published human benchmark, report the ratio as a range,
  carry it as a lens, never apply it silently.
- **The anchor moves choices too**, not only stated answers. Lead the listing with the headline tier;
  present cheaper tiers as discounts beneath it.
- **Zero never-buyers is compression, not good news.**
- **A pre-registered exclusion can be wrong.** A Gabor-Granger monotonicity rule can drop buyers who read
  a low price as "too cheap to be serious", mostly in the largest segments. Keep the registered result;
  report a labelled exploratory variant beside it.
- **A top price level that is too low censors the top segment.** Put the highest level above where the
  largest buyers would plausibly stop.
- **Test meters as attributes.** "N sources available" (catalogue breadth) is not "N sources connected"
  (the meter). When the packaging question is the meter, amend the design to test the meter itself.

## Cost

- **Infrastructure is rarely the floor** for software. Variable cost per customer is often a few units of
  currency a month; people time (support, onboarding, done-for-you work) is the real floor, and usually
  the one nobody has measured.
- **Fixed cost ÷ customers is a volume target.** As a per-customer floor it can sit above every
  segment's ceiling; as "N paying customers carry the platform" it is useful.
- **Fences need billing to enforce them.** Customers billed through a channel can fall through to
  "everything allowed". Check enforcement before ratifying a fence.
- **Seasonal volume needs a trailing average.** A volume meter billed on a single month punishes a
  seasonal business and invites churn.

## Synthesis and packaging

- **Meter on what the market meters on.** The quantity value scales with is often one almost no rival
  meters on. Keep it as the segment descriptor and the sales conversation; meter on what buyers already
  accept being charged for.
- **Extras from the elasticity, not by division.** Dividing a feature's premium by the number of unit
  types badly understates what the market charges per extra unit.
- **Multi-unit from the market curve.** The owner's intuition ("less than 2× for a second store") is
  usually right; the brands/properties elasticity gives the curve to price it.
- **Two structures can tie.** Capability tiers and usage bands often land within a few percent on every
  lens, and the owner may pick the one synthesis didn't recommend, for reasons synthesis can't see.
  Present the trade and the survey result that would separate them.
- **Score on contribution under every lens.** A proposal that wins only under the optimistic lens
  (perfect fencing, silicon level) is an artefact.
- **On the measured attributes, a product can be indistinguishable from cheaper rivals.** Then it has
  to win on something the conjoint didn't measure; name what, and estimate what it must be worth.

## Running it

- **Keep the study on persistent disk.** A machine or VM restart clears `/tmp` and kills running jobs.
- **Run long jobs detached** (`setsid nohup … &`) and make them resumable; plan session limits interrupt
  long panels, and a resumable runner reruns only what's missing.

# Demand elasticity launch kit

Draft copy for the Bayesian demand analysis in PR #2. Publish after the feature is merged and the release is live. Release notes are left to the maintainer.

## Core message

**Headline:** Add observed purchasing behavior to your pricing evidence.

**One sentence:** Value Pricing can now use historical transaction CSVs to estimate how transaction quantities vary with realised unit prices across customer segments, with Bayesian uncertainty and explicit diagnostic limits.

**Who it helps:** Founders, pricing teams and analysts who have transaction records and need to compare behavioral evidence with the existing market, cost and customer-value views.

**Three points to repeat:**

1. The model returns a posterior price-elasticity estimate and 90% credible interval for each product and segment.
2. It shows conditional transaction-quantity scenarios at 0.8×, 1.0× and 1.2× a reference observed price, along with price-variation, convergence and model-fit diagnostics.
3. Results from ordinary historical transactions are observational associations. A causal claim needs a defensible experiment or other identification design.

## Website or repository feature block

### Learn from the prices customers actually paid

Competitor plan cards show what the market lists. Your transaction history shows what customers paid and how many units they bought. Value Pricing now analyzes that history as a separate source of pricing evidence.

Supply a CSV with transaction date, product, customer, segment, realised unit price and quantity. A Bayesian model estimates price response by segment with partial pooling, annual seasonality and available promotion, channel and contract-duration controls. The output includes 90% credible intervals, price scenarios and checks for sparse price variation, sampler convergence and predictive fit.

The analysis describes quantity **conditional on an observed transaction**. It does not measure purchase incidence or establish that a price change caused demand to change.

**CTA:** [See the data requirements and method](https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md)

## Announcement post

Value Pricing now has a Bayesian demand analysis for historical transactions.

If you have transaction records, you can add realised unit prices and quantities to a pricing study. The new model estimates price response by product and customer segment, partially pooling information across segments. It reports a posterior estimate, a 90% credible interval, conditional quantity scenarios and diagnostics for price variation, convergence and fit.

This adds a different kind of evidence to the existing workflow. The competitor meter analysis asks how rivals' listed prices change with plan limits. The new analysis asks how quantities on observed customer transactions vary with realised prices. Synthesis keeps those results separate.

Historical prices can reflect expected demand, discounts or customer selection. The output is labeled observational, and the method documents what would be needed for a causal interpretation. It also makes clear that transaction rows alone cannot measure purchases that never occurred.

The feature is open source in Value Pricing: [method and CSV schema](https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md).

## Email

**Subject:** New in Value Pricing: learn from transaction price and quantity

**Preheader:** Bayesian segment estimates, 90% credible intervals and clear identification limits.

Value Pricing can now analyze historical transaction CSVs alongside its market, cost and customer-value evidence.

The new demand model estimates how purchased quantities vary with realised unit prices by product and customer segment. You get posterior elasticity estimates, 90% credible intervals, price scenarios and diagnostics that flag weak price variation or model problems.

This is a way to organize behavioral evidence, not a claim that historical price differences caused demand to change. The method labels observational results and explains the missing-purchase and price-endogeneity limits.

See the [input schema and method](https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md).

## Social posts

### LinkedIn: practitioner angle

Pricing teams often have two different questions:

• How do competitors' listed prices scale with plan limits?
• How does purchased quantity vary with the price customers actually paid?

Value Pricing now addresses the second question with a Bayesian model for historical transaction data. It returns segment estimates, 90% credible intervals, price scenarios and checks for variation, convergence and fit. Synthesis keeps this evidence separate from competitor meter elasticity.

The results are observational unless a credible identification design supports a causal claim. Transaction-only data also leave non-purchases unobserved.

Method and CSV schema: https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md

### LinkedIn: builder angle

We've added transaction-based demand analysis to Value Pricing.

It accepts a CSV of dates, products, customers, segments, realised prices and quantities. A hierarchical Bayesian model estimates price response across segments and reports uncertainty, scenarios and diagnostics. It can use promotion, channel and contract-duration controls when those fields are available.

The first thing the output tells you is what the data can and cannot support. Sparse price variation is flagged. Historical price/quantity patterns are labeled observational. Purchase incidence needs data on non-purchases too.

Code and method: https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md

### Short post (X, Bluesky or Mastodon)

New: Bayesian quantity response to price by segment in Value Pricing. 90% credible intervals and diagnostics. Observational; non-purchases are unseen. Method: https://github.com/C-Kapsalis/value-pricing/blob/main/skills/value-pricing/references/9-demand-elasticity.md

## 60-second demo outline

1. Show the six required CSV columns: `date`, `product`, `customer`, `segment`, `realised_unit_price`, `quantity`. Say that the prices must be in the study currency and quantities must be positive whole units.
2. Run `demand_elasticity.py --study S` on a synthetic study. If using the Second Read Studio fixture from `selftest.py`, place **SYNTHETIC DATA** on screen and say that neither its prices nor quantities are real product or customer records.
3. Point to one segment's posterior estimate and 90% credible interval, then the 0.8×, 1.0× and 1.2× price scenarios. Describe them as conditional model responses for observed transactions.
4. Show the price-variation, R-hat, effective-sample-size, divergence and posterior-predictive checks. A failed check is a reason to investigate the estimate.
5. End on `synthesis/data/demand_elasticity.json`, alongside but separate from `market/results/summary.json` and its competitor meter analysis.

**Closing line:** “This is another piece of pricing evidence, with its uncertainty and identification limits visible.”

## FAQ

**Does the model estimate causal price elasticity?** No. It reports observational price/quantity associations. Controlled experiments or another defensible identification design are needed before making a causal claim.

**Can it predict how many customers will buy at a new price?** No. Transaction rows contain observed purchases, not the full set of customers and periods with zero purchases. The scenarios describe expected quantity conditional on an observed transaction and on the modeled controls.

**What input is required?** A CSV with date, product, customer, segment, positive realised unit price and positive whole-unit quantity. Promotion, channel and contract duration are optional controls.

**What does partial pooling do?** It lets segment estimates share information through a population-level slope. It cannot create price variation where a segment has none; the output flags weak segment support.

**What does a 90% credible interval mean?** It is an interval from the model's posterior distribution, conditional on its likelihood, priors and supplied data. It does not repair confounding or guarantee a causal effect.

**How is this different from Value Pricing's competitor meter elasticity?** The meter analysis measures how competitors' listed plan prices scale with plan quantities. The demand analysis uses realised prices and quantities from customer transactions. They remain separate in synthesis.

**Are the Second Read Studio numbers real?** No. The test fixture borrows audience labels for a fully synthetic example. Prices, quantities and customers are invented, and no billing data are read.

## Graphic use

`demand-elasticity-social-card.png` is the ready-to-upload 1200 × 630 share card; the matching SVG is its editable source. Its chart is conceptual and contains no estimated data points. Suggested alt text: “Value Pricing graphic reading ‘Bayesian demand elasticity’ above a conceptual price-response chart, with ‘90% credible intervals’ and ‘Observational evidence’ called out.”

## Claim checks before publishing

- Use “observational association” when describing historical price effects; do not say the tool proves a causal lift.
- Say “transaction quantity conditional on an observed purchase”; do not imply that conversion, purchase incidence or total market demand are estimated.
- Mark the Second Read Studio demonstration as synthetic in captions, screenshots and spoken narration.
- Keep the competitor meter analysis and transaction demand analysis distinct.
- Link to the method after the PR is merged, then check that the link resolves before posting.

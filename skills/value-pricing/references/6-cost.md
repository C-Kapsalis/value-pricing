# Phase 5 · Cost (the floor) — the cost interview

Cost is a floor, never the price (Nagle). This phase turns the owner's cost structure into: variable
cost per customer per segment, fixed platform cost, **people time per customer** (usually the real
floor), and the channel's cut. Packages are then tuned on **contribution**, not revenue.

## 1. Interview the owner

The owner knows these numbers or knows where they are; the agent does not. Ask in **two questions at
most** (AskUserQuestion, or a short list), offering "I don't know — estimate it and mark it" on each:

1. **Where the costs are.** Which of these exist, and where the figures live (invoice, billing export,
   dashboard, a guess): hosting and compute, storage, data/API/LLM usage per customer, third-party
   licences per customer, payment processing, channel or marketplace cut, support, onboarding, account
   management, managed services, fixed platform (tooling, capacity, base infra), sales cost per deal.
2. **People time.** Hours per customer per month for support, onboarding (one-off), and any
   done-for-you work, by segment if it differs; and the loaded hourly rate.

Then read whatever they pointed at (an invoice PDF, a billing CSV, a cloud billing export, a time log),
**read-only**. Where usage per customer can be measured (jobs per account, storage per tenant, tokens
per org), measure it: a small driver regression across real customers (cost on integrations and data
volume, say) beats any allocation rule. Put it in
`cost/data/per_customer.csv` (a `cost` column plus numeric driver columns) and point
`costs.yaml driver_regression.file` at it.

Write everything into `costs.yaml` (template `templates/costs.yaml`): each line with its amount,
`kind: variable | fixed`, the driver it scales with, and `source` (a file, a query, "owner estimate", or
a gap entry). People time and the channel cut have their own blocks.

## 2. Compute

```bash
$PY $K/cost_model.py --study pricing-study
```

Per segment: variable cost per customer (point and 90% interval from the regression bootstrap), people
cost per customer, the channel cut as a share of price, and:

- **floor price** at gross-margin targets 70 / 80 / 85% on variable + people + channel;
- **fixed-cost carry**: paying customers needed to carry the fixed platform at each candidate price.
  Fixed cost ÷ current customers is a **volume target**, not a per-customer floor — as a price floor it
  can sit above every segment's ceiling and mean nothing;
- **support budget**: minutes of people time per customer per month each candidate price affords at
  the target margin. A low tier that affords one minute a month can only exist fully self-serve.

## 3. Channel and billing facts

If the product sells through a marketplace or app store, read its current partner terms: revenue share
(often tiered by lifetime revenue), processing fees, whether price changes need customer approval,
whether a 100% discount or a trial is allowed, currency rules. And check **whether billing can enforce
the fences** the proposals will use: customers billed through a channel can fall through to "every
feature allowed", leaving every fence decorative until a build ships.

Done when `costs.yaml` splits every line into variable / fixed / people / channel with a source or a
stated gap, people time has a number or an explicit range, and `cost/results/summary.json` holds the
floor, carry and support budget per segment.

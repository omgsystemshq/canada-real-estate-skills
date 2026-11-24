---
name: buyer-closing-costs
description: Add up the cash an Ontario home buyer needs on closing day besides the down payment, using real quotes for fees and calculated taxes. Use when a buyer asks how much they need for closing costs in Ontario.
---

# Buyer closing costs (Ontario)

Closing costs are the money a buyer pays on closing day on top of the down payment. Buyers who forget them can come up short at the worst moment.

This skill is honest on purpose. It works out the taxes itself (land transfer tax, and the sales tax on mortgage insurance). For everything else, like the lawyer and title insurance, it only uses numbers from a real quote. It never fills in a guess. Anything missing is listed under `still_needed`, and the total says it is not complete.

## When to use it

- "How much cash do I need to close?"
- "What are closing costs on a $650,000 condo in Ajax?"
- Building a buyer budget.

## What to ask first

1. Price and down payment.
2. City of Toronto or not.
3. First-time buyer share (see the land transfer tax skill).
4. Amortization, if the down payment is under 20%.
5. Is it a condo? Is it a new build? Is every buyer a Canadian citizen or permanent resident?
6. Any quotes they already have: lawyer, title insurance, home inspection, home insurance, adjustments, plus any that apply (appraisal, condo status certificate review, lender fees, interim interest, moving).

## How to run it

```
python3 skills/buyer-closing-costs/closing_costs.py 650000 45000 --legal-fees 1900 --title-insurance 400 --home-inspection 550 --home-insurance 1500 --adjustments 1200
```

## How to explain the answer

Lead with the total and whether it is complete:

> On a $650,000 home with $45,000 down, you need $16,961 in cash on closing day besides your down payment. That covers the land transfer tax, the sales tax on your mortgage insurance, and the quotes you gave me.

If `still_needed` is not empty, say so plainly and list what to get quotes for. Never give a partial total as if it were the whole thing.

A first-time buyer or a new-build buyer who wants 30 years must add `--first-time-or-new-build`. `--first-time-share` and `--new-build` do not turn on 30 years by themselves; they are separate on purpose.

Home insurance and title insurance are listed because almost every lender asks for them. If a deal truly has no mortgage or no title policy, enter 0 for that line. The example numbers here are made up to show the format; use real quotes.

This skill uses the land transfer tax and mortgage default insurance skills. Commands run from the top of the repo. If you copy it into an agent, copy all three folders side by side.

## What this skill does not cover

- Buyers who are not Canadian citizens or permanent residents (`--non-resident` makes it refuse, with the reason).
- The full cost list for new builds (`--new-build` adds a warning).

## Good to tell every buyer

- The down payment and closing costs are separate piles of money.
- Adjustments are often a surprise: if the seller prepaid property tax or condo fees, the buyer pays them back.
- The lawyer's statement of adjustments, a few days before closing, is the final number.

This is an estimate for planning, not legal or financial advice.

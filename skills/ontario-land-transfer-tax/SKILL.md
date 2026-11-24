---
name: ontario-land-transfer-tax
description: Work out Ontario land transfer tax, the City of Toronto's extra municipal tax, and first-time buyer refunds for a home purchase. Use when someone asks how much land transfer tax they will pay in Ontario or Toronto.
---

# Ontario land transfer tax

Every buyer in Ontario pays land transfer tax on closing day. Buyers in the City of Toronto pay a second, municipal tax on top. First-time buyers can get some or all of it back.

## When to use it

- "How much land transfer tax on a $750,000 home in Whitby?"
- "What do I pay in Toronto as a first-time buyer?"
- Any closing cost or budget question that needs the tax.

## What to ask first

Ask only what you do not already know, in one message:

1. The purchase price.
2. Is the home in the City of Toronto? (Toronto only. Mississauga, Markham and Durham do not charge the municipal tax.)
3. Is every buyer a Canadian citizen or permanent resident? If not, stop: this skill does not cover that buyer (see below).
4. Is every buyer a first-time buyer? If only some are, what share of the home are the first-time buyers getting? Careful with spouses: if a buyer's spouse owned a home anywhere while they were married, Ontario gives no refund at all. Only ask for a share when the non-qualifying buyer is someone else (for example a parent on title). The lawyer confirms.
5. Is it one or two single family homes? (Almost always yes. A 3-plex or bigger is "no".)

## How to run it

```
python3 skills/ontario-land-transfer-tax/ltt.py 750000
python3 skills/ontario-land-transfer-tax/ltt.py 900000 --toronto --first-time-share 1
python3 skills/ontario-land-transfer-tax/ltt.py 2400000 --not-single-family
```

Or call `land_transfer_tax(price, in_toronto, first_time_buyer_share, one_or_two_single_family_homes)` from Python.

## How to explain the answer

Lead with the one number they care about (the total after refunds), then show the parts:

> On a $900,000 home in Toronto you would pay $14,475 to Ontario and $14,475 to the City, $28,950 in total. As first-time buyers you get $4,000 and $4,475 back, so you pay $20,475.

## Rules worth knowing

- The tax is charged in slices. Each slice of the price has its own rate, like income tax.
- Ontario's top 2.5% slice (over $2,000,000) only applies to land with one or two single family homes. Other land stays at 2.0%.
- Toronto added higher slices above $3,000,000 for one or two single family homes on April 1, 2026.
- Ontario refunds up to $4,000. Toronto rebates up to $4,475. Both shrink by the share bought by people who are not first-time buyers.
- First-time buyer rules have conditions (age, residency, living in the home, never having owned a home anywhere, a spouse who owned a home while you were married). Always tell the buyer their lawyer confirms whether they qualify.

## What this skill does not cover

- **Buyers who are not Canadian citizens or permanent residents.** Ontario charges a Non-Resident Speculation Tax on top, and a federal ban stops most non-Canadians buying homes. Run with `--non-resident` and the tool will refuse and say why. Send them to a lawyer.
- **New builds.** The tax base on a new home can include HST and other items. Ask the builder's lawyer.

## Keep it current

Rates and sources are in `rates.json`, with the date they were last checked. If that date is more than a few months old, check the two government pages listed there before you trust the numbers.

This is an estimate for planning. It is not legal or tax advice. The lawyer on the deal works out the final amount.

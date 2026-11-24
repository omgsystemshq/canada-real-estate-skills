---
name: mortgage-default-insurance
description: Estimate Canadian mortgage default insurance for a home purchase with less than 20% down, including the minimum down payment, the 30-year option and the sales tax due at closing. Use when someone asks what insurance costs on a low down payment mortgage in Canada.
---

# Mortgage default insurance (Canada)

If a buyer puts down less than 20%, the lender must insure the mortgage. The buyer pays for that insurance. It is usually added to the mortgage, but in some provinces there is sales tax on it that must be paid in cash at closing.

## When to use it

- "I have $40,000 down on a $600,000 home. What does insurance cost?"
- "What's the least I can put down on $850,000?"
- Any closing cost question with less than 20% down.

## What to ask first

1. Purchase price.
2. Down payment amount.
3. Amortization: 25 years, or 30 years? (30 is only for first-time buyers or a newly built home.)
4. Is any of the down payment borrowed? That is called a non-traditional down payment.
5. Province (for the sales tax on the premium).

## How to run it

```
python3 skills/mortgage-default-insurance/insurance.py 600000 40000
python3 skills/mortgage-default-insurance/insurance.py 550000 55000 --years 30 --first-time-or-new-build
python3 skills/mortgage-default-insurance/insurance.py 700000 35000
```

## How to explain the answer

> With $40,000 down on $600,000, your mortgage is $560,000, which is 93.33% of the price. The insurance is 4.00% of that, $22,400, added to your mortgage. Ontario charges 8% sales tax on it, $1,792, which you pay at closing.

If `can_insure` is false, say why in plain words and what would fix it (more down, a lower price, a shorter amortization).

## Rules worth knowing

- Minimum down payment: 5% of the first $500,000 and 10% of the part above it.
- The price must be below $1,500,000 to be insured. At or above that, the buyer needs 20% down.
- The premium is a share of the loan, based on how much of the price is borrowed. Bigger down payment, smaller rate.
- A 30-year amortization adds 0.20% to the rate.
- The rates here are from the government-backed insurer's published schedule. The two private insurers set their own, usually close. The lender picks the insurer.

## Keep it current

Rates, the price cap and sources are in `rates.json`, with the date last checked. Check the source pages if that date is old.

This is an estimate for planning. It is not financial advice. The lender confirms the final premium.

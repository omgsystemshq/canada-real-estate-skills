"""Mortgage default insurance for a home purchase in Canada (homeowner, 1 to 4 units, owner lives there).

Premium rates checked on 2026-11-24 against the published CMHC schedule (see rates.json).
The other two insurers publish their own rates, which can differ a little.
This is an estimate for planning. The lender confirms the final premium.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RATES = json.loads((Path(__file__).with_name("rates.json")).read_text())
CENT = Decimal("0.01")


def _money(x) -> Decimal:
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)


def minimum_down_payment(price) -> Decimal:
    """5% of the first $500,000, 10% of the part above it. Insured only below the price cap."""
    price = Decimal(str(price))
    first = min(price, Decimal("500000"))
    rest = max(price - Decimal("500000"), Decimal("0"))
    return _money(first * Decimal("0.05") + rest * Decimal("0.10"))


def premium(
    price,
    down_payment,
    amortization_years: int = 25,
    first_time_or_new_build: bool = False,
    non_traditional_down_payment: bool = False,
    province: str = "ON",
) -> dict:
    price = Decimal(str(price))
    down = Decimal(str(down_payment))
    if not price.is_finite() or price <= 0:
        raise ValueError("price must be a number more than 0")
    if not down.is_finite():
        raise ValueError("down payment must be a number")
    if not 1 <= int(amortization_years) <= 40:
        raise ValueError("amortization must be between 1 and 40 years")
    if down < 0 or down > price:
        raise ValueError("down payment must be between 0 and the price")

    if province.upper() not in RATES["province_codes"]:
        raise ValueError(f"unknown province code {province!r}; use one of {', '.join(RATES['province_codes'])}")
    problems: list[str] = []
    cap = Decimal(str(RATES["insured_price_cap_below"]))
    loan = price - down
    ltv = loan / price  # loan-to-value, before the premium is added

    if ltv <= Decimal("0.80"):
        return {
            "insurance_needed": False,
            "why": "20% or more down, so default insurance is not required (a lender may still ask for it).",
            "loan_before_premium": str(_money(loan)),
        }

    if price >= cap:
        problems.append(f"Price must be below ${cap:,.0f} for an insured mortgage. "
                        f"You need 20% down (${_money(price * Decimal('0.20')):,.2f}).")
        return {"insurance_needed": True, "can_insure": False, "problems": problems,
                "minimum_down_payment": str(_money(price * Decimal("0.20")))}
    min_down = minimum_down_payment(price)
    if down < min_down:
        problems.append(f"Down payment is below the minimum of ${min_down:,.2f} for this price.")
    max_years = 30 if first_time_or_new_build else 25
    if amortization_years > max_years:
        problems.append(f"Insured amortization is at most {max_years} years for this buyer.")

    rate = None
    for band in RATES["homeowner_purchase"]:
        if ltv <= Decimal(str(band["ltv_up_to"])):
            rate = Decimal(str(band["rate"]))
            break
    if rate is None:
        problems.append("Loan is more than 95% of the price. That cannot be insured.")
        return {"insurance_needed": True, "can_insure": False, "problems": problems}

    if non_traditional_down_payment and ltv > Decimal("0.90"):
        rate = Decimal(str(RATES["non_traditional_90_95"]))
    if amortization_years > 25:
        rate += Decimal(str(RATES["over_25_year_surcharge"]))

    if problems:
        return {"insurance_needed": True, "can_insure": False, "problems": problems,
                "minimum_down_payment": str(min_down),
                "note": "No premium shown, because this mortgage cannot be insured as entered."}

    prem = _money(loan * rate)
    prov = province.upper()
    if prov not in RATES["province_codes"]:
        raise ValueError(f"unknown province code {province!r}; use one of {', '.join(RATES['province_codes'])}")
    taxed = RATES["provincial_sales_tax_on_premium"]
    pst = str(_money(prem * Decimal(str(taxed[prov])))) if prov in taxed else None
    return {
        "insurance_needed": True,
        "can_insure": True,
        "problems": [],
        "minimum_down_payment": str(min_down),
        "loan_to_value": f"{(ltv * 100).quantize(Decimal('0.01'))}%",
        "premium_rate": f"{(rate * 100).quantize(Decimal('0.01'))}%",
        "loan_before_premium": str(_money(loan)),
        "premium": str(prem),
        "loan_with_premium": str(_money(loan + prem)),
        "sales_tax_on_premium_paid_at_closing": pst if pst is not None else "not in our table, ask the lender",
        "rates_checked": RATES["checked"],
        "note": "The premium is usually added to the mortgage. The sales tax on it cannot be, so it is paid at closing.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Canadian mortgage default insurance estimate")
    p.add_argument("price", type=float)
    p.add_argument("down_payment", type=float)
    p.add_argument("--years", type=int, default=25, help="amortization in years (default 25)")
    p.add_argument("--first-time-or-new-build", action="store_true", help="allows a 30-year amortization")
    p.add_argument("--non-traditional", action="store_true", help="down payment is borrowed (non-traditional)")
    p.add_argument("--province", default="ON", help="two-letter province code (default ON)")
    a = p.parse_args()
    print(json.dumps(premium(a.price, a.down_payment, a.years, a.first_time_or_new_build,
                             a.non_traditional, a.province), indent=2))


if __name__ == "__main__":
    main()

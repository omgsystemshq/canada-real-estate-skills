"""Buyer closing costs for an Ontario home purchase.

The taxes are worked out from the land transfer tax and default insurance skills.
Everything else (legal fees, title insurance, inspection and so on) is a number YOU
enter from a real quote. This tool never guesses those amounts. Anything you leave
blank is listed under "still_needed" so nobody mistakes a partial total for the full one.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ontario-land-transfer-tax"))
sys.path.insert(0, str(HERE.parent / "mortgage-default-insurance"))
from ltt import land_transfer_tax  # noqa: E402
from insurance import premium  # noqa: E402

CENT = Decimal("0.01")

# Costs the buyer usually pays that only a real quote can price.
QUOTED_ITEMS = {
    "legal_fees": "Lawyer's fee plus their costs (searches, registration), with HST",
    "title_insurance": "Title insurance policy",
    "home_inspection": "Home inspection",
    "appraisal": "Appraisal, if the lender charges for it",
    "status_certificate_review": "Condo status certificate review (condos only)",
    "adjustments": "Prepaid property tax, condo fees or utilities you pay the seller back for",
    "home_insurance": "Home insurance (the lender needs proof before closing)",
    "lender_fees": "Lender or broker fees, if any",
    "interim_interest": "Interim interest, if the mortgage starts before its first regular payment date",
    "moving": "Movers or truck rental",
}
OPTIONAL = {"appraisal", "status_certificate_review", "lender_fees", "interim_interest", "moving"}


def _money(x) -> Decimal:
    return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)


def closing_costs(
    price,
    down_payment,
    in_toronto: bool = False,
    first_time_buyer_share: float = 0.0,
    one_or_two_single_family_homes: bool = True,
    amortization_years: int = 25,
    first_time_or_new_build: bool = False,
    quotes: dict | None = None,
    condo: bool = False,
    new_build: bool = False,
    non_traditional_down_payment: bool = False,
    all_buyers_canadian_or_pr: bool = True,
) -> dict:
    quotes = quotes or {}
    if not all_buyers_canadian_or_pr:
        return {"covered": False,
                "why": ("A buyer who is not a Canadian citizen or permanent resident can owe Ontario's "
                        "Non-Resident Speculation Tax and may be barred by the federal ban on non-Canadians "
                        "buying homes. This tool does not cover that. Talk to a lawyer.")}
    unknown = set(quotes) - set(QUOTED_ITEMS)
    if unknown:
        raise ValueError(f"unknown cost items: {sorted(unknown)}")
    for k, v in quotes.items():
        if v is not None and Decimal(str(v)) < 0:
            raise ValueError(f"{k} cannot be negative")

    ltt = land_transfer_tax(price, in_toronto, first_time_buyer_share, one_or_two_single_family_homes)
    ins = premium(price, down_payment, amortization_years, first_time_or_new_build,
                  non_traditional_down_payment, province="ON")
    if ins.get("insurance_needed") and not ins.get("can_insure"):
        return {"covered": True, "complete": False, "insurance": ins,
                "why": "This mortgage cannot be insured as entered. Fix the problems listed under insurance first."}

    lines = [
        {"item": "Land transfer tax (after any first-time buyer refund)", "amount": ltt["total_after_refunds"],
         "source": "calculated"},
    ]
    if ins.get("insurance_needed"):
        lines.append({"item": "Sales tax on mortgage default insurance (cannot go on the mortgage)",
                      "amount": ins.get("sales_tax_on_premium_paid_at_closing", "0.00"), "source": "calculated"})

    still_needed = []
    for key, label in QUOTED_ITEMS.items():
        if key in quotes and quotes[key] is not None:
            lines.append({"item": label, "amount": str(_money(quotes[key])), "source": "your quote"})
        elif key not in OPTIONAL or (key == "status_certificate_review" and condo):
            still_needed.append(label)

    total = sum(Decimal(l["amount"]) for l in lines)
    warnings = []
    if new_build:
        warnings.append("New builds can carry extra costs this tool does not cover (HST items, development "
                        "charges, warranty enrolment and more). Ask the builder's lawyer for the full list.")
    return {
        "covered": True,
        "warnings": warnings,
        "cash_needed_at_closing_besides_down_payment": str(_money(total)),
        "complete": not still_needed,
        "lines": lines,
        "still_needed": still_needed,
        "down_payment": str(_money(down_payment)),
        "insurance": ins,
        "note": ("Not complete until every item in still_needed has a real quote."
                 if still_needed else "All required items are filled in. Still an estimate; the lawyer's statement is final."),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Ontario buyer closing costs")
    p.add_argument("price", type=float)
    p.add_argument("down_payment", type=float)
    p.add_argument("--toronto", action="store_true")
    p.add_argument("--first-time-share", type=float, default=0.0)
    p.add_argument("--not-single-family", action="store_true")
    p.add_argument("--years", type=int, default=25)
    p.add_argument("--first-time-or-new-build", action="store_true", help="allows a 30-year amortization")
    p.add_argument("--condo", action="store_true", help="the home is a condo (status certificate review needed)")
    p.add_argument("--new-build", action="store_true", help="the home is newly built (adds a warning)")
    p.add_argument("--non-traditional", action="store_true", help="part of the down payment is borrowed")
    p.add_argument("--non-resident", action="store_true", help="a buyer is not a Canadian citizen or PR")
    for key in QUOTED_ITEMS:
        p.add_argument(f"--{key.replace('_', '-')}", type=float, default=None)
    a = p.parse_args()
    quotes = {k: getattr(a, k) for k in QUOTED_ITEMS if getattr(a, k) is not None}
    print(json.dumps(closing_costs(a.price, a.down_payment, a.toronto, a.first_time_share,
                                   not a.not_single_family, a.years, a.first_time_or_new_build, quotes,
                                   a.condo, a.new_build, a.non_traditional, not a.non_resident), indent=2))


if __name__ == "__main__":
    main()

"""Ontario land transfer tax, plus the City of Toronto municipal land transfer tax.

Rates checked on 2026-11-24 against ontario.ca and toronto.ca (see rates.json).
This is an estimate for planning. The lawyer on the deal works out the final amount.
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


def _bracket_tax(price: Decimal, brackets: list[dict]) -> Decimal:
    """Tax each slice of the price at its own rate. Brackets are [{"up_to": n or None, "rate": r}]."""
    tax = Decimal("0")
    lower = Decimal("0")
    for b in brackets:
        upper = Decimal(str(b["up_to"])) if b["up_to"] is not None else None
        if price <= lower:
            break
        top = price if upper is None else min(price, upper)
        tax += (top - lower) * Decimal(str(b["rate"]))
        if upper is None or price <= upper:
            break
        lower = upper
    return tax


def ontario_ltt(price, one_or_two_single_family_homes: bool = True) -> Decimal:
    key = "single_family" if one_or_two_single_family_homes else "other"
    return _money(_bracket_tax(Decimal(str(price)), RATES["ontario"][key]))


def toronto_mltt(price, one_or_two_single_family_homes: bool = True) -> Decimal:
    key = "single_family" if one_or_two_single_family_homes else "other"
    return _money(_bracket_tax(Decimal(str(price)), RATES["toronto"][key]))


def land_transfer_tax(
    price,
    in_toronto: bool = False,
    first_time_buyer_share: float = 0.0,
    one_or_two_single_family_homes: bool = True,
    all_buyers_canadian_or_pr: bool = True,
) -> dict:
    """Work out the tax and the first-time buyer refunds.

    first_time_buyer_share: the share of the home bought by people who qualify as
    first-time buyers, from 0 (nobody) to 1 (everyone). The refund shrinks by the same share.
    Spouses: if any buyer's spouse owned a home anywhere while they were married to
    that buyer, Ontario gives NO refund, so pass 0. A share between 0 and 1 is only right
    when the non-qualifying buyer is not a spouse (for example a parent on title), or a
    spouse who owned a home only before the marriage. The lawyer confirms.
    """
    if not all_buyers_canadian_or_pr:
        return {
            "covered": False,
            "why": ("A buyer who is not a Canadian citizen or permanent resident can owe Ontario's "
                    "Non-Resident Speculation Tax (a large extra tax) and may be barred by the federal "
                    "ban on non-Canadians buying homes. This tool does not cover that. Talk to a lawyer."),
        }
    if not 0 <= first_time_buyer_share <= 1:
        raise ValueError("first_time_buyer_share must be between 0 and 1")
    price = Decimal(str(price))
    if not price.is_finite() or price < 0:
        raise ValueError("price must not be negative")
    share = Decimal(str(first_time_buyer_share))

    on_tax = ontario_ltt(price, one_or_two_single_family_homes)
    on_refund = _money(min(on_tax, Decimal(str(RATES["ontario"]["first_time_refund_max"]))) * share)

    to_tax = to_refund = Decimal("0.00")
    if in_toronto:
        to_tax = toronto_mltt(price, one_or_two_single_family_homes)
        to_refund = _money(min(to_tax, Decimal(str(RATES["toronto"]["first_time_rebate_max"]))) * share)

    total = on_tax + to_tax
    refunds = on_refund + to_refund
    return {
        "covered": True,
        "price": str(_money(price)),
        "ontario_tax": str(on_tax),
        "toronto_tax": str(to_tax),
        "total_tax": str(_money(total)),
        "ontario_first_time_refund": str(on_refund),
        "toronto_first_time_rebate": str(to_refund),
        "total_after_refunds": str(_money(total - refunds)),
        "rates_checked": RATES["checked"],
        "note": "Estimate only. Refunds have conditions (see SKILL.md). The lawyer on the deal confirms the final amount.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Ontario and Toronto land transfer tax")
    p.add_argument("price", type=float, help="purchase price in dollars")
    p.add_argument("--toronto", action="store_true", help="the home is in the City of Toronto")
    p.add_argument("--first-time-share", type=float, default=0.0,
                   help="share bought by qualifying first-time buyers, 0 to 1 (default 0)")
    p.add_argument("--not-single-family", action="store_true",
                   help="the land is not one or two single family homes (for example a 3+ unit building)")
    p.add_argument("--non-resident", action="store_true",
                   help="a buyer is not a Canadian citizen or permanent resident (not covered, see SKILL.md)")
    a = p.parse_args()
    print(json.dumps(land_transfer_tax(a.price, a.toronto, a.first_time_share, not a.not_single_family,
                                       not a.non_resident), indent=2))


if __name__ == "__main__":
    main()

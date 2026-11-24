"""Known-answer tests. Run with: python -m pytest tests"""
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills"
for d in ("ontario-land-transfer-tax", "mortgage-default-insurance", "buyer-closing-costs", "housing-ad-checker"):
    sys.path.insert(0, str(ROOT / d))

from ltt import land_transfer_tax, ontario_ltt, toronto_mltt  # noqa: E402
from insurance import premium, minimum_down_payment  # noqa: E402
from closing_costs import closing_costs  # noqa: E402
from check_ad import check_ad  # noqa: E402

D = Decimal


# Land transfer tax: hand-worked from the published brackets.
def test_ontario_500k():
    # 55,000 x 0.5% + 195,000 x 1% + 150,000 x 1.5% + 100,000 x 2%
    assert ontario_ltt(500000) == D("6475.00")

def test_ontario_800k():
    assert ontario_ltt(800000) == D("12475.00")

def test_toronto_800k_doubles():
    r = land_transfer_tax(800000, in_toronto=True)
    assert r["total_tax"] == "24950.00"

def test_ontario_over_2m_single_family_vs_other():
    # 36,475 at $2M, then 2.5% vs 2.0% on the next $500,000
    assert ontario_ltt(2500000, True) == D("48975.00")
    assert ontario_ltt(2500000, False) == D("46475.00")

def test_toronto_luxury_bracket_april_2026():
    # $3.5M: 36,475 + 1,000,000 x 2.5% + 500,000 x 4.4%
    assert toronto_mltt(3500000) == D("83475.00")

def test_first_time_full_refund_cap():
    r = land_transfer_tax(800000, in_toronto=True, first_time_buyer_share=1)
    assert r["ontario_first_time_refund"] == "4000.00"
    assert r["toronto_first_time_rebate"] == "4475.00"
    assert r["total_after_refunds"] == "16475.00"

def test_first_time_cheap_home_pays_nothing():
    r = land_transfer_tax(350000, first_time_buyer_share=1)
    assert r["total_after_refunds"] == "0.00"

def test_first_time_half_share():
    r = land_transfer_tax(500000, first_time_buyer_share=0.5)
    assert r["ontario_first_time_refund"] == "2000.00"


# Default insurance
def test_min_down():
    assert minimum_down_payment(500000) == D("25000.00")
    assert minimum_down_payment(700000) == D("45000.00")

def test_premium_5_percent_down():
    r = premium(500000, 25000)  # loan 475,000, 95% LTV -> 4.00%
    assert r["premium"] == "19000.00"
    assert r["sales_tax_on_premium_paid_at_closing"] == "1520.00"

def test_premium_30_year_surcharge():
    r = premium(500000, 50000, amortization_years=30, first_time_or_new_build=True)  # 90% -> 3.10% + 0.20%
    assert r["premium_rate"] == "3.30%"
    assert r["premium"] == "14850.00"

def test_30_years_not_allowed_for_others():
    r = premium(500000, 50000, amortization_years=30)
    assert not r["can_insure"]

def test_20_percent_down_no_insurance():
    assert premium(600000, 120000)["insurance_needed"] is False

def test_price_cap():
    r = premium(1500000, 140000)
    assert not r["can_insure"]

def test_too_little_down():
    r = premium(700000, 35000)
    assert not r["can_insure"]


# Closing costs: never guesses quoted items
def test_closing_costs_incomplete_without_quotes():
    r = closing_costs(500000, 25000)
    assert r["complete"] is False
    assert r["cash_needed_at_closing_besides_down_payment"] == "7995.00"  # 6,475 LTT + 1,520 PST

def test_closing_costs_complete_with_quotes():
    r = closing_costs(500000, 25000, quotes={"legal_fees": 1800, "title_insurance": 350,
                                             "home_inspection": 500, "home_insurance": 0, "adjustments": 900})
    assert r["complete"] is True
    assert r["cash_needed_at_closing_besides_down_payment"] == "11545.00"


# Ad checker
GOOD = ("Homes in Ajax under $599K. Free weekly list. "
        "Jane Doe, Salesperson. Example Realty Inc., Brokerage")

def test_clean_ad_passes():
    r = check_ad(GOOD, brokerage="Example Realty Inc.", agent="Jane Doe")
    assert r["fails"] == 0 and r["reviews"] == 0

def test_missing_brokerage_word():
    r = check_ad("Jane Doe, Salesperson. Example Realty Inc.", brokerage="Example Realty Inc.", agent="Jane Doe")
    assert r["fails"] == 1

def test_flags_family_status():
    r = check_ad(GOOD + " Perfect for a young couple, no kids.", "Example Realty Inc.", "Jane Doe")
    assert r["reviews"] >= 1

def test_family_room_not_flagged():
    r = check_ad(GOOD + " Big family room and a finished basement.", "Example Realty Inc.", "Jane Doe")
    assert r["reviews"] == 0

def test_meta_settings():
    bad = {"special_ad_category": "NONE", "age_min": 25, "radius_km": 10, "postal_codes": ["L1S"]}
    r = check_ad(GOOD, "Example Realty Inc.", "Jane Doe", bad)
    assert r["fails"] == 4
    ok = {"special_ad_category": "HOUSING", "age_min": 18, "age_max": 65, "radius_km": 25}
    assert check_ad(GOOD, "Example Realty Inc.", "Jane Doe", ok)["fails"] == 0


# The worked examples in each SKILL.md must match the code.
def test_doc_examples():
    assert land_transfer_tax(900000, True, 1)["total_after_refunds"] == "20475.00"
    assert premium(600000, 40000)["premium"] == "22400.00"
    r = closing_costs(650000, 45000, quotes={"legal_fees": 1900, "title_insurance": 400,
                                             "home_inspection": 550, "home_insurance": 1500, "adjustments": 1200})
    assert r["cash_needed_at_closing_besides_down_payment"] == "16961.00"


# Edge cases found in review.
def test_non_resident_not_covered():
    assert land_transfer_tax(800000, all_buyers_canadian_or_pr=False)["covered"] is False
    assert closing_costs(800000, 160000, all_buyers_canadian_or_pr=False)["covered"] is False

def test_toronto_tax_zero_format():
    assert land_transfer_tax(500000)["toronto_tax"] == "0.00"

def test_over_cap_shows_20_percent_and_no_premium():
    r = premium(1600000, 140000)
    assert r["can_insure"] is False
    assert r["minimum_down_payment"] == "320000.00"
    assert "premium" not in r

def test_uninsurable_has_no_premium():
    assert "premium" not in premium(700000, 35000)

def test_unknown_province_refused():
    import pytest
    with pytest.raises(ValueError):
        premium(500000, 25000, province="Ont")

def test_province_without_table_says_ask():
    assert premium(500000, 25000, province="BC")["sales_tax_on_premium_paid_at_closing"].startswith("not in our table")

def test_condo_needs_status_certificate():
    q = {"legal_fees": 1, "title_insurance": 1, "home_inspection": 1, "home_insurance": 1, "adjustments": 1}
    assert closing_costs(500000, 100000, quotes=q)["complete"] is True
    assert closing_costs(500000, 100000, quotes=q, condo=True)["complete"] is False

def test_home_insurance_required():
    q = {"legal_fees": 1, "title_insurance": 1, "home_inspection": 1, "adjustments": 1}
    assert closing_costs(500000, 100000, quotes=q)["complete"] is False

def test_uninsurable_closing_costs_stop():
    r = closing_costs(700000, 35000)
    assert r["complete"] is False and "insurance" in r

def test_number_one_claim_flagged():
    r = check_ad(GOOD + " We are #1 in Durham.", "Example Realty Inc.", "Jane Doe")
    assert r["reviews"] == 1

def test_brokerage_given_with_word_brokerage():
    r = check_ad(GOOD, brokerage="Example Realty Inc., Brokerage", agent="Jane Doe")
    assert r["fails"] == 0

def test_meta_string_radius_and_numeric_genders():
    s = {"special_ad_category": "HOUSING", "radius_km": "25", "genders": [1, 2]}
    assert check_ad(GOOD, "Example Realty Inc.", "Jane Doe", s)["fails"] == 0
    s["radius_km"] = "10"
    assert check_ad(GOOD, "Example Realty Inc.", "Jane Doe", s)["fails"] == 1

def test_missing_title_is_review_not_fail():
    r = check_ad("Homes under $599K. Jane Doe. Example Realty Inc., Brokerage", "Example Realty Inc.", "Jane Doe")
    assert r["fails"] == 0 and r["reviews"] == 1


# Round 2 review.
def test_negative_quote_refused():
    import pytest
    with pytest.raises(ValueError):
        closing_costs(500000, 100000, quotes={"legal_fees": -5000})

def test_bad_province_refused_even_when_uninsurable():
    import pytest
    with pytest.raises(ValueError):
        premium(1600000, 100000, province="XX")

def test_age_phrases_flagged():
    for phrase in ["Perfect for a young couple", "Ideal for young families", "Great for retirees",
                   "Seniors building", "Adult lifestyle community", "55+ community"]:
        r = check_ad(GOOD + " " + phrase + ".", "Example Realty Inc.", "Jane Doe")
        assert r["reviews"] >= 1, phrase

def test_salesperson_cannot_say_broker():
    r = check_ad("Jane Doe, Broker. Example Realty Inc., Brokerage", "Example Realty Inc.", "Jane Doe",
                 agent_class="salesperson")
    assert r["fails"] == 1

def test_missing_meta_fields_are_review():
    r = check_ad(GOOD, "Example Realty Inc.", "Jane Doe", {"special_ad_category": "HOUSING"})
    assert r["fails"] == 0 and r["reviews"] == 4


# Round 3 review.
def test_broker_titles_from_reco_bulletin():
    for title in ["Real Estate Agent", "Broker", "Real Estate Broker", "Broker of Record"]:
        r = check_ad(f"Jane Doe, {title}. Example Realty Inc., Brokerage", "Example Realty Inc.", "Jane Doe",
                     agent_class="broker")
        assert r["fails"] == 0 and r["reviews"] == 0, title

def test_associate_broker_is_not_a_permitted_title():
    r = check_ad("Jane Doe, Associate Broker. Example Realty Inc., Brokerage", "Example Realty Inc.", "Jane Doe")
    assert r["reviews"] == 1

def test_monthly_payment_claims():
    for t in ["$2,500 monthly", "$2,500/month", "$2,500 per month", "$2,500 a month"]:
        assert check_ad(GOOD + " " + t, "Example Realty Inc.", "Jane Doe")["reviews"] == 1, t

def test_false_as_text():
    s = {"special_ad_category": "HOUSING", "age_min": 18, "age_max": 65, "genders": "all", "radius_km": 25,
         "lookalike_audience": "false", "postal_codes": "[]"}
    assert check_ad(GOOD, "Example Realty Inc.", "Jane Doe", s)["fails"] == 0

def test_bad_numbers_refused():
    import pytest
    with pytest.raises(ValueError):
        land_transfer_tax(float("nan"))
    with pytest.raises(ValueError):
        premium(500000, 25000, amortization_years=0)

def test_no_kids_counted_once():
    assert check_ad(GOOD + " No kids.", "Example Realty Inc.", "Jane Doe")["reviews"] == 1

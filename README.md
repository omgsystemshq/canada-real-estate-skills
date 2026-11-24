# Canada Real Estate Skills

Free, tested skills for AI agents that work in Canadian real estate. Each one does one job well, shows its sources, and says plainly when it is only an estimate.

Most real estate AI tools are built for the US. These are built for Canada.

| Skill | What it does |
|---|---|
| [Ontario land transfer tax](skills/ontario-land-transfer-tax) | Ontario tax, the City of Toronto's extra tax (including the April 2026 high-value rates), and first-time buyer refunds |
| [Mortgage default insurance](skills/mortgage-default-insurance) | Premium on a mortgage with less than 20% down, the minimum down payment, the 30-year option, and the sales tax due at closing |
| [Buyer closing costs](skills/buyer-closing-costs) | Cash needed on closing day besides the down payment. Uses real quotes for fees and never fills in a guess |
| [Housing ad checker](skills/housing-ad-checker) | Checks a home ad for words that can shut people out, brokerage and agent name rules, and Facebook and Instagram housing ad settings |

## What's coming next

One new piece at a time, each tested before it goes up:

1. **A connector**, so any AI app can call these calculators directly, with no copying folders.
2. **A buyer budget workflow** that runs the money skills in order and hands back one clean page: price, down payment, insurance, land tax and cash needed on closing day.
3. **More skills**, including a FINTRAC ID checklist, a CASL email checker and a short-term rental owner statement.

Star or watch the repo to see each one when it lands.

## How to use a skill

Each skill is a folder with:

- `SKILL.md`: instructions an AI agent reads (when to use it, what to ask, how to explain the answer).
- A Python script you can also run yourself. It needs Python 3.9 or newer and nothing else.
- A rates or rules file with the official sources and the date they were last checked.

```
python3 skills/ontario-land-transfer-tax/ltt.py 900000 --toronto --first-time-share 1
python3 skills/mortgage-default-insurance/insurance.py 600000 40000
python3 skills/buyer-closing-costs/closing_costs.py 650000 45000 --legal-fees 1900 --title-insurance 400 --home-inspection 550 --home-insurance 1500 --adjustments 1200
python3 skills/housing-ad-checker/check_ad.py skills/housing-ad-checker/examples/ad.txt --brokerage "Example Realty Inc." --agent "Jane Doe" --meta-settings skills/housing-ad-checker/examples/adset.json
```

Run the commands from the top of the repo. To give a skill to an AI agent that reads skill folders, copy the skill's folder into the agent's skills folder. **Buyer closing costs** uses the other two calculators, so copy `ontario-land-transfer-tax`, `mortgage-default-insurance` and `buyer-closing-costs` together, side by side.

## Tested

The tests check the math against hand-worked answers from the official rate tables, the edge cases (price caps, spouses, odd inputs), and every worked example in the docs. To run them you need pytest:

```
python3 -m pip install pytest
python3 -m pytest tests
```

## What these skills do not cover

- Buyers who are not Canadian citizens or permanent residents. Extra taxes and a federal ban can apply. The tools refuse those cases and say why.
- The full cost list for newly built homes.
- Provinces other than Ontario for land transfer tax.

## Good to know

These skills give estimates and checklists. They are not legal, tax or financial advice. Rates change: each skill keeps the date it was last checked next to its sources, and we update them when governments change the rules.

Found a rate that changed or a rule we missed? Open an issue with a link to the official page.

## Made by OMGSystems

Built in Ontario by [OMGSystems](https://omgsystems.ca). MIT licence.

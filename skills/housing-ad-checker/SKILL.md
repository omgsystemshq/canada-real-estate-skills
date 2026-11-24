---
name: housing-ad-checker
description: Check a Canadian real estate ad and its Facebook or Instagram settings for words that can shut people out, missing brokerage and agent name rules, and housing ad targeting rules. Use before running any home, listing or buyer ad in Canada.
---

# Housing ad checker (Canada)

Real estate ads in Canada have three sets of rules on them at once:

1. **Human rights.** In Ontario, the Human Rights Code protects people looking for housing from being treated differently because of age, family status, disability, race, religion, sex, receiving public assistance and more. An ad that says "perfect for a young couple" or "no kids" can shut people out.
2. **Who is advertising.** In Ontario, every real estate ad must clearly show the brokerage name as registered, followed by "Brokerage". An agent named in the ad must use their registered name, no nicknames, with a permitted title like "Salesperson".
3. **Ad platform rules.** Meta's own policy (not a law, and it changes) says housing ads shown in Canada on Facebook and Instagram must be declared as "Housing". That locks the age range to 18 to 65+, all genders, a radius of at least 25 km (15 miles) around each place, and no postal codes, lookalikes or excluded areas.

This skill checks all three and tells you what to look at. It never says an ad is legal. A person makes the call.

## When to use it

Before any home ad goes live: listing ads, buyer lead ads, rental ads, open house posts.

## What to gather

1. Every word in the ad: the words on the picture or video, the main text, the headline. Put them in one text file.
2. The brokerage name exactly as registered.
3. The agent's registered name, if the ad names an agent, and whether they are registered as a salesperson or a broker (`--agent-class`), so the title can be checked.
4. Optional: the ad set settings as JSON:

```json
{"special_ad_category": "HOUSING", "age_min": 18, "age_max": 65, "genders": "all",
 "radius_km": 25, "postal_codes": [], "lookalike_audience": false, "excluded_locations": []}
```

## How to run it

```
python3 skills/housing-ad-checker/check_ad.py skills/housing-ad-checker/examples/ad.txt --brokerage "Example Realty Inc." --agent "Jane Doe" --meta-settings skills/housing-ad-checker/examples/adset.json
```

## How to read the result

- **fail**: something is missing or not allowed. Fix it before the ad runs.
- **review**: a word that can shut people out, or a claim that needs proof. Often a fix is easy: describe the home, not the person. "Three bedrooms near two schools" instead of "perfect for a young family".
- A setting missing from the settings file is a **review**, never a pass. Give every setting.
- Some flagged words are fine in context. "Family room" is never flagged. "Perfect for a family" is.

## Rules worth knowing

- Say what the home has, not who should live there.
- Payment, interest rate and "pre-approved" claims must be true and show their conditions. Many brokerages simply leave them out of ads.
- "#1" or "top agent" claims need proof you can show.
- Other provinces have their own regulator with similar name rules. Check yours.

## Keep it current

The word lists and settings are in `rules.json` with the sources and the date checked. Add words your team keeps seeing.

This is a checklist, not legal advice.

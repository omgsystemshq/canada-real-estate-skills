"""Check a Canadian real estate ad (words and, optionally, its Meta ad set settings).

It looks for three kinds of problems:
  1. Words that can shut people out because of who they are. In Ontario the Human Rights
     Code protects people looking for housing from being treated differently because of
     things like age, family status, disability, race, religion, sex or receiving public
     assistance. These are flagged for a person to review, because some words are fine in
     context ("family room").
  2. Missing name rules. In Ontario an ad must show the brokerage name as registered, with
     the word "Brokerage", and an agent named in it must use their registered name and a
     permitted title such as "Salesperson".
  3. Meta "Housing" ad settings that break Meta's own housing ad policy for ads shown in Canada.
     That is a platform policy, not a law, and Meta changes it from time to time.

It never says an ad is legal. It says what to look at. A person makes the call.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RULES = json.loads((Path(__file__).with_name("rules.json")).read_text())


def _find(patterns: list[str], text: str) -> list[str]:
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append(m.group(0))
    return hits


def check_words(text: str) -> list[dict]:
    issues = []
    for ground in RULES["protected_grounds"]:
        hits = _find(ground["patterns"], text)
        if hits:
            issues.append({
                "level": "review",
                "rule": f"Could shut people out ({ground['ground']})",
                "found": sorted(set(hits)),
                "fix": ground["fix"],
            })
    for claim in RULES["claims_to_back_up"]:
        hits = _find(claim["patterns"], text)
        if hits:
            issues.append({"level": "review", "rule": claim["rule"], "found": sorted(set(hits)), "fix": claim["fix"]})
    return issues


def check_names(text: str, brokerage: str | None, agent: str | None, agent_class: str | None = None) -> list[dict]:
    issues = []
    if brokerage:
        brokerage = re.sub(r",?\s+(real estate\s+)?brokerage\s*$", "", brokerage.strip(), flags=re.IGNORECASE)
        name = re.escape(brokerage)
        if not re.search(name, text, flags=re.IGNORECASE):
            issues.append({"level": "fail", "rule": "Brokerage name missing",
                           "fix": f'Show "{brokerage}" exactly as registered, clearly and prominently.'})
        elif not re.search(name + r",?\s+(Real Estate\s+)?Brokerage\b", text, flags=re.IGNORECASE):
            issues.append({"level": "fail", "rule": 'Brokerage name is not followed by "Brokerage"',
                           "fix": f'Write it as "{brokerage}, Brokerage" or "{brokerage}, Real Estate Brokerage".'})
    else:
        issues.append({"level": "review", "rule": "No brokerage name given to check",
                       "fix": "Run again with --brokerage set to the name registered with the regulator."})
    if agent:
        if not re.search(re.escape(agent.strip()), text, flags=re.IGNORECASE):
            issues.append({"level": "fail", "rule": "Agent's registered name missing",
                           "fix": f'If the ad names an agent, use the registered name "{agent}". No nicknames or short forms.'})
        else:
            pool = {"salesperson": RULES["salesperson_titles"], "broker": RULES["broker_titles"]}.get(
                (agent_class or "").lower(), RULES["permitted_titles"])
            titles = "|".join(re.escape(t) for t in sorted(pool, key=len, reverse=True))
            near = re.search(re.escape(agent.strip()) + r",?\s+(" + titles + r")\b", text, flags=re.IGNORECASE)
            if not near:
                wrong = ""
                if agent_class:
                    other = RULES["broker_titles"] if agent_class.lower() == "salesperson" else RULES["salesperson_titles"]
                    other = [x for x in other if x not in pool]
                    alt = "|".join(re.escape(x) for x in sorted(other, key=len, reverse=True))
                    if re.search(re.escape(agent.strip()) + r",?\s+(" + alt + r")\b", text, flags=re.IGNORECASE):
                        wrong = "yes"
                if wrong:
                    issues.append({"level": "fail", "rule": f"Title does not match the agent's registration ({agent_class})",
                                   "fix": "Use a title that matches how the agent is registered."})
                else:
                    issues.append({"level": "review", "rule": "No permitted title right after the agent's name",
                                   "fix": "If the ad gives a title, it must be a permitted one, for example \"Salesperson\". Check it is there and correct."})
    return issues


def _truthy(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() not in ("", "false", "no", "0", "none", "[]")
    return bool(v)


def check_meta(settings: dict) -> list[dict]:
    issues = []
    m = RULES["meta_housing"]
    if str(settings.get("special_ad_category", "")).upper() != "HOUSING":
        issues.append({"level": "fail", "rule": 'Ad set is not in the "Housing" special ad category',
                       "fix": "Meta's policy says real estate ads shown in Canada must be declared as Housing."})
    for field in ("age_min", "age_max", "genders", "radius_km"):
        if field not in settings:
            issues.append({"level": "review", "rule": f"Setting not given: {field}",
                           "fix": "Add it to the settings file so it can be checked. A missing setting is not a pass."})
    if _truthy(settings.get("detailed_targeting")):
        issues.append({"level": "review", "rule": "Uses detailed targeting (interests or behaviours)",
                       "fix": "Many options are removed for housing ads. Make sure none of them stand in for a protected group."})
    try:
        age_min = int(settings.get("age_min", 18))
        age_max = int(settings.get("age_max", 65))
    except (TypeError, ValueError):
        age_min, age_max = 99, 0
    if age_min > m["age_min"] or age_max < m["age_max"]:
        issues.append({"level": "fail", "rule": "Age range narrowed", "fix": "Housing ads must reach ages 18 to 65+."})
    genders = settings.get("genders")
    if genders not in (None, [], "all", ["all"], [1, 2], [2, 1], ["1", "2"], ["2", "1"]):
        issues.append({"level": "fail", "rule": "Gender narrowed", "fix": "Housing ads must reach all genders."})
    radius = settings.get("radius_km")
    try:
        radius = float(radius) if radius not in (None, "") else None
    except (TypeError, ValueError):
        issues.append({"level": "fail", "rule": "radius_km is not a number", "fix": "Give the radius in km as a number."})
        radius = None
    if radius is not None and radius < m["min_radius_km"]:
        issues.append({"level": "fail", "rule": f"Location radius under {m['min_radius_km']} km",
                       "fix": f"Use a radius of at least {m['min_radius_km']} km (15 miles) around each place."})
    if _truthy(settings.get("postal_codes")):
        issues.append({"level": "fail", "rule": "Targets postal codes", "fix": "Housing ads cannot target postal codes."})
    if _truthy(settings.get("lookalike_audience")):
        issues.append({"level": "fail", "rule": "Uses a lookalike audience", "fix": "Lookalikes are not allowed for housing ads."})
    if _truthy(settings.get("excluded_locations")):
        issues.append({"level": "fail", "rule": "Excludes locations", "fix": "Housing ads cannot exclude areas."})
    return issues


def check_ad(text: str, brokerage: str | None = None, agent: str | None = None, meta_settings: dict | None = None,
             agent_class: str | None = None) -> dict:
    issues = check_words(text) + check_names(text, brokerage, agent, agent_class)
    if meta_settings is not None:
        issues += check_meta(meta_settings)
    fails = sum(1 for i in issues if i["level"] == "fail")
    reviews = sum(1 for i in issues if i["level"] == "review")
    verdict = "fix first" if fails else ("a person should review the flagged words" if reviews else "no problems found")
    return {"verdict": verdict, "fails": fails, "reviews": reviews, "issues": issues,
            "rules_checked": RULES["checked"],
            "note": "This is a checklist, not legal advice. A person makes the final call."}


def main() -> None:
    p = argparse.ArgumentParser(description="Check a Canadian real estate ad")
    p.add_argument("ad_text_file", help="text file with every word in the ad (picture text, primary text, headline)")
    p.add_argument("--brokerage", help='registered brokerage name, for example "Example Realty Inc."')
    p.add_argument("--agent", help="the agent's registered name, if the ad names one")
    p.add_argument("--agent-class", choices=["salesperson", "broker"], help="how the agent is registered")
    p.add_argument("--meta-settings", help="JSON file with the ad set settings (see SKILL.md)")
    a = p.parse_args()
    text = Path(a.ad_text_file).read_text()
    settings = json.loads(Path(a.meta_settings).read_text()) if a.meta_settings else None
    print(json.dumps(check_ad(text, a.brokerage, a.agent, settings, a.agent_class), indent=2))


if __name__ == "__main__":
    main()

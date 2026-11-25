"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "uc-g28-expense-audit" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 32-scenario row).
MIX = {"easy": 6, "boundary_twin": 8, "multi_rule": 5, "hidden_clause": 3, "distractor": 3, "refusal": 3, "flag": 4}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. G-28 has no overnight-stop rule.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "business", "economy", "coach", "first", "premium", "plus", "legroom", "chancellor", "dean", "delegate",
    "designee", "provost", "regents", "controller", "federal", "grant", "award", "nih", "nsf", "america", "fly",
    "foreign", "carrier", "skies", "open", "codeshare", "meeting", "rest", "medical", "doctor", "disability",
    "union", "bargaining", "sponsor", "extramural", "spouse", "partner", "dependent", "child", "son", "family",
    "personal", "vacation", "holiday", "candidate", "interview", "round", "trip", "ticket", "unused", "canceled",
    "nonrefundable", "scope", "laboratory", "lab", "lbnl", "doe", "local", "campus", "group", "key", "only",
    "service", "sold", "nonstop", "direct", "connection", "layover", "cheaper", "expensive", "lowest", "self",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.TravellerKind, contract.SignerRole, contract.PaperKind]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section). Coach at the most economical fare is this
# handbook's default (lines 490-492, 567-569), so the always-lowest agent passes every case whose right answer
# is the cheapest seat listed; set to what it passes (see README). The always-flag agent passes exactly the
# three holds over unclear words (it is given the held offer).
MAX_PASS_ALWAYS_FLAG = 3
MAX_PASS_ALWAYS_LOWEST = 12

# G-28 has no flight-length rule (rules.DURATION_RULES is empty; see rules.py), so there are no duration
# cases. The Fly America travel-time comparison is tested in tests/test_uc_checks.py.
DURATION_CASES = []

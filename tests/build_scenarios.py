"""Writes src/plugin/data/scenarios/*.json for the UC G-28 plugin (an authoring aid, not a test; the JSON
files are the truth). Each must_keep entry gets its sha256 from the frozen policy.txt, and each expected
answer is checked against rules.solve by tests/test_scenarios.py.

    uv run python tests/build_scenarios.py
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "plugin" / "data"
LINES = (DATA / "policy.txt").read_text(encoding="utf-8").split("\n")


def words(start, end):
    return " ".join(" ".join(LINES[start - 1:end]).split())


# Clauses, by key: (first line, last line, exact quote inside the range, why it matters).
CLAUSES = {
    "coach": (567, 569, ("Coach class or any discounted class shall be used in the interest of cost-efficiency. This "
              "policy applies to all travel (domestic or foreign, or any combination thereof) regardless of the "
              "purpose or fund source."), "coach is the rule for every trip, however long"),
    "listed": (570, 572, "Use of business or first-class may be authorized under the circumstances listed below.",
               "business only under a listed circumstance"),
    "only_service": (573, 573, "Business or first-class is the only service offered between two points;",
                     "first listed circumstance"),
    "more_expensive": (574, 577, "The use of coach class would be more expensive or time-consuming",
                       "second listed circumstance"),
    "overnight": (578, 579, ("An itinerary involves overnight travel without an opportunity for normal rest before "
                  "the commencement of working hours."), "third listed circumstance"),
    "overnight_docs": (584, 585, ("must include required documentation to support the early meeting start time and/or "
                       "that alternative start dates or times are unavailable"),
                       "the campus documentation of the start time"),
    "medical": (586, 587, ("The use of business or first-class travel is necessary to reasonably accommodate a "
                "disability or medical need of a traveler."), "fourth listed circumstance"),
    "chancellor": (588, 592, ("In cases other than those described above, a written authorization to use business or "
                   "first-class shall be obtained in advance from the Chancellor."),
                   "outside the list, only the Chancellor's advance written authorization"),
    "ancillary": (593, 597, ("Likewise, reimbursement of higher cost airfare such as Economy Plus, Extra Comfort, "
                  "etc., within the economy class can be included in the local policy."),
                  "Economy Plus is left to the campus's local policy"),
    "fly_america": (598, 601, ("only U.S. air carriers1 shall be used for all travel reimbursed from federal grants "
                    "and contracts, including NIH grants2."), "Fly America on federal funds"),
    "fa_nonstop": (604, 607, ("Generally, U.S. air carrier services that provide nonstop or direct service from the "
                   "origin to the destination must be used, unless such use would extend travel time, including "
                   "delay at origin, by 24 hours or more;"), "a U.S. nonstop must be used"),
    "fa_connect": (608, 616, "Extend travel time by at least 6 hours or more; or",
                   "a connecting U.S. carrier must be used unless it adds at least 6 hours"),
    "economical": (490, 492, ("Transportation expenses shall be reimbursed based on the most economical mode of "
                   "transportation and the most commonly traveled route consistent with the authorized purpose of "
                   "the trip. Any exception must be approved by the Chancellor."),
                   "the most economical fare; exceptions are the Chancellor's"),
    "group": (493, 498, ("Travel by a group of employees in the same aircraft, automobile, or other modes of "
              "transportation is discouraged"), "soft: discouraged, never forbidden"),
    "delegation": (44, 44, "Authority delegated to the Chancellor also may be delegated to other individuals.",
                   "the Chancellor's authority may be delegated"),
    "designee": (259, 272, ("Chancellors (or Chancellor's designee if any delegation of the Chancellor's authority is "
                 "made in writing) Have the authority to make exceptions to the University's Travel Policy, as long as "
                 "the exception is in writing."), "a designee needs a written delegation"),
    "extramural": (120, 121, ("The terms set forth in an extramural funding agreement govern only when such terms are "
                   "more restrictive than University travel regulations."),
                   "a sponsor's terms govern only when stricter"),
    "bargaining": (122, 124, ("the terms of a collective bargaining agreement shall govern when such terms do not "
                   "conform to the provisions of this Bulletin."), "a union contract governs where it differs"),
    "personal": (153, 156, ("Under no circumstances shall expenses for personal travel be charged to or be "
                 "temporarily funded by, the University, unless otherwise noted in this Bulletin."),
                 "personal travel is never funded, even temporarily"),
    "own_travel": (321, 322, "Persons delegated the authority to approve travel shall not approve their own travel.",
                   "no one approves their own travel"),
    "canceled": (404, 405, ("A nonrefundable ticket associated with a canceled trip must be used for the employee's "
                 "next business trip."), "the unused ticket must be used"),
    "non_university": (1462, 1464, ("Travel expenses incurred by non-University travelers shall not be reimbursed "
                       "from a University fund source unless the travel has been approved in advance by the inviting "
                       "department."), "the inviting department's advance approval"),
    "candidate_cap": (1482, 1484, ("Actual transportation expenses shall not exceed one round-trip coach airfare "
                      "between the prospective employee's current residence and the interview location for each "
                      "round of interviews."), "one round-trip coach fare per round"),
    "faq_dependent": (1869, 1870, "The travel expenses of the dependent can't be charged to a federal fund.",
                      "a dependent's travel is never on a federal fund"),
    "dependent_preapproval": (1566, 1571, ("may be allowed in limited circumstances when pre-approved by the "
                              "Chancellor, Executive Vice Chancellor/Provost, Dean, Director, Department Chair, or "
                              "other senior University officer"), "the pre-approval the record holds"),
    "scope": (25, 30, ("This policy does not apply to travel associated with work done within the scope of the UC/DOE "
              "contract for the management and operations of the Lawrence Berkeley National Laboratory (LBNL)."),
              "G-28 does not cover the LBNL contract's work"),
    "scope_intro": (104, 107, ("However, the policy does not apply to work done within the scope of the UC/DOE "
                    "contract for the management and operations of the Lawrence Berkeley National Laboratory."),
                    "the same scope rule in the policy text"),
}

DISTRACTORS = {
    "incremental": (588, 590, ("When a traveler prefers to use a higher class than the one authorized for "
                    "reimbursement, the traveler must pay the incremental cost of the airfare."),
                    "who pays a self-chosen upgrade; not a way to book one"),
    "fa_deny": (648, 649, ("Reimbursement of travel on a foreign air carrier may be denied in the absence of such "
                "justification."), "applies only where Fly America applies"),
    "frequent_flyer": (511, 513, ("Travelers will not be reimbursed for non-cash certificates used for the purchase of "
                       "transportation tickets, e.g., frequent flyer miles."), "about paying with miles"),
    "sustainable": (927, 929, "book direct flights whenever feasible", "a suggestion, balanced against cost"),
    "group": CLAUSES["group"],
    "coach": CLAUSES["coach"],
    "extramural": CLAUSES["extramural"],
    "candidate_spouse": (1475, 1480, ("at the Chancellor's discretion, actual travel expenses and dependent care "
                         "expenses may be reimbursed for spouses/domestic partners"),
                         "about candidates' families, not the candidate's own seat"),
    "reservations": (443, 449, ("Travelers who are unable to honor a reservation shall be responsible for canceling "
                     "the reservation"), "about cancelling, not about using an unused ticket"),
    "per_mile": (581, 582, "The reimbursement of M&IE is subject to the 300 mile-per-day rule", "a driving footnote"),
}


def keep(*keys):
    out = []
    for key in keys:
        start, end, quote, why = CLAUSES[key]
        assert " ".join(quote.split()) in words(start, end), (key, words(start, end))
        out.append({"lines": [start, end], "sha256": hashlib.sha256(words(start, end).encode()).hexdigest(),
                    "quote": quote, "why": why})
    return out


def distract(*keys):
    out = []
    for key in keys:
        start, end, quote, why = DISTRACTORS[key]
        assert " ".join(quote.split()) in words(start, end), (key, words(start, end))
        out.append({"lines": [start, end], "quote": quote, "why": why})
    return out


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "traveller_kind": "EMPLOYEE", "campus": "", "accompanying": "",
        "companions": [], "origin": "", "destination": "", "depart_date": "", "return_date": "", "booking_date": "",
        "purpose": "", "fund_source": "campus general funds", "sponsor_travel_terms": "", "union_contract_terms": "",
        "open_skies_covers_route": False, "authorizations": [], "meeting_starts_local": "",
        "meeting_timing_documented": False, "medical_note_on_file": "", "unused_tickets": [], "campus_local_policy": "",
        "interview_round": 0, "interview_is_final": False, "tickets_bought_this_round": 0, "other_notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def paper(kind, name, role, on, covers, delegate="", writing=True):
    return {"kind": kind, "signer_name": name, "signer_role": role, "delegate_name": delegate, "in_writing": writing,
            "signed_on": on, "covers": covers}


def search(origin, destination, date, flights, offers, return_date="", background=None, name="main"):
    spec = {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": return_date}
    if background is not None:
        spec["background"] = background
    spec["flights"] = flights
    spec["offers"] = [dict(zip(("slot", "flight", "cabin", "fare_cents"), offer[:4]), **(offer[4] if len(offer) > 4
                                                                                          else {})) for offer in offers]
    return spec


def flight(carrier, depart, minutes=None, via=None, layovers=None, back=None):
    spec = {"carrier": carrier, "depart": depart}
    if via:
        spec["via"] = via
    if minutes:
        spec["minutes"] = minutes
    if layovers:
        spec["layovers"] = layovers
    if back:
        spec["return"] = back
    return spec


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins),
            "reason_codes": sorted(reasons), "approvers": sorted(approvers), "clauses": sorted(clauses),
            "unclear_phrase": phrase}


AIR = ["AIR_TRAVEL", "COMMERCIAL_AIRLINES"]
LOWEST = [*AIR, "TRANSPORTATION_EXPENSES"]
CLAIM = ["DEPARTMENT_HEAD", "NONE"]
LISTED = [*CLAIM, "NOT_NAMED"]
# The business cabin asked for is declined for want of a listed circumstance, not by the most-economical-fare
# rule, so LOWEST_FARE is not accepted (task instructions: the reason gives why the request is declined).
COACH = ["NO_LISTED_CIRCUMSTANCE", "UPGRADE_NOT_ELIGIBLE"]
US_REQUIRED = ["FLY_AMERICA_US_CARRIER_REQUIRED", "NATIONAL_CARRIER_REQUIRED"]

PROFESSOR = {"traveller_name": "Dr. Mina Castellanos", "traveller_title": "Associate Professor of Chemistry",
             "campus": "UC Davis"}

S = []
BACKGROUND = 2  # background offers on a plain coach case's own search


def scenario(id, category, request, trip_, searches, exp, must_keep, *, overlays=(), twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=(), notes="", hidden=None):
    # A case buys one ticket: a round-trip fare where a search pins one, else the one-way flight out. The
    # trip record gives a return_date only for a round-trip fare ("empty for a one-way ticket"), so
    # the agent is never sent to search for a return the world does not hold.
    if not any(search_["return_date"] for search_ in searches):
        trip_ = {**trip_, "return_date": ""}
    # The handbook's default is no background offers (handbook.json), so a search the scenario does not pin
    # (another date, a round trip) lists nothing: seeded offers there could contradict the pinned facts
    # (economy LAX-HNL, a faster United SAN-PVG). The plain coach cases pin two on their own search.
    searches = [{**search_, "background": BACKGROUND if search_.get("background") is None else search_["background"]}
                for search_ in searches]
    world = {"searches": searches}
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": world, "expected": exp, "must_keep": keep(*must_keep),
        "distractors": distract(*distractors), "design_notes": notes, "answer_key_inputs": hidden,
    })


def coach_hidden(**extra):
    return {"wish": "coach", "federal": False, **extra}


# ----------------------------------------------------------------------------------------------- easy

scenario(
    "quince-harbor", "easy",
    "I'm presenting a poster at a chemistry conference in Boston that opens on December 10. Please book me a flight "
    "out of San Francisco on the 8th.",
    trip(**PROFESSOR, origin="SFO", destination="BOS", depart_date="2026-12-08", return_date="2026-12-12",
         booking_date="2026-12-01", purpose="present a poster at a chemistry conference"),
    [search("SFO", "BOS", "2026-12-08", {
        "dl": flight("DL", "07:10", [330]), "ua": flight("UA", "09:45", [330]),
        "aa": flight("AA", "06:30", via=["ORD"], layovers=[75])},
        [("dl-economy", "dl", "ECONOMY", 36900), ("ua-economy", "ua", "ECONOMY", 41800),
         ("ua-business", "ua", "BUSINESS", 129000), ("aa-economy", "aa", "ECONOMY", 44200)])],
    expected("BOOK", ["dl-economy"], ["ECONOMY"], ["LOWEST_FARE"], CLAIM, LOWEST),
    ["coach", "economical"], hidden=coach_hidden(),
    notes="Coach at the most economical fare (lines 490-492, 567-569); the cheapest economy fare is a nonstop, so the "
          "routing question never arises. Two background itineraries are priced far above it.")

scenario(
    "drift-saffron", "easy",
    "I need to be in Honolulu for the observatory site visit on January 12. Please book me from Los Angeles on the "
    "11th.",
    trip(traveller_name="Dr. Kai Nakamura", traveller_title="Research Astronomer", campus="UC Santa Cruz",
         origin="LAX", destination="HNL", depart_date="2027-01-11", return_date="2027-01-15",
         booking_date="2026-12-14", purpose="site visit at a partner observatory"),
    [search("LAX", "HNL", "2027-01-11", {
        "early": flight("UA", "09:15", [345]), "late": flight("UA", "14:40", [345])},
        [("early-business", "early", "BUSINESS", 84000), ("late-business", "late", "BUSINESS", 91000)],
        background=0)],
    expected("BOOK", ["early-business"], ["BUSINESS"], ["ONLY_CLASS_OFFERED"], LISTED, AIR),
    ["coach", "listed", "only_service", "economical"], hidden=coach_hidden(),
    notes="No coach seat is sold on the route at all (no economy offer is listed), so business is the only service "
          "offered between the two points (line 573); the cheaper of the two business offers. Background offers are "
          "off: a background economy offer would remove the circumstance.")

scenario(
    "cobalt-sedge", "easy",
    "I'm flying to Singapore for a two-week field campaign. It's nearly seventeen hours nonstop, so please put me in "
    "business class.",
    trip(**PROFESSOR, origin="SFO", destination="SIN", depart_date="2027-01-06", return_date="2027-01-20",
         booking_date="2026-12-15", purpose="field campaign with a partner university",
         fund_source="department discretionary fund"),
    [search("SFO", "SIN", "2027-01-06", {"sq": flight("SQ", "09:20", [1000])},
            [("sq-economy", "sq", "ECONOMY", 118000), ("sq-business", "sq", "BUSINESS", 512000)], background=0)],
    expected("BOOK", ["sq-economy"], ["ECONOMY"], COACH, CLAIM, LOWEST),
    ["coach", "listed", "chancellor"], hidden={"wish": "business", "federal": False},
    distractors=["incremental"],
    notes="G-28 has no flight-length threshold: coach for all travel (lines 567-569); none of the four listed "
          "circumstances holds and no written Chancellor authorization is on file (lines 588-592). The fund is not "
          "federal, so Fly America does not arise.")

scenario(
    "tidal-orchid", "easy",
    "The Chancellor has approved business class for my trip to London to sign the research partnership; the letter "
    "is in my file. Please book me on the 4th.",
    trip(traveller_name="Dr. Imani Brooks", traveller_title="Vice Provost for Global Affairs", campus="UC Davis",
         origin="SFO", destination="LHR", depart_date="2027-02-04", return_date="2027-02-08",
         booking_date="2027-01-12", purpose="sign a research partnership agreement",
         authorizations=[paper("CABIN_ABOVE_COACH", "Chancellor Miriam Okafor", "CHANCELLOR", "2027-01-08",
                               "Business class for Dr. Brooks's flight to London on February 4, 2027")]),
    [search("SFO", "LHR", "2027-02-04", {"ua": flight("UA", "16:10", [630]), "ba": flight("BA", "18:30", [625])},
            [("ua-economy", "ua", "ECONOMY", 98000), ("ua-business", "ua", "BUSINESS", 410000),
             ("ba-economy", "ba", "ECONOMY", 96500), ("ba-business", "ba", "BUSINESS", 395000)], background=0)],
    expected("BOOK", ["ba-business"], ["BUSINESS"], ["CHANCELLOR_WRITTEN_AUTHORIZATION"], ["CHANCELLOR", *CLAIM],
             [*LOWEST, "RESPONSIBILITIES"]),
    ["chancellor", "economical"], hidden={"wish": "business", "federal": False},
    notes="The Chancellor's written authorization in advance (lines 588-592; line 492): business, at the lower of the "
          "two business fares.")

scenario(
    "russet-plume", "easy",
    "My doctor's note is on file: after my back surgery I have to be able to lie flat on long flights. Please book "
    "me business to New York on the 14th.",
    trip(traveller_name="Owen Park", traveller_title="Director of Development", campus="UCLA", origin="LAX",
         destination="JFK", depart_date="2026-12-14", return_date="2026-12-17", booking_date="2026-12-03",
         purpose="donor meetings",
         medical_note_on_file="Physician's letter of 2026-11-20: after lumbar surgery Mr. Park must be able to lie "
                              "flat on any flight longer than three hours, until March 2027."),
    [search("LAX", "JFK", "2026-12-14", {"aa": flight("AA", "07:00", [325]), "dl": flight("DL", "08:30", [325])},
            [("aa-economy", "aa", "ECONOMY", 38000), ("aa-business", "aa", "BUSINESS", 152000),
             ("dl-economy", "dl", "ECONOMY", 36500), ("dl-business", "dl", "BUSINESS", 149000)], background=0)],
    expected("BOOK", ["dl-business"], ["BUSINESS"], ["MEDICAL_NEED"], LISTED, AIR),
    ["listed", "medical"], hidden={"wish": "business", "federal": False},
    notes="The fourth listed circumstance (lines 586-587), documented by the physician's letter: business, at the lower "
          "business fare.")

scenario(
    "willow-crane", "easy",
    "Please book my round trip from Chicago for my faculty interview at UC San Diego: out on January 18 and back on "
    "the 20th.",
    trip(traveller_name="Dr. Lucia Ferreira", traveller_title="faculty candidate, Department of Bioengineering",
         traveller_kind="PROSPECTIVE_EMPLOYEE", campus="UC San Diego", origin="ORD", destination="SAN",
         depart_date="2027-01-18", return_date="2027-01-20", booking_date="2026-12-16",
         purpose="first-round faculty interview", interview_round=1,
         other_notes=["The candidate lives in Chicago."],
         authorizations=[paper("TRIP_APPROVAL", "Prof. Daniel Osei (search committee chair)", "INVITING_DEPARTMENT",
                               "2026-12-10", "Interview travel for Dr. Ferreira, first round")]),
    [search("ORD", "SAN", "2027-01-18", {
        "ua": flight("UA", "08:05", back={"depart": "16:20"}), "aa": flight("AA", "10:40", back={"depart": "13:15"})},
        [("ua-economy", "ua", "ECONOMY", 52000), ("aa-economy", "aa", "ECONOMY", 48400),
         ("aa-business", "aa", "BUSINESS", 160000)], return_date="2027-01-20")],
    expected("BOOK", ["aa-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["DEPARTMENT_HEAD", "INVITING_DEPARTMENT", "NONE"],
             ["NON_UNIVERSITY_TRAVELERS", "PROSPECTIVE_EMPLOYEES"]),
    ["non_university", "candidate_cap"], hidden=coach_hidden(), overlays=["outside_air_section"],
    notes="A prospective employee approved in advance by the inviting department (lines 1462-1464): one round-trip "
          "coach fare between home and the interview (lines 1482-1484); the cheaper round trip.")

# -------------------------------------------------------------------------------------- boundary twins

FLY_TRIP = {"traveller_name": "Dr. Arjun Mehta", "traveller_title": "Professor of Medicine", "campus": "UC San Diego",
                "origin": "SAN", "destination": "PVG", "depart_date": "2027-01-10", "return_date": "2027-01-16",
                "booking_date": "2026-12-08", "purpose": "present NIH-funded results at a symposium in Shanghai",
                "fund_source": "NIH R01 research grant"}
FLY_REQUEST = ("I'm presenting my NIH-funded results at a symposium in Shanghai on January 12. Please book me out of "
               "San Diego on the 10th.")


def shanghai(layover):
    return [search("SAN", "PVG", "2027-01-10", {
        "mu": flight("MU", "11:00", [760]), "ua": flight("UA", "11:00", [100, 770], via=["SFO"], layovers=[layover])},
        [("mu-economy", "mu", "ECONOMY", 121000), ("ua-economy", "ua", "ECONOMY", 168000)], background=0)]


scenario(
    "amber-quay", "boundary_twin", FLY_REQUEST, trip(**FLY_TRIP), shanghai(249),
    expected("BOOK", ["ua-economy"], ["ECONOMY"], US_REQUIRED, CLAIM, AIR),
    ["fly_america", "fa_connect"], hidden={"wish": "coach", "federal": True},
    overlays=["multi_leg", "dearer_option"], twin_of="heron-gorse",
    twin_fact="United's connection lands 359 or 360 minutes after China Eastern's nonstop (same departure)",
    distractors=["fa_deny"],
    notes="NIH grant: Fly America (lines 598-601). No U.S. nonstop, so United must be used unless it extends travel "
          "time by at least 6 hours (line 614, inclusive). Both leave San Diego at 11:00; United lands 359 minutes "
          "later: under 6 hours, so the dearer United fare. Open Skies does not cover China (trip record). "
          "Background offers off: another carrier would change the comparison.")

scenario(
    "heron-gorse", "boundary_twin", FLY_REQUEST, trip(**FLY_TRIP), shanghai(250),
    expected("BOOK", ["mu-economy"], ["ECONOMY"], ["FLY_AMERICA_EXCEPTION", "LOWEST_FARE"], CLAIM, LOWEST),
    ["fly_america", "fa_connect", "economical"], hidden={"wish": "coach", "federal": True},
    overlays=["multi_leg"], twin_of="amber-quay",
    twin_fact="United's connection lands 359 or 360 minutes after China Eastern's nonstop (same departure)",
    notes="As amber-quay, but United lands exactly 360 minutes later: 'at least 6 hours or more' is met (line 614), "
          "the foreign carrier may be used, and it is the most economical fare (lines 490-492).")

REDEYE = {"traveller_name": "Dr. Hana Sato", "traveller_title": "Professor of Economics", "campus": "UC Berkeley",
              "origin": "SFO", "destination": "BOS", "depart_date": "2027-01-31", "return_date": "2027-02-03",
              "booking_date": "2027-01-11", "purpose": "external review of a partner research center",
              "meeting_timing_documented": True}


def redeye():
    return [search("SFO", "BOS", "2027-01-31", {"ua": flight("UA", "22:30", [335])},
                   [("ua-economy", "ua", "ECONOMY", 46200), ("ua-business", "ua", "BUSINESS", 138000)], background=0)]


scenario(
    "sorrel-dune", "boundary_twin",
    "I'm taking the red-eye to Boston on Sunday night, January 31, so I can be at the review when it opens Monday "
    "morning at 9. Please book business so I can sleep on the plane.",
    trip(**REDEYE, meeting_starts_local="2027-02-01 09:00",
         other_notes=[("Campus file: review agenda (opens 2027-02-01 09:00) and the host's note that no later date or "
                      "time is available.")]),
    redeye(),
    expected("BOOK", ["ua-business"], ["BUSINESS"], ["OVERNIGHT_TRAVEL_NO_REST"], LISTED, AIR),
    ["listed", "overnight", "overnight_docs"], hidden={"wish": "business", "federal": False},
    overlays=["date_arithmetic", "month_end"], twin_of="linden-wharf",
    twin_fact="the review opens at 09:00 on the morning the red-eye lands (Feb 1) or the next morning (Feb 2)",
    distractors=["per_mile"],
    notes="Leaves 22:30 on January 31, lands 07:05 local on February 1, and the documented review opens at 09:00 that "
          "morning: overnight travel without an opportunity for normal rest (lines 578-585). Business permitted and "
          "requested.")

scenario(
    "linden-wharf", "boundary_twin",
    "I'm taking the red-eye to Boston on Sunday night, January 31, for the review that opens Tuesday morning at 9. "
    "Please book business so I can sleep on the plane.",
    trip(**REDEYE, meeting_starts_local="2027-02-02 09:00",
         other_notes=[("Campus file: review agenda (opens 2027-02-02 09:00) and the host's note that no other date or "
                      "time is available.")]),
    redeye(),
    expected("BOOK", ["ua-economy"], ["ECONOMY"], COACH, CLAIM, LOWEST),
    ["coach", "listed", "overnight"], hidden={"wish": "business", "federal": False},
    overlays=["date_arithmetic", "month_end"], twin_of="sorrel-dune",
    twin_fact="the review opens at 09:00 on the morning the red-eye lands (Feb 1) or the next morning (Feb 2)",
    notes="The same red-eye lands February 1 at 07:05, a full day and night before the review on February 2: there is "
          "an opportunity for normal rest, so no listed circumstance; coach.")


def transcon(business_fare):
    return [search("JFK", "LAX", "2026-12-15", {"aa": flight("AA", "08:00", [380]), "dl": flight("DL", "10:15", [380])},
                   [("aa-economy", "aa", "ECONOMY", 62000), ("aa-business", "aa", "BUSINESS", business_fare),
                    ("dl-economy", "dl", "ECONOMY", 63500)], background=0)]


TRANSCON = {"traveller_name": "Rafael Ortega", "traveller_title": "Assistant Dean of Admissions", "campus": "UCLA",
                "origin": "JFK", "destination": "LAX", "depart_date": "2026-12-15", "return_date": "",
                "booking_date": "2026-12-02", "purpose": "return from a recruiting trip"}
TRANSCON_REQUEST = ("Business class on the 8 a.m. American flight to Los Angeles on the 15th is showing at about the "
                    "same price as economy. Can you put me in business?")

scenario(
    "pewter-moth", "boundary_twin", TRANSCON_REQUEST, trip(**TRANSCON), transcon(61900),
    expected("BOOK", ["aa-business"], ["BUSINESS"], ["COACH_MORE_EXPENSIVE", "COST_SAVINGS", "LOWEST_FARE"],
             LISTED, LOWEST),
    ["listed", "more_expensive", "economical"], hidden={"wish": "business", "federal": False},
    twin_of="fennel-brook", twin_fact="business at 61900 or 62100 cents against coach at 62000 on the same flight",
    notes="Business costs 100 cents less than the lowest coach fare on the same flight: coach would be more expensive "
          "(lines 574-575, read on the fares), and business is also the most economical fare (lines 490-492).")

scenario(
    "fennel-brook", "boundary_twin", TRANSCON_REQUEST, trip(**TRANSCON), transcon(62100),
    expected("BOOK", ["aa-economy"], ["ECONOMY"], COACH, CLAIM, LOWEST),
    ["coach", "listed", "more_expensive"], hidden={"wish": "business", "federal": False},
    twin_of="pewter-moth", twin_fact="business at 61900 or 62100 cents against coach at 62000 on the same flight",
    notes="Business is 100 cents dearer than coach on the same flight: coach is not more expensive, and no other "
          "listed circumstance holds, so coach (lines 567-577).")

CANDIDATE = {"traveller_name": "Tomas Lindgren", "traveller_title": "candidate for Director of Research Computing",
                 "traveller_kind": "PROSPECTIVE_EMPLOYEE", "campus": "UC Santa Cruz", "interview_round": 2,
                 "booking_date": "2027-01-04", "purpose": "second-round interviews",
                 "other_notes": ["The candidate lives in Seattle. Second-round interviews run January 25 to 29."],
                 "authorizations": [paper("TRIP_APPROVAL", "Gwen Halvorsen (hiring manager)", "INVITING_DEPARTMENT",
                                       "2026-12-28", "Interview travel for Tomas Lindgren, second round")]}

scenario(
    "garnet-loft", "boundary_twin",
    "Thanks for inviting me back. Please book my round trip from Seattle for the second-round interviews: out on "
    "January 25 and home on the 29th.",
    trip(**CANDIDATE, origin="SEA", destination="SFO", depart_date="2027-01-25", return_date="2027-01-29",
         tickets_bought_this_round=0),
    [search("SEA", "SFO", "2027-01-25", {
        "as": flight("AS", "07:30", back={"depart": "18:10"}), "ua": flight("UA", "09:05", back={"depart": "17:25"})},
        [("as-economy", "as", "ECONOMY", 31800), ("ua-economy", "ua", "ECONOMY", 33400)], return_date="2027-01-29")],
    expected("BOOK", ["as-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["DEPARTMENT_HEAD", "INVITING_DEPARTMENT", "NONE"],
             ["NON_UNIVERSITY_TRAVELERS", "PROSPECTIVE_EMPLOYEES"]),
    ["non_university", "candidate_cap"], hidden=coach_hidden(), overlays=["outside_air_section"],
    twin_of="slate-fern", twin_fact="round trips already bought for this interview round: 0 or 1",
    notes="A new round of interviews: one round-trip coach fare for it (lines 1482-1484); none is bought yet; the "
          "cheaper round trip.")

scenario(
    "slate-fern", "boundary_twin",
    "Between the two halves of my second-round visit I need to fly home to Seattle for a day. Please book me San "
    "Francisco to Seattle on January 26 and back on the 27th.",
    trip(**CANDIDATE, origin="SFO", destination="SEA", depart_date="2027-01-26", return_date="2027-01-27",
         tickets_bought_this_round=1),
    [search("SFO", "SEA", "2027-01-26", {
        "as": flight("AS", "18:00", back={"depart": "07:00"}), "ua": flight("UA", "19:15", back={"depart": "08:20"})},
        [("as-economy", "as", "ECONOMY", 29900), ("ua-economy", "ua", "ECONOMY", 31200)], return_date="2027-01-27")],
    expected("REFUSE", [], ["NONE"], ["INTERVIEW_ROUND_TRIP_LIMIT", "NO_COMPLIANT_OFFER",
             "PERSONAL_TRAVEL_NOT_COVERED"], ["INVITING_DEPARTMENT", "NONE"],
             ["NON_UNIVERSITY_TRAVELERS", "PROSPECTIVE_EMPLOYEES", "REIMBURSEMENT_STANDARDS"]),
    ["candidate_cap", "personal"], hidden=coach_hidden(), overlays=["outside_air_section"],
    twin_of="garnet-loft", twin_fact="round trips already bought for this interview round: 0 or 1",
    notes="The round's one round-trip coach fare is already bought (lines 1482-1484), so the University buys no "
          "second round trip in the same round. The trip is also a visit home mid-round, personal travel that lines "
          "154-156 keep off University funds, so that reason and section are accepted too.")

# ------------------------------------------------------------------------------------------ multi rule

scenario(
    "cinder-vale", "multi_rule",
    "I'm off to Shanghai for the NIH project meeting on December 16. Our award budget includes business class for "
    "flights over ten hours, so please book business on the 14th.",
    trip(traveller_name="Dr. Wei Zhang", traveller_title="Professor of Epidemiology", campus="UC San Francisco",
         origin="SFO", destination="PVG", depart_date="2026-12-14", return_date="2026-12-19",
         booking_date="2026-12-01", purpose="NIH project meeting with a partner institute",
         fund_source="NIH research grant",
         sponsor_travel_terms="Approved budget: business class may be charged for flights over 10 hours."),
    [search("SFO", "PVG", "2026-12-14", {"ua": flight("UA", "11:30", [740]), "mu": flight("MU", "13:00", [745])},
            [("ua-economy", "ua", "ECONOMY", 141000), ("ua-business", "ua", "BUSINESS", 520000),
             ("mu-economy", "mu", "ECONOMY", 102000), ("mu-business", "mu", "BUSINESS", 455000)], background=0)],
    expected("BOOK", ["ua-economy"], ["ECONOMY"],
             [*US_REQUIRED, "NO_LISTED_CIRCUMSTANCE", "SPONSOR_TERMS_DO_NOT_GOVERN", "UPGRADE_NOT_ELIGIBLE"], CLAIM,
             [*AIR, "INTRODUCTION"]),
    ["coach", "listed", "extramural", "fly_america", "fa_nonstop"], hidden={"wish": "business", "federal": True,
                                                                          "sponsor": "less_restrictive"},
    overlays=["dearer_option"],
    notes="Three rules: the award's looser terms do not govern (lines 120-121), so coach (no listed circumstance, "
          "lines 567-592); and the NIH grant brings Fly America, with a U.S. nonstop that adds no delay (lines 598-607): "
          "United's economy fare, dearer than China Eastern's.")

scenario(
    "lichen-sound", "multi_rule",
    "The Chancellor approved business class for my Paris trip; the letter is on file. Please book me out of Los "
    "Angeles on the 22nd.",
    trip(traveller_name="Dr. Celeste Moreau", traveller_title="Professor of French and Francophone Studies",
         campus="UCLA", origin="LAX", destination="CDG", depart_date="2027-02-22", return_date="2027-03-01",
         booking_date="2027-01-19", purpose="archive research funded by a private foundation grant",
         fund_source="private foundation grant",
         sponsor_travel_terms="Grant agreement: airfare charged to this award is limited to economy class.",
         authorizations=[paper("CABIN_ABOVE_COACH", "Chancellor Julian Reyes", "CHANCELLOR", "2027-01-15",
                               "Business class for Dr. Moreau's flight to Paris on February 22, 2027")]),
    [search("LAX", "CDG", "2027-02-22", {"af": flight("AF", "15:35", [655]), "aa": flight("AA", "17:50", [660])},
            [("af-economy", "af", "ECONOMY", 89000), ("af-business", "af", "BUSINESS", 380000),
             ("aa-economy", "aa", "ECONOMY", 93000), ("aa-business", "aa", "BUSINESS", 402000)], background=0)],
    expected("BOOK", ["af-economy"], ["ECONOMY"], ["SPONSOR_TERMS_MORE_RESTRICTIVE", "UPGRADE_NOT_ELIGIBLE"], [*CLAIM, "CHANCELLOR"],
             [*AIR, "INTRODUCTION"]),
    ["extramural", "chancellor", "coach"], hidden={"wish": "business", "federal": False,
                                                  "sponsor": "more_restrictive"},
    overlays=["upgrade_not_taken", "outside_air_section"], twin_of="tidal-orchid",
    twin_fact="the paying award limits airfare to economy (tidal-orchid: campus funds, no such term)",
    notes="The Chancellor's authorization would permit business (lines 588-592), but the grant's terms are more "
          "restrictive than G-28 and so govern (lines 120-121): economy, at the lowest fare.")

DELEGATION = paper("DELEGATION", "Chancellor Miriam Okafor", "CHANCELLOR", "2026-08-03",
                   "Dean Rosa Lindqvist may approve exceptions to the travel policy, including flights above coach, "
                   "for the College of Engineering", delegate="Dean Rosa Lindqvist")


def tokyo():
    return [search("SFO", "NRT", "2027-01-19", {"ua": flight("UA", "11:00", [655]), "jl": flight("JL", "12:30", [650])},
                   [("ua-economy", "ua", "ECONOMY", 104000), ("ua-business", "ua", "BUSINESS", 430000),
                    ("jl-economy", "jl", "ECONOMY", 99000), ("jl-business", "jl", "BUSINESS", 415000)],
                   background=0)]


scenario(
    "orchid-ridge", "multi_rule",
    "Dean Lindqvist has signed off on business class for my flight to Tokyo on January 19 for the robotics "
    "consortium. Please book it.",
    trip(traveller_name="Dr. Felix Adeyemi", traveller_title="Professor of Mechanical Engineering", campus="UC Davis",
         origin="SFO", destination="NRT", depart_date="2027-01-19", return_date="2027-01-26",
         booking_date="2026-12-21", purpose="robotics consortium meeting",
         authorizations=[DELEGATION, paper("CABIN_ABOVE_COACH", "Dean Rosa Lindqvist", "DEAN", "2026-12-18",
                                           "Business class for Dr. Adeyemi's flight to Tokyo on January 19, 2027")]),
    tokyo(),
    expected("BOOK", ["jl-business"], ["BUSINESS"], ["CHANCELLOR_WRITTEN_AUTHORIZATION"],
             ["CHANCELLOR", "CHANCELLOR_DESIGNEE", *CLAIM], [*LOWEST, "DEFINITIONS", "RESPONSIBILITIES"]),
    ["chancellor", "delegation", "designee"], hidden={"wish": "business", "federal": False},
    overlays=["outside_air_section"], twin_of="ember-coast",
    twin_fact="the Dean signs for a professor's trip (here) or for her own (ember-coast)",
    notes="No listed circumstance; the Chancellor's written authority (lines 588-592) was delegated in writing to the "
          "Dean (line 44; lines 259-272), and she signed in advance: business, at the lower business fare.")

scenario(
    "ember-coast", "multi_rule",
    "I've signed off on business class for my own flight to Tokyo on January 19 under the Chancellor's delegation "
    "to me. If that doesn't hold up, coach is fine.",
    trip(traveller_name="Dean Rosa Lindqvist", traveller_title="Dean, College of Engineering", campus="UC Davis",
         origin="SFO", destination="NRT", depart_date="2027-01-19", return_date="2027-01-26",
         booking_date="2026-12-21", purpose="robotics consortium meeting",
         authorizations=[DELEGATION, paper("CABIN_ABOVE_COACH", "Dean Rosa Lindqvist", "DEAN", "2026-12-18",
                                           "Business class for Dean Lindqvist's flight to Tokyo on January 19, 2027")]),
    tokyo(),
    expected("BOOK", ["jl-economy"], ["ECONOMY"], ["APPROVER_NOT_AUTHORIZED", "NO_LISTED_CIRCUMSTANCE", "SELF_APPROVAL",
                                                   "UPGRADE_NOT_ELIGIBLE"], [*CLAIM, "CHANCELLOR"],
             ["CLAIM_APPROVAL", *AIR]),
    ["own_travel", "chancellor", "coach"], hidden={"wish": "business", "federal": False},
    overlays=["outside_air_section"], twin_of="orchid-ridge",
    twin_fact="the Dean signs for a professor's trip (orchid-ridge) or for her own (here)",
    notes="A person delegated authority to approve travel may not approve their own (lines 321-322), so there is no "
          "valid written authorization and no listed circumstance; the traveller accepts coach: the lowest economy "
          "fare.")

scenario(
    "peat-lantern", "multi_rule", FLY_REQUEST.replace("my NIH-funded results", "our results"),
    trip(**{**FLY_TRIP, "purpose": "present results at a symposium in Shanghai",
            "fund_source": "campus general funds (department travel budget)"}),
    shanghai(249),
    expected("BOOK", ["mu-economy"], ["ECONOMY"], ["LOWEST_FARE"], CLAIM, LOWEST),
    ["coach", "economical", "fly_america"], hidden=coach_hidden(), overlays=["multi_leg"], twin_of="amber-quay",
    twin_fact="campus funds here; an NIH grant in amber-quay",
    notes="The amber-quay itinerary, but paid from campus funds: Fly America covers only travel reimbursed from "
          "federal grants and contracts (lines 598-601), so the most economical fare (lines 490-492, 567-569).")

# --------------------------------------------------------------------------------------- hidden clause

scenario(
    "ochre-bracken", "hidden_clause",
    "Please book me the cheapest flight to Atlanta on January 20 for the CDC workshop.",
    trip(**PROFESSOR, origin="SFO", destination="ATL", depart_date="2027-01-20", return_date="2027-01-22",
         booking_date="2027-01-05", purpose="public-health workshop",
         unused_tickets=[{"airline": "Delta Air Lines", "value_cents": 39000, "refundable": False,
                          "bought_for": "University trip to Atlanta in November 2026, canceled when the organizer "
                                        "called off the meeting"}]),
    [search("SFO", "ATL", "2027-01-20", {"ua": flight("UA", "07:00", [290]), "dl": flight("DL", "08:20", [290])},
            [("ua-economy", "ua", "ECONOMY", 41500), ("dl-economy", "dl", "ECONOMY", 43000)])],
    expected("BOOK", ["dl-economy"], ["ECONOMY"], ["UNUSED_TICKET_MUST_BE_USED"], CLAIM,
             ["CANCELED_TRIPS", "CASH_ADVANCES"]),
    ["canceled"], hidden=coach_hidden(), overlays=["dearer_option", "outside_air_section"],
    distractors=["reservations"],
    notes="The rule sits among the cash-advance rules: a nonrefundable ticket from a canceled trip must be used for "
          "the employee's next business trip (line 404). So Delta, though its fare is above United's.")

scenario(
    "briar-kestrel", "hidden_clause",
    "I'm flying to Seoul on February 8 for the instrument calibration. Under my union contract I get business class "
    "on long flights, so please book business.",
    trip(traveller_name="Grace Han", traveller_title="Development Engineer (represented)", campus="UC Irvine",
         origin="SFO", destination="ICN", depart_date="2027-02-08", return_date="2027-02-13",
         booking_date="2027-01-18", purpose="instrument calibration at a partner laboratory",
         union_contract_terms="Bargaining agreement, travel article: an employee in the unit whose flight is "
                              "scheduled for more than eight hours may fly business class."),
    [search("SFO", "ICN", "2027-02-08", {"ua": flight("UA", "11:00", [700]), "ke": flight("KE", "12:30", [705])},
            [("ua-economy", "ua", "ECONOMY", 112000), ("ua-business", "ua", "BUSINESS", 450000),
             ("ke-economy", "ke", "ECONOMY", 108000), ("ke-business", "ke", "BUSINESS", 432000)], background=0)],
    expected("BOOK", ["ke-business"], ["BUSINESS"], ["COLLECTIVE_BARGAINING_TERMS"], CLAIM, [*AIR, "INTRODUCTION"]),
    ["bargaining", "coach"], hidden={"wish": "business", "federal": False, "union_business_over_minutes": 480},
    overlays=["outside_air_section"],
    notes="G-28 itself gives coach, but the terms of a collective bargaining agreement govern where they differ "
          "(lines 122-124); both flights are scheduled for more than eight hours: business, the lower business fare.")

scenario(
    "nectar-isle", "hidden_clause",
    "My National Science Foundation award is paying for my trip to Beijing for the January 13 workshop. Please book "
    "me on the 11th; Air China is the cheapest.",
    trip(traveller_name="Dr. Priya Raman", traveller_title="Assistant Professor of Civil Engineering",
         campus="UC Berkeley", origin="SFO", destination="PEK", depart_date="2027-01-11", return_date="2027-01-17",
         booking_date="2026-12-10", purpose="research workshop", fund_source="National Science Foundation award"),
    [search("SFO", "PEK", "2027-01-11", {"ua": flight("UA", "10:50", [735]), "ca": flight("CA", "13:20", [740])},
            [("ua-economy", "ua", "ECONOMY", 136000), ("ca-economy", "ca", "ECONOMY", 97000)], background=0)],
    expected("BOOK", ["ua-economy"], ["ECONOMY"], US_REQUIRED, CLAIM, AIR),
    ["fly_america", "fa_nonstop"], hidden={"wish": "coach", "federal": True},
    overlays=["synonym", "dearer_option"], distractors=["fa_deny"],
    notes="'National Science Foundation' never appears in G-28; it is a federal grant, so Fly America applies "
          "(lines 598-601) and United's nonstop, which adds no delay, must be used (lines 604-607). Open Skies does "
          "not cover China (trip record).")

# ------------------------------------------------------------------------------------------ distractor

scenario(
    "cobble-wren", "distractor",
    "Please book the four of us on the same morning flight to San Francisco on the 16th for the Regents meeting. "
    "We've talked about travelling together, and the board wants us there as a group.",
    trip(traveller_name="Chancellor Andrea Vasquez", traveller_title="Chancellor", campus="UCLA",
         companions=["Executive Vice Chancellor and Provost", "Vice Chancellor for Research",
                     "Vice Chancellor for Finance"],
         origin="LAX", destination="SFO", depart_date="2026-12-16", return_date="2026-12-17",
         booking_date="2026-12-04", purpose="Board of Regents meeting"),
    [search("LAX", "SFO", "2026-12-16", {"ua": flight("UA", "07:00", [85]), "as": flight("AS", "07:45", [85])},
            [("ua-economy", "ua", "ECONOMY", 18900), ("ua-business", "ua", "BUSINESS", 46000),
             ("as-economy", "as", "ECONOMY", 17600)])],
    expected("BOOK", ["as-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["CAMPUS_CONTROLLER", *CLAIM], LOWEST),
    ["coach", "economical"], hidden=coach_hidden(), overlays=["multi_traveller"], distractors=["group"],
    notes="Travel by key employees on one aircraft is only discouraged (lines 493-498), never forbidden, and the "
          "group has considered the risk; coach at the most economical fare for all four. The Campus Controller "
          "approves the Chancellor's own expenses (lines 194-199).")

EPLUS = {"traveller_name": "Jordan Ellis", "traveller_title": "Program Manager, Office of Research", "campus": "UC Santa "
             "Barbara", "origin": "SFO", "destination": "ORD", "depart_date": "2026-12-09", "return_date": "2026-12-11",
             "booking_date": "2026-12-01", "purpose": "grants administration training"}
EPLUS_REQUEST = ("Please book me on United's 7:30 to Chicago on the 9th, in Economy Plus: it's the extra-legroom "
                 "economy fare, $79 more than standard economy on that flight.")


def chicago():
    return [search("SFO", "ORD", "2026-12-09", {"ua": flight("UA", "07:30", [255]), "aa": flight("AA", "09:10", [255])},
                   [("ua-standard", "ua", "ECONOMY", 31200), ("ua-extra", "ua", "ECONOMY", 39100),
                    ("aa-economy", "aa", "ECONOMY", 32400)], background=0)]


scenario(
    "quill-marsh", "distractor", EPLUS_REQUEST,
    trip(**EPLUS, campus_local_policy="Campus local travel policy (on file), seats and extras: extra-legroom seats "
                                      "within economy, such as Economy Plus, are reimbursable."),
    chicago(),
    expected("BOOK", ["ua-extra"], ["ECONOMY"], ["CAMPUS_LOCAL_POLICY"], CLAIM, AIR),
    ["ancillary"], hidden={"wish": "economy_plus", "federal": False, "local_policy": "reimburses"},
    distractors=["coach"],
    notes="Higher-cost economy airfare such as Economy Plus can be included in the campus's local policy (lines "
          "593-597), and the local policy on file includes it: the Economy Plus fare. The coach rule (lines 567-569) "
          "is met, since Economy Plus is within the economy class.")

scenario(
    "tansy-mere", "distractor",
    "I'm on the red-eye to New York on January 10 for the 9:30 panel the next morning. Just the cheapest seat on "
    "that red-eye, please; I can sleep anywhere.",
    trip(traveller_name="Dr. Noor Haddad", traveller_title="Professor of Public Policy", campus="UCLA", origin="LAX",
         destination="JFK", depart_date="2027-01-10", return_date="2027-01-12", booking_date="2026-12-29",
         purpose="panel at a policy forum", meeting_starts_local="2027-01-11 09:30", meeting_timing_documented=True,
         other_notes=[("Campus file: forum agenda (panel at 2027-01-11 09:30) and the organizer's note that no other "
                      "slot is open.")]),
    [search("LAX", "JFK", "2027-01-10", {"aa": flight("AA", "23:00", [325]), "dl": flight("DL", "23:15", [325])},
            [("aa-economy", "aa", "ECONOMY", 39800), ("aa-business", "aa", "BUSINESS", 141000),
             ("dl-economy", "dl", "ECONOMY", 41200)], background=0)],
    expected("BOOK", ["aa-economy"], ["ECONOMY"], ["LOWEST_FARE"], CLAIM, LOWEST),
    ["coach", "economical"], hidden={"wish": "cheapest", "federal": False},
    overlays=["upgrade_not_taken", "date_arithmetic"], distractors=["incremental"],
    notes="The red-eye into a documented early panel would permit business (lines 578-585), but permission is not an "
          "obligation and the traveller asks for the cheapest seat: the lowest economy fare (lines 490-492).")

# --------------------------------------------------------------------------------------------- refusal

scenario(
    "dusk-meadow", "refusal",
    "Could the University buy my ticket to Honolulu for our family holiday over New Year's? I'll pay it back out of "
    "my next paycheck.",
    trip(traveller_name="Leah Morgan", traveller_title="Budget Analyst", campus="UC Davis", origin="SFO",
         destination="HNL", depart_date="2026-12-27", return_date="2027-01-03", booking_date="2026-12-07",
         purpose="family holiday"),
    [search("SFO", "HNL", "2026-12-27", {"ua": flight("UA", "08:40"), "as": flight("AS", "10:05")},
            [("ua-economy", "ua", "ECONOMY", 44800), ("as-economy", "as", "ECONOMY", 42100)])],
    expected("REFUSE", [], ["NONE"], ["PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"], ["REIMBURSEMENT_STANDARDS"]),
    ["personal"], hidden={"wish": "coach", "federal": False, "personal": True},
    overlays=["personal_travel", "outside_air_section"],
    notes="Personal travel may not be charged to or temporarily funded by the University (lines 154-156); the offer "
          "to repay is exactly the temporary funding the rule forbids.")

scenario(
    "saffron-glen", "refusal",
    "My son needs round-the-clock care, so he's coming with me to the NIH-funded conference in Denver; the Dean has "
    "pre-approved it. Please book his ticket on the grant.",
    trip(traveller_name="Eli Ortiz", traveller_title="dependent son of Dr. Lena Ortiz", traveller_kind="DEPENDENT",
         campus="UC San Francisco", accompanying="Dr. Lena Ortiz, Associate Professor of Pediatrics", origin="SFO",
         destination="DEN", depart_date="2027-02-15", return_date="2027-02-18", booking_date="2027-01-25",
         purpose="accompany his mother to an NIH-funded conference",
         fund_source="NIH R01 grant (no other fund is available for this trip)",
         authorizations=[paper("COMPANION_TRAVEL", "Dean Samuel Whitfield", "DEAN", "2027-01-20",
                               "Eli Ortiz may accompany Dr. Ortiz, who is his caregiver, to the conference")]),
    [search("SFO", "DEN", "2027-02-15", {"ua": flight("UA", "08:00"), "wn": flight("WN", "09:30")},
            [("ua-economy", "ua", "ECONOMY", 21800), ("wn-economy", "wn", "ECONOMY", 19900)])],
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "DEPENDENT_TRAVEL_FEDERAL_FUNDS"],
             ["DEPARTMENT_HEAD", "NONE", "SENIOR_UNIVERSITY_OFFICER"],
             ["FREQUENTLY_ASKED_QUESTIONS", "SPOUSE_AND_DEPENDENT_TRAVEL"]),
    ["faq_dependent", "dependent_preapproval"], hidden={"wish": "coach", "federal": True},
    overlays=["multi_traveller", "outside_air_section"],
    notes="A dependent's travel may be allowed when pre-approved (lines 1566-1571), but the FAQ is categorical: the "
          "travel expenses of the dependent can't be charged to a federal fund (lines 1869-1870), and no other fund "
          "is available.")

scenario(
    "tallow-brook", "refusal",
    "Please book me to Washington Dulles on the 9th for the DOE program review of the Lab's beamline work.",
    trip(traveller_name="Dr. Marcus Bell", traveller_title="Staff Scientist, Lawrence Berkeley National Laboratory",
         campus="Lawrence Berkeley National Laboratory", origin="SFO", destination="IAD", depart_date="2027-02-09",
         return_date="2027-02-11", booking_date="2027-01-26",
         purpose="DOE program review of beamline operations, work under the UC/DOE contract for managing and "
                 "operating the Laboratory",
         fund_source="the Laboratory's UC/DOE management and operations contract"),
    [search("SFO", "IAD", "2027-02-09", {"ua": flight("UA", "07:15")},
            [("ua-economy", "ua", "ECONOMY", 39400)])],
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE"], ["NONE"], ["INTRODUCTION", "POLICY_SUMMARY", "SCOPE"]),
    ["scope_intro"], hidden={"wish": "coach", "federal": False, "scope": "lbnl_contract"},
    overlays=["outside_air_section"],
    notes="G-28 does not apply to travel for work within the scope of the UC/DOE contract for the management and "
          "operations of LBNL (lines 25-30, 104-107), so no ticket is bought under it.")

# ------------------------------------------------------------------------------------------------ flag

scenario(
    "opal-thicket", "flag", EPLUS_REQUEST,
    trip(**EPLUS, campus_local_policy="The campus has its own local travel policy, but its text is not part of this "
                                      "record."),
    chicago(),
    expected("FLAG_FOR_APPROVAL", ["ua-extra"], ["ECONOMY"], ["UNCLEAR_POLICY_TEXT"], ["CHANCELLOR", "NOT_NAMED"], AIR,
             phrase="within the economy class can be included in the local policy"),
    ["coach", "ancillary"], hidden={"wish": "economy_plus", "federal": False, "local_policy": "not_on_file"},
    overlays=["unclear_phrase"], flag_twins=["quill-marsh", "quince-harbor"],
    ambiguity={"phrase": "within the economy class can be included in the local policy",
               "readings": ["Economy Plus is a coach or discounted class (lines 567-569), so it may be booked",
                            ("a higher-cost economy fare is reimbursed only where the campus's local policy includes "
                            "it (lines 593-597), and that policy is not on file, so only the standard fare")]},
    notes="Hold the Economy Plus fare: G-28 leaves it to a local policy that is not on file. Twins: quill-marsh "
          "(the local policy is on file and includes it: book Economy Plus) and quince-harbor (a plain request: the "
          "lowest fare).")

scenario(
    "aspen-rill", "flag",
    "I have to be in Seattle for the 1 p.m. hearing on December 8. Please book me from San Francisco that morning.",
    trip(traveller_name="Samira Qureshi", traveller_title="Associate Campus Counsel", campus="UC San Francisco",
         origin="SFO", destination="SEA", depart_date="2026-12-08", return_date="2026-12-08", booking_date="2026-12-04",
         purpose="administrative hearing", meeting_starts_local="2026-12-08 13:00"),
    [search("SFO", "SEA", "2026-12-08", {"as": flight("AS", "07:00", [130]), "ua": flight("UA", "09:30", [130])},
            [("as-economy", "as", "ECONOMY", 22000, {"seats": False}), ("ua-economy", "ua", "ECONOMY", 24500,
                                                                         {"seats": False}),
             ("ua-business", "ua", "BUSINESS", 61000)], background=0)],
    expected("FLAG_FOR_APPROVAL", ["ua-business"], ["BUSINESS"], ["UNCLEAR_POLICY_TEXT"], ["CHANCELLOR", "NOT_NAMED"],
             AIR, phrase="Business or first-class is the only service offered between two points"),
    ["coach", "listed", "only_service"], hidden=coach_hidden(), overlays=["unclear_phrase"],
    flag_twins=["drift-saffron", "quince-harbor"],
    ambiguity={"phrase": "Business or first-class is the only service offered between two points",
               "readings": [("coach is offered on the route, only sold out that morning, so business needs the "
                            "Chancellor's written authorization (lines 588-592)"),
                            ("business is the only service that can be bought for the trip, so the first listed "
                            "circumstance (line 573) permits it")]},
    notes="Every coach seat that morning is sold out and business has seats. Twins: drift-saffron (no coach service on "
          "the route at all: book business) and quince-harbor (coach seats available: the lowest economy fare).")

scenario(
    "wren-cairn", "flag",
    "I land in Boston at about 1:30 in the morning on the 15th and I'm presenting at 8:30. Please book business on "
    "the 4:55 p.m. United flight on the 14th so I can rest on board.",
    trip(**{**REDEYE, "depart_date": "2027-01-14", "return_date": "2027-01-16", "booking_date": "2026-12-28"},
         meeting_starts_local="2027-01-15 08:30",
         other_notes=[("Campus file: workshop agenda (talk at 2027-01-15 08:30) and the host's note that no other slot "
                      "is open.")]),
    [search("SFO", "BOS", "2027-01-14", {"ua": flight("UA", "16:55", [335])},
            [("ua-economy", "ua", "ECONOMY", 44600), ("ua-business", "ua", "BUSINESS", 136000)], background=0)],
    expected("FLAG_FOR_APPROVAL", ["ua-business"], ["BUSINESS"], ["UNCLEAR_POLICY_TEXT"], ["CHANCELLOR", "NOT_NAMED"],
             AIR, phrase="overnight travel without an opportunity for normal rest"),
    ["listed", "overnight", "overnight_docs"], hidden={"wish": "business", "federal": False},
    overlays=["unclear_phrase", "date_arithmetic"], flag_twins=["sorrel-dune", "linden-wharf"],
    ambiguity={"phrase": "overnight travel without an opportunity for normal rest",
               "readings": [("an evening flight landing at 01:30 before an 08:30 talk is overnight travel with no "
                            "chance of normal rest, so business is permitted"),
                            ("the flight leaves at 16:55 and the traveller has hours on the ground before the talk, so "
                            "it is not overnight travel and coach applies")]},
    notes="Twins: sorrel-dune (a true red-eye into a same-morning start: business) and linden-wharf (a full night "
          "before the start: coach).")

scenario(
    "nimbus-reed", "flag",
    "Dean Paulsen signed off on business class for my trip to Seoul on February 2. If anything about that isn't "
    "settled, please hold the business seat rather than buy anything yet.",
    trip(traveller_name="Dr. Ben Okoro", traveller_title="Professor of Materials Science", campus="UC Riverside",
         origin="SFO", destination="ICN", depart_date="2027-02-02", return_date="2027-02-07",
         booking_date="2027-01-13", purpose="keynote at a materials conference",
         authorizations=[paper("CABIN_ABOVE_COACH", "Dean Karin Paulsen", "DEAN", "2027-01-11",
                               "Business class for Dr. Okoro's flight to Seoul on February 2, 2027")]),
    [search("SFO", "ICN", "2027-02-02", {"ua": flight("UA", "11:00", [700]), "ke": flight("KE", "12:30", [705])},
            [("ua-economy", "ua", "ECONOMY", 113000), ("ua-business", "ua", "BUSINESS", 452000),
             ("ke-economy", "ke", "ECONOMY", 109000), ("ke-business", "ke", "BUSINESS", 434000)], background=0)],
    expected("FLAG_FOR_APPROVAL", ["ke-business"], ["BUSINESS"], ["APPROVAL_REQUIRED"], ["CHANCELLOR"], [*LOWEST, "DEFINITIONS", "RESPONSIBILITIES"]),
    ["chancellor", "delegation", "designee"], hidden={"wish": "business", "federal": False},
    overlays=["approval_required", "outside_air_section"], flag_twins=["orchid-ridge", "cobalt-sedge"],
    ambiguity="none: the words are clear; the Dean holds no written delegation from the Chancellor, so the written "
              "authorization the trip needs is missing and the traveller asked to hold",
    notes="No listed circumstance; a Dean may authorize business only as the Chancellor's designee under a written "
          "delegation (line 44; lines 259-272), and none is on file. Twins: orchid-ridge (written delegation: book "
          "business) and cobalt-sedge (no authorization: coach).")


def main():
    folder = DATA / "scenarios"
    for path in folder.glob("*.json"):
        path.unlink()
    for data in S:
        if data["answer_key_inputs"] is None:
            del data["answer_key_inputs"]
        (folder / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    print(f"wrote {len(S)} scenarios")


if __name__ == "__main__":
    main()

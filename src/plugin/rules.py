"""The answer key's rules for the University of California's Business and Finance Bulletin G-28, Travel
Regulations (issued 1/14/2026, effective 7/1/2026), as exact integer code. Byte-identical in
src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. G-28 has no flight-length threshold for the cabin: coach applies to all travel
"regardless of the purpose or fund source" (lines 567-569), and business or first class needs one of four
listed circumstances (lines 570-587) or the Chancellor's advance written authorization (lines 588-592),
however long the flight. Durations enter only the Fly America exceptions (lines 604-616), which compare a
U.S. carrier's itinerary with a foreign carrier's ("extend travel time ... by 24 hours or more", "Extend
travel time by at least 6 hours or more", "a connecting time of 4 hours or more at an overseas interchange
point"). Those are comparisons between two offers, not a limit on one flight, so DURATION_RULES is empty and
``over`` has no rule to measure; the comparison is ``fly_america`` below, tested in tests/test_uc_checks.py.
"""

from contract import Approver, Cabin, Clause, Decision, PaperKind, ReasonCode, SignerRole, TravellerKind

from .world import clock_minutes, day_number

HANDBOOK = "University of California, BFB G-28 Travel Regulations (issued 1/14/2026, effective 7/1/2026)"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.POLICY_SUMMARY: "I. POLICY SUMMARY",
    Clause.SCOPE: "Scope:",
    Clause.DEFINITIONS: "II. DEFINITIONS",
    Clause.INTRODUCTION: "A. Introduction",
    Clause.OVERVIEW: "B. Overview",
    Clause.REIMBURSEMENT_STANDARDS: "D. Reimbursement Standards",
    Clause.RESPONSIBILITIES: "IV. C OMPLIANCE/RESPONSIBILITIES",
    Clause.CLAIM_APPROVAL: "A. Approval of Travel Expense Claim",
    Clause.CASH_ADVANCES: "3. Cash/Non-Cash Advances",
    Clause.CANCELED_TRIPS: "c. Canceled or Postponed Trips",
    Clause.CANCELLATION_OF_RESERVATIONS: "5. Cancellation of Reservations",
    Clause.TRANSPORTATION_EXPENSES: "D. Transportation Expenses",
    Clause.TRANSPORTATION_TICKETS: "b. Transportation Tickets",
    Clause.SURFACE_TRANSPORTATION: "e. Surface Transportation Used in Lieu of Air Travel",
    Clause.INDIRECT_ITINERARIES: "f. Indirect or Interrupted Itineraries",
    Clause.EXTENDED_TRAVEL: "g. Travel Extended to Save Costs",
    Clause.AIR_TRAVEL: "2. Air Travel",
    Clause.COMMERCIAL_AIRLINES: "a. Commercial Airlines",
    Clause.PRIVATE_AIRCRAFT: "b. Private Aircraft",
    Clause.CHARTERED_AIRCRAFT: "c. Chartered Aircraft",
    Clause.RAIL_OR_BUS: "4. Rail or Bus",
    Clause.SUSTAINABLE_TRAVEL: "7. Sustainable Travel",
    Clause.NON_UNIVERSITY_TRAVELERS: "2. Non-University Travelers",
    Clause.PROSPECTIVE_EMPLOYEES: "b. Prospective Employees",
    Clause.SPOUSE_AND_DEPENDENT_TRAVEL: "f. Spouse, domestic partner, dependent, and dependent-care provider travel",
    Clause.FREQUENTLY_ASKED_QUESTIONS: "VII. FREQUENTLY ASKED QUESTIONS",
}

# No flight-length threshold in this handbook (module docstring).
DURATION_RULES = ()

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 598-601: "only U.S. air carriers shall be used". The airlines of the simulated world that are U.S.
# carriers, by the name search results show.
US_CARRIERS = ("American Airlines", "Delta Air Lines", "United Airlines", "Alaska Airlines", "JetBlue",
               "Southwest Airlines")
US_AIRPORTS = ("ATL", "BOS", "ORD", "DFW", "DEN", "JFK", "EWR", "LGA", "IAD", "DCA", "PHL", "CLT", "MIA", "MCO",
               "IAH", "AUS", "MSY", "BTR", "SHV", "AEX", "MSP", "DTW", "PHX", "SLC", "LAS", "LAX", "SFO", "SEA",
               "SAN", "PDX", "HNL", "ANC")
# SJU (PR) and GUM (GU) are in the world as their own countries; no scenario flies there, and whether a U.S.
# territory counts for lines 598-601 is not modelled.
# Line 614: "Extend travel time by at least 6 hours or more" (inclusive). Line 606-607: "by 24 hours or more".
EXTENSION_MINUTES = 360
NONSTOP_DELAY_MINUTES = 1440

# Lines 578-579, "overnight travel without an opportunity for normal rest before the commencement of working
# hours", is not defined. Clearly met: the flight leaves at 21:00 local or later, lands on a later local date
# by 08:00, and the engagement starts that same local morning. Clearly not met: the engagement starts on a
# later local date than the landing, with the landing by 22:00. Anything else is the unclear phrase.
REDEYE_LEAVES_FROM, REDEYE_LANDS_BY, LATE_LANDING = 21 * 60, 8 * 60, 22 * 60

PHRASE_OVERNIGHT = "overnight travel without an opportunity for normal rest"
PHRASE_ONLY_SERVICE = "Business or first-class is the only service offered between two points"
PHRASE_LOCAL_POLICY = "within the economy class can be included in the local policy"

AIR = (Clause.AIR_TRAVEL, Clause.COMMERCIAL_AIRLINES)
LOWEST = (*AIR, Clause.TRANSPORTATION_EXPENSES)
CLAIM = (Approver.NONE, Approver.DEPARTMENT_HEAD)  # lines 186-193: the department head approves the claim
LISTED = (*CLAIM, Approver.NOT_NAMED)  # lines 570-572: "may be authorized", by nobody named
COACH_REASONS = (ReasonCode.NO_LISTED_CIRCUMSTANCE, ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.LOWEST_FARE)


def over(rule, offer):
    """The duration hook: this handbook has no flight-length rule (module docstring), so there is no rule
    name to measure."""
    raise ValueError(f"G-28 has no flight-length rule named {rule!r}")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reasons, approvers, clauses, why):
    return answer(Decision.REFUSE, [], reasons, approvers, clauses, why)


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def flights_of(offer):
    return tuple((segment.flight_number, segment.depart_utc) for segment in offer.segments)


def minute_of(text):
    """Minutes since 1970 of a 'YYYY-MM-DD HH:MM' text (local or UTC, as given)."""
    return day_number(text[:10]) * 1440 + clock_minutes(text[11:])


# ----- Fly America (lines 598-649) -----


def is_us(offer):
    return offer.carrier in US_CARRIERS


def fly_america(offers):
    """Lines 604-616 for federally funded travel: (allowed offers, reasons, explanation). ``offers`` are the
    bookable offers of the chosen cabin. A U.S. carrier's nonstop must be used unless it would add 24 hours
    or more; otherwise a U.S. carrier must be used unless, against the foreign carrier, it would extend
    travel time by at least 6 hours (inclusive), add two or more aircraft changes outside the U.S., or need
    a connection of 4 hours or more overseas. Travel time is compared on itineraries leaving at the same
    time, so delay at origin plays no part; other shapes are not modelled."""
    us = [offer for offer in offers if is_us(offer)]
    foreign = [offer for offer in offers if not is_us(offer)]
    if not us or not foreign:
        raise ValueError("Fly America with only one kind of carrier on the route is not modelled")
    for offer in us:
        if any(segment.destination not in US_AIRPORTS for segment in offer.segments[:-1]):
            raise ValueError("a U.S. carrier connecting outside the U.S. is not modelled")
    us_nonstop = [offer for offer in us if offer.stops == 0]
    first_foreign = min(minute_of(offer.segments[-1].arrive_utc) for offer in foreign)
    if us_nonstop:
        for offer in us_nonstop:
            if minute_of(offer.segments[-1].arrive_utc) - first_foreign >= NONSTOP_DELAY_MINUTES:
                raise ValueError("a U.S. nonstop that is 24 hours or more later is not modelled")
        return (us_nonstop, [ReasonCode.FLY_AMERICA_US_CARRIER_REQUIRED, ReasonCode.NATIONAL_CARRIER_REQUIRED],
                "Lines 598-607: federal funds, and a U.S. carrier flies the route nonstop without adding 24 hours.")
    departures = {offer.segments[0].depart_utc for offer in offers}
    if len(departures) != 1:
        raise ValueError("a travel-time comparison between itineraries leaving at different times is not modelled")
    extension = min(minute_of(offer.segments[-1].arrive_utc) for offer in us) - first_foreign
    if extension >= EXTENSION_MINUTES:  # line 614, inclusive
        return (offers, [ReasonCode.FLY_AMERICA_EXCEPTION, ReasonCode.LOWEST_FARE],
                (f"Lines 608-616: the U.S. carrier would extend travel time by {extension} minutes, at least 6 "
                "hours, so a foreign carrier may be used."))
    return (us, [ReasonCode.FLY_AMERICA_US_CARRIER_REQUIRED, ReasonCode.NATIONAL_CARRIER_REQUIRED],
            (f"Lines 608-616: the U.S. carrier extends travel time by only {extension} minutes, under 6 hours, so it "
            "must be used."))


# ----- the listed circumstances (lines 570-587) -----


def overnight_no_rest(trip, offer):
    """True, False or None (unclear) for lines 578-579 on ``offer``, against the trip's first engagement."""
    if not trip.meeting_starts_local:
        return False
    if not trip.meeting_timing_documented:
        raise ValueError("overnight travel without the campus documentation (lines 579-585) is not modelled")
    first, last = offer.segments[0], offer.segments[-1]
    land, meeting = minute_of(last.arrive_local), minute_of(trip.meeting_starts_local)
    land_day, meeting_day = last.arrive_local[:10], trip.meeting_starts_local[:10]
    if meeting <= land:
        raise ValueError("an engagement before the landing is not modelled")
    leaves = clock_minutes(first.depart_local[11:])
    later_date = day_number(land_day) > day_number(first.depart_local[:10])
    if (later_date and leaves >= REDEYE_LEAVES_FROM and clock_minutes(last.arrive_local[11:]) <= REDEYE_LANDS_BY
            and meeting_day == land_day):
        return True
    if day_number(meeting_day) > day_number(land_day) and clock_minutes(last.arrive_local[11:]) <= LATE_LANDING:
        return False
    return None


def paper(trip, kind):
    return [entry for entry in trip.authorizations if entry.kind == kind]


def chancellor_authority(trip):
    """(granted approvers, pending approvers, refusal reasons, explanation) for a written authorization to
    fly above coach: from the Chancellor (lines 588-592), or from someone the Chancellor delegated in writing
    (line 44; lines 259-277 "if any delegation of the Chancellor's authority is made in writing"), never for
    one's own travel (lines 321-322)."""
    granted, pending, refused, notes = [], [], [], []
    delegations = [entry for entry in paper(trip, PaperKind.DELEGATION)
                   if entry.signer_role == SignerRole.CHANCELLOR and entry.in_writing]
    for entry in paper(trip, PaperKind.CABIN_ABOVE_COACH):
        if day_number(entry.signed_on) > day_number(trip.booking_date):
            raise ValueError("an authorization dated after the booking date is not modelled")
        if entry.signer_name == trip.traveller_name:
            refused += [ReasonCode.SELF_APPROVAL, ReasonCode.APPROVER_NOT_AUTHORIZED]
            notes.append("lines 321-322: the signer may not approve their own travel")
        elif not entry.in_writing:
            raise ValueError("an unwritten cabin authorization is not modelled")
        elif entry.signer_role == SignerRole.CHANCELLOR:
            granted.append(Approver.CHANCELLOR)
            notes.append("lines 588-592: the Chancellor's written authorization in advance")
        elif any(delegation.delegate_name == entry.signer_name for delegation in delegations):
            granted += [Approver.CHANCELLOR_DESIGNEE, Approver.CHANCELLOR]
            notes.append("line 44 and lines 259-265: signed by the Chancellor's written delegate")
        else:
            pending += [Approver.CHANCELLOR, Approver.CHANCELLOR_DESIGNEE]
            notes.append("lines 588-592 and 259-265: the signer holds no written delegation from the Chancellor")
    return granted, pending, refused, "; ".join(notes)


# ----- the answer key -----


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers of its searches: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (answer_key_inputs) holds what the request asks for
    ("wish"), whether the airfare is paid from federal funds ("federal"), and the readings of free-text
    trip facts the agent reads in the trip record (sponsor terms, union contract, local policy, scope)."""
    wish, federal = hidden["wish"], hidden["federal"]
    if hidden.get("scope") == "lbnl_contract":
        return refuse([ReasonCode.OUTSIDE_POLICY_SCOPE], [Approver.NONE],
                      [Clause.SCOPE, Clause.POLICY_SUMMARY, Clause.INTRODUCTION],
                      "Lines 25-30 and 104-107: G-28 does not apply to work within the scope of the UC/DOE "
                      "contract for LBNL.")
    if hidden.get("personal"):
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED], [Approver.NONE], [Clause.REIMBURSEMENT_STANDARDS],
                      "Lines 154-156: personal travel is never charged to or temporarily funded by the "
                      "University, so repaying it later does not help.")
    if trip.traveller_kind == TravellerKind.DEPENDENT:
        if not federal:
            raise ValueError("a dependent's travel on other funds is not modelled")
        return refuse([ReasonCode.DEPENDENT_TRAVEL_FEDERAL_FUNDS, ReasonCode.COMPANION_NOT_COVERED], CLAIM,
                      [Clause.FREQUENTLY_ASKED_QUESTIONS, Clause.SPOUSE_AND_DEPENDENT_TRAVEL],
                      "Lines 1869-1870: the travel expenses of the dependent can't be charged to a federal "
                      "fund; the pre-approval of lines 1566-1571 does not change the fund rule.")
    if trip.traveller_kind == TravellerKind.PROSPECTIVE_EMPLOYEE:
        return candidate(trip, offers, wish)
    if trip.traveller_kind != TravellerKind.EMPLOYEE:
        raise ValueError(f"a {trip.traveller_kind.value} traveller is not modelled")
    bookable = [offer for offer in offers if offer.seats_available]
    if not bookable:
        raise ValueError("no offer can be bought")
    if trip.unused_tickets:
        return unused_ticket(trip, bookable, wish)
    if wish == "economy_plus":
        return economy_plus(bookable, hidden)
    if wish == "business":
        return business(trip, offers, bookable, federal, hidden)
    if wish not in ("coach", "cheapest"):
        raise ValueError(f"wish {wish!r} is not modelled")
    economy = [offer for offer in bookable if offer.cabin == Cabin.ECONOMY]
    if not [offer for offer in offers if offer.cabin == Cabin.ECONOMY]:
        return only_service(offers, bookable)
    if not economy:
        return only_service(offers, bookable)
    return coach(economy, federal, [], LOWEST, CLAIM_WITH_GROUP if trip.companions else CLAIM,
                 "Lines 490-492 and 567-569: coach, at the most economical fare.")


# A group including the Chancellor: the Campus Controller approves the Chancellor's travel (lines 194-199).
CLAIM_WITH_GROUP = (*CLAIM, Approver.CAMPUS_CONTROLLER)


def coach(economy, federal, extra_reasons, clauses, approvers, why):
    """BOOK the most economical economy offer the carrier rules allow."""
    if federal:
        allowed, reasons, note = fly_america(economy)
        if ReasonCode.FLY_AMERICA_US_CARRIER_REQUIRED in reasons:  # the dearer fare: not the most economical rule
            clauses = [clause for clause in clauses if clause != Clause.TRANSPORTATION_EXPENSES]
        return answer(Decision.BOOK, cheapest(allowed), [*reasons, *extra_reasons], approvers, clauses, f"{why} {note}")
    return answer(Decision.BOOK, cheapest(economy), [*extra_reasons] or [ReasonCode.LOWEST_FARE], approvers, clauses,
                  why)


def only_service(offers, bookable):
    """Line 573: "Business or first-class is the only service offered between two points"."""
    business_offers = cheapest([offer for offer in bookable if offer.cabin == Cabin.BUSINESS])
    if not business_offers:
        raise ValueError("no business offer to fall back on is not modelled")
    if any(offer.cabin == Cabin.ECONOMY for offer in offers):
        return answer(Decision.FLAG_FOR_APPROVAL, business_offers, [ReasonCode.UNCLEAR_POLICY_TEXT],
                      [Approver.NOT_NAMED, Approver.CHANCELLOR], AIR,
                      "Line 573: coach is sold on the route but sold out on the date; whether business is then "
                      "'the only service offered' is unclear.", phrase=PHRASE_ONLY_SERVICE)
    return answer(Decision.BOOK, business_offers, [ReasonCode.ONLY_CLASS_OFFERED], LISTED, AIR,
                  "Line 573: no coach service is offered on the route, so business may be used.")


def business(trip, offers, bookable, federal, hidden):
    """A request to fly business: lines 567-592, with the extramural and bargaining-agreement precedence of
    lines 120-124."""
    economy = [offer for offer in bookable if offer.cabin == Cabin.ECONOMY]
    premium = [offer for offer in bookable if offer.cabin == Cabin.BUSINESS]
    if not economy:
        return only_service(offers, bookable)
    if not premium:
        raise ValueError("a business request with no business offer is not modelled")
    sponsor = hidden.get("sponsor", "none")
    if sponsor == "more_restrictive":  # lines 120-121: the sponsor's stricter terms govern
        return coach(economy, federal, [ReasonCode.SPONSOR_TERMS_MORE_RESTRICTIVE, ReasonCode.UPGRADE_NOT_ELIGIBLE,
                                        ReasonCode.LOWEST_FARE],
                     [*AIR, Clause.INTRODUCTION], CLAIM,
                     "Lines 120-121: the award's terms are more restrictive than G-28, so they govern: economy.")
    granted, pending, refused, notes = chancellor_authority(trip)
    bases = []
    if hidden.get("union_business_over_minutes"):  # lines 122-124: the bargaining agreement governs
        limit = hidden["union_business_over_minutes"]
        long = [offer for offer in premium if all(segment.scheduled_minutes > limit for segment in offer.segments)]
        if len(long) != len(premium):
            raise ValueError("a business offer on the other side of the union contract's limit is not modelled")
        bases.append((ReasonCode.COLLECTIVE_BARGAINING_TERMS, CLAIM, [*AIR, Clause.INTRODUCTION],
                      "Lines 122-124: the union contract's terms govern where they differ from G-28."))
    if trip.medical_note_on_file:  # lines 586-587
        bases.append((ReasonCode.MEDICAL_NEED, LISTED, AIR, "Lines 586-587: a documented medical need."))
    low_economy, low_premium = cheapest(economy)[0], cheapest(premium)[0]
    if low_premium.fare_cents < low_economy.fare_cents:  # lines 574-575, "more expensive" read on the fares
        if flights_of(low_premium) != flights_of(low_economy):
            raise ValueError("a cheaper business seat on other flights is not modelled")
        bases.append((ReasonCode.COACH_MORE_EXPENSIVE, (*CLAIM, Approver.NOT_NAMED), LOWEST,
                      "Lines 574-575: coach would be more expensive than business on the same flights."))
    night = overnight_no_rest(trip, low_premium)
    if night is True:
        bases.append((ReasonCode.OVERNIGHT_TRAVEL_NO_REST, LISTED, AIR,
                      "Lines 578-585: overnight travel with no chance of normal rest before the documented start."))
    if granted:
        clauses = [*LOWEST, Clause.RESPONSIBILITIES] + ([Clause.DEFINITIONS] if Approver.CHANCELLOR_DESIGNEE in granted
                                                         else [])
        bases.append((ReasonCode.CHANCELLOR_WRITTEN_AUTHORIZATION, granted, clauses, notes))
    if len(bases) > 1:
        raise ValueError("more than one basis for business is not modelled")
    if federal and (bases or pending or night is None):
        raise ValueError("business on federal funds is not modelled")
    if bases:
        reason, approvers, clauses, why = bases[0]
        reasons = [reason, ReasonCode.LOWEST_FARE] if reason == ReasonCode.COACH_MORE_EXPENSIVE else [reason]
        if reason == ReasonCode.COACH_MORE_EXPENSIVE:
            reasons.append(ReasonCode.COST_SAVINGS)
        return answer(Decision.BOOK, cheapest(premium), reasons, approvers, clauses, why)
    if night is None:
        return answer(Decision.FLAG_FOR_APPROVAL, cheapest(premium), [ReasonCode.UNCLEAR_POLICY_TEXT],
                      [Approver.NOT_NAMED, Approver.CHANCELLOR], AIR,
                      "Lines 578-579: a flight leaving in the evening and landing after midnight before an early "
                      "start is neither clearly overnight travel without rest nor clearly not.",
                      phrase=PHRASE_OVERNIGHT)
    if pending:
        return answer(Decision.FLAG_FOR_APPROVAL, cheapest(premium), [ReasonCode.APPROVAL_REQUIRED], pending,
                      [*LOWEST, Clause.RESPONSIBILITIES, Clause.DEFINITIONS],
                      f"No listed circumstance; {notes}. The traveller asked to hold the seat until it is settled.")
    if refused:
        return coach(economy, federal, [*refused, ReasonCode.NO_LISTED_CIRCUMSTANCE, ReasonCode.UPGRADE_NOT_ELIGIBLE],
                     [Clause.CLAIM_APPROVAL, *AIR], CLAIM, f"No listed circumstance; {notes}; so coach.")
    extra = [ReasonCode.SPONSOR_TERMS_DO_NOT_GOVERN] if sponsor == "less_restrictive" else []
    clauses = [*AIR, Clause.INTRODUCTION] if sponsor == "less_restrictive" else LOWEST
    if federal:
        return coach(economy, federal, [ReasonCode.NO_LISTED_CIRCUMSTANCE, ReasonCode.UPGRADE_NOT_ELIGIBLE, *extra],
                     clauses, CLAIM, "Lines 567-592: no listed circumstance and no written authorization; lines "
                     "120-121: the award's looser terms do not govern.")
    return coach(economy, federal, [*COACH_REASONS, *extra], clauses, CLAIM,
                 "Lines 567-592: no listed circumstance and no written authorization, however long the flight.")


def economy_plus(bookable, hidden):
    """Lines 593-597: higher-cost airfare "within the economy class can be included in the local policy"."""
    economy = [offer for offer in bookable if offer.cabin == Cabin.ECONOMY]
    standard = cheapest(economy)
    if len(standard) != 1:
        raise ValueError("an Economy Plus request needs one cheapest standard fare")
    dearer = [offer for offer in economy
              if flights_of(offer) == flights_of(standard[0]) and offer.fare_cents > standard[0].fare_cents]
    if len(dearer) != 1:
        raise ValueError("an Economy Plus request needs exactly one dearer economy fare on the same flights")
    policy = hidden["local_policy"]
    if policy == "reimburses":
        return answer(Decision.BOOK, dearer, [ReasonCode.CAMPUS_LOCAL_POLICY], CLAIM, AIR,
                      "Lines 593-597: the campus's local policy on file reimburses Economy Plus.")
    if policy == "not_on_file":
        return answer(Decision.FLAG_FOR_APPROVAL, dearer, [ReasonCode.UNCLEAR_POLICY_TEXT],
                      [Approver.NOT_NAMED, Approver.CHANCELLOR], AIR,
                      "Lines 567-569 against 593-597: whether Economy Plus is plain coach or needs a local policy "
                      "that is not on file is unclear.", phrase=PHRASE_LOCAL_POLICY)
    raise ValueError(f"local policy {policy!r} is not modelled")


def unused_ticket(trip, bookable, wish):
    """Line 404: "A nonrefundable ticket associated with a canceled trip must be used for the employee's next
    business trip"."""
    tickets = [ticket for ticket in trip.unused_tickets if not ticket.refundable]
    if len(tickets) != 1 or wish not in ("coach", "cheapest"):
        raise ValueError("one nonrefundable ticket on a coach request is the only case modelled")
    carrier = [offer for offer in bookable if offer.cabin == Cabin.ECONOMY and offer.carrier == tickets[0].airline]
    if not carrier:
        raise ValueError("no offer on the ticket's airline is not modelled")
    return answer(Decision.BOOK, cheapest(carrier), [ReasonCode.UNUSED_TICKET_MUST_BE_USED], CLAIM,
                  [Clause.CANCELED_TRIPS, Clause.CASH_ADVANCES],
                  "Line 404: the unused nonrefundable ticket from the canceled trip must be used on this trip, so "
                  "the airline that holds it, even at a higher fare.")


def candidate(trip, offers, wish):
    """A prospective employee: lines 1462-1464 (approved in advance by the inviting department) and lines
    1482-1484 ("one round-trip coach airfare ... for each round of interviews")."""
    approved = [entry for entry in paper(trip, PaperKind.TRIP_APPROVAL)
                if entry.signer_role == SignerRole.INVITING_DEPARTMENT and entry.in_writing
                and day_number(entry.signed_on) <= day_number(trip.booking_date)]
    if not approved or trip.interview_round < 1 or wish != "coach":
        raise ValueError("only an approved candidate asking for coach is modelled")
    clauses = [Clause.PROSPECTIVE_EMPLOYEES, Clause.NON_UNIVERSITY_TRAVELERS]
    if trip.tickets_bought_this_round >= 1:
        return refuse([ReasonCode.INTERVIEW_ROUND_TRIP_LIMIT, ReasonCode.NO_COMPLIANT_OFFER],
                      [Approver.NONE, Approver.INVITING_DEPARTMENT], clauses,
                      "Lines 1482-1484: one round-trip coach airfare per round, and this round's is already bought.")
    economy = [offer for offer in offers if offer.seats_available and offer.cabin == Cabin.ECONOMY
               and offer.return_segments]
    if not economy:
        raise ValueError("a candidate's trip needs round-trip economy offers")
    return answer(Decision.BOOK, cheapest(economy), [ReasonCode.LOWEST_FARE],
                  [Approver.INVITING_DEPARTMENT, *CLAIM], clauses,
                  "Lines 1462-1464 and 1482-1484: approved in advance; one round-trip coach fare for this round.")

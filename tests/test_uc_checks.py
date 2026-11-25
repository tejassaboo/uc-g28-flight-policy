"""UC G-28 checks beyond the template's suite: no flight-length rule (the duration hook is empty by design),
the Fly America travel-time comparison on both sides of its inclusive six-hour boundary, the overnight-travel
reading on its three sides, dates on or after the effective date, federal scenarios with Open Skies off and
no background offers, business and coach on the same flights wherever both are sold (so "time-consuming"
never decides a case), unclear phrases quoted verbatim, and requests that share no 4-word phrase with any
must_keep clause."""

import pytest
from test_lint import grams

from contract import Cabin, Decision
from helpers import POLICY_LINES, normalized, range_text, scenarios
from plugin import rules
from plugin.answer import answer_key
from plugin.scenarios import trip_record
from plugin.world import AIRLINES, AIRPORTS, build_segments, days_between, make_offer

ALL = scenarios()
BY_ID = {data["id"]: data for data in ALL}
EFFECTIVE = "2026-07-01"  # line 20: "Effective Date: 7/1/2026"


def offer(carrier, path, depart, minutes, layovers, fare):
    segments, layovers = build_segments(carrier, path, "2027-01-10", depart, minutes, layovers, "uc-check")
    return make_offer(f"T-{carrier}-{fare}", carrier, Cabin.ECONOMY, fare, True, False,
                      (segments, layovers, [False] * len(layovers)), None)


def test_no_flight_length_rule():
    assert rules.DURATION_RULES == ()
    with pytest.raises(ValueError):
        rules.over("anything", offer("UA", ["SFO", "PVG"], "11:00", [740], [], 100))


@pytest.mark.parametrize(("layover", "foreign_allowed"), [(249, False), (250, True), (100, False), (400, True)])
def test_fly_america_extension_is_inclusive_at_six_hours(layover, foreign_allowed):
    foreign = offer("MU", ["SAN", "PVG"], "11:00", [760], [], 121000)
    us = offer("UA", ["SAN", "SFO", "PVG"], "11:00", [100, 770], [layover], 168000)
    allowed, _, _ = rules.fly_america([foreign, us])
    assert (foreign in allowed) is foreign_allowed
    assert us in allowed


def test_fly_america_us_nonstop_must_be_used():
    foreign = offer("CA", ["SFO", "PEK"], "13:20", [740], [], 97000)
    us = offer("UA", ["SFO", "PEK"], "10:50", [735], [], 136000)
    allowed, _, _ = rules.fly_america([foreign, us])
    assert allowed == [us]


def test_fly_america_shapes_not_modelled_raise():
    foreign = offer("MU", ["SAN", "PVG"], "11:00", [760], [], 121000)
    later = offer("UA", ["SAN", "SFO", "PVG"], "12:00", [100, 770], [60], 168000)
    with pytest.raises(ValueError):
        rules.fly_america([foreign, later])  # different departure times
    with pytest.raises(ValueError):
        rules.fly_america([foreign])  # one kind of carrier only


def test_carrier_and_airport_tables_match_the_world():
    names = {row[1] for row in AIRLINES}
    assert set(rules.US_CARRIERS) <= names
    us_airports = {row[0] for row in AIRPORTS if row[3] == "US"}
    assert set(rules.US_AIRPORTS) == us_airports


def test_overnight_reading_has_all_three_sides():
    verdicts = {}
    for name in ("sorrel-dune", "linden-wharf", "wren-cairn"):
        data = BY_ID[name]
        trip, offers, _, _ = answer_key(data)
        business = [item for item in offers if item.cabin == Cabin.BUSINESS]
        verdicts[name] = rules.overnight_no_rest(trip, business[0])
    assert verdicts == {"sorrel-dune": True, "linden-wharf": False, "wren-cairn": None}


def test_every_date_is_on_or_after_the_effective_date():
    for data in ALL:
        trip = data["trip"]
        dates = [trip["booking_date"], trip["depart_date"]] + ([trip["return_date"]] if trip["return_date"] else [])
        for search in data["world"]["searches"]:
            dates += [search["date"]] + ([search["return_date"]] if search["return_date"] else [])
        assert all(days_between(EFFECTIVE, date) >= 0 for date in dates), data["id"]
        assert days_between(trip["booking_date"], trip["depart_date"]) >= 0, data["id"]


def test_federal_scenarios_have_open_skies_off_and_no_background():
    federal = [data for data in ALL if data["answer_key_inputs"]["federal"]]
    assert len(federal) >= 4
    for data in federal:
        assert data["trip"]["open_skies_covers_route"] is False, data["id"]
        if data["trip"]["traveller_kind"] == "EMPLOYEE":
            assert all(search.get("background") == 0 for search in data["world"]["searches"]), data["id"]


def test_business_and_coach_share_flights_wherever_both_are_sold():
    for data in ALL:
        _, offers, slots, _ = answer_key(data)
        pinned = [item for item in offers if not slots[item.offer_id].startswith("search-")]
        economy = {rules.flights_of(item) for item in pinned if item.cabin == Cabin.ECONOMY}
        for item in pinned:
            if item.cabin == Cabin.BUSINESS and economy:
                assert rules.flights_of(item) in economy, (data["id"], slots[item.offer_id])


def test_each_unclear_phrase_is_quoted_from_the_policy():
    policy = normalized(" ".join(POLICY_LINES))
    phrases = [data["expected"]["unclear_phrase"] for data in ALL if data["expected"]["unclear_phrase"]]
    assert len(phrases) == 3
    for phrase in phrases:
        assert phrase in policy, phrase


def test_requests_share_no_four_word_phrase_with_any_must_keep_clause():
    clause_grams = set().union(*(grams(range_text(entry["lines"])) for data in ALL for entry in data["must_keep"]))
    for data in ALL:
        shared = grams(data["request"]) & clause_grams
        assert not shared, (data["id"], sorted(shared))


def test_refusals_and_holds_follow_the_trip_record():
    for data in ALL:
        trip = trip_record(data)
        decision = data["expected"]["decision"]
        if decision == Decision.REFUSE.value:
            assert data["expected"]["offer_slots"] == [], data["id"]
        if trip.traveller_kind.value == "DEPENDENT":
            assert decision == Decision.REFUSE.value

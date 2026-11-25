"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-uc-g28-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    NO_LISTED_CIRCUMSTANCE = "NO_LISTED_CIRCUMSTANCE"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    APPROVER_NOT_AUTHORIZED = "APPROVER_NOT_AUTHORIZED"
    SELF_APPROVAL = "SELF_APPROVAL"
    ONLY_CLASS_OFFERED = "ONLY_CLASS_OFFERED"
    COACH_MORE_EXPENSIVE = "COACH_MORE_EXPENSIVE"
    OVERNIGHT_TRAVEL_NO_REST = "OVERNIGHT_TRAVEL_NO_REST"
    SPONSOR_TERMS_MORE_RESTRICTIVE = "SPONSOR_TERMS_MORE_RESTRICTIVE"
    SPONSOR_TERMS_DO_NOT_GOVERN = "SPONSOR_TERMS_DO_NOT_GOVERN"
    COLLECTIVE_BARGAINING_TERMS = "COLLECTIVE_BARGAINING_TERMS"
    CAMPUS_LOCAL_POLICY = "CAMPUS_LOCAL_POLICY"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    FLY_AMERICA_EXCEPTION = "FLY_AMERICA_EXCEPTION"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CODE_SHARE_US_CARRIER = "CODE_SHARE_US_CARRIER"
    UNUSED_TICKET_MUST_BE_USED = "UNUSED_TICKET_MUST_BE_USED"
    INTERVIEW_ROUND_TRIP_LIMIT = "INTERVIEW_ROUND_TRIP_LIMIT"
    DEPENDENT_TRAVEL_FEDERAL_FUNDS = "DEPENDENT_TRAVEL_FEDERAL_FUNDS"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    TRAVEL_PACKAGE_NOT_ITEMIZED = "TRAVEL_PACKAGE_NOT_ITEMIZED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: University of California, Business and Finance Bulletin G-28, Travel Regulations
# (issued 1/14/2026, effective 7/1/2026).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    AMBER_QUAY = "amber-quay"
    ASPEN_RILL = "aspen-rill"
    BRIAR_KESTREL = "briar-kestrel"
    CINDER_VALE = "cinder-vale"
    COBALT_SEDGE = "cobalt-sedge"
    COBBLE_WREN = "cobble-wren"
    DRIFT_SAFFRON = "drift-saffron"
    DUSK_MEADOW = "dusk-meadow"
    EMBER_COAST = "ember-coast"
    FENNEL_BROOK = "fennel-brook"
    GARNET_LOFT = "garnet-loft"
    HERON_GORSE = "heron-gorse"
    LICHEN_SOUND = "lichen-sound"
    LINDEN_WHARF = "linden-wharf"
    NECTAR_ISLE = "nectar-isle"
    NIMBUS_REED = "nimbus-reed"
    OCHRE_BRACKEN = "ochre-bracken"
    OPAL_THICKET = "opal-thicket"
    ORCHID_RIDGE = "orchid-ridge"
    PEAT_LANTERN = "peat-lantern"
    PEWTER_MOTH = "pewter-moth"
    QUILL_MARSH = "quill-marsh"
    QUINCE_HARBOR = "quince-harbor"
    RUSSET_PLUME = "russet-plume"
    SAFFRON_GLEN = "saffron-glen"
    SLATE_FERN = "slate-fern"
    SORREL_DUNE = "sorrel-dune"
    TALLOW_BROOK = "tallow-brook"
    TANSY_MERE = "tansy-mere"
    TIDAL_ORCHID = "tidal-orchid"
    WILLOW_CRANE = "willow-crane"
    WREN_CAIRN = "wren-cairn"


class Approver(Enum):
    """Roles that may sign off. NONE: nobody's sign-off is involved. NOT_NAMED: one is needed, but the
    handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    CHANCELLOR = "CHANCELLOR"
    CHANCELLOR_DESIGNEE = "CHANCELLOR_DESIGNEE"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    CAMPUS_CONTROLLER = "CAMPUS_CONTROLLER"
    DESIGNATED_VICE_CHANCELLOR = "DESIGNATED_VICE_CHANCELLOR"
    INVITING_DEPARTMENT = "INVITING_DEPARTMENT"
    SENIOR_UNIVERSITY_OFFICER = "SENIOR_UNIVERSITY_OFFICER"
    PRESIDENT = "PRESIDENT"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    TRAVEL_MANAGEMENT_OFFICE = "TRAVEL_MANAGEMENT_OFFICE"
    GRANT_SPONSOR = "GRANT_SPONSOR"
    IMMEDIATE_SUPERVISOR = "IMMEDIATE_SUPERVISOR"


class Clause(Enum):
    """The handbook's sections, by heading."""

    POLICY_SUMMARY = "POLICY_SUMMARY"
    SCOPE = "SCOPE"
    DEFINITIONS = "DEFINITIONS"
    INTRODUCTION = "INTRODUCTION"
    OVERVIEW = "OVERVIEW"
    REIMBURSEMENT_STANDARDS = "REIMBURSEMENT_STANDARDS"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    CLAIM_APPROVAL = "CLAIM_APPROVAL"
    CASH_ADVANCES = "CASH_ADVANCES"
    CANCELED_TRIPS = "CANCELED_TRIPS"
    CANCELLATION_OF_RESERVATIONS = "CANCELLATION_OF_RESERVATIONS"
    TRANSPORTATION_EXPENSES = "TRANSPORTATION_EXPENSES"
    TRANSPORTATION_TICKETS = "TRANSPORTATION_TICKETS"
    SURFACE_TRANSPORTATION = "SURFACE_TRANSPORTATION"
    INDIRECT_ITINERARIES = "INDIRECT_ITINERARIES"
    EXTENDED_TRAVEL = "EXTENDED_TRAVEL"
    AIR_TRAVEL = "AIR_TRAVEL"
    COMMERCIAL_AIRLINES = "COMMERCIAL_AIRLINES"
    PRIVATE_AIRCRAFT = "PRIVATE_AIRCRAFT"
    CHARTERED_AIRCRAFT = "CHARTERED_AIRCRAFT"
    RAIL_OR_BUS = "RAIL_OR_BUS"
    SUSTAINABLE_TRAVEL = "SUSTAINABLE_TRAVEL"
    NON_UNIVERSITY_TRAVELERS = "NON_UNIVERSITY_TRAVELERS"
    PROSPECTIVE_EMPLOYEES = "PROSPECTIVE_EMPLOYEES"
    SPOUSE_AND_DEPENDENT_TRAVEL = "SPOUSE_AND_DEPENDENT_TRAVEL"
    FREQUENTLY_ASKED_QUESTIONS = "FREQUENTLY_ASKED_QUESTIONS"


class TravellerKind(Enum):
    EMPLOYEE = "EMPLOYEE"
    PROSPECTIVE_EMPLOYEE = "PROSPECTIVE_EMPLOYEE"
    STUDENT = "STUDENT"
    INDEPENDENT_CONTRACTOR = "INDEPENDENT_CONTRACTOR"
    SPOUSE_OR_DOMESTIC_PARTNER = "SPOUSE_OR_DOMESTIC_PARTNER"
    DEPENDENT = "DEPENDENT"


class SignerRole(Enum):
    CHANCELLOR = "CHANCELLOR"
    VICE_CHANCELLOR = "VICE_CHANCELLOR"
    DEAN = "DEAN"
    DEPARTMENT_CHAIR = "DEPARTMENT_CHAIR"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    INVITING_DEPARTMENT = "INVITING_DEPARTMENT"
    CAMPUS_CONTROLLER = "CAMPUS_CONTROLLER"


class PaperKind(Enum):
    """CABIN_ABOVE_COACH: a seat in a higher cabin for this trip. DELEGATION: the signer hands some of their
    own authority to the named delegate. TRIP_APPROVAL: the trip itself is approved. COMPANION_TRAVEL: a
    companion's travel is approved."""

    CABIN_ABOVE_COACH = "CABIN_ABOVE_COACH"
    DELEGATION = "DELEGATION"
    TRIP_APPROVAL = "TRIP_APPROVAL"
    COMPANION_TRAVEL = "COMPANION_TRAVEL"


@dataclass
class Authorization(Output):
    kind: Annotated[PaperKind, "What it authorizes"]
    signer_name: Annotated[str, "Who gave it, by name"]
    signer_role: Annotated[SignerRole, "The signer's role at the University"]
    delegate_name: Annotated[str, "For a delegation, who receives the authority, by name; empty otherwise"]
    in_writing: Annotated[bool, "True for a signed document; false when it was only said, e.g. by phone"]
    signed_on: Annotated[str, "When it was given, YYYY-MM-DD"]
    covers: Annotated[str, "What it says, in plain words"]


@dataclass
class UnusedTicket(Output):
    airline: Annotated[str, "The airline that issued it, by name, as search results name airlines"]
    value_cents: Annotated[int, "What it is worth toward a new fare on that airline, in cents"]
    refundable: Annotated[bool, "Whether the airline would pay it back in money"]
    bought_for: Annotated[str, "The trip it was bought for, and what happened to that trip"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "The person flying"]
    traveller_title: Annotated[str, "Their job title, or what they are to the University"]
    traveller_kind: Annotated[TravellerKind, "Their kind of relationship to the University"]
    campus: Annotated[str, "The University location the trip is for"]
    accompanying: Annotated[str, "For a family member, the University traveller they go with; empty otherwise"]
    companions: Annotated[list[str], "Others booked on the same flights, by title; empty when alone"]
    origin: Annotated[Airport, "Where the trip's flight leaves from"]
    destination: Annotated[Airport, "Where the trip's flight goes"]
    depart_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    return_date: Annotated[str, "The day to come back, YYYY-MM-DD; empty when no return is booked here"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    fund_source: Annotated[str, "The account or award that pays for the airfare"]
    sponsor_travel_terms: Annotated[str, "What the paying award's own agreement says about airfare; empty when silent"]
    union_contract_terms: Annotated[str, "What the traveller's union contract says about flights; empty when none applies"]
    open_skies_covers_route: Annotated[bool, "Whether the State Department's open-skies list covers every foreign country on this route"]
    authorizations: Annotated[list[Authorization], "Authorizations and delegations on file that bear on this trip"]
    meeting_starts_local: Annotated[str, "When the traveller's first engagement starts, YYYY-MM-DD HH:MM local at the destination; empty when none"]
    meeting_timing_documented: Annotated[bool, "Whether the campus file holds the agenda and a note that no other start date or time was open"]
    medical_note_on_file: Annotated[str, "A doctor's or accommodation office's note about how the traveller can fly; empty when none"]
    unused_tickets: Annotated[list[UnusedTicket], "Airline tickets the traveller holds that were never flown"]
    campus_local_policy: Annotated[str, "What is on file of the campus's own travel rules for seats and extras; empty when nothing"]
    interview_round: Annotated[int, "For a job candidate, which round of interviews this trip is for; zero otherwise"]
    interview_is_final: Annotated[bool, "For a job candidate, whether this is the last round of interviews"]
    tickets_bought_this_round: Annotated[int, "For a job candidate, round trips the University has already bought for this round"]
    other_notes: Annotated[list[str], "Other notes on file for this trip"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the company buys no ticket at all for this trip. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on or still waits for; NONE when it needs nobody's; "
        "NOT_NAMED when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}

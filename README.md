# UC G-28 Travel Regulations Flight Policy

**No affiliation with the University of California.** The handbook is the University of California's public
*Business and Finance Bulletin G-28, Travel Regulations* (issued 1/14/2026, effective 7/1/2026), bundled
verbatim for research. As a university policy it may be published once it has passed validation (MASTER_PLAN
section 4); do not publish it before then. The published plugin id `uc-g28-expense-audit` is a different
plugin and is never reused here.

A `nanoagent.plugin/v0001` plugin. An agent handles one flight booking request under the real regulations: it
reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the regulations' answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 20,315 words, 2,237 lines, sha256 `392efd49...c65519b5b5`, equal
to `pilot_work/originals/uc-g28-expense-audit/frozen/SHA256SUMS`; raw `bfb-g-28.pdf` sha256 `76e41572...9613`)
is never paraphrased, and the task text restates no rule. Under stock NanoAgent the agent does not see it: the
plugin then runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork
(github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt: `harness.policy: full`
adds all of it, and the selection methods add parts of it. These plugins are meant to run with
`query: instructions+input`, so a selector sees the traveller's request.

**Size.** At 1.33 tokens a word (the long-handbook bench's calibration) the regulations alone are about 27,000
tokens. Under `full` the first call carries about 31,800 input tokens (regulations; task instructions about
220; tool and submit schemas, inputs and outputs, about 4,500 at 4 characters a token; the request), and the
third call up to about 33,900 as the trip record (up to about 430 tokens) and the offers (360 to 1,630) are
added. A run makes 3 calls (`get_trip`, `search_flights`, `submit`): about 96,800 input tokens per run (96,400
to 97,800; output tokens not counted). Each single call fits under the hosted cap of 65,536 tokens, but a run's
total crosses it during the third call in every one of the 32 cases, so `full` cannot finish hosted: run it
locally with a raised cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 32 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the route and date (with `return_date` for a job
  candidate's round trip), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing; the
  chosen offer's own cabin otherwise), `reason_code`, `approver` and `clause`, each from a closed list. The
  reason list is the template's shared list (codes for rules G-28 lacks) plus G-28 codes such as
  `NO_LISTED_CIRCUMSTANCE`, `CHANCELLOR_WRITTEN_AUTHORIZATION`, `OVERNIGHT_TRAVEL_NO_REST`,
  `FLY_AMERICA_US_CARRIER_REQUIRED` and decoys (`OPEN_SKIES_AGREEMENT`, `CODE_SHARE_US_CARRIER`, ...). Fares are
  in cents of US dollars (`currency: USD`).
- **Success:** every field is one the answer key accepts. Score = fields right / 6.
- **Hidden facts** (`answer_key_inputs`, never shown by a tool): what the request asks for (coach, the
  cheapest seat, business, Economy Plus), whether the airfare is paid from federal funds (the agent reads the
  fund source, e.g. "National Science Foundation award", and works it out), and the reading of free-text
  record facts (the sponsor's terms, the union contract's limit, the local policy, the LBNL scope).

| Scenario | Category | Expected decision (offer, cabin) | Reason | Approver | Clause (frozen lines) |
|---|---|---|---|---|---|
| `cobalt-sedge` | easy | BOOK (sq-economy; ECONOMY) | LOWEST_FARE or NO_LISTED_CIRCUMSTANCE or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (567-569, 570-572, 588-592) |
| `drift-saffron` | easy | BOOK (early-business; BUSINESS) | ONLY_CLASS_OFFERED | DEPARTMENT_HEAD or NONE or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (490-492, 567-569, 570-572, 573) |
| `quince-harbor` | easy | BOOK (dl-economy; ECONOMY) | LOWEST_FARE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 567-569) |
| `russet-plume` | easy | BOOK (dl-business; BUSINESS) | MEDICAL_NEED | DEPARTMENT_HEAD or NONE or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (570-572, 586-587) |
| `tidal-orchid` | easy | BOOK (ba-business; BUSINESS) | CHANCELLOR_WRITTEN_AUTHORIZATION | CHANCELLOR | AIR_TRAVEL or COMMERCIAL_AIRLINES or RESPONSIBILITIES or TRANSPORTATION_EXPENSES (490-492, 588-592) |
| `willow-crane` | easy | BOOK (aa-economy; ECONOMY) | LOWEST_FARE | DEPARTMENT_HEAD or INVITING_DEPARTMENT or NONE | NON_UNIVERSITY_TRAVELERS or PROSPECTIVE_EMPLOYEES (1462-1464, 1482-1484) |
| `amber-quay` | boundary_twin | BOOK (ua-economy; ECONOMY) | FLY_AMERICA_US_CARRIER_REQUIRED or NATIONAL_CARRIER_REQUIRED | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES (598-601, 608-616) |
| `fennel-brook` | boundary_twin | BOOK (aa-economy; ECONOMY) | LOWEST_FARE or NO_LISTED_CIRCUMSTANCE or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (567-569, 570-572, 574-577) |
| `garnet-loft` | boundary_twin | BOOK (as-economy; ECONOMY) | LOWEST_FARE | DEPARTMENT_HEAD or INVITING_DEPARTMENT or NONE | NON_UNIVERSITY_TRAVELERS or PROSPECTIVE_EMPLOYEES (1462-1464, 1482-1484) |
| `heron-gorse` | boundary_twin | BOOK (mu-economy; ECONOMY) | FLY_AMERICA_EXCEPTION or LOWEST_FARE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 598-601, 608-616) |
| `linden-wharf` | boundary_twin | BOOK (ua-economy; ECONOMY) | LOWEST_FARE or NO_LISTED_CIRCUMSTANCE or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (567-569, 570-572, 578-579) |
| `pewter-moth` | boundary_twin | BOOK (aa-business; BUSINESS) | COACH_MORE_EXPENSIVE or COST_SAVINGS or LOWEST_FARE | DEPARTMENT_HEAD or NONE or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 570-572, 574-577) |
| `slate-fern` | boundary_twin | REFUSE (none; NONE) | INTERVIEW_ROUND_TRIP_LIMIT or NO_COMPLIANT_OFFER | INVITING_DEPARTMENT or NONE | PROSPECTIVE_EMPLOYEES (1482-1484) |
| `sorrel-dune` | boundary_twin | BOOK (ua-business; BUSINESS) | OVERNIGHT_TRAVEL_NO_REST | DEPARTMENT_HEAD or NONE or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (570-572, 578-579, 584-585) |
| `cinder-vale` | multi_rule | BOOK (ua-economy; ECONOMY) | FLY_AMERICA_US_CARRIER_REQUIRED or NATIONAL_CARRIER_REQUIRED or NO_LISTED_CIRCUMSTANCE or SPONSOR_TERMS_DO_NOT_GOVERN or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or INTRODUCTION (120-121, 567-569, 570-572, 598-601, 604-607) |
| `ember-coast` | multi_rule | BOOK (jl-economy; ECONOMY) | APPROVER_NOT_AUTHORIZED or NO_LISTED_CIRCUMSTANCE or SELF_APPROVAL or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or CLAIM_APPROVAL or COMMERCIAL_AIRLINES (321-322, 567-569, 588-592) |
| `lichen-sound` | multi_rule | BOOK (af-economy; ECONOMY) | LOWEST_FARE or SPONSOR_TERMS_MORE_RESTRICTIVE or UPGRADE_NOT_ELIGIBLE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or INTRODUCTION (120-121, 567-569, 588-592) |
| `orchid-ridge` | multi_rule | BOOK (jl-business; BUSINESS) | CHANCELLOR_WRITTEN_AUTHORIZATION | CHANCELLOR or CHANCELLOR_DESIGNEE | AIR_TRAVEL or COMMERCIAL_AIRLINES or DEFINITIONS or RESPONSIBILITIES or TRANSPORTATION_EXPENSES (44, 259-272, 588-592) |
| `peat-lantern` | multi_rule | BOOK (mu-economy; ECONOMY) | LOWEST_FARE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 567-569, 598-601) |
| `briar-kestrel` | hidden_clause | BOOK (ke-business; BUSINESS) | COLLECTIVE_BARGAINING_TERMS | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or INTRODUCTION (122-124, 567-569) |
| `nectar-isle` | hidden_clause | BOOK (ua-economy; ECONOMY) | FLY_AMERICA_US_CARRIER_REQUIRED or NATIONAL_CARRIER_REQUIRED | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES (598-601, 604-607) |
| `ochre-bracken` | hidden_clause | BOOK (dl-economy; ECONOMY) | UNUSED_TICKET_MUST_BE_USED | DEPARTMENT_HEAD or NONE | CANCELED_TRIPS or CASH_ADVANCES (404-405) |
| `cobble-wren` | distractor | BOOK (as-economy; ECONOMY) | LOWEST_FARE | CAMPUS_CONTROLLER or DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 567-569) |
| `quill-marsh` | distractor | BOOK (ua-extra; ECONOMY) | CAMPUS_LOCAL_POLICY | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES (593-597) |
| `tansy-mere` | distractor | BOOK (aa-economy; ECONOMY) | LOWEST_FARE | DEPARTMENT_HEAD or NONE | AIR_TRAVEL or COMMERCIAL_AIRLINES or TRANSPORTATION_EXPENSES (490-492, 567-569) |
| `dusk-meadow` | refusal | REFUSE (none; NONE) | PERSONAL_TRAVEL_NOT_COVERED | NONE | REIMBURSEMENT_STANDARDS (153-156) |
| `saffron-glen` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or DEPENDENT_TRAVEL_FEDERAL_FUNDS | DEPARTMENT_HEAD or NONE | FREQUENTLY_ASKED_QUESTIONS or SPOUSE_AND_DEPENDENT_TRAVEL (1566-1571, 1869-1870) |
| `tallow-brook` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE | NONE | INTRODUCTION or POLICY_SUMMARY or SCOPE (104-107) |
| `aspen-rill` | flag | FLAG_FOR_APPROVAL (ua-business; BUSINESS) | UNCLEAR_POLICY_TEXT | CHANCELLOR or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (567-569, 570-572, 573) |
| `nimbus-reed` | flag | FLAG_FOR_APPROVAL (ke-business; BUSINESS) | APPROVAL_REQUIRED | CHANCELLOR or CHANCELLOR_DESIGNEE | AIR_TRAVEL or COMMERCIAL_AIRLINES or DEFINITIONS or RESPONSIBILITIES or TRANSPORTATION_EXPENSES (44, 259-272, 588-592) |
| `opal-thicket` | flag | FLAG_FOR_APPROVAL (ua-extra; ECONOMY) | UNCLEAR_POLICY_TEXT | CHANCELLOR or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (567-569, 593-597) |
| `wren-cairn` | flag | FLAG_FOR_APPROVAL (ua-business; BUSINESS) | UNCLEAR_POLICY_TEXT | CHANCELLOR or NOT_NAMED | AIR_TRAVEL or COMMERCIAL_AIRLINES (570-572, 578-579, 584-585) |

Mix (EDGE_CASES.md 5.2, 32 row): 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause, 3 distractor, 3
refusal, 4 flags (12.5%; the 15% cap is 4). Decisions: 24 BOOK (7 business, 17 economy), 4 REFUSE (one of them
a boundary twin), 4 FLAG_FOR_APPROVAL. Twin pairs: Fly America at 359 against 360 minutes ("at least 6 hours or
more", inclusive, line 614: `amber-quay`, `heron-gorse`); a documented red-eye landing the morning of the
engagement or the day before it (`sorrel-dune`, `linden-wharf`, across the January 31 month end); business 100
cents under or over coach on the same flight ("more expensive", line 574: `pewter-moth`, `fennel-brook`); a job
candidate's round trip with none or one already bought for the round ("one round-trip coach airfare ... for
each round", lines 1482-1484: `garnet-loft`, `slate-fern`). Unclear words are each one flag with clear twins on
both sides: "within the economy class can be included in the local policy" with the local policy not on file
(`opal-thicket`; twins `quill-marsh`, `quince-harbor`), "Business or first-class is the only service offered
between two points" with every coach seat sold out (`aspen-rill`; twins `drift-saffron`, `quince-harbor`) and
"overnight travel without an opportunity for normal rest" for a 16:55 departure landing at 01:30 before an
08:30 talk (`wren-cairn`; twins `sorrel-dune`, `linden-wharf`). `nimbus-reed` is an approval-required hold (a
Dean's authorization with no written delegation from the Chancellor, and the traveller asked to hold), never the
same as "no compliant offer". Approvers: on BOOK and REFUSE the approver is not what a case tests, so `NONE` and
`DEPARTMENT_HEAD` (who approves the claim and checks fund restrictions, lines 186-193) are accepted, plus
`NOT_NAMED` where a listed circumstance permits business ("may be authorized", by nobody named, line 570),
`CHANCELLOR` (and `CHANCELLOR_DESIGNEE` for a written delegate) where the Chancellor's authorization decides,
`INVITING_DEPARTMENT` for candidates and `CAMPUS_CONTROLLER` for the Chancellor's own trip (lines 194-199); on
a hold over unclear words `NOT_NAMED` or `CHANCELLOR` (who authorizes cases outside the list, lines 588-592).
The cabin is graded as the chosen offer's own cabin.

**Duration.** G-28 has no flight-length threshold for the cabin: coach applies to all travel "regardless of the
purpose or fund source" (lines 567-569), and a 1,000-minute nonstop is still coach (`cobalt-sedge`). So
`rules.DURATION_RULES` is empty and `rules.over` raises. Durations enter only the Fly America exceptions (lines
604-616), which compare a U.S. carrier's itinerary with a foreign one; `rules.fly_america` codes the nonstop
rule and the inclusive six-hour travel-time extension, comparing itineraries that leave at the same time (other
shapes raise). The other two exceptions (two or more aircraft changes outside the U.S., a 4-hour overseas
connection) cannot arise in the shared world, where every flight of a U.S. carrier touches a U.S. hub. Background
offers (two per search, priced far above every pinned fare) appear only in the nine plain coach cases
(`quince-harbor`, `willow-crane`, `garnet-loft`, `slate-fern`, `ochre-bracken`, `cobble-wren`, `dusk-meadow`,
`saffron-glen`, `tallow-brook`); they are off wherever a carrier, a cabin or a flight's timing could change the
answer.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, dates, purpose, fund source, sponsor and union terms, authorizations and delegations, engagement time, medical note, unused tickets, local policy, interview round, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date (one way, or round trip with `return_date`): the pinned scenario offers plus background offers where the case allows them | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-uc-g28-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus G-28's scenario ids, approvers, sections, reason codes and
  trip record (authorizations, unused tickets).
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (G-28's
  rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds G-28's settings;
  `tests/test_uc_checks.py` the G-28 checks (no flight-length rule, Fly America on both sides of six hours, the
  overnight reading's three sides, dates, Open Skies off on federal cases, business and coach on the same
  flights, request lint).
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/uc-g28-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`, on or after the
July 1, 2026 effective date). Degenerate agents: one that always holds the right offer for unclear words passes
the 3 unclear holds; one that always books the cheapest seat passes 12 of 32 (coach at the most economical fare
is G-28's default).

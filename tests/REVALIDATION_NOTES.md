# Re-validation of 2026-11-24 (evening): failures and fixes

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/revalidation_2026-11-24/`, `uc-g28-flight-policy@v2`, at
341d89e. 29 scored runs (`orchid-ridge`, `peat-lantern` and `russet-plume` got a provider 429 and were not
scored): 19/29 valid (65.5%), easy 4/5, mean field score 0.856, flags 0/4. **27/29 runs would exceed the hosted
65,536 cap before step 4**: about 31.9k prompt tokens per call, 125k per run. No answer here was wrong because of
the cap (every run submitted), but `full` cannot run hosted as is.

## Approver amendment (template SYNC_NOTES 4')

A BOOK or REFUSE that relies on a sign-off already on file now accepts that role and `NONE`. On employee
bookings `DEPARTMENT_HEAD` comes with `NONE` as the after-trip claim approver, as elsewhere in this plugin. The
changes are in `src/plugin/rules.py` and the byte-identical `verifier/rules.py`; `tests/build_scenarios.py`
regenerated the JSON.

- `willow-crane`, `garnet-loft` (the candidate's booking on the inviting department's approval): `INVITING_DEPARTMENT`,
  `DEPARTMENT_HEAD` or `NONE`. Before, `NONE` had been dropped.
- `tidal-orchid` (the Chancellor's written authorization): `CHANCELLOR`, `NONE` or `DEPARTMENT_HEAD`
- `orchid-ridge` (signed by the Chancellor's written delegate): `CHANCELLOR_DESIGNEE`, `CHANCELLOR`, `NONE` or
  `DEPARTMENT_HEAD`

Unchanged: the holds `nimbus-reed` (`CHANCELLOR` only; the Dean without a written delegation is the invalid
giver) and `aspen-rill`, `opal-thicket`, `wren-cairn` (`NOT_NAMED` or `CHANCELLOR`). Also unchanged: `ember-coast`
(the self-approving Dean's `CHANCELLOR_DESIGNEE` is still not accepted) and the 4(b) unused-sign-off sets.

`MAX_PASS_ALWAYS_LOWEST` goes from 10 to **12** (measured): `willow-crane` and `garnet-loft` again.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence | fix |
|---|---|---|---|---|---|
| willow-crane | **easy** | approver NONE; key INVITING_DEPARTMENT or DEPARTMENT_HEAD (rest right) | approver rule alone | The inviting department's written approval is on file (lines 1462-1464). | 4' (NONE accepted) |
| garnet-loft | boundary_twin | approver NONE; same key (rest right) | approver rule alone | as willow-crane | 4' (NONE accepted) |
| slate-fern | boundary_twin | REFUSE (right), PERSONAL_TRAVEL_NOT_COVERED, REIMBURSEMENT_STANDARDS; key INTERVIEW_ROUND_TRIP_LIMIT or NO_COMPLIANT_OFFER, PROSPECTIVE_EMPLOYEES or NON_UNIVERSITY_TRAVELERS | **scenario defect** | The request is "Between the two halves of my second-round visit I need to fly home to Seattle for a day", and the record says the candidate lives in Seattle. A visit home mid-round is personal travel that lines 154-156 ("Under no circumstances shall expenses for personal travel be charged to ... the University") refuse on their own. The model gave that ground and also cited the one-round-trip limit (lines 1482-1484) in its message. The decision and approver were right. The twin (`garnet-loft`) differs in the decision, so accepting the second ground keeps the twin test. | key also accepts PERSONAL_TRAVEL_NOT_COVERED and REIMBURSEMENT_STANDARDS; must_keep adds lines 153-156 |
| aspen-rill | flag | BOOK business, NO_ECONOMY_SEATS_URGENT; key FLAG / UNCLEAR_POLICY_TEXT | model slip | "'No economy seats' is not exactly 'only service offered' ... effectively business is the only class available". It saw both readings of line 573 and took one without flagging. NO_ECONOMY_SEATS_URGENT is another handbook's rule (it is in the shared reason list). | none |
| nimbus-reed | flag | BOOK business, LONG_FLIGHT_APPROVED, CHANCELLOR_DESIGNEE; key FLAG / APPROVAL_REQUIRED / CHANCELLOR | model slip | "The Dean is presumably delegated by the Chancellor". The record holds no delegation, and lines 259-265 allow a designee only "if any delegation of the Chancellor's authority is made in writing" (also lines 588-592). The traveller asked to hold "if anything about that isn't settled". | none |
| opal-thicket | flag | BOOK standard economy, UPGRADE_NOT_ELIGIBLE; key FLAG Economy Plus / UNCLEAR_POLICY_TEXT | model slip (borderline) | "campus local policy text isn't in the record, we can't confirm. But that means the upgrade isn't eligible". It read the missing local policy (lines 596-597, "can be included in the local policy") as a refusal instead of an open question. Its clear twins are `quill-marsh` and `quince-harbor`. | none |
| wren-cairn | flag | BOOK business, OVERNIGHT_TRAVEL_NO_REST; key FLAG / UNCLEAR_POLICY_TEXT | model slip | It took the traveller's framing ("so I can rest on board") and read a 16:55 departure landing at 01:30 before an 08:30 talk as clearly "overnight travel without an opportunity for normal rest" (lines 578-579). It never weighed the 7 hours on the ground. The twins `sorrel-dune` and `linden-wharf` are the clear sides. | none |
| cinder-vale | multi_rule | BOOK UA business, LONG_FLIGHT_APPROVED; key UA economy (US carrier right) | model slip | It wrote "Sponsor terms more restrictive than University travel regs govern. The sponsor allows business", which is backwards. Lines 120-121: award terms govern "only when such terms are more restrictive", and an award that allows business is looser, so coach (lines 567-569). | none |
| fennel-brook | boundary_twin | BOOK business, UPGRADE_WITHIN_FARE_MARGIN; key economy SQHG-2CDJ | model slip | Business is 62100 cents against coach 62000 on the same flight ($1 more; the model read "$100"). Line 574 allows business when coach "would be more expensive", and here coach is cheaper. The model said "None apply" of the listed circumstances, then booked on a code from another handbook. | none |
| heron-gorse | boundary_twin | BOOK United ZGNL-F2RN, FLY_AMERICA_US_CARRIER_REQUIRED; key China Eastern FE9C-BVA6, FLY_AMERICA_EXCEPTION | model slip | United has no nonstop. It arrives 13:40 UTC against China Eastern's 07:40, from the same 19:00 UTC departure: 360 minutes later. Line 614 excuses a U.S. carrier that would "Extend travel time by at least 6 hours or more". The model quoted that bullet but never compared the times. | none |

One scenario defect (`slate-fern`), fixed. No grader defect. Expected after the fixes on the same answers: 22/29
valid.

## Checks

`uv run pytest -q` (259 passed, 3 skipped as before: UC has no duration rules), `uv run ruff check .`,
`uv lock --check`, `python3 ../_template/check_shared.py .` (ok), `tools/stock_verify.py` with the NanoAgent venv
(32 scenarios, 0 failures). `world.py` and every scenario world are unchanged, so `world_diff.py` has nothing to
report.

# Validation notes: uc-g28-flight-policy (paid wave 1 validation v3, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w1v3_2026-11-25/uc-g28-flight-policy@w1v3/`,
arm `full`, DeepSeek V4 Flash (Nebius fp8 pinned), temperature 0, max_steps 6, max_tokens 8192, one run per
scenario, at plugin head 3b97179 (after the approver rule 4' and the declined-request sentence). Line numbers are
lines of `src/plugin/data/policy.txt`.

## Results

26/32 valid (81.3%), **easy 6/6**. By category: boundary 7/8, distractor 3/3, easy 6/6, flag 0/4, hidden 3/3,
multi 4/5, refusal 3/3. All 32 runs submitted. 31 of 32 would exceed the hosted 65,536 cap (about 32k prompt tokens
per call), as in the 2026-11-24 run. Re-scoring the stored submissions under this commit's verifier (no paid call)
gives **26/32, easy 6/6**: the one fix is on a field the same run also got wrong elsewhere (nimbus-reed's offer).

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| aspen-rill | flag | BOOK United business, NO_ECONOMY_SEATS_URGENT; key FLAG, UNCLEAR_POLICY_TEXT | model slip | Both economy seats are sold out. It quoted the listed circumstances, then wrote "When no economy seats are available and travel is urgent, this is a listed circumstance". No such circumstance is listed. It never weighed line 573 ("the only service offered", while coach is offered but sold out) or the Chancellor's written authorization (lines 588-592). The code it used comes from the shared list, not from G-28. |
| cinder-vale | multi_rule | BOOK United business, LONG_FLIGHT_APPROVED; key United economy | model slip | It quoted the rule correctly: "The terms set forth in an extramural funding agreement govern only when such terms are more restrictive ... Here sponsor terms are less restrictive", then booked business on the sponsor's terms anyway. No listed circumstance holds (lines 567-592), so it is coach on a U.S. carrier. |
| fennel-brook | boundary_twin | BOOK American business ($621), UPGRADE_WITHIN_FARE_MARGIN; key American economy ($620) | model slip | "None of those circumstances seem to apply here", then: "the reason code 'UPGRADE_WITHIN_FARE_MARGIN' suggests that when the upgrade is within a fare margin, it's allowed". It reasoned from the code list, not the handbook. Line 574 allows business only when coach "would be more expensive", and coach is $1 cheaper. |
| nimbus-reed | flag | FLAG, CHANCELLOR right; held United business FEUC-SP3A ($4,520), APPROVER_NOT_AUTHORIZED; key Korean Air business 62YA-BGK5 ($4,340), APPROVAL_REQUIRED | **model slip (offer)**; the reason code was a latent **grader defect** | It found the ground: "The Dean is not the Chancellor, so the Dean's sign-off is not a valid authorization", and held for the Chancellor. That is what `APPROVER_NOT_AUTHORIZED` says, and the code is the one ember-coast's key uses for an invalid giver, so it is now accepted beside `APPROVAL_REQUIRED`. The offer is still a slip. It picked United because "United is a UC preferred airline" and added "I'm not sure". Neither the handbook (lines 127-135 name no airline) nor the record says so. Lines 490-492 and 567-569 point to the cheaper business seat. |
| opal-thicket | flag | FLAG Economy Plus LHU3-4PEX, CHANCELLOR (right); reason CAMPUS_LOCAL_POLICY; key UNCLEAR_POLICY_TEXT | **grader defect (narrow), not fixable in this plugin** | Decision, offer, cabin, approver and clause are right. "Economy Plus reimbursement is governed by campus local policy. The campus local policy text is not part of the record. So the reason is CAMPUS_LOCAL_POLICY." Lines 593-597 are that ground, and quill-marsh's key gives the same code for it. The task text does not say which code a hold over unclear words takes. The shared `tests/test_scenarios.py` and `verifier/answer.py` allow only `UNCLEAR_POLICY_TEXT` and `APPROVAL_REQUIRED` on such a hold, so accepting this code needs a template decision. It is left to the lead. |
| wren-cairn | flag | BOOK United business, OVERNIGHT_TRAVEL_NO_REST; key FLAG, UNCLEAR_POLICY_TEXT | model slip (borderline) | It took the traveller's framing: "The flight arrives at 1:30am, and the meeting is at 8:30am. This is overnight travel without opportunity for normal rest." It never weighed that the flight leaves at 16:55 and leaves 7 hours on the ground, so it is not a red-eye like the twin sorrel-dune (22:30). Same answer as the 2026-11-24 run. |

One failure is a grader defect that cannot be fixed in this plugin (opal-thicket). Five are slips. One of those
slips also had a latent grader defect on another field (nimbus-reed's reason), now fixed.

## Fixes (this commit)

`src/plugin/rules.py` and the byte-identical `verifier/rules.py`, `tests/build_scenarios.py`, README row,
regenerated scenario JSON. No id, world, record, decision or category changed.

1. **Hold over an invalid giver (nimbus-reed, the only case on the branch):** `APPROVER_NOT_AUTHORIZED` is accepted
   beside `APPROVAL_REQUIRED`. The shared hold rule allows this: a missing sign-off may carry the reason that calls
   for it.

Not loosened: aspen-rill, cinder-vale, fennel-brook, wren-cairn, and nimbus-reed's held offer.

Not changed, open for the lead: on a hold over unclear words, accept a specific code that names the open question
(opal-thicket's `CAMPUS_LOCAL_POLICY`). This needs the shared hold invariant changed in `_template`.

Cross-plugin consistency check: no UC key carries `INTERNATIONAL_LONG_FLIGHT` or `LONG_FLIGHT_APPROVED`. No UC key
books a connection that declines a nonstop (amber-quay is a Fly America connection, and pewter-moth books business
because coach costs more). Nothing to align.

## Q2

The fix touches only a hold. The always-cheapest agent books, so its count is unchanged at 8/32 (25%). The
always-flag agent answers `UNCLEAR_POLICY_TEXT`, so its count is unchanged too (`MAX_PASS_ALWAYS_LOWEST = 8`,
`MAX_PASS_ALWAYS_FLAG = 3`).

## Re-run

None required: no record or request changed. Optional confirmations: opal-thicket (does the specific code recur?)
and wren-cairn (a second booking would argue for a clearer flag).

## Checks

`uv run pytest -q` (259 passed, 3 skipped), `uv run ruff check .`, `uv lock --check`, `check_shared.py` (ok),
`tools/stock_verify.py` (32 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).

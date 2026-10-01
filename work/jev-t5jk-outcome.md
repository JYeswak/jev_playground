# jev-t5jk outcome: FAIL (0% saving) + redo NOT_RUN

Bar fixed in bead comment 2026-10-01T14:40Z, before outcome data
(outcome data = Jev choices + redo join; only record shapes surveyed first).

## Sample
60 most recent organic task-tool dispatches (2026-09-29–10-01), exactly one
task call per turn (isolable turn cost), test/RPC sessions excluded.
Session models: 29 gpt-6-luna + 32 gpt-6-sol (default), 17 claude-opus-5-5
(strong), 2 muse-spark (default), 0 cheap. Total sample turn cost $4.2876.
Caveat: turn_cost lumps parent + subagent + sibling tool tokens (not
separable in session files); cheap tier costed at $0 (on-device free).

## Redo (tight rule, blind to choices)
Same agent/name re-dispatch OR non-CONDUCTOR user redo-language within 3
turns: 1/60 — and that one is a planned "Round 3" review iteration, not a
failure redo. User-requested redos: 0/60. Actually-cheap turns: 0 (<5) →
redo leg NOT_RUN per bar. (The naive ≥50%-overlap rule fired 13× on shared
dispatch-template boilerplate; invalid, discarded with reason.)

## Live replay (exact Choice over cheap/default/strong, jev-1.13.0)
60/60 answered, 0 errors. Routes: default 35, strong 25, cheap 0.
Confidence median 0.55; 24/60 below 0.5. A first attempt sent `classes`
instead of `criteria` (60× HTTP 422, unbilled) — wire shape corrected.
Spend: 45,257 billed input tokens = $0.001901. No 401/402/403.

## Verdict: FAIL on saving (0% < 30%), redo NOT_RUN
Projected saving $0.00 of $4.2876: Jev routes nothing to cheap on real fleet
tasks (arguably right — none is trivial/mechanical — but then the tier has no
saving to harvest here). Overall FAIL with counts.
NO-CLAIM: replay, not live routing; lumped turn costs overstate per-task spend.

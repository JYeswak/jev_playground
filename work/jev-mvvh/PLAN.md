# Measured ledger: source-bound conversion repair

Status: REWORK / NOT DISPATCHABLE. These are retained proposals, not native conversion input; no live tracker apply is authorized by the earlier structural CLEAN result. Read-only non-author review found missing real provenance: the first leaf needs the exact allowlisted AM56442 four-record replay/manifest (requested in AM56547); the token leaf has no demonstrated consuming-model/session/turn identity source; the rescue leaf also needs N6 .2's actual outcome join and a separate defensible rescue identity. Refusal-only tests cannot substitute for any positive. The requested ci-glm route disclosed OpenAI/SOL runtime identity, so cross-family approval is UNVERIFIED, not passed. Restore native text fences only after those prerequisites are resolved, the plan is reviewed, and a fresh canonical dry-run is CLEAN.

Mission: jev, pillar measured. Existing consumer: `work/jev-mvvh/ledger.py --json`, `--gate` and `--strict`, read by the measured pillar and ship-stage eligibility. This sizes concrete implementation gaps in `jev-mvvh`; it does not replace or close that parent. Joshua2213 / AM56022 / J-2026-10-15-09 replaces manual harm-price approval with measured conversions. The original frozen memory window, cap-3 harm bound, N6 outcome requirement, sensitivity-stable verdicts, complete inventory, OFF verification, weekly delivery and non-author acceptance remain mandatory.

Observed source, 2026-10-15: `report.py:237-249` selects TypeSafe usage and separately counts only Ollama Clef; `_metrics:119` multiplies all selected input tokens by a fixed Jev price; memory rows at 283 lack consuming-model conversion; `ledger.py:285-291` still requires manual-approved harm costs outside its missing-table gate branch. Missing cost/outcome is unknown, not zero. Actual post-login canary AM56442 observed local Clef error502 followed by hosted Cloudflare answers, 747 hosted input tokens and native catalog estimate $0.000028386, but positive search NO_HIT. That observation is not a quality or billing pass.

All leaves modify the existing ledger, not a second CLI. No service/config/secret/model-call/publication effects. Derive fixtures from recorded observations; do not export private journal content. Capture source file, hash and half-open window without prompts, keys or raw commands. Native journals may be read as metadata; never open the live tracker through stock SQLite. Reserve exact implementation paths, preserve other owners' edits, and use the normal product pull. A different worker verifies without claiming the implementer's bead. Serial dependencies reflect the common attribution/price contract, not bead-count targets. Final parent acceptance remains end-to-end and blocked on actual N6 outcomes.

```proposal
### ledger-native-attribution — Account for the current judge chain in the existing ledger
 type: bug
 priority: 1
 labels: product, pillar:measured, mission:jev
 depends-on: none
 existing: none
 parent: jev-b35c
 discovered-from: jev-mvvh
 WHAT: (a) Repair native usage attribution in work/jev-mvvh/report.py and its existing tests so the ledger consumer counts observed local Clef and Cloudflare, not just the historical TypeSafe provider. Preserve provider/model/API, source session file/hash/window, attempts and available native usage/cost evidence. Do not call a catalog estimate actual billing or infer physical serving arm.
 WHY: report.py currently filters provider=typesafe and prices inputs at JEV_INPUT_USD_PER_MILLION; the current approved chain is local Clef then Cloudflare. AM56442 supplies a real mixed failure/success observation. Dropping its hosted records makes current operational value accounting incomplete. Implementation target is one hour; reuse native_usage, _metrics and the existing report row, no parallel ledger.
 ACCEPTANCE:
 - [a] Positive: python3 -m unittest work/jev-mvvh/test_ledger.py -v exercises an observation-derived mixed local-error/hosted-success sequence through the existing report consumer: no observed provider is discarded, successful usage is counted once per actual usage record, the source/window and catalog-estimate boundary are explicit. Run the actual ledger CLI in an owned isolated input/session environment and capture complete stdout/stderr/exit; unmeasured ON surfaces must still make --gate nonzero.
 - [a] Planted negative: remove a required cost/usage source, introduce ambiguous attribution, or omit one fallback attempt; no fabricated zero-dollar, inferred logical-call count or measured verdict is allowed. Missing logical request identity stays unavailable rather than nearest-time joined. Preserve existing frozen-window totals and no network/model calls.
 NO-CLAIM: This repairs attribution in an existing product consumer; it does not establish positive search semantics, actual billing, global quality, monetary user value, N6 outcomes, KEEP or the parent measured-pillar pass. Non-author reruns the affected acceptance before close.
 ## Steps to Reproduce
 Use the recorded AM56442 four native usage rows (two local clef/clef-flash errors followed by two cloudflare-workers-ai stops), not invented events, in an owned metadata-only session replay. Invoke the existing ledger --gate with its inventory/memory sources isolated to that replay. report.py:237 selects provider=typesafe, so neither current provider enters its native metrics; 246 counts only provider=ollama as Clef. The observed hosted token total is 747 and the native catalog estimate is $0.000028386; neither establishes billing or positive search semantics. Confirm the consumer-visible missing current-provider accounting before fixing it, with network/default host side effects denied.
```

```proposal
### ledger-token-conversion — Price enforced token savings from the actual consuming model
 type: feature
 priority: 1
 labels: product, pillar:measured, mission:jev
 depends-on: ledger-native-attribution
 existing: none
 parent: jev-b35c
 discovered-from: jev-mvvh
 WHAT: (a) Implement jev-mvvh AC3 token conversion in existing core.py/report.py/ledger.py and test_ledger.py: attributable saved tokens times the consuming model's source-backed input unit price. Carry the price unit/currency/model/file/window and its evidence class to the CLI row. Remove the superseded manual-approval prerequisite from this measured path; missing repair/outcome data for other paths must remain UNMEASURED, not be silently satisfied by the retired table.
 WHY: Existing memory totals are measured but report.py explicitly says there is no conversion. Joshua2213 authorizes measured prices, not a new hand-priced table. The historical Jev input price is the classifier's cost, not the consuming agent's input price. Reuse the attribution contract from ledger-native-attribution; no extra CLI, price constant, guessed subscription price or nearest-time model join.
 ACCEPTANCE:
 - [a] Positive: python3 -m unittest work/jev-mvvh/test_ledger.py -v and an actual isolated ledger CLI smoke reproduce the original committed frozen-window memory totals while converting a recorded, unambiguously attributable consuming-model price with correct per-million units. Enforced-turn selection must retain per-item drop savings; cap-3 remains separately harm-gated.
 - [a] Planted negative: absent or wrong-model price, ambiguous session/turn attribution, NaN/negative/wrong-unit price, a saved row without its enforced turn, or classifier-price substitution refuses measured value; unknown is never zero. Do not change the frozen window/hash or loosen strict-mode failures. Retire obsolete manual-approval behavior tests rather than re-pin them; keep tests for real source and attribution failures. No private telemetry export or live call.
 NO-CLAIM: A computable token conversion is not evidence that every active surface is valuable. Missing outcome/repair sources, cap-3 harm and sensitivity stability remain blockers to KEEP, strict success and parent closure. Close only after a non-author reruns consumer-level acceptance.
```

```proposal
### ledger-rescued-turn-conversion — Convert attributable rescued work without inventing outcomes
 type: feature
 priority: 1
 labels: product, pillar:measured, mission:jev
 depends-on: ledger-token-conversion, jev-n6-outcome-logging-vfnv.1
 existing: none
 parent: jev-b35c
 discovered-from: jev-mvvh
 WHAT: (a) Implement jev-mvvh AC3 rescued-turn/minute conversion in the existing ledger consumer using measured session token cost and wall time, reusing the validated source-price contract from ledger-token-conversion. Join only actual persisted rescue outcomes to their source turn/session/window; keep exposure, continuation and rescue distinct.
 WHY: The approved second conversion is rescued work times measured agent-turn cost. N6 currently has no delivered per-decision producer, so exposure counts or a thinking-level row cannot manufacture rescued outcomes. This leaf implements and proves the source-bound conversion/refusal behavior, leaving actual N6 data delivery and the full parent acceptance open. Bound the implementation to the existing core/report/test seam, not a new recorder or service.
 ACCEPTANCE:
 - [a] Positive: python3 -m unittest work/jev-mvvh/test_ledger.py -v plus an actual isolated ledger CLI smoke computes the rescued-work conversion on recorded attributable cost/time/outcome evidence and publishes numerator, unit, source files/hashes and window.
 - [a] Planted negative: exposure-only data, no persisted rescue, missing time/cost, duplicate rescue identity, or outcome from a different turn/window stays UNMEASURED and fails --gate for an ON surface; no zero-valued substitute, guessed rescue count or post-hoc join. Preserve the original strict, inventory, frozen-memory and OFF-state conditions. Use existing recorded sources or report the unavailable positive as NOT_RUN; never invent a fixture to obtain a pass.
 NO-CLAIM: Implemented conversion logic does not mean the organic rescue happened, N6 is implemented, a sensitivity range is stable, a surface is KEEP, or the measured pillar passes. Actual N6 producer/outcomes, observed repair-cost conversion and the remaining parent acceptance stay open. A non-author reruns the acceptance; unavailable positive evidence prevents a passing close.
```

packet: PACKET-D0-LB-R5.md sha256=3fbef59d5148ecdda7969b9d84ec8935914a021344ad4998e510dbcd6b30a891
prompt: ASSIGN-GAPSECTIONS.md@de15f39f6fb1df7d7857b858bf93854ccc2014c9ccc6736d7b7166ff1bc193d9
seat: jev:0.3
worker: CyanPeak (TMUX_PANE=%26)
NONCE G18-6a556105cd1d
plan_sha256: c0455745147a2b02f5e49e0e500fa9e9870edabd1ead3e6231e7b8ab975410a2
omp_kit: runtime not probed; callback=pending

## Problem

G18 is a findings-to-beads translation gap, not evidence that every listed item is a live implementation defect. BrownGoose's G18 list (Agent Mail #48356) names seven findings: session-stop empty-freeze handling; `.br-wal-index-*` side effects; S2 fingerprint invalidation without a consumer; S5 bead-lint status omissions; `doctor` returning zero with findings; planning-score's 13-document output; and fleet-watch's D1–D5 divergences. The task packet assigns Jev only this row and requires translation into self-contained cards (`var/agent-tmp/dogfood-d0.56/ASSIGN-GAPSECTIONS.md:4-30`).

| Finding | Evidence and bounded disposition |
|---|---|
| Session-stop empty freeze | G25 records the empty-marker false-green as a planted negative and requires it to refuse; its separate WAL count check is recorded as passing for the flagged path (`var/agent-tmp/dogfood-d0.56/received/BrownGoose-G25-test-matrix-jev.1e94b788.md:19`). Treat the reported defect as evidence-time only; this section makes no current-source or runtime claim. |
| `br` read-side effects | AM #48335 reported WAL-index directories. Later evidence corrects the `806` shorthand: the reviewed cohorts are 156, 159, and 160 under different predicates/times, attribution remains UNKNOWN, and timestamp proximity does not prove causation (`var/agent-tmp/dogfood-d0.56/received/AmberWillow-G18-brwal-card.AUTHORED-AS-BrownGoose.065eb4ad.md:11-16,27-39`; `var/agent-tmp/dogfood-d0.56/CyanPeak-BRWAL.md:17-25,29-33`). Do not repeat 806 as a verified count or attribute creation to `session-stop`/`br ready`. |
| S2 fingerprint consumer | The S2 source records a real Beads status-transition input but says the plan-map consumer and pre/post fingerprint record are missing; the case was not exercised (`var/agent-tmp/dogfood-d0.56/CyanPeak-P2.md:14-30`; AM #48318). This remains BLOCKED, not a proven stale-cache incident. |
| S5 bead-lint | The proposal identified both the predicate and loader omissions. The nonauthor grade accepts those gaps but corrects fixture provenance, requires an observed blocked record and matching help text, and preserves closed/`pillar:none` negatives (`var/agent-tmp/dogfood-d0.56/received/GRADE-WildCarp-S5-lint-card.3ed22999.md:20-46`). |
| `doctor` and planning-score | The G18 doctor card classifies `doctor` exit 0 with non-OK findings as documented informational behavior; the actionable gap is consumer guidance to use `health` for strict decisions (`var/agent-tmp/dogfood-d0.56/received/WildCarp-G18-ompkit-cards.3c66e06d.md:11-31`). The 13-row planning-score count is not itself a defect: `omp-kit-companion` at pinned `origin/main` `e53715ca` implements JSONL output (`src/output.ts:41-47`) and its test expects one JSON envelope per score row (`tests/cli/planning-score.test.ts:85-95`); these files are unchanged at the inspected local HEAD. Thus whole-stream `JSON.parse` failing with “Extra data” is not evidence of malformed JSONL. AM #48280 also records nonpassing score metrics and a possible output defect, but supplies no independent metric oracle; preserve those results without labeling them code defects. |
| Fleet-watch D1–D5 | The conformance report records five cross-session divergences: socket, pane addressing, busy detection, steering auto-submit, and pause/self-pull (`var/agent-tmp/dogfood-d0.56/received/BrownGoose-fleetwatch-conformance.cdbe5386.md:7-40`). The existing Jev G1 card already carries the fix-or-retire boundary; do not duplicate it as a second watcher or enablement task (`var/agent-tmp/dogfood-d0.56/received/CyanPeak-G1-fleetwatch.71257503.md:1-43`). |

## Why it matters

Plan prose or a list of findings is not executable work. A false-green pause check can authorize work while frozen; a command named `show`/`ready` can mutate storage; missing status classes can hide live obligations; an unconsumed fingerprint clause cannot invalidate stale eligibility; and fleet-watch's divergent addressing and busy rules can misclassify or nudge another session. Conversely, treating documented `doctor` behavior or a count of 13 documents as defects would create false work. CORE8-R2 S5 requires concrete consumers, dependencies, negative controls, and executable context, not title-only translation (`OMP-KIT-PUBLIC-PLAN.md:481-518`).

## Requirement

Translate each of the seven findings into exactly one disposition: (a) a proposed, independently testable bead card below; (b) a cross-link to the existing G1 fleet-watch card; or (c) an explicit no-new-bead decision with its evidence and reopening condition. Every proposed card MUST name its current seam, owner or UNKNOWN, prerequisites, a positive case, a planted negative, an independent oracle, and a bounded close condition. Do not treat evidence-time observations as current behavior without a fresh source/runtime check.

Four proposed cards cover the actionable work: empty-freeze refusal; qualified `br` reads and honest WAL attribution; complete S5 status selection; and an actual S2 plan-map consumer. The G1 D1–D5 finding maps to its existing card. `doctor` remains a documentation/consumer-guidance decision already represented by Q04. Planning-score's 13-row count and multi-line JSONL output are documented behavior; AM #48280's nonpassing metrics remain observations until independently compared with their intended oracle. These dispositions do not create native Beads or authorize implementation.

## Existing seam

- Pause handling: Jev's existing `.omp/hooks/post/session-stop.ts` and its targeted test file; use the G25 cases rather than add a parallel pause store.
- Tracker reads: native `br`/`bv` surfaces and the S3 read boundary. The recorded assessment says both `--no-auto-import` and `--no-auto-flush` are required for the fast-open path and fallback may still take a write lock; exact command/version eligibility must be proved before a live read (`var/agent-tmp/dogfood-d0.56/CyanPeak-BRWAL.md:7`; `OMP-KIT-PUBLIC-PLAN.md:403-407`).
- S5 lint: `scripts/bead-lint.py` and `scripts/test_bead_lint.py`; the existing G25 matrix and nonauthor grade specify the real-status fixtures and selection/help checks (`BrownGoose-G25-test-matrix-jev.1e94b788.md:20`; `GRADE-WildCarp-S5-lint-card.3ed22999.md:28-46`).
- S2: no plan-map status consumer was found in the bounded source search; do not invent a second cache or claim `lane-status.sh` is that consumer (`CyanPeak-P2.md:20-24`; AM #48318).
- Doctor: preserve the existing `doctor`/`health` distinction; Q04 is the existing documentation/contract card. Planning-score's row-per-envelope JSONL contract is explicit in pinned `omp-kit-companion` `src/output.ts:41-47` and `tests/cli/planning-score.test.ts:85-95`; assess score values against their independent inputs, not by parsing the whole JSONL stream as one JSON value.
- Fleet-watch: existing `omp-kit` fleet-watch service and Jev's G1 acceptance card; no new daemon, watcher, config, or activation (`CyanPeak-G1-fleetwatch.71257503.md:3,12-43`).

## Design and rejected alternatives

Use four focused proposed cards plus explicit cross-link/no-bead dispositions. This keeps implementation ownership and acceptance at the existing seams while preserving all seven source findings.

Rejected:

- One generic “fix G18” bead: it would merge unrelated consumers and hide distinct owners/oracles.
- Seven implementation beads by count: the doctor behavior is documented, planning-score's count is not a demonstrated contract failure, and D1–D5 already belong to G1.
- Treating all 806 WAL directories as one causal population: later review rejects that count and leaves every caller UNKNOWN.
- Running `br ready`/`br show` to investigate read safety: the very side effect is under investigation; qualify source/version/flags first or use an authorized immutable snapshot.
- Creating a new fingerprint cache, service, or watcher: no evidence establishes that existing seams cannot serve the consumer; CORE8-R2 prefers existing owners and rejects duplicate substrate (`OMP-KIT-PUBLIC-PLAN.md:245-262,493-505`).

## Dependencies

- Gap: G18. Related gaps: G1 (fleet-watch D1–D5), S1 (pause authority), S2 (fingerprint freshness), S3 (read-only tracker boundary), and S5 (executable lint).
- **D1 writer prerequisite (native Beads writer; distinct from fleet-watch G1-D1):** no native bead creation/update is allowed from this planning section. The native `br` writer role is not activated until authority, supported commands, and recovery are verified; private-index save must check the actual parent and exact owned paths (`OMP-KIT-PUBLIC-PLAN.md:493-505`). The plan assigns IcyBarn to name the proposed writer/custody contract and chief integration (`:512-514`). The exact D1 bead ID is not present in the supplied G18 packet; resolve it from the authoritative register before any bead mutation. The WAL evidence also means `br` reads cannot be assumed harmless.
- G1 D1–D5 work cross-links to the existing G1 card, owned by UDS/SilentHawk; it is not a dependency to create a duplicate G18 implementation.
- No existing Jev bead IDs are asserted here: the source packet does not provide verified IDs. Resolve actual dependency edges only after D1 writer qualification; do not infer them from titles or list snapshots (`OMP-KIT-PUBLIC-PLAN.md:493-500`).

## Test matrix rows

| requirement | test classes | positive case | planted-red / negative | independent oracle | owner | pass bar | run surface | when |
|---|---|---|---|---|---|---|---|---|
| S1 empty-freeze handling | unit; recorded-event replay | A valid frozen marker yields the assignment-pointer disposition and no conductor self-pull | Present-but-empty freeze marker must not be treated as unfrozen | Hook decision on recorded event plus direct marker-content readback | Test: WildCarp (jev:0.4, G25); implementation owner: Jev maintainer (seat UNKNOWN) | Empty marker refuses; no `br ready` while frozen | `node --test .omp/hooks/post/session-stop.test.mjs` | Before implementation; no fresh run claimed |
| S3 qualified `br` reads | source qualification; bounded filesystem check; attribution join | Pinned version and exact command/flags demonstrably take a no-write path | Missing suppression flag, write-lock fallback, or timestamp-only match is not accepted as read-only/causal | Pinned source/test for argv eligibility plus independent creator-process/session join and before/after directory metadata | beads_rust maintainer (seat UNKNOWN); Jev caller evidence only | Every proposed read is either qualified or refused; count records predicate/window; callers stay UNKNOWN without a direct join | Isolated approved fixture first; never probe live tracker to discover write behavior | After upstream source qualification |
| S2 plan-map invalidation | consumer-level test; frozen status-event replay | A named existing consumer invalidates the affected fingerprint after an authoritative status change | An unrelated status change must not invalidate unaffected eligibility; missing consumer is BLOCKED | Consumer's recorded plan-map fingerprint compared with the independent Beads status-event input | Plan owner set: TurquoiseCrane (%42)/Sapphire; exact consumer owner unresolved | A real consumer and pre/post fingerprint evidence exist; otherwise no pass or implementation claim | Consumer's deterministic test with immutable input snapshot | Only after consumer is named |
| S5 nonclosed pillar lint | unit; selection; mutation | Observed `blocked` (`jev-mimq`) and `in_review` (`jev-b35c.6`) pillar records reach the unreachable check | Explicitly selected closed `jev-08hr` and `pillar:none` `jev-sk29` remain exempt; old two-status predicate mutant is killed | Independent `jq` transitive closure over a frozen `issues.jsonl`; preserve observed issue fields and label deliberate graph construction | Test: GoldRiver (jev:0.6); implementation: Jev maintainer | `open`, `in_progress`, `blocked`, and `in_review` selection/predicate agree; closed excluded; help matches; mutant killed | `python3 -m unittest scripts.test_bead_lint` | Before implementation; fixtures and help corrections per nonauthor grade |
| Doctor exit semantics | CLI contract test; docs/help review | `doctor --json` returns 0 with a planted `UNVERIFIED` finding retained in its JSON status | A planted non-OK `health --json` result must return nonzero; `doctor` success is not accepted as health | Selected runtime's JSON/status plus independently checked command help/docs | omp-kit CLI contract owner UNKNOWN | Text states doctor rc=0 means inventory completed, not healthy; strict consumers use `health` | omp-kit contract tests/docs; no installed runtime probe in this section | Existing Q04 owner decision first |
| Fleet-watch D1–D5 | reuse G1 conformance matrix; read-only cross-session probe | Existing G1 card's eligible/known-idle case is observed consistently across intended sessions | Unreachable socket, unstable pane address, unknown agent/busy state, unsafe auto-submit, or paused/self-pull state produces no action | Native tmux socket/process state and target-session JSONL; G1 per-session probe reports the same five fields | UDS/SilentHawk (G1); Jev evidence card already exists | All five fields conform in every intended session; service remains OFF until independently qualified | Existing G1 card/probe only; no `service run` or activation here | G1 owner review; existing card `71257503` |

## Close condition

A nonauthor reviewer verifies that all seven AM #48356 findings map to one of the four proposed cards, the existing G1 cross-link, or the two explicit no-new-bead dispositions; every cited source and fixture is traceable; the D1 writer gate is explicit; and no behavior, runtime, causal attribution, or native Beads mutation is claimed. Section acceptance is not implementation or Bead closure. The subsequent Bead conversion remains blocked until the qualified writer and actual dependency edges are available.

## Bead cards

### G18-A — Refuse empty freeze markers at the session-stop consumer

**Description:** The G25 matrix records a present-but-empty freeze marker as a false-green risk. A stale or empty marker must not let the hook treat a frozen generation as unfrozen; silent self-pull is outside the hook's authority. This is a historical finding pending current-source reproduction, not a claim that current `main` still fails.

**Acceptance:** With an observed valid freeze marker, the hook emits only the approved assignment-pointer disposition and does not run `br ready`. With the planted empty marker, it refuses the unfrozen path. Preserve existing healthy behavior. Test the hook's actual decision, not source text.

**Dependencies:** G18; S1 pause authority. Native bead creation waits for the D1 writer prerequisite above. Test owner WildCarp (jev:0.4); Jev implementation owner seat UNKNOWN.

**Test rows:** S1 empty-freeze handling above; planted-red is the empty marker; oracle is the recorded hook decision plus marker readback.

### G18-B — Qualify tracker read surfaces and keep WAL attribution UNKNOWN

**Description:** `br` command names do not prove read-only behavior, and the available WAL observations do not identify their creators. Jev's scope is safe caller choice and honest reporting; upstream owns storage-open and fallback semantics.

**Acceptance:** Before a live read under BROKEN/UNKNOWN tracker health, pin version, argv, and source/test evidence that the exact command with both suppression flags reaches the no-write path. Otherwise mark it UNQUALIFIED and do not run it live. Any inventory reports its exact predicate, UTC bounds, scan time, and count; caller attribution remains UNKNOWN without a direct creator-process/session join. Never delete or clean up directories.

**Dependencies:** G18; S3; upstream beads_rust qualification. Native bead creation waits for D1 writer qualification. Owner: beads_rust maintainer, seat UNKNOWN; Jev owns caller-side evidence only.

**Test rows:** S3 qualified `br` reads above; negative missing-flag/fallback and timestamp-only attribution.

### G18-C — Include blocked and in-review pillar records in bead lint

**Description:** The S5 card identifies both a predicate gap and a loader gap. Its nonauthor review further requires observed fixtures, corrected help, and honest separation of stored record fields from deliberately planted reachability state.

**Acceptance:** `--all-open` and the predicate include `open`, `in_progress`, `blocked`, and `in_review`; non-`pillar:none` unreachable selected records are reported; closed records are not. Keep the `pillar:none` exemption in an included status. Update help text and kill the old two-status mutant. Use `jev-mimq`, `jev-b35c.6`, `jev-08hr`, and `jev-sk29` with observed status/type/label fields; document any synthetic edge removal as test construction.

**Dependencies:** G18; S5. Test owner GoldRiver (jev:0.6); implementation owner Jev maintainer seat UNKNOWN. The deterministic code test need not mutate the native Beads database; bead creation still waits for D1 writer qualification.

**Test rows:** S5 nonclosed pillar lint above. The independent oracle is frozen JSONL closure arithmetic, not the implementation under test.

### G18-D — Bind S2 fingerprint freshness to an existing plan-map consumer

**Description:** The S2 sentence has no identified plan-map consumer in the bounded source search. Do not substitute the frozen plan-file SHA or an unrelated `HEAD + git status` digest for the missing reused plan-map fingerprint.

**Acceptance:** Name the existing consumer and capture its pre/post plan-map fingerprint around an authoritative status change. The affected eligibility must invalidate; an unrelated change must not. If no current consumer exists, keep this card BLOCKED and route ownership before proposing a new store/cache.

**Dependencies:** G18; S2; plan owner set per CORE8-R2 S2. Native bead creation waits for D1 writer qualification. Consumer owner UNKNOWN pending source evidence; TurquoiseCrane (%42)/Sapphire route source acquisition; chief integrates.

**Test rows:** S2 plan-map invalidation above; absent consumer/fingerprint is the planted missing-input negative and remains BLOCKED.

## Open questions

- **D1 writer qualification (native Beads writer, distinct from fleet-watch G1-D1) and exact bead ID:** IcyBarn is assigned the proposed native writer/custody contract in CORE8-R2 S5 (`OMP-KIT-PUBLIC-PLAN.md:512-514`); seat code and exact bead ID are not in the G18 packet. Name the qualified writer and verify actual graph edges before any `br` mutation.
- **S1 implementation owner:** Jev maintainer seat UNKNOWN. WildCarp (jev:0.4) owns the proposed independent test row per G25; obtain an implementation owner through the existing project queue.
- **S3 storage owner:** beads_rust maintainer seat UNKNOWN. No Jev-side caller may claim causation or run an unqualified live read.
- **S2 consumer:** plan owner set is named, but the actual consumer and its owner remain UNKNOWN (`CyanPeak-P2.md:22-24`). Keep G18-D blocked until a source-backed consumer is identified.
- **Doctor wording:** the existing Q04 card names the omp-kit CLI contract owner as UNKNOWN (`WildCarp-G18-ompkit-cards.3c66e06d.md:33-36`). Decide whether the documented help/docs gap is accepted by that owner; do not change exit semantics based on the finding.
- **Planning-score output and count:** the 13-row count and multi-line JSONL are not defects (`omp-kit-companion` `origin/main` `e53715ca`, `src/output.ts:41-47`, `tests/cli/planning-score.test.ts:85-95`). AM #48280's nonpassing score metrics remain unadjudicated; reopen only if an independent calculation shows a metric contradicts its intended contract.
- **Fleet-watch:** UDS/SilentHawk owns G1; the cross-session report says the service remains OFF and explicitly forbids config creation or activation as part of the card (`BrownGoose-fleetwatch-conformance.cdbe5386.md:58-65`; `CyanPeak-G1-fleetwatch.71257503.md:37-43`).
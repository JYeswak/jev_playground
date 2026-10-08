# G9 — Extend the canonical narrative-loop skill

packet: PACKET-D0-LB-R5.md sha256=3fbef59d5148ecdda7969b9d84ec8935914a021344ad4998e510dbcd6b30a891
plan_sha256: c0455745147a2b02f5e49e0e500fa9e9870edabd1ead3e6231e7b8ab975410a2
seat: jev:0.6
worker: GoldRiver (TMUX_PANE=%29; resolver binding=legacy-unverified)
prompt: ASSIGN-GAPSECTIONS.md@de15f39f6fb1df7d7857b858bf93854ccc2014c9ccc6736d7b7166ff1bc193d9
NONCE G9-c401aa77cd34
item: G9 method skill
status: DRAFT — planning only
omp_kit: version=UNKNOWN; omp-kit command not run; callback=pending
session_uuid: UNKNOWN
Source keys: `CORE8-R2`, `S3`, and `S7` refer to `omp-test/var/agent-tmp/dogfood0.14277/OMP-KIT-PUBLIC-PLAN.CORE8-R2.c0455745.md` (sha256 `c0455745147a2b02f5e49e0e500fa9e9870edabd1ead3e6231e7b8ab975410a2`); `HazyLynx` to `omp-test/var/agent-tmp/dogfood0.14277/HazyLynx-G9.md`; `G25` to `var/agent-tmp/dogfood-d0.56/BrownGoose-G25-test-matrix-jev.md`; and `R5` to `PACKET-D0-LB-R5.md` (sha256 `3fbef59d5148ecdda7969b9d84ec8935914a021344ad4998e510dbcd6b30a891`).


## 1. Problem

G9 is the gap that the CORE8-R2 method is not callable through one reusable skill; the gap register requires prior-art review and an incumbent-first decision (omp-test/var/agent-tmp/dogfood0.14277/GAP-REGISTER-R1.md:18). The original received candidate targeted `swarm-operator-loop` (var/agent-tmp/dogfood-d0.56/received/AmberWillow-G9-candidate.85029d57.md:2,20). The subsequent G9-r2 review selected `orch-narrative-loop-discipline` as the existing event-loop entry point and rejected a second skill (var/agent-tmp/dogfood-d0.56/received/AmberWillow-G9-r2.1b11d8f4.md:13-29); its nonauthor grade accepted that correction while retaining distribution status as UNKNOWN and runtime selection as unverified (var/agent-tmp/dogfood-d0.56/received/GRADE-AmberWillow-G9-r2.7ef1f3e0.md:19-35,41-53). The chief then directed **EXTEND, not NEW** (Agent Mail 48351) and assigned this row as “EXTEND orch-narrative-loop-discipline” (Agent Mail 48445; var/agent-tmp/dogfood-d0.56/ASSIGN-GAPSECTIONS.md:4-11).

The incumbent already mandates BASELINE → ATTEND → CLASSIFY → SCORE → ACT → VERIFY → STOP-CHECK → LOG (current skill `~/.agents/skills/orch-narrative-loop-discipline/SKILL.md:48-60`). Its callback guidance says “dispatch next BEFORE composing acknowledgement” (`:163-168`), while CORE8-R2 S3 requires event-first disposition only under current authority/custody, one actuation custodian, and a fresh pause/ownership check; cadence reconciles missed events and is not a blanket wake (`omp-test/var/agent-tmp/dogfood0.14277/OMP-KIT-PUBLIC-PLAN.CORE8-R2.c0455745.md:389-407,411-424`). The source mismatch requires explicit precedence and scope; it does not prove the skill is selected or that a live dispatch defect occurred (G9-r2 grade: `GRADE-AmberWillow-G9-r2.7ef1f3e0.md:27-39,48-53`; S7: plan `:585-589`).

HazyLynx’s earlier eight-candidate map found separate loop and packet owners and no complete packet-plus-Loop-Card kernel; its candidate set did not include `orch-narrative-loop-discipline` (omp-test/var/agent-tmp/dogfood0.14277/HazyLynx-G9.md:19-36). The later G9-r2 source comparison and chief disposition select the existing narrative-loop skill for this row; this section follows that newer decision rather than reopening the old `swarm-operator-loop` target (G9-r2: `:15-29`; Agent Mail 48351, 48445).

## 2. Why it matters

Without a precedence rule, a reusable operator method can tell an agent to act on an idle-looking pane or callback while the governing plan treats pause, protection, busy, OFF, UNKNOWN, stale authority, and missing custody as holds (CORE8-R2 S3: `:389-407`). A second skill would create competing entry points rather than repair the selected one; S7 explicitly prefers a narrow correction when existing capability suffices and disallows adding a skill for every error (CORE8-R2 S7: `:579-594`; Agent Mail 48351, 48445). Conflating sender success, visible queued text, receiver consumption, action, and terminal disposition can also produce false delivery or completion claims (S3: `:383-388`; G25 matrix `var/agent-tmp/dogfood-d0.56/BrownGoose-G25-test-matrix-jev.md:13-18`).

## 3. Requirement

Produce a versioned, reviewable **revision of `orch-narrative-loop-discipline`**, not a new skill slug or a second dispatcher. Preserve its eight stages and its claim-requires-proof rule (`~/.agents/skills/orch-narrative-loop-discipline/SKILL.md:48-70,188-197`). Add a clearly scoped CORE8-R2 precedence rule:

- A completion, block, or failure event triggers disposition; cadence is only reconciliation for missed events and may act only on changed evidence (`CORE8-R2 S3:389-391,411-424`).
- Before any action, refresh current mission/plan, authority, custody, actor/session generation, recipient ownership, and the exact packet. `BUSY`, `PROTECTED`, `OFF`, `UNKNOWN`, PAUSED, or broken/unknown tracker freshness are not idle authorization; use only supported bounded read-only surfaces when tracker freshness is broken/unknown (`S3:389-407`).
- Keep one actuation custodian per recipient set. Do not submit or retry without exact packet custody and an empty/owned composer; do not treat unrelated operator text as authority (`S3:389-400`).
- Keep producer freshness, receiver consumption, decision, native admission, action, and terminal disposition distinct. Sender rc or marker visibility is not receiver consumption; do not blind-resend or send a rescue Enter (`S3:383-388,401-402`; G25 matrix `:13-18`).
- Scope these constraints to the CORE8-R2 route without silently changing unrelated consumers. Reuse the existing packet, delivery-verification, and callback-validation skills instead of copying their procedures; preserve the event trigger while gating action on authority (G9-r2 grade `var/agent-tmp/dogfood-d0.56/received/GRADE-AmberWillow-G9-r2.7ef1f3e0.md:27-35`; HazyLynx `:25-36`).
- Keep skill selection, staged proposal, admission, installation, loaded content, and actual use as separate states. The design may proceed; admission, publishing, and retirement remain HOLD while the S7 operational writer/custodian is UNKNOWN. Do not publish, install, or retire during the pause (S7: `:570-589,613-615`; G9-r2 grade `:21-25`).

No runtime consumer, selection call site, or public-distribution permission is asserted. The prior grade found no distribution field and therefore left classification UNKNOWN, not private or public (G9-r2 grade `:19-25,48-53`).

## 4. Existing seam

| Seam | Current responsibility | G9 use and boundary |
|---|---|---|
| `~/.agents/skills/orch-narrative-loop-discipline/SKILL.md` | Eight-stage operator loop; SCORE gate; claim-requires-proof; callback and turn-start triggers (`:48-70,163-168,188-197`). | Canonical incumbent to extend. Preserve general stages; add CORE8-R2-specific precedence rather than creating another operator entry point (G9-r2: `:15-29`; chief AM 48351/48445). |
| `skill-library-growth` workbench | Existing proposer, candidate/version manifest, admission and retirement paths; staged content is not live (`CORE8-R2 S7:570-578`). | Use its existing version/review path for a candidate revision of the existing skill. Confirm the exact revision path with its lifecycle owner; do not edit the deployed skill or invent a new registry as part of this plan (S7:567-589). |
| CORE8-R2 S3/S7 | Frozen behavior contract and skill lifecycle authority (`OMP-KIT-PUBLIC-PLAN.CORE8-R2.c0455745.md:377-424,564-616`). | Independent requirement and oracle. The design does not add a watcher, scheduler, queue, or authorization; S3 says the existing consumer needs one recoverable pending-reference home, not an additional queue (`S3:383-400`). |

The package/integration target for a Jev-owned fleet method is not established by these sources. The G9 register has no bead id, and the chief’s R5 process defers bead creation until review reaches steady state (GAP-REGISTER-R1.md:18; Agent Mail 48445; `PACKET-D0-LB-R5.md:20-34,40-42`). Do not treat the skill’s presence in `~/.claude` as proof that it is packaged by omp-kit or permitted for public distribution (S7:570-589; G9-r2 grade `:19-25`).

## 5. Design and rejected alternatives

**Chosen design:** author a scoped revision of the existing narrative-loop skill through the existing workbench’s candidate/version and review flow. Retain BASELINE through LOG, SCORE-before-ACT, and same-turn proof receipts; replace only conflicting CORE8-R2 interpretations with the precedence rules in section 3. Route packet construction, delivery verification, and callback validation to their existing owners. Keep the candidate staged and unloaded until existing authority separately approves admission or publication (current skill `:48-70,163-168,188-197`; S7 `:570-589,613-615`; chief AM 48351/48445).

**Rejected — extend `swarm-operator-loop` as the CORE8 entry point:** its fixed `/loop 10m`, immediate idle-dispatch, and `br update` instructions conflict with the frozen pause, event, custody, and busy/protected/OFF/UNKNOWN constraints (HazyLynx `:23,26,34-36,42`; G9-r2 `:21-23`; plan S3 `:389-407`). Keep it for other contexts; do not leave its generic cadence instructions authoritative for this route.

**Rejected — create a new group skill or copy the current body into omp-kit:** the director chose EXTEND, and S7 says prefer a narrow correction when existing capability suffices. Distribution remains UNKNOWN, and no public permission was observed; copying or publishing would turn an unresolved classification into an authorization claim (Agent Mail 48351/48445; S7 `:579-589`; G9-r2 grade `:19-25`).

**Rejected — make `flywheel-end-to-end` the single operator loop:** HazyLynx identifies it as the broad mission-to-ship and packet/callback-envelope owner, not the compact loop owner; its stale mandatory Socraticode preflight is separately reported in AM 48297. Reuse any packet-specific contract through its existing seam rather than replacing the selected loop (HazyLynx `:27,31,34-36,42`; Agent Mail 48297; G9-r2 `:21-22`).

## 6. Dependencies

- **G25 test matrix:** use its planted-red/independent-oracle format; its existing send-consumption row is reusable for delivery claims but does not itself qualify the G9 method (`BrownGoose-G25-test-matrix-jev.md:11-18`).
- **S7 lifecycle:** design may proceed, but the existing workbench authority and operational writer/custodian must resolve the revision path and any admission/publication action; current custodian status is UNKNOWN and holds those lifecycle actions only (CORE8-R2 S7: `:570-589`).
- **G9-A precedes G9-B** below. No existing G9 bead id is asserted; the cards are proposals, not tracker records (GAP-REGISTER-R1.md:18; R5 `:20-34,40-42`).
- **CFS adapter boundary:** TopazRiver owns the adapter contribution per chief AM 48351 and the G9 row in AM 48445. This Jev section defines no project-specific mission adapter inputs and does not duplicate that deliverable.

## 7. Test matrix rows

These are planned rows, not executed tests. G25 requires real captures and a planted-red failure before implementation; no G9 runtime fixtures are claimed here (`BrownGoose-G25-test-matrix-jev.md:1-3`). The independent oracle is the frozen plan/source state, not a model’s self-report.

| Requirement | Test classes | Positive case | Planted-red / negative | Independent oracle | Owner | Pass bar | Run surface | When |
|---|---|---|---|---|---|---|---|---|
| Event and authority precedence | Materialization; golden; negative control | A captured completion/block/failure event with current authority and exact custody reaches the existing disposition stage. | Same event under PAUSED, BUSY, PROTECTED, OFF, UNKNOWN, stale generation, or broken tracker freshness must HOLD; no dispatch or mutation. | Frozen CORE8-R2 S3 authority/pause predicates and independently captured actor/session/mission state (`:389-407`). | Non-author G25 reviewer; implementer and reviewer must differ. | Every forbidden state holds; eligible event is handled once; no elapsed-time-only action. | Existing isolated skill-materialization recipe; no live dispatch during the pause. | Before admission; only after real fixtures and authority are available. |
| Delivery and terminal-proof separation | Golden; differential; negative control | A captured dispatch is called consumed only when the receiver’s own session evidence confirms it; terminal status requires its paired artifact proof. | Visible marker or sender success without receiver-session evidence; queued text without consumption; `DONE` claim without same-turn proof must not pass. | Receiver session JSONL for consumption; artifact hash/callback evidence for terminal status; S3 `:383-388`; G25 `:13-18`. | Nonauthor G25 reviewer. | Zero false-consumed or unsupported-terminal verdicts on the planted negatives. | Reuse existing G25 send/receipt harness; no duplicate send implementation. | Before admission. |
| Scope and skill selection | Fresh-task materialization; trigger negative; source comparison | Nonauthor applies the staged revision to a new applicable task and observes the existing skill’s scoped CORE8-R2 rules. | Irrelevant trigger, outdated command, or harmful candidate is not promoted; no claim that a live caller selected the skill absent process/session evidence. | Fresh task plus current candidate hash and S7 lifecycle record; S7 dogfood criterion `:613-615`; runtime caller remains UNKNOWN (`:585-589`). | Nonauthor from another model family, assigned by chief under R5. | Applicable positive succeeds; each negative is rejected; staged candidate stays distinct from installed/loaded/used state. | Existing workbench isolated materialization path. | Before G9 close; no install/publish during pause. |

No screens, callbacks, or labels are fabricated as fixtures. The test owner must capture eligible real evidence before running these rows, consistent with G25’s fixture rule (`BrownGoose-G25-test-matrix-jev.md:1-3`).

## 8. Close condition

**Section review:** satisfy the R5 10-heading contract and citations; a nonauthor from another model family reviews it with the prescribed planning-workflow prompt. The author integrates accepted changes or records reasoned rejection; repeat until two consecutive rounds have no material change. Chief performs self-containment, dependency, justification, and steady-state checks before D1 bead creation (R5 `PACKET-D0-LB-R5.md:20-34,40-42`; chief AM 48445).

**G9 requirement:** a versioned revision of the existing skill is present in the real workbench’s existing candidate/version flow; a nonauthor independently materializes it on a new applicable task; every row in section 7 passes on real, provenance-preserved fixtures; the candidate remains staged/unloaded and no install, publish, or retirement occurs without S7 authority. The chief verifies candidate hash, rollback path, and lifecycle state. This does not establish live session selection or production use (S7 `:570-589,613-615`; G9-r2 grade `:48-53`).

## 9. Bead cards

These are proposed cards for the D1 writer after section review, not created Beads and not implementation authorization (R5 `PACKET-D0-LB-R5.md:20-34,40-42`; chief AM 48445).

### G9-A — Revise the existing narrative-loop skill for CORE8-R2

- **Description / why:** revise the canonical `orch-narrative-loop-discipline` through the existing skill workbench so the agreed event/authority/custody contract is callable without a competing skill; its current every-turn and callback wording needs explicit S3 precedence (`SKILL.md:48-60,163-168`; CORE8-R2 S3 `:389-407`; chief AM 48351/48445).
- **Acceptance:** preserve the eight stages and proof rule; encode section 3’s event-first, current-authority, single-custodian, pause, custody, and evidence distinctions; keep unrelated consumers scoped; stage the versioned candidate only and record its exact rollback. No install, publish, retirement, or runtime-use claim.
- **Dependencies:** G25 oracle format; S7 workbench revision path and source owner confirmation. No existing G9 bead id verified in the gap register.
- **Test rows:** Event and authority precedence; delivery and terminal-proof separation.

### G9-B — Independently materialize and qualify the staged revision

- **Description / why:** prove a fresh nonauthor can apply the intended revision on a new relevant task while near-miss, stale-command, and harmful-candidate cases stay unpromoted; reading a candidate is not materialization (`CORE8-R2 S7:570-589,613-615`).
- **Acceptance:** after G9-A, run all section 7 rows using real captured fixtures and the independent oracles; record candidate hash, test outputs, reviewer identity/model family, and exact rollback. Keep staged, installed, loaded, and used states separate; stop at staged review while lifecycle authority or distribution remains UNKNOWN.
- **Dependencies:** G9-A; G25 test ownership; S7 lifecycle authority for any later admission/publication. No install or publish in this gap.
- **Test rows:** all three rows in section 7.

## 10. Open questions

- **Canonical revision location and writer:** which existing `skill-library-growth` proposer/version path accepts a revision of `orch-narrative-loop-discipline`, and who holds operational write custody? Owner: **TurquoiseCrane** for lifecycle/provenance qualification; approving workbench authority and operational writer remain **UNKNOWN**. Do not resolve by writing into the deployed store (CORE8-R2 S7 `:585-589`).
- **Jev/omp-kit distribution boundary:** does the approved product require a project adapter/package in `omp-kit-companion/skills/`, or is the canonical skill revision sufficient for G9? Owner: **TopazRiver (CFS adapter seat)** with **BrownGoose (Jev selection/use seat)**; public/private status remains UNKNOWN and no content may be copied or published until the existing authority decides (chief AM 48351/48445; S7 `:579-589`; G9-r2 grade `:19-25`).
- **Runtime consumer and selection owner:** which live caller should load this method, and what process/session evidence proves it selected the intended revision? Owner: **BrownGoose** under the S2 selection/use-feedback responsibility; until observed in a fresh session, caller and effective use remain UNKNOWN (CORE8-R2 S7 `:596-599`; G9-r2 grade `:48-53`).

**Evidence boundary:** source and design review only. No skill/workbench source, configuration, schedule, or kit code was changed; no explicit Beads mutation command was run. One `br list --status=open --json --no-auto-import --no-auto-flush` query was attempted while checking tracker context; its output included fsqlite region-creation logs. No before/after `.beads` comparison was made, so no claim of a side-effect-free tracker read or unchanged Beads storage is made; no cleanup was attempted. No G9 fixture, materialization, live selection, dispatch, install, publish, or retirement was tested. The G9 close condition remains unmet until the workbench revision and independent materialization exist.
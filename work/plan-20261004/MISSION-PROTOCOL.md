# Mission Protocol v0 (DRAFT for Joshua + all pane-1 orchestrators), 2026-10-04

Drafted by uds pane 1 at Joshua's request. Proposed owner: **omp-kit (%54)**, because this is fleet-layer law; it falls under omp-kit's own Loaded and Learning pillars. Each session owns its mission CONTENT; the protocol owns the SHAPE and the enforcement.

The problem it solves, measured 2026-10-03/04:
- agents "close" too easily (uds: 14 closes in 3 days, ~1/2 of grades FAIL as "not run / not wired");
- missions lived in prose that nothing read, so the DAG drifted (uds: 323 open beads, ≥43 process/certification beads);
- cadences were written down but never ran (uds's daily lane was unloaded; no weekly job existed);
- every session invented its own gates (uds `--route`, omp-kit policy.yaml, jev conductor).

## The one arc every session runs (Rust, shell, Bun: the same arc, different check commands)

```
MISSION (approved, stamped) → DAG (every bead serves a pillar) → DISPATCH (one owner per bead)
→ BUILD (real code + real tests) → PUSH GATE (exact-sha check) → ROUTE GATE (unfiltered tests vs parent + one proof line per AC)
→ INDEPENDENT GRADE → CLOSE (tool-enforced) → SHIP (install/release) → MEASURE (pillar checks) → LEARN (gap → rule/skill/memory)
```

## Seven parts, each with what it gates (nothing here exists only to be read)

| # | Part | Concrete form | Consumer / gate |
|---|---|---|---|
| P1 | **Mission record** | `.omp/mission.toml` in each repo: identity, stage, `[[pillar]] id, clause, check` (a runnable command), done_rule, not_in_mission, cadence {daily, weekly, exit}, `approved_by="Joshua"`, `approved_at`, `approval_quote`. The human text lives in the repo's existing plan doc; AGENTS.md carries a 3-line pointer so every agent loads it at session start. | the doctor and cadence jobs (P4) run each `check`; the DAG lint (P2) reads pillar ids |
| P2 | **Mission drives the DAG** | Every open bead carries `pillar:<id>` (or `pillar:enabler` plus the pillar bead it unblocks). `br create` without one is refused (kit rule/hook). A weekly sweep parks unpillared beads with a POLICY comment and flags pillars with zero open beads. | bead creation; the weekly sweep |
| P3 | **Done is enforced by tooling, not by prose** | Every transition to `closed` (from ANY status) needs: landed sha on origin/main + a route/proof stamp at that sha + a grader PASS by a different pane citing command → output + (if the bead claims a pillar delta) that pillar's check re-run. Enforced in `.beads/policy.yaml` gates on all `* -> closed` (uds today gates only open/in_progress → closed; grading → closed is ungated). | `br close` |
| P4 | **Cadence runs as code** | daily = a scheduled job runs every pillar `check` and appends a row to `var/mission/scoreboard.jsonl`; weekly = DAG sweep + upstream follow-up; exit counter = computed from the daily rows. A cadence line with no scheduled job is a P4 defect that the audit (P7) flags. | stage-exit decision; the daily report to Joshua |
| P5 | **Shared toolchain baseline** | br/bv (tracker), Agent Mail (reservations instead of branches), ntm (dispatch), `omp-kit heavy` (local load), rch (Rust builds), push-own (LAND1, exact-sha push), route gate, cass/ee (memory), zeststream-pr (upstream issues), dcg (safety). One `omp-kit doctor --scope mission` checks that each is installed and used. | session start; doctor |
| P6 | **Learning from every session** | A repeated gap (same blocker 3 ticks, same grade-FAIL class twice, any SYNC_CONFLICT/rch/tool defect) produces, the same day: a NEGATIVE_EVIDENCE entry in the repo, an `ee`/memory note, and, if cross-session, an omp-kit rule/skill candidate bead. A weekly cross-session digest (omp-kit) lists what each session learned and which rule shipped. | omp-kit Learning pillar; the next session's preflight |
| P7 | **Audit (repeatable)** | localbench's 7-question MISSION-AUDIT becomes a command: `pillars_checkable n/m`, unpillared beads, cadence jobs loaded vs written, close rule enforced Y/N, `br lint` count, `br dep cycles`, overlaps. Weekly, posted to each session's pane 1 and to Joshua. | weekly; Joshua |

## Cross-session awareness (separate projects, shared ground)

- `~/.agents/missions.toml` (or an omp-kit registry): one row per session with mission path, owner pane, the shared binaries it depends on, holds, no-upgrade windows and notify-before rules. uds already collected these 2026-10-04 into `uds/registries/upgrade_policy.toml` (omp-test, cfsios, localbench, jev); that becomes the seed.
- Overlap rule: when two missions claim the same ground, the owning session keeps it and the other narrows to a read-only check that points at the owner (agreed today: omp-kit JS1 → a read-only doctor finding pointing at uds).

## What this protocol is NOT

No new dashboards, no certificates, no per-session scorecard beyond the daily pillar-check row. No re-approval ritual: Joshua approves once per stage change. Any piece that gates nothing gets deleted at the weekly audit.

## Rollout (proposal)

1. Joshua approves this shape (edits welcome).
2. %54 (omp-kit) adopts it as kit law: `~/.agents/AGENTS.md` pointer + `skill://mission-protocol` + `omp-kit doctor --scope mission` + the `br create` pillar rule.
3. Each pane 1 writes its `.omp/mission.toml` from its approved mission and loads its daily/weekly jobs. uds will go first as the pilot, since its mission and audit already exist.
4. First weekly audit one week later; protocol v1 fixes whatever the audit shows doesn't work.

## v0.1 amendments (from reviews)

jev (protocol-jev.md): ACK, with these folded in.
- **P2:** a new bead may carry `pillar:triage` for up to 24 h; after that the weekly sweep parks it.
- **P3:** a REFUTATION or INVESTIGATION bead (its outcome is a finding, not a code change) may close on the landed sha of its investigation artifact (report/receipt committed to the repo) instead of a code sha. A grader PASS is still required.
- **P5:** each baseline tool is marked `shipped` or `pending` (e.g. push-own/LAND1 and `omp-kit doctor --scope mission` are pending); doctor treats a pending tool as a note, not a failure.
- **Add to P1:** a `blast_radius` field per mission (which shared binaries, paths and sessions this project can affect). Seeds the cross-session registry.
- **Add to P5:** br concurrency. The shared-tracker SYNC_CONFLICT (beads_rust#532) is a known hazard: no raw sqlite readers; latch auto-recover only when lsof shows no holder.
- **P2 DAG lint implementation:** adopt jev's `scripts/bead-lint.py` (offered) as the reference, instead of writing a new one.

omp-test %54 (protocol-omp-test.md): ACK the shape and omp-kit ownership. Folded in:
- **O1 (P1):** the mission record IS the `skill://charter` record (one per project, edited in place) plus the protocol fields (pillars with checks, cadence, not_in_mission, blast_radius, approval). There is no second convention.
- **O2 (P1/P4):** pillar `check` commands are repo code, so they run only after hash registration (canonical path + sha256, the same trust rule as watch specs and push checks), and they execute through `omp-kit heavy`. A changed check stays inactive until re-registered.
- **O3 (P3):** `.beads/policy.yaml` must be `strict: true` with explicit transitions, and gates on EVERY edge into `closed` (open, in_progress, grading, ...). Measured on br 0.7.4: without strict, open->closed and in_progress->closed bypass the gates, and uds's grading->closed is ungated. Each edge gets a planted-bypass test.
- **O4 (P2):** the refusing enforcement point for an unlabelled `br create` is br policy if it can require a label at creation; otherwise fleet-guard (a kit extension, tool_call -> block). Not a TTSR rule, which can only interrupt.
- **O5 (P5/P7):** one command: `omp-kit doctor --scope mission` IS the P7 audit. P5 checks installed + version only; use is measured by P7's cadence and DAG facts.
- **O6 (new):** each stage of each mission has ONE stage-exit bead that depends on the pillar beads; its acceptance = every pillar check green for N consecutive daily rows. That ties mission -> DAG mechanically.
- **Add (P5): dispatch-ack.** A dispatch counts only when the target pane starts a turn (spinner or turn event), not when `ntm send` returns 0 (omp-kit STEER1 rz5.90).
- **Add: ceremony bound.** Adopting the protocol must not stop product work past one sitting. Day one = P1 record + P2 labels + P3 strict policy only. P4-P7 ship as omp-kit beads (MP1-MP4 drafted by %54), each deleted at the weekly audit if it gates nothing.

Pending reviews: cfsios %53, localbench %55.

## APPROVED by Joshua, 2026-10-04 (relayed by jev pane 1)

Shape approved as agreed by all orchestrators, with this caveat, verbatim:

> "any failures that any sessions find get reported uphill, fixed foundationally, and applied to all repos through our omp-kit process"

**P6 amendment (binding):**
- **Reported uphill:** any failure a session finds goes to omp-kit (%54) as an omp-kit bead with evidence. That covers tool, gate, process and cross-repo failures. A local workaround alone is not enough.
- **Fixed foundationally:** omp-kit fixes it at the shared layer (a kit rule, hook, skill, template, script, or the upstream issue via zeststream-pr). It does not patch one repo at a time.
- **Applied to all repos:** the fix rolls out to every repo through the omp-kit process (kit install/update, `omp-kit doctor --scope mission` verifies it is loaded everywhere).
- A session's local mitigation may stand until the omp-kit fix lands; it is then removed in favour of the kit's version.

Example from 2026-10-04 that this covers: uds's `push-own-hunks.sh`, its rch completion-marker fix, the br SYNC_CONFLICT auto-recover in uds-tick-gate.sh, and the rch lease. Each is a local mitigation; each belongs in omp-kit (LAND1 rz5.86 for push-own; the rest to be filed by uds pane 1 as omp-kit beads).

# Pane 1 handoff, 2026-09-25 ~17:15Z (AmberWillow, conductor)

Written by pane 1 before Joshua restarts it. Read this, then `AGENTS.md` (RULE 15 is new today),
then resume the loop at "First ten minutes" below. HEAD at writing: `026d1230`. CI green on
`59808fc` (run 36164482100); nightly README stranger run green (36135948301).

## Who is who

| pane | tmux | agent (Agent Mail) | profile | bead(s) now |
|---|---|---|---|---|
| 1 | %18 | **AmberWillow** (you) | launched as `omp --auto-approve` | conductor: verify, dispatch, close |
| 2 | %26 | CopperHeron | claude | `jev-yru2` public command set (prereg stage) |
| 3 | %27 | IvoryCreek | codex | `jev-9gtw.4.2` page-text candidates (awaiting your check) |
| 4 | %32 | OrangeFrog | codex | `jev-jy7t.1.13` Emerald segment 2 (keyless design) |
| 5 | %29 | WindyLantern | codex | `jev-9gtw.4` MiniWoB held-out LIVE run in progress |

`resolve_pane_identity` is stale for %27 (says StormyCondor/MagentaRidge); the table above is
right. All panes 2-5 were restarted today after the rollout (`6b47a96`), so they have the review
extension, the Infisical key provider and secret redaction. `ReadmeStrangerRun` was a hub subagent
of pane 1 (README owner); it dies with this session; re-spawn a README owner when a result needs
the README (it must keep stages 15/95/97, readme-gate and the claim-coverage floor; README is
54,824 B, 48 B under the limit, coverage 114/115 = floor, so text must be replaced, not added).

## Do first (pending on you)

1. **`jev-9gtw.4.2`** (IvoryCreek): checked `026d1230` at ~17:20Z, DEFECT (bead comment):
   `build_candidates` inserted `derive_needed_text` (the answer) at position 0, so coverage was
   1.000 by construction. Without it the generic builder covers 4 of 5 captured tasks
   (text-transform not covered). Pane 3 is fixing: builder never reads the grader; generic
   adjacent-character rule; a test that output is unchanged with the grader patched to raise;
   20 no-model observations per page-text task; request size. Verify its next commit the same
   way (remove the grader from reach, recount coverage and needed-string index yourself).
2. **`jev-yru2`** (CopperHeron): prereg NAME-GAP resolved and extract verified at ~17:25Z
   (`20f99ed3`, `bfc19b43`): cohort frozen as a rule, MIT-only with per-file license evidence,
   10 target-shape rows (4 from one repo), thresholds PROPOSED. Next from pane 2: two blind label
   files, then you adjudicate the disagreements. Live readiness needs 10 target-HARM rows, so one
   no-harm label makes it UNDERPOWERED; that is an acceptable reported outcome.
3. **MiniWoB held-out run** (pane 5): pids 30607/30641, `run-after-rotation.sh --live --steps
   combined`, arms `quoted,none,color` (from `work/miniwob-jev/v3-combined-arm-list.txt`), run root
   under `var/agent-tmp/`. Do not touch it. When it lands: recount rows, check keys equal the
   prereg held-out set, model `jev-1.13.0`, code hashes (note: rows hash jev_arm.py, not run.py;
   gap recorded), then McNemar vs v1 on the same keys as preregistered.

## Waiting on Joshua (ask once, do not act)

- `work/gate-question-gap/extract-5.jsonl` (55d30a4) and `extract-5-extension.jsonl` (f3f544f):
  raw session commands published to the public repo by pane 2. Scanned: 0 credential-shaped
  spans, 0 PRIVATE matches. Options: leave, delete from tree, or scrub history (force push).
  Do not delete without his word (RULE 1).
- `/never-give-up` skill location (bead `jev-vbh.5`); not found on grokbot, ~/.grok, Brain, GitHub.
- PokéJev on the public Showdown server needs a bot account (`jev-jy7t.1.10`).
- Foundry / franken-harvest bugs live in his other repos (blocked beads `jev-foundry-*`, `jev-route-*`,
  `jev-stampcheck-*`).

## Today's results (all non-author checked; cite these, not memory)

- **Key rotated 13:14Z**; `scripts/key-status.py` says OK. Leaked key fingerprint in
  `scripts/key-revoked.tsv`. Panes have no key in their env; omp tools/extensions fetch it from
  Infisical in-process (`work/jev-client/src/infisical-key.ts`, 10-min cache).
- **OSWorld Best-of-N** (`jev-9gtw.2`, closed, R112): lost to best single archive on 337 tasks
  (296.4 vs 303.4, McNemar p=0.109); 12 max_tokens_exceeded refusals were 71% of the loss.
- **Usage router** (`jev-vbh.4`, closed, R111): short web goals 13/19 < 0.833 bar; stays shadow.
- **Diff reviewer** (`jev-k9z.2`, closed): advisory line at boundary >= 0.9; loads in every session
  (`.omp/extensions/jev-review.ts`); compound git commands are not-applicable (`1eb4bf1`).
- **Gate-question pass** (`jev-pvdp`, closed, R113): UNDERPOWERED, 1 target row in 3,838 fleet
  commands (0.156/hour); retry via public set = `jev-yru2`.
- **Emerald segment 1** (`jev-jy7t.1.12`, closed): Jev 80/80 median 62; random 26/33 at 271;
  state-blind (Jev's pooled button frequencies, Docker `24d9ffff`) 80/80 at 67. Gain is mostly
  the button prior. README "Where Jev lost" has it (`283aa72a`). Segment 2 = `jev-jy7t.1.13`.
- **MiniWoB v3 isolated arms** (`47b1eb9`): quoted 16/16 PASS, none 8/11 PASS, date_time 5/10
  dev-only, page_text 10/35 FAIL, drag 12/87 FAIL; colour 0/12 was a harness bug (read `color`,
  MiniWoB has `bg_color`), rerun 8/12 = PASS line exactly (`858e0cc6`, `00b213e3`).
- **Tools built today**: `scripts/jev-state-size.py` (32k limit, band from billed tokens; FITS
  324/NEAR 10/OVER 3 on OSWorld), `row-provenance-check.py` now fails a non-JSON first line and
  checks answer rows, fleet line `Jev tools 24h:` (surface-census), nightly stranger line in
  `ci-main-status.py`, `.omp/skills/jev-tools/SKILL.md`. `jev-ja32` closed: no real-work consumer
  for the four omp Jev tools; HOLD on new Jev omp tools until one has a consumer. The fleet line
  says "every tool called" but those calls were rollout/smoke tests, not organic use.
- **AGENTS.md RULE 15** (Joshua: "derive test patterns instead of creating them"): fixtures
  captured not typed; assert effects; every bar names EXTERNAL/INCUMBENT/ARITHMETIC/DOCS or is
  PROPOSED; feasibility before spend. Audit `1de0f39`: 45 bars, 32 UNSOURCED, 0 EXTERNAL.
  External MiniWoB rates now in `work/miniwob-jev/external-rates.tsv` (CC-Net Table 3, tested).

## The loop (what pane 1 does every tick)

```bash
cd /Users/josh/Developer/jev && git fetch -q origin main && git merge -q --ff-only origin/main
br sync --import-only; br ready --json            # claim the highest bead you did NOT author
python3 scripts/ci-main-status.py                  # CI + nightly stranger line
JEV_WATCH_PANES=2,3,4,5 JEV_WATCH_INBOX_ROOT=/nonexistent python3 scripts/fleet-idle-watch.py --once
```

- Joshua's standing prompt: "Mission: validate Jev, build tools from what survives, liven an omp
  surface, dogfood it, keep the README a stranger can run... Claim the highest you did not author."
  When every ready bead is yours and assigned, verify pane work, unblock, and dispatch.
- **Verify as non-author** in a fresh `git clone --local` under /tmp: run the test, plant 1-3
  defects (each must fail a test), restore byte-identical (`cmp`), recount numbers from rows with
  your own code. Close with a VERDICT reason naming commits; never a placeholder reason.
- **Dispatch**: `ntm send jev --pane=N '...'` (one line, ~1 KB ok); file beads with WHAT/WHY/
  ACCEPTANCE, `--actor AmberWillow`, assign the pane's agent name.
- **Commits**: stage explicit paths, `git commit --only ... -- <paths>`, subject names a level
  (`[pending]`/`[test]`/`[mutation]`/`[live]`); bead store: `br sync --flush-only` then commit
  `.beads/issues.jsonl` alone. Before pushing, `git log origin/main..main` and look at other panes'
  commits (raw session text must never go public).
- **Shared files** (`TESTS.md`, `EVAL.md`, `NEGATIVE_EVIDENCE.md`, bead store): reserve only for
  the seconds of the edit (Agent Mail MCP `file_reservation_paths` / `release_file_reservations`,
  or `am file_reservations reserve|release ~/Developer/jev AmberWillow <paths>`); ask holders by ntm
  to release. `TESTS.md` Run: commands must be on one line (runner parses them); stage 70
  (`foundation/gates.d/70-tests-registry-sync.sh`) fails on unregistered tests.
- **Restarting a pane** (Joshua authorized rollout restarts): only at a unit boundary; Escape,
  `/exit`, then `cd /Users/josh/Developer/jev && omp --profile <codex|claude>`, then ntm the pane its
  identity, bead and next step.
- **Supervised processes** (`hub ps`): `fleet-idle-watch` (restart after watcher/census code
  changes with `hub op:restart name:fleet-idle-watch`), `p2-mailmon`, `p3-mailmon`.
- **Live spend is approved** (Joshua, 2026-09-21), but only after a verified prereg and a
  feasibility check: key via `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --`,
  `scripts/key-status.py` first, stop on 401/402.

## Traps that cost time today (do not repeat)

- A check that passes only on this Mac: hide local venvs (`/tmp/jev-miniwob-jev/venv`) and
  untracked clones before closing; CI runners have neither.
- A `--fake` path that differs from `--live` proves nothing; drive the live path with a stub.
- Release a held-out/combined step only after reading the dev gates it depends on.
- A results file where every row has `child_error` / null `final` is a crash, not a result.
- A pane blocked inside a long foreground command cannot read steering; interrupt it (SIGINT to
  the run, not the pane) if a wrong run must stop.
- `br close` with a placeholder reason sticks; reopen and close again if it happens.
- Never print the key; key checks compare fingerprints (`/tmp/keyreal.py`-style, paths only).

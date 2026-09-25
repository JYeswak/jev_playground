# Pane 1 handoff: restart document (2026-09-25, written ~17:35Z)

You are **AmberWillow**, pane 1 (tmux `%18`), the conductor of the `jev` NTM session. Joshua
restarted every pane after ordering the fleet quiet. This file is everything you need to pick the
work back up. Read it top to bottom once, then `AGENTS.md` (RULE 15 is new today, and RULE 0:
Joshua's word overrides everything). Then do "First actions".

State at writing: HEAD `e660d5c4`. CI was RED at `f7fb6c7` (two tests unregistered);
`e660d5c4` registers them, so the next CI run should be green; confirm it. The nightly README
stranger run last passed as run 36135948301. No pane has a running process, and no live (paid)
run is in progress.

## First actions, in order

1. Sync and look:
   ```bash
   cd /Users/josh/Developer/jev && git fetch -q origin main && git merge -q --ff-only origin/main
   br sync --import-only; br ready --json
   python3 scripts/ci-main-status.py
   JEV_WATCH_PANES=2,3,4,5 JEV_WATCH_INBOX_ROOT=/nonexistent python3 scripts/fleet-idle-watch.py --once
   ```
2. **Ask Joshua whether the quiet order is lifted** before sending any unit. He said: "let all
   agents go quiet - dont dispatch anymore. once project is quiet we'll restart all panes after a
   proper handoff is written." Do not assume the restart ended the quiet order.
3. When he lifts it, send each worker pane one ntm message: its agent name, its handoff path, "read
   AGENTS.md RULE 15 first", and the next step from the table below. Panes 3-5 restarted at
   17:26:54-17:27:14Z and have **not** yet been told who they are. `resolve_pane_identity` is stale
   for `%27` (it answers StormyCondor or MagentaRidge); the table below is right.
4. Verify the first commit each pane sends, as non-author (method under "How pane 1 works").

## The fleet

| pane | tmux | agent | launch (from repo root) | handoff | resume with |
|---|---|---|---|---|---|
| 1 | %18 | AmberWillow (you) | `omp --auto-approve` | this file | conductor |
| 2 | %26 | CopperHeron | `omp --profile claude` | `notes/deep/dispatch/HANDOFF-CopperHeron-20250925.md` (`3de3a195`, `7a72bad3`) | `jev-yru2` labels |
| 3 | %27 | IvoryCreek | `omp --profile codex` | `notes/deep/dispatch/HANDOFF-IvoryCreek-20250925.md` (`95435c5f`) | `jev-9gtw.4.2` fix |
| 4 | %32 | OrangeFrog | `omp --profile codex` | `notes/deep/dispatch/HANDOFF-OrangeFrog-20250925.md` (`eac40895`) | `jev-jy7t.1.13` baselines |
| 5 | %29 | WindyLantern | `omp --profile codex` | `notes/deep/dispatch/HANDOFF-WindyLantern-20260925.md` (`d4c94471`) | `jev-9gtw.4` held-out relaunch |

Three handoff file names say 2025; they are today's. Corrections to them, found when pane 1
read them:
- CopperHeron's "uncommitted `label_prompt.md`" was committed in `3de3a195`.
- IvoryCreek's "jev-ja32 reopened, do not close" is out of date: pane 1 closed `jev-ja32` on the
  no-consumer outcome (see results).
- WindyLantern's run is no longer running (next section).

Helpers that survive restarts (`hub ps`): `fleet-idle-watch` (restart it after changes to
`scripts/fleet-idle-watch.py` or `work/omp-jev-review/surface-census.py`), `p2-mailmon`,
`p3-mailmon`. `ReadmeStrangerRun` (the README owner) was a hub helper of the old pane 1 and is
gone. Re-create one when a result needs the README. It must keep stages 15/95/97, readme-gate
and the claim-coverage floor. README is 54,824 B (48 B under the limit), and claim coverage is
114/115, the floor. So new text replaces old text.

## Per bead: exactly where each unit stopped

**`jev-9gtw.4` (WindyLantern): MiniWoB v3, P1.**
- Isolated arms are verified (`47b1eb9`): quoted 16/16 PASS, none 8/11 PASS, date_time 5/10
  dev-only, page_text 10/35 FAIL, drag 12/87 FAIL. Colour's 0/12 was a harness bug (it read
  `color`; MiniWoB provides `bg_color`/`fg_color`). The rerun scored 8/12, exactly the PASS line
  (`858e0cc6`, `00b213e3`).
- The combined held-out arm list is `quoted,none,color` (`work/miniwob-jev/v3-combined-arm-list.txt`).
  Comma arms were fixed at `7ff8dac`; the arm-list test at `e65f2cdb`.
- **The held-out live run ended when pane 5 was restarted** (it was a child of pane 5's omp).
  Run root `var/agent-tmp/jev-9gtw-heldout-live-rerun.3921/`:
  - Keyless baseline complete: 1,250 rows.
  - Paid phase: 20 of 625 rows, 17:25:15Z to 17:27:03Z. 131 Jev calls, 1,021,276 input tokens,
    all `jev-1.13.0`, code_sha256 `9909a066`.
  - The rows are in `work/miniwob-jev/rows/miniwob-jev-v3-heldout.s0.jsonl`, untracked, sha256
    `b424d191...`.
  - NOT SCORED: a partial set is never scored.
- **Next:** relaunch with `hub op:start` (persist), never inside a pane's own shell, so a restart
  cannot kill it. Before relaunching:
  - The sheet refuses an existing held-out label file unless `--resume`
    (`run-after-rotation.sh:134`). Decide in a committed note: resume the 20 rows (same code sha,
    model and arms), or start fresh by moving the file aside. Never delete it (RULE 1).
  - The combined step always recomputes baselines (`run-after-rotation.sh:141`, about 50 min
    keyless) unless changed.
  - Then run it through `infisical run ... work/miniwob-jev/run-after-rotation.sh --live --steps
    combined --run-root <root> [--resume]`. Spend is approved.
- When it completes, check each of these yourself:
  - the keys equal the prereg held-out set;
  - `jev-1.13.0` on every row;
  - hashes, noting the gap that rows hash `jev_arm.py`, not `game-floors/miniwob/run.py`;
  - McNemar against v1 on the same keys, as preregistered.

**`jev-9gtw.4.2` (IvoryCreek): page-text candidates, P2.**
- `026d1230` is DEFECTIVE: `build_candidates` inserted the grader's answer (`derive_needed_text`)
  at index 0, so coverage was 1.000 by construction.
- Without that, the generic builder covered 4 of 5 captured tasks. text-transform was not covered.
- A fix is in IvoryCreek's working tree, uncommitted: `work/miniwob-jev/text_candidates.py` and
  `test_text_candidates.py`. Its handoff lists them.
- Still to do:
  - a test that the output is unchanged when the grader is patched to raise;
  - a generic rule for adjacent single-character spans;
  - 20 no-model observations per page-text task (captured through a separate scratch root);
  - coverage and median index of the needed string;
  - request size via `scripts/jev-state-size.py`.
- Registered in `TESTS.md` with the defect stated. **Verify:** keep the grader out of reach and
  recount coverage yourself.
- Do not let anyone edit `jev_arm.py` or `run.py` while a MiniWoB live run is alive.

**`jev-yru2` (CopperHeron): public command set for the gate-question retry, P2.**
- Prereg `b3cfcece`. Repo cohort frozen as a rule: `topic:github-actions` top 10 by stars at
  17:01:59Z (`20f99ed3`). Extract `5b368355` (bfc19b43 superseded: duplicate row ids).
- 7 MIT repos, 3 excluded for no license. 110 rows = 10 target-shape + 100 seeded non-target.
  4 of the target rows come from one repo. States all FITS.
- Thresholds 70% / +5 / +2.0 pp are PROPOSED (descriptive only).
- Label prompt `work/jev-yru2-public/label_prompt.md`. Labeller A was started around 17:20Z and
  stopped unfinished; no label file exists.
- **Next:** two blind labellers, with the concrete model ids recorded (not just the aliases
  `smol`/`slow`). Then pane 1 adjudicates the disagreements.
- Live readiness needs 10 target-HARM rows. With exactly 10 target-shape rows, one no-harm label
  means UNDERPOWERED, and that is an acceptable reported outcome. No live call in this unit.

**`jev-jy7t.1.13` (OrangeFrog): Emerald segment 2, P2.**
- Code and prereg at `31169ec4`. Segment from recorded rows 299/303 of `states/emerald-boot.jsonl`:
  alternating x=1/x=2 starts, goal is a position change, cap 50.
- Baselines: uniform, and state-blind with segment-1 frequencies. `live_segment.py` receipt now
  writes `key_status`.
- The first Docker run was refused (all 80 invalid: seed-1 drift). Fixed by trace replay; the
  seed-1 smoke passed. The full 160-episode Docker run has NOT been run. UBS final status is
  pending.
- **Next:** UBS, then both 80-seed policies in the pinned `jev-pokeagent-runtime:20260925` image,
  then `jev-state-size.py`, then `power_mwu.py --control-policy state_blind --cap 50
  --fixed-control`, then commit.
- Acceptance requires the state-blind policy to fail on this goal (goal rate < 50%, or median at
  least 2x Jev's segment-1 median). Otherwise pick another segment and say why.
- `test_segment2_baselines.py` is not yet non-author verified.

Other open beads (not active): `jev-3e2i` and `jev-jy7t.1.4` (CopperHeron, parked), `jev-k9z`,
`jev-9gtw`, `jev-jy7t`, `jev-jy7t.1` (parents, pane 1), `jev-1yqu` (upstream issue #45, no
maintainer reply), `jev-oxdq` (josh), and the blocked set in "Waiting on Joshua".

## Waiting on Joshua (ask once each, do not act)

1. **Is the quiet order lifted?** (First actions, step 2.)
2. Two raw session-command files that pane 2 published to the public repo:
   `work/gate-question-gap/extract-5.jsonl` (`55d30a4`) and `extract-5-extension.jsonl`
   (`f3f544f`). Scanned: 0 credential-shaped spans, 0 PRIVATE matches. The choices are to leave
   them, delete them from the tree, or scrub history (force push). Never delete without his word.
3. Where `/never-give-up` lives (`jev-vbh.5`). It was not on grokbot, `~/.grok`, Brain, or GitHub.
4. A Showdown bot account (`jev-jy7t.1.10`), and fixes in his other repos (the `jev-foundry-*`,
   `jev-route-*` and `jev-stampcheck-*` blocked beads).

## What is true today (cite these, not memory)

- **Key** rotated 13:14Z; `scripts/key-status.py` says OK.
  - The leaked key's fingerprint is in `scripts/key-revoked.tsv`; runners refuse it.
  - Panes have no key in their environment. omp tools and extensions fetch it from Infisical in
    memory (`work/jev-client/src/infisical-key.ts`, 10-min cache, `6b47a96`).
  - Live scripts use `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --`.
- **Rollout** (Joshua: "roll out all features to every pane"): every session loads the four Jev
  tools (`jev_rerank`, `jev_claim_check`, `jev_flag`, `jev_screen`) and the diff reviewer
  (`.omp/extensions/jev-review.ts`). The reviewer adds one advisory line at boundary >= 0.9 and
  never blocks; compound git commands are not-applicable (`1eb4bf1`).
- **`jev-ja32` closed:** no real-work step calls any of the four tools; every recorded call was a
  test. HOLD on new Jev omp tools until one has a consumer. The fleet line "every tool called"
  counts those test calls.
- **Losses and non-results, each with a NEGATIVE_EVIDENCE row:**
  - Usage router R111: short web goals 13/19 < 0.833, stays shadow.
  - OSWorld Best-of-N R112: 296.4 vs 303.4 on 337 tasks, p=0.109. 12 over-limit refusals were
    71% of the loss.
  - Gate-question R113: 1 target row in 3,838 fleet commands, UNDERPOWERED.
- **Emerald segment 1** (`jev-jy7t.1.12`, closed):
  - Jev 80/80, median 62 macros.
  - Random 26/33, median 271.
  - State-blind with Jev's own button frequencies 80/80, median 67 (Docker `24d9ffff`).
  - So the gain is mostly the button prior. In README "Where Jev lost" (`283aa72a`).
- **Tools built today:**
  - `scripts/jev-state-size.py`: 32k documented limit, band from 325 billed calls. On OSWorld:
    FITS 324 / NEAR 10 / OVER 3, and one answered request was NEAR, so no uniform NEAR rule works.
  - `scripts/row-provenance-check.py`: fails a non-JSON first line; checks answer rows.
  - `scripts/key-status.py`.
  - The fleet-line additions (Jev tools 24h, key exposure, nightly stranger status).
  - `.omp/skills/jev-tools/SKILL.md`.
  - `work/miniwob-jev/external-rates.tsv`: CC-Net Table 3 human, CC-Net and aggregated-SotA
    rates, tested against the PDF.
- **AGENTS.md RULE 15** (Joshua: "derive the test patterns instead of creating them (making shit
  up)"):
  - Fixtures are captured, never typed.
  - Tests assert effects, not inputs.
  - Every bar is EXTERNAL / INCUMBENT / ARITHMETIC / DOCS, or it is PROPOSED and cannot gate.
  - Feasibility comes before spend: the solving action is offered, and the request fits the limit.
  - Audit `1de0f39`: of 45 bars, 32 are UNSOURCED and 0 EXTERNAL.

## How pane 1 works (the loop)

- **Joshua's standing prompt:** "Mission: validate Jev, build tools from what survives, liven an
  omp surface, dogfood it, keep the README a stranger can run... Claim the highest you did not
  author."
  - If a ready bead exists that you did not write, claim it.
  - Otherwise verify pane work, unblock, and dispatch. Dispatch only if not under a quiet order.
- **Non-author verification**, every time a pane sends a sha:
  - Work in `git clone --local /Users/josh/Developer/jev /tmp/<x>`.
  - Run the test. Plant 1-3 defects, each of which must fail a test. Restore byte-identical
    (`cmp`).
  - Recount the headline numbers from the rows with your own code.
  - Hide local-only venvs and untracked clones when a test could depend on them.
  - Record the result on the bead. Close only with a VERDICT reason that names commits.
- **Dispatch:**
  - `ntm send jev --pane=N '<one line>'`.
  - File beads with WHAT/WHY/ACCEPTANCE, `--actor AmberWillow`, assignee set to the agent name.
  - Every packet names the mission stage, the tools, and the acceptance shape (AGENTS.md "Every
    dispatch packet").
- **Commits:**
  - Stage explicit paths; use `git commit -q --only -m "[level] ..." -- <paths>`. Levels are
    pending, test, mutation, live and oracle.
  - For the bead store: `br sync --flush-only`, then commit `.beads/issues.jsonl` alone.
  - Before pushing, read `git log origin/main..main` and check other panes' commits. Raw session
    text must never be pushed.
- **Shared files** (`TESTS.md`, `EVAL.md`, `NEGATIVE_EVIDENCE.md`, the bead store):
  - Reserve only for the seconds of the edit: Agent Mail MCP `file_reservation_paths` /
    `release_file_reservations`, or `am file_reservations reserve|release ~/Developer/jev
    AmberWillow <paths>`.
  - Ask holders by ntm to release. Holders who sleep until a lease expires are a known failure.
  - Every `TESTS.md` `Run:` command must be on one line.
  - Stage 70 fails CI on any unregistered test. After a pane adds a test, check
    `bash foundation/gates.d/70-tests-registry-sync.sh`.
- **Restarting a pane:** only at a unit boundary, and never while it hosts a live run. Send Escape,
  then `/exit`, then `cd /Users/josh/Developer/jev && omp --profile <p>`. Then ntm the pane its
  identity and next step.
- **Live spend is approved** (Joshua, 2026-09-21), but only after a non-author-verified prereg and
  a keyless feasibility check. Run `scripts/key-status.py` first; stop on 401/402; run as a
  supervised process.

## Traps that cost time today

- A check that passes only on this Mac. CI runners have no `/tmp/jev-miniwob-jev/venv` and no
  untracked clones.
- A `--fake` path that differs from `--live`. Drive the live path with a stub runner.
- A test that asserts the value passed in rather than its effect (the comma arm list).
- A fixture typed by hand (colour `"color": "red"`).
- A grader leaking into the thing it grades (`derive_needed_text`).
- A combined or held-out step released before its dev gates were read.
- Rows with `child_error` / null `final` treated as a result. That is a crash, not a result.
- A long run launched inside a pane's own shell. A pane restart kills it, as happened to the
  MiniWoB held-out run at 20/625.
- A pane blocked inside a foreground command cannot read steering. Interrupt the run (SIGINT to
  its pid), not the pane.
- `br close` with a placeholder reason is permanent until reopened.
- Never print the key. Key checks compare fingerprints, and scans print paths only.

## Tracked files modified in the shared tree with no owner in any handoff

Leave these alone: no staging, reverting or stashing. Ask the restarted panes whether any is
theirs:

- `ARC.md`
- `docs/demos/tick.md`
- `docs/demos/upstream-repro/loss-depth-pokejev-20260925.md`
- `notes/deep/next-gen/BRIEF.md`
- `notes/deep/omp-kit-load-census.tsv`
- `notes/deep/omp-kit-upstream-proofs.md`
- `upstream/MANIFEST.tsv`
- `work/jev-question-writing/w74-oof-auroc.py`
- `work/loss-depth/pokejev/autopsy.py`
- `work/nev-differential/DIFF-RECEIPT.json`
- `work/nev-differential/PREREGISTER-DIFF.md`
- `work/nev-injection/INSTALL-RECEIPT.txt`
- `work/nev-routing/tool-select-derived.json`
- `work/nev-routing/tool-select-extract.json`
- `work/poke-jev/stage-b/receipt.json`
- `work/skill-routing/pairs.jsonl`

Also IvoryCreek's two, listed above, and about 167 untracked paths.

# Roadmap

This file is jev's plan of record. `AGENTS.md` and `work/plan-20261004/PRODUCT.md` link here; when
they disagree, this file wins. The machine-readable form is `.omp/mission.toml`, kept equal to this file's pillar
table by `scripts/mission-sync.py --check` (converge r4 mission-sync bead). Mission Protocol v0.1 is
owned by omp-kit; its text is untracked and gitignored in uds
(`var/agent-tmp/gaps/missions/MISSION-PROTOCOL.md`), so it is pinned here by content, sha256
`229b45bad8c37626d1ba62391cf1a7a9e75bcb346ec4c0ce0df8fad1f1d23672` (2026-10-05), until omp-kit
commits it; a byte-identical copy is committed at `work/plan-20261004/MISSION-PROTOCOL.md`.

## Mission (approved by Joshua, 2026-10-04)

**Typed classifiers that earn their place in our tools: each one proven live, measured, and delivered
through one model-neutral CLI (`classifier`) that makes the next one cheap.**

Approval, verbatim: *"yes i like c"* (mission C, 2026-10-04). Protocol shape approved the same day:
*"i approve the shape that all agent orchs agree on, with a caviet that any failures that any
sessions find get reported uphill, fixed foundationally, and applied to all repos through our
omp-kit process"*. Supersedes the 2026-09-30 mission line ("Turn Jev ON in the tools we use and
prove it live"), which pillar 1 keeps.

### Pillars

Each pillar names the command that checks it. `status` is today's truth, not a promise.

| # | Pillar | Clause | Check | Today | Owning beads |
|---|---|---|---|---|---|
| 1 | **Live** | Every claimed surface is ON in a real omp session: it fires on a positive and stays silent on a planted negative in a fresh `omp --mode=rpc` session. | `classifier doctor --json`: exits non-zero when any claimed-ON surface lacks a fresh both-ways L3 receipt in `work/l3-receipts/receipts.jsonl` (`jev-grzn`; doctor side: converge r4 `jev-b35c.30`) | PARTIAL: `python3 work/omp-jev-review/surface-census.py --scoreboard --days 7` proves calls, not both-ways receipts | `jev-grzn` (L3 receipts), `jev-b35c.3`, `jev-b35c.30`, ship-winner `jev-c710` (other ship-winner beads are listed under their family's pillar), `pillar:live` |
| 2 | **Measured** | Every live surface has a value-minus-cost receipt from our own session logs (tokens saved, harms caught, turns rescued, minus Jev/Clef spend and latency). A negative result turns the surface off. | `python3 work/jev-mvvh/ledger.py --gate --days 7`: exits non-zero on any UNMEASURED surface or any KILL verdict still ON | MISSING | `jev-mvvh`; family bake-offs `jev-n1-result-family-bakeoff-fcqw`, `jev-n2-reread-dedup-rule-i817`, `jev-c3vl` (route episodes + labels), `jev-n3-route-locate-bakeoff-4xnz` (route bake-off), `jev-n4-recover-error-rule-1grh`, `jev-n6-outcome-logging-vfnv`, `jev-n7-pin-compaction-files-k0gu`, `jev-n8-delegate-outcome-label-umcw`, `jev-n9-nudge-actionability-4471`, `jev-x4-vendored-probe-closeout-82p7`, `jev-x8-memory-relevant-drop-enn9`; ship-winners `jev-sxi2`, `jev-ayly`, `jev-dq7p`, `jev-sm2f`, `jev-7o58`, `jev-2af1`, `jev-np5k`, `jev-jm1n`, `jev-pn19`, `jev-x3su`; `pillar:measured` |
| 3 | **Honest** | Every quality claim has its bar committed before the first live call, an incumbent on the same rows, N, date, model id and spend. | `python3 scripts/bar_chronology.py --since 2026-09-24 --json --strict` (`jev-6gun`: bar before first call, plus incumbent, row-set hash, N, date, model id and spend on every result row); `python3 scripts/bead-lint.py --all-open` stays as the plan-quality lint | PARTIAL: no check that the bar predates the first call, or that result rows carry incumbent, N, model id and spend, until `jev-6gun` lands | `jev-6gun`, `jev-oh7c`; build-freeze gate `jev-convergence-gate-g57u`; miner `jev-n0-fleet-decision-miner-sclo`; conformance harness `jev-conformance-harness-acs2`; metamorphic `jev-metamorphic-label-pending-uvi5`; `jev-n5-land-failure-classes-uphill-az20`, `jev-n10-review-rules-incumbent-xqx8`, `jev-x7-gate-rules-closeout-9td0`; ship-winners `jev-pifg`, `jev-8i8i`; `pillar:honest` |
| 4 | **Local-first** | Clef serves a family only where a committed receipt shows it non-inferior to Jev within a preregistered margin under the same calibration; otherwise Jev. Clef runs through localbench's gateway (localbench kit-jtq2, tracked by a jev bead); if that gateway is not delivered, Clef stays out of stage 1 and every family keeps Jev or its rule incumbent. Stage 1 measures Clef-Flash on the gate and screen family suites only (X2); other families keep Jev or their rule/encoder winner, and full Clef (51 GB) is DROPPED from stage 1 (jev-52s0 records the decision and its provenance). | `classifier backend audit --json`: exits non-zero when any family routes to Clef without a committed non-inferiority receipt | MISSING: no router; Clef-Flash serves on `:8010` from an untracked throwaway `serve.py` (`work/plan-20261004/specs/clef-backend-spec.md` F5) and full Clef (51 GB) is on disk at `/Volumes/ZestData/models/cloudflare/clef/` (download done 18:10Z); neither is measured on the family suites; full Clef's exit (DROP) is `jev-52s0`, and localbench's gateway kit-jtq2 is tracked by `jev-k3yw` | `jev-b35c.4`, `jev-x1-injection-encoders-e2gp`, `jev-x2-clef-four-suites-3rbd` (gate + screen suites), `jev-x3-factcheck-encoders-s28q`, `jev-x6-intent-encoder-0u9a` (locate arms on `jev-c3vl`'s labels), `jev-oy76` (serve.py lifecycle, gateway registration), `jev-52s0`, `jev-k3yw`, ship-winner `jev-d7tn`, `pillar:local-first` |
| 5 | **Portable** | A stranger runs the README from a fresh clone, and `classifier ready` plus one family run in a project we did not write. | the last 7 `schedule` runs of `.github/workflows/stranger-run.yml` all green (`gh run list --workflow stranger-run.yml --event schedule --limit 7`; manual reruns counted separately, never filling a failed day); `classifier ready <dir>` | PARTIAL: 5 of the last 7 scheduled stranger-runs green (2026-09-29 to 2026-10-05); 2026-10-01 and 2026-10-03 failed and were rescued by manual `workflow_dispatch` reruns, which do not count. The lane is keyless and uses `--fake`: it proves the README's offline commands run, not a live classifier decision. `classifier ready` not built | `jev-r1vp` (stranger adopts), `jev-b35c.7`, `pillar:portable` |
| 6 | **Current** | What is declared ON is what is running: no switch, hook or log that says one thing while the machine does another. | `classifier doctor --json` drift section: exits non-zero on any declared-vs-running mismatch | MISSING: the kit's `npx --prefix kit --no-install jev doctor --robot` says `NOT_RUN`/"no key" while hooks run with a key (plain `jev` on PATH is Hermes 0.19.0, not ours) | `jev-b35c.3`, `jev-35sg`, `pillar:current` |

### Done for a feature

Live in a real session both ways, a value receipt, and a non-author re-ran its acceptance, with the
commit on `origin/main`. A refutation closes on its committed investigation artifact instead of a
code commit. Enforced by `.beads/policy.yaml` (strict workflow: every edge into `closed` needs a
non-author reviewer gate, no self-close, a `commit:` or `investigation:` reference). `br` checks
only that the reference is present. Until omp-kit MP3 (`ompkit-rc-epic-land-fix-release-dogfood-rz5.95`)
enforces more, `scripts/close-ref-check.py` (converge r4 close-ref bead) checks every close: a
`commit:<sha>` must be an ancestor of `origin/main` (`git merge-base --is-ancestor`), and an
`investigation:` reference must name a path tracked in git on `origin/main`, not a bead id or a
gitignored file.

### Cadence

| When | What | Runs as | Today |
|---|---|---|---|
| Daily | Stranger-run of the README | GitHub Actions `stranger-run.yml`, 03:17 UTC | runs: 5 of the last 7 scheduled runs green, 2026-09-29 to 2026-10-05 (`gh run list --workflow stranger-run.yml --event schedule`); keyless `--fake` lane |
| Daily | `jev-latest` canary against the pinned `jev-1.13.0` | launchd `ai.zeststream.jev-latest-canary`, 09:07 | runs |
| Daily | Every pillar check, one scoreboard row | omp-kit MP5 `ompkit-rc-epic-land-fix-release-dogfood-rz5.97` | NOT RUNNING: open in omp-kit; jev side `jev-2b7f` |
| Daily | Fleet watcher pages pane 1 on idle, needs-human, CI red; nudges undelivered omp steering messages | `scripts/fleet-idle-watch.py` | runs (restarted 2026-10-05T15:55Z after the 2026-10-04 overnight pause) |
| Weekly | Value-ledger review: keep, kill or promote each surface; mission audit | omp-kit MP2 `ompkit-rc-epic-land-fix-release-dogfood-rz5.94` (`doctor --scope mission`) | NOT RUNNING: open in omp-kit; jev side `jev-2b7f` |
| Long-term | The sixteen decision families (`work/plan-20261004/PRODUCT.md` section 8) each live, shipped as code, refuted or dropped with evidence; Clef the default only where it is non-inferior; `classifier` adoptable by another repo in under an hour | stage-exit bead `jev-uzq1` | open |

### Not in the mission

Benchmark tourism; certificates, ledgers or dashboards with no consumer; games, computer use,
trading; paid comparator models; a family without a host tool; audits of our own docs (one named
exception: the convergence gate `jev-convergence-gate-g57u` reviews the bead plan before builds; a
round cap is PROPOSED, pending Joshua, with no gate effect: ask him after round 7 whether to release
the freeze); fleet plumbing that omp-kit owns (git writers, idle dispatch, index locks).

### Neighbours (same rigor, separate scopes)

| Ground | Owner |
|---|---|
| Local models, GPU, serving, arbitration, attribution | localbench (%55) |
| OMP, rules, fleet layer, machine load, pause/resume + dispatch-ack protocol, the Mission Protocol | omp-kit (omp-test %54) |
| Dicklesworthstone binaries | uds (conductor `control-plane:%57`) |
| Jev surfaces, the `classifier` CLI, decision logic, labels and quality bars | jev (pane 1) |

- **Failures go uphill.** A failure any jev agent finds in shared tooling is reported to omp-kit
  (%54), fixed at the foundation, and rolled to every repo through omp-kit. No local-only patch of a
  shared defect.
- **Blast radius.** Any jev surface installed outside this repo (omp extension, hook, rule) has a
  latency budget under omp's handler limits, never holds the host turn, takes the safe side its
  decision contract declares when the classifier is down, slow or capped (a result or memory screen
  passes the result; a command gate may refuse the call when the classifier is down or slow, and at
  its daily cap passes the call with a log unless a committed bar shows a session's normal volume
  never reaches the cap), and has an off switch the host session's pane 1 may use
  without asking. It also declares what data leaves: per surface, the data class sent, the recipient,
  the repos it loads in, retention of local sidecars, and owner consent (`jev-p15`'s inventory,
  checked by `classifier doctor`). Incident: the memory filter hit omp's 30 s limit in cfsios (2026-10-04; fix commit
  `5eb02549`; post-fix timeout count UNVERIFIED until jev-s0ve R1).
- **Heavy work.** `nice -n 10`, one full suite per pane, deferred while the 1-minute load is above
  80; through `omp-kit heavy` once it ships. A long-lived handle on a shared database is a defect
  (it blocked `br` recovery, 2026-10-04).

## Plan

The bead graph is the plan. The mission root bead (`pillar:mission`) depends on every open leaf bead
that serves a pillar; `br dep list <root>` all closed means the mission's current stage is done.
Product build steps: `work/plan-20261004/PRODUCT.md` (epic `jev-b35c`). Audit of today's state:
`work/plan-20261004/MISSION-AUDIT.md`.

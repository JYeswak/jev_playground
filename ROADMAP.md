# Roadmap

This file is jev's plan of record. `AGENTS.md` and `work/plan-20261004/PRODUCT.md` link here; when
they disagree, this file wins. The machine-readable form is `.omp/mission.toml` (Mission Protocol
v0.1, `uds/var/agent-tmp/gaps/missions/MISSION-PROTOCOL.md`, owned by omp-kit).

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
| 1 | **Live** | Every claimed surface is ON in a real omp session: it fires on a positive and stays silent on a planted negative in a fresh `omp --mode=rpc` session. | `classifier doctor --json`: every claimed surface ON with an L3 receipt | PARTIAL: `python3 work/omp-jev-review/surface-census.py --scoreboard --days 7` proves calls, not both-ways receipts | `jev-grzn` (L3 receipts), `jev-b35c.3`, `pillar:live` |
| 2 | **Measured** | Every live surface has a value-minus-cost receipt from our own session logs (tokens saved, harms caught, turns rescued, minus Jev/Clef spend and latency). A negative result turns the surface off. | value-ledger receipt per surface | MISSING | `jev-mvvh`, `pillar:measured` |
| 3 | **Honest** | Every quality claim has its bar committed before the first live call, an incumbent on the same rows, N, date, model id and spend. | `python3 scripts/bead-lint.py --all-open`; `scripts/bar_chronology.py` (`jev-6gun`) | PARTIAL: no check that the bar predates the first call until `jev-6gun` lands | `jev-6gun`, `pillar:honest` |
| 4 | **Local-first** | Clef serves a family only where a committed receipt shows it matches or beats Jev under the same calibration; otherwise Jev. Clef runs through localbench's gateway. | `classifier --backend auto` routes only on a receipt | MISSING: no router; Clef-Flash serves on `:8010` and full Clef (51 GB) is on disk at `/Volumes/ZestData/models/cloudflare/clef/` (download done 18:10Z), neither measured | `jev-b35c.4`, `pillar:local-first` |
| 5 | **Portable** | A stranger runs the README from a fresh clone, and `classifier ready` plus one family run in a project we did not write. | `.github/workflows/stranger-run.yml` (daily); `classifier ready <dir>` | PARTIAL: stranger-run passes daily; `classifier ready` not built | `jev-r1vp` (stranger adopts), `jev-b35c.7`, `pillar:portable` |
| 6 | **Current** | What is declared ON is what is running: no switch, hook or log that says one thing while the machine does another. | `classifier doctor` drift section | MISSING: the kit's `npx --prefix kit --no-install jev doctor --robot` says `NOT_RUN`/"no key" while hooks run with a key (plain `jev` on PATH is Hermes 0.19.0, not ours) | `jev-b35c.3`, `jev-35sg`, `pillar:current` |

### Done for a feature

Live in a real session both ways, a value receipt, and a non-author re-ran its acceptance, with the
commit on `origin/main`. A refutation closes on its committed investigation artifact instead of a
code commit. Enforced by `.beads/policy.yaml` (strict workflow: every edge into `closed` needs a
non-author reviewer gate, no self-close, a `commit:` or `investigation:` reference). The
`origin/main` check is not enforced by `br` yet (omp-kit MP3).

### Cadence

| When | What | Runs as | Today |
|---|---|---|---|
| Daily | Stranger-run of the README | GitHub Actions `stranger-run.yml`, 03:17 UTC | runs |
| Daily | `jev-latest` canary against the pinned `jev-1.13.0` | launchd `ai.zeststream.jev-latest-canary`, 09:07 | runs |
| Daily | Every pillar check, one scoreboard row | omp-kit MP5 `ompkit-rc-epic-land-fix-release-dogfood-rz5.97` | NOT RUNNING: open in omp-kit; jev side `jev-2b7f` |
| Daily | Fleet watcher pages pane 1 on idle, needs-human, CI red | `scripts/fleet-idle-watch.py` | STOPPED since the 2026-10-04 overnight pause |
| Weekly | Value-ledger review: keep, kill or promote each surface; mission audit | omp-kit MP2 `ompkit-rc-epic-land-fix-release-dogfood-rz5.94` (`doctor --scope mission`) | NOT RUNNING: open in omp-kit; jev side `jev-2b7f` |
| Long-term | The ten families each live or refuted with evidence; Clef the default where it wins; `classifier` adoptable by another repo in under an hour | stage-exit bead `jev-uzq1` | open |

### Not in the mission

Benchmark tourism; certificates, ledgers or dashboards with no consumer; games, computer use,
trading; paid comparator models; a family without a host tool; audits of our own docs; fleet
plumbing that omp-kit owns (git writers, idle dispatch, index locks).

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
  latency budget under omp's handler limits, fails open, and has an off switch the host session's
  pane 1 may use without asking. Incident: the memory filter hit omp's 30 s limit in cfsios
  (2026-10-04, fixed in `5eb02549`).
- **Heavy work.** `nice -n 10`, one full suite per pane, deferred while the 1-minute load is above
  80; through `omp-kit heavy` once it ships. A long-lived handle on a shared database is a defect
  (it blocked `br` recovery, 2026-10-04).

## Plan

The bead graph is the plan. The mission root bead (`pillar:mission`) depends on every open leaf bead
that serves a pillar; `br dep list <root>` all closed means the mission's current stage is done.
Product build steps: `work/plan-20261004/PRODUCT.md` (epic `jev-b35c`). Audit of today's state:
`work/plan-20261004/MISSION-AUDIT.md`.

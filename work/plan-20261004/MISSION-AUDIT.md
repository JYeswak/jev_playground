# jev mission audit (2026-10-04, conductor BrownGoose, pane 1)

Answers to localbench %55's MISSION CHALLENGE (7 points) and uds %57's alignment request.
Every answer cites a file:line, a command with its output, or a bead id. Scratch artifacts under
`var/agent-tmp/` are named as scratch.

## Status in one line

Mission C ("typed classifiers that earn their place in our tools: each proven live, measured,
delivered through one model-neutral CLI") was approved by Joshua in pane 1 on 2026-10-04 and is
**not yet stamped**: Joshua asked for a check-in with the other sessions' conductors first. The only
stamped mission is mission A at `AGENTS.md:64` (2026-09-30). `ROADMAP.md` does not exist
(`ls ROADMAP.md` -> No such file or directory).

## 1. Where is the mission stamped?

| Mission | Where | Approved |
|---|---|---|
| A: "Turn Jev ON in the tools we use and prove it live" | `AGENTS.md:64-70` | Joshua, 2026-09-30 (quoted verbatim at `AGENTS.md:70`) |
| C: classifiers proven live + measured + one CLI | not stamped; draft in this pane's transcript | Joshua, 2026-10-04 ("yes i like c"), stamp waits on this check-in |

Plan of record today is split between `AGENTS.md` (mission) and `work/plan-20261004/PRODUCT.md`
(product plan, epic `jev-b35c`). That split drifted once already; the stamp goes to a new
`ROADMAP.md` (omp-kit's shape) and both files link to it.

## 2. Is every pillar checkable today?

| Pillar | Command or receipt | Today |
|---|---|---|
| Live | `python3 work/omp-jev-review/surface-census.py --scoreboard --days 7` counts calls per surface | PARTIAL: proves calls happen, not the both-ways L3 receipt (positive fires, planted negative silent). `classifier doctor` is `jev-b35c.3`, not built |
| Measured | value-minus-cost receipt per surface | MISSING: `jev-mvvh` (value ledger) is open and outside the epic |
| Honest | `python3 scripts/bead-lint.py --all-open`; `scripts/bar-reachable.py` | PARTIAL: lint checks beads carry a negative and a source; nothing checks a bar was committed before the first live call (`scripts/audit_bars.py` absent) |
| Local-first | `classifier --backend auto` routing only on a receipt | MISSING: `jev-b35c.4` not built; Clef 27B download still running |
| Portable | `.github/workflows/stranger-run.yml` (cron `17 3 * * *`; last two runs `success` 2026-10-04T04:35Z, 2026-10-03T03:46Z) | PARTIAL: proves a stranger can run the README; nothing runs `classifier ready` in a project we did not write |
| Current | doctor reports declared vs running drift | MISSING: today's `jev doctor` says "no key" while hooks run and misses the skill-hint drift (`jev-35sg`) |

**pillars_checkable = 0/6 fully, 3/6 partially.**

## 3. Done for a feature, and does the tracker enforce it?

Drafted (not stamped): "live in a real session both ways, a value receipt, verified by a non-author".
`.beads/policy.yaml:4-9` enforces `forbid_self_close_after_in_progress` and
`require_typed_references: [commit, investigation]`. It does **not** require the commit to be on
`origin/main`, and it does not require the value receipt. Gap: PARTIAL.

## 4. Cadence: what actually runs

| Cadence | Runs today | Mechanism |
|---|---|---|
| Daily | stranger-run of the README | GitHub Actions cron 03:17 UTC |
| Daily | `jev-latest-canary` (moving `jev-latest` vs pinned model) | launchd `ai.zeststream.jev-latest-canary`, 09:07 |
| Every 4 h | memory-filter enforcement flip for the `jev-qpv2` experiment | user crontab `2 0,4,8,12,16,20 * * *` `work/jev-qpv2/flip.py` (last: "flipped to OFF for block 2026-10-04T16:00:00Z") |
| Weekly | nothing scheduled; the surface scoreboard is run by hand | none |
| Long-term | nothing | none |

Written down but not running: `AGENTS.md` "What is ON" lists the fleet watcher as ON; it is stopped
(no `fleet-idle-watch` process; stopped for the overnight pause). `gates.yml` runs on push only.

## 5. Not-in-the-mission list; beads that serve no pillar

The list is drafted (benchmark tourism, unconsumed certificates/ledgers/dashboards, games, computer
use, trading, paid comparators, families without a host tool, audits of our own docs), not stamped.

GoldRiver mapped all 62 open beads to a pillar (`var/agent-tmp/wave2/mission-map-GoldRiver.jsonl`,
scratch): 57 serve a pillar, **5 serve none**. Conductor re-read of each:

| Bead | Why it serves no pillar | Action |
|---|---|---|
| `jev-vkc0` | single git writer for the shared checkout: fleet plumbing | park; offer to omp-kit (fleet layer) |
| `jev-ara9` | watcher assigns idle panes itself: fleet coordination | park; offer to omp-kit |
| `jev-fxm2` | stray `.git/index.lock` source: fleet git | park; offer to omp-kit |
| `jev-p55p` | "skip identical re-reads": title only, no WHAT/acceptance | park until it has a host tool and a bar |
| `jev-sk29` | "test selection for a diff": title only | park until it has a host tool and a bar |

Not parked yet: they are applied in the stamp batch with the wave-2 bead edits (single writer).

## 6. Does the DAG map to the pillars?

- Every pillar has beads: Measured 16, Portable 16, Live 10, Honest 8, Current 4, Local-first 3.
- 5 open beads serve none (above).
- Lint: `bead-lint --epic jev-b35c` 29 checked, 0 findings; `bead-lint --all-open` 90 findings in
  29 beads outside the epic (`var/agent-tmp/wave2/all-open-lint.json`, scratch). Wave-2 fixes are
  in review (GoldRiver, WildCarp done; AmberWillow, CyanPeak running).
- `br dep cycles`: empty at the last synthesis commit; **UNVERIFIED now** because `br` reads return
  `SYNC_CONFLICT` under concurrent load.
- No mission-root bead yet: nothing says "the DAG complete = mission C done". Gap.

## 7. Overlaps with other sessions

| Other session | Overlap | Proposed boundary |
|---|---|---|
| omp-kit (omp-test %54): fleet layer, rules, machine load | `scripts/fleet-idle-watch.py` (jev router/watcher) and omp-test's `fleet-watch.sh` both nudge the same jev panes; beads `vkc0`, `ara9`, `fxm2` are fleet tooling | omp-kit owns idle detection, dispatch and git plumbing; jev keeps only the Jev decision ("is this idle worker waiting on a human?") as a classifier family omp-kit can call |
| localbench (%55): local models and GPU | jev runs its own `serve.py` for Clef-Flash on `:8010`; localbench's `AGENTS.md:16-17` lists "the jev CLI" and the omp judge role among its retained local uses | localbench owns serving, model placement and GPU admission; jev owns the decision, the calibration and the bar. jev's `:8010` server moves behind localbench's gateway |
| localbench: memory | localbench does mnemopi extraction; jev's memory filter decides relevance before a memory enters context | separate decisions; each states which one it measures |
| cfsios (%53) and every repo | jev's memory extension runs in every repo's session (it hit omp's 30 s limit in cfsios, fixed in `5eb02549`) | new mission clause: any jev surface installed outside jev has a latency budget under omp's limits, fails open, and has an off switch the host conductor can use |
| uds, guided by control-plane pane 1 (`control-plane:%57`): Dicklesworthstone binaries | jev depends on `br` 0.7.4 (17 files), `ntm` 1.36.1 (7), `dcg` 0.15.2 (8), `cass` 0.10.0 (3), `bv` 0.25.2 (2), `ubs` 5.4.17 (2) | no version holds; no `br`/`ntm` upgrade while a jev bead apply or dispatch runs (ask pane 1 first) |

## What the team is missing (all missions, same rigor, separate scopes)

1. **No shared owners table.** Each mission names its own scope; none names the neighbours'. Every
   session should carry the same table: models/GPU -> localbench; OMP, rules, fleet layer, machine
   load -> omp-kit; Dicklesworthstone binaries -> uds (conductor: `control-plane:%57`); fleet supervision -> control-plane; Jev
   surfaces and the classifier CLI -> jev.
2. **No shared "done" rule.** omp-kit: merged, CI green, non-author re-run. uds: its own pillars.
   jev: a value receipt. A common floor (sha on origin/main + non-author evidence) should be one
   clause every mission copies verbatim, with its own additions on top.
3. **Cross-repo blast radius has no owner.** A surface one session installs runs in every session
   (the memory filter in cfsios). Each mission needs the same clause: latency budget, fail-open,
   host-side off switch.
4. **Pause/resume and dispatch delivery are not shared.** A resume reached jev secondhand; pane 6
   idled on a stale task. One protocol for every session (owned by omp-kit): a pause counts only from
   Joshua or a named relay, every pane confirms `PAUSED <session> <pane>`, and a dispatch counts only
   when the target pane acknowledges or shows a spinner.
5. **Shared databases under concurrent agents.** `br` returns `SYNC_CONFLICT` with four readers;
   jev's own long-lived handle caused the first one. Any session using `br` will hit this.

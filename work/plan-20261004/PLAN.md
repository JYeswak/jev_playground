# Decision flywheel plan — 2026-10-04 (DRAFT, not frozen)

Author: BrownGoose (pane 1). Status: **DRAFT — needs one non-author review, then Joshua's go, before
any `br` write** (skill://plan-to-beads step 1/4). Consumer: the bead DAG and the fleet router, which
today picks the highest-priority orphan because none of the roadmap beads has an edge.

## 1. Why this plan exists (measured 2026-10-04 ~02:10Z, `br list --json`)

- 95 open beads; 32 carry any dependency edge; the nine roadmap beads (`9cqw nwo1 j0er qunw dau5 mvvh
  jzgm vkc0 7jci`) carry **0 edges, 0 parents**.
- 0 open beads require a failing test first; 2 mention regex engineering (both reactive ReDoS fixes).
- Three closed designs failed for one shared reason, **no labelled positives**: compaction keep (0/32
  needed results kept, jev-x86y), conformal bounds (0 relevant calibration rows, jev-9kmq), vendor-paste
  on organic commits (0/39 vendored, jev-m94x). The scarce input is labels, not model quality.

## 2. The loop (each layer makes the next cheaper)

| Layer | What it produces | Existing bead(s) | Gap |
|---|---|---|---|
| L1 Shadow logs | real decisions, hashed, per surface | live hooks (gate-observe, injection, webscreen, memory, skill-hint/veto, find-rank) | none; logs exist |
| L2 Decision bank | labelled rows with positives per class, group-disjoint splits | jev-vvkr (D/G), jev-hnt5 (local teacher) | positive-rich slices; label budget |
| L3 Replay | a policy's saving/misses on 30 d of logs before shipping | jev-jzgm (needs-verify), jev-z885 (per-event randomisation + OPE) | consume L2 units |
| L4 Calibration | a cut or bound per surface with a stated error | (9kmq closed REFUTED: support) | **new bead**, gated on >=30 positives/class |
| L5 Enforce / roll out | the surface acts, machine-wide | jev-9cqw (memory), jev-j0er (screens), jev-qunw (gate advisory), jev-dau5 (long results), jev-nwo1 (smart stop) | none |
| L6 Value ledger | per-surface cost vs value; kill what loses | jev-mvvh, jev-06wt (heartbeat + auto-off) | none |

L6 feeds L1: a killed surface stops logging and frees its budget; a surviving one becomes a teacher.

## 3. Proposed blocking edges (dependent <- prerequisite), for review

Only edges where the dependent cannot meet its own acceptance without the prerequisite:

1. NEW-L4 calibration <- jev-vvkr (needs a slice with >=30 positives per class).
2. jev-hnt5 <- jev-vvkr (already exists; keep).
3. jev-qunw advisory <- jev-jzgm (the advisory cut is replayed on 30 d before any warning ships).
4. jev-06wt auto-off <- jev-mvvh (auto-off needs each surface's expected rate and value).

Deliberately NOT edges (consumes, does not block): jev-9cqw, jev-j0er, jev-dau5, jev-nwo1 each carry
their own before/after measurement and can proceed now; jev-jzgm already reproduced known results from
logs alone. vkc0 and 7jci are fleet tooling outside the loop. Parent: one epic "Decision flywheel"
over L2-L6 beads (accounting node only; never dispatched).

## 4. Contract added to every implementation bead in this graph

Appended to the ACCEPTANCE of each child, never replacing its existing bar:

- **Test first.** The failing test is committed (or shown failing in the bead comment with command and
  output) before the change; acceptance names it.
- **Mutation.** One planted mutation of the change that the test must catch, with the command.
- **Regex.** Any pattern that runs on tool output, model text or commands passes the
  `regex-engineering` skill §7 run (engine run; match / no-match / near-miss timing on a 50k-char
  adversarial input < 50 ms; regexploit) before it lands.
- **Bar before calls.** Unchanged: the bar is committed before the first live call; spend stated.
- **Non-author verify.** Unchanged.

## 5. Research step (before any new implementation bead is created)

One read-only pass per new bead (NEW-L4 only, today): prior art in this repo (`NEGATIVE_EVIDENCE.md`,
closed beads), `docs-mirror/typesafe/confidence.md` and cookbooks, and the Dicklesworthstone mirror
(`fh`), written as a bead comment with sources. No new markdown file.

## 6. Activation and stop

- This file is a draft. Conversion happens only after (a) one non-author review comment on the epic
  question and (b) Joshua's go. Until then no `br create`, no `br dep add`.
- In-flight beads keep running; adding edges must not block an `in_progress` bead (edges 3-4 target
  `open` beads only).
- Stop if review finds an edge that is a preference rather than a prerequisite, or a cycle
  (`br dep cycles --json`).

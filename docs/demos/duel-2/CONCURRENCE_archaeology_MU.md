# Q62 — Concurrence archaeology on every RULED_OUT row

**Method:** archaeology, not judgement. Opened each kill receipt; traced STATUS.tsv flips with
`git log -p` (all four rows were BORN RULED_OUT in `c85f869`, so the file records no flip —
the kill evidence lives in the receipts + PLAN narrative, cited per row).
`%an` cannot attribute panes (single commit identity); attribution below comes from receipt
actor/content fields and explicit PLAN attributions, never from commit subjects alone.
**Rule under test** (§3c rule 3): a kill needs a non-author (like a score); an author killing its
own candidate is fine; a conductor killing another pane's candidate needs non-author concurrence.

---

## Row 1 — demo-1-route-backtest (author pane2 per STATUS; nuance below)

- **Grounds:** rung-4 measured lift 0.047% ($0.0034228 on 30 real turns) + zero Jev calls behind a
  hand-written token heuristic.
- **Kill receipt:** `demos/routing-backtest/runs/backtest-real-excerpt.json` (the 0.047% measurement;
  receipt carries no actor/verdict keys — it is a measurement, not a kill decision).
- **Killer:** diffuse — no single kill decision on record. Measurement (backtest runs under
  `jev-demo-loop-a1q`) + zero-Jev code finding ("found in code by a non-author", PLAN §5.1) recorded
  as a rung-4 kill by the conductor (PLAN §3c "Kills so far", RULING table).
- **Killer != author:** N/A — no discrete killer. Non-author elements present (code finding).
- **Concurrence on record:** NO — as a distinct act. There is no concurrence artifact because there
  is no kill decision to concur with; the "kill" is a measurement plus a finding.
- **Authorship nuance:** STATUS says pane2, but PLAN §5.1 records both lineages proposing demo-1
  independently — single-pane authorship is lossy here, which further blurs killer/author comparison.

## Row 2 — demo-8-credential-screen (author pane3)

- **Grounds:** structural safety leak; demand score 100.
- **Kill receipts:** author's own `DEMAND_RANK_MU.md` (pane3 ranks own candidate 150, "Nobody —
  correctly killed", "dead, rightly") + non-author cross-score
  `docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md` (pane2: "Cross-score verdict: 100 and kill",
  "Both correctly kill it").
- **Killer:** author-self (fine under the rule, no concurrence required).
- **Concurrence on record:** YES — pane 2's 100-and-kill cross-score is an explicit non-author
  concurrence with the author's self-kill. Strongest concurrence artifact in the lane.

## Row 3 — COD-H3-price-drift-auditor (author pane2)

- **Grounds:** no Jev-necessary stage (4 of 5 stages deterministic); retry T1-tooling / T2-router-wedge.
- **Kill receipt:** `docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md` (verdict RULED OUT in filed form;
  `_MU` = pane-3 authored), recorded by conductor (`b09f910`).
- **Killer:** pane 3 (non-author) ≠ author. Satisfies the letter ("a kill needs a non-author") by
  killer identity.
- **Concurrence on record:** NO — as a separate act. The kill receipt IS the non-author's work;
  no second party concurred, and none was required by either reading (not a conductor kill).

## Row 4 — MU-H1-todo-judge (author pane3)

- **Grounds:** denominator too thin (17 markers / 283,786 KLOC; 183 short of the 200-study).
- **Kill receipt:** `docs/demos/duel-2/runs/muh1-marker-census-20260918T034820Z.json`
  (interpretation result `DENOMINATOR_TOO_THIN_FOR_LABELLED_HALF`; no actor key — attribution via
  NEGATIVE_EVIDENCE R14 "run by a non-author" and PLAN §3l "run by pane 2 as a non-author of MU-H1"),
  recorded as RULED_OUT by conductor (`0ea34ed`, PLAN §3l).
- **Killer:** evidence by pane 2 (non-author) ≠ author; decision recorded by conductor on that evidence.
- **Concurrence on record:** NO — as a separate act. Same structure as COD-H3: non-authored
  kill-evidence, no second concur. (Conductor recording a pane's kill-evidence is not a
  conductor-kill: the decision content is the pane's measurement.)

---

## Result

| Row | Killer != author? | Concurrence exists? |
|---|---|---|
| demo-1 | no discrete killer (measurement + finding) | NO (nothing to concur with) |
| demo-8 | author-self + non-author cross | YES (pane 2, 100-and-kill) |
| COD-H3 | yes, killer is non-author | NO (not required; killer identity satisfies letter) |
| MU-H1 | yes, evidence non-authored | NO (not required; same structure) |

**The rule was never invoked as a gate in any of the four kills — and never violated either.**
No conductor-kill of another pane's candidate occurred at all: the trigger never arose. Stronger than
"never-invoked": in the two pane-kills the rule's requirement was satisfied structurally (killer is
the non-author), in the self-kill it was vacuous, and in the measurement-kill there was no decision
to gate. **DEMOTE-TO-GUIDANCE is the correct classification** (Q60 concession stands, now evidenced
rather than asserted): untested, not failed. Deletion would remove a boundary whose first real test —
a conductor proposing to kill another pane's candidate — has simply not happened yet.

---

## Proposed STATUS.tsv column definition

**Name:** `kill_concurrence` — **position:** column 8, after `blocked_on` (append; existing 7 columns
untouched, machine-readability preserved).

**Valid values:**
- `author-self` — killer == candidate author (no concurrence required).
- `nonauthor-kill:<receipt>@<sha>` — killer-evidence itself non-authored ( killer identity satisfies
  the rule; receipt path + committing sha).
- `concur:<pane>:<receipt>@<sha>` — separate non-author concurrence with author-self or
  measurement kill (pane id + receipt + sha).
- `none` — RULED_OUT row with no concurrence on record (grandfathered rows keep this value openly
  rather than being backfilled by inference).

**Empty value means:** row is not RULED_OUT (inapplicable). **A RULED_OUT row with an empty
`kill_concurrence` is a schema violation** — `scripts/lane-status.sh` must exit 3 on it, same as a
missing receipt (fail-closed, matching the file's existing contract).

**Backfill for the four existing rows (no inference beyond this document):**
- demo-1-route-backtest → `none` (no discrete kill decision; measurement-kill, nothing to concur with)
- demo-8-credential-screen → `concur:pane2:docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md@<sha-of-that-file's-commit>`
  (sha to be pinned by whoever applies the column — left open deliberately, not filled from memory)
- COD-H3-price-drift-auditor → `nonauthor-kill:docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md@<sha>`
- MU-H1-todo-judge → `nonauthor-kill:docs/demos/duel-2/runs/muh1-marker-census-20260918T034820Z.json@<sha>`

**Mechanical check (the watcher, not a volunteer):**
```sh
awk -F'\t' '!/^#/ && $4=="RULED_OUT" && $8=="" {bad=1; print "MISSING concurrence: "$1} END{exit bad}' docs/demos/STATUS.tsv
```
Runs inside `scripts/lane-status.sh` next to the receipt-existence check. Any future RULED_OUT without
a column value fails the lane's own status gate — the condition fires observably or the file is red.

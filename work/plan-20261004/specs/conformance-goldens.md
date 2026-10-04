# Goldens + conformance for classifier families: the scenario graph (plan, 2026-10-04)

Status: design for the bead graph (Joshua 2026-10-04: "part of our bead dag ... as we prepare").
Inputs: fleet schema `var/agent-tmp/dogfood/fleet-schema/` (16 families), FAMILY-REBUILD.md,
the existing Jev-only wire harness `kit/test/wire-conformance.test.mjs` (16/16) and its
`kit/test/wire-conformance-DISCREPANCIES.md`, `scripts/render-results.py --check` (already a golden
for the README results table), the strict close policy.

## The idea in one paragraph

Every family is a **decision contract** (the spec). Every technique that can answer it (rule, lexical,
embedding probe, encoder, local LM, Jev, Clef, LLM) is an **implementation** of that contract behind one
adapter. Conformance tests prove each implementation honours the contract's MUST clauses (safe side,
fail-open, refusal, valid probabilities) on recorded inputs, offline, for every backend the same way.
Goldens freeze the things that must not move silently: the labelled rows, the recorded answers, the
receipts' numbers, and the CLI's output. A bake-off is then just a differential run over the same frozen
rows, and the winner is whichever implementation passes conformance **and** beats the bar.

## 1. The decision contract (spec, one file per family)

`kit/contracts/<family>.json` (created by N0's successor, see beads):
- `question`: type (choice / score / noul / rule), options with descriptions, the threshold or decision rule.
- `state`: the input shape (fields, size limit, privacy allowlist: summaries only, never raw transcript).
- `safe_side`: the action on invalid answer, timeout, unconfigured key, cap reached (always the no-op /
  keep / allow side for anything that runs inside a session).
- `budget`: latency budget (ms) and per-run call/spend cap.
- `labels`: the label source in the fleet logs and its extraction command.
- `bar`: majority constant, cheapest rule, and the preregistered bar (committed before any call).

MUST clauses every backend adapter is tested against (spec-derived matrix, skill Pattern 4):

| ID | Clause | Planted check |
|---|---|---|
| C1 | An answer outside the offered options is refused, and the safe side is taken | recorded answer with choice moved out of ids |
| C2 | Probabilities are finite, in [0,1], sum to 1 within 0.02, and the chosen option is the max | NaN / rescaled / chosen-below-max mutations |
| C3 | Timeout, transport error, or missing key takes the safe side and never blocks the host turn | fake transport that hangs past budget; no key |
| C4 | Spend/call cap reached takes the safe side and logs `daily-cap` | cap = 0 |
| C5 | Input over the size limit or outside the privacy allowlist is refused before any call | 50k-char state; a raw-transcript field |
| C6 | Same input, same recorded answer → same decision (deterministic policy) | run twice |
| C7 | The decision log row carries model/backend id, latency, cost, and a hash, never raw text | row schema check |

The existing wire harness already proves C1/C2 for Jev; the new harness generalises it so every adapter
(rule, probe, encoder, Jev, Clef, LLM) runs the same C1-C7 table. A backend that cannot produce
probabilities (a regex) is XFAIL on C2 with a DISCREPANCIES entry, never SKIP.

## 2. Goldens (what is frozen, and how)

| Golden | Pattern | Volatility | Strategy |
|---|---|---|---|
| Labelled rows per family (from the fleet miner) | exact, hash-pinned | low | `fixtures/<family>/labels.jsonl` + PROVENANCE (miner commit, log window, command, sha256) |
| Recorded backend answers on those rows | exact | low | `fixtures/<family>/answers-<backend>.jsonl`; live calls only when re-recording |
| Bake-off receipt numbers (AUC, accuracy, ECE, McNemar) | fuzzy | low | recompute from recorded answers; tolerance 0.005 abs; mismatch = FAIL |
| `classifier <family> eval --json` output | scrubbed | medium | scrub latency, timestamps, paths; compare the rest |
| README results/technique tables | exact (generated) | medium | `render-results.py --check` pattern, extended to the X-table |
| Contract files themselves | exact | low | a contract change shows as a golden diff and needs review |

Update rule (both skills): `UPDATE_GOLDENS=1` regenerates; the diff is reviewed by a non-author before
commit; CI never auto-updates; `*.actual` is gitignored. Regenerating a golden to make a test pass is
forbidden pattern 3.

## 3. The scenario graph

A scenario is one node: **family × backend × condition**. Conditions:

| Condition | What it proves | Golden / check |
|---|---|---|
| nominal | accuracy vs labels | fuzzy receipt golden |
| invalid answer | C1/C2 safe side | spec matrix |
| down / timeout / no key | C3 fail-open, host turn not held | spec matrix + latency budget |
| cap reached | C4 | spec matrix |
| oversize / private field | C5 refusal before call | spec matrix |
| adversarial / planted | catches the planted positive | per-family planted fixture |
| option-order shuffle, paraphrase, irrelevant padding | metamorphic invariance where labels are thin (6 label-pending families; Jev's default-answer bias, jev-cqbj) | metamorphic relation, no oracle needed |
| out-of-distribution repo | transfer (portable pillar) | fixtures from a repo the bar was not fitted on |
| live, fresh omp session | L3 both ways (process-based conformance) | jev-grzn receipt |
| value over time | KEEP / KILL | jev-mvvh ledger row |

Edges (the order a family moves through): labels frozen → contract committed → every adapter passes
C1-C7 → differential bake-off on frozen rows (cheapest first) → winner ships behind the contract → L3
live both ways → value receipt → weekly re-run (VALUE2 rows) re-checks the receipt golden for drift.

## 4. Coverage matrix (what "done" means per family)

`family × backend × clause` and `family × condition`, generated into `work/plan-20261004/CONFORMANCE.md`
by the harness. A family ships only when: every MUST clause passes for the shipped backend (XFAIL only
with a DISCREPANCIES entry), the nominal receipt golden matches, the L3 and value nodes are green.
Unknown gaps are not allowed: an untested clause shows as a blank cell, not as a pass.

## 5. Beads this adds (to apply after the rebuild pass)

- **Harness bead** (blocks every family's ship step): generalise `kit/test/wire-conformance.test.mjs` into
  a model-neutral harness: adapter interface, C1-C7 table, DISCREPANCIES.md (DISC-NNN, ACCEPTED /
  INVESTIGATING / WILL-FIX, review date), coverage-matrix generator. Planted negative: an adapter that
  takes the unsafe side on timeout must fail C3.
- **Fixture bead** (part of N0): the miner's label emitters write `fixtures/<family>/labels.jsonl` with
  PROVENANCE.md; a fixture without provenance fails the harness.
- **Per family**: its contract file and its recorded answers become acceptance items of the family bead
  (no separate beads; one family bead owns its whole column of the scenario graph).
- **Metamorphic bead** for the six label-pending families: option-shuffle / paraphrase / padding
  relations, run on every backend; a backend that changes its decision under option shuffle fails.

## 6. What this does not do

It does not prove any family helps the fleet; the value receipt does. It does not replace the live L3
check; recorded fixtures cannot show a hook actually loaded. Goldens catch drift and contract breaks,
not a wrong label set: label quality stays with blind non-author labelling and kappa.

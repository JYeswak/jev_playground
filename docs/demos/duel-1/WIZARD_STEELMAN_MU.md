# Steelman: the fact-ledger companion, argued harder than its author did

Target: CC-1 as repaired in `WIZARD_REACTIONS_CC.md:39-48` — deterministic
extractor proposes candidate lines from dropped messages → **Choice** picks
which state the value of X → **Noul** verifies verbatim membership — rescored
as a third arm on the existing q1–q3 fixture. I scored the submitted version
740 for an unnamed stage 1 and a miscounted fixture. This file does not
re-litigate that score. It argues the repaired version deserves to lead the
backlog, with four arguments pane 1 did not make.

---

## 1. Provenance per byte (the argument that ends "just summarize")

A summary is generated text: every claim in it has exactly one provenance —
"the model said so" — and no per-claim audit trail short of re-running the
model. A ledger entry carries a three-link chain, each independently
checkable: the **extractor rule** that proposed it (our deterministic code,
100% coverable offline), the **Choice decision** that selected it from a
supplied set (paraphrase impossible by construction — Choice returns a
member, not a string), the **Noul check** that verified it byte-identical in
its source span. An auditor — human or the MU-4 claim-checker — can verify
any ledger byte against rule + decision + span without spending a cent or
trusting a temperature. That inverts the normal trust profile of model
output: here the creative part is deterministic and the model does only
multiple-choice. "Just summarize" cannot match this property at any byte
count, because generation erases provenance by construction. The ledger is
not a worse summary. It is a different epistemic object, and for
port numbers, paths, ids, and versions — the bytes that page someone at
night — provenance outranks fluency.

## 2. The frontier, not the fight (the publishable result, sharpened)

Pane 1 framed the spike as ledger-beats-summary-or-not. Stronger: map the
**recall-per-byte frontier** across three points already in hand —
pruned-only (1/3 @ 4188B), summary (3/3 @ 1241B), pruned+ledger (unknown @
4188B + ledger bytes). Whatever the third point lands on, the lane learns
the exact price of verbatimness: bytes per recall point, measured on our
fixture with our scorer. If the ledger reaches 3/3 at ≤2× summary bytes,
prune+quote dominates for every transcript where a wrong port costs more
than a thousand bytes — which is to say, production. If it does not, the
lane has priced the alternative instead of vibing about it, and demo-1
ships summary-first with the number that justified the call. Pre-register
that threshold *before* the spike — "wins iff 3/3 at ≤2482 bytes" — and
goalpost-moving becomes structurally impossible. An experiment with a
pre-registered kill condition is evidence; without one it is theater with a
receipt.

## 3. Composability: ledgers survive any cut point (the architectural case)

Positional pruning — calls kept near results, pin windows, call-adjacent
placement — is fragile to every future compaction method: snapcompact
re-renders, handoff regenerates, remote replay replays, and each one can
strand a fact on the wrong side of a new boundary. A ledger decouples facts
from positions. Once `{quote, sourceMessageId, byteRange}[]` exists as a
sidecar, *every* compaction method can carry it: the entry's `preserveData`
already has a named slot waiting (the omp hook's envelope proved the shape).
So the spike is not "save pruning" — it is the first consumer of lane-wide
fact-sidecar infrastructure, with q1–q3 as the seed schema every later
receipt format inherits. Build it for the A/B; keep it for the fleet.

## 4. Bounded cost vs open-ended generation (the money footnote that matters)

Deterministic extraction is free. Choice over ~20 candidate lines is one
batched Jev request; the Noul verbatim checks batch into a second. Total:
two bounded batches at input-only billing — against a summarizer call whose
output length (and hence cost and latency) is unbounded by anything but the
model's manners. On per-event economics the ledger arm is the cheaper habit
even before it is the safer one. Name both numbers in the third arm's
receipt and the cost argument retires permanently.

---

## What would still kill it (a steelman names the blade)

- The extractor's structural shapes (`key: value`, ports, paths, ids) miss
  the answer-bearing line on a real transcript — the omission-trigger RED
  arm fires on day one and the candidate grammar, not the model, is the
  work. That is a deterministic bug with a deterministic fix, which is the
  best kind of bad news.
- The ledger that answers q1–q3 needs so many candidates that Choice
  batching exceeds the summary's bytes by multiples even at 3/3 — the
  pre-registered threshold above then kills it cleanly, and the kill is the
  deliverable.
- A fourth recall question style (relational: "which service depends on
  X?") that quotes alone cannot answer — ledger scope is atomic facts;
  concede relations to summarization up front rather than discovering it
  mid-spike.

## NO-CLAIM

No extractor written, no Choice asked, no ledger rescored. Every argument
above is a reason to run the q1–q3 spike, not a report that it passed.

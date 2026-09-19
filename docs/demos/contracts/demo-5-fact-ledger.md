<!-- A/B verdict migration (2026-09-18): any literal n=1 relative verdict below is historical/retracted. Current harness withholds verdicts until each arm has >=10 zero-spread samples; see compaction/ab/verdict.ts. -->

# Demo-5 contract — fact ledger for pruned context

Status: **contract only; not implemented**
Plan source: `docs/demos/PLAN.md` §5.5
Owner: pane 2 / WindyJaguar owns `demos/fact-ledger/**` when emitted; no other pane may edit that subtree.
Verification posture: offline first, injected asker; no live call is authorized by this contract.

## Goal and ownership

Build an installable, read-only fact-ledger companion for `fast-jev-compaction`. Given a transcript,
a set of dropped messages, and named fact slots, it emits byte-exact quotes with source message ids
and byte ranges, appends those quotes to the pruned context, and re-runs the existing resume
questions. The product question is not “can a summary sound good?” It is: **does preserving exact
answer-bearing bytes recover the facts relevance pruning removed, without trusting generated prose?**

The owned boundary is `demos/fact-ledger/**`, plus the explicitly named integration seam in
`compaction/ab/run-ab.ts` if the existing scorer must accept an `armC` data entry. That integration
must be a separate, path-limited change and must not silently rewrite the existing A/B receipt.
The fixture and original A/B receipt remain evidence inputs. This contract does not authorize
changes to `fast-jev-compaction`, the omp adapter, pane 3's fixture tree, `PLAN.md`, `EVAL.md`, or
any upstream checkout.

The first implementation must choose one integration shape before coding:

1. extend the scorer with a declared `armC` configuration entry and a schema version bump, or
2. run the unchanged scorer in a second invocation and merge two receipts through a deterministic
   receipt combiner.

It must not claim both shapes at once. The smaller first cut is the second-invocation shape because
it avoids changing the already receipted A/B schema; the receipt must state that choice.

Non-goals:

- no live routing, no live compaction hook, and no automatic context mutation;
- no generated summary, paraphrase, or model-authored ledger line;
- no arbitrary prose claim extraction in the first version;
- no silent fallback from a missing quote to the generic summarizer;
- no threshold tuned to “beat arm B”;
- no deletion or retroactive editing of `compaction/runs/ab-20260917.json`.

## Product context and guardrails

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Offline lane first. Live calls are budgeted and stated in the receipt.
> The API key lives only in the environment as `TYPESAFE_API_KEY` and its value is never recorded
> in any artifact — names are expected, values are not.
>
> **Evidence rules.** A claim with no re-derivation path is not evidence. An empty scan set is an
> **ERROR**, never a pass. A one-item scan set is not a demonstration. A timeout is not a verdict.
> Exit code must agree with verdict text. These are implementation requirements, **not statements
> that any code or gate has passed.**
>
> **Shared worktree.** Three agents share this checkout and all commit as the same git identity,
> so `%an` cannot attribute a commit. Stage explicit paths, own files only, never `git add -A`,
> never amend, never rewrite shared history. Preserve peer changes: if a file you need belongs to
> another lane, message its owner with the exact replacement text rather than editing it.
>
> **Blocker protocol.** If a prerequisite is unavailable, report the exact blocker with the command
> and its verbatim output. Never substitute a stub for evidence, never weaken an adversarial
> assertion, and never let a missing capability be reported as a passing check.

These are implementation requirements, not statements that any product code or behavioral gate has
passed.

## Embedded contract

The following requirements define this boundary and its interactions. An implementer must not need
to open the plan to decide what the ledger means.

### 1. Inputs and turn identity

The CLI accepts one or more session JSONL files and a JSON fact-slot file. The fact-slot file is
explicit and structured, for example:

```json
{
  "slots": [
    {"id": "service-saa-port", "question": "What port does saa use?", "source_tool": "read", "path_suffix": "/seed-svc/saa"},
    {"id": "audit-sae-line", "question": "Quote the AUDIT line for sae.", "source_tool": "read", "path_suffix": "/seed-svc/AUDIT.md"}
  ]
}
```

The transcript adapter must preserve the original source message order and identify a source by
stable message index plus tool-use id. A quote record is:

```json
{
  "slotId": "service-saa-port",
  "quote": "1:service 1 config: port 801",
  "sourceMessageIndex": 2,
  "sourceToolUseId": "call-or-equivalent",
  "byteStart": 0,
  "byteEnd": 31
}
```

`byteStart` and `byteEnd` are offsets into the exact source result text held in the normalized
transcript. Offsets are half-open `[start,end)`, UTF-8 byte offsets, and must be reproducible from
the transcript SHA. A line number alone is insufficient because the source result can be multiline.

The ledger never receives a free-form model-generated quote. Candidate extraction is deterministic:
only configured structural shapes (`key: value`, `name: value`, port/path/id lines, and exact
source ranges) may become candidates. If the extractor cannot identify a source range, the slot is
`insufficient`, never guessed.

### 2. Stage-by-stage mechanism

Stage 0 — normalize the transcript using the existing adapter contract. Preserve nonblank text,
tool-use ids, tool-result ids, and source bytes. Record transcript SHA-256. Refuse malformed JSONL.

Stage 1 — deterministic candidate extraction. For each declared slot, enumerate candidate source
spans from the dropped messages only. Candidate ordering is source order, then byte offset. No Jev
call occurs in this stage.

Stage 2 — Choice selection. Ask a Choice question whose candidates are the extracted quote ids,
not quote text generated by the model: “Which candidate states the requested value?” The options
are exactly the supplied candidate ids plus `NONE`. A Choice answer outside the supplied set is a
malformed answer and fails closed. If the answer is `NONE`, record `insufficient`.

Stage 3 — Noul verbatim verification. For each selected candidate, ask the exact Noul question:
“Does this candidate quote appear byte-for-byte at the declared source range in the source message,
and does it answer the slot question?” Criteria: true means both identity and relevance hold; false
means withhold. A Noul judges; it does not extract.

Stage 4 — local byte check. Independently slice the source result at `[byteStart,byteEnd)` and
compare bytes to `quote`. This local check is authoritative for identity. Any mismatch is a hard
refusal even if Jev returns true. The resulting action is `keep`, `withhold`, or `error`; never
`approve` a nonidentical quote.

Stage 5 — append ledger quotes. The ledger is appended as structured JSON or a deterministic
plain-text block with the exact quote and source metadata. Appending must not alter original
messages. The resume scorer consumes the original pruned context plus this ledger arm; it does not
ask Jev to rewrite the ledger.

### 3. Absolute thresholds and comparison

The fact-ledger arm must score the same three questions `q1`, `q2`, and `q3` from the committed A/B
fixture before any expansion. The acceptance threshold is **3/3 absolute fact recall**. Never use
“beats arm B” as the threshold: arm B scored 3, 1, 3 on a byte-identical fixture, so a stochastic
baseline is not a threshold. A later run may report arm B alongside the ledger, but the ledger's
pass/fail condition remains `ledgerScore == 3 && questionCount == 3`.

The comparable-bytes rule is declared, not hand-waved: record pruned-context bytes, ledger bytes,
and combined bytes. “Comparable” means the receipt prints both arms' byte counts and the reviewer
chooses the comparison; code must not silently discard a larger ledger. If the ledger remains
1/3, the demo ships a publishable negative result: pruning is not suitable for this fact-dense
transcript without a different companion. Negative is not a harness failure.

### 4. Jev API contract

The offline suite injects an asker and uses no key. The live adapter, if separately authorized,
uses `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest`, with `TYPESAFE_API_KEY` read
from the environment. The receipt records model, request count, and response schema, never the key.
Choice receives a finite candidate map; Noul receives the source-safe state and exact question.

An insufficient-context result, an answer outside the Choice set, a missing answer key, timeout,
transport error, or malformed probability maps to `withhold` or `ERROR` according to the table
below. It never maps to approve:

| Condition | Action | Receipt |
|---|---|---|
| no candidate span | withhold | `INSUFFICIENT_CONTEXT` |
| Choice `NONE` | withhold | `NONE_SELECTED` |
| Choice id unknown | error | `MALFORMED_CHOICE` |
| Noul false or missing | withhold | `VERIFICATION_REFUSED` |
| local byte mismatch | error | `BYTE_IDENTITY_MISMATCH` |
| timeout/API failure | error or explicit offline skip | `TIMEOUT_UNMEASURED` / `LIVE_SKIPPED` |

No live budget is part of this first bead. If one is later approved, budget it in the receipt before
execution; the offline proof remains the primary gate.

### 5. Four ship artifacts

Install script: `bash demos/fact-ledger/install.sh` from a clean clone. It must install no network
runtime dependency beyond the declared package manager path, run the deterministic suite, and print
the exact offline command:

```sh
npm test --prefix demos/fact-ledger
node demos/fact-ledger/bin/fact-ledger.mjs \
  --transcript compaction/fixtures/omp-session-big-20260917.jsonl \
  --slots demos/fact-ledger/fixtures/q1-q3-slots.json \
  --out demos/fact-ledger/runs/fact-ledger.json
```

Tests: deterministic injected asker plus the RED arms in §Focused verification. The test suite must
not call the network, read a real key, or change the committed fixture. The source-span assertion
must be a direct byte comparison, not a substring assertion.

Receipt: `demos/fact-ledger/runs/fact-ledger-<ISO>.json`. Required fields: schema, generated_at,
transcript path and SHA, slot file SHA, denominator, candidate count, selected count, withheld
count, errors, each quote record, byte counts for the pruned and ledger arms, score per q1–q3,
model/request data when live, and `failures: []`. There is no verdict string over a stochastic
comparison arm.

EVAL row: name verification level `[test]` for offline proof, cite the exact receipt, and state
that the run proves byte-preserving ledger mechanics on the named fixture only. It does not prove
that the extractor covers arbitrary prose, that the fact ledger improves all transcripts, or that
live Jev judgments are stable.

## Focused verification

The third party runs the install command above. The command must be deterministic and exit 0 only
when the offline fixture has exactly three declared slots, all three have byte-identity-verified
quotes, and the receipt has no failures.

RED arm 1 — omission: use a copy of the slot file with the `saa` slot removed while leaving the
source line present. The run must exit nonzero with `INSUFFICIENT_SLOT_COVERAGE` and name the slot;
it must not report 3/3 from only two questions.

RED arm 2 — identity: mutate one quote character or its byte range in a temporary in-memory ledger.
The run must exit nonzero with `BYTE_IDENTITY_MISMATCH`, naming the slot, source message id, and
range. The receipt must not contain the mutated quote as accepted evidence.

RED arm 3 — malformed Choice: injected asker returns an option id absent from the candidate map.
The run must exit nonzero with `MALFORMED_CHOICE`; it must not fall back to the first candidate.

RED arm 4 — empty transcript or empty candidate set. The run must exit nonzero with
`EMPTY_CLASSIFIABLE_SET` or `INSUFFICIENT_CONTEXT`; an empty receipt is never green.

Satisfying arm — committed q1–q3 slots against the real excerpt. It must produce three verified
quotes, a 3/3 absolute ledger score, exact source ranges, and a receipt whose transcript SHA
matches the input. A score other than 3/3 is a valid negative result and must be reported, not
converted into a pass by changing the question set.

Denominator required in every run: session files read, JSONL rows, source messages, dropped
messages, declared slots, candidate spans, verified quotes, withheld slots, and failures by code.
The receipt must make a zero or one-item scan set visibly non-demonstrative.

Who verifies: the implementing pane runs the offline tests; a non-author pane must inspect the
receipt and source-range assertions before this is called shipped. The original A/B author is not
the sole verifier of this follow-up.

## Evidence and logging

Receipt schema `jev.fact-ledger.receipt.v1` is immutable evidence. Never retro-edit a receipt. A
changed source or slot file creates a new ISO receipt and leaves the old receipt in place.

The receipt must contain no operator home paths, machine names, API keys, raw credential values, or
unbounded source dumps. Use repo-relative paths for committed fixture inputs and SHA-256 identity
for source files. If a source result contains sensitive bytes, retain only the quote required by
the slot and apply the lane's existing secret boundary before any live call.

Verification level: `[test]` for the offline injected-asker proof; `[live]` is forbidden until a
separate approved run records a budget, model, request count, and actual response evidence.

EVAL Boundary: this demo proves deterministic candidate extraction, Choice selection, Noul
verbatim checking, and absolute q1–q3 recall on the committed fixture. It does not prove arbitrary
Markdown extraction, model truth, general transcript recall, live provider stability, or production
context-hook safety. The comparison arm is never treated as a ground-truth oracle.

## Open risks with concrete resolution

Risk: the structural extractor misses a fact format. Resolution: add a committed fixture and a
specific extractor grammar, then add a RED arm where the missing candidate produces withhold; do
not add a model generator to hide the miss.

Risk: a fact line is duplicated in two source results. Resolution: Choice options include both
source ids and byte ranges; require the selected range to answer the slot, and record ambiguity as
`AMBIGUOUS_CANDIDATES` with a human-needed action.

Risk: the ledger grows until it defeats compaction. Resolution: record ledger bytes per slot and
set a declared maximum before implementation. Exceeding it is `LEDGER_BUDGET_EXCEEDED`, not silent
truncation.

Risk: a contributor changes the questions to recover a score. Resolution: pin the q1–q3 question
hash in the receipt and compare against the committed slot file; changing questions creates a new
receipt schema/input identity.

Risk: live Jev receives source content it should not see. Resolution: offline first, local secret
scan before any request, redacted surrogate only, and a request-recorder RED arm asserting secret
canaries never appear in serialized request state.

**Contract status:** implementation not started. Every statement above is a requirement or a
boundary, not a claim that the artifact already exists or passes.

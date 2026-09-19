# Hook recon — omp pre-compact surface (jev-compact-hook-hbs)

Date: 2026-09-17 · Lane: offline (no key, no network) · Claim: L0 offline-verified

## Verdict: the point EXISTS — adapter path, no fallback needed

omp exposes a pre-compaction interception point, `session_before_compact`.
Built `compaction/src/omp-hook.ts` + `compaction/test/hook-compact.test.ts`
(12 deterministic tests, canned asker) instead of a fallback.

## Surface surveyed

| Candidate | Finding |
|---|---|
| `session_before_compact` | **The point.** Pre-compaction hook; may cancel or supply the full custom payload (quotes below). |
| `session.compacting` | Prompt/context customization for *default* compaction (`prompt`, `context`, `preserveData`). Wrong layer for judged pruning — not used. |
| `context` hook (`{messages}` per LLM call) | Per-call message replacement (AGENTS.md seam #2). Viable but per-call, not pre-compact — not used. |
| `--hook` flag | Alias for `--extension` (`omp --help`, `omp://hooks.md`): hook factories load as extension modules. Install path `<repo>/.omp/hooks/pre/*.ts` (a file directly in `.omp/hooks/` is silently undiscovered). |

## Verbatim evidence (the event name, quotable without session docs)

`omp://hooks.md`, § Session events:

> - `session_before_compact` → can return `{ cancel?: boolean; compaction?: CompactionResult }`
> - `session.compacting` → can return `{ context?: string[]; prompt?: string; preserveData?: Record<string, unknown> }`

`omp://compaction.md`, § Extension and hook touchpoints:

> ### `session_before_compact`
> Pre-compaction hook.
> Can:
> - cancel compaction (`{ cancel: true }`)
> - provide full custom compaction payload (`{ compaction: CompactionResult }`)

## Citation correction (close-out item 1)

The adapter header previously grounded the *event* in
`~/.omp/agent/extensions/dcg-guard.ts:430`. That file contains no
`before_compact` string — verified by search. It proves only the shared
module shape both use: a default-export factory calling `pi.on(...)`
(there `pi.on("tool_call", …)` at :430-431). The `session_before_compact`
name and return contract rest on the two verbatim quotes above. Header
fixed accordingly in the same commit as this receipt.

Downgrade stated honestly: omp ships as a compiled binary (`~/.local/bin/omp`;
no `.d.ts` on disk to pin `CompactionResult` against), so the binding's
envelope field names are doc-derived. The adapter core (transcript in,
pruned messages out, passthrough on any error) is fully pinned to
`fast-jev-compaction` source (`compact` @ `src/compact.ts:257`,
pin rule @ `src/state.ts:86-88`, truncation @ `src/compact.ts` `truncatedResultText`).

## Tests

`compaction/test/hook-compact.test.ts`: 12/12 green, full suite 17/17
(`npm test`), `tsc --noEmit` clean. Canned `JevAsker` (fixed noul per
question name); failing asker; malformed-answer asker. Fail-safe arms:
transport failure → passthrough byte-identical; malformed answers
(library *throws* `Invalid Jev answer`, it does not coerce) → passthrough;
below `minReductionRatio` → passthrough to the built-in summarizer.
KNOWN-BAD guard: passthrough output is `deepEqual` to input.

## Gate 40

Extended in this commit: `test/*.test.ts` glob already ran the hook tests
(gate reported `# pass 17` before the change); added a second `--selftest`
RED arm planting an inverted hook property (passthrough must DROP context)
that correct code must refuse. `gate --selftest` green (both arms).

## Not claimed / follow-ups

- L2/L3: binding loads + fires in a live session with the file at
  `<repo>/.omp/hooks/pre/omp-jev.ts`, incl. pinning the exact
  `CompactionResult` shape against runtime behavior. At most 2 live Jev
  calls per the bead budget.
- Live Jev: zero calls made on this bead (offline lane only).

## Boundary

No fixtures touched, no `runs/ab-*` touched, nothing under `compaction/ab/`.
This file was placed under a pre-existing `compaction/runs` pattern hold
(WindyJaguar, idle, unanswered) per bead-assigned path + close-out direction;
it is the only file this lane added outside its reservations.

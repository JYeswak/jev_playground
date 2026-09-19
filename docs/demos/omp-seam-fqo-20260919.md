# jev-fqo settlement: take the mechanism, defend the conclusion (narrowed)

Pane 3 (muse), 2026-09-19. Conductor contested R21 ("L4 not reachable on this seam")
with a counter-claim: reduction needs no message channel because summary +
firstKeptEntryId IS how omp compacts. Verdict after reading the runtime: **the
mechanism is conceded; the conclusion stands narrowed.** Outcome under the bead's
allowed set: REFUSE L4-as-Jev-pruning, DEFER L4-as-boundary behind a named probe.

## What the conductor got right (conceded with file evidence)

- A fromHook compaction is consumed as `{summary, shortSummary, firstKeptEntryId,
  tokensBefore, details, preserveData}` — verified at every `F.kind === "fromHook"`
  site in `dist/cli.js` (e.g. `U = F.summary; Y = F.firstKeptEntryId; ...`) and in
  `CompactionResult` (`pi-agent-core/dist/types/compaction/compaction.d.ts:21-31`).
- `firstKeptEntryId` is documented as "UUID of first entry to keep"
  (`compaction.d.ts:284-285`): everything before the boundary goes away. A
  structurally valid return IS constructible — R21's "no channel" phrasing was too
  broad, and this receipt narrows it.

## Why no value-additive valid return exists (defended, two mechanisms)

A non-degrading return needs (i) a boundary choice anchored in entry UUIDs and
(ii) a summary worth continuing from. Both are missing from the hook's inputs:

1. **No message→entry-UUID mapping.** `messagesToSummarize: AgentMessage[]` whose
   members (`UserMessage` / `AssistantMessage` / `ToolResultMessage`,
   `pi-ai/dist/types/types.d.ts:760-886`) carry **no entry UUID** — only opaque
   `details` / `providerPayload` blobs. Entry UUIDs exist one layer down
   (`SessionEntryBase.id`, `entries.d.ts:3-5`) and `branchEntries: SessionEntry[]`
   is branch lineage (root-to-leaf), not a message→entry index. Aligning by content
   or order is a guess, and the bead's own SAFETY clause ("must yield rather than
   guess" — a wrong firstKeptEntryId corrupts a session) forbids it. Echoing
   preparation's own boundary back is guess-free but contributes nothing.
2. **No summary authorship.** Jev judges; it does not summarize. Candidates: reuse
   `previousSummary` (stale by construction — it is the summary being replaced),
   or emit Jev decision lines ("3 kept, 2 truncated") as the continuation context
   (destroys content, degrades the session). A valid-shaped return with either
   text is well-formed corruption.

So: the only guess-free, non-degrading return is one that adds no value, and every
value-adding return available from the hook's inputs guesses or degrades. The
current behavior — log `would-compact`, yield `undefined` — is the correct fixed
point, not a placeholder.

## Disposition

- **REFUSE:** L4-as-Jev-pruning (no message channel; R21 stands on this half).
- **DEFER:** L4-as-boundary behind one concrete probe — read `SessionMessageEntry`
  linkage in `entries.d.ts` to see whether a message→entry-UUID join exists without
  guessing; if yes, attempt (a) on a throwaway keyed session; if no, the DEFER
  converts to REFUSE. That probe is the follow-up bead, not this one.
- R21 amended (not rewritten) to this narrowed framing the same session.

Boundary: zero live calls; no session touched. All evidence read from the shipped
runtime on disk, which is also the standing rebuke: the .d.ts answered this before
any of us asked.

## Amendment (2026-09-19, conductor rebuttal accepted)

Conductor weakened Reason 1 with file evidence and I verified it rather than
defending: `SessionEntryBase{type,id,parentId,timestamp}` and
`SessionMessageEntry{type:'message', message:AgentMessage}` exist
(`dist/types/session/session-entries.d.ts:49-58`), and the preparation
constructor builds **positional parallel arrays** — `u.push(S)` (entries) alongside
`p.push(v)` (their extracted messages), boundary `h = u[firstKeptEntryIndex].id`,
summarize-set `w = p.slice(0, y)` (`dist/cli.js` preparation builder). So a
message→entry-UUID join is constructible at preparation time, and whether the
hook's `branchEntries` shares those refs is an empirical alignment question, not
a missing channel. **Reason 1 is withdrawn as a refusal ground.** My NO-CLAIM
matches the conductor's: neither of us has tested identity alignment on a real
session.

The settlement now rests on Reason 2 alone, which the conductor concedes as
decisive: `CompactionResult.summary` is a required string and Jev returns typed
judgments, not prose. Any boundary-L4 needs a summarizer Jev is not — which would
make the hook a wrapper around omp's own model. DEFER stands on that ground; the
entry-linkage probe (does `branchEntries` align with the construction arrays by
identity or only structurally?) is still the correct next measurement, but it now
serves a summarizer-gated future, not a mapping impossibility.

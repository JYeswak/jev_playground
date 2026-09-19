---
name: jev-compact
description: Jev-judged pre-compaction for omp sessions. Use when asked about compacting a session with calibrated keep/drop judgment, installing the compaction hook, or reading the compaction decision log.
---

# jev-compact

A `session_before_compact` hook that runs the session's summarizable prefix through
Jev (typed keep/drop questions per tool call) and **measures the verdict while omp's
own summarizer keeps the job**.

## What it is and is not

- It is a **measurement instrument**, not a pruning hook. omp consumes a hook
  compaction as `{summary, firstKeptEntryId, tokensBefore, ...}` — summary plus
  keep-boundary, no pruned-message channel (verified against the shipped runtime).
  Returning a pruned transcript would arrive with undefined summary and boundary,
  so on a compact verdict the hook logs `would-compact N -> M` and yields.
- Claim level: **L3 for fire-plus-refuse** (fires in real sessions; known-bad
  envelopes make it refuse). **L4 is not reached and not reachable on this seam.**
  Never claim a session was shrunk by this hook.
- Fail-safe direction: every path yields (`undefined`). A Jev outage, a malformed
  envelope, or a below-minimum reduction costs a missed optimisation, never context.

## Install

```sh
# from the jev repo, into any repo:
./compaction/install-jev-compact.sh /path/to/repo
```

What lands in the target repo (all reviewable, all project-scoped):

- `.omp/hooks/pre/jev-compact.ts` — 3-line entry, delegates to the factory.
- `.omp/lib/jev-compact/{omp-binding,omp-hook,omp-adapter}.ts` — the tested logic.
- `.omp/lib/jev-compact/node_modules/fast-jev-compaction` — pinned dependency,
  installed from this repo's pinned clone (no registry; no network at install).
- `.omp/skills/jev-compact/` — this skill.

Then: restart the session **with `TYPESAFE_API_KEY` present**, run `/compact`, and
read the decision log. The installer verifies placement plus dependency resolution;
it never claims the seam fires — only a log line proves that.

## Operate

- Key: `TYPESAFE_API_KEY` in the environment only. Keyless sessions load the entry
  but register nothing — by design, and indistinguishable from "not installed"
  except by the log test below.
- Decision log: `~/.jev-compact.log` (`JEV_COMPACT_LOG` relocates it). Outcomes:
  `refused` (known-bad input, never a guess), `passthrough` (outage or below the
  25% reduction floor), `would-compact` (Jev verdict measured, native kept the job).
- Did it fire? `tail ~/.jev-compact.log` after `/compact`. No new line means the
  hook never ran here: wrong session root, keyless session, or omp skipped the
  event — not a verdict.
- Tuning: `minReductionRatio` (default 0.25) in `OmpHookConfig`; below-floor yields
  to the built-in summarizer. Threshold changes are policy changes: record what the
  new floor admits and rejects.

## Known observations (not defects to re-diagnose)

- Each compact logs **twice, ~3ms apart**: the handler appears registered on both
  the hook and extension runner paths. Idempotent and harmless; do not "fix" by
  guessing which registration to cut.
- The transcript arrives at `preparation.messagesToSummarize`, never `event.messages`;
  live messages are `{role, customType, content, ...}` with string-or-parts content
  and sometimes `role: custom`. All of this was learned from production refusals,
  and the adapter normalizes it.
- Cost: one Jev call per compact *attempt with tool calls in the prefix*, not per
  session. A prefix with no tool calls declines with zero requests.

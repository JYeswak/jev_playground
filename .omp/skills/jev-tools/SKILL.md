---
name: jev-tools
description: 'Use when choosing passages, checking claims, screening prompt injection, or reviewing git diffs.'
---

# Jev tools

Choose the tool by the decision you need. These are advisory signals; keep the fail-safe path when Jev is unavailable.

## Trigger Phrases

- choosing passages
- checking claims
- screening prompt injection
- reviewing git diffs

## Organic consumer status (2026-09-25)

No organic trigger is added from this audit. A bounded search of project omp session JSONL files modified in the last 24 hours, excluding probe/smoke/test sessions, found no recurring real-work step that selects passages or checks a qualitative sentence.

The only three matching rerank records were explicit rollout tests, not consumers:
- `~/.omp/profiles/claude/agent/sessions/-Developer-jev/2026-09-25T15-28-20-163Z_01a0d92e-86c3-72dc-ba29-dbb87f90138d.jsonl:5` — prompt says "Do exactly two things" and calls `jev_rerank`.
- `~/.omp/profiles/codex/agent/sessions/-Developer-jev/2026-09-25T15-33-44-451Z_01a0d933-7983-7192-9145-8f6a963f6b07.jsonl:5` — same rollout-test shape.
- `~/.omp/profiles/claude/agent/sessions/-Developer-jev/2026-09-25T15-34-54-984Z_01a0d934-8d08-7228-89ad-3ca2dae9bdb2.jsonl:5` — explicitly says "testing the jev omp tool rollout".

The qualitative-claim search found only the prior L3 test receipt at `~/.omp/profiles/claude/agent/sessions/-Developer-jev/2026-09-24T22-52-06-168Z_01a0d59e-7298-7468-bb25-cf3d166adab7/1.bash.log:153-157`; no non-test claim-check, flag, or screen consumer appeared. These records are evidence of test traffic only, not an organic trigger.

| Tool | Use it when | Measured boundary |
|---|---|---|
| `jev_rerank` | A query has candidate passages and you need their relative order before selecting context. Pass 2–30 non-empty passages. | Only passage reranking is measured. The shipped rubric scored 0.7115 paired accuracy on NevIR (984/1,383); its Noul replacement lost all nine paired comparisons. One or 31 passages are schema refusals before a Jev call. Sources: `docs/demos/upstream-repro/jev-rerank-l3-scifact-20260924.md:5-11,31-36`; `docs/demos/upstream-repro/rerank-nevir-20260924.md:90-111,125-168`. |
| `jev_claim_check` | A qualitative sentence needs checking against the evidence text you already have. Pass the claim and evidence, not a file path. | Claims containing numbers are refused before the API. R83's close-reason design caught 0/31 changed numbers (AUC 0.598); this is not a numeric or exact-value checker. Source: `NEGATIVE_EVIDENCE.md:R83`; `docs/demos/upstream-repro/jev-claim-check-20260924.md:7-18`; `docs/demos/upstream-repro/close-reason-check-20260924.md`. |
| `jev_flag` | You want a human-facing prompt-injection annotation, not an execution gate. Treat `flag` as review-needed, `note` as uncertainty, and `silent` as no annotation. | The underlying news-assistant seat is context-bound: R80 found 175/300 false flags on clean tool results against a ceiling of 15, with 163 caused by the persona framing. Do not attach this signal to ordinary tool output. Source: `NEGATIVE_EVIDENCE.md:R80`; `docs/demos/upstream-repro/jev-k9z5-flag-20260924.md`. |
| `jev_screen` | Text is a user message for the described news assistant and the caller needs `pass`, `flag`, or human `review`. | Cut is p≥0.5 for `flag`; malformed answers are `review`. Context-free variants missed the two-sided bar: plain catch Wilson lower bound 0.758 and criteria 0.654 (<0.80), despite only 12/300 and 4/300 tool false flags. Do not use it as a tool-result hook. Source: `NEGATIVE_EVIDENCE.md:R82`; `docs/demos/upstream-repro/jev-toolout-flag-20260924.md`. |
| `omp-jev-review` | Nothing to invoke: when loaded, it automatically observes `bash` `git diff`/`git show` calls on project code and adds an advisory line to the matching result. | Empty, thin, non-code, and vendored-only diffs are not applicable; scored diff text is capped at 12,000 characters. Boundary p≥0.9 appends once, never blocks; the draw fired on 3/125 real code diffs (2.4%), and accuracy is unmeasured. Source: `docs/demos/upstream-repro/omp-jev-review-advisory-20260925.md:8-21,32-37,43-65`; `work/omp-jev-review/src/index.ts:40,74-76,153`. |

## Shared operating rules

- A `NOT_RUN`, `review_error`, or malformed/refused result is not a pass. Preserve the safe behavior and report the reason.
- `jev_flag`, `jev_screen`, and `omp-jev-review` are advisory. They never authorize, block, or merge code by themselves.
- The measurements above are scope limits, not general accuracy claims: keep the cited state shape, model pin (`jev-1.13.0`), and corpus boundary visible when reporting a result.

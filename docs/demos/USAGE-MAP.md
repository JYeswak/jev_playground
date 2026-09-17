# What people actually use Jev for — mined 2026-09-17/18

Sources: lane checkouts at pinned SHAs (see bottom). Every entry quotes the
repo's own measured claim, not our paraphrase. Purpose: feed the demo duel —
each pattern is a candidate installable demo.

Core shape (awesome-jev-by-typesafe@d57f5ce): "text or JSON state + typed
questions → constrained answers + probabilities → your code." Jev never
generates operative text; code owns control flow, thresholds, side effects.

## 1. Pre-context screening (keep bad bytes out)
- jev-mcp@6ec5efc `jev_screen`: judges content BEFORE it enters context.
  Measured: blocked a pricing page with a hidden "ignore your instructions"
  note at injection probability 0.99, while still reading it as a real page.
- Demo angle: screen hook for omp context admission (files, fetches, pastes).

## 2. Claim verification (check words against evidence)
- jev-mcp@6ec5efc `jev_verify`: checks claims against evidence. Measured:
  caught a contradicted claim at confidence 1.0 against a city ordinance.
- Demo angle: claim-check helper for our own workflow (verify working points
  against cited evidence before writing them down). Dogfoods lane discipline.

## 3. Candidate ranking without embeddings
- jev-mcp@6ec5efc `jev_find`: ranks candidates by meaning, no embeddings.
  Measured: 3 files on caching-vs-infra-cost, right pick at 1.0.
- jev-rerank-bench@cd9a35b: Jev rubric nDCG@10 0.692 vs Cohere Pro 0.691
  (1,617 questions, 8 datasets); Jev better on negation; $0.45 vs $2.51 per
  1k queries; 422ms vs 844ms per query.
- skillranker@3fe85c4: same pattern wired to skill selection for a live session.
- Demo angle: BM25→Jev-rubric rerank recipe with measured nDCG on a sample slice.

## 4. Per-turn model routing (spend frontier only when needed)
- jev-router@86660a0: `jev-claude` / `jev-codex` preserve native CLI, Jev picks
  the tier per fresh turn.
- jev-codex-router@8292b51: measured −60% vs full-frontier on a 7-day replay of
  237 real turns (BACKTEST.md); $0.00003 + 0.6s per decision; fail-open; kill
  switch; local decision log for calibration.
- Demo angle: backtest harness for OUR omp logs — replay turns, measure what
  routing would have saved. Most directly valuable to us.

## 5. Continuous review signal (agent still fixes)
- jev-review@57690af: one MCP tool, scalar scores across correctness/complexity/
  changeability/modularity/tests/security; local process, no backend, key stays
  on machine.
- Demo angle: review-signal hook as advisory lane-gate input alongside ubs.

## 6. Completion judging (independent done/not-done)
- foreman@2c43982: Codex worker builds, Foreman+Jev independently assesses
  complete / requirements-met / tests-sufficient / verify-needed / human-needed.
- Demo angle: foreman-lite wrapper for lane tasks (verdict + evidence checklist).

## 7. Failure attribution (who/when/what broke)
- jev-agent-failure-benchmark@4d46af7: on 6,257 Who&When-Pro text traces Jev
  beats GPT-5.4 on every axis (Who 73.4, When 76.4, All 31.3) for ~$1.28 total
  (Jev bills input only; output tokens free).
- Demo angle: attribution probe for failed agent runs (ours fail often enough).

## 8. Commit triage (security-relevant history)
- commit-miner@977617e: classifies diffs+messages (bug/security/CWE/change type).
  `scan . -n 500`, installable via cargo.
- Demo angle: scan lane-adjacent repos for security fixes before depending on them.

## 9. Zero-label classification (questions beat labels)
- jev-spam-eval@76ef183: plain-English question, no labels. TF-IDF needed
  100–10,000 own-distribution labels to match; on shifted mail TF-IDF fell 20+
  points behind.
- jev-phishing-bench@1d56e8c: Jev verdict alone loses on accuracy (62.6 vs 81.3)
  but 5 signal questions → logistic regression hits 95.1%, AUROC 0.988,
  ECE 0.027. Signals beat verdicts; fixed rules on strong signals need no fitting
  (free-hosting rule alone: 89.5%).
- Demo angle: zero-label classifier starter (question + calibration report) AND
  the meta-lesson for our A/B: ask signals, fit tiny models, don't trust verdicts.

## 10. Browser action selection (one decision per step)
- jev-ultrafast@452c1ad: Jev picks operation+element per observation; small LLM
  writes text only for TYPE_TEXT. Zürich→London Flights in 7.1s.
- Demo angle: none immediate (needs browser harness); watch for the pattern
  (constrain-then-delegate) in our hook designs.

## 11. System1/System2 gating (allow/confirm/block/warn/steer)
- bicameral@3bea244: System 2 writes code, Jev scores, deterministic policy maps
  to actions. "This is not a sandbox" — isolation stays with containers.
- s1-rs@b916897: Rust derives turn enums into Choice/Score/Noul questions.
- Demo angle: policy-gate template (scores → actions in code, thresholds named).

## 12. Guardrail benchmarks (blind, public corpora)
- jev-sec-bench@fdb16b9: injection (662 deepset msgs) + vuln-code (200 pairs),
  blind, with TUI dashboard.
- Demo angle: our gates' future — blind held-out sets for hook quality (L2/L3).

## 13. Calibration discipline (probabilities must mean something)
- foundation/ (ours): ECE 0.061, Brier 0.020, Noul 58/60, Choice 19/20.
- phishing-bench calibration audit: ECE, bins, flip rates between passes.
- Demo angle: portable calibration micro-harness (<100 lines, any Noul/Choice).

## 14. Context compaction (prune, don't summarize)
- fast-jev-compaction@6e1da50 + our A/B: 45% reduction, zero text loss — but
  preserve-instructed summary won 3–1 on fact recall at 1/3 the bytes.
- Standing lesson: relevance-pruning loses verbatim recall; pair with fact ledger
  or yield to summarization for fact-dense transcripts.

## SHAs (all pinned 2026-09-18)
jev-mcp 6ec5efc · jev-review 57690af · jev-ultrafast 452c1ad · jev-router 86660a0 ·
jev-codex-router 8292b51 · jev-rerank-bench cd9a35b · jev-phishing-bench 1d56e8c ·
jev-sec-bench fdb16b9 · jev-spam-eval 76ef183 · jev-agent-failure-benchmark 4d46af7 ·
typesafe-ai-benchmark e94fcda · commit-miner 977617e · foreman 2c43982 ·
bicameral 3bea244 · s1-rs b916897 · system-one-adapter-python 0bb819b ·
awesome-jev-by-typesafe d57f5ce · fast-jev-compaction 6e1da50 · skillranker 3fe85c4

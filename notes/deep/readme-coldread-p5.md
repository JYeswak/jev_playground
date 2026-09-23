# README cold read (U3, plan W6.2 acceptance d)

Method: one-file subagent (ColdRead3, task backend) given ONLY the README text — no repo access. Two earlier attempts failed on infrastructure (scout backend model `ollama/qwen3.8:27b-mlx` 404; first brief carried a PLACEHOLDER instead of the text — both my defects, recorded here). The task-backend reader returned four quoted answers plus UNRESOLVABLE lists. I checked every answer against the tree below.

## The reader's answers (all four correct, all quotes traceable)

1. Repository: "Jev answers typed questions about a state with calibrated numbers" + the regex-vs-number mission sentence. Verified: matches the lane's stated purpose.
2. First run: `node demos/guard/demo.mjs`, `bash scripts/quickstart.sh`, Node 20+, no key. Verified: both exist and both exit 0 keyless (guard rc=0 re-run this drive; quickstart.sh rc=0, 12s, output ends on the lane-status pointer).
3. Findings: 639/662 Jev, 558 grok-4, 579 Haiku; the tool-call-harm loss. Verified: `analyze_diff.py` rc=0 reproduces all three at the pin.
4. Non-claims: fixtures show policy not model; smokes are directions not benchmarks; file beats page. Verified present verbatim.

## Misled nowhere; dangling nothing that matters

Every file/command reference the reader flagged UNRESOLVABLE resolves on disk: 20 `demos/*/demo.mjs` (matches "twenty"), 17 `live-receipt.json` (matches "seventeen"), `demos/LIVE.md`, `demos/START.md`, `work/jev-client/README.md`, `.omp/tools/jev-screen.ts`, `DIFF-RECEIPT.json`, `analyze_diff.py`, seat-guard suite (9/9), `verify-claim.mjs` (rc=0), 17 `gates.d/*.sh` (matches "seventeen stages"), `GATES.md`, `NEGATIVE_EVIDENCE.md`, `PLAN-DEEP-KIT-20260922.md`, `LICENSE` (MIT). The 8/5/4 live-smoke split recounts exactly from LIVE.md notes (8 differ, 5 same, 4 live-only). The stage-80 paragraph matches the current tree (16/1 post-35629b2); the "As of 2026-09-22" date-stamp carries it honestly.

## What the text alone cannot back (genuinely external)

`docs.typesafe.ai` model-behavior claims ("does not generate text"), the `jev-sec-bench` corpus contents, github repo state, and `omp.sh` — all correctly outside a one-file read. The 639/558/579 and ECE/Brier numbers are maintainer claims from text alone; this drive executed the first set and reproduced the second live (ECE 0.062 vs 0.0614), which is exactly the verification the README invites ("Re-run the command").

## Reader-calibration finding (about the exercise, not the README)

The reader marked its own correctly-extracted answers as UNRESOLVABLE factual claims — it did not discriminate "supported by this text" from "backed by the world." A cold reader that flags everything flags nothing; the useful signal was confined to its four quoted answers, which were all right. Next cold read needs a reader that separates internal support from external backing, or the (a)/(b) lists are noise.

## Cosmetic

README line 5 wraps the hero image in `__omp_shell(...)` markup a cold reader must skip over; harmless, flagged for the W6.2 rewrite pass, not changed here.

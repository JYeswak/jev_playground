# §10 adoption record — what persona-clone already carries (ADOPTED, not authored)

Source: `~/.agents/skills/persona-clone/references/eval_harness.md` (read 2026-09-20;
grep for constant|baseline|random|majority|join returns 0 — the gap below is real).

Adopted verbatim as pattern (not copied as text):

1. **Separate judge.** PersonaGym rule: never let the generator grade itself. The
   judge is a distinct invocation with a fixed grading prompt — not the process
   that generated the answer.
2. **Golden vs trap sets.** Golden = answerable from corpus (score GROUNDING +
   FABRICATION [inverted: 5 = zero invented] + TONE); a golden pleading ignorance
   where the corpus HAS the answer is a false negative (retrieval bug, not honesty).
   Trap = unanswerable (must REFUSE / admit gap); a trap that answers is leak
   (TRAP-LEAK named). Judge output brace-free (`GROUNDING: <1-5>` lines).
3. **Report to file** (`eval_report.txt`), per-dimension averages vs targets,
   JUDGE-FAIL / TRAP-LEAK / GOLDEN-WEAK lists. Grind loop: fix weakest, re-run.
4. **Prompt-echo pitfall:** grade the cleaned answer, never the echoed prompt
   (mention-vs-use's cousin — c6eb7ab).

## What persona-clone lacks (added by this section, from §6)

- **Constant baseline** (`ownConstant`): majority-label share every verdict must
  beat. No analogue exists in the harness.
- **Random-judge control** (`randomBaseline`): seeded chance floor. No analogue.
- **Join** (`joinOutcomes` + selector verification + zero-hit REFUSE): no analogue;
  golden rows joined to corpus-source records instead of eyeballed.

Live in `demo.mjs` + `adopt.test.mjs` in this package.

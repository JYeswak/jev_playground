# P73 — Wave B remainder (8, 9, 10) then Wave E (23, 24), P1–P12 each

Waves A, C and D are closed. §7 is yours and already done; §21 and §22 are closed by another
agent; §6 passed. These five are what remain of the 24.

`%71` is on R41's trigger (the interpreter-vs-payload stripper). Do not touch
`work/toolcall-judge-v3/rules-v4.mjs` or `work/omp-harm-rule/harm-rule.ts` — they are that unit's
ground and both were reverted to a known-good state this turn.

## Sections

**8 jev-prevalence-first** — prevalence cell mandatory; authored ≠ real. Two free base rates
already measured: `bv --robot-triage` gives 23 of 50 actionable (46%), and §19 gives 0 of 20
packages promoted. The sharper finding from §14e is **read the near-threshold count BEFORE
prevalence** — 197 of 400 rows sat inside ±0.10 of the 0.50 line, so half the verdicts were made
by our threshold rather than by Jev. A prevalence-first skill that does not also demand the
near-threshold column is incomplete.

**9 SDK-SURFACE field traps** — Choice/Score/Noul field names; refuse silent null scoring.
Live trap already proven and costly: `recording()` filed every SUCCESSFUL `askJevChoice` call as
`ok:false`, because that asker returns `{choice, confidence, probabilities}` and **no `scores`**.
Four extensions' good calls would have entered the register as errors, silently. `recordingChoice`
fixed it and test 12 is a planted negative asserting the old wrapper misfiles it. **That is the
section's core evidence — start there, not from the SDK docs.** Also rule on whether the absence
of a `.score` caller in `jev-client` is a gap or a correct refusal.

**10 random-judge + outcome-join** — **ADOPT, do not author.** `persona-clone`'s
`references/eval_harness.md` already carries "Why a separate judge", the PersonaGym rule "never
let the generator judge itself", and golden+trap sets with TRAP-LEAK named. It has no constant
baseline, no random-judge control and no join, so it is complementary to §6's delta, which you
built. Add only what it lacks.

**23 dcg explain-before-override** — safe alternative path; explicit `git add <path>`. dcg
refused five commands tonight and was right every time: `rm -rf` on a home-adjacent path, a
recursive delete, `find -delete`, `git stash` worktree-wide, and `git checkout --` discard. I
worked around the last two with explicit copies rather than reshaping to evade, which is the
behaviour this section should encode.

**24 infisical placeholder cleanup** — delete leftover `<id>`; inject one-liner only. Note the
working key path in use all night:
`infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`.

## Constraints

- **Commit on create**; staging is not protection.
- Quote live numbers with pinned inputs, or label them live-and-monotonic — four reproducibility
  defects tonight, all one shape.
- **Grep the directory, not the file** — a per-package probe assuming one canonical entry file
  cost me a wrong census.
- Test file + `TESTS.md` entry in the same commit. Exit codes unpiped. No Codex.

One ledger line per section into `docs/demos/upstream-repro/commit-learnings-20260919.md`:
`SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`. **Batch the ledger
appends into one commit per wave** — 12 separate append commits inflated PROCESS in honesty pass 5.

FAIL and REFUSE are real outcomes; a fabricated PASS is not.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between them.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-S<n>-<PASS|FAIL>: <receipt path> <sha>. NEXT <section>. NO-CLAIM <limit>."`

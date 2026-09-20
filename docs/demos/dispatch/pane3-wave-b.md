# P3 — WAVE B (sections 6–10), P1–P12 on each

`jev-vbh.2` verified and accepted: I read `question-writing-loop-20260920.md` (`d9ad895`) and the
verdicts hold up — `dependency_freshness_lag` 8/8 tuned + 4/4 fresh, `verification_weakened` 8/8 +
4/4 fresh, both computed by `gradeQuestion`, not chosen. 24 live calls, five passes at zero calls,
and you flagged the thin basis and the labeller-stated-pins caveat yourself. That is the standard.

**`verification_weakened` is in the control-tampering family — our one surviving seat (`6830ce2`).**
I am deepening it myself as section 14; do not duplicate that.

## Read before starting — two sections are ADOPT, not AUTHOR

A non-author probe (recorded in `commit-learnings-20260919.md` §5c–5e, verified by me):

- **§6 jev-eval-honesty** — `jev-vbh.3` is **RESCOPED**. `~/.claude/skills/evaluation-framework`
  already covers rubric design, the 5-step process, mode selection, CI thresholds, 10
  anti-patterns, Krippendorff-alpha. Build ONLY the three absent mechanisms: **outcome join**
  (with selector verification + zero-hit guard), **co-presence**, **random-judge / own-constant
  calibration**. Its "no baseline" anti-pattern means a *regression* baseline — a different object
  from a constant baseline, and it would not have caught the commit judge going
  DEGENERATE/WEAK/WEAK.
- **§10 random-judge + outcome-join** — `persona-clone`'s `references/eval_harness.md` already
  carries "Why a separate judge", the PersonaGym "never let the generator judge itself" rule, and
  golden+trap sets with TRAP-LEAK named. **Adopt it.** It has no constant baseline, no
  random-judge control and no join, so it is complementary to §6's delta.

Trap worth knowing: `jsm install e292b255-…` FAILS — "Directory exists but is not tracked by jsm".
The skill is on disk since 2026-04-23 and invisible to `jsm list` (150 entries, 0 matches). Read
it from `~/.claude/skills/evaluation-framework/` directly. Do not `--force`; the on-disk copy may
be a local variant.

## Your sections

6. **jev-eval-honesty** — the three mechanisms above. Nothing else.
7. **jev-silent-register** — `jev-vbh.7` is CLOSED and shipped: `work/jev-score-register/`
   (`8e2d533`), `omp-jev-commit` wired, replay reads 43 rows with `api calls made: 0`. Your job is
   the section's remaining half — the lost `pi.on` / glob `*.{ts,js}` / neighbour-fires / lab≠working
   traps the plan names. Verify the register survives them; report FAIL if not.
8. **jev-prevalence-first** — prevalence cell mandatory; authored≠real. Note `bv --robot-triage`
   gives a base rate for free (23 of 50 actionable = 46%).
9. **SDK-SURFACE field traps** — Choice/Score/Noul field names; refuse silent null scoring. Live
   trap already recorded: `jev-client` sanctions only `askJev` + `askJevChoice`, so a `.score`
   caller does not exist yet; your §9 should say whether that is a gap or a correct refusal.
10. **random-judge + outcome-join** — adopt per above, then add what persona-clone lacks.

## Constraints, all measured

- P7 needs a **quoted live row**; P10 a prevalence cell or the literal `UNKNOWN`; P11 a planted
  negative that fires.
- Hand-built corpora failed to transfer **six times**. `node work/toolcall-judge-v3/harvest-allowed.mjs`
  regenerates 77,767 real commands.
- **Stage every new file in the same breath as creating it.** I lost a finished, passing gate
  stage tonight to a peer merge because it sat untracked for ten minutes (§22c).
- Test file + `TESTS.md` entry in the same commit. No Codex.
- The tree may be on a peer branch (`fix/pr24-rebase`); check `git branch --show-current` before
  assuming `main`.

One ledger line per section: `SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`.
A FAIL line carries the next command.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between them.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-WAVEB-S<n>-<PASS|FAIL>: <receipt path> <sha>. NEXT <section>. NO-CLAIM <limit>."`

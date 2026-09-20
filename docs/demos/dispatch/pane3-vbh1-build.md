# P3 (MUSE) — Build the thing you just scoped: `jev-vbh.1`, R44's open trigger

Your rescope is accepted and it is the right call. CLOSE-as-satisfied would have been wrong for
the reason you gave — §21 shipped a REJECT plus a gate, while vbh.1's WHAT was to BUILD; those are
opposites, so the bead is not satisfied, its premise is refused. And REFUSE would have discarded
the one live thread in this territory. You are now working the bead you rescoped, which is the
correct sequence.

## The problem, exactly

**Distinguish a command string EXECUTED inside an interpreter program from one PASSED AS DATA
within it.**

State after R44 (`e33bd5d`), which you should not re-derive:

```
organic fires  28 -> 5     precision still 0
```

All five survivors are our own probes shaped like `node -e "... 'some dangerous command' ..."` —
the dangerous text is a **string literal inside a `-e` program**. The positional rule is right to
treat `-e` as code; the code merely mentions a command as data. **Mention-vs-use retreated one
level rather than dying**, which is the twentieth instance of this defect tonight and the only one
still open.

## Why this is hard, so you can refuse honestly if it is

Inside `node -e '...'`, `execSync("rm -rf /")` is executed and `const s = "rm -rf /"` is not, and
telling them apart is a parsing problem, not a regex problem. A cheap approximation might be
"does the literal appear as an argument to an exec-family call in the program text" — that is
narrow, testable, and may be enough for our corpus. **It may also be the wrong shape entirely, and
saying so with evidence is a full-credit outcome.**

## ACCEPTANCE — all three, exactly as R44 records them

1. `node work/omp-harm-rule/organic-fires.mjs` → fires **0** on the same denominator (~81k).
2. `node work/omp-harm-rule/verify-claim.mjs` → still `VERDICT: REPRODUCIBLE COMMITTED CORPUS`.
   **Run the unmodified rule as your own control in the same session** — do not trust my numbers.
3. `node --test work/toolcall-judge-v3/rules-v4.test.mjs` → green, with a NEW arm pinning an
   executed literal as firing and a planted negative pinning a data literal as silent.

Any one failing → **append the result to R44 and the trigger stands.** That is a real outcome and
this lane has scored several of them tonight. My own first repair took the suite from 10/10 to
4/10 and was reverted; a worse rule shipped is worse than no rule.

## Constraints

- Do NOT re-run the §21 ceiling measurement.
- Commit on create — staging is not protection.
- Test file + `TESTS.md` entry in the same commit, facts from running the file alone.
- Exit codes unpiped; `cmd | tail` reports tail's status and has bitten me twice.
- Note R44's numbering: a peer holds R41, my entries are R44. Cite R44.
- No Codex. Panes 1 and 2 are `WAIT_FOR_RESET` on quota, so you are alone for now — prefer a
  partial with a receipt over a complete unit that does not land.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-VBH1-<DONE|REFUSED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

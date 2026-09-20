# P3 — Sweep the front door: which README claims are still true?

`README.md` is 886 lines and it is what a stranger reads first. **Four of its numbers were stale
tonight and every one was found by accident**, while chasing something else: 25 verdict rows for
33, 12 gate stages for 13, and the ledger at 31 when it holds 50. Nobody has ever swept it
deliberately. That is rung 1.

Stage 97 now covers exactly three numeral families (stage count, verdict rows, the cleared/held/
ruled-out parenthetical) and **free prose is out of scope by ruling**. So everything below is
unguarded by construction — the gate cannot help you here and is not supposed to.

## The unit

Work top to bottom. For each **checkable factual claim** — a count, a ratio, a file path, a
command, a "we did X" — mark it:

- **CONFIRMED** with the command that settled it;
- **STALE** with the true value, and fix it;
- **UNVERIFIABLE** with why (needs a key, needs another machine, denominator lost).

Prioritise in this order, because this is where the damage lands:

1. **Claims with a number in them.** Especially any denominator: this repo has a measured
   live-target class where unpinned denominators drift (`77,767`→`78,242`, `matched=15525`→`15618`).
   A share whose denominator moved is a wrong share even if nobody edited the sentence.
2. **Every runnable command** in a fenced block. Run it. The `RULES.md` stranger test found two
   of nine commands depended on gitignored artifacts a fresh clone cannot produce — the README has
   far more commands than that, and the same hazard.
3. **Every claim of the form "we found / we shipped / it fires"** — the mention-vs-use family has
   25 instances this session, including a hook that never emitted a row while 13 tests passed.
   If the README says something fires, check that it fires.
4. **Every internal link and receipt path.** `lane-status.sh` integrity-checks STATUS receipts
   only; README links are unchecked.

## Known traps, so you do not pay for them twice

- **Exit codes unpiped.** `cmd | tail` reports tail's status; that cost two false reads tonight.
- **`grep -c foo # 0` exits 1** — zero matches is grep's failure status. The README documents this
  about one of its own commands, which is exactly the kind of claim to re-run rather than trust.
- **My own greps have been the broken instrument three times in two hours** (a too-narrow caveat
  pattern, an env var where the script takes a positional, `grep -c 'arm'` returning 1 against 5
  real arms). Prefer reading the file over a clever pattern when the count matters.
- Do not "fix" a number by arithmetic. Re-derive it from the source the sentence claims.

## ACCEPTANCE

`docs/demos/upstream-repro/readme-claim-sweep-20260920.md`: a table of every claim checked with
its verdict and settling command, the fixes applied, and **a headline count — how many of N
checkable claims were stale.** That number is the product: it tells a reader how much of our
front door to trust, and it is the first time anyone will have measured it.

If the sweep is too large for one unit, **split by section and ship the first half with a
receipt** — a partial with a receipt beats a complete unit that never lands. Say where you stopped.

Stage 97 and the full suite must stay green. Exit codes unpiped. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-README-SWEEP-<DONE|PARTIAL>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

# P3 — Two units: rule the stage-97 gap, then check the prose I did not

## Unit 1 — Is stage 97's selector gap BLOCKING, or is a refusal the right answer?

`foundation/gates.d/97-readme-counts.sh` exists to catch stale typed counts. Its own commit
subject (`a8a6f24`) reads *"catches the typed count that goes stale, and caught its own arrival"*.
This tick, **three stale counts went past it while all 13 stages were green**:

```
README line 105   "25 verdict rows (7 cleared, 9 held, 8 ruled out)"   actual 33 (8/13/12)
README line 106   "12 gate stages green"                               actual 13
README line 827   "25 verdict rows"                                    actual 33
```

Mechanism: line 73 is `grep -q "$word stages"` — it matches the **spelled-out** form
("Thirteen stages") only. The README states the same fact in **numerals** elsewhere, and verdict-row
counts are not checked at all.

I fixed the README (already committed). **I did not touch the gate, because I tripped it and
self-approving a widening of the gate you just tripped is the move this lane refuses.**

Rule one of three, with evidence:

- **WIDEN** — the numeral form is a real blocking gap; add it to the existing arm. Then the
  Creation Gate applies in full: consumer, gate, **observed** defect, retirement condition. The
  observed defect is above, so this is the one option where the paperwork is already half done.
- **REFUSE WITH A TRIGGER** — the `R18` shape. Argue that chasing every restatement of a number
  through prose false-positives by construction (a README legitimately says "12" about other
  things), name the trigger that would change the answer, and file it in `NEGATIVE_EVIDENCE.md`.
  **Use R45 or higher** — R41/R42/R43 have collisions from concurrent panes and R44 is taken.
- **SCOPE IT** — the honest middle: check numerals only for the two facts that have a machine
  source (`stage count` from `foundation/gates.d/*.sh`, `verdict rows` from `STATUS.tsv`), and
  say explicitly that free prose is out of scope forever.

**I lean SCOPE IT and I am probably wrong about something.** Both derived facts have an exact
machine source, which is what separates them from prose — but you have the evidence, not me.
Whatever you rule, the gate's header must end up stating what it actually checks; it currently
implies more.

If you widen or scope: `--selftest` must gain a planted arm that fires RED on the exact defect
that escaped, and 13 stages must stay green in both modes.

## Unit 2 — Check the prose I changed four numbers inside

My commit's NO-CLAIM: *"I changed four numbers and the sentences around them are unverified."*
Honesty pass 7 named adjacent-text failure as my top defect this window — **the "Eight rules"
header and the STATUS backfill were both cases of me verifying a number and not reading the
sentence containing it.** So do not trust that I got the surrounding claims right.

At README lines 105–110, 784–790, 825–831, verify against artifacts:

- *"31 dead-end ledger entries each with a reopen condition"* — count entries in
  `NEGATIVE_EVIDENCE.md` and check each carries a reopen/retry condition. **Note the known ID
  collisions (R41×2, R42×3, R43×2) — a naive count of IDs and a count of entries will differ, and
  which one the README means is itself the question.**
- *"one promotion awarded and retracted the same day"* — does the Foreman story hold?
- *"Observer (B) mechanism MET at n=1 lab; working-profile dogfood OPEN"* — still true after the
  `safeAppend` fix?
- The parenthetical breakdown `(8 cleared, 13 held, 12 ruled out)` sums to 33. Confirm against
  `STATUS.tsv` yourself rather than trusting my arithmetic.

Report each as CONFIRMED / STALE / UNVERIFIABLE with the command that settled it. Fix STALE ones.

## Both units

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them. When your queue drains, run `br ready`, claim the highest-priority bead you did not author,
and work it.

Exit codes unpiped. Commit on create. Test file and `TESTS.md` entry in the same commit.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

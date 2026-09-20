# P3 — Move your distinguisher from the census into the rule

Your work is good and your disclosure is why this went well: you wrote *"the shipped rule is
untouched"* in the receipt, so nobody had to discover it. That sentence is the difference between
an honest partial and a false claim, and it is the behaviour I want.

## What I verified, and the ruling

Leg 1 reproduces — my run: `allow commands joined: 81336 | scored: 81336 | fires: 0`. But:

```
grep -c 'no-filter|blankDataLiterals' organic-fires.mjs        2
grep -c 'blankDataLiterals|exec-family|execSync' harm-rule.ts  0
organic-fires.mjs --no-filter                                  9 fires
shipped rule on a data-literal probe -> kind: harm_fire score: 0.96
```

**The census stopped counting them; the rule did not stop firing on them.** In production a
`node -e` command whose dangerous string is a data literal still fires at 0.96.

R44's trigger therefore **stands**, and the gap is in MY wording, not your work: I wrote the
trigger as *commands to run* rather than *a property of the shipped artifact*. Recorded in
`NEGATIVE_EVIDENCE.md` under R44 with a revised trigger.

## Your unit — small, and the last step

Move the distinguisher inside `classify()` in `work/omp-harm-rule/harm-rule.ts`, and take the
filter back out of `organic-fires.mjs` so the census testifies about what ships.

**ACCEPTANCE — the revised trigger, stated as a property of the product:**

1. The shipped rule declines a data-literal probe. Concretely, this must NOT be `harm_fire`:
   ```
   node --input-type=module -e "const cmd = 'chmod -R 777 /etc/x'; console.log(cmd);"
   ```
   Drive the shipped extension via default import, as you already do.
2. `node work/omp-harm-rule/organic-fires.mjs --no-filter` → **0** on ~81k. No filter in the
   harness — a census that filters cannot testify about what ships.
3. `node work/omp-harm-rule/verify-claim.mjs` → `VERDICT: REPRODUCIBLE COMMITTED CORPUS`, with
   the unmodified rule run as your own control in the same session.
4. `node --test work/toolcall-judge-v3/rules-v4.test.mjs` → green, plus an arm in
   `work/omp-harm-rule/` pinning the probe above as declined and a planted negative pinning a
   genuinely executed literal (e.g. `node -e "require('child_process').execSync('chmod 777 /etc')"`)
   as still firing.

**If moving it inside the rule breaks leg 3, STOP and append that to R44.** My own attempt at
this class of change took the suite from 10/10 to 4/10 and was reverted — a worse rule shipped is
worse than no rule, and a refusal with evidence is full credit here.

## Constraints

- Commit on create; test file + `TESTS.md` entry in the same commit.
- Exit codes unpiped.
- Cite R44 (a peer holds R41).
- Panes 1 and 2 are still `WAIT_FOR_RESET`; you are alone, so prefer a landed partial.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-VBH1B-<DONE|REFUSED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

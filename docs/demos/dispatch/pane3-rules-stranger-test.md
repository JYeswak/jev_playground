# P3 — The stranger test on `docs/RULES.md`

`docs/RULES.md` is the artifact most likely to be read by someone outside this lane: nine rules,
nine runnable commands, 85 lines. **Every command on it has only ever been run by the person who
put it there.** That is the definition of unreviewed, and rung 1 says take it.

## The page's own standard, turned on the page

Its header says: *"Every one names the commit that produced it and a command you can run now. A
rule with no runnable command is not on this page."* Test exactly that claim.

For each of the nine rules:

1. **Run the command verbatim**, from the repo root, as a stranger would. Some have two.
2. **Does the output demonstrate the rule?** Not "does it exit 0" — does a reader see the thing
   the sentence claims? Rule 2's comment says *"73.7% saved, 31.1% of substantive reuse lost"*;
   if the output no longer prints those columns, the rule is undemonstrated even though the
   command works.
3. **Does the cited sha resolve** (`git cat-file -e <sha>^{commit}`)?
4. **Would the command work on a FRESH CLONE?** This is the one I expect to fail somewhere.
   Several depend on gitignored artifacts — `real-allowed.json` is regenerable but absent,
   `scores.jsonl` is local-only. A command that needs a file a stranger does not have is a
   broken promise, even if it runs here.

## Known hazards, so you do not rediscover them

- `work/toolcall-judge-v3/real-allowed.json` is **gitignored**; regenerate with
  `node work/toolcall-judge-v3/harvest-allowed.mjs` (~50s). A peer once regenerated it with a
  limit argument and left 30 records, which made a downstream run print `NaN%`.
- Exit codes **unpiped** — `cmd | tail` reports tail's status and has produced two false reads
  tonight.
- Rule 1's command reads a 338MB session and takes ~9s. That is deliberate: the fast fixture has
  6 scored results and the oracle reports ADOPT on it, which the rules themselves reject.

## ACCEPTANCE

A table, one row per rule: `RUNS` / `RUNS-BUT-DOES-NOT-DEMONSTRATE` / `BROKEN`, plus
`FRESH-CLONE-OK` yes/no, plus the quoted output line that settles it. Then one verdict:
**is this page true as written?**

Fix what is cheaply fixable (a stale column reference, a wrong path). For anything needing a
committed fixture, **report it rather than committing a large artifact** — and say what the
smallest honest fixture would be.

**A clean pass is a real outcome.** So is "three of nine do not work on a fresh clone", which
would be more valuable, and which I half expect.

## Constraints

- No new Jev calls needed; every rule command is offline or reads recorded data.
- Commit on create; exit codes unpiped; cite R44/R6 numbering (a peer holds R41).
- If you change the page, keep it at nine rules — the cap is the point, and a tenth displaces one.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-RULESTEST-<TRUE|MIXED|FALSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

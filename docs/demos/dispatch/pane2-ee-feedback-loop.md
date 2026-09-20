# P2 — close the loop: detect → recall → suggest → write back. The tools found the path.

I ran `ripwire`, `ast-grep` and `rg` over the repo instead of guessing. Findings, with the
commands so you can re-derive them:

```
ripwire . --for="wire ee preflight into the guard hook"
  r3   compaction/src/omp-binding.ts  registerOmpCompactionHookFromEnv   cx=5  in=2
  r6   compaction/src/omp-hook.ts     registerOmpHook(pi, deps)          cx=6  ccx=7
  r7   work/omp-guard-rule/guard-rule.ts  classify(command)              cx=12
  r10  work/omp-guard-rule/golden.mjs     mock pi {on, appendEntry}

ast-grep --lang ts -p 'pi.appendEntry($$$ARGS)'   -> the decision-row shape, e.g. omp-jev-jargon
rg -l 'appendEntry' work/ | wc -l                 -> 57 files
```

**Nothing needs inventing.** `registerOmpHook(pi, deps)` in `compaction/src/omp-hook.ts` is a
tested, live registration pattern with a typed `OmpHookApi`, defaults, and config resolution —
and 57 files already emit decision rows. The guard is the 58th; the loop is three small edits.

## Unit 1 — repair `ee`, because the recall half is dead

`ee preflight check '<cmd>' --json` returns `{"matches":[],"matchedMemories":[]}` — **the
surface exists, is queryable per command, and is empty.** Writing to it fails:
`EE-E040 migration_drift`, and the error names its own repair. Run `ee doctor --fix-plan --json`
(4 of 5 issues fixable), apply, then prove the round trip:

```
ee remember --level procedural "<rule>"      # must succeed
ee preflight check '<the command>' --json    # must return a non-empty match
```

**If the round trip cannot be made to work, STOP and report `BLOCKED`** — everything below
depends on it and a loop with a dead memory is worse than no loop, because it looks wired.

## Unit 2 — seed the memory from defects we already measured

We have 21 recorded defect classes and ~50 `NEGATIVE_EVIDENCE` entries. **Seed only the ones with
a command-shaped trigger and a corrected command** — a rule that cannot name the right way to do
it is advice, not memory. Start with these, each carrying its measured instance count:

- pipe-then-read-rc → *"4 measured false reads; run unpiped, `cmd >/tmp/out 2>&1; echo rc=$?`"*
- `grep` as proof → *"zero matches exits 1 and reads as clean; `scripts/vgrep.sh` exits 3"*
- env-var where argv is documented → *"2 instances; read the Usage header first"*
- digest pinned to a live file → *"took the lane RED; extract a stable per-section receipt"*

**Do not bulk-import all 50.** A memory store full of unmatched rules is the same wallpaper
problem as a guard that fires on every command.

## Unit 3 — wire recall into the fire, and the write-back

In `guard-rule.ts`, on a fire: call `ee preflight check` for the command, and if it returns
matches, **put the matched rule's corrected command into the decision row** as `suggestion`, and
surface it in the warning text. The row already carries `class`, `command`, `toolCallId` — this
adds the one field that turns *"you did it wrong"* into *"here is the right way, and you did
this N times before"*.

Write-back is the other half: **when a defect is confirmed** (a ruling lands, a gate goes red
for a real reason), one `ee remember --level procedural` call records it. That is what makes
each call feed the system instead of only being judged by it.

**Keep `ee` out of the hot path**: if `ee` is slow or absent the hook must still fire, with the
generic text and a `suggestion:null`. A guard that breaks when its enrichment is unavailable is
worse than one that degrades.

## The Jev question, answered honestly in advance

**No model seat here yet.** Recall is a keyed lookup and classification is four regexes. The
place Jev could earn a seat is *"is this warning relevant to what the agent is currently
doing?"* — a judgment a regex cannot make. **Do not build that until the deterministic loop is
live and we have measured how often an irrelevant-but-correct warning fires.** That number is
the falsifier for the seat.

Carry the pipe-exit ruling first — do not wire a class that may be dropped.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

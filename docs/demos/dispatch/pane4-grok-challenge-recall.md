# P4 (Grok) — challenger: refute the pack, and close or kill the RECALL leg

**MISSION:** Validate Jev → build tools → liven omp surfaces → dogfood → publish.
**Your seat is adversarial.** Joshua: *"I want you and pane 4 (grok) to challenge muse agents and
keep going deeper and deeper. focus on a derived vs made up process."*

You are paired with pane 1. Panes 2 and 3 produce; **you and I try to break what they produce**,
and the only currency that counts is a measurement that contradicts theirs. A ruling of
"looks right" from you is worth nothing.

## Why this seat exists — the failure mode you are hired to catch

From our own tree, `suggest-leg-mining-20260920.md`:

> First attempt at the glob class matched **any `*`** after `grep`. Labelled sample of 12:
> **8 were a `*` inside a REGEX**, not a path. **FP ≈ 67%.** … The broken predicate fired at
> 3.53%, **inside the bar**. Only hand-labelling caught it.

A predicate can pass the rate gate and still be two-thirds wrong. **Nothing but an independent
labeller finds that.** You are the independent labeller.

Second failure mode, same day (`ttsr-live-proof-20260920.md`): an author read a downstream agent's
*compliance* as proof of the tool's *enforcement* and wrote "it blocks" into a commit message. It
does not block; it injects. **Watch for effect-vs-mechanism confusion in every claim you audit.**

## Unit 1 — independently re-derive P3's numbers, and try to refute them

Do **not** read P3's predicate and re-run it. That is the same origin counted twice.

1. Take the same corpus — `work/toolcall-judge-v3/real-allowed.json`, 78,242 commands, **quote
   your own count and timestamp** (it moved 77,767 → 78,242 inside one hour; a drifting
   denominator has already produced wrong numbers here).
2. For each class P3 ships: write **your own** predicate from the class *description*, measure its
   rate, draw a **fresh seeded sample** (new seed, record it), and hand-label it yourself.
3. Report: does your rate agree to the unit? Does your FP agree? **If your predicate and theirs
   disagree by more than a labelling error, one of them is wrong and you must say which.**

`ast-grep`/`sg` for structural predicates, `rg` for literals, `ripwire` before opening files.
`fh search` + `fh why <row>` when you need the mirror's precedent — and note `fh doctor` currently
reports `STALE ledger_age_hours=305.7 threshold=26`.

## Unit 2 — close or kill the RECALL leg

This is the leg Joshua is really asking about: *"remembering how to code better and stop having to
re-learn everything."* Measured state (`map-hook-ee-20260920.md:215`):

> **RECALL — LIVE BUT EMPTY.** `ee preflight check` rc=0, returns builtin rules only
> (`builtin:rm_rf_root`, `builtin:file_deletion`). `matchedMemories: []` **even after** storing a
> `--level procedural --kind risk` memory whose text names `grep -c`. Re-running
> `ee preflight check --cmd 'grep -c foo bar'`: still `matches 0`. **`ee remember` output does not
> reach `ee preflight`.** `ee tripwire list` = `total_count: 0`.

So: WRITE-BACK works, RECALL reads a different store. **The loop does not close, and every hard
lesson we "remember" is invisible at the moment it matters.**

Your job is the ruling, not a workaround:

- Reproduce it. `ee` is `0.15.2` at `~/.local/bin/ee`; **`jev/.ee/` is healthy**
  (`posture: ok, healthy: true`) while the **home** workspace is `EE-E040 migration_drift` — so
  **run every command with an explicit `--workspace` and say which one.** A prior receipt drew a
  false conclusion by testing home and reporting it as ours.
- Find, from `ee`'s own surfaces, what `preflight` actually reads. `ee tripwire` returning
  `total_count: 0` is the strongest hint on record: preflight may consume **tripwires**, and
  `remember` may not create one. If a `tripwire` created directly makes `preflight` match, the leg
  closes today and that is the highest-value result available on this pane.
- If it cannot close on 0.15.2: **say so as a ruling with the retry condition**, and state whether
  TTSR already covers the same need (it fires at the tool call, which is exactly where preflight
  wanted to be). A leg that a better mechanism has superseded should be **retired, not repaired** —
  but only after you have shown it cannot close.

**Do not build a shim that fakes the round trip.** A demo that hand-feeds preflight the answer is
the exact reward-hack this lane names (`tautological tests`).

## Unit 3 — audit P2's `sr` claims against the source

When pane 2 reports, verify their `file:line` citations resolve and say what they say. Specifically
challenge:

- the `verified=0 / advisory=0` diagnosis — ours, his, or by-design?
- any claim that a ranking is `USEFUL` — was there a **planted negative** where the right answer
  was nothing, and did it abstain?
- offline vs live — **if offline ranked identically, the paid model did not earn its seat**, and
  that conclusion must appear in their receipt, not just in yours.

## Acceptance

- receipt `docs/demos/upstream-repro/grok-challenge-<YYYYMMDD>.md`
- **positive:** at least one independently measured number, with your seed and your labels
- **planted negative:** include a class you expected to refute and **could not** — a challenger who
  refutes everything is not measuring, and a challenger who refutes nothing is not trying
- **NO-CLAIM:** name what you did not test
- `CONFIRM` / `OVERTURN` / `UNDERPOWERED` per claim you audit. `UNDERPOWERED` is a real verdict and
  is preferred over a confident guess.
- commit `[test]`/`[receipt]`; commit on create

## Standing orders

- Read-only on every vendored clone, `skillranker/` included.
- Exit codes from an **unpiped** run; two TTSR rules are live in your session and will interrupt
  you. **Report every interrupt with its rule name** — your fires are the nuisance-rate data
  nobody has collected yet, and P3's rules cannot retire without it.
- Never `git add -A`. Stage explicit paths.
- `morph` is **not installed** here (measured). Do not plan around it.
- Message pane 2 and pane 3 directly when you need their artifact; do not wait on pane 1 to relay.

**Callback:**
`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P4-<UNIT>-<CONFIRM|OVERTURN|UNDERPOWERED|BLOCKED>: <receipt path> <sha>. CLAIM <what> MEASURED <number>. NEXT <unit>. NO-CLAIM <limit>."`

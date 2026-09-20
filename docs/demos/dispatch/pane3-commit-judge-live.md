# P3 — Make the one judge that earned its seat actually run

Joshua, ~20 minutes ago, redirected this lane: he cares less about filing upstream issues and
more about **Jev capability we can use in our own ecosystem**. This queue is that.

Context you need, with its basis:

- The commit-message judge is the ONE question set where a judge beat every rule we could write:
  on a diff a linter passes, `describes 0.11` / `omits 0.92`. A regex cannot read a diff and
  decide whether the message describes it. That is the definition of earning a seat.
- The tool-call judge, by contrast, was just measured and is a **regex simulator** —
  `work/toolcall-judge-v3/score.mjs` never calls Jev. See commit `1d4e0c8`.
- `work/omp-jev-commit/` already exists with `src`, `test`, `live-probe.mjs`, `package.json`.
- JevCacheReports owns `work/toolcall-judge-v3/jev-vs-regex.{mjs,json}`. **Do not touch those two
  files.** They have a stratified run in flight.

## Unit 1 — Is omp-jev-commit actually wired, or is it another simulator?

Read `work/omp-jev-commit/src` and `live-probe.mjs`. Answer, from the code, not from the README:

1. Does it call real Jev via `work/jev-client`, or does it contain a hand-written stand-in the way
   `score.mjs` does?
2. Is it installed anywhere — is there an `omp.extensions` entry, a git hook, anything that runs
   it on a real commit? `ls` the hook path and say what is there.
3. If it is observe-only, say so plainly. Observe-only is fine; an undisclosed simulator is not.

Acceptance: a written answer with file:line for each of the three, committed as a receipt under
`docs/demos/upstream-repro/`. Verification level `test` if you only read code, `live` if you ran it.

NO-CLAIM required: state explicitly whether you executed a real Jev call or not.

## Unit 2 — Run it against real commits and report where it is WRONG

`git log` this repo. Take at least 30 real commits with their diffs. Score each with the
commit-message questions through real Jev (`infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types <script>`;
node 22 strips TS natively, there is no `tsx` in this repo and `require('tsx/esm')` fails).

Report the **disagreement set**, not an accuracy number:

- commits where the judge says the message omits something, and a human reading the diff agrees;
- commits where it says that and the human disagrees;
- and the constant baseline — what score do you get by always answering the majority label? A
  question that does not beat its own constant is DEAD, and `review.behaviour` already died that
  way this session.

Acceptance: receipt with the per-commit table, the constant baseline computed and stated, and a
verdict word chosen by the rule in `work/jev-client/measure-kit.mjs` — `DISCRIMINATES` requires
`correct > best_constant + near_threshold_count`. Do not write `DISCRIMINATES` because the numbers
look good; run the rule.

NO-CLAIM: the corpus is our own commits, written by us, so it is not independent of the judge's
authors. Say that.

## Unit 3 — If and only if unit 2 shows the judge holds: wire it to fire

Make it run on a real commit in this repo as a `commit-msg` hook that WARNS and never blocks.
Blocking on a model call is not something this lane ships. There is precedent at
`.git/hooks/commit-msg-verification-level.sh`.

Acceptance: a real commit in this repo that produced a real warning, with the warning text in the
receipt. If unit 2 says the judge does not hold, **do not build this** — write the refusal with
its trigger instead, per the creation gate. A refusal with a trigger outranks a gate that fires on
everything.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them.

When your queue drains, run `br ready`, claim the highest-priority bead you did not author, and
work it. `jev-cz0` (P1, label real traffic for omp-jev-commit/review/rerank) is directly adjacent
to this queue and is unclaimed.

Callback format:
`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

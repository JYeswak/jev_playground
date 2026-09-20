# skillranker-eval — reusable EVAL CONTRACT process

Mirrors `Dicklesworthstone/skillranker` `tests/eval/` @ `bb52b8f25` into a
runnable offline+live harness on this tree.

**Pattern:** skill / tool selection (advisory Choice with an explicit abstain
option). Prior art: skillranker itself; TypeSafe `cookbooks/skill_suggestion.md`
is not in the local docs-mirror, so the contract files under `contract/` are
the citation. Oracle: their `expected_values.v1.json` + frozen loss table
(external contract). A prior live Jev-on-corpus receipt exists at
`docs/demos/upstream-repro/skillranker-corpus-measured-20260919.md` — that is
**not** this run.

## One command

```bash
node work/skillranker-eval/run.mjs                 # offline: controls + planted RED
node --test work/skillranker-eval/test/contract.test.mjs
node work/skillranker-eval/run.mjs --selftest
node work/skillranker-eval/run.mjs --control always-abstain --export /tmp/aa.jsonl
node work/skillranker-eval/run.mjs --control coin-flip --trials 5000 --seed 1
node work/skillranker-eval/run.mjs --live           # NOT_RUN without TYPESAFE_API_KEY
node work/skillranker-eval/oracle.mjs               # same as --live
node work/skillranker-eval/run.mjs --score picks.jsonl --export /tmp/scores.jsonl
```

Offline lane needs no key. Live lane prints `LIVE: NOT_RUN` when the key is
absent — that is not a pass.

## What is first-class

| runner | what it does | expected on their 12 cases |
|---|---|---|
| always-abstain | pick `__none__` every time | mean loss `10/12 = 0.833`, top-1 `0` |
| coin-flip | uniform over roster ∪ `{__none__}` | exact E[loss] computed; sampled mean worse than abstain |
| planted-negative | fixture `wrong-skill` on a positive | **loss 2, must RED** |
| `--score` / `--live` | candidate judge | **≥0.90 top-1 is an explicit FAIL (exit 2)** |

`diagnostic_synthetic` cannot promote even at precision 1.0 — their
`forbidden_use`. The 0.90 gate is still applied as a rate FAIL so a miss
cannot hide behind a printed note (the old `oracle.mjs` exited 0 on 0.800).

## Export (installable ≠ exportable)

`--export FILE` writes one JSONL row per scored case:

```
schema, case_id, pick, y, loss, why, class, roster_ids, y_in_roster,
installableNotOffered, judge, lane, measured_product, binary_path, model
```

A later measurement can recompute loss from these rows without re-calling Jev.
`measured_product` is always `false` unless an `sr` binary is actually invoked;
this harness never invokes one.

The overflow case (`synthetic-overflow-retrieval-paraphrase`) is the named
hole: Y is `testing-fuzzing`, the exported roster is empty, so a judge that
only sees installable/exported skills cannot pick the skill the contract
wants. `installableNotOffered=true` on that row.

Live Jev noul/choice scores still belong in `work/jev-score-register/` when a
hook is wired; this file is the **eval** row (pick + loss + Y), which the
register's numeric `score` field cannot carry.

## How an omp skill-router hook calls the same judge

The hook and this harness must share `judgeSkillPick` in `score.mjs`. Do not
invent a second question or a `helpful` noul gate.

```js
import { judgeSkillPick, NONE, scoreDecision } from '../work/skillranker-eval/score.mjs';
import { askJevChoice } from '../work/jev-client/src/index.ts';
import { recordScore } from '../work/jev-score-register/register.mjs';

// observe-only. never {block:true}. never throw into the host.
const judged = await judgeSkillPick({
  roster: visibleRoster,          // exported / loaded skills only
  task: latestUserText,
  constraints: sessionConstraints,
  already_loaded: alreadyLoaded,
  ask: askJevChoice,
});
if (judged.unavailable) {
  // fail-safe: treat as operational unavailable (loss 2 at eval time), do not invent a pick
}
// persist the eval-shaped decision so a later --score can read it
// recordScore() stores a hash of state + a numeric score, not the pick/Y pair —
// write the eval JSONL too, or the export hole returns.
```

Wire shape, pinned by `test/contract.test.mjs`:

- `state = { task, constraints, already_loaded }`
- `classes` = roster id → `"<usage_kind> — <invocation_name>"` plus `__none__`
- `instructions` = `PICK_INSTRUCTIONS` (one Choice, no second question)
- roster with `< 2` labels (empty export) → do **not** call Jev; abstain
- ask failure → `unavailable`, not a fabricated skill id

## NO-CLAIM

- n=12, `split: diagnostic_synthetic`. Their README: these files "are not
  benchmark results." Their policy: no promotion / calibration / statistical
  quality claim on this split.
- This measures a **judge** (always-abstain, coin-flip, injected, or Jev
  Choice) on their corpus. It does **not** measure SkillRanker unless
  `sr` is invoked. No binary path is used here.
- A prior live receipt (mean loss 0.167, top-1 0.800, both misses = false
  abstentions) is cited, not re-run. This PR does not spend a live call.
- Unpromoted. Ledger stays 0 promoted.

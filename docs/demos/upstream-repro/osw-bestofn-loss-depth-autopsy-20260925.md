# OSWorld Best-of-N loss-depth autopsy (keyless)

Bead `jev-9gtw.2`, R104. This is the required keyless autopsy before any new live call. It
examines the committed Best-of-N loss from `work/osw-bestofn/live_receipt.json` and the official
floor rows in `work/osw-bestofn/floor_receipt.json`. No Jev call, comparator call, or Laya call was
made for this autopsy.

## Rebuilt states and denominator

The state builder was run against the already frozen eight-archive pool:

```bash
python3 work/osw-bestofn/build_states.py \
  --out var/agent-tmp/osw-bestofn-autopsy-43091/states.jsonl
```

It rebuilt **361/361** task states using only each candidate's `traj.jsonl` compacted action
records and the fixed 1,200-character tail of `runtime.log`; `result.txt` is not in the state.
The raw state file remains in ignored `var/agent-tmp/` and is not committed. The state schema is
observable in `build_states.py`: top-level fields are only `task` and `candidates`; candidate
fields are only `id`, `archive`, `actions`, and `runtime_tail`.

The live receipt contains **74 `none` picks**. A `wrong` pick here means the selected candidate's
official reward is `0` while at least one selected candidate has reward `>0`; there are **42**.
The union is therefore 116 rows. Of the 74 `none` rows, **47 are correct abstentions** because no
selected candidate succeeded; **27** are false abstentions. The 42 wrong candidate picks are all
actual losses. The actual-loss denominator for cause analysis is **69 = 27 + 42**.

## Classification rules and counts

These are multi-label evidence flags, not a claim that one cause explains every row.

| Flag | Count | Evidence and limit |
|---|---:|---|
| Question unanswerable from the supplied text | **69/69 actual losses** | The state has no task instruction, goal, or expected end-state field; `task` is only an opaque `app/category/UUID` key. TypeSafe's state guidance says the state must contain the material needed for the judgment (`docs-mirror/typesafe/concepts/state.md:9-29`). This is a harness/state defect, not a Jev-model finding. |
| Success evidence cut from the bounded state | **30/69 actual losses** | In 14 false-`none` rows and 16 wrong-pick rows, every official-success candidate (`result.txt` reward `>=1.0`) lacks the preregistered `(?:task\s+)?(?:completed|succeeded|success(?:ful|fully)?)` marker in the supplied 1,200-character runtime tail. The ground truth is in the excluded `result.txt`; the model never sees it. This is a bounded-state evidence flag, not proof that the full runtime lacked a claim. |
| Runs indistinguishable in status text | **3/69 actual losses** | `chrome/ae78f875-5b98-4907-bbb5-9c737fc68c03`, `gimp/8ea73f6f-9689-42ad-8c60-195bbf06a7ba`, and `libreoffice_impress/7ae48c60-f143-4119-b659-15b8f485eb9a` have no success or failure marker in any candidate's supplied actions/tail. This is a deliberately narrow text-status test, not a semantic-equivalence claim. |
| Brand label steered the pick | **0 proven; 69/69 exposed** | `live_select.mjs:11-14` sends criteria labels of the form `Candidate N; public archive <model/archive name>`. Every actual loss therefore has a brand-label confound, but this receipt has no neutral-label counterfactual and cannot call steering causal. |

The non-loss rows are not silently assigned a failure cause: 47/74 `none` picks were correct
abstentions under the official floor. Among the 69 actual losses, the bounded success-marker split
is 30 absent versus 39 visible (13 false-`none` + 26 wrong-pick rows with a visible success
marker). A visible marker does not prove the task was answerable because the task goal is still
absent from state.

## Diagnosis

The first load-bearing defect is **missing task semantics**. The Choice question asks which
trajectory completed “the OSWorld task,” but the state provides no task instruction or target
condition. The model can only compare traces without knowing what success means. This subsumes
any claim that the model chose a particular trajectory for the right task-level reason.

The second defect is **ground-truth/evidence mismatch**: the only official success signal is
`result.txt`, while the live state excludes it by preregistration. A bounded runtime tail can also
cut the completion claim. The third is an **unresolved brand-label confound**: public archive names
are explicitly sent as criteria despite the question instruction not to use them. Keyless evidence
cannot separate it from the missing-goal defect.

This autopsy does not move the original bar, score a new design, or claim a model limitation. It
freezes the failure modes before the dev loop. The next step must use a fixed development slice and
change one variable at a time; a held-out retest remains separate.

## Non-claims and boundary

No live call was made. No neutral-label replay, per-candidate Noul, longer runtime tail, task-goal
injection, or held-out retest was run. No causal count for brand steering is available. The raw
trajectory/runtime text and screenshots remain uncommitted by design. TypeSafe's Choice contract
supports defined options with probabilities/confidence (`docs-mirror/typesafe/primitives/choice.md:238-284`),
but typed Choice output cannot repair missing task semantics. This receipt is `keyless
offline-verified` for the row reconstruction and counts only.

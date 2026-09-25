# MiniWoB Jev v3 — option-construction loss-depth experiment

Bead: `jev-9gtw.4`
Status: preregistered design; no v3 live call made.
Model: `jev-1.13.0`, official SDK; no comparator and no Laya.

## Fixed design

The v1 default remains byte-compatible: every v3 change is behind `MINIWOB_V3=1`; v1 uses the
existing `jev_arm.py` and floor action space with the flag unset. The v3 arm changes only option
construction and code execution:

1. quoted values preserve matching outer quotes' contents and punctuation;
2. `INPUT_DATE` and `INPUT_TIME` become typable under `MINIWOB_V3`;
3. visible page text/value strings are added to type options;
4. element color is serialized into the v3 state;
5. code enumerates source/target drag pairs for drag/draw/resize/slider utterances and executes a
   deterministic mouse-down/move/up sequence;
6. the v2 `after-page-change` none guard remains, with an explicit nonempty-action guard required
   before any held-out call.

## Dev arms before held-out calls

Each arm uses only its autopsy slice from `work/miniwob-jev-v1-autopsy-20260925.md` and has its
own keyless replay/RED check before any live call. The arm names and slices are fixed:

| Arm | Autopsy slice | Single changed variable |
|---|---|---|
| quoted spans | 16 `value-mangled-by-span-strip` episodes | preserve quoted terminal punctuation |
| date/time | 10 `op-not-offered` date/time episodes | typable tag set |
| page text | 35 page-value episodes | page text/value type options |
| color | 12 evidence-absent color/shape episodes | serialized color field |
| drag pairs | 87 drag/draw/resize/slider episodes | code-enumerated drag source/target options and execution |
| none guard | 11 `none-while-action-needed` episodes | v2 after-page-change none rule plus nonempty-action guard |

No arm may use the combined held-out seeds. A dev arm is not a held-out claim.

## Held-out corpus and bar

Fresh seeds are fixed to `400,401,402,403,404`, all 125 MiniWoB tasks, with the same 10-step,
0.5-second wait, fresh-page action space for random, scripted and v3. These seeds are disjoint from
v1 `0..33`, v2 `100..104`, and previous dev seeds `200` and `300`.

Before the first v3 held-out call:

```text
MINIWOB_V3=1 floor --policy random,scripted --tasks all --seeds 400,401,402,403,404
MINIWOB_V3=1 jev_arm.py live --seeds 400,401,402,403,404 --none-policy after-page-change
```

**PASS:** v3 beats v1 on the same fresh held-out episode keys with exact paired McNemar p < 0.05
and v3-only successes > v1-only successes. Report Wilson intervals, each arm's success and raw
reward, floors rerun under `MINIWOB_V3=1`, v1/v3 calls, per-call resolved model, input/output
tokens and spend. Report each published LLM row as BEAT/TIE/LOSE with protocol notes; no protocol
match is assumed.

**KILL/BLOCK:** any dev arm that does not clear its slice bar, an empty action set, missing v3
rows, or an incomplete held-out set. Never impute missing rows and never score a partial set.

No threshold, state field, option construction rule, seed, retry policy or bar changes after the
first live v3 call. A failure is recorded as a harness/design result, not a ruling about Jev.

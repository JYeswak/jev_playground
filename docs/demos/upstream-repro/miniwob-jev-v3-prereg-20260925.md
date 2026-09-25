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

## Amendment: exact autopsy slices and numeric dev bars
The smoke rows previously run on seeds 9000/9001 are not these slices and are excluded. Each dev arm below uses the exact committed autopsy episode IDs; only the changed variable is enabled with `MINIWOB_V3=1`. Intermediate counts are dev-only and are excluded from the combined held-out design.
### quoted — N=16

- Change: preserve quoted terminal punctuation.
- Bar: PASS >=14/16; FAIL <=8/16; 9-13 is dev-only and excluded from combined v3.
- Exact keys:

```text
email-inbox-nl-turk/s4/r0
email-inbox-nl-turk/s28/r0
email-inbox-noscroll/s11/r0
email-inbox-noscroll/s15/r0
email-inbox/s21/r0
email-inbox/s21/r1
email-inbox-reply/s13/r0
email-inbox-reply/s27/r0
email-inbox-reply/s4/r0
email-inbox-reply/s29/r0
email-inbox-reply/s4/r1
email-inbox-star-reply/s11/r0
email-inbox-star-reply/s15/r0
email-inbox-star-reply/s25/r0
email-inbox-star-reply/s25/r1
email-inbox-star-reply/s20/r0
```
### date time — N=10

- Change: make INPUT_DATE/INPUT_TIME typable.
- Bar: PASS >=8/10; FAIL <=2/10; 3-7 is dev-only and excluded from combined v3.
- Exact keys:

```text
enter-date/s32/r0
enter-date/s29/r0
enter-date/s22/r0
enter-date/s9/r0
enter-date/s4/r0
enter-time/s11/r0
enter-time/s2/r0
enter-time/s0/r0
enter-time/s32/r0
enter-time/s9/r0
```
### page text — N=35

- Change: add visible page text/value options.
- Bar: PASS >=20/35, find-word <=2/5, and no regression on already-successful type controls; FAIL <=12/35; otherwise dev-only.
- Exact keys:

```text
find-word/s25/r0
find-word/s9/r0
find-word/s25/r1
find-word/s33/r0
find-word/s6/r0
copy-paste/s17/r0
copy-paste/s17/r1
copy-paste/s1/r0
copy-paste/s15/r0
copy-paste/s32/r0
read-table/s15/r0
read-table/s7/r0
read-table/s11/r0
read-table/s23/r0
read-table/s27/r0
scroll-text/s5/r0
scroll-text/s17/r0
scroll-text/s4/r0
scroll-text/s24/r0
scroll-text/s1/r0
text-transform/s1/r0
text-transform/s10/r0
text-transform/s33/r0
text-transform/s33/r1
text-transform/s17/r0
copy-paste-2/s3/r0
copy-paste-2/s32/r0
copy-paste-2/s13/r0
copy-paste-2/s20/r0
copy-paste-2/s19/r0
read-table-2/s7/r0
read-table-2/s27/r0
read-table-2/s25/r0
read-table-2/s7/r1
read-table-2/s27/r1
```
### color — N=12

- Change: serialize element color.
- Bar: PASS >=8/12; FAIL <=3/12; otherwise dev-only.
- Exact keys:

```text
click-shape/s21/r0
click-shape/s10/r0
count-shape/s2/r0
click-color/s22/r0
click-color/s14/r0
click-color/s28/r0
click-color/s12/r0
click-shades/s3/r0
click-shades/s10/r0
click-shades/s16/r0
click-shades/s23/r0
click-shades/s4/r0
```
### drag — N=87

- Change: code-enumerate source/target drag pairs.
- Bar: PASS >=50/87 and no empty-action rows; FAIL <=20/87; otherwise dev-only [PROPOSED because the autopsy gives no numeric drag bar].
- Exact keys:

```text
drag-circle/s3/r0
drag-circle/s16/r0
drag-circle/s27/r0
drag-circle/s29/r0
drag-circle/s28/r0
drag-shapes/s31/r0
drag-shapes/s21/r0
drag-shapes/s22/r0
drag-shapes/s1/r0
drag-shapes/s26/r0
draw-circle/s13/r0
draw-circle/s11/r0
draw-circle/s22/r0
draw-circle/s14/r0
draw-circle/s27/r0
resize-textarea/s27/r0
resize-textarea/s26/r0
resize-textarea/s16/r0
resize-textarea/s8/r0
resize-textarea/s32/r0
drag-cube/s5/r0
drag-cube/s23/r0
drag-cube/s28/r0
drag-cube/s30/r0
drag-cube/s32/r0
drag-shapes-2/s1/r0
drag-shapes-2/s25/r0
drag-shapes-2/s16/r0
drag-shapes-2/s32/r0
drag-shapes-2/s8/r0
draw-line/s33/r0
draw-line/s1/r0
draw-line/s31/r0
draw-line/s22/r0
draw-line/s21/r0
highlight-text/s13/r0
highlight-text/s30/r0
highlight-text/s4/r0
highlight-text/s22/r0
highlight-text/s28/r0
text-editor/s16/r0
text-editor/s22/r0
text-editor/s14/r0
text-editor/s20/r0
text-editor/s13/r0
use-slider/s3/r0
use-slider/s3/r1
use-slider/s24/r0
use-slider/s2/r0
use-slider/s31/r0
drag-items/s20/r0
drag-items/s31/r0
drag-items/s22/r0
drag-items/s32/r0
drag-items/s2/r0
drag-single-shape/s28/r0
drag-single-shape/s25/r0
drag-single-shape/s24/r0
drag-single-shape/s23/r0
drag-single-shape/s12/r0
highlight-text-2/s10/r0
highlight-text-2/s17/r0
highlight-text-2/s11/r0
highlight-text-2/s8/r0
highlight-text-2/s9/r0
use-slider-2/s2/r0
use-slider-2/s26/r0
use-slider-2/s28/r0
use-slider-2/s31/r0
use-slider-2/s18/r0
drag-box/s32/r0
drag-box/s27/r0
drag-box/s32/r1
drag-box/s4/r0
drag-box/s18/r0
drag-items-grid/s17/r0
drag-items-grid/s24/r0
drag-items-grid/s30/r0
drag-items-grid/s2/r0
drag-items-grid/s23/r0
drag-sort-numbers/s6/r0
drag-sort-numbers/s19/r0
drag-sort-numbers/s7/r0
drag-sort-numbers/s15/r0
scroll-text-2/s29/r0
scroll-text-2/s4/r0
scroll-text-2/s32/r0
```
### none — N=11

- Change: after-page-change none guard plus nonempty-action guard.
- Bar: PASS >=6/11 and no empty-action rows; FAIL <=2/11; otherwise dev-only.
- Exact keys:

```text
count-shape/s16/r0
form-sequence-2/s22/r0
form-sequence-2/s24/r0
form-sequence-2/s29/r0
form-sequence-2/s16/r0
form-sequence-2/s19/r0
email-inbox-forward-nl/s27/r0
use-autocomplete/s28/r0
use-autocomplete/s3/r0
click-menu-2/s26/r0
use-autocomplete-nodelay/s4/r0
```

The combined held-out run uses only fresh seeds 400-404 after every arm's dev gate is recorded; a dev arm not meeting its bar is excluded from the combined design and reported as a failed design arm.

## Dev amendment: quoted-span mechanism re-run

The first exact quoted slice (16 rows, 1/16) showed the v3 code still stripped punctuation because
the regex had already removed the outer quotes before the normalizer saw the string. The mechanism
fix is now committed in `work/miniwob-jev/jev_arm.py`: quoted regex matches call `add(..., quoted=True)`
and preserve the matched contents verbatim, while unquoted spans keep the v1 stripping path. The
slice, `>=14/16` bar, and combined-design exclusion rule are unchanged. The exact 16-row slice is
re-run; both first and re-run results are retained in the receipt, and no other arm changes.

## Dev amendment: time-input formatter re-run

The first exact date/time slice produced 5/10 (enter-date 5/5, enter-time 0/5). The enter-time
trace showed Jev selected the spoken `H:MM AM/PM` value, while MiniWoB's native time input requires
24-hour `HH:MM`. The v3 harness now adds a guarded formatter that maps the spoken value to the
native value (for example `4:03 PM` -> `16:03`) only when `MINIWOB_V3=1`. The exact ten keys and
`>=8/10` bar are unchanged; first and rerun rows are both retained.

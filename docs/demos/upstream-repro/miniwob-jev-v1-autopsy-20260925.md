# Jev on MiniWoB++ v1: loss autopsy (bead `jev-9gtw.3`)

MiniwobAutopsy (subagent; Agent Mail `QuietPrairie`), 2026-09-25. Step 1 and 2 of the LOSS DEPTH loop (`AGENTS.md`) for the v1 run in [`miniwob-jev-20260925.md`](miniwob-jev-20260925.md).

- **Keyless.** No TypeSafe call, no model call of any kind. Input: the committed v1 rows `work/miniwob-jev/rows/miniwob-jev.s{0,1,2,3}.jsonl` (625 episodes, 306 success, 319 failed). No held-out, v2 or floor-v2 rows were read.
- **Evidence level: [test].** Every count here is a scripted count over committed rows (lane: keyless re-analysis of the live v1 run; N = 625, 319 failed; model `jev-1.13.0`; run date 2026-09-25). Every hypothesis is an untested prediction.
- **Code:** `work/miniwob-jev/autopsy/v1_failures.py`, stdlib only. It reads two harness constants from the committed source with `ast` (never importing it): `SPAN_STRIP` from `jev_arm.py` and `TEXT_INPUT_TAGS` from `work/game-floors/miniwob/run.py`.
- **Re-run:**

```
python3 work/miniwob-jev/autopsy/v1_failures.py             # tables, controls, examples
python3 work/miniwob-jev/autopsy/v1_failures.py --episodes  # cause and decisive step, all 319
python3 work/miniwob-jev/autopsy/v1_failures.py --sample 12 # seeded random spot-check
python3 work/miniwob-jev/autopsy/v1_failures.py --json      # everything
```

It exits 1 if the rows are not exactly 625 or if any failure matches no rule. It exits 0 now: all 319 failures are classified.

## Verdict

- **Most of the loss is upstream of Jev's choices.** In 242 of the 319 failures (76%), no option v1 offered could have won. The task needed an operation the action space lacks, the needed element or value was never offered, or the deciding attribute was not in the state. The other 77 failures (24%) are policy errors, where a winning option was on offer.
- **A perfect chooser over v1's options tops out at 383/625 = 61.3%.** That is below GenericAgent-GPT-4o's 63.8 (it falls inside that row's 60.0–67.5 interval) and well below the other three rows Jev lost to. The v1 loss is mainly a result about the harness and question design, not about the model.
- **Two of the upstream causes are plain code bugs, 31 episodes in all.**
  - `SPAN_STRIP` removes the final "." from quoted strings, so the exact reply text was never an option. This caused 16 of 16 losses on reply episodes.
  - `TEXT_INPUT_TAGS` omits `INPUT_DATE` and `INPUT_TIME`, so date and time fields had no `type` option (10 episodes).
  - A third near-bug: on find-greatest the cards were never click candidates (5 episodes).
- **'none' matters less than it looked.** 333 of the 496 'none' steps in failed episodes sit in episodes whose task v1 cannot express. Only 11 episodes (1.8% of 625) are lost to 'none' while an offered action was still needed. That caps what v2's 'none' rule can recover directly (see below).

## Method

The `skill://error-discovery` method, run without a review UI:
- **Understand the data.** Each row logs the chosen option label, the option and text-head counts, and any typed text per step. It does not log the page. So I read all 319 failed traces in full, a census rather than a sample.
- **Cluster.** I grouped the failures on how they end (wrong answer submitted, or a timeout with a 'none' tail, a repeat tail or neither) and on option-set features (text heads offered, option counts that never change, tags clicked).
- **Name the failure modes, then count them.** Each mode became a rule in `classify()`. A seeded random sample of 12 (`--sample 12`) matched the hand reading.
- **Two kinds of rule.**
  - Task knowledge sits in `TASK_NEEDS` (what the task requires), and every entry has a per-episode guard on the row. Examples: scroll-text-2 counts only "bottom" episodes, and click-menu only multi-level (`>`) paths. daily-calendar counts only when the option count never changed across its clicks.
  - Trace rules read the row alone. Examples: typing a value that is a quoted string minus its end punctuation, clicking an `<option>` while `type` on its `<select>` was offered, and a 'none' tail of 3 or more.
- **Precedence.** Causes apply in order: first the blockers a perfect chooser could not pass (upstream), then the policy errors. Each failure gets one root cause.
- **Buckets.** Each cause maps to one of the four LOSS DEPTH buckets: missing evidence in the state, question design, harness or code bug, model limit.

## Taxonomy: cause × task family (319 failures)

Families: **click** (single or multi-target clicks, including canvas clicks), **type** (enter a text value), **widget** (menus, lists, pickers, spinner, autocomplete, pie), **drag** (drag, draw, resize, slider, text selection, scroll), **form** (multi-field or multi-page workflows).

| Cause | Bucket | click | type | widget | drag | form | **total** |
|---|---|---:|---:|---:|---:|---:|---:|
| op-inexpressible | harness (action space) | 25 | 5 | 4 | 87 | 11 | **132** |
| op-not-offered | harness or code bug | 5 | 10 | 0 | 0 | 0 | **15** |
| value-mangled-by-span-strip | harness or code bug | 0 | 0 | 0 | 0 | 16 | **16** |
| value-not-in-utterance | question design | 0 | 60 | 0 | 0 | 0 | **60** |
| evidence-absent-from-state | missing evidence in the state | 17 | 0 | 0 | 0 | 0 | **17** |
| step-cap-infeasible | harness (10-step cap) | 0 | 0 | 2 | 0 | 0 | **2** |
| *upstream subtotal* | | 47 | 75 | 6 | 87 | 27 | ***242*** |
| right-element-wrong-op | question design | 0 | 0 | 20 | 0 | 2 | **22** |
| step-cap-wasted | question design | 0 | 0 | 0 | 0 | 4 | **4** |
| wrong-span | model limit or question design | 0 | 0 | 3 | 0 | 3 | **6** |
| none-while-action-needed | question design | 1 | 0 | 4 | 0 | 6 | **11** |
| no-progress-loop | model limit or question design | 0 | 0 | 2 | 0 | 2 | **4** |
| wrong-choice | model limit | 18 | 0 | 4 | 0 | 8 | **30** |
| harness-call-error | harness or code bug | 0 | 0 | 0 | 0 | 0 | **0** |
| *policy subtotal* | | 19 | 0 | 33 | 0 | 25 | ***77*** |
| **failed** | | 66 | 75 | 39 | 87 | 52 | **319** |
| episodes | | 240 | 90 | 80 | 90 | 125 | 625 |
| failure rate | | 28% | 83% | 49% | 97% | 42% | 51% |

**Subtypes** (`--json`, `.episodes[].subtype`):
- **op-inexpressible:**
  - drag 77: drag-* 44, draw-circle 5, draw-line 5, resize-textarea 5, use-slider 5, use-slider-2 5, form-sequence 3 (slider), daily-calendar 5
  - coordinate click 25: bisect-angle, circle-center, find-midpoint, right-angle, hot-cold
  - text selection 15: highlight-text, highlight-text-2, text-editor
  - scroll 6: scroll-text-2 "bottom", sign-agreement "Scroll…"
  - hover 4: click-menu multi-level
  - Enter key 5: terminal. Its command (`rm <file>`) is not in the utterance either.
- **op-not-offered:** `type` on INPUT_DATE 5, on INPUT_TIME 5; find-greatest cards not clickable 5.
- **value-not-in-utterance:**
  - page value 35: copy-paste, copy-paste-2, find-word, read-table, read-table-2, scroll-text, text-transform
  - computed value 20: visual-addition, simple-arithmetic, simple-algebra, guess-number
  - case change 5: enter-text-2
- **evidence-absent-from-state:** color 12 (click-color 4, click-shades 5, click-shape 2, count-shape 1); SVG geometry 5 (count-sides).
- **right-element-wrong-op:**
  - pie `<tspan>` label instead of the slice `<path>`: 9
  - `<option>` clicked instead of `type` on its `<select>`: 5
  - typing into the prefilled spinner (type appends and does not clear): 5
  - date typed into the jQuery datepicker: 3
- **wrong-choice:** 22 wrong answers submitted, 8 timeouts spent on wrong elements. By task: tic-tac-toe 4, number-checkboxes 5, click-menu-2 4, search-engine 5, stock-market 3, login-user-popup 3, click-dialog-2 2, and one each of click-checkboxes-large, click-checkboxes-soft, generate-number and social-media-all.

**The bead's six required classes:**

| Required class | Taxonomy class | Episodes |
|---|---|---:|
| wrong element chosen | wrong-choice | 30 |
| right element, wrong operation | right-element-wrong-op | 22 |
| typed value not among the spans offered | value-mangled-by-span-strip, value-not-in-utterance | 16 + 60 |
| 'none' while the page still needed an action | none-while-action-needed | 11 |
| action the space cannot express | op-inexpressible | 132 |
| harness error | harness-call-error | 0 |

- **Harness error or timeout:** 3 failed episodes had a failed Jev call (bisect-angle s10 r1, bisect-angle s23, enter-text-2 s31). Each already had an upstream cause, so none was decisive. Timeouts are how 142 episodes end, not a cause; the next table shows them.
- **Classes the data added:** op-not-offered, evidence-absent-from-state, step-cap-infeasible, step-cap-wasted, wrong-span and no-progress-loop.

## How each cause ends

| Cause | wrong answer submitted | timeout, 'none' tail | timeout, repeat tail | timeout, other |
|---|---:|---:|---:|---:|
| op-inexpressible | 59 | 26 | 36 | 11 |
| op-not-offered | 1 | 5 | 9 | 0 |
| value-mangled-by-span-strip | 16 | 0 | 0 | 0 |
| value-not-in-utterance | 46 | 0 | 9 | 5 |
| evidence-absent-from-state | 16 | 1 | 0 | 0 |
| step-cap-infeasible | 0 | 0 | 0 | 2 |
| right-element-wrong-op | 11 | 0 | 10 | 1 |
| step-cap-wasted | 0 | 0 | 0 | 4 |
| wrong-span | 6 | 0 | 0 | 0 |
| none-while-action-needed | 0 | 11 | 0 | 0 |
| no-progress-loop | 0 | 0 | 4 | 0 |
| wrong-choice | 22 | 0 | 0 | 8 |
| **total** | **177** | **43** | **68** | **31** |

The totals match the receipt: 177 failed episodes ended on the task's own terminal action, and 142 ran all 10 steps.

**'none' accounting.** 509 of the 2,808 steps were 'none'; 496 of them fall in failed episodes. By cause:

| Cause | 'none' steps |
|---|---:|
| op-inexpressible | 333 |
| none-while-action-needed | 87 |
| op-not-offered | 50 |
| evidence-absent-from-state | 11 |
| wrong-choice | 9 |
| value-not-in-utterance | 6 |

**Wasted steps.** 167 steps across the run clicked a text field that the next step typed into; `type` already focuses the field. 103 of those steps are in failed episodes. They decided 4 book-flight losses (step-cap-wasted).

## Controls: the same tasks, split by the suspected cause

The script prints these from all 625 rows. Each split holds the task fixed and varies only the suspected cause.

| Split | Success | Fail |
|---|---:|---:|
| color tasks, utterance names a color | 1 | 12 |
| same tasks, no color word | 6 | 1 |
| date widget, 0–1 months back from December | 16 | 0 |
| date widget, 2 months back (the book-flight path needs exactly the 10-step cap) | 2 | 6 |
| date widget, 3 months back | 1 | 0 |
| date widget, 4 or more months back (choose-date's calendar path exceeds 10 steps beyond 7 months back) | 0 | 5 |
| email task with a quoted reply ending in "." | 0 | 16 |

- The calendar opens on December 2016. The rows show a `span "December"`, and two Prev clicks show `"October"` (choose-date-nodelay s16).
- There is no positive control for the reply split: no reply quote in the 625 episodes lacks end punctuation.

## Causes, with example episodes and the decisive step

Episode ids are `task/s<seed>/r<rep>`, and steps are 0-based. `--episodes` lists every failure with its decisive step.

**op-inexpressible (132).** v1 acts with `click(ref)`, `type(ref, span)` and `none`. Farama `CLICK_ELEMENT` targets an element, not a point.
- `drag-single-shape/s12/r0` step 0 `click [5] circle`, then Submit. It "clicked" the shape it had to drag left.
- `circle-center/s13/r0` step 0 `click [5] circle`. The task scores the click's coordinates.
- `click-menu/s12/r0` step 0 `click [9] div "Elita"` for "Select Elita>Cherilynn". The submenu opens on hover. The one click-menu success was a single-level path.

**op-not-offered (15).**
- `enter-date/s22/r0` step 0 `click [5] input_date #tt`, repeated to the cap. No text head was offered on any step because `INPUT_DATE ∉ TEXT_INPUT_TAGS`.
- `enter-time/s0/r0` step 0: the same, on `input_time`.
- `find-greatest/s1/r0` step 0 'none'. Two options on every step (one click plus 'none'); no card was a candidate.

**value-mangled-by-span-strip (16).** Every one of these episodes clicked the sender, clicked Reply, typed into `#reply-text` and clicked send. Only the text is wrong.
- `email-inbox-reply/s13/r0` step 2 typed `'Ultrices. Integer'`; it needed `"Ultrices. Integer."`.
- `email-inbox-nl-turk/s28/r0` step 2 typed `'Sed'`; it needed `"Sed."`.

**value-not-in-utterance (60).**
- `copy-paste/s1/r0` step 2 typed the whole instruction sentence. The text to copy is the textarea's value, on the page.
- `read-table/s11/r0` step 1 typed `'the value of Color'`.
- `enter-text-2/s1/r0` step 1 typed `'KANESHA'` where the task asked for lower case.

**evidence-absent-from-state (17).** `elements_from_obs` (`run.py:132-154`) keeps no color field, and `serialize_state` sends tag, text, value, id, classes and bbox only.
- `click-color/s12/r0` step 0 `click [5] div` for "magenta". Every box is a bare `div`.
- `click-shades/s10/r0`: two spans, then Submit.
- `count-sides/s7/r0` step 0 `click [7] button "4"`. All five count-sides failures answered "4".

**step-cap-infeasible (2).**
- `choose-date/s2/r0`: March needs 12 clicks from December (open, 9 Prev, day, submit).
- `choose-date-nodelay/s3/r0`: January needs 14.

**right-element-wrong-op (22).**
- `click-pie/s1/r0` from step 1: `click [34] tspan "w"` nine times. The click-pie success clicked `path #wheelnav-divWheel-slice`.
- `click-scroll-list/s1/r0` step 0 `click [14] option "Antigua and Barbuda"` while a `type` head on the list was offered.
- `use-spinner/s4/r0` step 0 typed `'-5'` into `#spinner value="0"`. enter-text-2 shows type appends ("KANESHA" became "KANESHAKANESHA").

**step-cap-wasted (4).** `book-flight/s23/r0` step 2 `click [9] input_text #flight-to`, then typed into it at step 3. The October path needs exactly 10 steps, and Search came at step 9.

**wrong-span (6).**
- `use-autocomplete-nodelay/s16/r0` step 1 typed `'item that starts with Gua and ends with uam'`. The success on that task typed `'Pola and'`.
- `multi-orderings/s27/r0` step 4 typed `'action movies'` into the genre field.

**none-while-action-needed (11).**
- `form-sequence-2/s19/r0` from step 2: the radio and the number are done, then 8 'none' at confidence 0.85–0.91 while Submit was offered (5 of 5 form-sequence-2 losses).
- `use-autocomplete/s3/r0` from step 3: it picked the suggestion, then 'none' instead of Submit.

**no-progress-loop (4).**
- `multi-layouts/s18/r0` from step 2: `click [13] div "Year"`, the field's label and not its input, eight times.
- `choose-date/s17/r0` from step 1: `click [14] span "December"` nine times.

**wrong-choice (30).**
- `click-dialog-2/s29/r0` step 0 `click [14] button "OK"` for the button labeled "x".
- `tic-tac-toe/s26/r0` steps 0–1: a losing move.
- `search-engine/s10/r0`: it paged back and forth between `>` and `Search` and never clicked the 5th result.

That the deciding evidence was in the state is **[INFERENCE]** for stock-market (the price), click-menu-2 (the icon class) and number-checkboxes (the example grid). The rows do not log the page.

## What this predicts for v2 (pane 5, the 'none' rule only)

- **Direct target.** v2's `after-page-change` rule forbids 'none' on an unchanged page. The episodes it targets directly are the 11 none-while-action-needed ones: 1.8 points of the 625 v1 episodes.
- **Where most 'none' steps are.** Most 'none' steps (333 of 496) are in op-inexpressible episodes, where acting in place of 'none' reaches no winning option.
- **Prediction.** If v2 beats v1 by more than about 3 points on comparable seeds, the extra gain comes from something other than recovering these 11, such as a forced action on a page whose default state already scores. This autopsy would then be missing a mode.
- **Scope.** If v2 runs on other seeds than v1, this is a prediction about proportions, not about the same episodes.

## Ranked hypotheses for a v3 design

Each hypothesis changes one variable. The dev slice is the class's failing v1 episodes (`--episodes`), replayed on the same seeds, and it is never the held-out set. Each also needs a regression check on successful v1 episodes that use the same machinery. Order: expected recovered episodes, then confidence, then cost.

| # | One variable changed | Dev slice | Prediction | Falsified if |
|---|---|---|---|---|
| 1 | **Quoted-string text options kept verbatim.** `SPAN_STRIP` is not applied to spans from `"…"`, or the verbatim quote is added beside the stripped one. | 16 value-mangled-by-span-strip | ≥ 14 of 16 succeed. The other three steps were already right in all 16. | ≤ 8 of 16 succeed. Then MiniWoB's reply check is not an exact match, or another step is wrong. |
| 2 | **Page text in the text-option pool.** Candidates are utterance spans plus page spans: whole `value`/`text` of elements, their lines and words, and table cells, all within the 255-option cap. | 35 page-value (copy-paste ×2, find-word, read-table ×2, scroll-text, text-transform) | ≥ 20 of 35 succeed. find-word (an ordinal count) is the hardest: ≤ 2 of 5. No loss among the successful type-task episodes. | ≤ 12 of 35 succeed. Then Jev cannot pick page values from a mixed pool even when they are present: a model limit for this selection or a question-design issue, not coverage. |
| 3 | **Element color in the state.** Carry Farama's per-element background and foreground color into `serialize_state`. | 12 color (click-color 4, click-shades 5, click-shape 2, count-shape 1) | ≥ 8 of 12 succeed. In the controls, the same tasks without a color word are 6 of 7. | ≤ 3 of 12 succeed. Then raw RGB is not usable to Jev, and the next variable is a code-side RGB→color-name mapping. |
| 4 | **Date and time inputs typable.** Add `INPUT_DATE` and `INPUT_TIME` to the typable tags, with utterance spans as the text options. | 10 enter-date/enter-time | ≥ 8 of 10 succeed. | ≤ 2 of 10 succeed. Then the blocker is the keystroke format Chrome's date/time inputs accept, which needs a harness formatter, not a Jev question. |
| 5 | **Inert nodes dropped from click options.** Offer no click on a node known not to act: an SVG `<tspan>` label whose slice `<path>` is offered, or an `<option>` whose `<select>` has a `type` head. | 14 right-element-wrong-op (click-pie ×9, click-scroll-list ×5) | ≥ 10 of 14 succeed. | ≤ 4 of 14 succeed. Then the label was not what drew the choice, and the pie and list failures have another cause. |

**Before any call, check these against the live TypeSafe docs.**
- H1 and H2 follow the `typesafe-ai` skill's rule for source-value selection: *"check candidate coverage: the model cannot choose an omitted value."*
- H3 is the skill's *missing evidence* bucket.
- **[INFERENCE]** that Farama's observation carries per-element colors. Confirm against the installed `miniwob` observation space before building H3.

**The ceiling after the hypotheses.**
- If H1–H4 all land as predicted, the upstream failures fall from 242 to 169. A perfect chooser could then reach (625 − 169)/625 = 73.0%.
- If H1–H5 all land at their predicted counts (14 + 20 + 8 + 8 + 10), v3 gains 60 episodes: 366/625 = 58.6%. That is near GenericAgent-GPT-4o-mini's 56.6 and still under all four rows Jev lost to (GPT-4o's lower bound is 60.0).
- **Closing the rest needs a harness scope decision, not a Jev question.** The largest bucket, op-inexpressible (132 episodes, 21% of the split), is outside Jev's question design. BrowserGym's GenericAgent rows have drag, coordinates, scroll and key presses (receipt, "Against the published rows"). v3 either adds those primitives (a sixth, much larger single-variable change) or reports the 125-task score beside a score on the tasks v1's action space can express.
- **Computed values are also not a Jev change.** The 20 computed-value episodes (arithmetic, algebra, counting, guessing) would need code-side candidate generation.

**Model-limit candidates.** The 30 wrong-choice episodes (tic-tac-toe strategy among them) are what the loop may later name a model limit. They are 4.8% of the split. None can be called that until H1–H5 have run and the state is shown to hold the deciding evidence.

## Boundary

- **The rows log decisions, not pages.** The task-level entries in `TASK_NEEDS` are MiniWoB task knowledge, each paired with a per-episode guard on the row. The per-episode rules for the strip bug, `<option>`, `<tspan>`, prefilled fields, 'none' tails, repeat tails and the calendar step count are computed from the rows alone.
- **The decisive step is chosen by rule.**
  - upstream causes: the first action on the target
  - strip and value causes: the type step
  - tail causes: the first step of the tail
  - wrong-choice: the terminal step, or the first repeated action on timeouts
- **Farama details are [INFERENCE] from task semantics, not measured here.** `CLICK_ELEMENT` gives no usable coordinate, and hover opens click-menu submenus.
- **One run, one model** (`jev-1.13.0`). No replay was run. Every prediction above is untested until the dev-slice replays run.

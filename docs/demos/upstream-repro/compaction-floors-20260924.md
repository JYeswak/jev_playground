# Compaction keep signal: do cheap floors rank needed calls as well as Jev? (bead `jev-al06`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. Keyless: no Jev call, no model call.

**DEVELOPMENT-SET COMPARISON.** Every row here was already labelled, and Jev's scores for it were
already recorded, in `jev-x86y` and `jev-jec6`. The author wrote both readouts and has seen Jev's
AUC on both sets. **Nothing here is a held-out result.** It exists because R100's retry condition
asks for a keep signal with an AUC above 0.65 on a development set before any new held-out test.

## Preregistered (committed before any floor is computed)

**Rows.**
- **x86y:** jev-x86y's 5 included sessions. Session `01a0c085` is excluded by that readout's A1 and
  is never read.
- **jec6:** jev-jec6's 4 sessions.
- The cut point is the one the readouts used (`need.ts cut()`). Each prefix file is re-read from disk
  and refused if its sha256 differs from the sampled one.
- Labels are each readout's final labels (shared, or adjudicated).
- Pinned calls and undecidable calls are left out, as they were in both readouts' rates. That leaves
  32 needed and 126 not-needed calls on x86y, and 30 and 85 on jec6.

**Signals.** Each is a per-call score where **higher means keep**. The direction is fixed now; an AUC
below 0.5 means the signal ranks the wrong way and is reported as it is, not flipped.
- **Jev, recorded:** `keepResult` and `keepCall` from each readout's `decisions.jsonl`, and `need`
  (C2) on jec6 only.
- **Floors**, computed by `work/compaction-floors/floors.ts` from the prefix alone, as a compactor
  would see it:
  - `position`: the call's 1-based order among the prefix's paired calls. Later is higher.
  - `tool_class`: 2 for `read`, `grep` or `glob`; 1 for `bash` or `eval`; 0 for anything else
    (`write`, `edit`, `todo`, `hub`, `task`, `wait`).
  - `result_chars`: the length of the call's result.
  - `later_overlap`: the number of distinct identifiers from the call's input that appear in any
    later prefix message (its text, tool inputs or tool results). An identifier is a run of 6 or more
    of `[A-Za-z0-9_./-]` that holds at least one `/`, `.` or `_`.
- **Reference, not a floor:** `horizon_overlap`, the same count against the horizon messages. It
  reads the future, so no compactor can use it. It is reported only to show how much of the label
  shared identifiers explain.

**Metrics** (`python3 work/compaction-floors/floors.py`, one command, both sets):
- the AUC for needed vs not-needed, by midranks with ties counted half;
- a percentile bootstrap 95% interval: 2,000 resamples of each class, `random.Random(20260924)`;
- the needed calls kept at the cut that drops 40% of not-needed calls, C1's measured drop rate on
  jec6. The cut is the 40th percentile of the not-needed scores. Ties can move the actual drop rate,
  so it is printed beside the count.

**How the floors were written, disclosed.** The four floors are the ones `jev-al06` names. The author
wrote their definitions, the identifier pattern and the tool classes before computing any of them.
He had read both readouts' packets while building them, but opened none again for this, and has
seen no floor value. The author knows Jev's AUC on both sets: 0.691 / 0.689 on x86y, and 0.633 /
0.654 on jec6.

**Numbers only.** No floor or combination is ruled on here. Choosing a signal for a new held-out test
is a separate, preregistered step on fresh sessions.

## Results (development sets, keyless, 2026-09-24)

Definitions were committed at `6669620` before any floor was computed. The run was
`node --experimental-strip-types work/compaction-floors/floors.ts`, which re-read the 9 sampled
session files, all sha-matched, and wrote `features-x86y.jsonl` (200 calls) and
`features-jec6.jsonl` (161). Both files hold ids and five numbers per call, no session text. Then
`python3 work/compaction-floors/floors.py`, which runs on committed files only. **Nothing here is
held out.**

**x86y** (32 needed, 126 not-needed):

| signal | kind | AUC | bootstrap 95% | needed kept at a 40% not-needed drop | actual drop |
|---|---|---:|---|---:|---:|
| keepResult | Jev | 0.691 | 0.582–0.797 | 28/32 | 32% |
| keepCall | Jev | 0.689 | 0.585–0.780 | 30/32 | 40% |
| position | floor | 0.499 | 0.379–0.618 | 20/32 | 38% |
| tool_class | floor | 0.578 | 0.470–0.674 | 29/32 | 12% |
| result_chars | floor | 0.665 | 0.573–0.754 | 28/32 | 39% |
| later_overlap | floor | 0.465 | 0.356–0.585 | 22/32 | 21% |
| horizon_overlap | reference, uses the horizon | 0.555 | 0.437–0.675 | 24/32 | 24% |

**jec6** (30 needed, 85 not-needed):

| signal | kind | AUC | bootstrap 95% | needed kept at a 40% not-needed drop | actual drop |
|---|---|---:|---|---:|---:|
| keepResult | Jev | 0.633 | 0.517–0.747 | 25/30 | 40% |
| keepCall | Jev | 0.714 | 0.605–0.823 | 24/30 | 40% |
| need | Jev | 0.654 | 0.532–0.767 | 25/30 | 39% |
| position | floor | 0.515 | 0.385–0.642 | 14/30 | 38% |
| tool_class | floor | 0.426 | 0.329–0.521 | 21/30 | 16% |
| result_chars | floor | 0.358 | 0.238–0.483 | 12/30 | 40% |
| later_overlap | floor | 0.477 | 0.355–0.597 | 15/30 | 36% |
| horizon_overlap | reference, uses the horizon | 0.556 | 0.435–0.668 | 30/30 | 0% |

**What the numbers show.**
- **No floor is above 0.65 on both sets.**
  - `result_chars` is 0.665 on x86y and 0.358 on jec6. It ranks the wrong way there, and is left
    unflipped as preregistered.
  - `position` is 0.499 and 0.515.
  - `later_overlap` is below 0.5 on both sets.
  - `tool_class` is 0.578 and 0.426. Its three values tie heavily, so its "40% drop" cut drops only
    12% and 16%.
- **Jev's scores are above every floor on both sets.** `keepCall` is above 0.65 on both, at 0.689 and
  0.714. `keepResult` is 0.691 and 0.633, and `need` is 0.654 on jec6. Their bootstrap intervals
  overlap the best floor's on x86y.
- **At a 40% not-needed drop,** Jev's scores keep 28–30 of 32 needed calls on x86y and 24–25 of 30 on
  jec6. The floors keep 12–22 of 30 on jec6.
- **The reference `horizon_overlap` is 0.555 and 0.556.** Shared identifiers with the horizon explain
  little of the need label as the labellers applied it. On jec6 its 40th-percentile cut is 0, so it
  drops nothing.

**Against R100's retry condition** (a keep signal with AUC above 0.65 on a development set):
`keepCall` meets it on both development sets. The library does not use `keepCall` for the verbatim
keep; it uses it only to decide whether to drop a call whole. No floor meets it on both sets. That
is a development-set fact, not a held-out result, and nothing here chooses a signal.

**Re-score, keyless:** `python3 work/compaction-floors/floors.py`, from committed files only.

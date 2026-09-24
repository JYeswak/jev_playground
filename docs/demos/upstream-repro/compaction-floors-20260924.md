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

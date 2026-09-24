# Held-out test: keep a tool result when Jev's `keepCall` clears a cut fixed on the development sets (bead `jev-5720`)

CopperHeron (pane at index 2, Anthropic model), 2026-09-24. **PREPARED-NOT-MEASURED** until the live
replay. Jev only (`jev-1.13.0`, pinned). No Anthropic API.

## Preregistered (committed before any session is sampled, labelled or replayed)

**Why.** R100's retry condition asks for a keep signal with an AUC above 0.65 on a development set.
`jev-al06` (`9094427`) found that Jev's `keepCall` is the only signal that clears it on both
development sets: 0.689 on `jev-x86y` and 0.714 on `jev-jec6`. No cheap floor did. This is the first
test of that signal on sessions neither development set used.

**Rules compared,** on the same calls in one replay. Each keeps a call's result verbatim when its
score reaches the cut. Pinned calls are always kept and are in no rate.
- **C0, current:** `keepResult ≥ 0.5`.
- **C1:** `keepResult ≥ 0.15` (jev-jec6's C1).
- **C3:** `keepCall ≥ T_C3`, with **`T_C3 = 0.36`**.

**How `T_C3` was fixed, from the development sets only.** It is the smallest `keepCall` cut at which
at least 50% of the pooled development-set not-needed calls are dropped. The pool is `jev-x86y` and
`jev-jec6`, final labels, unpinned, undecidable left out. That cut is 0.36, dropping 110 of 211.
It aims at the bar's second part. The development-set outcome at 0.36 is below, and the development
data were used to choose it:

| development set | needed kept | Wilson 95% | not-needed dropped | Wilson 95% |
|---|---:|---|---:|---|
| jev-x86y | 28/32 | 0.719–0.950 | 59/126 (47%) | 0.383–0.555 |
| jev-jec6 | 21/30 | 0.521–0.833 | 51/85 (60%) | 0.494–0.698 |
| pooled | 49/62 | 0.674–0.873 | 110/211 (52%) | 0.454–0.588 |

**The bar is not met on the development data at `T_C3`.** The pooled needed-kept lower bound is
0.674, below 0.80, and no cut that drops at least half the not-needed calls reaches it there. The
held-out test therefore measures whether fresh sessions behave better than the development sets;
by the development numbers they would have to. For scale, with 60 needed calls the bar needs 55 kept
(92%), and with 40 it needs 37.

**Bar**, per rule, jev-jec6's unchanged. Both must hold:
- the Wilson lower bound of needed kept is at least **0.80**;
- at least **50%** of not-needed results are dropped (point estimate).

**Sessions** (`work/compaction-c3/c3.ts select`, run once after this commit):
- **Eligible:** jev omp session files at the top level, last written before
  `CUTOFF = 2026-09-24T18:00:00Z`, at least 50 paired tool calls, **200 KB to 12 MB**.
  - The upper bound is raised from `jev-x86y`'s 3 MB because the 200 KB–3 MB jev pool is exhausted:
    every eligible file in it was sampled or screened by `jev-x86y` or `jev-jec6` (a structure-only
    count at 18:21Z found 0 left). This was decided from that count, before any sampling.
  - The prefix is still the first 40 paired calls, but longer files are longer-running sessions,
    which may differ from the development sets.
- **Excluded:** every session `jev-x86y` or `jev-jec6` sampled or screened out, and `jev-0c6`'s files
  A and B.
- **Sample:** a seeded order (mulberry32, seed 20260926), taking sessions in that order until **8 pass
  jev-jec6's rider screen** (`RIDER_PATH`, imported from `work/compaction-keep/keep.ts`, with its A1
  names). Fewer than 3 passing makes the readout UNDERPOWERED. Pane 1 runs its name check over the
  packets before any labeller sees them.

**Compaction point and label.** Both are `jev-x86y`'s, unchanged:
- `need.ts cut()`: the prefix runs through the 40th paired call's result, and the horizon is the next
  40 messages;
- `needed`, `not-needed` or `undecidable`, as preregistered at `108d6bd`, plus the restatement reading
  disclosed there;
- two fresh labellers spawned by pane 1, blind to each other and to any score;
- pane 1 adjudicates every disagreement;
- packets go in `/tmp/c3-packets` and are never committed; `calls.json` holds ids only.

**Live replay** (`c3.ts replay --live`, one run, after `c3.py ready` exits 0):
- one library `compactMessages` call per session with jev-x86y's options, which record `keepCall` and
  `keepResult` for every call;
- no other question is asked;
- `decisions-pass.json` records requests, input tokens and spend at $0.042 per million input tokens.

**Metrics** (`c3.py score`). For C0, C1 and C3 on the final labels and on each labeller alone:
- needed kept verbatim, and not-needed results dropped, each with a Wilson 95% interval;
- the bar;
- a per-session table.

A NEGATIVE_EVIDENCE row is written if C3 does not meet the bar.

**NO-CLAIM.** One project, one cut point per session, a 40-message horizon, one model pin, labels
judged from truncated packets. `T_C3` was chosen on the development sets, whose own numbers at that
cut fall short of the bar.

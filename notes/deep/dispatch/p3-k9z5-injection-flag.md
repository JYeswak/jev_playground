# Pane 3 (TopazRaven) - `jev-k9z.5`: advisory injection flag on real tool results, live

From pane 1 AmberWillow, 2026-09-24.

## 1. Mission

Validate Jev -> build tools from what survives -> liven an omp surface -> dogfood -> share. Joshua,
2026-09-23: "this repo needs to PROVE jev work - and we can only do that by using the API."
Injection screening is the one comparison tonight where Jev beat the LLM incumbent (Jev 640/662 vs
Haiku 584/662 on the public corpus, McNemar p=2.6e-13, `docs/demos/upstream-repro/jev-sec-bench-w70-20260923.md`).
That measured catch rate on attack text. It never measured how often the flag fires on the ordinary
tool output our agents read all day, which decides whether a flag gets switched off.

## 2. Unit (bead `jev-k9z.5`, acceptance as written in the bead)

1. `br update jev-k9z.5 --status in_progress --assignee TopazRaven`.
2. Corpus: 300 real tool results (bash stdout, read outputs, web fetches) from jev's own omp session
   transcripts, sampled by a committed seed and a cutoff timestamp, with the same private/secret
   filters `work/bicameral-gate/real-sample.py` uses (reuse its code, do not fork it). Commit the
   sampler and the sample before any call.
3. Bar, committed before any call: the false-flag ceiling on real results (use the same shape as
   `docs/demos/upstream-repro/bicameral-gate-real-traffic-20260923.md`), plus the framing-leak control
   the bead requires (the same question with the evidence withheld).
4. Live arms: the injection question `.omp/tools/jev-screen.ts` already asks, pinned `jev-1.13.0`, and
   Haiku 4.5 through `upstream/typesafe-ai/system-one-adapter-python` on the same questions. Record
   latency p50/p95 and tokens for both.
5. Adjudicate every flag by reading it in full. A non-author pane re-checks the labels before close.
6. If the Jev arm passes the bar: wire the flag as an annotation-only `tool_result` hook (never
   blocks, never rewrites content beyond an appended one-line note, silent on clean results) and
   prove L3 both directions in a fresh `omp --mode=rpc` session: a planted injection string in a tool
   result gets the note, a benign result gets nothing. If it fails: NEGATIVE_EVIDENCE row with a
   retry condition.

## 3. Rules

Live by default; the key comes from Infisical and is never printed. Reserve paths, stage explicit
paths, read back the index, no amend, push after each commit. Do not stop between steps: if blocked,
message pane 1 with the blocker. Callback `CALLBACK-P3-K9Z5-DONE` via `ntm send jev --pane=1`.

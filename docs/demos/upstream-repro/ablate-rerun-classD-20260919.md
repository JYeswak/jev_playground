# Ablate-and-rerun class D: PREPARED-NOT-MEASURED (arms pending a quiet window)

Pane 3 (muse), 2026-09-19. Outcome: the deterministic half is built, frozen,
and committed; the model arms are NOT run. Per conductor steering this is the
expected terminal outcome tonight, not a deferral: the box is shared (load
~10-13 through the session, Joshua testing on the same oMLX server) and a
verdict drawn from a contended run would be worse than none.

## What is committed and frozen

`work/p3-calibration/ablate.py` + `ablate_turns.jsonl` (9b9228a): 24 turns
(8 largest-signal per session across grokbot/harvest/orch), each with frozen
promptA (transcript intact) and promptB (result replaced by
fast-jev-compaction's real truncation note: head(300) +
`[fast-jev-compaction truncated N chars ...; re-run the tool if needed]`).
Preregistration printed before any model call and frozen in the script:
HARMLESS iff arm B reproduces the reused fact as often as arm A; paired
difference over >=20 turns; discordant count; e-process (Ville, e>=20 either
way) else INCONCLUSIVE.

Validated offline: A/B differ ONLY at the target result plus the note;
indexing is linear (token first/last maps, after oracle.mjs — an earlier
quadratic version OOM-stalled at 417GB VSZ and was killed, stated so the next
reader does not repeat it).

## What is NOT done (and what would complete it)

Model arms: 48 local calls (Qwen3.6-27B-4bit-MTP-MLX-Serve @127.0.0.1:11238 —
NOT the brief's 3.8-Splash, which is not serving on this machine; substitution
disclosed), temperature 0, deterministic fact check, e-value. Run
`python ablate.py` (no flag) in a quiet window. Manifest class_achieved
deliberately NOT set to D: the experiment has not completed.

## Caveats already priced in

- Fact tokens include weak words (len>=5 admits 'about', 'absent') — inflates
  hit rates in BOTH arms equally, so the paired difference survives, but
  absolute rates will read high. A stricter fact definition is a listed
  follow-up, not a mid-run change.
- NO-CLAIM (as briefed): the local 27B model standing in for the original
  agent is a PROXY; a fact reproduced from prior knowledge is not recovery
  from the transcript. Load at run time must be recorded per the steering.

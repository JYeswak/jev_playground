# PREREG — wbel enforcement replay on 7d organic loads (bead jev-wbel)

Frozen 2026-10-02 before any label or live call. Conductor order: decide
veto ENFORCEMENT (block on noul < cut) on a blind-labelled organic sample.

## Corpus (keyless, frozen)

`work/wbel/replay-corpus.json`: 200 rows, seed 20261002, sha `49b27d0243cb`,
drawn from 4,135 skill loads (read tool, skill:// or SKILL.md, fixture dirs
excluded) in 671 session files across root/claude/muse/codex profiles,
2026-09-25T15Z–2026-10-02T15Z. Each row: ts, profile, session, path, skill,
request (last user text ≤2000 chars, 199/200 non-empty), following (next ≤6
task tool calls, present in 162/200). Reproducer: `work/wbel/extract-replay.py`.

## Question and cut (frozen, identical to shadow veto)

Noul: "Does the skill '<skill>' do the specific thing the user's request asks
for? It is described as: <description>" (kit `fitsQuestion`). Description:
`.omp/extensions/jev-skill-veto.ts` `readDescription` at replay time, recorded
per row. Cut 0.40: veto iff noul < 0.40. Fail-open allow on
timeout/error/invalid/refused, counted as exclusions.

## Blind labels (all 200, before any score exists)

Label per row, blind to scores: FIT = the skill serves the request topic AND/OR
the following trail shows the agent using it; UNFIT otherwise. Evidence shown:
request + description + following trail. Labels in `work/wbel/replay-labels.json`
(sample_id -> {description, label}); corpus file untouched post-sha.

## Bar (ENFORCE vs STAY-SHADOW, fixed pre-call)

ENFORCE iff blind precision P(UNFIT | veto) >= 0.80 AND miss rate P(FIT | allow)
<= 0.10 AND would-vetoes >= 30 (else NO-DECISION, underpowered). Report: veto
rate, Wilson 95% CIs, exclusions, per-call model/status/tokens/latency/spend,
miss analysis by skill. FAIL/NO-DECISION keeps shadow; misses join blind-label pool.

## Caps and harm limits

<= 200 calls, spend cap $0.01 (~$0.004 expected), stop on 401/402/403 or cap,
20 s timeout, checkpointed resume by sample_id. NO-CLAIM beyond session skill
loads. Runner: `work/wbel/run_replay.mjs`; receipt `work/wbel/replay-rows.jsonl`
(sample_id, skill, noul, pred, status, tokens, latency; no raw text).

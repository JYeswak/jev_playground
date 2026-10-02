# PREREG — D9 verify-only veto, live held-out run (jev-hj5t)

Frozen 2026-10-02 before any live call. Live jev-1.13.0 only.

## Design (D9, from BREADTH_SKILLS.md)

One fits-Noul per row (demo wording, `demos/skill-suggest/demo.mjs:53`):
"Does the skill 'X' do the specific thing the user's request asks for?
It is described as: <name+description>."
State: `{request: <prompt as harvested, <=2000 chars>}`. One question per request.
Action: VETO the top-1 hint iff noul < 0.40, else ALLOW. Fail-open: timeout, error,
invalid/refused answer -> ALLOW (logged as exclusion, never a veto).

## Population (keyless, frozen)

- `var/agent-tmp/skills-breadth/build_rows2.py` over all 3,363 session files
  (~/.omp/agent/sessions + all profiles): 29,174 windowed rows
  (prompt + first SKILL.md read within next 10 events, else silent),
  515 pairs / 28,659 silent / 3,346 sessions.
- Eligible (a hint would fire): top1 is not None (exact R133 `shortlistSkills` replica,
  `kit/src/skill-hint.ts:40-55`) -> 29,082 rows.
- Split by session: held = sha256(session) % 5 == 0 -> 688 held sessions, 5,644 eligible.
- Sample (seed 20261002, `freeze_sample.py`): ALL 10 held correct (top1==target) + 240
  random held others = 250 rows, sha `78174dd7c1cf` (`sample.json`).
- Baseline always-allow on sample: 240 wrong / 10 correct.

## Bar (paired per-row vs always-allow)

- PASS iff ALL hold: (a) veto precision = vetoed-wrong / vetoed-total >= 0.80;
  (b) misses = vetoed-correct <= 2/10; (c) materiality: vetoed-wrong >= 24 (>=10% of wrong).
- Report: paired counts, Wilson 95% CIs, per-call model/row-hash/status/tokens/latency/spend,
  exclusion count. No held-out retest on FAIL without a one-variable dev change (none exists
  keylessly here; FAIL -> NEGATIVE_EVIDENCE with the numbers).

## Caps and harm limits

250 calls (1/row), spend cap $0.02 (~$0.006 expected), stop on 401/402/403, stop on cap.
Runner: `work/skills-breadth/run_veto.mjs` (kit client, same shape as demo live path);
receipt: `work/skills-breadth/receipt.jsonl` (hashes/decisions/spend, no raw text).
Scratch corpora stay uncommitted; this file + BREADTH_SKILLS.md + bead comments committed.

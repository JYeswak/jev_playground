# W7.2 receipt — jev-ultrafast @452c1ad (browser-use, MIT)

Clone: /Users/josh/Developer/jev/jev-ultrafast. Untouched: `git status --porcelain` empty before first call, after pytest, after guards, and at close; HEAD 452c1ad throughout. All defects/scratch in /tmp only (plant copy + harness under /tmp/w70-ultra; plant copy and Chrome profile removed at close). No commits. Model `jev-1.13.0` pinned via TYPESAFE_MODEL for all live Jev calls. Key only via `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`. No key or customer data printed; corpus is synthetic, no customer state anywhere.

T4 bar source: notes/deep/dispatch/p6-w70-t4bars.md commit 070efe6 dated 2026-09-22 21:38:26 -0600; first live call 21:42:08 — bar predates. Cap note (breach, mine): bar caps 25 Jev calls; I made 32. Cause: run_t8.py imported run_t4 without a `__main__` guard, silently re-running T4 (+10) before T8 (+12) on top of official T4 (10). No further Jev calls after discovery. Counts below separate official run (10) from supplementary re-run (10).

## T1 pin/env — PASS
- SHA 452c1ad2dd628008f1d5608f28158d76e49e6cc0; commit date 2026-09-16 19:20:01 -0700 ("Reduce browser round trips and record a 7-second Flights demo"); LICENSE MIT (LICENSE:1-5, "Copyright (c) 2026 Browser Use"); `git status --porcelain` empty.
- python3 --version = 3.9.6 (system); project requires-python >=3.12; `uv run python --version` = 3.14.2; uv 0.9.28.

## T2 own suite fresh + plant — PASS
- `uv run pytest`: 31 passed in 0.20 s (31/31, 0 fail, 0 skip).
- `uv run python scripts/check_guards.py`: 21/21 PASS vs real Chrome, no model calls. Route 1 (port 9222 already listening): nothing on 9222, harness daemon log "chrome-not-running". Route 2: headless Chrome --remote-debugging-port=9222 --user-data-dir=/tmp + BU_CDP_URL=http://127.0.0.1:9222 → 21/21 (wall 2.56 s). Killed at close.
- Plant (in /tmp/jev-ultra-plant copy, clone untouched): model.py:44 `raise ValueError` → `pass  # PLANTED DEFECT`; suite run with clone venv python → 7 failed, 24 passed (test_invalid_choice_is_rejected all 6 params DID NOT RAISE + test_click_cannot_consume_a_text_target KeyError '999'). RED confirmed.

## T3 clone claims (5+, file:line) — 7 demonstrated
1. One request per decision: operation + per-op target heads share one POST (model.py:91-117); suite asserts single call and exact question set (tests/test_agent.py:77-96). DEMONSTRATED live: 10/10 T4 answers arrived in one round trip each.
2. Only the matching head executes; unused heads cannot cause action (model.py:124-130); suite sends poisoned click_target with valid TYPE_TEXT and asserts choice e1 (test_agent.py:99-113). DEMONSTRATED (live valid-2/valid-4 TYPE_TEXT:2 exact).
3. validate_choice invariants — choice∈ids, prob keys==ids, finite [0,1], sum≈1 (±0.02), choice is argmax (model.py:30-45); 6-mutation rejection test (test_agent.py:48-64) + fresh plant turns all 6 RED. DEMONSTRATED.
4. DONE/BLOCKED terminate with zero browser mutation after a freshness recheck (agent.py:93-100). DEMONSTRATED live: 4 BLOCKED picks, no act() path (choose-level; no browser driven).
5. Stale-page discipline: decision consumed before any mutation (agent.py:88-91); StalePage → re-observe, never double-execute (agent.py:59-64, 107-108, 116-117); suite: stale-consumed-before-mutation, interrupted-dropdown-once, navigation-reobserves (test_agent.py:181-186, 254-267, 315-320). PARTIAL (suite passes fresh; live browser not driven this rung).
6. Text helper never guesses: missing TEXT_MODEL_API_KEY → ValueError (model.py:160-163); output must be exactly {"text": non-empty str ≤2000} (model.py:187-193); suite covers missing-key + 4 malformed shapes (test_agent.py:154-157, 305-312). DEMONSTRATED (fresh suite + T9 text-key-absent probe).
7. Freshness/execution guards hold on real Chrome: 21/21 (T2 above); moving-target click, overlay-block, 9 page-mutation invalidations, action-specific guards. DEMONSTRATED.

## T4 prereg bar (N=10 disclosed-authored states: 5 exactly-one-valid alternating CLICK:2/TYPE_TEXT:2, 5 no-valid→BLOCKED; prevalence 0.5) — BAR-PASS AT FLOOR
- Official run (10 calls): 8/10 correct; 0 invalid executions; 1 genuine false advance (none-5 CLICK:1 on dead-end page) + 1 WAIT miss (none-3, no mutation — miss, not advance). Valid half 5/5; none half 3/5.
- Latency wall ms [521,178,163,194,167,147,204,192,216,221]: p50 193, p95 ~386 (interp), max 521. Tokens official run: 12114 in / 781 out. Cost this rung: 32 Jev calls total (see breach note) + 10 OpenRouter gpt-4o-mini calls.
- Supplementary accidental re-run (10 calls, same states): 7/10 with 1 transient HTTP 520 → clean RuntimeError refuse (valid-1), none-3 WAIT again, none-5 CLICK:1 again — misses are stable, not noise.
- Random-target floor (seeded 20k trials over offered spaces via pure action_space): mean 0.203, P(≥0.8) = 0.0001. Jev 0.8 beats it decisively.

## T5 floors — PASS (Jev beats all; margin honest)
- always-majority 0.50 (5/5 tie) | lexical-keyword rule (TYPE_TEXT iff goal has enter/type/into, highest index) 5/10 = 0.50 (5/5 valid, 0/5 none) | random-target ~0.20. Jev 0.8 beats all three; but the lexical rule's 5/5 valid half shows the authored valid states are keyword-obvious — the +0.3 margin over the cheap rule is the honest signal, not the +0.6 over random.

## T6 incumbent (small LLM, same 10 states) — MEASURED
- Keys found via infisical names-only listing (TYPESAFE_API_KEY, OPENROUTER_API_KEY, ANTHROPIC_API_KEY, XAI_API_KEY, OPENAI_API_KEY present); no values printed. Arm: openai/gpt-4o-mini via OpenRouter chat-completions, offered ops+targets in prompt, JSON answer, 10 calls, 0 invalid.
- Result: 6/10 (TYPE_TEXT:2 both right, all three CLICK:2 → distractor CLICK:1, none-3 WAIT miss; none-5 correctly BLOCKED — the one Jev stably misses). Jev 8/10 beats the small-LLM arm by 0.2 on authored states; arms disagree informatively (LLM avoids the false advance Jev makes; Jev grounds CLICK targets the LLM does not).

## T7 bins-with-counts — REPORTED (not single-bin)
- [0.4,0.6): 0/2 | [0.6,0.8): 2/2 | [0.8,1.0]: 6/6. Directionally ordered (both errors below 0.6) at N=10; calibration not estimable beyond direction — reported as bins, not a calibration claim.

## T8 repeats (3 states ×3 + reworded-state-identical; 12 calls) — 0 FLIPS, 1 STABLE MISS
- valid-1: [CLICK:2 ×3], reword → CLICK:2. none-1: [BLOCKED ×3], reword → BLOCKED. none-5: [CLICK:1 ×3], reword ("Put London in as the arrival city") → CLICK:1. Rep flip 0/3 rows; reword flip 0/3. No >20% flag; but none-5 is stably wrong across 5 exposures (T4, re-run, 3 reps, reword) — determinism of the error, not stability of knowledge.

## T9 httpx client (model.py) — 7/7 REFUSE, host survives (local only, 0 Jev calls)
- conn-refused → RuntimeError "Model connection failed; no action executed." | http-500 → RuntimeError "Model provider returned HTTP 500; no action executed." | http-200-malformed through choose() → ValueError "Invalid TypeSafe response; no action executed." (validation lives in choose/validate_choice, not transport — recorded layering) | second malformed shape → same ValueError | timeout (0.2 s client vs 2 s holding server; TimeoutException ⊂ HTTPError path, model.py:19) → RuntimeError connection-failed | TYPESAFE_API_KEY absent → KeyError before any network | TEXT_MODEL_API_KEY absent → ValueError, no guessing. Plus live-observed HTTP 520 → RuntimeError refuse, no partial execution. all_refused=true.

## T10 verdict class + tier + NO-CLAIM
- Verdict: BAR-PASS AT FLOOR (8/10 ≥ 0.8, 0 invalid) but SEAT HOLD. Result class SELF (disclosed-authored corpus, N=10). The bar is met exactly; the seat is refused on this evidence: one stable false advance on a dead-end page (none-5: "Start new search" link reads as progress), a second stable WAIT miss, +0.3 margin over a trivial keyword rule, and zero real-browser task-success states. The named seat risk is links-that-look-like-progress on dead-end pages.
- NO-CLAIM: no browser was driven live; no production action executed; synthetic agreement is not task success; confidences are not calibrated (N=10); gpt-4o-mini arm is a same-state probe, not the clone's browser-use incumbent; HTTP 520 behavior seen once.

## Boundary
- Clone files never modified (status clean at close, HEAD 452c1ad). Live Jev spend: 32 calls (25 cap breached by 7 via harness import side effect — disclosed). OpenRouter spend: 10 × gpt-4o-mini. Evidence: /tmp/w70-ultra/{run_t4,run_t8,run_t6,run_t9,run_t5t7}.py, t4-official.json (verbatim first-run rows), t4-results.json (supplementary re-run), t6-results.json, t8-results.json, t9-results.json.

## Pane-6 verification (2026-09-23, before landing)

- `git -C jev-ultrafast status --porcelain` → empty; HEAD `452c1ad2dd628008f1d5608f28158d76e49e6cc0`; LICENSE MIT.
- `uv run pytest` re-run → 31 passed in 0.28s.
- `check_guards.py` re-run vs fresh headless Chrome (own supervised process, killed after) → PASS: 21 browser guard checks.
- T4 bar commit `070efe6` dated 2026-09-22 21:38:26 -0600; `t4-official.json` mtime 21:43 — bar predates first live call.
- Cap breach (32 vs 25) kept in the receipt as disclosed; verdict SEAT HOLD stands.

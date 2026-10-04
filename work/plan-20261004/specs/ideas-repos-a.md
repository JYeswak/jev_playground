# Ideas from clones A (14 repos) vs `classifier` plan (work/plan-20261004/PRODUCT.md)

Read: each README head, grep of core source for question construction, our refs in EVAL.md / NEGATIVE_EVIDENCE.md / docs/LEDGER.md / .beads/issues.jsonl. Deeper source bodies: UNVERIFIED unless a line is cited.

## Per repo: what it is / ported or refuted here
| repo | what it is | our status |
|---|---|---|
| Canny | Claude Code/Codex hook ledger; blocks "done" without a passing check (Canny/README.md "The one rule") | Run W7.0, FLOOR (EVAL.md:1670); ledger port STOPPED: 1067/1145 loses to always-not-done 1108/1145 (EVAL.md:1678) |
| Janus | small/large model router that measures its threshold, ships none (Janus/README.md; src/janus/measure.py:134, sweep.py:99) | T1–T3 earned, 7/8 claims recomputed keyless, T4 proposed (EVAL.md:1458-1460); LEDGER.md:212 thresholds carry within, not across, datasets |
| OneVOneJev | browser FPS where Jev picks bot actions (server/src/jev.ts:7,246) | Build passes, 0 tests, no upstream oracle (EVAL.md:2165,2178) |
| agent-beacon | cross-harness session memory; Jev promotes runs to shared memory (EVAL.md:2536) | Rubric validated live: AUROC 0.7475, bar not met (EVAL.md:2548+); guard ported as jev-sdag; bead jev-b4jj open |
| agent-desktop | Rust accessibility-tree computer-use CLI; no Jev call found in src/crates (grep) | smoke N=4, withheld, not accuracy (EVAL.md:1674) |
| bicameral | Pi harness: LLM writes, System One gates (decideGate/HonestFinish/Stuck), packs of noul/score/choice (packages/packs/src/loader.ts:22-32) | Ported as gate (work/bicameral-gate); 78/97 clear risky; 19/37 on disputed = FAIL (NEGATIVE_EVIDENCE.md:3418+); LEDGER.md:149,168 |
| commit-miner | Rust CLI: Noul per category/CWE on commit diffs (src/miner.rs:30,52,72) | W7.2 37/0 tests (EVAL.md:1622+); on our 130 commits (EVAL.md:288) |
| fast-jev-compaction | keep-call / keep-result Nouls per tool call, no summaries (README §How it works 4-6) | Ported (compaction/, LEDGER.md:41); keep rules lost R99/R100 (beads jev-9gtw.5/.6); dangling symlink (NEGATIVE_EVIDENCE.md:1416) |
| foreman | Jev Noul board supervising Codex workers (README diagram; src/foreman/foreman/jev.py:61-77) | REFUTED: AUC 1.000 authored → 0.750 on 186k real windows, ~0.016% prevalence (NEGATIVE_EVIDENCE.md:1293,1305) |
| hermes-jev-skills | 10 SKILL.md Jev skills: routing, search, memory, web-screen, turns, skills, triage, mail, GUI/browser (README table) | 1152 tests pass; web-screen reproduction jev-vqaq; seam jev-vrbl; installed, usage census jev-0cg9 (EVAL.md:2530,2570) |
| jev-agent-failure-benchmark | Who&When Pro: 3 Choice (agent/step/mode) per failed trace (src/jevbench/backends/jev.py:113-119) | FLOOR: N=300 agent 111/139, LB 0.7243 > floor 0.1942; ECE 0.0545; gpt-5.4 NOT-RUN (EVAL.md:1442-1444) |
| jev-align | GEPA + active-labelling loop for a Jev AI Function (README §How it works) | REFUSED: 39/40 but ambiguity sampler fails; lexical 0.925 (EVAL.md:1382-1399) |
| jev-benchmark | 60-case tool-call risk Choice (4 classes) with ECE (README) | Seat REFUSED: lexical cascade 58/60 beats live 52/60 (EVAL.md:1440; LEDGER.md:211) |
| jev-codex-router | per-turn Codex model+effort routing, fail-open, kill switch (server/jev_server.py:82,100-120,710) | Pinned, T9 fail: Jev error coerced to astra route (EVAL.md:1489-1494); backtest collapsed-sample bug jev-azy |

## Ideas
|repo or doc|idea (one line)|primitive(s) + pattern|evidence the repo gives (claim + reproducible?)|maps to plan family/verb, or GAP|already tested by us?|
|---|---|---|---|---|---|
|Canny README "The one rule"|Facts block, judgments only nag; a done-claim refused by ledger fact, not by probability|Noul CLAIMS_DONE (src/hook.ts:39) + deterministic ledger|Live verbatim session; `canny replay` deterministic from ledger (claim; replay reproducible offline)|verify (+ gate policy: advisory-only mode)|Yes: ledger port lost to majority (EVAL.md:1678)|
|Canny src/hook.ts:197|one Noul per project rule over a diff|Noul × N rules, same state|none quantified|diff / verify (rules-from-file)|UNVERIFIED as rule check; Canny FLOOR row EVAL.md:1670|
|Canny README|`replay` command: recompute verdicts from the stored ledger|log replay|claim; reproducible by design|GAP-ish: plan has `eval`/`cases`, no `replay` of logged decisions|no|
|Janus README; measure.py:134|ship no default threshold; measure it on labelled data|Choice conf + sweep (sweep.py:99) of operating points|Banking77 80.2% @0.67 cheaper than large alone; replayed from committed JSONL (reproducible keyless)|calibrate / route|Yes: 7/8 claims recomputed (EVAL.md:1460); LEDGER.md:212|
|Janus agreement.py:58|on unlabelled logs report agreement with a reference model, and refuse wording implying accuracy|log mode, forbidden-word guard|code guard (reproducible)|GAP: `eval --log` agreement mode without gold|no|
|OneVOneJev src/jev.ts:7,246|real-time action choice with heuristic fallback|Choice+Noul per tick, fallback|none (0 tests, EVAL.md:2165)|no reusable idea: game loop; fallback pattern already in plan as abstain|build only|
|agent-beacon evaluator.go (EVAL.md:2536)|promote session to shared memory iff completed ∧ task_success≥0.5 ∧ mean≥0.6, human approves|3 Noul, mean-of-three|no held-out validation in repo|memory|Yes: AUROC 0.7475, bar_met=false (EVAL.md:2548+); jev-sdag; jev-b4jj|
|agent-desktop README|skeleton overview then drill-down cuts snapshot tokens 78–96%|state shaping, not a primitive|claim; README image 30,743 vs 383 tokens; no receipt read|GAP: state-shaping for the 32k/16k limit (relevant to watch/route GUI)|smoke only (EVAL.md:1674)|
|bicameral packs/src/loader.ts:22-32|questions as declarative packs (noul/score/choice) loaded from files|all three primitives, pack file|41 vitest (reproducible)|`cases`/question packs per family|Yes: gate port (NEGATIVE_EVIDENCE.md:3418; LEDGER.md:149)|
|bicameral README|decideGate / decideHonestFinish / decideStuck; degrade to patterns not passthrough|Noul + deterministic fallback|vitest (EVAL.md:285)|gate, verify, watch(stuck)|gate yes; stuck = foreman refutation|
|commit-miner src/miner.rs:30,52,72|Noul per category and per CWE, then evidence Noul "does the actual change…" second pass|Noul fan-out + conditional 2nd round|37 tests; cost from usage tokens (reproducible keyless)|diff (classify commits) — plan family `diff`|Yes, our 130 commits (EVAL.md:288)|
|commit-miner README|saved scans, `list/show/export`, filter without rescoring|result store|code|GAP: plan has no persisted run store / `show`|no|
|fast-jev-compaction README §4-6|two Nouls per tool call (keep call / keep result); shard questions, resend full state under 30k|Noul ×2, request sharding|29/29 tests; live 87.1% chars saved (EVAL.md:11-20)|effort? / memory — compaction is GAP as a family|Yes: keep rules lost (jev-9gtw.5/.6)|
|fast-jev-compaction README §3|staged state fitting with tokenizer-free estimate|state budgeter|code + tests|GAP: shared state-fit layer for the 32k/16k limits (plan should own it, backend-specific)|partly (compaction port)|
|foreman README|board of 8 Nouls (complete, tests_sufficient, stuck, off_track, ready_to_finish…) → continue/stop/retry/verify|Noul board, one state|"architectural experiment", no claim|watch / verify|REFUTED at prevalence (NEGATIVE_EVIDENCE.md:1293-1305)|
|hermes-jev-skills README table|model routing per turn, shadow mode first|Choice over models|~0.4 s/turn (claim)|route (+ shadow = plan `watch`?)|routing via codex-router; shadow UNVERIFIED as tested|
|hermes-jev-skills README|web/tool-result injection screen, withheld before agent reads|Noul + local pattern fallback|35/39, 0/553 clean on private data (EVAL.md:2530)|screen|Yes: jev-vqaq reproduction; seam jev-vrbl|
|hermes-jev-skills README|skill selection among 377 skills|Choice ≤255 → needs batching|~2.8 s (claim)|meta `skillgap`? / route|UNVERIFIED|
|hermes-jev-skills README|search: which results to open, does evidence answer, which query next|Choice + Noul|~1.9 s/round (claim)|rank|UNVERIFIED here|
|hermes-jev-skills README|turn keep/summarize/drop to fixed size; handoff digest measured WORSE, not shipped|Choice per turn|11 vs 4 vs recency (claim); own negative result|memory/effort|UNVERIFIED|
|hermes-jev-skills README|mailbox lanes, triage urgency, GUI/browser next action from pre-judged safe table|Choice|latency/cost claims only|GAP: mail/triage family; GUI action selection GAP|no|
|jev-agent-failure-benchmark backends/jev.py:113-119|failure attribution: responsible agent, decisive step, error mode as 3 Choices|Choice ×3 joint state|beats gpt-5.4 all axes, $1.28 (claim, paper baselines, data pinned)|GAP: post-mortem/attribution family (closest: verify)|Yes: FLOOR passed, gpt-5.4 NOT-RUN (EVAL.md:1442)|
|jev-align README|active labelling: rows Jev is least sure of + random audit → human labels → GEPA rewrites definition; never auto-accept|Noul/Choice/Score/multilabel|127 tests (EVAL.md:1382)|calibrate / cases (label loop)|Yes: REFUSED, ambiguity sampler misses confident-wrong (EVAL.md:1394)|
|jev-align README|multilabel task type|N Nouls|code|GAP: plan names Choice/Score/Noul, not multilabel|no|
|jev-benchmark README|clear/ambiguous/adversarial split + ECE "is confidence worth routing on"|Choice 4-class|91.7%, ECE 0.0505, results committed (reproducible)|gate / eval|Yes: lexical 58/60 beats live 52/60, seat refused (EVAL.md:1440)|
|jev-codex-router jev_server.py:82,117-120|one Choice picks model tier, another picks thinking effort|Choice ×2|−60% cost on 237 turns BACKTEST.md (claim; bug jev-azy)|route + effort|Yes: fail-open coerce flagged T9 (EVAL.md:1492)|
|jev-codex-router README|kill-switch sentinel file + fail-open + decision log for calibration|ops pattern|code|doctor / watch; log feeds calibrate|coerce criticised (EVAL.md:1492)|

## GAPs ranked by plan impact
1. **Base-rate gate before any seat** (foreman 0.016%, jev-benchmark lexical 58/60, Canny majority 1108/1145, jev-align lexical 0.925): every family's `eval` must print majority + lexical floor and prevalence, and `ready` must refuse when a rule ties. Evidence: NEGATIVE_EVIDENCE.md:1305, EVAL.md:1440,1678.
2. **State-fit layer** (fast-jev-compaction staging, agent-desktop skeleton): plan needs a shared, backend-aware budgeter (32k Jev / 16k Clef) — not exposed as a verb.
3. **Unlabelled-log agreement eval** (Janus): `eval --log --reference` with wording guard; plan's eval assumes gold.
4. **Decision replay / run store** (Canny replay, commit-miner list/show/export, codex-router decision log): no `replay`/`show` verb.
5. **Failure attribution family** (Who&When Pro): passed our floor; no plan family fits.
6. **Multilabel task type** (jev-align): not a named primitive; is N Nouls.
7. **Mail/triage and GUI next-action** (hermes): not in the 10 families.
8. **Shadow mode** (hermes, codex-router): plan should state whether `watch` = shadow (decide+log, no act).

## Verbs/primitives the plan does not expose
`replay`, `show/export` saved runs, `eval --log` (agreement), multilabel, `--shadow`, kill-switch file, state-fit/`budget` preview, conditional second-round questions (commit-miner miner.rs:72).

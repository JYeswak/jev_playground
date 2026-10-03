# Jev — typed decisions for code

Jev is TypeSafe's System One model for typed judgments. Give it a JSON state and a typed question; get a choice, score, or true/false value with probabilities and confidence. Jev does not generate prose. Your code owns the threshold, the safe side, and the action taken when an answer is malformed or uncertain.

This repository turns measured Jev behavior into small, runnable tools. The full measurement ledger lives in [`docs/LEDGER.md`](docs/LEDGER.md); source receipts and preregistrations are linked there instead of being copied into this page.

## Quickstart

**Publication boundary (2026-09-30):** public GitHub `main` was observed at `b3e1cd89a5ba1e09ec318471cb325481590231f4` by a fresh `git ls-remote` check. The P9 keyless acceptance recorded in `EVAL.md` §jev-p9 ran against that public SHA: 14 README command rows (12 exit 0; doctor and real no-key Choice exit 2/`NOT_RUN`). At this observation, the corrected local README/LEDGER had not been published; a public same-HEAD readback of those revisions is required for P9 closure. This is offline keyless CLI acceptance, not a live Jev answer, omp activation, or a complete P1 installer/gate handoff. Check `git remote get-url origin` and `git rev-parse HEAD` in your clone; a different public HEAD needs its own same-revision readback. `git cat-file -e` proves object presence, not public-branch inclusion.

From a fresh public clone:

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
git remote get-url origin
git rev-parse HEAD
npm ci --prefix kit
npx --prefix kit --no-install jev doctor --robot
# Expected without a key: NOT_RUN and exit 2.
npx --prefix kit --no-install jev ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot
npx --prefix kit --no-install jev verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot
npx --prefix kit --no-install jev score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot
npx --prefix kit --no-install jev classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot
npx --prefix kit --no-install jev gate --command "npm publish --access public" --fake --robot
```

### Install Jev into omp

From this checkout, install the project-scoped omp tools into a disposable git repo. The command is keyless and exits 0:

```bash
python3 -c 'from pathlib import Path; Path("var/agent-tmp/jev-omp-demo").mkdir(parents=True, exist_ok=True)' && git init -q var/agent-tmp/jev-omp-demo && npx --prefix kit --no-install jev omp install --dir var/agent-tmp/jev-omp-demo --robot
```

Expected JSON has `status: READY` for copied files, `extensionActivation: MANUAL_REQUIRED`, and `repo` set to the disposable directory. The installer refuses unmanaged or edited tool collisions and records hashes in `.omp/jev-kit-manifest.json`. It never writes `.omp/config.yml`: omp replaces extension arrays rather than merging them, so a generated list could silently remove existing host safety extensions. An installation managed by an older kit that wrote config requires owner review before upgrading.

The install copies six callable tools, one post-hook, five extension files, and shared kit helpers. It does not prove any extension loaded or fired; enable only reviewed paths by merging them into the target's existing omp config without dropping host extensions.

| Installed tool | Measured basis / receipt | Limit to keep in mind |
|---|---|---|
| `jev_rerank` | BEIR FiQA + NFCorpus receipts: `work/rerank-scifact/receipt-fiqa-mkex.json`, `work/rerank-scifact/receipt-nfcorpus-v2.json` | This is top-1 selection over 2-20 passages, not a full ranking or arbitrary passage count. |
| `jev_claim_check` | Kit verify Noul receipts: SciFact `docs/demos/upstream-repro/noul-scifact-20260924.md`; Climate-FEVER `work/jev-oioo/final-receipt.json` | Uses strict `noul > 0.5`; measured SciFact accuracy 90.2% and Climate-FEVER 65.3% (weak case). Numeric claims are outside measured scope. |
| `jev_classify` | Banking77 measurement: `docs/demos/upstream-repro/choice-banking77-20260924.md` | The 80.1% result is the measured Banking77 corpus, not a general classification guarantee. |
| `jev_gate` | Held-out gate receipt: `work/jev-1lim/final-receipt.json` | Reported rates are stratified sample rates; the receipt contains 47 harm rows, not fleet-wide prevalence. |
| `jev_flag` | Coding-agent seat: `work/jev-a9fv/receipt.json` + markerless replication `work/jev-29s4/receipt.json` | 5/300 false flags on real tool results; 268/300 markerless planted injections caught (Wilson lower 0.853); replication closed. |
| `jev_screen` | Coding-agent seat: `work/jev-a9fv/receipt.json` + markerless replication `work/jev-29s4/receipt.json` | Same coding-agent seat and privacy boundary; 5/300 clean false flags, 268/300 markerless catch (Wilson lower 0.853); replication closed. |
Only use the disposable target shown above until the project's owner has reviewed its extension list and provider-bound input policy. Copying files into another repo does not grant permission to send its commands or results to Jev.

`jev omp install` is an installer, not a model call. The tools return keyless `NOT_RUN`/safe results when no TypeSafe key is available.

The example state and Choice question are captured from committed rows: `work/pokeagent-emerald/segment2-request-states.jsonl:1` and `work/pokeagent-emerald/macro_choice.py:73-89`. The fake command uses no network.
The gate example is a captured public command (`work/jev-yru2-public/commands.jsonl` plus its committed `live-gate-question-retest-20260926.jsonl` answer); `jev gate --fake` uses that fixture offline and returns the frozen RISK decision. The fleet confirmations used the same design: sample rates, not fleet rates, with 47 harm rows in the held-out weighted population.
The fake command returns `lost_or_stolen_card` (confidence 0.86) for the captured row, while that source row's true label is `card_arrival`; this example shows the tool output, not a guaranteed-correct answer. The measured Banking77 result is 2,467/3,080 (80.1%), not 100%.


The stranger-runnable top-1 rerank verb uses one Choice over all candidate passages and refuses more than 20 or OVER/NEAR states:

`node kit/bin/jev.mjs rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot`
For a live call, set `TYPESAFE_API_KEY` outside the repository using the official [TypeSafe quickstart](https://docs.typesafe.ai/introduction/quickstart), then run the same pinned Choice command without `--fake`. Without a key, doctor reports `NOT_RUN` and the live command refuses locally (exit 2); a configured key alone is not proof of API authorization:

```bash
if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install jev ask choice --state kit/examples/state.json --question kit/examples/question.json --robot || { rc=$?; exit "$rc"; }
```

The pinned model is `jev-1.13.0`.

The separate live smoke in [`work/kit-live-receipt-20260927.json`](work/kit-live-receipt-20260927.json) records **four calls** (`classify`, `rerank`, `verify`, `score`) to `jev-1.13.0` on 2026-09-27, with 3,472 input tokens and an estimated $0.000145824 input charge. This is an existing one-call-per-verb smoke, not a result reproduced by the offline commands above; the fake answer is not a live answer. No claim about real omp extension loading, organic benefit, or accuracy follows from copying files or from those four calls.

At the 2026-09-30 04:20 UTC snapshot, the corrected local stage-15 gate passed (431/431 enforced), while the ordinary foundation aggregate remained **RED at stage 80** (consumer-check 11/12 and a selftest referencing a missing pre-commit hook); the aggregate `--selftest` passed at 04:41 UTC. A later stage-15 claim-coverage RED (115/119, then 116/118 against the then-unchanged 119/120 floor) was repaired in `2ae763c6`: its targeted gate passed 432 claims with 0 failed, 3 skipped, and coverage 121/122. After source-backed claim additions, the coverage floor was strengthened again; the 2026-09-30 targeted run recorded in `EVAL.md` §jev-p9 passed 432 claims with 0 failed, 3 skipped, coverage 123/124, and the stage's planted-negative `--selftest` passed. A later floor sync to 124/124 with its claims.tsv rows keeps the targeted gate at 433 passed, 0 failed.

## What Jev answers

| Decision shape | Return | Typical code use |
|---|---|---|
| Choice | one label plus probabilities | route, classify, select a tool |
| Score | rubric level plus probabilities | rank, filter, prioritize |
| Noul | a value in `[0, 1]` | verify a claim, flag a risk |

Every request is validated before code acts: the answer must name an offered option, probabilities must be finite and normalized, and low confidence must take the preregistered safe path.

## Measured results

The table summarizes measured results, including a failed NFCorpus joint bar, whose receipts and bars are in [`docs/LEDGER.md`](docs/LEDGER.md). Values are not claims about an unpinned `jev-latest`; they are tied to `jev-1.13.0`, the named corpus, and the cited receipt.

<!-- BEGIN GENERATED: measured-wins -->
| Surface | Result | Shape | Evidence |
|---|---|---|---|
| Banking77 intent classification | Jev 2467/3080 (80.1%) vs Haiku 2267/3080 (73.6%) | Choice | `work/choice-banking77/score.py --set full-prompted` |
| SST-5 sentiment scoring | Jev 273/500, MAE 0.488 vs Haiku 251/500, MAE 0.556 | Score | `work/score-sst5/score.py` |
| SciFact claim verification | Jev 361/400 (90.2%, Brier 0.0709) vs Haiku 351/400 (87.8%, Brier 0.1002) | Noul | `work/noul-scifact/score.py` |
| Replicated web-screen | Jev+local 68/78 own attacks; 135/256 deepset; Hermes own 15/40 fresh S-Labs; 0/1,437 clean withheld; pinned jev-1.13.0 | Noul / web-screen | `work/hermes-webscreen-repro/RECEIPT.md; work/omp-hermes-screen/hermes-own-live-receipt-20260926.json; kerpopule/hermes-jev-skills@cf9e84c` |
| MiniWoB v3 held-out | v3 342/625 vs v1 321/625 (McNemar p=0.02203; spend $0.458563) | Computer-use | `work/miniwob-jev/live-20260925/receipt.json` |
| BEIR NFCorpus rerank | Jev top-1 70.9% vs BM25 58.1% (McNemar 45 vs 15, p=0.00013); free LLM 66.7% vs Jev 70.9% (McNemar 18 vs 28, p=0.184); nDCG free LLM 0.434 vs Jev 0.448; joint bar FAIL: top-1 +0.128 met +0.10, nDCG@10 +0.027 missed +0.05; free LLM p50 25.9s, $0 by unchanged usage; Jev eligible run $0.0882 ($0.3354 including discarded run); 15+1 free LLM retries disclosed | Choice rerank / free incumbent | `work/rerank-scifact/receipt-nfcorpus-v2.json; work/rerank-scifact/receipt-jev-97bq.json` |
| BEIR FiQA rerank confirmation | Jev top-1 76.2% vs BM25 39.3% (McNemar 129 vs 10, p=1.65e-27); nDCG@10 delta +0.157; confirmatory top-1 bar passed; $0.119 | Choice rerank | `work/rerank-scifact/receipt-fiqa-mkex.json` |
| OMP judge usage | 2026-09-25 local session-file census (files modified in prior 24 h): 1,711 calls, $0.3547; find 1,595, auto-thinking 113, judge_batch 2, judge 1; not a current daily rate | OMP judge usage | `EVAL.md@b74704c9` |
| Jev gate question (blind fleet sample) | Jev catch 90/93 vs existing 92/93; precision 90/230 (39.1%) vs 92/359 (25.6%); harmless flagged 140/465 vs 267/465; McNemar b=128 c=1 p=3.82e-37; stratified sample rates, not fleet rates; jev-1.13.0 $0.018826; 52 pre-bar calls disclosed ($0.001774) | Noul / gate | `work/jev-uncd/final-receipt.json` |
| Coding-agent tool-result injection seat | Clean real tool results falsely flagged 5/300 (Wilson 0.7%-3.8%); markerless planted injections caught 268/300 (Wilson 85.3%-92.3%; marked version 269/300); jev-1.13.0 $0.029779; Jev only, no LLM comparator; one public attack corpus planted at three fixed positions; replaces the news-persona seat's 175/300 false flags | Noul / coding-agent tool-result injection | `work/jev-a9fv/receipt.json; work/jev-29s4/receipt.json` |
| Jev held-out fleet confirmation | Jev caught 47/47 vs 47/47; sample precision 47/57 (82.5%) vs 47/196 (24.0%); weighted precision 67.3% vs 24.0%; weighted harmless flagged 1.4% vs 9.1%; McNemar b=141 c=2 p=1.8e-39; strata 196/1,488; 47 harm rows only (Wilson lower 0.924, reported not gated); jev-1.13.0 $0.0134 | Noul / gate | `work/jev-1lim/final-receipt.json` |
<!-- END GENERATED: measured-wins -->

The two gate rows compare Jev with an earlier **Jev-derived** flag, not a joined deterministic incumbent. `work/jev-1miz/final-receipt.json` records `dcg_joined_rows=0` and `NOT_COMPARABLE`; 67.3% versus 24.0% is a stratified within-Jev comparison, not an organic or deterministic-baseline win.

A 2026-09-25 local census found 1,711 native omp Jev calls in session files modified in the prior 24 hours. It does not establish today's rate or the outcomes of those decisions.

## Where it runs

- `work/jev-client/`: the current official-SDK client and policy surface.
- `foundation/`: keyless calibration and gate receipts.
- `demos/`: one-command examples using recorded answers first.
- `.omp/`: the integration seams: tools, hooks, and observation surfaces.

## Jev in omp — what is ON

Native judge (`modelRoles.judge`, key command-resolved via `work/jev-client/bin/typesafe-key.mjs`) runs in five profiles (default, claude, codex, muse, grok): passage ranking on `find`, per-prompt effort from auto-thinking, promise-and-stop detection from smart stop. Proven live both ways over RPC 2026-09-30 (EVAL.md smart-stop/autothink rows); organic 2026-10-01 02:10–04:50Z: 514 find, 85 auto-thinking, 76 unexpected-stop calls (EVAL.md §2026-10-01).

`find` WORKS: 576 vs 5,293 tokens spent per located file against grep (jev-04q2 verified, 141/222 located vs 875/2627).

Injection screens act on Jev-only scores: flagged tool results are annotated in the transcript and never withheld (annotate-only default since jev-fpkw, where withholding cut success to 4/24 with zero follows; jev-rud1: clean 0/222, catch 268/300); flagged web results are withheld only for external content (scope 2b41517e). Local patterns log, never act. Both run through one composable handler that captures bytes once and scores both concurrently (jev-n4eu: 600/600 byte-identical equivalence, catch 269/300 at incumbent, no double fire). Machine-wide, the same handler annotates flagged results in every repo while the web side stays in shadow (j0er annotate flip).

Gate cascade WORKS: local nimble screens every command, paid Jev confirms only nimble-flagged ones (96% screened free in 1h live, fallback to paid on gateway failure, runtime `cascade-off` switch file, jev-nr3c). Deterministic destructive pre-rule routes straight to paid (jev-nbbm: 10/10 planted paid, 1.86 extra paid/day); the pre-rule also covers find -delete, find -exec rm, and every rm (2596d25c, 89b23139). Every row carries one screen class with zero timeout-taken-clears in 7d (jev-t3tk). Nimble-cleared commands audit 0/950 harmful (jev-syje). Bash-risk shadow itself is NO-SIGNAL (jev-qunw 0/403, jev-3m65 replication 0/148 flagged truly harmful).

Memory filter ENFORCES: concurrent 4-wide judging at session start (jev-11qz: wall 1308ms, -60% vs 3.3s serial, 20/20 in budget, byte-exact prune); keep precision 0.22 (jev-m959, saving unchanged); median 797 tokens removed per turn.
To replay available memory-filter traffic (up to 30 days) without model calls or writes: `python3 work/jev-jzgm/replay.py --days 30 --memory-cap 3 --policy cap3`. Gate reporting counts actual `jevSkipped` booleans in the last completed UTC hour; use `--gate-from` and `--gate-to` together for a custom interval. No score threshold is fitted or applied. `INSUFFICIENT_COVERAGE` means source event timestamps do not span the requested bounds; a spanning event range does not prove continuous logging. The report includes cap3 reference and gate-share checks, observed-only latency, and explicit no-op deltas; it cannot infer missing log days, unobserved harm labels, or latency for paths that did not run.

Skill veto stays shadow-only: loads are scored and logged, never blocked (jev-wbel: 0.990 demo precision falls to 0.335 on real loads at a 79% veto rate). Vendor-paste post-commit shadow logs would-flag hunks on every commit (jev-30hi: 0.842 precision, 0.640 recall); enforcement waits on a blind 0.90/0.10 bar.

Per-prompt skill hints PARKED (R133 VEIN-EXHAUSTED): every recall gain came with misroutes; silence was strictly safer. Extension stays OFF. The semantic retry is refuted too (jev-zbb1, R135: best recall 4/20 below the 8/20 gate). Web-search rerank stays OFF (jev-ib1h: 0 opens in 15 answered).

Local models LOSE-TO-JEV except nimble as cascade first pass (jev-uhc5: gate/injection worse, p95 1.2–2.7 s).

TTSR judged rules: rules below 0.80 precision retired (R132 `jev-key-canonical-source`); `claim-without-evidence` retired earlier (R130, precision 0.571).

Fleet watcher (`scripts/fleet-idle-watch.py`): an idle worker waiting on a human pages pane 1 with the 140-char excerpt (jev-7aj1 verified: recall 10/10, 0/10 false pages). Enrichment beyond the excerpt is deleted (jev-zljn, R136: n=1, fragile).

## Read next

- [`docs/LEDGER.md`](docs/LEDGER.md): complete measurements, boundaries, and receipts.
- [`docs-mirror/typesafe/introduction/quickstart.md`](docs-mirror/typesafe/introduction/quickstart.md): official request shape.
- [`docs-mirror/typesafe/primitives.md`](docs-mirror/typesafe/primitives.md): Choice, Score, and Noul.
- [`EVAL.md`](EVAL.md): verification ledger with lane, N, model, and boundary.

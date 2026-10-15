# X7 gate rules: historical descriptive receipt

**Status: DESCRIPTIVE ONLY — no gate-quality pass or enforcement recommendation.** The earlier paired sample shows DCG + the destructive pre-rule is not a substitute for recorded Jev on these command views. This continuation corrected the sampling-provenance check and recomputed the deterministic bound from already recorded rows; it does not change historical labels or Jev answers.

## Historical paired result

| Arm | Harm caught | No-harm false alarms | Weighted false-alarm rate |
|---|---:|---:|---:|
| Jev 1.13.0, recorded | 47/47 | 10/349 | 1.40% |
| DCG 0.15.2 | 7/47 | 75/349 | 14.81% |
| Destructive pre-rule alone | 0/47 | 0/349 | 0.00% |
| DCG + pre-rule | 7/47 | 75/349 | 14.81% |
| Jev, audited NP cut (>0.79) | 14/47 | 0/349 | 0.00% |
| Free model dots-studio/dots-3-note-preview:free, preregistered parked (never launched) | NOT_RUN | NOT_RUN | NOT_RUN |

Recorded Jev recall 47/47 (100%) is **recall conditional on the Jev-flagged stratum**; it is not gate-wide recall. The pre-rule matched 0/396 rows, so the combined result equals DCG. Historical clause 5 (Infisical run) catches are reported separately below; the git-push catch rate is **NOT_IDENTIFIABLE** from the committed command-free score rows; no raw command text is included here.
- Pre-approved free comparator (jev-qsa6 comments 877/1036: PREREG `work/jev-1lim/PREREG-QSA6.md`, model `dots-studio/dots-3-note-preview:free` via OpenRouter, `work/jev-qsa6/run.mjs` refuses before launch; parked, never launched): bound to the same frozen 396 gate rows and negative-rate cut when run, with the McNemar bar on no-harm false alarms (free-only vs Jev-only). Status **NOT_RUN**; no paid arm was run or inherited.

The corrected offline recomputation finds 0/200 labelled harms in the random-unflagged stratum. Its one-sided 95% Clopper–Pearson upper bound is 1.487% for that label-defined stratum; multiplying by the frozen 1,488-row frame gives at most 22.1 estimated missed harms and a weighted recall lower bound of approximately 0.68. The rows and labels are unchanged; the calculation uses the corrected sampling-time provenance join. The labels came from two local LLM labelers and are not independently human-verified; therefore the interval is conditional on those labels and does not establish human-grounded recall.

The 200 random-unflagged rows are selected by the manifest's sampling-time `existing_flag=false`, not by their later Jev rescore. Two rows rescore to `jevFlag=true` (both labelled no-harm); row 79 has `max_score=0.52`, just above the 0.5 cut. This is a sampling-time/rescore disagreement, not a stratum violation. Every labelled harm in the random-unflagged stratum remains counted as a possible miss in the Clopper–Pearson bound; rescore flags on that stratum are reported separately.

## Provenance and limits

- Frozen rows: `row-scores.jsonl` (396 rows, 47 `harm:*`, 349 `no-harm`); recorded Jev answers: `kit/fixtures/gate/answers-jev.jsonl`; deterministic outputs: `kit/fixtures/gate/answers-dcg.jsonl`. `kit/contracts/gate.json` records the question, privacy allowlist, safe side, label source, bars, and call budget.
- The historical Jev call used the bounded command view (at most 200 characters). Its SHA-256 matched the original recorded command on 100/396 rows and differed on 296/396; the full suffix is unavailable. This is a paired comparison on the recorded projection only, not the full original command.
- Historical Jev usage: 318,056 input tokens; prior-run spend estimated at $0.01336 at $0.042/M input tokens. On 2026-10-06, an inadvertent native `find` attempted 17 judge/rerank requests; all returned HTTP 402 for no credits, with 0 tokens and $0.00 spend. No successful model response or new Jev/free-model experiment result was received.
- `unflagged-PREREG.md` was originally frozen at `6c6f6b31`; this commit amends it with the sandbox-replay protocol, blind local Gemma/Qwen/Tev panel, five-clause rubric, and source-tagged label reporting. No independent non-author human labeller exists: the human assay is UNAVAILABLE (retired scope per AM56022/J-2026-10-15-06), so no fresh human assay will run. The replay/panel runs remain **NOT_RUN**; the existing 400-request, zero-retry, HTTP 401/402/403 stop, and $0.05 spend limits remain unchanged. No paid comparator.
- Do not use the historical 47/47 conditional result as an unconditional gate recall claim. Do not broaden the claim beyond the recorded command projection or the existing label provenance.

## Verification boundary

Offline evidence: `uv run --no-project --offline --python 3.12 -m unittest work.x7-gate-rules.test_np_cut -v` passed 14/14; `np_cut.py --json` returned `AUDITED` (fit 175, audit 174, FAR 0, one-sided upper 0.01707); `recall_bound.py --json` returned 47/47 conditional flagged-stratum harm catches, 0/200 random-unflagged labelled harms, upper 0.014867, and weighted-recall lower bound 0.679956. The recorded rows show Jev clause 5 37/37 and deterministic clause 5 5/37; git-push remains `NOT_IDENTIFIABLE`. These are historical, label-dependent results, not a new label set or gate-quality pass. No successful Jev/free-model experiment call was made.

## Audited cutoff is not the historical decision

The disjoint negatives-only fit uses recorded Jev `max_score`, not the binary DCG decision. The fit half contains 175 negatives and the audit half 174; both exceed the frozen minimum of 149 at alpha 0.02 and delta 0.05. The fitted cutoff is **0.79**, applied with strict `>`: the audit has 0/174 false alarms and a one-sided 95% upper rate of 0.01706949. This certifies an **unweighted** audit rate only; the weighted false-alarm figures above remain descriptive.

At this audited cutoff, the recorded arm catches **14/47** harms in the Jev-flagged stratum and its weighted recall lower bound is **0.20253998**, not the historical 0.5-arm bound. No harm row is silently dropped as unscored. The historical 0.5 arm has 10/349 unweighted false alarms (2.87%), so it fails the alpha 0.02 unweighted bar despite its lower descriptive weighted false-alarm rate. Neither arm earns a gate-quality PASS from these label-dependent data.

The pre-approved free arm, `dots-studio/dots-3-note-preview:free` under `work/jev-1lim/PREREG-QSA6.md`, remains **NOT_RUN** on the same frozen gate rows and negative-rate comparison; there are no recorded free-arm answers to score or inherit. The DCG-stratified human-labelled assay is UNAVAILABLE (retired per AM56022) under `unflagged-PREREG.md`; its old labels are not relabelled as prospective or human-grounded evidence.

## Executable recorded-answer consistency

`uv run --no-project --no-config python3 work/x7-gate-rules/recall_bound.py --json` now recomputes historical arm counts and weighted false-alarm rates from the exact joined recorded answers, then checks the canonical receipt table before emitting its descriptive report. Counts must match exactly; rate differences over 0.005 absolute, non-finite rates, missing arms and duplicate arms are refused. The original conditional-recall claim guard remains in force.

`uv run --no-project --no-config python3 -m unittest work/x7-gate-rules/test_np_cut.py -v` covers the matching recorded receipt and planted changed harm counts, altered weighted false-alarm rates, missing recorded arms and non-finite rates, alongside the existing harm-exclusion, disjoint-audit, insufficient-sample and threshold controls. These are offline consistency checks, not new model or deployment evidence. The gate family stays EXPLORED; the independent-human assay prerequisite is retired as UNAVAILABLE per AM56022, and shipping acceptance is separately required.

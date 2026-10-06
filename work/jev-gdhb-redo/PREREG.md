SPEC_SHA256: 5ec621e64ca404f372619361da1044c7bd440c234d4570cb0b77fd045a32e3f9

# MASSIVE en-US local Clef-Flash intent measurement

## Registration

- Frozen: 2026-10-06T18:26:22Z, after pinning the local-only protocol and before any Clef classification request.
- Study: one descriptive Clef-Flash-only measurement on the frozen MASSIVE corpus. This supersedes the earlier Jev/free paired-comparison plan; no prior Jev or free-model result is reused.
- Jev arm: `NOT_RUN`. No Jev model request, free-model request, or paid comparator is authorized by this preregistration.
- Decision: run at most one ordered pass over the complete fixed sample. No early stopping based on outcomes, label filtering, prompt edits, model substitution, retries, resume, or automatic rerun.

## Data and sample

- Source: AmazonScience MASSIVE 1.1, `en-US`, `test`; archive URL `https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz`.
- Pinned archive SHA-256: `4cba5faa11c71437928e17cb1b9b3d8b8e727e7ea363a3a9a8045e19c0491577`; member: `1.1/data/en-US.jsonl`.
- Dataset card: `https://huggingface.co/datasets/AmazonScience/massive`; dataset-builder source commit: `ff6bd8e4b27c35434e4f8f2108f32bb95a6f8740`.
- License: CC BY 4.0, as declared by the dataset card.
- Frozen corpus SHA-256: `4909490e7a8efabfc4e97eee6a58bee04ac3d634cae02224f82ffdb9b9f9d5b1`.
- Sample: all 954 frozen English utterances across 59 observed intents. Each intent contributes up to 18 rows; all eligible retained rows are included and no row is removed based on model output.
- Selection: exclude utterances matching any prior corpus after Unicode NFKC normalization, case-folding, and whitespace collapse. For each remaining observed intent, rank test rows by SHA-256 of `jev-gdhb-massive-1.1-en-US-test-cap18-v1|<source_id>` and take the first 18. Sort by `(intent, row_id)`. The corpus hash pins exact IDs, text, scenario, and labels.
- Zero-overlap sources and frozen hashes:
  - `work/choice-banking77/full.jsonl` — `60c42d092665d74e78db7b524c9c214a75215df699734388164136d34d60956e`
  - `work/choice-clinc150/full.jsonl` — `2ecf72aee4b8f49211378744beba883d1e99385ce76ebbec42be20708595f126`
  - `work/jev-gdhb/corpus.jsonl` — `d35b793a7a908d45f0b7c088fb3357557020945dcbbc52b23909b95c7047be98`
- Majority-label baseline: 18/954 = 0.0188679245. It is descriptive context only, not an inferential comparator.

## Local guarded model requests

- Model: `clef-flash` only.
- Keyless identity preflight: `GET http://127.0.0.1:11300/jev/clef-flash/`; continue only if the identity response contains model id `clef-flash`. This discovery GET is not an inference request.
- Classification endpoint: `POST http://127.0.0.1:11300/jev/clef-flash/classify` through localbench. The gateway routes the request to Clef's System One endpoint as profile `jev`, feature `jev-classify`; do not call Clef directly on port 8010 or substitute another host or port.
- Require the `X-Localbench-Request-Id` response header on every classification response. Record it per row; missing header, redirect, gateway refusal, HTTP error, malformed answer object, or transport failure stops the pass. The gateway's guard is not bypassed.
- Each row is sent verbatim as `state.customer_message`, with one Choice question named `intent`, instructions `Which intent best matches this spoken voice-assistant request?`, and all 59 frozen labels. Each `criteria` description is the corresponding frozen label with underscores replaced by spaces; option keys remain the exact labels used by the gold data.
- Execution: one synchronous request at a time (concurrency 1); one attempt per row (retries 0); cap 954 requests total. No fallback or resume. The client bypasses proxy environment settings, refuses redirects, and sends only to the pinned loopback URL.
- Cost: $0.00 for the local Clef experiment. No external model API or credential is used. Jev requests: 0; Jev spend: $0.00; free-comparator requests: 0.
- No model-inference POST is made during corpus checks, preregistration, keyless preflight, or selftest. The keyless preflight performs only the loopback identity GET. Commit and push the frozen preregistration, runner, test, and corpus before the first classification POST.
- Execution interpreter: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python` (observed Python 3.14.2).

## Outcomes and reporting

- Primary metric: exact-match accuracy over the complete 954-row corpus. Invalid answers count wrong when invalid answers are at most 5%; if the invalid rate is greater than 5%, report `NOT_SCORED`.
- Validate the response model id is exactly `clef-flash`; choice is one of the offered labels; probability keys exactly match those labels; probabilities are finite and in [0,1] and sum to 1 within 0.02; the selected choice has maximum probability; supplied confidence is finite and in [0,1].
- Any request error or missing answer stops the pass. Report `INCOMPLETE_NO_VERDICT` if any result row was recorded, otherwise `NOT_RUN`; never score only completed rows. A complete pass with more than 5% invalid answers is `NOT_SCORED`; otherwise report `CLEF_ONLY_MEASURED`.
- No McNemar test, Jev comparison, significance claim, win/loss label, deployment recommendation, or broad model-quality claim. The majority baseline is descriptive only.
- `rows.jsonl` records one result per attempted row: row id, gold label, choice/status, validated probabilities when valid, latency, model id, localbench request id, attempt count, prereg/corpus/runner hashes, and error class without utterance text or response-body dumps. `RECEIPT.md` records counts, accuracy, invalid rate, hashes, and the Jev `NOT_RUN` boundary.

## Immutable run artifacts

`run.py` binds this file's SHA-256, the corpus SHA-256, and the canonical spec SHA-256 before it can make a classification POST. The run is authorized only after keyless preflight passes and the preregistration, runner, tests, and frozen corpus are committed and pushed. Any change to data, model id, endpoint, prompt, validation, score rule, sample, or request cap requires a new pre-inference preregistration.

Preflight: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/jev-gdhb-redo/run.py --preflight --json`
Offline selftest: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/jev-gdhb-redo/run.py --selftest --json`
Single local pass: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/jev-gdhb-redo/run.py --run-clef --json`

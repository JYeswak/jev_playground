# `--backend jev|clef|auto` seam for the kit client: spec

Status: design only. Nothing under /Users/josh/Developer/jev was edited.
Liveness probe, run once on 2026-10-03: `curl -s -m 3 http://127.0.0.1:8010/` returned `{"models": [{"id": "clef-flash"}]}`, exit 0. GET only, no POST.
Offline receipt replays, run with no network (they read committed rows only):
- `python3 work/local-decision-arms/run.py --platt clefflash` printed `a=1.353 b=0.000 dev_n=200 acc 0.9617 ece 0.0246 median_ms 4388 PASS`.
- `python3 work/local-decision-arms/vendor.py --platt clefflash` printed `a=1.239 b=2.926 dev_n=120 auc 0.83885 ece 0.0832 PASS`.
- An inline refit using the same algorithm as run.py:161-183 and vendor.py:145-168 gave full-precision values: B77 `a=1.3526520145076346 b=0.0002885751250081534`; vendored `a=1.239108052096005 b=2.9255164678194676`.

## 0. Findings that shape the design (read before the table)

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| F1 | Clef puts the **question key** into the prompt (`ID: {question_id}`). If `instructions` is empty, Clef uses the key in its place. Jev documents that the key "is not sent to the underlying model". | joint_schema_model.py:116, :120-122; docs-mirror/typesafe/api.md:36 | A calibration holds only for the key it was fitted with. The kit sends keys `choice`, `score` and `value` (client.ts:159, :161; bin/jev.mjs:81). The receipts used `intent` (run.py:36) and `vendored` (vendor.py:36). The Clef transport must post the receipt's key and map the answer back. |
| F2 | Clef's system prompt tells it to "Decide every field jointly". Jev evaluates each question "in parallel" against the state. | joint_schema_model.py:24-26; docs-mirror/typesafe/models.md:20 | Under Clef, one answer depends on the other questions in the same request. Both receipts are single-question, so `auto` never sends a request with more than one question to Clef. gate's 5-Noul RISK bundle (gate.ts:62-63) stays on Jev. |
| F3 | Clef **silently truncates the state** to fit 16,384 tokens. It raises an error only when the schema alone is too long. | joint_schema_model.py:106, :165-170, :547 | Response `usage.input_tokens` is the length after truncation (joint_schema_model.py:575). Treat `input_tokens >= 16384` as truncated and refuse. |
| F4 | Clef echoes the request `model` string back as the response model. The receipts posted `"kev-latest"` and still got Clef answers. | joint_schema_model.py:573; run.py:33; vendor.py:34 | The response `model` field does not prove which weights answered. Identity has to come from a fingerprint, not from `model`. |
| F5 | The Clef server and weights are untracked throwaway files. The repo-root `.gitignore` rule `/*` covers them, and git tracks 0 files under the directory. | serve.py:1 ("Throwaway"); `git check-ignore -v` → `.gitignore:10:/*`; `git ls-files var/agent-tmp/clef-flash.conductor` → 0 | The served model cannot be reproduced from the repo. Doctor must say so, and the calibration pins weight hashes. |
| F6 | The SDK reads `TYPESAFE_BASE_URL` and sends `Authorization: Bearer <TypeSafe key>` to whatever base URL it has. | work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs:58, :513, :579-581 | Do not route Clef through the SDK, because that would send the paid key to the local server. Use plain `fetch` with no auth header. Doctor warns if `TYPESAFE_BASE_URL` is set. |
| F7 | `confidence` means different things. Clef choice: `confidence = p(choice)`; Clef score: `confidence = max level probability`. Jev: confidence is "derived from probabilities". In a live Jev answer, confidence 0.97 came with p(choice) 0.98. | joint_schema_model.py:533, :540; api.md:264-265; client.ts:93-94; confidence.md:138 | The Platt map is fitted on `p_choice` (run.py:174). The Clef choice `confidence` is defined as `Platt(p_choice)`. It is not comparable to Jev's raw `confidence`. |
| F8 | Raw Clef Noul scores are badly calibrated on vendored code: held ECE 0.311 vs Jev 0.185 (FAIL). After Platt the ECE is 0.083 (PASS). | `vendor.py --score clefflash` printed `ece 0.31058 … FAIL`; `vendor.py --platt clefflash` printed `ece 0.0832 PASS` | An uncalibrated Clef Noul is unsafe to threshold, so refuse it. |
| F9 | Clef is about 27× slower than Jev at the median and queues behind one global lock. | Clef ms from rows-clefflash.jsonl: p50 4388, p95 5850, max 9107 (n=600); vendor-rows-clefflash.jsonl: p50 2834, p95 5421, max 6921 (n=200). Jev `latencyMs` from work/vendor-paste/vendor-rows.jsonl: p50 163, p95 400, max 1811 (n=320). Lock: serve.py:11, :22 | The kit's Jev default timeout of 4000 ms (client.ts:410, :484, :552, :613) is below Clef's p50. Clef needs its own timeout and one request in flight per process. |

## 1. Wire compatibility: Jev vs Clef

| Row | Jev (`jev-1.13.0`) | Clef (`clef-flash`) | Seam rule |
|---|---|---|---|
| Endpoint | `POST https://api.typesafe.ai/v1/systemone` (api.md:14; client.ts:65). The SDK builds `${baseURL}/v1/systemone` (sdk index.mjs:554, :579). | `POST http://127.0.0.1:8010/v1/systemone` (vendor-shadow.mjs:107). The server ignores the path on POST and on GET (serve.py:16-19). | `JEV_CLEF_URL`, default `http://127.0.0.1:8010/v1/systemone`. Refuse any host that is not loopback. Local use is justified by "no data leaving the machine" (AGENTS.md:92-93). |
| Auth | `Authorization: Bearer $TYPESAFE_API_KEY` (api.md:15; sdk index.mjs:581). A missing key returns `unconfigured` (client.ts:385-393). | None. The server never reads headers apart from Content-Length (serve.py:20). | The Clef transport sends **no** Authorization header (F6). Without a key, Clef still works: keyless. |
| Liveness / identity | No GET in the kit. Doctor checks only the key and the SDK (bin/jev.mjs:32-56). | `GET /` → `{"models":[{"id":"clef-flash"}]}` (serve.py:16-17; probe above). There is no fingerprint (serve.py:17). | Doctor uses a GET only. `auto` requires a fingerprint (§2, T0). |
| Request `model` | Required (api.md:27-28). The kit default is `jev-1.13.0` (client.ts:66); `JEV_MODEL` overrides it (client.ts:378). | Must be a string, otherwise ValueError → HTTP 500 (joint_schema_model.py:553-554; serve.py:26). The value is ignored and echoed back (F4). | Send `"clef-flash"`, as vendor-shadow does (vendor-shadow.mjs:122). |
| Request `state` | string, object, or array (api.md:23-24). | Any JSON. A non-string is rendered as sorted-key compact JSON (joint_schema_model.py:35-43). | Pass through unchanged. The receipts used `{customer_message}` (run.py:34) and `{code: ≤4000 chars}` (vendor.py:35). |
| Request question key | Not used in inference (api.md:36). | Part of the prompt (F1; joint_schema_model.py:116). | The calibration stores `question_key`. The Clef transport posts under that key and maps the answer back to the caller's key. |
| Noul request | `{type:"noul", instructions, criteria?:{true,false}}` (client.ts:400-406). | The same. Custom `criteria` merge over the default true/false texts (joint_schema_model.py:48-54). | Same body. |
| Choice request | `criteria` is a map with ≥2 entries (client.ts:473-479). At most 255 options (api.md:125). | `criteria` must not be empty (joint_schema_model.py:560-561). Options are sorted before encoding (joint_schema_model.py:56). The code has no options cap; the 16,384-token schema budget limits it (joint_schema_model.py:166-169). | Run the kit's existing ≥2 check (preflight.ts:96-107) first. A schema that is too long → Clef HTTP 500 → `http`. |
| Score request | `criteria` is a list with ≥2 entries (client.ts:546-548; sdk index.mjs:534). | Levels are the list indices (joint_schema_model.py:57). | Same body. There is no Clef score receipt, so `auto` never routes score. |
| Noul answer | `{type:"noul", noul}` = probability that the answer is yes (api.md:213-214; noul.md:240). Validated in [0,1] (validate.ts:41-44). | `{type:"noul", noul: round(softmax p(true), 4)}` (joint_schema_model.py:525-526). | Validate first, then Platt-map with the task's map (vendor-shadow.mjs:111-114). With no map, refuse (§2). |
| Choice answer | `{type, choice, probabilities (sum 1), confidence}` (api.md:250-276). Validation: keys equal the offered labels, sum within 1 ± 0.02, choice is the argmax (validate.ts:24-39, :52-65). | `choice = argmax`, `confidence = p(choice)`, probabilities rounded to 4 dp (joint_schema_model.py:527-535). | Reuse `validateChoiceAnswer` unchanged. Output `confidence = Platt(p_choice)`. Keep `probabilities` raw and label them `probabilitiesRaw: true` (F7). |
| Score answer | `{type, score, legend, probabilities, confidence}`; score is the probability-weighted mean (api.md:310-319; score.md:732). | `score = Σ i·p_i`, `confidence = max p`, plus legend and probabilities (joint_schema_model.py:536-543). | Reuse `validateScoreAnswer` (validate.ts:74-90). Refused today because there is no calibration. |
| `usage` | `input_tokens`, `output_tokens` (api.md:198-206). `readUsage` never invents values (client.ts:359-375). | `input_tokens = len(encoded ids)` after truncation; `output_tokens = 0` (joint_schema_model.py:575). | Same parser. Add the truncation check (F3). |
| Response `model` | "The model that performed the evaluation" (api.md:184-185). Read as `resolvedModel` (client.ts:348-349). | Echo of the request (joint_schema_model.py:573). | Report `model: "clef-flash+platt:<task_id>.v<N>"`. Never echo the response `model`. |
| Probability semantics | Trained "to return calibrated decisions" (models.md:44). Recorded calibration: B77 ECE 0.1017, vendored ECE 0.185 (run.py:194; vendor.py:184). | Raw B77 ECE 0.054 (PASS) and raw vendored ECE 0.311 (FAIL), from the `--score` runs above. After Platt: 0.0246 and 0.0832 (`--platt` runs). | Calibration is per task. A map is never applied outside its `question_sha256`. |
| Size limit | 64k tokens per request; 32k for state plus the longest question (models.md:15). The kit preflights at 32,768 tokens using a byte band (preflight.ts:1-5, :40-51). | 16,384 tokens in total, including the system prompt, schema and all questions. The state is truncated silently (F3; joint_schema_model.py:150-170). | Preflight with `sizePreflight(..., {limitTokens: 16384})` (preflight.ts:79-85). The byte band was fitted to Jev's tokenizer; for Clef's tokenizer it is UNVERIFIED, so the post-call `input_tokens` check is the authority. |
| Latency | p50 163 ms, p95 400 ms (n=320, vendor-rows.jsonl). Kit timeout 4000 ms (client.ts:410). | p50 4388 / p95 5850 / max 9107 ms on B77 with 77 options; p50 2834 / p95 5421 ms on vendored code (F9). vendor-shadow times out at 10,000 ms (vendor-shadow.mjs:109). | `JEV_CLEF_TIMEOUT_MS` default 10000, separate from Jev's. |
| Concurrency | 1,200 req/min and 250k tok/s; 429/529 → back off (models.md:14, :19; api.md:333-338). The SDK owns retries; the kit default is 0 retries (client.ts:311-321). | One `threading.Lock` around every inference (serve.py:11, :22). `ThreadingHTTPServer` queues the rest (serve.py:5, :40). | At most 1 Clef request in flight per process (semaphore). 0 retries. Circuit hold described in §3. |
| Error shape | 401/422/429/529 come back as SDK `APIError` → `http`; 401/402/403 start a 15-minute hold (client.ts:237-242, :326-329; api.md:331-334). | Any exception inside `systemone` → HTTP 500 `{error, detail}` (serve.py:21-26). Bad JSON or a missing Content-Length raises outside the `try` (serve.py:20), so the client sees the connection drop. | 500 → `http`; connection drop or abort → `transport`. No billing hold for Clef. |

## 2. Per-task Platt maps: where they live, how they are versioned, how refusal works

**Location.** `kit/calibration/clef/<task_id>.v<N>.json`. There is one file per task, and only the current version is kept; git history holds the old ones. The `files` list in kit/package.json:11-20 must gain `"calibration"` so the maps ship with the npm package.

**Schema `jev.clef-calibration.v1`** (values for the two receipts that exist today):

| Field | banking77-intent.v1 | vendored-code.v1 |
|---|---|---|
| `primitive` | `choice` | `noul` |
| `question_key` | `intent` (run.py:36) | `vendored` (vendor.py:36) |
| `question_sha256` | sha256 of canonical JSON `{type, instructions, criteria}` (sorted keys, the 77 humanized labels → null; run.py:16, :28, :37-40) plus `state_keys:["customer_message"]` | Same construction over `{type:"noul", instructions:Q}` (vendor.py:19-22) plus `state_keys:["code"]` |
| `model.id` | `clef-flash` (serve.py:17) | `clef-flash` |
| `model.joint_head_sha256` | `19cdcec8…f5ba0` (shasum of model/joint_head.safetensors) | same |
| `model.index_sha256` | `941305ff…a96c` (shasum of model/model.safetensors.index.json) | same |
| `map` | `{kind:"platt-logit", target:"p_choice", a:1.3526520145076346, b:0.0002885751250081534, clip:1e-4}` | `{kind:"platt-logit", target:"noul", a:1.239108052096005, b:2.9255164678194676, clip:1e-4}` |
| `fit` | dev rows `rows-clefflash-dev.jsonl` sha256 `6eed954a…1099`, n=200, 2000 steps, lr 0.1, init (1,0) (BAR-b77-platt.md:6-9) | dev rows `vendor-rows-clefflash-dev.jsonl` sha256 `d7cd0339…c0ab`, n=120 (BAR-vendor-platt.md:5-10) |
| `receipt.prereg_commit` / `result_commit` | `ca787540` / `8b1bb513` | `0c1cba40` / `478698ce` |
| `receipt.held` | `rows-clefflash.jsonl` sha256 `850fc6f6…becb`, n=600: acc 0.9617, ECE 0.0246 vs jev-1.13.0 0.7867 / 0.1017 → PASS (BAR-b77-platt.md:11-12) | `vendor-rows-clefflash.jsonl` sha256 `6dab0552…a54c0ab`, n=200: AUC 0.839, ECE 0.083 vs jev 0.827 / 0.185 → PASS (BAR-vendor-platt.md:8-9) |
| `receipt.command` | `python3 work/local-decision-arms/run.py --platt clefflash` | `python3 work/local-decision-arms/vendor.py --platt clefflash` |

**Versioning.** Bump `v<N>` and refit whenever any of these changes: `model.*_sha256`, `question_sha256`, `question_key`, or the map. Each bump needs a new prereg commit (bar first) and a new result commit. A version without both commits never loads.

**Fail-safe direction: refuse, never pass raw.** The Clef transport gets a validated answer and then looks up a calibration whose `question_sha256` and `question_key` match the request.
- **No calibration found:** return `{ok:false, reason:"uncalibrated", error, latencyMs, model}`. The result carries **no** `noul`, `choice`, `confidence`, `score` or `probabilities`. Raw Clef numbers never leave the transport, because raw vendored ECE is 0.311 (F8).
- **`usage.input_tokens >= 16384`:** return `reason:"truncated"` (F3).
- **Map fails to load** (bad schema, non-finite a or b): return `reason:"uncalibrated"`.

Today `--backend clef` therefore answers only the B77 classify shape and the vendored Noul. Every other call is refused.

Since the B77 map is fitted on `p_choice`, the label never changes and accuracy is unchanged (BAR-b77-platt.md:10).

`JevFailure` (client.ts:114) gains `"uncalibrated" | "truncated" | "backend-hold"`.

## 3. `auto` policy

**Evidence gate.** A request routes to Clef only if **all** of the following hold:
1. A loaded calibration file has `receipt.verdict == "PASS"` against incumbent `jev-1.13.0` on held rows, under a bar committed before the dev calls (`prereg_commit` comes before `result_commit`).
2. The request's `question_sha256` and `question_key` match that file (exact match, no fuzzy matching).
3. The request has exactly 1 question (F2).
4. The server fingerprint from `GET /` (probed once per process, 3 s timeout, cached) equals `model.joint_head_sha256` and `model.index_sha256`. **Today the server returns no fingerprint (serve.py:17), so `auto` routes 0 calls to Clef until T0 lands.**
5. No `backend-hold` is active.

If any condition fails, the request goes to Jev and the result shows `backend:"jev"` and `route_reason:"<first failing clause>"`.

Receipts that qualify today: `banking77-intent.v1` and `vendored-code.v1`. **Converge r4 (2026-10-05): neither qualifies.** A receipt qualifies `auto` only if its question key belongs to a registered family's contract (`kit/contracts/<family>.json`) and its rows are that family's frozen labelled rows; Banking77 is a public benchmark with no fleet traffic and vendored-code belongs to no registered family, so `auto` routes 0 calls to Clef until a family receipt exists (jev-b35c.4). The only kit verb whose request matches is `classify`, and only when it is called with the 77 humanized Banking77 labels (classify.ts:4, :41-43 matches run.py:16, :28, :34-40 on state, instructions and criteria). `verify` (SciFact), `score` (SST5), `rerank` (FiQA/NFCorpus) and `gate` (RISK, 5 Nouls) have no Clef receipt and always go to Jev.

**Clef error or timeout under `auto`, per primitive:**

| Primitive / caller | On Clef `http`, `transport`, timeout, `truncated` or `uncalibrated` | Why |
|---|---|---|
| choice (`classify`, `rerank`) | **Fall back** to exactly 1 Jev call, but only if a key is present and no billing hold is active (client.ts:233-235). Otherwise return the Clef failure. | Jev is the incumbent with a recorded quality figure. The answer is advisory. |
| noul (`verify`, `ask noul`) | **Fall back** to 1 Jev call, same conditions. | Same reason. |
| noul inside vendor-shadow (`scoreCommit`) | **Refuse**: `local_status:"NOT_RUN"` and no extra Jev call (vendor-shadow.mjs:125-133, :167). | Jev has already been asked in the same row (vendor-shadow.mjs:157). The local verdict is a second opinion that is only logged. |
| score | Not reachable under `auto` (no receipt). Under explicit `--backend clef`: refuse `uncalibrated`. | No map. |
| bundle (`gate`, `askJevBundle`) | Not reachable under `auto` (F2, clause 3). Under explicit `--backend clef`: refuse `uncalibrated`. | No joint-bundle receipt. gate hooks stay fail-open on Jev (AGENTS.md:108). |

**Explicit modes.**
- `--backend jev`: identical to today. Default backend is `jev`; `JEV_BACKEND` sets it.
- `--backend clef`: Clef only. **Never falls back**, because the caller chose Clef. Errors are returned as they are.

**Call cap** (per logical ask): at most **1 Clef attempt and 1 Jev attempt**, so ≤2 network calls. Clef gets 0 retries.

**Process-level limits.**
- **Semaphore:** 1 Clef request in flight.
- **`backend-hold`:** after 2 consecutive Clef `transport` or timeout failures, Clef is skipped for 60 s. `auto` goes straight to Jev; `clef` returns `backend-hold`. This mirrors the billing-hold pattern (client.ts:224-242).
- **Time budget:** the worst-case `auto` call is 10,000 + 4,000 ms.

## 4. Doctor checks (`jev doctor --robot`, new `backends` block; GET only, 0 POSTs)

| Check | Pass | Degrade / fail | Exit effect |
|---|---|---|---|
| `clef.reachable` | `GET <base>/` within 3 s and `models[].id` includes `clef-flash` (serve.py:16-17) | `DOWN` | none. Jev status still decides READY (bin/jev.mjs:46, :56) |
| `clef.url_loopback` | Host is 127.0.0.1, ::1 or localhost | `REFUSED` | Clef is disabled |
| `clef.fingerprint` | GET carries a fingerprint that equals the calibration `model.*_sha256` | `UNPINNED` (today) or `MISMATCH`. Either way `auto` routes 0 calls to Clef | none |
| `clef.provenance` | Server source is tracked in git | `WARN untracked` (F5) | none |
| `calibration.files` | Every `kit/calibration/clef/*.json` parses as v1 with finite a and b | `INVALID <file>` | 1 (shipped data is broken) |
| `calibration.receipts` (repo only) | `git cat-file -e` succeeds for both commits; dev/held row sha256 values match | `UNVERIFIABLE` outside the repo; `MISMATCH` inside it | 1 on MISMATCH |
| `calibration.refit` (`--deep`, repo only) | A Node port of run.py:161-183 / vendor.py:145-168 reproduces a and b within 1e-9 | `DRIFT` | 1 |
| `routing` | Prints, for each verb, the backend `auto` would pick and the receipt id or failing clause | none | none |
| `env.typesafe_base_url` | `TYPESAFE_BASE_URL` is unset | `WARN`: the SDK would redirect Jev and send it the key (F6) | none |

## 5. Implementation tasks (in order; each test is keyless and uses an injected transport)

Global acceptance: `cd kit && node --test test/*.test.mjs` (kit/package.json:31), plus `node kit/bin/jev.mjs doctor --robot` printing a `backends` block. In these tests a fetch spy counts POSTs.

| # | Files | Failing test first | Planted negative (must fail the test) | Acceptance |
|---|---|---|---|---|
| T0 | Promote `var/agent-tmp/clef-flash.conductor/serve.py` to tracked `work/clef-serve/serve.py` and `fingerprint.py`. `GET /` adds `fingerprint:{joint_head_sha256, index_sha256}`. Weights stay where they are and are passed as argv[1] (serve.py:7). | `work/clef-serve/test_fingerprint.py`: the fingerprint of a temp dir with known bytes equals hashlib's value. The test does not load the model. | Hashing file names instead of bytes. | `python3 -m unittest work/clef-serve/test_fingerprint.py` |
| T1 | `kit/src/calibration.ts`: `loadCalibrations(dir)`, `questionSha(question, stateKeys)`, `plattMap(p, map)` | `kit/test/calibration.test.mjs`: `plattMap` with the vendored map equals vendor-shadow `plattMap` (vendor-shadow.mjs:111-114) at p ∈ {0.1, 0.5, 0.9} within 1e-3 (vendor-shadow uses the 3-dp values) | (a) A file without `result_commit` loads. (b) `a: NaN` loads. | `node --test kit/test/calibration.test.mjs` |
| T2 | `kit/calibration/clef/banking77-intent.v1.json`, `vendored-code.v1.json` (values from §2); add `"calibration"` to kit/package.json `files` | Repo-only test: `questionSha` of classify.ts's question built over the humanized labels read from work/choice-banking77/full.jsonl equals the file's value. In-package test: files load. | The snake_case label set (classify's natural input) matches the receipt's sha, which would mean the sha is not discriminating. | same, plus `npm pack --dry-run --prefix kit` lists `calibration/` |
| T3 | `kit/src/clef.ts`: `askClef({primitive, state, question, callerKey, fetchImpl, url, timeoutMs})`. Plain fetch; reuses validate.ts and readUsage; posts under `question_key`; applies the map | `kit/test/clef.test.mjs`, injected `fetchImpl`: (1) body has `model:"clef-flash"` and the receipt key; (2) no `authorization` header; (3) 500 → `http`; (4) `input_tokens:16384` → `truncated`; (5) unknown question → `uncalibrated` with no numeric answer fields; (6) noul 0.5 → `plattMap(0.5)` | (a) An implementation that forwards Authorization. (b) One that returns the raw noul when there is no map. | `node --test kit/test/clef.test.mjs` |
| T4 | `kit/src/client.ts`: `backend?: "jev"\|"clef"\|"auto"` and `clefFetchImpl` on `AskOptions`, `AskChoiceOptions`, `AskScoreOptions`, `AskBundleOptions`; router, semaphore, `backend-hold`; extend `JevFailure` | `kit/test/backend.test.mjs` with two fetch spies: default leaves the Jev body byte-identical and makes 0 Clef calls; auto + receipted → 1 Clef call, 0 Jev; auto + unreceipted → 0 Clef; auto + Clef timeout → exactly 1 Jev call (≤2 total); clef + error → 0 Jev; 2 transport failures → 3rd auto makes 0 Clef calls; 2 parallel autos → max 1 Clef in flight; auto with no fingerprint → 0 Clef | (a) Default flipped to `auto`. (b) A fallback that retries Clef. (c) An auto bundle with 5 questions sent to Clef. | `node --test kit/test/backend.test.mjs` and the existing client, wire-conformance and fake tests unchanged |
| T5 | Thread `backend` and `clefFetchImpl` through classify.ts, rerank.ts, score.ts, verify.ts and gate.ts (they already take `ask` and `fetchImpl`: classify.ts:9-11, gate.ts:48) | Per-verb test: `classifyText({backend:"auto"})` with B77 labels hits the Clef spy; `scoreText({backend:"auto"})` does not | verify routed to Clef under auto | `node --test kit/test/*.test.mjs` |
| T6 | `kit/bin/jev.mjs`: `--backend` flag and `JEV_BACKEND` on ask, classify, verify, score, rerank, gate; robot output adds `backend` and `route_reason`. `--fake --backend clef` replays `kit/test/fixtures/clef-*.json` | cli.test.mjs: `ask choice --fake --backend clef --robot` with a B77 fixture → `ok:true` and `backend:"clef"`; with the noul fixture under a non-receipted question → `uncalibrated`, exit 1 | `--backend` silently ignored | `node kit/bin/jev.mjs classify … --fake --backend auto --robot` |
| T6a | Fixtures: one live local capture each for the B77 and vendored shapes, saved with the request sha256. This needs Clef up; it is $0 and the only live step. | n/a | n/a | fixture files exist with their `request_sha256` |
| T7 | Doctor `backends` block (§4) | doctor.test (inside cli.test.mjs) with an injected GET: DOWN → Jev status unchanged; fingerprint absent → `UNPINNED` and routing shows 0 Clef | A doctor that makes any POST (the spy asserts the method is GET) | `node kit/bin/jev.mjs doctor --robot` |
| T8 | Clean cutover: `work/vendor-paste/vendor-shadow.mjs` drops `LOCAL_PLATT`, `plattMap` and the inline askLocal body (vendor-shadow.mjs:107-134) and calls the kit's `askClef` | vendor-shadow.test.mjs still passes; new case: when the kit calibration file is missing, the local verdict is `NOT_RUN`/`uncalibrated` | A second copy of the map left in vendor-shadow (checked with grep for `2.926`) | `node --test work/vendor-paste/vendor-shadow.test.mjs` |
| T9 | Docs: kit/README.md and ROBOT.md backend section; AGENTS.md "Local vs paid" gains a Clef row (AGENTS.md:92-97) | n/a | n/a | the docs state the evidence gate word for word as in §3 |

## 6. Gateway URL contract (converge r4, 2026-10-05)

Clef is reached only through localbench's gateway (localbench bead `kit-jtq2`, open on 2026-10-05).

| Field | Value | Source |
|---|---|---|
| Host | `127.0.0.1` | `~/Developer/localbench/localbench/gateway.py:35` |
| Port | `11300` (gateway.PORT) | `~/Developer/localbench/localbench/__main__.py:4101` ("default 11300") |
| Health | `GET /healthz`, 500 ms bound in doctor and overview | `~/Developer/localbench/localbench/gateway.py:133` |
| Clef route path | UNKNOWN until `kit-jtq2` closes | `kit-jtq2` acceptance |

Validation rule for `JEV_CLEF_URL` (installer T11, backend seam): accept only if the host is loopback (`127.0.0.1`, `::1`, `localhost`) **and** the port is not `8010`. `http://127.0.0.1:8010` is refused (direct Clef, bypasses attribution); `http://10.0.0.5:11300` is refused (not loopback).

## Open items (UNVERIFIED)
- Whether Clef's tokenizer matches the byte band in preflight.ts:2-5. Verify by sending one long local request and comparing `usage.input_tokens` with `estimatedTokensAtLowRatio`.
- Jev latency on the Banking77 choice shape: `rows` for jev-1.13.0 carry no `ms`, and `--score` printed `median_ms: null`. The 163 ms Jev p50 above comes from vendored Noul rows only.
- Whether `auto` should ever cover vendored-code inside the kit. No kit verb sends that question today, so the receipt is used only by vendor-shadow after T8.

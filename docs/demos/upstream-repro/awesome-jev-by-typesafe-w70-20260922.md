# awesome-jev-by-typesafe W7.0 — catalogue — 2026-09-22

Fresh run. Class: catalogue. Profile: T1 + T3 only (`docs/PLAN-DEEP-KIT-20260922.md:427-428`). No live Jev call. Old `EVAL.md:35-42` is a lead, not a pass. T4 bar already committed at `da2a785` in `docs/demos/upstream-repro/w70-t4-bar-20260922.md`; this clone is excluded there (`:18`). No new accuracy bar.

Worker/host: `Joshs-Mac-Studio.local`, Darwin arm64. No RCH worker (no Rust). Measurement clock: 2026-09-23T03:15:57Z. `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` were unset before any command. No `omp` command was run.

## Tests

| id | status | result |
|---|---|---|
| T1 | PASS | Pin `d57f5ce8002cc7cadc2c744b34a45933507e0508`, commit date `2026-09-18 01:38:24 +0530`, MIT `LICENSE:1`, clean `git status` before and after. |
| T2 | NOT-APPLICABLE | Catalogue profile is T1+T3. A suite exists (`README.md:432`, 11 `def test_` methods in `tests/test_decision_policies.py`) and was not run. Not a failed run. |
| T3 | PASS | Eight of the clone's own claims or recipes, each with file:line and a status. Five are demonstrated. |
| T4 | NOT-APPLICABLE | Committed bar excludes catalogues (`w70-t4-bar-20260922.md:18`). No live call. No accuracy bar invented. |
| T5 | NOT-APPLICABLE | Floor arms apply to seat/benchmark only (`PLAN-DEEP-KIT-20260922.md:417`). |
| T6 | NOT-APPLICABLE | Incumbent arm applies to seat/benchmark only (`PLAN-DEEP-KIT-20260922.md:418`). |
| T7 | NOT-APPLICABLE | Calibration applies to seat/benchmark only (`PLAN-DEEP-KIT-20260922.md:419`). |
| T8 | NOT-APPLICABLE | Stability applies to seat/benchmark only (`PLAN-DEEP-KIT-20260922.md:420`). |
| T9 | NOT-APPLICABLE | Fault behaviour applies to SDK/client/tool clones only (`PLAN-DEEP-KIT-20260922.md:421`). |
| T10 | PASS | Result class withheld. Tiers, NO-CLAIM, and the earned-label note are below. |

No row is NOT-RUN. The four earned-label fields (command, verbatim output, file:line, two routes) are not triggered.

## T1

Command:

```text
git -C awesome-jev-by-typesafe rev-parse HEAD
git -C awesome-jev-by-typesafe log -1 --format='%H%n%ci%n%s%n%an'
git -C awesome-jev-by-typesafe status --porcelain=v1 -b
git -C awesome-jev-by-typesafe rev-parse origin/main
```

Verbatim:

```text
d57f5ce8002cc7cadc2c744b34a45933507e0508
2026-09-18 01:38:24 +0530
Swap: remove unrelated files
Anil Chandra Naidu Matcha
## main...origin/main
d57f5ce8002cc7cadc2c744b34a45933507e0508
```

`origin/main` equals HEAD. Remote: `https://github.com/Anil-matcha/awesome-jev-by-typesafe`. Porcelain empty before the receipt write. After the write, at 2026-09-23T03:21:42Z, `git status --porcelain=v1 -b` was `## main...origin/main` and HEAD was still `d57f5ce8002cc7cadc2c744b34a45933507e0508`. Clone not edited.

License: `LICENSE:1` `MIT License`. Copyright `(c) 2026 Anil Chandra Naidu Matcha` (`LICENSE:3`). No OpenAI/Anthropic rider in the file.

Environment at the pin read: `OMP_PROFILE=<unset>`, `PI_PROFILE=<unset>`, `PI_CODING_AGENT_DIR=<unset>`. Runtimes used: `git version 2.50.1 (Apple Git-155)`, `Python 3.9.6` (policy execution), `node v22.22.0` (present, not used). No omp version, because omp was not invoked.

## T3

Status words: demonstrated = executed or inspected at this pin and it holds; partial = part holds and part was not shown; aspirational = stated, not shown. Evidence level, named so a number is not mistaken for a test: claims 1, 5, and 6 are file inspection (N=1 tree, date 2026-09-23, no model). Claims 3 and 4 are a local Python execution of pure functions (N=12 calls, Python 3.9.6, no model, no API). Claim 2 is source inspection of workspace SDK pins, not this catalogue's pin. Claims 7 and 8 are external page reads (N=2 pages, 2026-09-23, no model call). Live Jev N=0. RULEBOOK tiers from `notes/deep/jev-assessment.md:7`: [Verified] inspected here; [External] public page; [Inference] judgment.

| # | claim or recipe | status | decides it | tier |
|---|---|---|---|---|
| 1 | Independent community collection, not an official TypeSafe repo (`README.md:25`) | demonstrated | Remote is `Anil-matcha/awesome-jev-by-typesafe`, not `typesafe-ai`. `LICENSE:3` names Anil Chandra Naidu Matcha. | [Verified, High] |
| 2 | Official Python SDK reads `TYPESAFE_API_KEY` and defaults to `jev-latest` (`README.md:81`). Quickstart constructs `TypeSafeClient()` with no model (`examples/python/quickstart.py:16`). | demonstrated against the workspace SDK, not a SHA this catalogue pins | Workspace `upstream/typesafe-ai/typesafe-sdk-python` at `0ffd094c72ed9445223060b24ffd7a56aa781fb4` (v0.7.1, 2026-09-21, after this catalogue's 2026-09-18 commit). `constants.py:3` `API_KEY_ENV = "TYPESAFE_API_KEY"`. `constants.py:18` `DEFAULT_MODEL = "jev-latest"`. `config.py:62` applies that default. JS SDK at `66880ccded6cb642dc1809620c2b108c33730214` (v0.6.0, 2026-09-15) agrees: `src/env.ts:4`, `src/client.ts:42`. Catalogue pins neither SDK SHA. | [Verified, Medium] |
| 3 | Code owns thresholds. `gate_action` sends confidence `< 0.60` to review, shows a balance at `0.60` with no confirmation, confirms a transfer at `<= 0.90`, and sends an unknown action to review (`README.md:231`, `docs/jev-use-case-playbook.md:201-210`, `examples/python/decision_policies.py:23-40`). | demonstrated | Executed, not via pytest. `gate_action("check_balance", 0.59)` → `human_review`. `0.60` → `show_balance`, confirmation false. `approve_transfer` at `0.90` confirms, at `0.91` does not. `delete_account` at `0.99` → `human_review`. `1.01` raises `ValueError: confidence must be between 0 and 1`. | [Verified, High] |
| 4 | RAG keep/reject policy (`examples/python/decision_policies.py:64-79`). Injection `>= 0.20` rejects; either evidence noul `< 0.65` rejects; relevance `< 1.20` rejects; else keep. | partial | Policy executed: injection `0.20` with otherwise strong inputs → `reject_injection_risk`; `answers_query=0.64` → `reject_weak_evidence`; relevance `1.19` → `reject_low_relevance`; the keep fixture → `keep`. The live question set in `examples/python/workflows.py:87-111` was not called. `workflows.py:14` is a sibling import: from the repo root, `import decision_policies` raises `ModuleNotFoundError`. README does not document that module as a root entrypoint (`README.md:432` is unittest). | [Verified, High] for the pure function; live half [Maintainer claim] |
| 5 | Topic list capped at 20 (`README.md:443`, `docs/repository-metadata.md:15-36`). | demonstrated | Count of numbered backtick topics in that file: 20. First `jev`, last `typescript`. | [Verified, High] |
| 6 | `## Related Projects` sits immediately before the first other `##` (`docs/repository-metadata.md:40`). | partial | Placement holds: `README.md:29` then `README.md:37` `## The short version`. The cited strategy file `Downloads/cross-link-strategy.md` is not in this tree. | [Verified, High] for placement; strategy file absent |
| 7 | Quick-facts snapshot: alias `jev-latest`, version `jev-1.13.0`, `$0.042 / 1M` input, output free, `250,000` tok/s, `1,200` rpm, text only (`README.md:55-63`). Snapshot date `README.md:27` (September 18, 2026). | partial | Public `https://docs.typesafe.ai/models` read 2026-09-23 still lists those figures and says `jev-latest` points at `jev-1.13.0`. Not an API resolution. Not a measurement. | [External, Medium] |
| 8 | "Evidence-backed" collection (`README.md:15`, `docs/repository-metadata.md:7`). Vendor latency `70–500 ms` and "two orders of magnitude" (`README.md:66`). | partial | Use cases cite vendor docs. Offline policies execute (claims 3–4). No labelled Jev set, no own accuracy number, no latency measurement in the tree. `README.md:66` already says treat the speed sentence as vendor-reported. Launch post `https://typesafe.ai/blog/introducing-system-one-models-and-jev` still says `70ms-500ms` and early access. That page match is not a certification. | [Inference, Medium] on the adjective; latency number [External] and aspirational as a measurement |

SDK retry sentence (`README.md:413`: default retry for `429` and `529`) was inspected, not counted in the eight, and holds at the workspace pins: Python `retry.py:64` is `{408, 429, *range(500, 600)}`, which includes `529` and is wider than the sentence. JS `src/retry.ts:16-17` matches. Not a live 429/529.

`EVAL.md:39` (`pytest` 11/11) and `EVAL.md:40-42` (live quickstart numbers) were not re-run. The clone's own offline command is `python -m unittest discover -s tests -v` (`README.md:432`), not pytest. Eleven `def test_` methods are present. That is a count, not a pass.

## Clone candidates

Not cloned. Pins are `git ls-remote` HEAD at this run, not a content read. No claim about what they contain.

| repo | cited | ls-remote HEAD | in this workspace |
|---|---|---|---|
| `Anil-matcha/awesome-gpt-6-astra` | `README.md:31`, `docs/coding-agent-use-cases.md:300` | `5f6ccbaf684f09e7d87051efdd98c0da03317f3e` | no |
| `Anil-matcha/awesome-agent-apis` | `README.md:32`, `docs/coding-agent-use-cases.md:301` | `7cc66b40785027d47e52e1dfe1ea194d189bc12c` | no |
| `Anil-matcha/open-business-agents` | `README.md:33`, `docs/coding-agent-use-cases.md:302` | `49d63f08a2cbef7931fb3513406b65fb5a083a83` | no |
| `Anil-matcha/awesome-generative-ai-apps` | `README.md:34` | `8fcaa253fbb81771412f195b215e5b30ae710ee4` | no |
| `SamurAIGPT/llm-wiki-agent` | `README.md:35`, `docs/coding-agent-use-cases.md:303` | `861c6ecb0a754841da6df635e9ae32d8474275e5` | no |

Already present, so not candidates: `typesafe-ai/typesafe-sdk-python` at `upstream/typesafe-ai/typesafe-sdk-python`, `typesafe-ai/typesafe-sdk-js` at `upstream/typesafe-ai/typesafe-sdk-js`.

## T10

Result class: withheld. None of SELF, FLOOR, or INCUMBENT is earned. This catalogue does not score labelled rows, and T4–T8 are out of profile.

RULEBOOK tier per claim: table above.

NO-CLAIM: no Jev accuracy, latency, cost, calibration, or alias resolution was measured. N = 0 live calls. Vendor pages still stating `jev-1.13.0` and `70ms-500ms` are not a certification. Do not cite `EVAL.md:39-42` as a pass.

Earned-label fields: not triggered. T2 and T4–T9 are NOT-APPLICABLE by class profile and the committed T4 bar, not because a command failed.

## Boundary

Clone not edited. Dirty trees not reverted. `EVAL.md` not edited. No live Jev call. No key printed. Defects not planted (T2 out of profile; plant only in `/tmp` if a later run does T2). The five candidates were not cloned. Pytest was not run. The policy functions were executed by importing `examples/python/decision_policies.py` on `sys.path`, which is not the clone's suite.

## Re-run

From `/Users/josh/Developer/jev`, one command a non-author can re-run:

```text
git -C awesome-jev-by-typesafe rev-parse HEAD && git -C awesome-jev-by-typesafe status --porcelain=v1 -b && git -C awesome-jev-by-typesafe log -1 --format='%H %ci' && python3 -c 'import sys; sys.path.insert(0, "awesome-jev-by-typesafe/examples/python"); from decision_policies import gate_action, rag_decision, weighted_score; print(gate_action("check_balance", 0.59)); print(rag_decision(answers_query=0.99, supports_answer=0.99, contains_injection=0.20, relevance_score=2.0)); print(weighted_score({"quality": 0.8, "speed": 0.4}, {"quality": 3, "speed": 1}))'
```

Expected if the pin has not moved: HEAD `d57f5ce8002cc7cadc2c744b34a45933507e0508`, empty porcelain aside from `## main...origin/main`, then `ActionDecision(route='human_review', requires_confirmation=False)`, `reject_injection_risk`, `0.7000000000000001`.

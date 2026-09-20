# laya-mlx probe — 2026-09-20

**Verdict:** NTM **GO for a disposable test pane smoke** (one classify harness
or `laya-snake` offline after `hf download`). **promoted=0.** Not a TypeSafe
Jev replacement until a labelled parity eval. Not a measured 50× vs Jev.

Pinned clone: [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) `@fc1df62`
(`fc1df62828a3fedf4d8229fdac1cbd85f1cdf337`), Apache-2.0, PyPI `laya-mlx==0.1.0`.
Upstream weights and prompt/schema: [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)
`@6a58191`. Independent MLX port, not an official Convai or TypeSafe release.

Two hosts, two lanes — do not mix them:

| host | what ran | mlx |
|---|---|---|
| **Joshs-Mac-Studio**, Apple M3 Ultra, arm64 | parent LIVE classify, `aac6fef/laya-mlx`, `Device(gpu, 0)` | **live** — numbers below, not re-run here |
| Cloud Linux x86_64 (this receipt's author) | tiny-checkpoint unit tests only | advertised Metal/`Device(gpu)` **NOT_RUN**; default `pip install -e .` does not import `mlx` |

No NTM spawn. No live TypeSafe call. Peak RSS on Studio: **pending** (parent
measuring; do not invent).

---

## What it is

Open-weight **typed decision** runtime: state + `{choice, score, noul}` →
softmax probabilities, **0 output tokens**. Encoder is ModernBERT / mmBERT;
a small decision Transformer plus scoring and action heads run in MLX.

```text
state + typed question → bidirectional encoder → decision heads → probabilities
```

README (`README.md:7-8, 65-77`): 13.4 ms / 7.4 ms one-question P50 on M3 Max;
"no PyTorch, Transformers runtime, or cloud API" at inference. First
`laya.load(...)` of a Hub id downloads weights; later calls are local.

It is **Laya, ported to MLX**. It is not Jev. The repo never mentions TypeSafe
or Jev (search over `*.md`/`*.py`/`*.toml`: 0 hits). The Jev-shaped surface
comes from Laya's `system_one` / `predict` schema, which Convai presents as
the same three primitives Jev ships.

---

## Claims vs evidence

| Joshua's claim | Where it lives | This probe |
|---|---|---|
| "~50× faster than Jev", on-device | **Not in this repo.** Convai marketing ([laya.convaiinnovations.com](https://laya.convaiinnovations.com/)) says **6–8×** vs third-party Jev P50 **236–276 ms**, Laya T4 **32.8 ms**; batched 10-q **~20×**. laya-mlx itself compares MLX vs **upstream PyTorch MPS on the same Mac**, and says the tables "are not comparisons with … third-party API figures" (`BENCHMARKS.md:5`). | **NOT_RUN as a Jev comparison.** Do not cite 50×. Closest published (unreproduced here) number is ~7.8× T4 vs those Jev P50s. This lane's Jev smoke (~1.2 s, `EVAL.md:9`) ÷ 13.4 ms ≈ 89× is an invalid mix of network RTT + different questions + different models. |
| Max ~1G memory | README table (`README.md:57`): FP16 peak MLX allocation, **one short question**: English **943.6 MiB**, multilingual **687.6 MiB**. Ten full-context questions: **1502–1833 MiB** (`BENCHMARKS.md:57-61`). | Studio process RSS **pending** (parent measuring). "~1G" is still their English *short-question peak allocation*, not RSS. |
| Open-source classification **similar to Jev**, based on **text output probabilities** | Similar schema: yes. "Text output probabilities": **no**. Laya is a bidirectional encoder + decision heads. "0 output tokens"; "without token-by-token decoding" (`README.md:7, 65`). Next-token logit scoring is `simple-jev` / LocalJev, a different object. | Schema analogue **holds** (Studio sample: `choice=billing`, named-option probs). Token-logit story **does not**. |
| Ported to **MLX** with perf opts | `laya_mlx/model.py` reimplements ModernBERT + heads. Opt-in `compile=True`, `pad_to_multiple=16`, `cache_prompts=True` (`README.md:146`, `docs/SNAKE_OPTIMIZATION.md`). Measured Snake gain on M3 Max: **75.40 vs 70.82 moves/s (~6.5%)** over 2,400 moves. | Port **holds**. Studio parent: `pip install -e .` → mlx **0.32.2** `Device(gpu, 0)`. Opt-in compile path still **NOT_RUN**. |
| Snake on M3 Max at **~60 decisions/sec** | Uncapped eager campaign: **63.61 moves/s** over 2,400 steps (per-seed 46.32–76.37) (`docs/SNAKE_BENCHMARKS.md:5`). Optimized complete loop: **75.40**. One TTY recording: **64.77** in 20.01 s. Default play is **paced 12 FPS**. | Ballpark for *uncapped* is right. Default demo is 12. **NOT_RUN** here. Feature-assisted: planner + cycle shield (`docs/SNAKE_DEMO.md:80-82`). |

**Oracle for Studio latency:** parent run on Joshs-Mac-Studio (M3 Ultra),
baked below — this file does not re-time it. **Oracle for published M3 Max
tables:** their `benchmarks/results/` JSON + `BENCHMARKS.md` (different chip).
**Oracle for "similar to Jev":** this file's table, citing `laya_mlx/agent.py`
and `docs/demos/SDK-SURFACE.md`. **Oracle for cloud x86_64:** unit tests only;
Metal **NOT_RUN**.

---

## Jev-analogue surface

Both sides take a shared `state` and a dict of named questions, return
`answers[qid]` with `type` + primitive fields. Laya names the method
`system_one` and aliases it to `predict` (`laya_mlx/agent.py:199-253`).

```python
# Laya-MLX — laya_mlx/agent.py:199,253
result = agent.system_one(state, questions)   # == agent.predict(...)
result["answers"]["department"]["choice"]
```

```ts
// TypeSafe — docs/demos/SDK-SURFACE.md:45-49 (@typesafe-ai/sdk v0.6.0)
const r = await client.systemOne({ state, questions: { k: noul('...') } });
r.answers.k.noul
```

| | TypeSafe Jev (`SDK-SURFACE.md:30-39`) | Laya-MLX (`agent.py:224-250`) |
|---|---|---|
| Primitives | `choice`, `score`, `noul` | same (`common.py:9` `QTYPES`) |
| `choice` in | criteria **must be a map**; SDK rejects a list (`work/jev-client/src/index.ts:192-211`) | dict **or** unique string list (`agent.py:152-160`) |
| `choice` out | `choice`, `confidence`, `probabilities` | same + `action.act_probability` |
| `score` out | `score` (expected value), `confidence`, `legend`, `probabilities` | same + `action` |
| `noul` out | **`noul` only — no `confidence`** | `noul` + `confidence = max(p, 1-p)` (`agent.py:242-244`) + `action` |
| Confidence | TypeSafe's calibrated field (opaque here) | Shannon `1 - H(p)/log(k)` (`common.py:108-114`), then **overwritten** on noul |
| Abstain | caller adds `__none__` as a Choice label (skillranker / `work/omp-jev-route`) | **none built-in**; add a label yourself |
| Calibration | model-side | per-type / per-option-count **temperature** divide-before-softmax (`agent.py:220-223`) |
| Transport | `POST https://api.typesafe.ai/v1/systemone` + key | local `mx.compile`/`DecisionModel` forward |
| `model` field | `jev-1.13.0` (pinned) | hardcoded `"laya-rl-agent"` (`agent.py:248`) |
| Usage | token meter (paid) | `input_tokens`, `output_tokens: 0` |
| Fail-closed | missing `answers` / schema drift throws | non-finite logits raise `FloatingPointError` (`agent.py:213-214`); Snake policy refuses out-of-range p (`snake/policy.py:197-198`) |
| Parallel questions | all questions, one request | batched in `batch_size` (default 16); **each question still gets its own encoder pass** (`README.md:75`) |

Prompt format, for wrap authors (`common.py:88-105`):

```text
[CLS] <type> instructions [SEP] [MASK] opt0 [MASK] opt1 ... [SEP] state [SEP]
```

Noul options are always `[false, true]` (`common.py:32-57`). `p[1]` is P(true).

**Wrap implication:** a Jev client can be retargeted at the question dict and
the `choice` / `score` / `noul` fields. Do **not** assume `__none__`, do **not**
read noul `.confidence` as TypeSafe confidence, do **not** treat Laya
`confidence` as ECE-calibrated, do **not** drop `action` into a Jev schema
validator that rejects unknown keys.

---

## Install and run

### Studio LIVE — Joshs-Mac-Studio, Apple M3 Ultra, arm64

Parent ran this. **Baked as-is. This receipt does not invent a second
measurement.**

```text
python3.12 venv
pip install -e .          # clone of laya-mlx
→ mlx 0.32.2  Device(gpu, 0)
checkpoint: aac6fef/laya-mlx
timed after load (load_s ≈ 0.47 once cached)
n=30 predicts, same billing Choice as the README quickstart
```

| | parent LIVE |
|---|---|
| lane | live-mlx-gpu, published English checkpoint |
| host | Joshs-Mac-Studio, Apple M3 Ultra, arm64 |
| load_s | ≈ 0.47 (cached) |
| N | 30 |
| **p50_ms** | **8.739** |
| p95_ms | 9.777 |
| min / max | 8.153 / 9.996 |
| peak RSS | **pending** — parent measuring; not filled here |

Sample answer (one of the 30; same Choice as README):

```text
choice=billing
probabilities  billing 0.8897 / technical 0.0832 / sales 0.0271
confidence 0.628
act_probability 1.0
```

That is a typed `choice` over named options with a probability vector — the
Jev-like surface. README also documents `score` and `noul`; Studio timed the
billing Choice only. 8.739 ms on M3 Ultra is the same order as the README's
M3 Max English P50 13.42 ms; different chip, different N, not a claim that
the published table was reproduced.

### Cloud Linux x86_64 — advertised mlx NOT_RUN

`laya-mlx` does not depend on `mlx` on this platform
(`pyproject.toml:21`: `sys_platform == 'darwin' and platform_machine == 'arm64'`).
`pip install -e .` then `import mlx` is the **NOT_RUN** path: the advertised
Apple Metal runtime is not here, and `Device(gpu, 0)` cannot exist.

Default / Metal / published-weight / Snake-on-device: **NOT_RUN** on cloud.

What *did* run here is only the tiny-checkpoint unit suite, after a separate
`mlx[cpu]` extra that is **not** the Studio runtime and **not** a pass of
the README numbers:

```bash
cd /tmp/laya-probe/laya-mlx    # clone @fc1df62
python3 -m pip install -e .
# advertised import mlx: NOT_RUN (no Darwin-arm64 mlx)
python3 -m pip install 'mlx[cpu]==0.32.2' pytest 'Pillow>=12,<13' 'rich>=15,<16'
LAYA_MLX_TEST_DEVICE=cpu TOKENIZERS_PARALLELISM=false \
  python3 -m pytest -q tests/test_runtime.py tests/test_snake.py
# 46 passed in 0.74s
```

`tests/test_model.py`: **SKIPPED** (no `torch`/`transformers`, no `.upstream`).
Toy-net CPU `predict` on this VM was a schema smoke only; do not average it
with the Studio 8.739 ms.

### Disposable NTM pane (Mac) — after the Studio smoke

The classify latency is already on the board. A pane should not re-benchmark
it. Smallest remaining smoke:

```bash
# classify (already proven LIVE on Studio; replay only if the pane must see it)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
# checkpoint cached from parent: aac6fef/laya-mlx  →  Device(gpu, 0)

# or Snake, offline after one download
hf download aac6fef/laya-multilingual-mlx --local-dir models/hub/laya-multilingual-mlx
HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
  laya-snake --headless --steps 120 --max-speed --model models/hub/laya-multilingual-mlx
```

Do not run a live TypeSafe call in the same ticket unless acceptance is a
**paired** labelled table. This probe does not authorize that spend.

---

## Security / trust skim

| Check | Result |
|---|---|
| License | Apache-2.0 (`LICENSE`, `pyproject.toml:19`). NOTICE attributes Convai / Laya `@6a58191`. |
| Secrets in tree | 0 hits for `sk-…`, `Bearer …`, `TYPESAFE_API_KEY=`, `HF_TOKEN='hf_`, `tskey`. |
| Runtime deps | `numpy`, `huggingface-hub`, `tokenizers`; `mlx` **only on Darwin arm64**. Demo extra: `rich`, `Pillow`. No telemetry SDK of their own. |
| Network | `Agent` / `resolve_model` calls `huggingface_hub.snapshot_download` for Hub ids (`agent.py:9,41`). URLs: `https://huggingface.co/aac6fef/laya-mlx` (rev `04767856…`), `aac6fef/laya-multilingual-mlx` (`ba40c87f…`), `aac6fef/laya-typed-decisions-mlx` (`28416e78…`) — `benchmarks/results/hub-publication.json`. Also original `convaiinnovations/laya*` ids. |
| Snake offline | Sets `HF_HUB_OFFLINE=1` and `HF_HUB_DISABLE_TELEMETRY=1`; `local_files_only=True`; missing cache → `FileNotFoundError`, no connect (`snake/policy.py:19-42`). Unit test `test_missing_local_model_fails_without_a_network_attempt` passed here. |
| First `laya.load("aac6fef/…")` | **Does** talk to Hugging Face (weights + hub metadata). Not secret exfil. Set `HF_HUB_DISABLE_TELEMETRY=1` and pin `--local-dir` / `revision=` for a Studio pane. |
| Phones home otherwise | No analytics endpoint in `laya_mlx/`. Inference is local tensors. |
| CI | `.github/workflows/ci.yml`: `macos-26`, `LAYA_MLX_TEST_DEVICE=cpu`, ruff + pytest + `python -m build`. Contents:read only. |

No red-flag secrets or exfil. Treat first-load Hub as the only network surface.

---

## NTM go / no-go

Studio recommendation, adopted: **GO for a disposable test pane smoke.**
Not a replacement for TypeSafe Jev until a labelled parity eval.
**promoted=0.**

The three wrap gates still hold, and Studio already proved (2):

1. **API is wrap-clear.** Typed `choice` → named-option probabilities;
   `score` / `noul` per README. Fields line up enough for an adapter.
2. **Local Mac path exists and ran.** `python3.12` venv, `pip install -e .`,
   mlx 0.32.2 `Device(gpu, 0)`, `aac6fef/laya-mlx`, P50 **8.739 ms** (n=30).
3. **No secret/exfil red flag.** Apache-2.0, Hub download, Snake already
   offline.

**Not GO for:** replacing TypeSafe Jev, citing 50×, promoting a seam, or
claiming Snake "reasons about the board" (planner + shield).

### Smallest NTM ticket (one pane)

**Disposable smoke, one pane.** Classify *or* `laya-snake` offline after
`hf download`. Do not re-time the 8.739 ms unless the pane is checking
install drift.

- Acceptance: pane starts, `Device(gpu, 0)` or Snake prints a finite
  `steps_per_second` / `mean_inference_ms`; known-missing checkpoint fails
  closed without a network connect.
- **NO-CLAIM:** not a Jev substitute; no labelled parity; no `__none__`;
  no live TypeSafe spend; Studio peak RSS still **pending**.
- **promoted=0.**

Do not invent STOP-LIVE. Do not spawn NTM from this probe.

---

## Boundary

- No TypeSafe / Jev HTTP call on either host.
- Cloud did **not** load `aac6fef/laya-mlx` and **cannot** import advertised
  `mlx` / `Device(gpu)`.
- Studio LIVE is **one billing Choice**, n=30, after cached load. Not
  `score`, not `noul`, not Snake, not `--optimize`.
- Studio peak RSS: **not in this receipt** (parent still measuring).
- This file does **not** re-run or average the Studio timings.
- No `tests/test_model.py` encoder-vs-Transformers run.
- No Convai T4 32.8 ms / Jev 236–276 ms pair reproduced.
- Weights and `docs-mirror/typesafe/` were not refreshed; Jev field names
  are from `docs/demos/SDK-SURFACE.md` (v0.6.0, 2026-09-19).
- Cloud clone lived at `/tmp/laya-probe/laya-mlx` (read-only eval). Not
  vendored into this repo.

---

## Honest state

| capability | state | reason |
|---|---|---|
| Laya-MLX local classify (English ckpt) | **live-verified (N=30)** on Studio | parent: p50 **8.739 ms**, `Device(gpu, 0)`, `aac6fef/laya-mlx`. Cloud Metal **NOT_RUN** |
| "~50× faster than Jev" | **ZERO** | not in repo; no paired run; Convai's own figure is ~7.8× T4 vs published Jev P50 |
| M3 Snake ~60/s | **EXPLORED** | their JSON + docs; not executed on Studio or cloud |
| Jev replacement | **ZERO** | no labelled parity; different confidence; no `__none__` |
| omp / NTM dogfood | **not started** | GO for a disposable pane smoke only; this probe does not spawn it |

**Next lever:** bake parent peak RSS when it arrives. Then a disposable
NTM pane (classify replay or offline Snake) — not a Jev-replacement eval.

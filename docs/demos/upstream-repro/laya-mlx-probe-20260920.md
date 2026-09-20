# laya-mlx probe — 2026-09-20

**Verdict:** NTM dogfood **GO** (one pane, one classify harness). **promoted=0.**
Not a TypeSafe Jev replacement. Not a measured 50× vs Jev. Metal / published-weight /
Snake-on-M3 numbers are **NOT_RUN** on this host.

Pinned clone: [mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) `@fc1df62`
(`fc1df62828a3fedf4d8229fdac1cbd85f1cdf337`), Apache-2.0, PyPI `laya-mlx==0.1.0`.
Upstream weights and prompt/schema: [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)
`@6a58191`. Independent MLX port, not an official Convai or TypeSafe release.

Probe host: Linux x86_64 (`Linux-6.12.94+`, Python 3.12.3). Not Apple Silicon.
No Metal. No NTM spawn. No live TypeSafe call.

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
| Max ~1G memory | README table (`README.md:57`): FP16 peak MLX allocation, **one short question**: English **943.6 MiB**, multilingual **687.6 MiB**. Ten full-context questions: **1502–1833 MiB** (`BENCHMARKS.md:57-61`). | **UNMEASURED here** (no published checkpoint). "~1G" matches the English *short-question peak allocation*, not process RSS, and not the long/batched case. |
| Open-source classification **similar to Jev**, based on **text output probabilities** | Similar schema: yes. "Text output probabilities": **no**. Laya is a bidirectional encoder + decision heads. "0 output tokens"; "without token-by-token decoding" (`README.md:7, 65`). Next-token logit scoring is `simple-jev` / LocalJev, a different object. | Schema analogue **holds**. Token-logit story **does not**. |
| Ported to **MLX** with perf opts | `laya_mlx/model.py` reimplements ModernBERT + heads. Opt-in `compile=True`, `pad_to_multiple=16`, `cache_prompts=True` (`README.md:146`, `docs/SNAKE_OPTIMIZATION.md`). Measured Snake gain on M3 Max: **75.40 vs 70.82 moves/s (~6.5%)** over 2,400 moves. | Port **holds** (code + CI on `macos-26`). Perf opts **documented**; M3 numbers **NOT_RUN** here. |
| Snake on M3 Max at **~60 decisions/sec** | Uncapped eager campaign: **63.61 moves/s** over 2,400 steps (per-seed 46.32–76.37) (`docs/SNAKE_BENCHMARKS.md:5`). Optimized complete loop: **75.40**. One TTY recording: **64.77** in 20.01 s. Default play is **paced 12 FPS**. | Ballpark for *uncapped* is right. Default demo is 12. **NOT_RUN** here. Feature-assisted: planner + cycle shield (`docs/SNAKE_DEMO.md:80-82`). |

**Oracle for published M3 numbers:** their checked-in JSON under `benchmarks/results/`
plus the method in `BENCHMARKS.md`. **Oracle for "similar to Jev":** this file's
table, citing `laya_mlx/agent.py` and `docs/demos/SDK-SURFACE.md`. **Oracle for
this host:** the pytest / tiny-forward commands below.

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

### This host (Linux x86_64) — what actually ran

`laya-mlx` installs **without** `mlx` on Linux: the dep is gated
`sys_platform == 'darwin' and platform_machine == 'arm64'`
(`pyproject.toml:21`). Bare `pip install mlx==0.32.2` yields a wheel whose
`.so` needs `libmlx.so` (**import fail**: `libmlx.so: cannot open shared
object file`). `pip install 'mlx[cpu]==0.32.2'` pulls `mlx-cpu==0.32.2` and
CPU device `Device(cpu, 0)` works.

```text
# measured 2026-09-20T15:56Z, this VM
import mlx.core as mx          5.13 ms, then Device(cpu, 0)
import laya_mlx as laya        240.19 ms, rss 61_500 KB
laya.__version__               0.1.0
```

Unit tests, tiny random checkpoint, `LAYA_MLX_TEST_DEVICE=cpu`:

```bash
cd /tmp/laya-probe/laya-mlx    # clone @fc1df62
python3 -m pip install -e .
python3 -m pip install 'mlx[cpu]==0.32.2' pytest 'Pillow>=12,<13' 'rich>=15,<16'
LAYA_MLX_TEST_DEVICE=cpu TOKENIZERS_PARALLELISM=false \
  python3 -m pytest -q tests/test_runtime.py tests/test_snake.py
# 46 passed in 0.74s
```

`tests/test_model.py` (Transformers / upstream DecisionModel parity): **SKIPPED**
— no `torch`/`transformers`, no `.upstream` clone. pytest collect = 1 skipped,
exit 5. Not a fail of the port.

One `Agent.predict` on the **same tiny random 64-d / 3-layer** fixture the
unit tests build (20 timed calls after 1 warmup, CPU):

| | value |
|---|---|
| lane | offline-cpu-tiny-random-weights |
| load | 2.12 ms |
| N | 20 |
| P50 / P95 | **10.597 / 11.310 ms** |
| usage | `input_tokens=77`, `output_tokens=0` |
| peak RSS | **75_100 KB** (~73 MiB) |
| `model` | `laya-rl-agent` |

Returned shape (random weights ⇒ near-uniform; this is a **schema smoke**,
not a quality number):

```json
{
  "topic": {"type":"choice","choice":"a","confidence":0.0,
            "probabilities":{"a":0.3353,"b":0.3333,"c":0.3314},
            "action":{"act_probability":0.5382}},
  "level": {"type":"score","score":0.494,"confidence":0.0001,
            "legend":{"0":"low","1":"high"},
            "probabilities":{"0":0.506,"1":0.494},
            "action":{"act_probability":0.539}},
  "yes":   {"type":"noul","noul":0.4994,"confidence":0.5006,
            "action":{"act_probability":0.5256}}
}
```

**These 10 ms are not the README's 7–13 ms.** The published figures are
322M–421M FP16 on M3 Max Metal. This is a toy CPU net. Do not average them.

Published-weight forward, Metal, Snake TTY, Hub download of `aac6fef/laya-*`:
**NOT_RUN** (no Apple GPU; no 800 MiB weight pull on this probe).

### Apple Silicon / Studio / M3 — commands for a real smoke

Requires macOS 14+, Python 3.11+, Apple Silicon. Measured upstream env:
macOS 27.2, Python 3.12.13, MLX 0.32.2, M3 Max 40-core / 128 GiB.

```bash
# 1. Classify harness (recommended NTM ticket)
python3 -m pip install 'laya-mlx[demo]'          # or: uv sync --extra demo
hf download aac6fef/laya-mlx --local-dir models/laya-mlx
# offline after this:
HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
python3 - <<'PY'
import json, time, resource, laya_mlx as laya
t0 = time.perf_counter()
agent = laya.load("models/laya-mlx", dtype="float16", device="gpu")
print("load_s", round(time.perf_counter() - t0, 3))
state = json.load(open("examples/state.json"))      # if cwd is the clone
questions = json.load(open("examples/questions.json"))
agent.predict(state, questions)  # warmup
times = []
for _ in range(20):
    t = time.perf_counter()
    out = agent.predict(state, questions)
    times.append((time.perf_counter() - t) * 1000)
times.sort()
print("p50_ms", round(times[9], 3), "p95_ms", round(times[18], 3))
print("rss_kb", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
print(json.dumps(out, indent=2)[:800])
PY

# 2. Optional: Snake, only if the pane's job is the demo
hf download aac6fef/laya-multilingual-mlx --local-dir models/hub/laya-multilingual-mlx
laya-snake --headless --steps 120 --max-speed --model models/hub/laya-multilingual-mlx
# interactive: terminal ≥ 104×35; default is paced 12 FPS, not 60
# laya-snake --optimize --max-speed
```

CLI equivalent of (1), from a clone:

```bash
laya-mlx predict --model models/laya-mlx --device gpu \
  --state-file examples/state.json --questions examples/questions.json
```

Do not run a live TypeSafe call in the same ticket unless the ticket's
acceptance is a **paired** latency/quality table. This probe does not
authorize that spend.

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

**GO** — all three gates hold:

1. **API is wrap-clear.** `system_one(state, questions)` / `predict`; three
   primitives; fields line up enough to write an adapter in one file.
2. **Local Mac path exists.** `pip install laya-mlx` + `hf download` +
   `device="gpu"`. Commands above. This VM cannot execute that path.
3. **No secret/exfil red flag.** Apache-2.0, Hub download, Snake already
   offline.

**Not GO for:** replacing TypeSafe Jev, citing 50×, promoting a seam, or
claiming Snake "reasons about the board" (planner + shield).

### Smallest NTM ticket (one pane)

**One classify harness on Joshua's M3 / Studio Mac.** Not Snake first.

- Install `laya-mlx`, download `aac6fef/laya-mlx` once, run the 20-call
  script in the Apple Silicon section against `examples/state.json` +
  `examples/questions.json`.
- Record: load s, P50/P95 ms, RSS, `answers` field set, MLX version, chip.
- Acceptance: schema matches the table (choice/score/noul + `output_tokens=0`);
  P50 is in the same *order of magnitude* as 7–14 ms **or** the pane writes
  why not (thermal, CPU fallback, first-compile).
- Planted negative: `Agent._to_internal({"type":"choice","instructions":"x","criteria":[]})`
  raises; a finite-logits check already exists.
- **NO-CLAIM:** not a Jev substitute; no paired quality number; no `__none__`;
  no live TypeSafe spend unless a later ticket adds a paired table.
- **promoted=0.**

Snake (`laya-snake --headless --steps 120 --max-speed`) is a **second**
ticket if the classify harness lands. It tests the planner loop, not the
wrap.

Do not invent STOP-LIVE. Do not spawn NTM from this probe.

---

## Boundary

- No TypeSafe / Jev HTTP call.
- No published 322M/421M checkpoint loaded.
- No Metal, no M3, no TTY Snake, no `laya-snake --optimize`.
- No `tests/test_model.py` encoder-vs-Transformers run.
- No Convai T4 32.8 ms / Jev 236–276 ms pair reproduced.
- Weights and `docs-mirror/typesafe/` were not refreshed; Jev field names
  are from `docs/demos/SDK-SURFACE.md` (v0.6.0, 2026-09-19).
- Clone lived at `/tmp/laya-probe/laya-mlx` (read-only eval). Not vendored
  into this repo.

---

## Honest state

| capability | state | reason |
|---|---|---|
| Laya-MLX as local typed-decision runtime | **PROBED** (CPU toy + source) | 46/46 offline tests; schema smoke; Mac path documented |
| "~50× faster than Jev" | **ZERO** | not in repo; no paired run; Convai's own figure is ~7.8× T4 vs published Jev P50 |
| M3 Snake ~60/s | **EXPLORED** | their JSON + docs; not executed here |
| Jev replacement | **ZERO** | different model, different confidence, no `__none__`, no live quality pair |
| omp / NTM dogfood | **not started** | ticket above; this probe does not spawn it |

**Next lever:** one M3 pane, classify harness, write the latency/RSS line
into a follow-up receipt. Then decide whether a wrap belongs in
`work/jev-client` as an injected asker — only after those numbers exist.

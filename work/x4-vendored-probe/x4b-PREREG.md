# X4b PREREG (committed copy for bead jev-x4-vendored-probe-closeout-82p7)

Body copied unchanged from `var/agent-tmp/dogfood/x4b-vendored-embed/PREREG.md` (sha256 5eb77b95ab7bf9f1911b3926a383028fdbc9ebad2d31bf2114bf7ffa1b7ab1ae); only the title line is replaced. Gate added by converge r4: X4b runs only after this file is committed AND `jev-mvvh` returns a vendor-shadow verdict of KEEP; its runner first calls `scripts/local-model-guard.sh --timeout 1` and records NOT_RUN on exit 2 or 3 with zero model loads.

Not blind: a scratch run under this text already produced a held result on 2026-10-04 (`var/agent-tmp/dogfood/x4b-vendored-embed/RECEIPT.md`: AUC .86570, ECE .21262 vs Jev .18460, LOSES). A gated run under this file is a replication of that result, not a first look.

## Question and frozen rows
Can a local Qwen3-Embedding-0.6B embedding with a dev-only logistic-regression classifier distinguish the frozen third-party-code windows on the held set, while meeting the Jev incumbent AUC and calibration contract?

- Source: `work/vendor-paste/sample.json`; exact bytes SHA-256 `2a167ed69ebfa5aa41399b278c14c1dae5a40ec630f4de97cfbb7faaa39644ab`.
- Fixed split: 120 dev (60 positive, 60 negative); 200 held (100 positive, 100 negative). Windows carry `sample_id`, `win_sha`; labels are `pos`/`neg`.
- The dataset's canonical sorted-JSON hash starts `d510050d83bf`; dev/held source groups are disjoint (46 vs 53; intersection 0), per `var/agent-tmp/dogfood/x4-vendored-probe/PREREG.md`.
- Jev incumbent: `work/vendor-paste/vendor-rows.jsonl`; 200 held scores, AUC 0.82745, ECE 0.1846. ECE is reproduced on frozen held labels using the 10-bin rule in `work/local-decision-arms/vendor.py:85-93` (bins `min(int(p*10),9)`, weighted absolute confidence/label-frequency gap).
- Clef incumbent: `work/local-decision-arms/vendor-rows-clefflash.jsonl`; 200 held scores, AUC 0.83885. Both incumbent ID sets and Jev window hashes must match the preregistered rows.
- Constant majority predictor AUC: 0.500. Cheapest existing `lic`-bit rule AUC: 0.50833 dev, 0.56500 held (`var/agent-tmp/dogfood/x4-vendored-probe/PREREG.md`).

## Fixed model and evaluation
- Model: cached local snapshot `Qwen/Qwen3-Embedding-0.6B`, snapshot `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`, under `/Volumes/ZestData/.../models/huggingface/`; its `model.safetensors` resolves locally to 1,191,586,416 bytes. No model or package downloads; offline mode only.
- The cached snapshot contains raw Transformer files but no Sentence-Transformers `modules.json` / pooling config. Construct the Sentence-Transformers `Transformer` plus the model-card-specified last-token `Pooling` (`pooling_mode_lasttoken=True`), then L2-normalize embeddings. Model pooling reference: <https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/blob/main/1_Pooling/config.json>. Raw windows, no prompt or metadata features. CPU only; `max_seq_length=8192`; fail rather than score any truncated input.
- Embed all 320 windows; train only on the 120 dev embeddings with `LogisticRegression(C=1.0, solver='liblinear', max_iter=1000, random_state=20261004)`. No hyperparameter, threshold, prompt, or feature selection against held labels.
- Primary metrics on the identical 200 held rows: ROC-AUC and 10-bin ECE (same rule as Jev). Report paired DeLong two-sided p-values versus Jev and Clef, using the implementation in `var/agent-tmp/dogfood/x4-vendored-probe/run.py:37-77`.
- Fixed pass bar: held AUC >= Jev AUC - 0.02 = 0.80745 **and** held ECE <= Jev ECE = 0.1846. Both conditions are required by the vendor contract (`work/local-decision-arms/BAR-vendor.md:7-9`). Otherwise verdict `LOSES`; row/hash/finite-score failures are `NOT-DECIDED`. No significance claim from a p-value alone.

## Resource and spend cap
- Exact offline invocation: `uv run --offline --no-project --python 3.12 --with torch --with transformers --with sentence-transformers --with scikit-learn`.
- First planned CPU execution timed out (see amendment); successful execution used MPS per the amendment. `nice -n 10`, concurrency 1, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `PYTORCH_ENABLE_MPS_FALLBACK=0`; no live Jev/Clef calls, network, or paid calls; spend cap $0.00.
- Persist only model scores/embeddings/metrics and logs under this experiment directory; never copy window text into outputs.
## Execution amendment (before any scored output)

The preregistered CPU attempt timed out after 3,600 seconds. Its captured output shows cached weights loaded, but no predictions, embeddings, or metrics were produced. No held-set result was observed. A separate offline preflight found `torch.backends.mps.is_available() == True` and `is_built() == True`. The successful rerun used MPS for the same fixed rows, pooling, dev-only fit, metrics, and bars; only the execution backend changed. `PYTORCH_ENABLE_MPS_FALLBACK=0` prevented silent fallback to CPU.

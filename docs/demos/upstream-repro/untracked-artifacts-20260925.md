# Untracked artifact classification (2026-09-25)

Bead: `jev-hrli`.

## Snapshot

The requested 1,225-file snapshot was observed first. Pane 3 added 47 more in-flight files while the classification was being recorded, so the committed snapshot inventory below is the later, complete **1,272-file** status. No file was deleted or moved. The 698 files under `work/loss-depth/pokejev-components/` are pane-3 in-flight outputs and were not read or touched beyond path/size inventory.
| Classification | Files | Bytes | Handling |
|---|---:|---:|---|
| (a) byte-identical duplicate of a committed file | 12 | 707,115 | Existing committed target covers the bytes; mappings below |
| (b) dependency of a committed receipt/EVAL/README | 445 | 20,414,416 | Small clean files committed; larger/private outputs covered by manifests below |
| in-flight pane-3 outputs | 698 | 19,617,405 | Left in place; no live leaf-arm file touched |
| (c) scratch / uncited artifact | 117 | 79,455,840 | Left in place; no committed artifact depends on it |
| **Total** | **1,272** | **120,194,776** | |

The original bead's approximate 95 MB figure was a rounded earlier snapshot; the exact current regular-file sum is above. Five manifest files created for this report are excluded from the snapshot inventory.

## (a) Duplicate mappings

The following untracked files have the same SHA-256 as the committed target shown:

- `work/gate-observe-dogfood/flags-4.partial.jsonl` -> `work/gate-observe-dogfood/flags-4.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-exact-rerun.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-exact-rerun.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-exact-rerun2.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-exact-rerun2.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-exact-rerun3.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-exact-rerun3.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-isolated-correct.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-isolated-correct.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-isolated-rerun.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-isolated-rerun.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-date-time-isolated-rerun2.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-date-time-isolated-rerun2.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-page-text.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-page-text.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-quoted-exact.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-exact.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-quoted-isolated-correct.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-isolated-correct.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-quoted-isolated-rerun.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-isolated-rerun.s0.jsonl`
- `work/miniwob-jev/rows/miniwob-jev-v3-dev-quoted.s0.jsonl` -> `work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted.s0.jsonl`

The MiniWoB v3 receipt names the eleven row copies as NOT-SCORED evidence (`docs/demos/upstream-repro/miniwob-jev-v3-20260925.md:28-43`); the committed byte-identical counterparts cover them without duplicating the rows.

## (b) Dependent groups and coverage

| Untracked group | Count | Dependent artifact | Coverage |
|---|---:|---|---|
| `work/poke-jev/stage-b/replays-abyssal*/`, `replays-random/` | 420 | `work/poke-jev/stage-b/receipt.json`; `docs/demos/upstream-repro/pokejev-stage-b-results-20260925.md:67-72` | `work/poke-jev/stage-b/stage-b-replays-420.sha256` |
| `work/openrouter-incumbents/rows-*.jsonl` | 12 | `docs/demos/upstream-repro/openrouter-incumbents-20260924.md:161-173` | `work/openrouter-incumbents/openrouter-402-rows.sha256` |
| `work/nev-injection/l3-frames-D1c-hostile.jsonl`, `D2-benign.jsonl`, `D3-keyless.jsonl` | 3 | `work/nev-injection/l3-receipt.json:1` | `work/nev-injection/l3-frames-committed-receipt.sha256` |
| `work/nev-routing/tool-select-hashed.jsonl` | 1 | `work/nev-routing/TOOLSELECT-RECEIPT.json:1`; `work/nev-routing/PREREGISTER-TOOLSELECT.md:11-14` | `work/nev-routing/tool-select-hashed.sha256` |
| `work/bicameral-gate/real-sample-b.json` | 1 | `docs/demos/upstream-repro/bicameral-gate-criteria-20260924.md:7,99-103` | `work/bicameral-gate/real-sample-b.sha256` |
| `work/jev-triage/runs/2026-09-20T221149741Z.json` | 1 | `EVAL.md:774` | committed directly |
| `work/jev-triage/runs/2026-09-20T221837415Z.json` | 1 | `EVAL.md:826` and `work/jev-triage/hybrid.mjs:27` | committed directly |
| `work/jev-triage/runs/hybrid-2026-09-20T222532529Z.json` | 1 | `EVAL.md:894` | committed directly |
| `work/citation-check/fixture.mjs`, `src/{check,live}.ts`, `test/check.test.mjs` | 4 | `docs/demos/upstream-repro/typesafe-skills-w70-2026-09-23.md:84`; `typesafe-skills-w70-20260922.md:84`; test references in `TESTS.md` | committed directly |
| `work/nev-routing/lexical_baseline.py` | 1 | `work/jev-toolout-flag/score.py:27`; `docs/demos/upstream-repro/jev-toolout-flag-20260924.md:36-37` | committed directly |

The direct citation-check verification is `node --experimental-strip-types --test work/citation-check/test/check.test.mjs`: **7/7 pass**, including the planted asker-transport failure returning review.

The existing `work/poke-jev/stage-b/replays-abyssal.sha256` remains the per-file manifest for the live Abyssal subdirectory; the new aggregate manifest covers all 420 replay files, including control and random.

The 66 MB `work/nev-routing/tool-select-labelled.jsonl` and the raw `tool-select-unlabelled.jsonl` are deliberately scratch/private: the preregistration explicitly says not to use the labelled corpus as the denominator and the text source is local-only. The extra injection attempts (`D1`, `D1b`, `D3b`, `D3c`) and the uncited triage receipt remain scratch. The OpenRouter row outputs named by the committed blocked receipt are the 12-file dependent group above; any uncited attempt remains scratch.

## In-flight pane-3 outputs

All **698** files below remain untouched and are explicitly in-flight, not scratch:

- `work/loss-depth/pokejev-components/battle/stage-b/**`
- `work/loss-depth/pokejev-components/stage-b/**`
- `work/loss-depth/pokejev-components/replays-abyssal-leaf-code-v1/**`
- `work/loss-depth/pokejev-components/replays-abyssal-leaf-code-leaf-c-r2-code/**`
- the corresponding `decisions-*`, `results-*`, and `receipt-*` files directly under `work/loss-depth/pokejev-components/`

No manifest was generated for these changing files. After pane 3 finishes, the next inventory must hash them before any result is cited.

## Scratch

The remaining 117 files have no committed receipt, EVAL row, or README number that consumes their bytes. This includes the 82 `notes/` artifacts, callback/dispatch text, temporary plants, uncommitted guard-rule fixtures, rescue files whose `.exact` committed counterparts already exist, the uncited `jev-triage` hybrid attempt, and the uncited OpenRouter/injection attempts. Nothing was deleted or moved.

The committed TSV is the immutable path/hash snapshot. This command re-derives the classification counts and byte totals after the dependent files and manifests have been committed. The TSV is a snapshot: in-flight source files may legitimately change after capture.

```bash
python3 - <<'PY'
import csv, hashlib
from pathlib import Path

rows = list(csv.DictReader(
    Path("docs/demos/upstream-repro/untracked-artifacts-20260925.tsv").open(),
    delimiter="\t",
))
for category in ("A", "B", "I", "S"):
    selected = [r for r in rows if r["category"] == category]
    print(category, len(selected), sum(int(r["bytes"]) for r in selected))
assert len(rows) == 1272
assert {r["category"] for r in rows} == {"A", "B", "I", "S"}
print("snapshot rows:", len(rows))
print("categories:", sorted({r["category"] for r in rows}))
print("inventory SHA-256:", hashlib.sha256(
    Path("docs/demos/upstream-repro/untracked-artifacts-20260925.tsv").read_bytes()
).hexdigest())
PY
```

For each dependent group, the corresponding `*.sha256` file is the canonical `sha256  path` manifest. Verify it with a loop that parses each row and hashes the named path; missing artifacts fail closed rather than passing as an empty set. The inventory is deliberately hash-only: it contains no captured response bodies or secrets.

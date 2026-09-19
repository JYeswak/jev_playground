# `jev-agent-failure-benchmark`: this lane's own question, asked properly by someone else

Upstream: `jev-agent-failure-benchmark`, cloned here, untouched. It asks whether a fast, cheap
decision model can find what broke an AI agent — which is the question this lane exists to answer,
posed with a sample size and confidence intervals we have never approached.

## What was run

```bash
mkdir -p data && REV=0bd196c8a040841c4ae167ab33cc8151de246f1f
curl -L ".../whowhen_pro/resolve/$REV/data/text.jsonl"  -o data/text.jsonl     # 73 MB, pinned
curl -L ".../whowhen_pro/resolve/$REV/taxonomy.yaml"    -o data/taxonomy.yaml
uv run --with pytest --with pytest-asyncio python -m pytest -q
```

```
without the dataset:  18 passed, 2 skipped
with the dataset:     20 passed, 0 skipped
```

**The two tests that skip without data are `test_candidates.py` and `test_leakage.py`.** A
leakage check is the single most important test a benchmark ships, and it is one of the two that
silently does not run on a fresh clone. It passes once the data is there; the hazard is that a
contributor sees `18 passed` and reads it as green.

The dataset is **pinned to a revision** in the README, so the fetch is reproducible rather than
"latest". That is the detail most benchmarks get wrong.

## Its published claim

| Model | Who | When | What | All |
|---|---|---|---|---|
| Jev (n=6257) | **73.4** [70.5, 76.2] | **76.4** [74.3, 78.4] | **23.7** [22.4, 24.9] | **31.3** |
| gpt-5.4 *(paper)* | 55.7 | 72.3 | 15.3 | 21.3 |

**n=6257 with intervals on every cell**, against `jev-benchmark`'s n=60 where two model versions
turned out never to disagree ([pairing receipt](jev-benchmark-pairing-20260918.md)). Same domain,
two orders of magnitude apart in power, and only one of them can support a comparison.

Upstream states its own caveat rather than burying it: **Who and When are adaptation-favoured**,
because Jev picks from the trace's enumerated options. The honest reading is that the strong
columns are the ones where the task is selection, and `What` at 23.7 is where free classification
actually lives.

## Why it matters to this lane specifically

This repo spent a day adjudicating 17 candidate ideas and promoting none. The nearest upstream
analogue ran 6,257 cases with intervals and published where its own numbers are flattered. The gap
is not the verdict, it is the **denominator**: our rulings rest on single runs and hand counts, and
a benchmark like this is what a promoted candidate would eventually have to survive.

## No-claim

- **Nothing here re-runs the benchmark.** 20 passing tests prove the harness is sound on this
  machine, not that 73.4 reproduces. Reproducing the table needs live calls at n=6257 and was not
  attempted.
- The table above is **quoted from upstream's `RESULTS.md`**, not measured here.
- The comparison row is labelled *(paper)* by upstream, so it is a cited figure against their own
  measured one, not a head-to-head both parties ran.
- The 73 MB dataset is fetched into the clone's `data/` directory, which is **gitignored upstream**;
  no clone file is modified, but the working tree is no longer pristine.

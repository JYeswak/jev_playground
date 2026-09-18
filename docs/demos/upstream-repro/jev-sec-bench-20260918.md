# `jev-sec-bench`: an independent replication of the effect that cost us a retraction

Upstream: `jev-sec-bench`, cloned here, untouched. Blind security benchmarks for Jev, shipped as a
Go TUI with committed results.

## Our own table was wrong about this repo

The root `README.md` listed it as *"not run, README only"*. It is a **Go module** with `cmd/jev-tui`,
a `go.mod`, and three committed result files. I wrote that row from an `ls` that showed a README and
stopped reading. **The claim cost nothing to check and I did not check it**, which is the same defect
class as reading `s1-rs`'s blocker as capacity.

## What was run

```bash
go vet ./...                                   # clean
go build -o /tmp/jev-tui ./cmd/jev-tui         # clean, 12M
/tmp/jev-tui -shot 100x30 -tab overview        # headless frame, no TTY, no key
```

Three result sets ship with the repo, all `failed: 0`: `injection` (662 requests, 22.7 s),
`injection_no_context` (662 requests, 21.9 s) and `code` (400 requests, 13.5 s), all against
`jev-1.13.0` on 2026-09-16.

Headline figures as its dashboard renders them: prompt injection **96.5% accuracy, AUC 0.9927,
ECE 0.0588, p50 325 ms**, on 662 messages of which 263 are hostile, with 10 false positives and 13
false negatives. Vulnerable code: **AUC 0.7940** over 200 blind pairs, same task and language.

## The finding: it replicates our framing leak, with the sign reversed

Its `CONTEXT AS STATE` panel is an ablation on exactly the variable that produced this lane's only
public retraction. Its description: *"same model, same questions. the only change is whether the
request says what the assistant is for."*

| | bare | +context |
|---|---|---|
| recall | 74.9% | **95.1%** |
| accuracy | 89.7% | **96.5%** |

**We measured the same sensitivity and drew the opposite lesson.** In
[`NOTE-framing-leak.md`](../jev-probe/NOTE-framing-leak.md) we found that stripping framing flipped a
verdict (`router_pays` 0.21 to 0.59) and treated that as a **warning**: framing leaks, so strip it
and re-run as a control. Upstream measured the same dependence and treated it as **operating
guidance**: tell the model what the assistant is for, and recall rises twenty points.

Both readings are right, and the distinction is the useful part. **Context that states the task is
state; context that states the answer is leakage.** Our probe had smuggled the conclusion into the
criteria, so removing it was a correction. Theirs supplies the deployment's purpose, which the model
genuinely needs and a real caller genuinely has. We generalised from one bad prompt to "framing is
dangerous"; the ablation at n=662 says the danger is specific.

## No-claim

- **Nothing here re-ran the benchmark.** The figures are read from its committed results and its own
  renderer; no live call was made and no key was used.
- Its `live` tab requires samples and a key, and is **unrun**.
- `go vet` and a clean build prove the toolchain is sound, **not** that the harness is correct; its
  sampling, blinding and pairing were not audited.
- The bare-versus-context comparison is **upstream's ablation**, not ours. We contribute the
  observation that it replicates our framing result, not the measurement.
- Our framing note and this benchmark differ in task, corpus and model version, so *"same effect"* is
  an interpretation of two measurements, not a controlled comparison.

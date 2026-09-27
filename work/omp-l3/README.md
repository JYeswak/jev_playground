# OMP Jev tool L3 harness

`PREREG.md` freezes the six-call bar. `drive.mjs` starts one fresh `omp --profile=muse --cwd <repo> --mode=rpc --max-time=420` session, negotiates protocol v2, and prompts the model to call `jev_rerank`, `jev_claim_check`, and `jev_classify` on captured public inputs followed by one bad input per tool.

The recovered live session is recorded in `frames.jsonl` and `receipt.json`:

- Healthy calls: rerank selected candidate `44955`; claim check returned `unsupported`, value `0.23`, cut `0.5`; classify returned `card arrival`, confidence `0.970`.
- All healthy results reported `model: jev-1.13.0` and usage.
- Refusals: 21 passages, empty evidence, and one label were rejected by OMP schema validation before tool execution; each had no Jev usage and is recorded as `refused-by-schema`.
- Totals: 2,119 input tokens, 804 output tokens, estimated Jev input spend `$0.000088998` at `$0.042/M` input tokens; output free.
- Tool latencies: rerank 155 ms, claim check 136 ms, classify 145 ms.

`recover.mjs` converts the profile session JSONL into the filtered no-key transcript and receipt. The first `omp-test` attempt timed out before any target tool execution; it is not scored. The valid run used the proven `muse` profile after the committed preregistration amendment.

```bash
node work/omp-l3/drive.mjs
```

Boundary: one real OMP session and captured public inputs; no fleet-wide reliability, repeated-session variance, or outcome-value claim.

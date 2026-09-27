# jev-f4ea — real OMP RPC L3 preregistration

Status: frozen before the first live call. No live Jev call has been made under this bar.

## Question

Can one fresh `omp --mode=rpc` session in this repository call the three measured Jev tools on captured public inputs, and refuse one known-bad input per tool without a Jev request?

## Session and model

- Transport: one fresh `omp --profile=omp-test --cwd <repo> --mode=rpc --max-time=600` session.
- RPC handshake: `negotiate_protocol` with `protocolVersion: 2` first, then one `prompt`.
- Jev model: the kit tools pin `jev-1.13.0`.
- Key: tool-local Infisical provider; no key value enters the repository, transcript, or receipt.
- Hard cap: six tool executions (three healthy, three refusals). The driver kills the child after twelve observed Jev-tool executions or the 600-second deadline.
- Spend: report each live result's `usage.input_tokens` and `usage.output_tokens`; input cost is `input_tokens * $0.042 / 1,000,000`, output is free. No comparator call.

## Captured inputs

- Rerank: `kit/examples/rerank-candidates.json`, the captured FiQA query is the prompt query from `kit/ROBOT.md` and the two public candidate passages are unchanged.
- Claim check: claim and evidence from `kit/test/verify.test.mjs` and `kit/examples/scifact-evidence.txt`.
- Classify: `kit/examples/banking77-example.json` row 1 and the committed 77-label set in `kit/examples/banking77-labels.json`.

## Healthy calls and bars

The model must call each tool exactly once with the captured inputs and the tool result must satisfy:

1. `jev_rerank`: `details.top1 === true`, selected index is one of the two offered candidates, `details.model === "jev-1.13.0"`, and usage is present.
2. `jev_claim_check`: `details.verdict` is `supported`, `unsupported`, or `unsure`; `details.threshold === 0.5`; `details.model === "jev-1.13.0"`; and usage is present.
3. `jev_classify`: `details.verdict === "classified"`, `details.label === "card arrival"`, `details.model === "jev-1.13.0"`, and usage is present.

A healthy call counts only when the tool execution is successful and returns a structured result; a prompt acknowledgement or model assertion is not a call result.

## Refusal calls and bars

The model must call each tool exactly once with these known-bad inputs:

1. `jev_rerank`: 21 candidates. Expected `details.verdict === "not_run"`, `details.top1 === false`, and no Jev usage.
2. `jev_claim_check`: empty evidence. Expected `details.verdict === "not_run"`, no Jev usage.
3. `jev_classify`: one label. Expected `details.verdict === "not_run"`, no Jev usage.

These are deterministic preflight refusals. Any HTTP usage, model usage, or successful decision on a bad input fails the bar.

## Stop and boundary rules

- Stop after six tool executions, after a 401/402/403, or at the 600-second deadline. No retries inside the driver.
- The receipt stores only filtered RPC/tool frames, structured tool outputs, model/usage/latency fields, and SHA-256 hashes of prompt input paths. It does not store the API key.
- This measures one real OMP session and these public captured inputs. It does not prove fleet-wide L3, repeated-session reliability, or outcome value beyond these calls.

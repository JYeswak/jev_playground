# MASSIVE en-US local Clef-Flash intent measurement

Status: **UNAVAILABLE — INCOMPLETE_NO_VERDICT**
Reason: 551 valid Clef responses; the guarded request for `massive-1.1-en-US-test-3099` timed out after 30 seconds. One error row recorded; 402 rows not attempted. No retry, resume, or score.

Dataset: AmazonScience/MASSIVE 1.1; en-US; test; archive SHA-256 `4cba5faa11c71437928e17cb1b9b3d8b8e727e7ea363a3a9a8045e19c0491577`.
Clef model: `clef-flash` via `http://127.0.0.1:11300/jev/clef-flash/classify`; localbench request-id guard required.
Execution: concurrency 1, retries 0, no fallback; Jev arm NOT_RUN; experiment spend $0.00.

Frozen corpus SHA-256: `4909490e7a8efabfc4e97eee6a58bee04ac3d634cae02224f82ffdb9b9f9d5b1`
Frozen preregistration SHA-256: `4295ac4d88132b7919829fb67bb8d42debd8163ed0d8354e5b2eda27eed911d5`
Frozen spec SHA-256: `5ec621e64ca404f372619361da1044c7bd440c234d4570cb0b77fd045a32e3f9`
Runner SHA-256: `a31bc01472ed58cc7913b4aac37f7211cce5dad8942e6c15576799c79e9f6eb6`
Keyless preflight: 954 rows / 59 labels; 0 prior-corpus overlaps; identity `clef-flash`.

Per-row predictions, validated probability vectors, latency, and localbench request IDs are in `rows.jsonl`; every row carries the frozen runner hash `a31bc01472ed58cc7913b4aac37f7211cce5dad8942e6c15576799c79e9f6eb6` and `first_request_started_at_utc` `2026-10-06T20:18:12.877Z`, sourced from the localbench request ledger. The runner now records `run_py_sha256` and `row_started_at_utc` on each emitted row, including terminal errors. Utterance text remains only in the frozen public `corpus.jsonl`.
This is a descriptive Clef-only measurement. Jev was NOT_RUN; no paired, comparative, superiority, or deployment claim is made.

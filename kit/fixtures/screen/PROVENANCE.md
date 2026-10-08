# Screen fixture provenance

These files are byte-for-byte copies of recorded outputs from the jev-x1-injection-encoders-e2gp experiment; they were not typed or regenerated for the conformance harness.

- Source run: `work/x1-injection-encoders/PREREG.md`, frozen before scoring; code/preregistration commit `8f690b8443de38e3a036c2197a3399f2157796f2`.
- Jev answers: `work/x1-injection-encoders/answers-jev.jsonl`; live model `jev-1.13.0`, recorded in the 2026-10-05 run. The experiment made 447 bounded public-row Jev calls; its receipt records 204,847 input tokens and estimated spend `$0.008603574`.
- ProtectAI answers: `work/x1-injection-encoders/answers-protectai.jsonl`; local model `protectai/deberta-v3-base-prompt-injection-v2`, revision `90c9989b1a342275dd0d1a95aad283c04e075671`, one CPU thread.
- Authoritative result and boundaries: `EVAL.md`, entry `2026-10-05 jev-x1-injection-encoders-e2gp: ProtectAI fails paired tool-result bar`; detailed receipt `work/x1-injection-encoders/RECEIPT.md`.

The conformance copies match their recorded outputs (`cmp -s` on both pairs):

| File | SHA-256 |
|---|---|
| `answers-jev.jsonl` | `d8d23f04e40662d356b3bbfd46849e9b88070792456b7bf21cfd7a00d5640d07` |
| `answers-protectai.jsonl` | `d5b56b13ba660b119d829f2bef7acb6f1fd2466dc23ca4e2812bd18c5447e541` |

The records retain source ids, labels, model/status, predicted score/flag, and SHA-256 of each input; raw input text is not included. This is provenance for offline recorded-answer fixtures, not a fresh model run or a claim that the experiment's paired bar passed (the bar failed).

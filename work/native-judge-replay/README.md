# Native omp judge questions: local System One vs hosted jev-1.13.0

Parity rows for localbench's decision tier (beads `kit-auto-thinking-route-kmt`,
`kit-jev-tasks-local-zmm`), so the measurement is not rerun. Run 2026-10-01 by the jev conductor
(bead `jev-j4ci`); summary in `EVAL.md` ("native Jev turned on fleet-wide").

- `smart-stop-rows.jsonl`: omp's unexpected-stop Noul (`unexpected-stop-classifier.ts`) on 300
  real text-only terminal stops from 160 random omp sessions; local `nimble:latest`.
- `auto-thinking-level-rows.jsonl`: omp's auto-thinking `level` Choice (`auto-thinking/classifier.ts`,
  input passed through omp's `preprocessTinyMessage` rules) on 200 real user prompts; local
  `nimble:latest` and `tev1:latest`.

Fields per row: `item_id` (session file : entry id), `question`, `model`, `model_digest`,
`request_sha256` / `hosted_request_sha256` (sha256 of the sorted-key JSON body), `answer`,
`hosted_jev_1_13_0_answer`, `label` (always null: these native questions have no ground truth, so
the rows measure agreement with the hosted model, not accuracy), `wall_ms`, `hosted_wall_ms`, `ok`.
The prompts and messages themselves are private session text and are not committed.

Ollama 0.35.0, `http://127.0.0.1:11434/v1/systemone`, batch 1, no localbench lease (latency is
descriptive only: the box was shared). Results: smart stop agreement 0.653, kappa 0.073;
auto-thinking nimble exact 0.66 / within one level 0.77, tev1 exact 0.54.

# `jev` robot contract

`jev doctor --robot` emits one JSON object and exits:

- `0`: `{ "status": "READY", "model": "jev-1.13.0", ... }`
- `2`: `{ "status": "NOT_RUN", "reason": "no key", "model": "jev-1.13.0", ... }`
- `1`: broken or invalid invocation.

`jev ask choice|score|noul --state FILE --question FILE --robot` emits the client result object.
`jev rerank --query Q --candidates FILE --robot` sends one Choice over the candidate passages and emits the chosen candidate first, followed by the original input order. It does not claim a full reranking.
`--fake` uses the captured FiQA answer row under `kit/test/fixtures/rerank-fiqa-answer.json` and reports `model: "fake"`; it never contacts Jev. The example passages and IDs are copied from BEIR FiQA-2018 query `10034`, not typed. The measured design has no synthetic `none` candidate: no-answer behavior is represented by refusing malformed/unoffered answers, so the example intentionally contains only retrieved passages.
`jev classify --text T --labels FILE --robot` sends the captured Banking77 intent Choice: state `{"customer_message": T}`, 77 humanized labels with null descriptions, and the measured instruction. It passes Jev's confidence through without a threshold. `--fake` uses `kit/test/fixtures/banking77-answer.json` and reports `model: "fake"` without contacting Jev.
`jev verify --claim C --evidence FILE --robot` sends the captured SciFact Noul: state `{"claim": C, "evidence": text}`, the measured instruction and true/false criteria. It labels values `>0.5` as `supported` and values `<=0.5` as `unsupported`. `--fake` uses `kit/test/fixtures/scifact-answer.json` and reports `model: "fake"` without contacting Jev.
`jev score --text T --levels FILE --robot` sends the captured SST-5 Score: state `{"text": T}`, the measured instruction and five ordered level descriptions. It returns the selected integer level, its description, confidence and probabilities. `--fake` uses `kit/test/fixtures/sst5-answer.json` and reports `model: "fake"` without contacting Jev.

```bash
npm ci
npx --no-install tsc -p tsconfig.json
node bin/jev.mjs score \
  --text "it represents better-than-average movie-making that does not demand a dumb, distracted audience." \
  --levels examples/sst5-levels.json --fake --robot
```

The live model is always pinned to `jev-1.13.0` unless the caller explicitly supplies the client
model option in code. The CLI never prints the API key.

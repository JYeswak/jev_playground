# `jev` robot contract

`jev doctor --robot` emits one JSON object and exits:

- `0`: `{ "status": "READY", "model": "jev-1.13.0", ... }`
- `2`: `{ "status": "NOT_RUN", "reason": "no key", "model": "jev-1.13.0", ... }`
- `1`: broken or invalid invocation.

`jev ask choice|score|noul --state FILE --question FILE --robot` emits the client result object.
`jev rerank --query Q --candidates FILE --robot` sends one Choice over the candidate passages and emits the chosen candidate first, followed by the original input order. It does not claim a full reranking.
`--fake` uses the captured answer rows under `kit/test/fixtures/recorded-answer-rows.json` and
never contacts Jev. Example:

```bash
npm ci
npx --no-install tsc -p tsconfig.json
node bin/jev.mjs rerank --query "Which candidate answers the query?" \
  --candidates examples/rerank-candidates.json --fake --robot
```

The rerank verb refuses more than 20 candidates, malformed or unoffered answers, and OVER/NEAR
state-size preflights before spending a call. A successful result has `ok: true`; configuration,
transport, HTTP, and validation failures have `ok: false` or a nonzero CLI exit.

The live model is always pinned to `jev-1.13.0` unless the caller explicitly supplies the client
model option in code. The CLI never prints the API key.

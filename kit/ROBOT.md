# `jev` robot contract

`jev doctor --robot` emits one JSON object and exits:

- `0`: `{ "status": "READY", "model": "jev-1.13.0", ... }`
- `2`: `{ "status": "NOT_RUN", "reason": "no key", "model": "jev-1.13.0", ... }`
- `1`: broken or invalid invocation.

`jev ask choice|score|noul --state FILE --question FILE --robot` emits the client result object.
`--fake` uses the captured answer rows under `kit/test/fixtures/recorded-answer-rows.json` and
never contacts Jev. A successful result has `ok: true`; configuration, transport, HTTP, and
validation failures have `ok: false` and a typed `reason`.

The live model is always pinned to `jev-1.13.0` unless the caller explicitly supplies the client
model option in code. The CLI never prints the API key.

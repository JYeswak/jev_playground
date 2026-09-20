# Contract for taste-loop omp-jev-* packages

Copy `work/omp-jev-heckle/` exactly. Deviations break the lane.

## Files (exactly these)

- `package.json` — name, omp.extensions `./src/index.ts`, type module
- `src/index.ts` — default export factory
- `test/<name>.test.mjs` — node:test, same arms as heckle
- `README.md` — why Jev, stop-condition, decision kinds, NO-CLAIM
- `measure.mjs` — uses `work/jev-client/measure-kit.mjs` for noul packages; for choice packages print cases and call `askJevChoice` (do not invent a second kit)

## Hard rules

1. `import { askJev } from "../../jev-client/src/index.ts"` and/or `askJevChoice`. Never fetch.
2. Detectors from `../../taste-loop/src/detect.mjs`. Do not reimplement path/tool checks.
3. `pi.on(...)`; every handler `try/catch`; every path `return undefined`.
4. Never `{ block: true }`. Never throw into the host.
5. Decision type `com.zeststream.omp-jev-<name>.decision.v1`.
6. Kinds: `<name>_scored` | `<name>_error` and optional `<name>_regex` when a regex wins.
7. Error rows: no `probabilities` field at all. `failure` is the JevFailure name.
8. Unset key: `askJev` already returns `unconfigured` — do not special-case beyond recording the error row.
9. Export `QUESTIONS` (noul map) and/or `CHOICE` `{ instructions, classes }` so tests pin the wire.
10. timeoutMs 2500.
11. Questions are SHORT. No rationale in criteria. `none` is a first-class choice label where the machine is a choice.
12. Do not register in any profile. Do not edit `STATUS.tsv`, root `README.md`, `GATES.md`, `NEGATIVE_EVIDENCE.md`.
13. Tests mock `globalThis.fetch` like heckle. Pin `Object.keys(sent.questions)` or choice criteria labels.
14. Required test arms: ignore non-matching events (0 rows); unset key → error not pass; throwing fetch → error; 200 scores → scored; 200 without answers → error; appendEntry throw → undefined; exact questions on the wire.

## Host helper (copy)

```js
function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: {
      on: (_e, cb) => { handler = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
  };
}
```

For two events (`tool_call` + `session_stop`), store handlers by name:

```js
pi: {
  on: (e, cb) => { handlers[e] = cb; },
  appendEntry: async (type, data) => { rows.push({ type, data }); },
}
fire: (name, event) => handlers[name](event),
```

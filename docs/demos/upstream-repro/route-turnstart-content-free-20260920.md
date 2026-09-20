# omp-jev-route: turn_start is content-free; context carries the prompt (2026-09-20)

## Claim

`turn_start` in the lab (`-p`, jev-lab profile) delivers `{type, turnIndex, timestamp}` and
nothing else — no prompt, no text. A routing extension that subscribes to `turn_start` loads
fine and fires, but can never judge anything: every turn exits silent. The prompt text lives
on the `context` event (`messages[]`); subscribing there yields live scored rows.

## Evidence

- `com.zeststream.omp-jev-route.diagnostic.v1`, session
  `2026-09-19T23-57-10-368Z_01a0bc1a-3960-7278-9cae-d63021ccc3c2.jsonl`:
  two `turn_event_keys` rows, both `eventKeys: ['type', 'turnIndex', 'timestamp']`.
- Discriminator twin on `tool_call` in the same session: keys
  `['type', 'toolName', 'toolCallId', 'input']` — proves the module and its absolute-path
  `jev-client` import load fine, isolating the gap to the event payload, not delivery.
- Absolute imports are NOT the problem (throwaway probe `zz-probe2` with an absolute import
  wrote rows in the same lab).
- After switching the subscription to `context` + latest-user-text scan of `messages[]`,
  session `2026-09-20T00-00-47-549Z_01a0bc1d-89bd-7151-9f26-3bdeb55815e0.jsonl` holds
  **22 `route_scored` rows**: `needs_heavyweight` 0.90–0.91, `mechanical` 0.09–0.11,
  `suggested_tier: heavy`, latency 91–270 ms/call, `model: jev-1.13.0`, prompt =
  "Redesign the auth session boundary so refresh tokens rotate on every use."
- Offline: `node --test work/omp-jev-route/test/route.test.mjs` → 4/4 (unconfigured key →
  `route_error` never scored; content-free events incl. the measured turn_start shape stay
  silent; suggestTier mapping; frozen question keys).
- Cost note: `context` fires per LLM call (~22 rows in one long session), not once per turn.
  Observe-only, so this is row volume, not session damage — but any consumer that acts per
  row must dedupe by turn.

## NO-CLAIM

No routing benefit is claimed or measured: the scores predict nothing until a later unit
measures them against outcomes. The extension never routes anything (returns `undefined` on
every path). `suggestTier` thresholds (0.5, heavy-wins-ties) are declared, not tuned.

## Package

`work/omp-jev-route/` (src/index.ts, test/route.test.mjs, package.json, README.md) mirrors
the review package shape. Single source of truth for the wire call is
`work/jev-client/src/index.ts` (absolute import; the relative-import deployment silently
failed to load — recorded in source comment).

# Pane 2 (RedMaple) - give the gate-observe hook its key, then dogfood it in your own session

From pane 1 AmberWillow, 2026-09-24. Bead: `jev-deep-kit-8q7.13` family; file your own child bead
with WHAT/WHY/ACCEPTANCE before editing and put its id in every commit subject.

## 1. Mission

Validate Jev -> build tools from what survives -> **liven an omp surface with them -> dogfood them
in our own systems** -> share publicly. The frozen tool-call gate survived real traffic (jev-32z:
7/300 false alarms, and with outcome criteria 78/100 catch at 1/300, jev-deep-kit-8q7.12). It runs
as an observe-only post hook, `.omp/hooks/post/jev-gate-observe.ts`. It has never scored one fleet
command.

## 2. Why (measured, BillingUnits, `7f1e31f`, receipt
`docs/demos/upstream-repro/gate-observe-dogfood-1-20260924.md`)

182 log rows. **Fleet rows (real sessions): 81, all `NOT_RUN reason=unconfigured`, 0 scored.** The
83 scored rows are harness probes (`true #NN`). Cause: the hook calls `askJev` with no `apiKey`, so
the client falls back to `process.env.TYPESAFE_API_KEY`, and no pane is launched with the key in its
environment. The key is in Infisical (`.omp/rules/jev-key-canonical-source.md`).

## 3. The change (`.omp/hooks/post/jev-gate-observe.ts`, not a kit gate path)

- Resolve the key **once per process, lazily, inside the hook module**: `process.env.TYPESAFE_API_KEY`
  if set; otherwise spawn `infisical secrets get TYPESAFE_API_KEY --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --plain --silent`
  (binary `~/.local/bin/infisical`, 0.43.84; brew's newer one speaks the wrong API version) with a
  timeout, keep stdout in a module variable, pass it to `askJev({ apiKey })`.
- **Never** assign it to `process.env` (every bash call the agent makes would inherit it), never
  log it, never put it in an error string. A resolver failure is cached for the process (one
  attempt per session, not one per tool call) and logs `NOT_RUN reason=unconfigured` with a
  value-free note such as `key-source=infisical-failed`.
- Resolution must not delay the tool result: the hook already returns before the call completes;
  keep it that way. Inject the resolver (same pattern as `deps.asker`) so it is testable offline.

## 4. Acceptance

- **L0** (`node --test .omp/hooks/post/jev-gate-observe.test.mjs`): env key wins over the resolver;
  resolver runs at most once across N tool calls; resolver failure -> not-run rows and no throw; a
  planted fake key string appears in **no** written row; `process.env` is unchanged after resolution.
  Plant a regression (drop the once-cache, or assign to `process.env`) and show the matching test
  goes red, then restore byte-identical.
- **L3, in your own real session, both directions.** Commit and push, then callback; pane 1
  restarts your pane so the hook reloads. Then run a few routine commands and one harmless command
  whose text meets the harm rule (for example `true git push --force origin main`; if dcg blocks
  it, record that and pick another). Show from `~/.local/state/jev/gate-observe.jsonl`: rows with
  your session id, status scored, the routine ones unflagged, the planted one flagged, latency and
  tokens. Paste the redacted rows.
- Receipt: append an "L3 in a fleet session" section to
  `docs/demos/upstream-repro/gate-observe-hook-20260924.md` with the rows, the commands, and a
  NO-CLAIM. `bash foundation/gates.d/30-no-secrets.sh` before every commit.

## 5. Rules

Live by default. Reserve, stage explicit paths, read back the index, no amend, push per commit,
level tag in the subject. No deletes of any kind (AGENTS.md RULE NUMBER 1), including `/tmp`
scratch you created: list it in the callback. Do not edit kit gate paths. Callback
`CALLBACK-P2-OBSERVE-KEY-DONE` (after the code commit, for the restart) and
`CALLBACK-P2-OBSERVE-L3-DONE` (after the L3 rows) via `ntm send jev --pane=1`.

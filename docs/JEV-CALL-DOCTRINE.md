# Jev-Call Doctrine (mined from sr @abf909d, P2 U3 + issue #4)

Portable rules for how WE structure Jev calls. Source: Jeffrey's shipped ranker
(`skillranker/`, read-only vendored) — every rule below names the mechanism, not
just the file. Full mining with outputs: `docs/demos/upstream-repro/sr-advise-20260920.md` U3.
Live proof on this machine: 4 requests, jev-1.13.0, 10→1 cut + measured abstain.

## 1. Two stages, never one giant question

- **Wide** (`src/jev/wide.rs`): one request over ALL admitted candidates. Cheap
  excerpts (description ≤160 scalars, `frontmatter.rs:28`), opaque option keys.
- **Gate-mean** (`wide.rs:356-357`): `needs_skill = (specialized + material +
  (1 − suffices)) / 3`. Below gate (default 0.30) → abstain `low-need`, no rerank.
- **Rerank** (`src/jev/rerank.rs`): second request over the shortlist only, with
  full descriptions (≤1000) + body excerpts (≤700). One Choice + one `fits::<opt>`
  Noul per candidate.
- Copy the shape; tune the caps to our token budget. One request per stage keeps
  cost attributable (our run: 5493 in / 554 out for wide+rerank).

## 2. Every Choice carries a typed none-sentinel

- Option `__none__` with a written description ("No listed skill adds useful
  guidance", `wide.rs:46`), resolved through the local option map like any
  candidate (`resolution.rs:611-612`).
- Publish rule: each candidate must **individually** beat `__none__`
  (`replay.rs:672-676`) AND clear the fits floor (`pipeline.rs:4054-4063`).
  Measured: 10 candidates → 1 published, 4 wrongs at exactly 0.0.
- Never publish "argmax of a bad lot". The sentinel is what makes abstention a
  judgement instead of an error path (our live negative: abstain/`low-fit`,
  none_p 1.0, after the FULL two-stage pass — not a shortcut).

## 3. Separate "should I act" from "what"

- Three oriented Noul gates (`wide.rs:37-52`): is context sufficient / would help
  materially improve / is a specialized method wanted. They route (rerank or
  not); they never select.
- `phase` Choice (8 fixed phases, `wide.rs:56-71`) is recorded telemetry, not a
  selector. Optional `stuck` Noul defaults OFF (`pipeline.rs:1637-1638`).
- No Score primitive anywhere — "intentionally unavailable" (`jev/codec.rs:68-70`).
  Choice + Noul cover selection + gating; do not invent a third shape.

## 4. State discipline

- One state object, same for every question in the request: profile, quality,
  harness, latest request, project signals, recent messages, session state.
- Skill/content text is UNTRUSTED: redacted before truncation, embedded only as
  JSON-quoted data after fixed instructions, never as instructions
  (`rerank.rs:7-11`). Answers resolve only through the local map — no response
  text ever becomes a name, path, or command.
- Hard budgets with a fixed trim order; candidates + sentinel are never dropped
  (`wide.rs:8-12`). Caps: 96 KiB/request, ≤254 real options, 1≤top≤shortlist≤32.

## 5. Refusal taxonomy (copy the shape)

- 25 typed kinds in 5 exit classes (`output/mod.rs:126-156`): Usage/2, Session/3,
  Provider/4, Roster/5, Timeout/6, Input/7, Privacy/8, Storage/9,
  ProviderContract/10, CacheMiss/11. Observed live: empty-roster/5,
  unusable-roster/5, cache-miss/11, authentication/4.
- Diagnostics never echo input (`output/mod.rs:158`). A refusal names the
  category + the next command, never the payload.

## 6. Replay testing (the capability we lacked)

- `--save-case`: owner-only (0600) ReplayCase = captured request + recorded
  wide/rerank responses + local evidence + historical decision
  (`replay.rs:102-111`). `replay FILE [--policy] [--compare-policy]` re-executes
  policy offline, $0 (`replay.rs:364-365,434-435`). Proven: both our saved cases
  replay exit 0.
- Every Jev integration we ship saves cases from live runs and replays them in
  CI. Policy changes are compared, not eyeballed.

## 7. Ledger (what to persist, and what it buys)

- SQLite tables (`storage/ledger.rs:151-290`): session_cursors, roster_snapshots,
  ranking_events, ranking_candidates (wide|rerank), provider_attempts
  (fingerprint-keyed → response cache), observations (attempted|loaded|censored),
  judgments (useful|harmful|neutral), feedback_proposals, calibrations
  (train|validation|holdout). 30-day retention, quota'd.
- What it buys the second run: snapshot reuse + changed detection, cache hits
  that skip the provider, session resume. (Priors exist; keep weight 0 until
  earned — `w_prior` defaults 0.0, `config.rs:883`.)

## 8. Defaults table (starting points, all flaggable)

top 5 · shortlist 8 · gate 0.30 · fits 0.30 · w_fit 1.0 / w_prior 0 / w_phase 0
(`config.rs:878-884`, `wide.rs:26-28`). Override per integration with measured
reason; never lower a gate to make a demo pass.

## 9. What we DELIBERATELY do not adopt

- **Global withhold** (`resolution.rs:530-540`): one enumeration gap revokes ALL
  authority → empty roster on default-shaped stores. Filed upstream as issue #4;
  until fixed, sr cannot route for us (P3 warned directly). Our replacements use
  per-name scoping (the pattern his read-failure path already uses, `:541-548`).
- **Provisional visibility**: rank-time labels without conformance evidence.
  Our seams name their evidence or say nothing.
- **Claude-only harness**: discovery follows one layout; our integrations declare
  their adapter contract up front instead of inheriting his.

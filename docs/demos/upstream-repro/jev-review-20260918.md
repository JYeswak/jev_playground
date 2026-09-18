# `jev-review`: an upstream scorer that already refuses to score

Upstream: `jev-review`, cloned here, untouched. A local MCP server that gives Claude Code, Codex,
Cursor and OpenCode structured quality scores, powered by Jev.

## What was run

```bash
cd jev-review && npm test
```

```
13 tests, 13 pass, 0 fail, 0 skipped
```

**Zero skipped matters here.** Every other keyed repo in this tree hides its live tests behind a
skip, so a keyless `npm test` reports green on a subset. This one's suite is entirely offline, so
13/13 is the whole suite rather than the part that runs without credentials.

## The design detail worth taking

Its per-metric contract returns, for each dimension:

- an independent **1–10 score** and a **0–1 confidence**
- **`{ "applicable": false }`** for dimensions the supplied context cannot support
- prioritized weak dimensions and **coarse predefined rubric hints, explicitly not generated
  root-cause explanations**
- per-metric deltas, improvements, regressions and unresolved weaknesses against a previous eval

**`applicable: false` is a refusal-to-score primitive**, and it is the same shape this repo had to
add to its own gate runner today. `foundation/gates.sh` gained a third state, `UNMEASURED` at exit 7,
after a stage that could not reach a verdict was laundering that into a PASS. Upstream shipped the
equivalent as part of its scoring contract rather than as a repair.

The second clause is the one this lane keeps relearning: **hints, not generated explanations.** A
scorer that explains its own score invites the reader to grade the explanation instead of opening
the control, which is precisely the failure this conductor has recorded roughly a dozen times.

## Why it is not simply adopted here

It scores *code quality* for an agent iterating on a change. This lane's open scoring problem is
different: whether a **claim** opens in the **receipt cited for it**, which `jev-mcp`'s `jev_verify`
addresses more directly and which is already recorded as the better candidate
([`jev-mcp-20260918.md`](jev-mcp-20260918.md)). Running both and taking neither yet is the honest
position; two scorers wired in on the same day, by the person who wants them to work, is how a lane
acquires instruments that gate nothing.

## No-claim

- **13 offline tests are not a measurement of its scores.** Nothing here evaluates whether its 1–10
  dimensions correlate with anything, and no live call was made.
- `dist/` and `node_modules/` ship in the clone, so a **build from source is not proven**.
- The `applicable: false` contract is read from its README and its tests, **not exercised against a
  real context that triggers it**.
- Not installed into this harness, and not recommended for installation in this receipt.

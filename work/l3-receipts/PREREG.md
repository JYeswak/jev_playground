# L3 receipt parser and planner contract

Scope: `jev-grzn.1`, original parent snapshot 2818. This freezes the read-only parser/planner interface, not a live experiment or a session-launch authorization. Its command never starts OMP, calls a model, flips a switch, changes an inventory declaration or writes a receipt. Fresh-session execution, source-derived per-turn bounds, isolation, memory seeding and non-author live acceptance remain the separate original parent obligations.

## Evidence is not a claim

`receipts.jsonl` is an initially empty observation ledger: no L3 pair has been collected by this unit. Empty or missing evidence cannot yield a passing audit for a declared-ON decision surface. The existing fleet inventory remains authoritative and is never rewritten by the checker. `PASS` from this program means only that supplied artifact references and pinned predicates agree; output always says `live_l3_proven: false`. It does not certify freshness, loaded-session identity, a meaningful experimental predicate, quality, parity or value.

The tests derive log observations from the already recorded gate answers in `kit/fixtures/gate/answers-jev.jsonl`. Their session reference is explicitly synthetic. They exercise parsing, source binding and refusal only, never live L3 behavior.

## Frozen budget input

A caller supplies either a JSON file or exactly one fenced `json` block in a preregistration Markdown file, schema `jev-l3-budget.v1`. Required fields:

| Field | Meaning / refusal boundary |
|---|---|
| `surfaces` | Object keyed by exactly the inventory's ON decision surface IDs. IDs must be strings with non-whitespace content and must be unique; missing/empty/whitespace-only identity refuses before planning. A blank declaration is never an identity alias. No hard-coded list, missing surface or extra surface. Infra decisions beginning with `none` are excluded. |
| Each `K_s` | Explicit nonnegative integer per scripted session; absence, booleans or a guessed default refuse. The actual code-path upper-bound derivation belongs to the original budget/execution acceptance, not this parser. |
| Each `B_s` | Must equal planned session count multiplied by `K_s`; never silently repaired. |
| Each `model` / `model_field` | Explicit answering-model pin and its field in the referenced log row. Session-model fallback cannot impersonate a pinned model. This does not authorize changing the parent's model policy or a shared role. |
| Each `positive` / `negative` / applicable `load` | Object with `field` and `equals`, pinning the observable JSON log predicate before receipt evaluation. The experimental meaning of the predicate requires independent review. |
| `total_budget` | Explicit integer equal to the sum of all `B_s`; missing or inconsistent totals refuse. |
| `spend_estimate_usd` | Explicit finite nonnegative pre-run estimate; it is not observed spend. |

The profile list comes from `expected.json`. Native surfaces require positive and negative cases in each profile. Project hooks, extensions, rules and global surfaces require positive and negative cases in `default` plus one load case in each remaining profile. Fleet observations instead have positive and negative `hub` cases with `runner: hub-observation`; they never schedule profile RPC or profile load cases. Other planned records use `runner: omp-rpc`. These are plan descriptions only, never executed by this program. There must be at least one ON decision surface; zero-population coverage never passes.

No live per-surface budget is declared in this parser-contract document. In particular, it contains no executable JSON budget and must be refused as `--budget` input until the actual source-derived plan is separately frozen under `jev-grzn.2`. No zero/dummy bound or expenditure is substituted. This is deliberate input refusal, not permission to launch a session or reduce the parent budget bar.

## Receipt input

Each `jev-l3-receipt.v1` JSONL row names `surface`, `profile`, `case`, `model` and finite nonnegative `spend_usd`. It binds a `session_file` by `session_sha256`, and a `log_file` plus positive 1-based `log_line` by `log_sha256` (SHA-256 of that line excluding CR/LF). The answering model and case predicate must match the actual referenced JSON log row. Declared success in a receipt is never a substitute for the log row.

All evidence must resolve inside the explicit `--evidence-root`; path escapes and unavailable inputs fail. The audit checks the matching first-column surface ID or inventory name in the supplied AGENTS Markdown table, and requires an explicit ON status. Missing, ambiguous or OFF declarations fail rather than inferring that a grouped prose table covers an individual surface. Contradictory inventory ON/OFF verdicts refuse before planning. Duplicate, unknown-surface and wrong-profile receipts fail.

## Commands

- `uv run --no-project --no-config python3 work/l3-receipts/run.py --budget <frozen-budget> --plan --json`: validates input and arithmetic, emits a plan, makes zero model calls.
- `uv run --no-project --no-config python3 work/l3-receipts/run.py --budget <frozen-budget> --inventory <inventory> --receipts <ledger> --agents <declarations> --evidence-root <authorized-root> --json`: reads and grades artifacts; exits 0 only if every required supplied pair/load record matches, otherwise 1.
- `uv run --no-project --no-config python3 -m unittest work/l3-receipts/test_run.py -v`: observed-source synthetic positive control plus missing-log, missing-receipt, missing-budget, state/model/hash/effect mismatch and profile-plan controls.

No live model run, existing session restart, service activation, secret read, shared config edit or ON/OFF change is authorized or performed by these commands. The parent's requirement to independently run fresh live both-ways evidence is unchanged.

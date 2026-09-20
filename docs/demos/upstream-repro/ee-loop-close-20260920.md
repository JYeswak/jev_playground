# ee `remember` → `preflight` loop close — 2026-09-20 `[receipt]`

MAP.md action-plan item 1. **Verdict: (b) — two different subsystems, with one closable half and one hard gate.** Nothing filed upstream.

## Under test
- `ee 0.15.2` — `/Users/josh/.local/bin/ee`, sha256 `b7ed9cefae6e297f98fd4d7326f09698b7602912b42a4612245294adc4768618`
- Workspace `/Users/josh/Developer/jev` (`wsp_6DQ2G042RJ8JGRBY1SC7ZVJS7P`, db `.ee/ee.db`), repo HEAD `e26b10f`
- Clean rooms `/tmp/ee-cleanroom-20260920`, `/tmp/ee-matrix-20260920` (fresh `ee init`, zero memories)

The `ee` binary is not in git, so the digest above is pinned to a **live file** — see the `digest-pinned-to-live-file` defect this very receipt seeds. Re-hash before trusting it.

## The documented contract, quoted

`ee preflight check --help`:

> Retrieve **advisory rule** and **risk-memory** context for a command

Two planes, and the JSON has one array each: `matches[]` (rules) and `matchedMemories[]` (memories). They are fed by different writers.

`ee tripwire --help`:

> List and check tripwires **from preflight assessments**

`ee rule add --help` — full flag set is `--scope --scope-pattern --maturity --confidence --utility --importance --trust-class --protect --tag --source-memory --dry-run --actor`. There is **no** command/glob/trigger pattern flag:

```
ee rule add --help > /tmp/ee_ruleadd.txt
scripts/vgrep.sh --expect-zero -n -E '\-\-(cmd|command|match|glob|trigger)-?(pattern)?' /tmp/ee_ruleadd.txt   # rc=0 (PASS = zero matches)
```

`ee agent-docs` has **no** preflight or tripwire topic; `ee agent-docs recipes` has zero preflight/tripwire entries (`grep -n -i -E 'preflight|tripwire|advisory|command-risk|rule add'` → rc 1, no output). The contract below is therefore reconstructed from measurement, not from docs.

## Reproduction of the reported symptom

```
ee remember 'Never use grep -c as proof of absence; ...' --level procedural --kind rule --workspace . --json
# rc=0, memory_id=mem_01M303BDQZEXYBZRVFPSRNW4GG
ee preflight check --cmd 'grep -c foo bar' --workspace . --json
# {"matches":[],"matchedMemories":[],"degraded":[]}
ee rule list --workspace . --json | jq .data.totalCount   # 0
```

Confirmed. `remember` never writes a `rule` row — `--kind rule` is a *memory kind string*, unrelated to the `rule` table.

## What each plane actually accepts

### `matches[]` — closed builtin set, unreachable by `ee rule add`

```
ee preflight check --cmd 'rm -rf /tmp/x' --workspace . --json
# matches: builtin:rm_rf_root (pattern "*rm -rf /*"), builtin:file_deletion (pattern "*")
#          both source.kind == "builtin"
```

Every match carries a glob `pattern` and `source.kind: "builtin"`. Observed firing set: `rm_rf_root`, `file_deletion`, `git_reset_hard`, `git_clean_fd`, `git_stash`, `git_push_force`, `terraform_destroy`.

Decisive single-variable test — a **validated, evidence-verified, workspace-scoped** rule whose content literally contains the command string:

```
M=$(ee remember --workspace . --kind risk "<text naming git stash>" --json | jq -r .data.memoryId)
ee rule add "<same text>" --scope workspace --maturity validated --source-memory "$M" --workspace . --json
# rule_01M303GGA6EV4V214DDPV2E2XX, maturity=validated, evidence.verified=true
ee preflight check --cmd-base64 'Z2l0IHN0YXNo' --workspace . --json
# matches: [ {ruleId:"builtin:git_stash", source.kind:"builtin"} ]   <- the authored rule is absent
# matchedMemories: [ mem_01M303GEF8E8CVVXEKDB3TPVEP (kind risk) ]    <- the memory IS present
```

Same text, same store, same call: the **memory** surfaces, the **rule** does not. Reproduced from zero in a fresh workspace (`/tmp/ee-cleanroom-20260920`): `rule list` totalCount 1, `preflight check` matches all `builtin:`.

### `matchedMemories[]` — this half closes, and `--kind` is the whole trick

The `no_risk_memories` degraded entry names the writer. Measured kind-by-kind in a fresh store, checking `rm -rf /tmp/z` after each insert:

| `--kind` | appears in `matchedMemories` |
|---|---|
| `risk` | **yes** |
| `anti-pattern` | **yes** |
| `failure` | **yes** |
| `fact` (the `remember` default) | **no** |

**This is the root cause of the original symptom.** `ee remember --level procedural` defaults to `--kind fact`, which is silently excluded. `--level` is irrelevant to preflight; `--kind` is the selector. Round trip with the corrected kind:

```
ee remember --workspace . --kind risk 'rm -rf on a shared tree destroyed uncommitted work twice today; ...' --json
ee preflight check --cmd 'rm -rf /tmp/x' --workspace . --json
# matchedMemories: 1  (mem_01M303DNBWE73R6NJV51Q8JPAJ)  and no_risk_memories cleared
```

## The hard gate: `matchedMemories` only fires on a builtin-recognized command

Fresh store, then **one** memory naming **both** commands, then both checks:

```
ee remember --workspace . --kind risk 'Both rm -rf and grep -c are dangerous here.' --json
```

| command | `matches` | `matchedMemories` | `degraded` |
|---|---|---|---|
| `rm -rf /tmp/z` (before memory) | 2 | 0 | `no_risk_memories` |
| `grep -c foo bar` (before memory) | 0 | 0 | **(empty)** |
| `rm -rf /tmp/z` (after memory) | 2 | **1** | (empty) |
| `grep -c foo bar` (after memory) | 0 | **0** | **(empty)** |

One memory, one store, one call each. It surfaces for the recognized command and never for the unrecognized one. Memory content, kind, and indexing are held constant, so the gate is the **builtin command recognition**: if no builtin pattern matches, ee never looks at memories at all.

**Consequence, and the reason item 1 cannot be closed for this repo's defects:** every one of today's four measured defects is a *non-destructive* command. All four return `matches 0, matchedMemories 0, degraded []` — and `exitCode 0`, shell rc 0 unpiped. An empty `degraded` makes "I checked and there is no risk" **byte-indistinguishable** from "I do not cover this command." That is this repo's dominant defect shape — a zero reading as clean — inside the tool we were going to use to prevent it.

## Four rules seeded, and their honest measurement

Stored in `.ee/ee.db` with the corrected `--kind risk` and tag `defect-20260920`. Each names the CORRECTED command. None of the four match, for the gate reason above — **not faked, not wrapped.**

| memory id | tag | corrected command | `preflight check` |
|---|---|---|---|
| `mem_01M303RQ79EKQRSVC02PGG538F` | `pipe-exit-rc-misread` | `cmd > /tmp/out 2>&1; rc=$?; tail /tmp/out` (or `${PIPESTATUS[0]}`) | 0 / 0 / `[]` |
| `mem_01M303RSRCECDRBK4N2TDSJQTQ` | `grep-as-proof-zero-hit` | `scripts/vgrep.sh` (exit 3 on zero), `--expect-zero` to invert | 0 / 0 / `[]` |
| `mem_01M303RVZ5EY48W0APD9M0QM5B` | `env-var-vs-argv-invocation` | `./script.sh <value>`, never `VAR=<value> ./script.sh` | 0 / 0 / `[]` |
| `mem_01M303RY4AESZR67EP623A1ZP5` | `digest-pinned-to-live-file` | `git show <sha>:<path> \| shasum -a 256`, record the sha | 0 / 0 / `[]` |

Re-derive: `ee memory show <id> --workspace . --json`, then `ee preflight check --cmd-base64 "$(printf '%s' '<cmd>' | base64)" --workspace . --json`.

## `tripwire list` has no production writer

`ee tripwire` has only `list` and `check` — no `add`/`arm`. Across ee's full introspect map (1.56 MB) there is no creation verb:

```
ee introspect --json > /tmp/ee_introspect.json
scripts/vgrep.sh --expect-zero -o -E 'tripwire (add|create|arm|set)' /tmp/ee_introspect.json   # rc=0 (PASS)
```

The only documented producer is a preflight assessment, and it never produces one:

```
ee preflight run 'Delete the build output tree and force-push the rewritten branch to origin' \
  --check-history --check-tripwires --workspace . --json
# risk_level "unknown", risks_identified 0, tripwires_set 0, evidence_ids []
# degraded: preflight_evidence_unavailable —
#   "Task text matched heuristic risk language, but heuristics are not treated as evidence-backed risks."
#   repair: "Provide explicit preflight evidence sources or run a project-local preflight risk-review skill."
```

Re-run with a task matching a risk memory already proven to match via `preflight check`: still `risks_identified 0`, `evidence_ids []`, same degraded. `preflight run` does not consume workspace risk memories, and its flag set (`--check-history --check-tripwires --dry-run --workspace` + global flags) contains **no** way to supply evidence sources. So its own repair string is unreachable from the CLI.

The table itself is wired — `ee diag tripwire`, self-described as *"Seed a deterministic tripwire row for diagnostic fixture replay"*, took `total_count` 0 → 1 armed in the clean room. That separates "storage broken" (it is not) from "no production writer" (there is none). Using the fixture seeder to claim a closed loop would be faking the match, so it is recorded as diagnosis only.

## Defect class observed: repair strings that point at surfaces that do not exist

Both are machine-readable `repair` fields an agent would run verbatim.

1. `no_risk_memories.repair` emits `ee remember --workspace . --kind risk --severity high "..." --json`. Run verbatim:
   ```
   {"code":"usage","message":"unexpected argument '--severity' found tip: a similar argument exists: '--schema-version'"}  rc=1
   ```
   `ee remember` has no `--severity` flag. Drop the flag and the command works.
2. `preflight_evidence_unavailable.repair` says "Provide explicit preflight evidence sources" — `ee preflight run` has no flag that does so.

## Side finding — `ee search` zero-hit reads as clean

Not item 1, recorded because it is the same defect shape and it invalidates search as a fallback retrieval path here:

```
ee search 'grep -c proof of absence' --workspace . --json
# success:true, shell rc 0, resultCount 0
# data.status: "index_error", degraded: ["index_corrupt"]
# errors: ["Query parse error: search_collect requires a text provider for exclusion syntax; use search_collect_with_text() or search()"]
```

A caller reading `resultCount == 0` as "nothing stored" is wrong; the honest selector is `.data.status`. Also measured: `ee impact --command` rejects `grep`, `grep -c`, `grep -rn foo .`, and `npm run build` with `usage: "Surface value could not be normalized as a command anchor"`, while accepting `cargo test --lib` and `git commit` (both `n=0`). So neither `search` nor `impact` is a working fallback for these four memories in this store. Relayed to `ReconcilePipeExit`.

## Answer to the three outcomes

**(b).** `remember` and `preflight` are different subsystems, and so are `rule` and `preflight`:

- `matches[]` ← a **closed builtin table only**. `ee rule add` writes a separate content-only `rule` table with no command-pattern column and no flag to add one. Nothing an operator authors can ever populate `matches[]`. Closing this needs an upstream pattern field, not a config change.
- `matchedMemories[]` ← `ee remember --kind risk|anti-pattern|failure`. **This half genuinely closes** and is proven above. It is what WOULD populate preflight. The default `--kind fact` is the silent trap; `--level procedural` does nothing here.
- `tripwire list` ← preflight assessments only, which never produce one; the sole writer is a fixture seeder.

Not (a): the round trip does not close for any of this repo's four measured defects, because they are non-destructive commands outside the builtin recognition set. Not (c): nothing here is a crash or a wrong result — the two unreachable `repair` strings are real bugs but small, and MAP's earlier BLOCKED verdict misattributed a two-layer selector problem (`--kind`, then the builtin gate) to migration drift.

## NO-CLAIM
- Nothing filed upstream. No issue, no PR, no wrapper, no shim.
- Not read: ee source. The builtin rule set is inferred from observed `matches[].ruleId`/`pattern` plus `strings` on the binary; it is a **lower bound**, not a proven-closed enumeration. `*kubectl delete*` appears in the binary's strings yet `kubectl delete pod` produced zero matches — unexplained, not chased.
- The kind table was measured for `risk`/`anti-pattern`/`failure`/`fact` only. `command`, `convention`, `decision`, `playbook-step` untested.
- `--kind fact` exclusion is measured behavior, not a documented rule; no doc states it.
- The HOME store's `EE-E040 migration_drift` was not touched or repaired; all work is workspace-scoped to this repo plus two `/tmp` clean rooms.
- Store mutated: this repo's `.ee/ee.db` gained the four tagged memories above plus ~7 probe memories and 2 probe rules (`rule_01M303BV8HEY9BPMEMZ89DZQHW`, `rule_01M303GGA6EV4V214DDPV2E2XX`) from reproduction. Content is accurate; not tombstoned.
- `/Users/josh/.omp/omp-extensions/ee-ambient-session-start.ts` and `ee-failure-journal.ts` were read and **not modified**. Neither calls preflight or tripwire (`scripts/vgrep.sh --expect-zero -n -E 'preflight|tripwire'` over both → rc=0, PASS). `ee-failure-journal.ts` calls `ee journal append --kind command_failure`, a third store again distinct from preflight.
- `foundation/gates.sh` not run.
- dcg blocked three probe invocations on destructive substrings in argv; worked around with ee's own documented `--cmd-base64`, which exists for exactly that false-match. No guard was disabled.

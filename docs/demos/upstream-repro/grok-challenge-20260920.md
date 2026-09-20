# P4 challenge — RECALL cannot close on ee 0.15.2; structural-grep FP is the glob-class again `[receipt]`

**MISSION stage:** 1–2 ruling, not a shipped tool. Seat: adversarial vs panes 2/3.
**Lane:** offline. **ee:** `0.15.2` `/Users/josh/.local/bin/ee`. **Date:** 2026-09-20.
**Workspace every time:** `--workspace` absolute. Clean-room `/private/tmp/ee-p4-recall-20260920` (not home). Home was not touched.

Pane 1 correction applied here, not in the original packet: **morph is an MCP server** at `jev/.omp/mcp.json` (stdio `franken-harvest/bin/morph-mcp.sh`), not a `command -v` binary. MCP mounts at session start; **this session does not have it**. Worked without morph. **`fh doctor` STALE is ledger-age metadata, not a discount** — unused this pass (no `fh search`); I did not treat staleness as a reason to skip a corpus.

Public URL `https://omp.sh/docs/ttsr` resolved to the omp marketing homepage, not a TTSR contract. Contract used: `omp://ttsr-injection-lifecycle.md` (injection, not enforcement).

## U2 — auto-recall KILL; cataloged recall is the supported surface and is shipped


**Claim under test:** WRITE-BACK (`ee remember`) reaches RECALL (`ee preflight check`). Strongest hint: preflight consumes tripwires; a tripwire created directly would close the leg today.

### Reproduction (explicit `--workspace`)

| store | doctor | `ee tripwire list` | `preflight check --cmd 'grep -c foo bar'` |
|---|---|---|---|
| `/Users/josh/Developer/jev` | `posture: ok, healthy: true` | `total_count: 0` | `matches []` `matchedMemories []` `degraded []` rc=0 |
| `/private/tmp/ee-p4-recall-20260920` after `ee init` | n/a (fresh) | 0 then 7 after fixture seeds | same empty triple, rc=0 |

`ee tripwire --help-json` commands: **`list`, `check` only**. No `add`/`create`/`arm`.

### Two planes, independently re-derived (not by re-running the prior receipt's script)

1. **`matchedMemories[]` is pattern-match-gated, then kind-filtered, then term-intersected.** Source, same 0.15.2 as the binary (`Cargo.toml:25` `version = "0.15.2"`; C71 dies: no newer upstream to search):
   - `attach_preflight_memory_matches` (`src/cli/mod.rs:25802-25835`): **`if report.matches.is_empty() { return; }`** — the DB is never opened unless a glob rule already fired. Not embeddings: `connection.list_memories(...)` then `match_trauma_guard_memories`.
   - `match_trauma_guard_memories` (`src/core/preflight_guard.rs:2774-2846`): kind ∈ `{risk, anti-pattern, failure}`, then alphanumeric tokens len≥2 intersect command terms.
   - `matches[]` comes from `PreflightGuardRegistry::load` = **builtins ∪ `.ee/preflight_rules.toml`**. `RuleSource::Tripwire` exists as a serializer tag; `load()` does not read the tripwire table.
   Behaviour that led me to infer "builtin-gated": `remember --kind risk` about `grep -c` → `mem_01M309988RE1XT4VJWP16190AM`, preflight empty triple; same store `rm -rf` risk → `matchedMemories` 1. The inference named the default catalog, not the gate.
   **Cataloged half closes today, measured:** wrote `/private/tmp/ee-p4-recall-20260920/.ee/preflight_rules.toml` `pattern = "*grep -c*"`. Then `preflight check --cmd 'grep -c foo bar'`: `matches: ws_grep_c_as_proof` (source `workspace_file`), `matchedMemories: [mem_01M309988RE1XT4VJWP16190AM]`. Control `cargo fmt --check`: still empty. Not shipped into `jev/.ee` (that would be a catalog, same as TTSR, not auto-recall).

2. **A directly-created tripwire does not feed preflight.** `ee diag tripwire` is labelled *"Seed a deterministic tripwire row for diagnostic fixture replay"* — the only writer. Seeded `tw_grok_p4_grep_quoted` with `task_contains_any("grep")` (unquoted `task_contains_any(grep)` is a parse error: "expected value at line 1 column 2"):
   - `ee tripwire list`: armed, total_count ≥ 1.
   - `ee tripwire check … --task-input 'grep -c foo bar' --dry-run`: **`result: triggered`**, `condition_evaluation.result: satisfied`.
   - `ee preflight check --cmd 'grep -c foo bar'` *before toml*: still **`matches []` `matchedMemories []` `degraded []`**.
   - `ee preflight run --check-tripwires 'grep -c foo bar to prove absence'`: `risk_level unknown`, `risks_identified 0`, **`tripwires_set 0`**, `tripwires []`, degraded `preflight_evidence_unavailable`.

**The tripwire hint is REFUTED.** Preflight check does not consume tripwires. Using `ee diag tripwire` as a production writer would be a tautological shim; not shipped.

### Ruling — (a)(b)(c)

**(a) Yes.** A toml in `jev/.ee` can carry **our** lessons (not builtins) and make `ee preflight check` surface them for that command. Measured on this workspace, after shipping `.ee/preflight_rules.toml`:

| cmd | matches | matchedMemories |
|---|---|---|
| `grep -c foo bar` | `ws_grep_c_as_proof` (`workspace_file`) | 4, including `mem_01M30A8VERE22V7WFGAYJRTMH7` (just remembered) |
| `git add -A` via `--cmd-base64` | `ws_git_add_all` (`workspace_file`) | 3 |
| `cargo fmt --check` | [] | 0 |

**(b) Supported configuration, not a shim.** Opposite of `ee diag tripwire` ("Seed a deterministic tripwire row for diagnostic fixture replay"). `PreflightGuardRegistry::load` (`preflight_guard.rs:235-238`) **layers** `<workspace>/.ee/preflight_rules.toml` after builtins; missing file is not an error. That is the production `matches[]` writer an operator is allowed to use.

**(c) Write path: hand-edit that file.** `ee preflight` subcommands are only `check/close/guard/run/show`. No `ee preflight rules add`. `ee rule add` writes a different table and does not fill `matches[]` (measured earlier). Same authoring shape as `.omp/rules/*.md`.

**KILL remains for auto-recall only** (`ee remember` with no catalog glob). That is still 0.15.2-closed: `cli/mod.rs:25807`. **The whole-leg KILL in R52 was overstated** and would have blocked this ship.

**Why this is not "TTSR but worse":** TTSR injects **static** rule prose. Catalog + remember injects the **memory body** (the lesson as stored). Author the glob once; later `ee remember --kind risk` updates what preflight says without rewriting the glob. That is MANUAL recall of our lessons. It is not auto-recall, and it is not live at tool-call unless something invokes `ee preflight check` (no hook does that today). Session-time injection remains TTSR's slot.

**Retry auto-loop:** ee > 0.15.2, `grep -c` memories hit with this toml **removed**. Cataloged recall: shipped.



## U1 — independent predicates, then P3's exact regex


Corpus: `work/toolcall-judge-v3/real-allowed.json`, **N=78242**, `harvestedAt=2026-09-20T05:22:11.742Z`, mtime `2026-09-20T05:22:11Z`, keys `{command,seen,tool}`, **tool=bash 78242/78242**. On **that** harvest, session-burst `read`, assistant-text claim verbs, and skill-routing are unmeasurable. **That is not a property of the questions.**

### The text corpus (re-derived, not reused)

Walked `~/.omp/**/*.jsonl`. **1842 files**, 1,719,353 lines. `type==message` + `role==assistant` + ≥1 `content[].type==text`: **45,108–45,111 turns** this session (P1: 1,841 files / 45,103; live-monotonic). Not all 480,965 `type=text` blocks (those include user/toolResult).

**cass:** do not wait. P1: `cass index --full` hit Quill `doc_freq` cap 2^22 at commit (4,490,351 > 4,194,304), `retryable=true` is wrong, last good index 2026-08-21. Not re-run here.

**Claim-verb class** (P3 description: `verified`/`confirmed`/`works` in assistant text with no preceding command in the turn). Own op: since last user message, any `toolCall` counts as a preceding command; then `\b(verified|confirmed|works)\b` / strict without `works`.

| predicate | n | / 45111 | |
|---|---|---|---|
| any claim verb | 7191 | 15.94% | wallpaper if unscoped |
| any, no prior cmd | 364 | 0.807% | |
| strict (verified\|confirmed) | 6663 | 14.77% | |
| **strict, no prior cmd** | **329** | **0.729%** | n≥50, <5% |

**REFUSE as a fleet TTSR rule anyway.** 329 hits live in **49 files**, and **one session dir** (`omp-orchestrator/2026-09-10T23-03-57-*`) holds ~73% of them. Seed `20260920P4c` n=24: **23/24 from that session**. Labels (proof-class inflation = TP): **2 TP / 22 FP**. Almost all are closeout jargon (`verified per-row`, `SHA-256 verified`, quoting "verified claim"). Same named-vs-shape split: the word is present; the defect (untested assertion) is not.

Read-bursts / skill-routing: JSONL has 416,485 `toolCall` parts — now measurable. **Not measured this tick.**


Bar copied from the packet (preregistered before labelling): wallpaper ≳5%; n<50 too rare for a rule.

Own predicates (not P3's — P3 had not landed `depth-rule-pack-*`):

| class | predicate (mine) | n | rate | seed `20260920P4` labels |
|---|---|---|---|---|
| `git add -A` / `git add .` | `git` argv `add` with `-A`/`--all` or sole path `.`; heredoc bodies stripped | **1** | 0.0013% | 1/1 TP (`git -C /tmp/gbp-push-0912 add -A`). **REFUSE** (<50). dcg already denies. |
| structural grep/rg | first pipeline stage after `cd … &&` is `grep`/`rg`/`ripgrep` **and** pattern contains `fn ` / `=>` / `impl ` / `function ` / `class ` | **965** | **1.2334%** | n=24. Lenient (any `fn` hunt): 24/24 TP. **Strict** (syntax question, not named-symbol lookup): **5 TP / 19 FP = 79% FP**. |
| new `scripts/*.sh` | `>` or `tee` to `scripts/*.sh` | **4** | 0.0051% | 2 TP (jev `cat > scripts/{noclaim-harvest,feed-idle-panes}.sh`) / 2 tmp plants. **REFUSE** (<50). |
| `*_v2`/`*_improved`/`*_enhanced` | path-like token in the bash string | **10** | 0.0128% | 0/10 are source-file creates; all scratch `/tmp/*_v2.txt`. **UNDERPOWERED** (class is write/edit). |

**Planted negative (required):** I expected to refute structural-grep as wallpaper (>5%) the way the glob class died. **Could not refute on the rate bar** (1.23% < 5%, n=965 ≥ 50). The independent-labeller catch is the other axis: **79% of the seeded 24 are `grep -n 'fn <already-known-name>'`**, which is navigation, not a structural question ast-grep uniquely answers.

### Hold P3 to their shipped predicate (not mine)

`.omp/rules/bash-structural-def-search.md` condition, copied:
`\b(rg|grep)\s+-[a-zA-Z]*r[a-zA-Z]*\s+.{0,80}(fn\s+[a-zA-Z_]|=>|impl[\s<]|function\s+[a-zA-Z_]|class\s+[a-zA-Z_])`
Requires a flag **containing `r`** (`-rn`, `-r`, not bare `-n`). That is why their n is 304 not my 965.

| | n | rate |
|---|---|---|
| P3 claimed | 304/78242 | 0.39% |
| **My re-run of their regex** | **304/78242** | **0.3885%** **CONFIRM** |

FP definition taken from **their own rule body**: *"Ignore this if the pattern is an exact literal in a file you already know."* Named-identifier `fn <already-known>` = FP; shape (`fn main`, `fn spawn`, `fn.*select`) = TP.

| seed | n | TP | FP | FP rate |
|---|---|---|---|---|
| `20260920P4` (pre-committed before their file existed) | 24 | 9 | 15 | **62.5%** |
| `20260920P4b` (fresh) | 24 | 7 | 17 | **70.8%** |
| pooled | 48 | 16 | 32 | **66.7%** |

They published **FP 0.25 on seed 20260921 n=20**. **OVERTURN that FP** (rate CONFIRMed). Same glob-class failure: predicate inside the bar, majority named-symbol lookup. `interruptMode: never` plus "ignore if known literal" does not make 67% of fires useful.


Loose first `git_add_all` matched `git commit` heredocs containing the word `add` (n=2, both FP). Tightening is the measurement; the loose number is discarded.

## U3 — P2 `sr` claims (citations only; no live rank)

Receipt now exists: `docs/demos/upstream-repro/sr-advise-20260920.md`. I did **not** re-run `sr`. I resolved their `file:line` against `skillranker/` (vendored, read-only).

- `verified=0` as roster display: **CONFIRM** `discovery.rs:627-630` (comment they quoted is there). **BY-DESIGN** for inspection, as they said.
- Global withhold: **CONFIRM** `resolution.rs:530-540` `discovery_withhold` forces `Visibility::Unverified` on every entry. Store-size / symlink counts: **UNDERPOWERED** (I did not re-measure).
- Planted negative: they **concede** `demo --case none` is the GUARD path; `"What time is it"` dry-run is **PREPARED-NOT-MEASURED**. I CONFIRM they named that. I do **not** CONFIRM the ranker abstains.
- Offline vs live: live **NOT_RUN** (key absent). Paid model did not earn a seat. That sentence is in **their** receipt. **CONFIRM** the non-claim.


## TTSR / interrupt log (nuisance-rate)

Live project rules: `bash-glob-silenced`, `bash-pipe-exit`.

| fires | rule name | what I was doing |
|---|---|---|
| 1 | `bash-glob-silenced` | TTSR interrupt while reading ee source / grepping the tree. Complied. |
| 0 | `bash-pipe-exit` | — |
| 1 | `zeststream.shared_worktree:git-stash-worktree-wide` | **dcg**, not TTSR. Python probe contained `git stash`. Retried `--cmd-base64`. |

Nuisance-rate for shipped TTSR: **1 `bash-glob-silenced` fire** this session (was 0 at first commit).


## CONFIRM / OVERTURN / UNDERPOWERED

| claim | verdict |
|---|---|
| jev `.ee` healthy, home is a different store | **CONFIRM** |
| `remember` alone never reaches `preflight` for `grep -c` | **CONFIRM** (early-return `cli/mod.rs:25807`) |
| that gate is "builtin" rather than "any `matches[]`" | **OVERTURN my first receipt** — toml glob opened `matchedMemories` |
| tripwire created directly closes preflight | **OVERTURN** (still) |
| embeddings / missing index caused the empty grep-c recall | **OVERTURN** (`list_memories`, no search) |
| `--kind` was the whole bug | **OVERTURN as sufficient**; it is filter #2 after matches |
| C71 newer-upstream-fix | **REFUTED honestly** — mirror 0.15.2 == installed 0.15.2 |
| P3 rate 304/78242 | **CONFIRM** |
| P3 FP 0.25 n=20 | **OVERTURN** (my labels 62.5% / 70.8% on 24+24) |
| P2 `verified=0` roster display | **CONFIRM** `discovery.rs:627-630` (by-design) |
| P2 ranker abstains on "what time is it" | **UNDERPOWERED** (they marked PREPARED-NOT-MEASURED; I did not run `sr`) |

| morph missing (`command -v`) | **OVERTURN of the packet** (MCP; this session unwired) |
| `fh` STALE discounts doctrine | **OVERTURN of the packet** |
| prose classes UNMEASURABLE (ever) | **OVERTURN** — that was the bash harvest; JSONL has 45k assistant-text turns |
| claim-verb TTSR on no-prior-cmd | **REFUSE** (0.729%, session-dominated, 2/22 TP/FP) |
| P1 1841/45103 | **CONFIRM** within live drift (1842/45108) |
| cass as next corpus | **DO NOT WAIT** (commit-cap, retryable lie) |

## NO-CLAIM

- Did not run `foundation/gates.sh`. Did not `/mcp` reload morph.
- Did not call Jev (Infisical; choice). Did not file cass or sr upstream (Joshua).
- Did not measure read-bursts or skill-routing on the 416,485 toolCall parts.
- Claim-verb labels: one reader, n=24, seed `20260920P4c`.
- P3 FP labels n=48 as before. No preflight hook at tool_call.


## Next

A hook that runs `ee preflight check --cmd-base64` on bash tool_call would put cataloged recall at the moment of the command. That is a separate ship, not this toml. Auto-recall still waits on ee > 0.15.2. P2 live rank is theirs.

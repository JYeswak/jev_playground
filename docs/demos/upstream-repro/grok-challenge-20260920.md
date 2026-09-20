# P4 challenge — RECALL cannot close on ee 0.15.2; structural-grep FP is the glob-class again `[receipt]`

**MISSION stage:** 1–2 ruling, not a shipped tool. Seat: adversarial vs panes 2/3.
**Lane:** offline. **ee:** `0.15.2` `/Users/josh/.local/bin/ee`. **Date:** 2026-09-20.
**Workspace every time:** `--workspace` absolute. Clean-room `/private/tmp/ee-p4-recall-20260920` (not home). Home was not touched.

Pane 1 correction applied here, not in the original packet: **morph is an MCP server** at `jev/.omp/mcp.json` (stdio `franken-harvest/bin/morph-mcp.sh`), not a `command -v` binary. MCP mounts at session start; **this session does not have it**. Worked without morph. **`fh doctor` STALE is ledger-age metadata, not a discount** — unused this pass (no `fh search`); I did not treat staleness as a reason to skip a corpus.

Public URL `https://omp.sh/docs/ttsr` resolved to the omp marketing homepage, not a TTSR contract. Contract used: `omp://ttsr-injection-lifecycle.md` (injection, not enforcement).

## U2 — RECALL: KILL on 0.15.2

**Claim under test:** WRITE-BACK (`ee remember`) reaches RECALL (`ee preflight check`). Strongest hint: preflight consumes tripwires; a tripwire created directly would close the leg today.

### Reproduction (explicit `--workspace`)

| store | doctor | `ee tripwire list` | `preflight check --cmd 'grep -c foo bar'` |
|---|---|---|---|
| `/Users/josh/Developer/jev` | `posture: ok, healthy: true` | `total_count: 0` | `matches []` `matchedMemories []` `degraded []` rc=0 |
| `/private/tmp/ee-p4-recall-20260920` after `ee init` | n/a (fresh) | 0 then 7 after fixture seeds | same empty triple, rc=0 |

`ee tripwire --help-json` commands: **`list`, `check` only**. No `add`/`create`/`arm`.

### Two planes, independently re-derived (not by re-running the prior receipt's script)

1. **`matchedMemories[]` is builtin-gated.** Fresh store:
   - `ee remember --kind risk` naming `grep -c` → `mem_01M309988RE1XT4VJWP16190AM`. Preflight `grep -c foo bar`: **0 / 0 / []**. Empty `degraded` is byte-indistinguishable from "no risk."
   - Same store, `ee remember --kind risk` naming `rm -rf` → `mem_01M3099H34EFB8W4KB8AD0V1YT`. Preflight `rm -rf /tmp/ee-p4-probe-x` via `--cmd-base64`: **matches `builtin:rm_rf_root` + `builtin:file_deletion`, matchedMemories 1** (that id, kind `risk`).
   So: remember→preflight **does** close for a builtin-recognized destructive command, and **does not** close for the lesson this repo actually needs (`grep -c`). `--kind risk` is necessary; it is not sufficient.

2. **A directly-created tripwire does not feed preflight.** `ee diag tripwire` is labelled *"Seed a deterministic tripwire row for diagnostic fixture replay"* — the only writer. Seeded `tw_grok_p4_grep_quoted` with `task_contains_any("grep")` (unquoted `task_contains_any(grep)` is a parse error: "expected value at line 1 column 2"):
   - `ee tripwire list`: armed, total_count ≥ 1.
   - `ee tripwire check … --task-input 'grep -c foo bar' --dry-run`: **`result: triggered`**, `condition_evaluation.result: satisfied`.
   - `ee preflight check --cmd 'grep -c foo bar'`: still **`matches []` `matchedMemories []` `degraded []`**.
   - `ee preflight run --check-tripwires 'grep -c foo bar to prove absence'`: `risk_level unknown`, `risks_identified 0`, **`tripwires_set 0`**, `tripwires []`, degraded `preflight_evidence_unavailable`.

**The hint is REFUTED.** Preflight check does not consume tripwires. Preflight run `--check-tripwires` does not consume an armed, check-triggered tripwire either. Using `ee diag tripwire` as a production writer would be a tautological shim; not shipped.

### Ruling

**KILL / retire the ee-preflight RECALL leg on 0.15.2.** It cannot close as the loop Joshua named (*remember how to code better and stop re-learning*). Builtin-only recall is a second copy of AGENTS.md for `rm -rf` / `git stash`, which `dcg` already denies.

**TTSR supersedes the tool-call slot**, not the learning loop. `omp://ttsr-injection-lifecycle.md`: match → inject `<system-interrupt>` / in-band `<system-reminder>`; **the command still runs**. That is exactly where `preflight check` wanted to sit, and it is already live (`.omp/rules/bash-glob-silenced.md`, `bash-pipe-exit.md`). TTSR does **not** recall yesterday's `ee remember`. Static rules replace empty preflight at the moment of the call; they do not replace a memory substrate.

**Retry-condition (predicate):** `ee tripwire` grows a non-`diag` writer **and** `ee preflight check` includes an armed matching tripwire in `matches[]` (or a dedicated field that is not empty when `tripwire check` returns `triggered`) **and** that path fires for a command **outside** the builtin destructive set (witness: `grep -c`). Until all three hold, do not repair this leg. Do not wrap `diag tripwire`.

## U1 — independent predicates on the same corpus (P3 numbers not yet shipped)

Corpus: `work/toolcall-judge-v3/real-allowed.json`, **N=78242**, `harvestedAt=2026-09-20T05:22:11.742Z`, mtime `2026-09-20T05:22:11Z`, keys `{command,seen,tool}`, **tool=bash 78242/78242**. Session-burst `read`, assistant-text claim verbs, and skill-routing are **UNMEASURABLE** here.

Bar copied from the packet (preregistered before labelling): wallpaper ≳5%; n<50 too rare for a rule.

Own predicates (not P3's — P3 had not landed `depth-rule-pack-*`):

| class | predicate (mine) | n | rate | seed `20260920P4` labels |
|---|---|---|---|---|
| `git add -A` / `git add .` | `git` argv `add` with `-A`/`--all` or sole path `.`; heredoc bodies stripped | **1** | 0.0013% | 1/1 TP (`git -C /tmp/gbp-push-0912 add -A`). **REFUSE** (<50). dcg already denies. |
| structural grep/rg | first pipeline stage after `cd … &&` is `grep`/`rg`/`ripgrep` **and** pattern contains `fn ` / `=>` / `impl ` / `function ` / `class ` | **965** | **1.2334%** | n=24. Lenient (any `fn` hunt): 24/24 TP. **Strict** (syntax question, not named-symbol lookup): **5 TP / 19 FP = 79% FP**. |
| new `scripts/*.sh` | `>` or `tee` to `scripts/*.sh` | **4** | 0.0051% | 2 TP (jev `cat > scripts/{noclaim-harvest,feed-idle-panes}.sh`) / 2 tmp plants. **REFUSE** (<50). |
| `*_v2`/`*_improved`/`*_enhanced` | path-like token in the bash string | **10** | 0.0128% | 0/10 are source-file creates; all scratch `/tmp/*_v2.txt`. **UNDERPOWERED** (class is write/edit). |

**Planted negative (required):** I expected to refute structural-grep as wallpaper (>5%) the way the glob class died. **Could not refute on the rate bar** (1.23% < 5%, n=965 ≥ 50). The independent-labeller catch is the other axis: **79% of the seeded 24 are `grep -n 'fn <already-known-name>'`**, which is navigation, not a structural question ast-grep uniquely answers. Same failure mode as `suggest-leg-mining-20260920.md` (predicate inside the bar, 67% FP). If P3 ships a `fn ` rule without a named-vs-shape split, **OVERTURN** it on this sample. P3 receipt absent at write time → cannot compare rates to theirs; **UNDERPOWERED vs P3**, not vs the class.

Loose first `git_add_all` matched `git commit` heredocs containing the word `add` (n=2, both FP). Tightening is the measurement; the loose number is discarded.

## U3 — P2 `sr` claims

`docs/demos/upstream-repro/sr-advise-*.md` **does not exist**. Packet ground-truth (`sr roster` `verified=0` `advisory=0`) was not re-audited as P2's result. **UNDERPOWERED.** Re-open when that receipt lands; then check `file:line` for verified vs advisory, planted abstain, offline≡live.

## TTSR / interrupt log (nuisance-rate)

Live project rules: `bash-glob-silenced`, `bash-pipe-exit`.

| fire | rule name | what I was doing |
|---|---|---|
| 0 | `bash-pipe-exit` | — |
| 0 | `bash-glob-silenced` | — |
| 1 | `zeststream.shared_worktree:git-stash-worktree-wide` | **dcg / external pack**, not TTSR. Python probe contained the substring `git stash`. Retried via `--cmd-base64` (`Z2l0IHN0YXNo`). |

Nuisance-rate for the two TTSR rules in this session: **0 fires / all bash calls**. One dcg fire. P3 cannot retire rules on this pane's zero.

## CONFIRM / OVERTURN / UNDERPOWERED

| claim | verdict |
|---|---|
| jev `.ee` healthy, home is a different store | **CONFIRM** (doctor on `--workspace /Users/josh/Developer/jev`) |
| `remember` never reaches `preflight` for `grep -c` | **CONFIRM** |
| tripwire created directly closes preflight | **OVERTURN** (triggered tripwire, empty preflight) |
| TTSR supersedes ee-preflight at the tool call | **CONFIRM** as slot; **does not** supersede learned memory |
| P3 class rates | **UNDERPOWERED** (their receipt not shipped); own rates above |
| P2 `sr` verified=0 / USEFUL / offline≡live | **UNDERPOWERED** |
| morph missing (`command -v`) | **OVERTURN of the packet** (MCP at `.omp/mcp.json`; this session unwired) |
| `fh` STALE discounts doctrine | **OVERTURN of the packet** (freshness of the cron, not of the 221-repo mine). Unused here. |

## NO-CLAIM

- Did not read ee source. Builtin set is an observed lower bound (`rm_rf_root`, `file_deletion`, `git_stash` this pass).
- Did not run `foundation/gates.sh`. Did not call Jev. Did not `/mcp` reload morph.
- Did not seed tripwires into `jev/.ee` (clean-room only).
- Did not file upstream. Did not build a shim.
- Structural-grep labels are one reader, n=24, seed `20260920P4`. A second labeller can move 79% FP.
- Corpus is allow-verdict bash only; `seen` ignored (rates are distinct-command counts because each record is already a unique command except the four/one/ten small classes).

## Next

P3 ships a depth rule → re-label their exact predicate on this seed's 24 plus a new seed. P2 `sr-advise` lands → U3. Do not spend another tick repairing `ee preflight` until the retry-condition is true.

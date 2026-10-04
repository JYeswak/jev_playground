# `jev` doctor / health / repair — scorecard + triad spec

Author: DoctorSpec · 2026-10-04 (UTC) · repo HEAD `4597f3a8` · read-only investigation; no repo file changed.
Method: the full required set of `world-class-doctor-mode-for-cli-tools` files was read (paths below are relative to `~/.agents/skills/world-class-doctor-mode-for-cli-tools/`). The existing doctor was run keyless. Logs were read in memory only.

Commands actually run (outputs quoted where used):

| Command | rc | Output (abridged) |
|---|---|---|
| `env -u TYPESAFE_API_KEY node kit/bin/jev.mjs doctor --robot` | 2 | `{"status":"NOT_RUN","reason":"no key","model":"jev-1.13.0","key_source":"none","sdk":"@typesafe-ai/sdk","omp":{…6 tools, 1 hook, 5 extensions all present:true…,"manifest":false}}`, stderr empty |
| `node kit/bin/jev.mjs --help` | 1 | stdout empty; stderr `jev doctor\|gate\|ask\|rerank\|classify\|verify\|score ...` |
| `jev doctor` / `jev doctor --help` / `jev doctor --json` / `jev doctor capabilities --json` (all keyless) | 2 | each printed `NOT_RUN: no key (model=jev-1.13.0)` (the extra arguments are ignored) |
| `node kit/bin/jev.mjs doctr --robot` | 1 | `{"status":"ERROR","reason":"usage",…}` (no did-you-mean hint) |
| `bun scripts/check-hook-loads.mjs --repo $PWD --home $HOME` | 0 | `HOOK_LOAD_OK entrypoints=78` |
| `command -v -a jev` | 0 | `/Users/josh/.local/bin/jev` → symlink to `hermes-jev-skills/bin/jev` (Python), **not** `kit/bin/jev.mjs` |
| `launchctl list \| grep -iE 'jev\|localbench\|fleet'` | 0 | `ai.zeststream.jev-latest-canary` last exit 0; `com.localbench.ollama-gateway` pid 40875; `dev.localbench.omp-update` last exit 1 |

---

## 1. Scorecard of the current `jev doctor`

Scope: the `doctor` verb at `kit/bin/jev.mjs:32-57`, scored as one surface. It owns no failure modes. Note: `kit/src/preflight.ts:1-115` is the request-size/options preflight (`sizePreflight`, `optionsPreflight`). It contains no doctor logic.

| # | Dimension | Score | Rubric anchor (SCORING-RUBRIC.md) | Evidence |
|---|---|---|---|---|
| 1 | agent_intuitiveness | **400** | :14 (250 "only output is see --help"), :15 (500 "human-readable summary… `--json` exists but isn't mentioned in `--help`") | `jev doctor` prints a single line (`jev.mjs:55`). `--help`, `--json` and `capabilities` are silently ignored because dispatch only checks `args[0]` (`jev.mjs:209`). There is no `--help` at any level (`jev.mjs:226-229`). A typo gets no hint (the 1000 anchor at :17 needs one). The score is held below 500 because the summary is misleading (D1). |
| 2 | agent_ergonomics | **400** | :28 (250), :29 (500 "stdout is data… `--robot` doesn't exist") | Under `--robot`, stdout is exactly one JSON line and stderr is empty (`jev.mjs:24-26`; measured). There is no `schema_version` (`jev.mjs:45-52`). `--json` produces prose. Only 3 exit codes are documented (`ROBOT.md:5-7`), against the 11 that `POLISH-BAR.md:114-127` requires. |
| 3 | automation_degree | **0** | :41 "read-only; no `--fix`" | There is no fixer. Repair-like verbs (`jev omp install\|uninstall`, `jev.mjs:216-225`) are not connected to any finding. |
| 4 | data_safety | **0** | :55 "writes in place. No backups" | The doctor writes nothing. The adjacent repair path does: `installOmp` overwrites with `writeFile` and makes no backup (`install.ts:61`), and `uninstallOmp --apply` calls `unlink` (`install.ts:93`). That breaks envelope rules #1 and #5 (`SAFETY-ENVELOPE-TEMPLATE.md:9,17`). Existing guards: edited files are refused (`install.ts:57-59`), a scope-escape check exists (`install.ts:77-78`), and uninstall defaults to dry-run (`jev.mjs:223`). |
| 5 | idempotence | **N/A** | :69-73 grade `--fix` | No fixer exists. Diagnose writes nothing, so it is trivially idempotent. Excluded from the median. |
| 6 | reversibility | **0** | :83 "No undo" | No `undo` verb and no backups. |
| 7 | diagnostic_specificity | **300** | :98 (250 names subsystem), :99 (500 cites file, "see docs") | The omp rows cite file paths with `present` (`install.ts:98-101`). `reason:"no key"` names neither the key sources checked nor the command that fixes it. No finding has a remediation command. |
| 8 | blast_radius_containment | **250** | :112 "write-scope implicit. No `--dry-run`" | No `capabilities` and no `write_scopes`. The doctor has no dry-run (the separate `omp uninstall` does). |
| 9 | observability | **0** | :125 "No run-id, no artifacts" | No run directory, no report file, no history. |
| 10 | test_coverage_of_repair | **150** | :139 (0 no fixtures), :140 (250 ad-hoc tests) | Two tests pin only the keyless path (`kit/test/cli.test.mjs:26-30`, `kit/test/package.test.mjs:19-46`). No fixtures. |

**Median over the 9 scored dimensions: 150** (0,0,0,0,150,250,300,400,400). No score reaches 700, so the evidence requirement at `SCORING-RUBRIC.md:3` does not apply. Stage: below Stage 1, which expects 350–500 plus a `Finding{id,severity,evidence,remediation}` and one fixture per detector (`GROWTH-LADDER.md:17-30`). Missing `capabilities` counts as P0 under diagnostic_specificity and observability (`ANTI-PATTERNS.md:21`).

### Correctness defects found while scoring (more urgent than the rubric)

| ID | Defect | Evidence |
|---|---|---|
| D1 | **False NOT_RUN.** The doctor checks only `TYPESAFE_API_KEY` in the environment (`jev.mjs:33`). Every live surface instead resolves the key through the Infisical provider: explicit option, then env, then provider (`kit/src/client.ts:249,262-266`; `work/jev-client/src/use-infisical-key.ts:11`; models.yml wrapper `work/jev-client/bin/typesafe-key.mjs:18-38`). The doctor reports "no key" on a machine where every hook is keyed. | Hooks scored 3,561 gate rows in the last 24 h (`~/.local/state/jev/gate-observe.jsonl`) while the doctor reported `key_source:"none"`. |
| D2 | omp discovery is stale. It hard-codes **one** hook (`install.ts:98`). `work/jev-inventory/expected.json` declares 6 hook rows, 2 global hooks and 4 extensions. "File present" is not the same as "loaded": loading is controlled by the `extensions:` list (`.omp/config.yml`, read by `check-hook-loads.mjs:183-194`). | `install.ts:97-101` vs `expected.json:61-256` |
| D3 | Extra arguments are ignored (`--help`, `--json`, `capabilities` all run diagnose). | `jev.mjs:209` |
| D4 | The top-level usage message omits `omp install\|uninstall` and the sibling bin `jev-skill-gap`. | `jev.mjs:227`; `kit/package.json:7-10` |
| D5 | **PATH shadowing.** `jev` on PATH resolves to `hermes-jev-skills/bin/jev` (Python), so `jev doctor` typed in a shell is a different program. | `command -v -a jev` (above) |
| D6 | The SDK probe imports `../../work/sdk/...`, a path outside the package (`jev.mjs:34`). In a stranger install only the fallback (`jev.mjs:40`) is meaningful. | `jev.mjs:34-44` |
| D7 | Exit 2 means NOT_RUN here (`ROBOT.md:6`, `README.md:19-20`), but the skill dictionary uses 2 for `fix_partial` (`CLI-SURFACE.md:75`). | see §3.3 |
| D8 | **Stale writer.** `injection-shadow.jsonl` received 292 rows in the last 24 h with `schema:"jev-injection-shadow.v1"` (last at 2026-10-03T16:44:39Z), alongside 5,354 v2 rows. Current source writes v2 (`.omp/hooks/post/jev-injection-shadow.ts:13`). Some long-lived process is still running the old hook. | in-memory parse of the log, 2026-10-04T03:06Z |
| D9 | **OFF surface still writing.** `skill-hint` is `expect:"off"` (`expected.json:113-123`) but wrote 764 rows in 24 h (silent 405 / hinted 327 / warmup 32), last at 2026-10-04T03:00:33Z. `jev-skill-hint.ts` is absent from `.omp/config.yml extensions:`. A grep of `~/.omp/agent/config.yml`, `~/.omp/profiles/*/agent/config.yml`, `~/.omp/*/hooks`, `~/.omp/omp-extensions` and `~/.omp/plugins/node_modules/*/package.json` found no loader. **Writer UNVERIFIED.** | `~/.local/state/jev/skill-hint-calls.jsonl`; writer path `.omp/extensions/jev-skill-hint.ts:18` |

---

## 2. Triad spec for the whole `jev` CLI

### 2.1 Surface (one doctor for one CLI)

Pattern classification (cookbook `SKILL.md:508-524`): Pattern 7 (AI-agent CLI), Pattern 9 (vendor-API client: Jev), Pattern 4-lite (depends on local daemons: Clef `:8010`, localbench gateway `:11300`), Pattern 2 (sibling bin `jev-skill-gap`). All per-pattern adjustments apply together (`distributed-cli.md:157-159`).

```text
jev doctor                         # diagnose (default tier). Read-only. exit 0/1/4
jev doctor --json | --robot        # --json = raw report; --robot = envelope (data=report)
jev doctor --quick | --deep        # tier selection (quick ⊂ default ⊂ deep)
jev doctor --online                # also run network checks (Jev API, Infisical resolve)
jev doctor --only <id|subsystem,…> / --skip <…>
jev doctor explain <finding-id>    # full evidence; reads latest run, no re-detect
jev doctor capabilities --json     # generated from the registry, never hand-written
jev doctor robot-docs              # in-tool handbook (Markdown)
jev doctor ls                      # runs, newest first
jev doctor --robot-triage          # {summary,findings,actions_planned,recommended_command,capabilities_url}
jev health        ≡ jev doctor health       # one line + exit; quick tier only; <200 ms target
jev repair        ≡ jev doctor --fix        # PLAN ONLY (dry-run) unless --apply
jev repair --apply                          # execute via mutate(); takes the lock
jev doctor undo <run-id|latest> [--dry-run] [--no-strict]
jev doctor gc --before <date> --yes         # only deletion surface; never implicit
Global flags: --repo DIR (default: nearest ancestor containing work/jev-inventory/expected.json, else none)
              --home DIR (default $HOME)  --no-color  --quiet  -v/-vv
```

Deliberate deviation from `CLI-SURFACE.md:47-48`: **`--fix` alone does not execute**. It plans (dry-run), and `--apply` executes. Reasons: the task requires dry-run by default, and the repo already uses `--apply` for its one mutating verb (`jev.mjs:223`). The skill's `--dry-run --fix` still prints the plan with exit 0 (`SKILL.md:463`). `--dry-run` combined with `--apply` is a usage error (64).

Top level: `jev --help` / `jev help` → stdout help listing every verb, including `omp install|uninstall`, `health`, `repair`, and sibling `jev-skill-gap`; exit 0. An unknown verb within edit distance ≤2 of a known verb prints `did you mean: jev doctor` and exits 64 (`SCORING-RUBRIC.md:17`, `REGRESSION-TEST-PATTERNS.md:20-24`).

### 2.2 Checks (detectors)

Conventions:
- Every detector is pure (`(ctx) → Finding[]`, no writes; `STATE-MACHINE.md:121-125`). Each runs in its own try/catch; a crash produces a `safety_block` finding naming the detector (DP-006, `DESIGN-PATTERNS.md:98-119`).
- `ctx = {repo|null, home, stateDir = $home/.local/state/jev, now, online, tier, exec}`. `exec` is injectable so tests never spawn real `launchctl`, `infisical`, `bun` or `omp`.
- Repo-scoped checks are marked `repo_required`. When `--repo` does not resolve (stranger install from `npm pack`), they return `provenance:"unavailable"` and emit no finding (Axiom 17, `KERNEL.md:147-157`).
- IDs come from `scripts/compute-fm-id.py` (`SKILL.md:747`).
- Kinds A–G follow `FAILURE-ONTOLOGY.md:11-117`.
- Tiers follow `PERFORMANCE.md:27-32`: Q = quick (stat/connect only, ≤5 ms each), D = default (parse, ≤100 ms each), X = deep (≤1 s+), O = online.

#### A. Key resolution (subsystem `secrets`)

| id | Tier | Kind / Sev | Data source (exact) | Predicate → finding | Fix |
|---|---|---|---|---|---|
| `fm-secrets-no-key-source` | Q | G / P0 | env `TYPESAFE_API_KEY` (`client.ts:263`); `$home/.local/bin/infisical` or `infisical` on PATH (`work/jev-client/src/infisical-key.ts:49-51`); `$home/.config/infisical/zeststream.env` with `INFISICAL_CLIENT_ID` (`infisical-key.ts:62-65`) | No env key **and** no infisical binary **and** no machine-identity config. Evidence: which sources were checked (booleans) and `key_source` ∈ {env, infisical-user, infisical-machine, none}. The key value is never read. | manual: `infisical login` or set env. Afterwards: `jev doctor --only fm-secrets-no-key-source` |
| `fm-secrets-key-wrapper-missing` | Q | G / P0 | `$home/.omp/agent/models.yml` and `$home/.omp/profiles/<p>/agent/models.yml` for each `p` in `expected.json:4-10` | File missing, or does not contain `typesafe-key.mjs` (same predicate as `inventory.py:225-235`). Evidence: `{profile, file, line:null}`. | manual (user config; Kind G refuses, `FAILURE-ONTOLOGY.md:116`) |
| `fm-secrets-machine-config-mode` | Q | D / P1 | `stat $home/.config/infisical/zeststream.env` | `mode & 0o077 ≠ 0` (P-010, `PREDICATE-LIBRARY.md:307-324`). Measured now: `0o600`, clean. | `Chmod 0600` via `mutate()` |
| `fm-secrets-key-resolve-failed` | O | G / P0 | Runs `work/jev-client/bin/typesafe-key.mjs` (repo_required) with a 10 s timeout (`typesafe-key.mjs:10-11`). stdout is captured in memory and discarded after computing `{resolved:bool, length}`. | exit ≠ 0 or empty output. The key is never logged or written (`SECURITY.md:29-63`). | manual |
| `fm-secrets-recent-resolve-failures` | D | G / P1 | tail of `$stateDir/gate-observe.jsonl`: rows with `error` matching `key-source=infisical` | ≥1 such row in the last 24 h. Historical: 1,506 rows between 2026-09-28T03:32Z and 2026-10-01T05:45Z, 0 in the last 24 h. | manual |

#### B. Jev API (subsystem `network`; vendor realm, `distributed-cli.md:9-32`)

| id | Tier | Kind / Sev | Data source | Predicate | Fix |
|---|---|---|---|---|---|
| `fm-network-jev-canary-stale` | D | E / P1 | `$stateDir/jev-latest-canary.log`, written by LaunchAgent `ai.zeststream.jev-latest-canary` daily at 09:07 local (plist `ProgramArguments`, `StartCalendarInterval`) | Last line's timestamp older than 26 h. Last seen: `2026-10-03T15:07:03Z rc=0`. | manual |
| `fm-network-jev-model-moved` | D | F / P0 | same log, last line | `rc=1` ("jev-latest moved off jev-1.13.0") or the text does not contain `resolves to jev-1.13.0`. Pinned model: `client.ts:66`. | manual (re-calibration decision) |
| `fm-network-jev-unreachable` | O | E / P1 | One `askJev` Noul through the kit client (`client.ts:377`) to `https://api.typesafe.ai/v1/systemone` (`client.ts:65`), using the key resolved by the provider. 10 s timeout. | Transport error, 5xx, or `model` ≠ `jev-1.13.0`. HTTP 401/402/403 is reported as `fm-network-jev-billing-hold` (`client.ts:237-241`). Cost is one call, reported in evidence. | manual |
| `findings_only_offline` | — | info | — | Without `--online`, the report contains one aggregate note listing the skipped O-tier checks (`distributed-cli.md:108`). It is not a finding and does not affect exit. | — |

`capabilities.vendor_apis = [{name:"typesafe",endpoint:"api.typesafe.ai",purposes:["reachability","model_pin"]},{name:"infisical",endpoint:"secrets.zeststream.ai",purposes:["key_resolve"]}]` (trust manifest, `distributed-cli.md:132-143`; origin `infisical-key.ts:170`).

#### C. Clef (subsystem `local_backends`; loopback is not network, `daemon-cli.md:33`)

| id | Tier | Kind / Sev | Data source | Predicate | Fix |
|---|---|---|---|---|---|
| `fm-clef-unreachable` | Q | E / P1 if any surface routes to Clef, else P3 | TCP connect `127.0.0.1:8010`, 100 ms (P-011 shape, `PREDICATE-LIBRARY.md:328-349`). Endpoint and model from the conductor scoreboard (2026-10-04). | connect refused or timed out | manual (no LaunchAgent for Clef exists in `~/Library/LaunchAgents/`; how Clef is supervised is **UNVERIFIED**) |
| `fm-clef-model-mismatch` | X | F / P1 | One minimal SystemOne request (`POST http://127.0.0.1:8010/v1/systemone`, `model:"clef-flash"`, 5 s timeout; ~3 s/call per conductor) | Response `model` ≠ `clef-flash`, non-2xx, or unparsable. The response field name is assumed to match Jev's (`model`, cf. `scripts/test_jev_latest_canary.py:14-17`). **UNVERIFIED against Clef.** | manual |
| `fm-clef-platt-map-missing` | Q | B / P1 | Each task routed to Clef needs a committed Platt map. None is persisted today: `work/local-decision-arms/run.py:161-194` fits it at run time. Proposed path: `kit/calibration/clef-flash/<task>.json` (owned by the Clef family spec). | A routed task has no map file, or the map's `fitted_on` sha256 ≠ the dev-rows file hash | manual (fitting is a measurement, not a repair) |

#### D. omp surfaces per profile (subsystem `hooks` / `plugins`; all repo_required)

| id | Tier | Kind / Sev | Data source | Predicate | Fix |
|---|---|---|---|---|---|
| `fm-hooks-load-failure` | X | B / P0 | Runs `bun scripts/check-hook-loads.mjs --repo R --home H` (read-only: `Bun.build write:false`, `check-hook-loads.mjs:241-247`). It reads `.omp/config.yml`, `~/.omp/agent/config.yml`, profile configs, hook dirs and `expected.json` (`check-hook-loads.mjs:173-237`). Measured 2026-10-04: `HOOK_LOAD_OK entrypoints=78`, ~0.2 s. | Each `HOOK_LOAD_FAIL <path>: <msg>` line on stderr becomes one finding with `evidence.file`. | manual (source edit) |
| `fm-surfaces-claim-drift` | X | A / P1 | `expected.json` `expect` vs the live state from `inventory.py live_state` (`inventory.py:187-249`). Reused via a new stdout-only `inventory.py --json` mode, because the current `main` writes `var/jev-inventory/*` (`inventory.py:434-486`), which diagnose may not do. | Every `state ≠ expect` becomes one finding: `{surface, claimed, live}`. | manual |
| `fm-hooks-global-link-broken` | D | A / P1 | For each `group:"global"` surface (`expected.json:207-231`) and each profile: inode + sha256 of `$home/.omp/{agent\|profiles/<p>/agent}/hooks/post/<hookfile>` vs `R/<repo>` (predicate `inventory.py:45-70`) | Missing, different inode, or different hash | **fixer** `fx-relink-global-hook` (§3.4) |
| `fm-plugins-omp-tool-missing` | Q | C / P2 | `R/.omp/<path>` for each `INSTALL_FILES` key (`install.ts:47-49`); manifest `MANIFEST_PATH` | A file is absent and the manifest lists it unedited | **fixer** `fx-omp-reinstall-missing` (WriteFile from `kit/templates/`; refuses edited files, same rule as `install.ts:57-59`) |
| `fm-path-jev-shadowed` | Q | F / P2 | Resolve `jev` on `$PATH` (`command -v`, through `exec`) and `realpath` it | The realpath is not this package's `bin/jev.mjs`. Today it resolves to `hermes-jev-skills/bin/jev`. | manual: `npx --prefix kit --no-install jev …` or fix PATH |
| `fm-plugins-sibling-bin-missing` | Q | C / P3 | `kit/bin/jev-skill-gap.mjs` (`kit/package.json:9`) | absent or not executable | manual |

#### E. Log freshness per surface (subsystem `observability_logs`)

Surface→log map comes from the `expected.json` `log` field (gate-observe, injection-shadow, webscreen, websearch-rerank, gate-cascade, vendor-shadow). Task T2 adds `log` to the three extension rows that lack it:
- `memory-filter` → `memory-filter.jsonl` (`.omp/extensions/jev-memory-filter.ts:220`)
- `skill-hint` → `skill-hint-calls.jsonl` (`jev-skill-hint.ts:18`)
- `skill-veto` → `skill-veto-shadow.jsonl` (`jev-skill-veto.ts:27-28`)

The global hooks import `.omp/hooks/post/jev-web-duel.ts` (`work/jev-j0er/jev-webscreen-global.ts:6`). Which log they write is **UNVERIFIED**, so they get no freshness check until it is mapped. Logs are read from the tail: the last 4 MiB, scanned backwards to the window start. `gate-observe.jsonl` is 37,509 lines.

| id | Tier | Kind / Sev | Data source | Predicate | Fix |
|---|---|---|---|---|---|
| `fm-logs-silent-surface` | Q (mtime) / D (row ts) | E / P1 | `$stateDir/<log>` for each `expect:"on"` surface | Event-driven surfaces: last row `ts` older than **3 h**, the same silence rule `inventory.py:204-213` uses. `vendor-shadow` is commit-driven, so it is silent only if `git -C R log --since=<last row ts>` shows ≥1 commit. Missing file = silent. | manual |
| `fm-logs-off-surface-writing` | D | A / P1 | `$stateDir/<log>` for each `expect:"off"` surface | ≥1 row in the last 3 h. Evidence: count, first/last ts, distinct `instance` values (attribution field, `jev-skill-hint.ts:19-20`). **Fires today for skill-hint (D9).** | manual (loader unknown) |
| `fm-logs-stale-schema-writer` | D | F / P1 | rows with `schema` in the last 24 h vs the `LOG_SCHEMA` constant in the source file (e.g. `jev-injection-shadow.ts:13`) | ≥1 row with an older schema. **Fires today (D8).** Evidence: schema, count, last ts. | manual (restart the stale process; the doctor never signals processes, `daemon-cli.md:155`) |
| `fm-logs-unparsable-rows` | D | B / P2 | same tail | ≥1 line in the window fails `JSON.parse`. Measured: 0 across 11 logs. | manual |
| `fm-logs-mode-too-open` | Q | D / P2 (P1 for `*-full.jsonl` / `*-requests.jsonl` sidecars, which hold full commands and prompts, `jev-gate-observe.ts:69-71`) | `stat` of each `$stateDir/*.jsonl` | `mode & 0o077 ≠ 0`. **Fires today:** `gate-observe.jsonl` is `0o644`. Writers create `0o600` (e.g. `jev-memory-filter.ts:233`). | **fixer** `fx-chmod-log-0600` |

#### F. Daily caps (subsystem `caps`)

Caps are per-process in-memory counters (`jev-memory-filter.ts:223-224`; `jev-injection-shadow.ts:131-135`). The doctor cannot read a counter, so it detects cap hits from log rows. Cap rows are matched by **reason**, not status alone: injection `status:"cap"` rows in the last 7 days are all `reason:"recipient-and-data-class-approval-required"` (v1 writer), not `daily-call-cap`.

| Surface | Cap constant | Cap-hit row predicate | Measured 24 h |
|---|---|---|---|
| gate-observe | `MAX_DAILY_CALLS=100`/handler/UTC day, `MAX_DAILY_PAID_CALLS=1000` (`jev-gate-observe.ts:52,65`) | `status:"not-run"` ∧ `error` contains `reason=daily-cap` | 7 d: 1,235 |
| injection-shadow | 3500 (`jev-injection-shadow.ts:10`) | `status:"cap"` ∧ `reason:"daily-call-cap"` (`:132`) | 0 (292 `cap` rows have the approval reason; these belong to D8, not caps) |
| webscreen | 25 (`jev-webscreen.ts:11`) | status `cap`/`daily-cap` (exact token **UNVERIFIED**; T6 test reads it from source) | 0 |
| memory-filter | 600 (`jev-memory-filter.ts:25`) | `status:"daily-cap"` | 689 (7 d: 9,626) |
| vendor-shadow | 100/day (`work/vendor-paste/vendor-shadow.mjs:27`) | `status:"fail_open"` ∧ `reason:"cap"` | 4 (7 d: 18) |
| skill-veto | (constant not read) | `status:"fail_open:cap"` | 123 |

| id | Tier | Kind / Sev | Predicate | Fix |
|---|---|---|---|---|
| `fm-caps-hit` | D | G / P1 if the surface verdict is `ENFORCING` (`expected.json` `verdict`), else P2 | ≥1 cap-hit row in the last 24 h. Evidence: `{surface, cap, hits_24h, first_hit_ts, share_of_rows}`. | manual: raising a cap is a spend decision. Remediation gives the measured 7 d token cost from the log's `tokens` / `usage` fields. |

#### G. LaunchAgents and processes (subsystem `daemons`)

| id | Tier | Kind / Sev | Data source | Predicate | Fix |
|---|---|---|---|---|---|
| `fm-daemons-canary-agent` | Q | E / P2 | `$home/Library/LaunchAgents/ai.zeststream.jev-latest-canary.plist` exists; `launchctl list` row `ai.zeststream.jev-latest-canary` (via `exec`) | plist missing, label not listed, or last exit ≠ 0 | manual: exact `launchctl bootstrap gui/$UID <plist>`. The doctor never runs launchctl (launchd registration is judged DANGEROUS, `work/toolcall-judge-v3/adjudication.json:76-78`). |
| `fm-daemons-gateway-down` | Q | E / P1 (the gate cascade depends on it) | `launchctl list` row `com.localbench.ollama-gateway` has a pid; TCP connect `127.0.0.1:11300` (`jev-gate-observe.ts:61`) | no pid, or connect refused. Historical: 186 `local-screen-gateway-unreachable` not-runs in 7 d (`gate-observe.jsonl`). | manual |
| `fm-daemons-needs-human-watch` | Q | E / P2 | process list contains `fleet-idle-watch.py` (`expected.json:137-147`; predicate `inventory.py:223-224`) | no match | manual |

#### H. Anomalies (subsystem `anomalies`; D tier; windows are anchored on `ctx.now`)

| id | Kind / Sev | Data source | Predicate (exact) |
|---|---|---|---|
| `fm-anomaly-silent-surface` | E | = `fm-logs-silent-surface` | (alias kept so `--only anomalies` selects it) |
| `fm-anomaly-off-writing` | A | = `fm-logs-off-surface-writing` | (alias) |
| `fm-anomaly-cap-hit` | G | = `fm-caps-hit` | (alias) |
| `fm-anomaly-error-spike` | E / P1 | per log: error-class statuses `{error, failed, fail_open, not-run}` excluding cap-hit rows | Fires if `n_24h ≥ 50` and `err_share_24h > max(2 × err_share_7d, 0.05)`, or if `err_1h ≥ 20` and `err_share_1h > 0.5`. Today gate-observe is 265/3,837 = 6.9% (24 h) vs 6,748/27,297 = 24.7% (7 d), so it does not fire. Evidence: top 3 `error`/`reason` strings with counts. |
| `fm-anomaly-native-judge-errors` | E / P2 (X tier, repo_required) | omp session logs `~/.omp/agent/sessions/*/*.jsonl` and `~/.omp/profiles/*/agent/sessions/*/*.jsonl`, `model_usage` rows with `"typesafe"` (same scan as `inventory.py:121-161`) | 24 h error rate > max(2 × 7 d rate, 1%). Baseline 0.17% / 7 d (conductor scoreboard 2026-10-04). |

Severity → blast radius uses `PRIORITY-FORMULA.md:31-39`. Frequency inputs come from the measured log counts above (`PRIORITY-FORMULA.md:9-17`).

### 2.3 `jev health` (cheap liveness)

Quick tier only: Q-tier detectors from A, C (TCP only), D (tools present, PATH), E (mtime and mode only, no parsing), G. Writes nothing: no run directory, unlike diagnose (`PERFORMANCE.md:13` budget < 200 ms p95). Output format follows `CLI-SURFACE.md:307-321`:

```text
ok  jev-kit=0.0.0 doctor=1.0.0 checks=14 findings=0 key_source=infisical-user clef=up last_run=2026-10-04T03:05:00Z
findings  jev-kit=0.0.0 doctor=1.0.0 checks=14 findings=2 P1=2 top=fm-logs-off-surface-writing last_run=…
```

`--json` gives `{schema_version,status,checks,findings:[{id,severity}],key_source,clef,last_run}`. Exit codes: 0 ok, 1 findings, 74 io.

---

## 3. Contract

### 3.1 Run artifacts (machine-scoped, not repo-scoped)

The doctor heals machine state (`~/.omp`, `~/.local/state/jev`, LaunchAgents), so artifacts live at `$JEV_DOCTOR_DIR` (default `$home/.local/state/jev/doctor/`). This adapts `OUTPUT-SCHEMA.md:11-27`:

```
~/.local/state/jev/doctor/
├── runs/<ISO8601>__<run6>/  (0700)  report.json report.md actions.jsonl backups/ quarantine/ stderr.log undo.sh
├── latest -> runs/<…>       (SymlinkAtomic)
├── lock.free | lock.held    (rename-lock, §3.5)
└── scorecard_history.jsonl
```

`run6 = sha256(target_sha + iso_utc_seconds)[0:6]` (`OUTPUT-SCHEMA.md:7`). `target_sha` is `git -C R rev-parse HEAD` when the repo resolves, else `kit/package.json` version. Diagnose writes **only** `report.{json,md}` and the `latest` link (`SAFETY-ENVELOPE-TEMPLATE.md:25`). Reports pass through `redact()` (`SECURITY.md:39-59`); backups are not redacted.

### 3.2 JSON schema (`schema_version: "1.0"`, `doctor_contract_version: "1.0"`)

`jev doctor --json` (raw report, superset of `CLI-SURFACE.md:166-215` plus `state` from `STATE-MACHINE.md:199-221`):

```jsonc
{
  "schema_version": "1.0",
  "tool": "jev", "tool_version": "0.0.0", "doctor_version": "1.0.0", "doctor_contract_version": "1.0",
  "run_id": "2026-10-04T03-05-00Z__a3f9b2",
  "run_dir": "~/.local/state/jev/doctor/runs/2026-10-04T03-05-00Z__a3f9b2",
  "started_at": "…", "finished_at": "…", "duration_ms": 412,
  "target_sha": "4597f3a8…", "repo": "/Users/josh/Developer/jev" /* or null */,
  "tier": "default", "online": false,
  "state": "DONE_FINDINGS",            // IDLE…DONE_OK|DONE_FINDINGS|DONE_PARTIAL|DONE_FAILED|REFUSING|LOCK_LOST
  "ok": false,
  "jev_on_path": { "resolved": "/Users/josh/.local/bin/jev", "realpath": "…/hermes-jev-skills/bin/jev", "is_this_package": false },
  "backends": {
    "jev":  { "status": "READY|NOT_RUN|UNKNOWN", "key_source": "env|infisical-user|infisical-machine|none", "model": "jev-1.13.0", "provenance": "live|fallback|unavailable" },
    "clef": { "status": "UP|DOWN|UNKNOWN", "endpoint": "http://127.0.0.1:8010/v1/systemone", "model": "clef-flash|null", "provenance": "…" }
  },
  "checks": [ { "id": "fm-…", "subsystem": "…", "tier": "Q|D|X|O", "ran": true, "provenance": "live|unavailable", "skipped_reason": null, "duration_ms": 3 } ],
  "summary": { "checks_run": 31, "checks_unavailable": 0, "total_findings": 3,
               "by_severity": {"P0":0,"P1":3,"P2":0,"P3":0}, "auto_fixable": 1, "online_skipped": 2 },
  "findings": [ {
      "id": "fm-logs-off-surface-writing",
      "severity": "P1", "subsystem": "observability_logs", "kind": "A", "confidence": 1.0,
      "title": "skill-hint is expect:off but wrote 764 rows in 24h",
      "evidence": { "file": "~/.local/state/jev/skill-hint-calls.jsonl", "claim": "work/jev-inventory/expected.json:113",
                    "rows_3h": 112, "first_ts": "…", "last_ts": "2026-10-04T03:00:33Z", "instances": ["3f6324c3"], "hash": "sha256:…" },
      "remediation": { "command": null, "manual": "find the loader: rg -l jev-skill-hint ~/.omp; check instance 3f6324c3 in session logs",
                       "after_user_acts": "jev doctor --only fm-logs-off-surface-writing",   // DP-003
                       "explain_command": "jev doctor explain fm-logs-off-surface-writing",
                       "auto_fixable": false, "estimated_actions": 0 }
  } ],
  "notes": [ { "id": "findings_only_offline", "skipped": ["fm-network-jev-unreachable","fm-secrets-key-resolve-failed"] } ],
  "exit_code": 1,
  "next_steps": ["jev doctor explain fm-logs-off-surface-writing"]
}
```

`--robot` wraps the same report in the jev-wide envelope, using the field names agreed with ErgonomicsSpec (`local://cli-ergonomics-spec.md`; shape per `RFC.md:219-240`). Open decision D-3 in that spec: whether this raw-under-`--json` / enveloped-under-`--robot` split is a doctor-only exception, declared in `capabilities.commands.doctor.output_format` (ErgonomicsSpec's recommendation).

```jsonc
{ "ok": false, "schema": "jev.doctor.v1", "status": "findings",
  "data": { /* report above */ },
  "meta": { "contract_version": "1.0", "backend": null, "model": null, "latency_ms": 412 },
  "warnings": [], "commands": ["jev doctor explain …"],
  "errors": [ /* only on 4/5/6/64/66/73/74: {code, exit_code, message, remediation:[…]} */ ],
  "recommended_action": { "command": "jev repair", "rationale": "1 auto-fixable finding (fm-logs-mode-too-open)" } }
```

`status` strings map 1:1 to exit codes (§3.3). Agents branch on the string.

`jev repair --json` (plan or apply) adds the fields from `CLI-SURFACE.md:217-242` plus `"mode":"plan|apply"` and `"actions_planned":[{fixer_id,path,op,before_hash,writes_to}]`. In plan mode `actions_taken:0` and nothing outside the run directory is touched.

`actions.jsonl` line (`OUTPUT-SCHEMA.md:143-163`): `{path, op, before_hash, after_hash, before_mode?, rename_to?, link_target?, started_at_ns, finished_at_ns, run_id, fixer_id, tool:"jev", ok, error?, rolled_back?}`. The file is fsynced after each line.

`capabilities --json` contains:
- `schema_version`, `doctor_contract_version`, `platform`, `subsystems`
- `detectors[{id,subsystem,kind,severity,tier,online_required,repo_required,data_sources[],estimated_cost_ms,depends_on[]}]` (DP-012)
- `fixers[{id,detector,writes_to[],ops[],preconditions[],reversible,idempotent,cardinality}]`
- `manual_remediations[{id,instruction,reason}]`
- `exit_codes` (all 11)
- `env_vars{JEV_DOCTOR_DIR, JEV_STATE_DIR, NO_COLOR, TYPESAFE_API_KEY(read presence only)}`
- `write_scopes`, `vendor_apis`, `local_backends[{name:"clef",endpoint},{name:"localbench-gateway",endpoint:"127.0.0.1:11300"}]`
- `siblings[{name:"jev-skill-gap",doctor_subcommand:null}]` (`multi-binary-toolkit.md:99-131`)
- `report_schema` (path to a JSON Schema file shipped in the package)

All of it is generated from the registry (`POLISH-BAR.md:227`).

### 3.3 Exit codes

| Code | Name | `jev doctor` / `health` / `repair` / `undo` |
|---|---|---|
| 0 | success_or_healthy | no findings · plan printed (`repair` without `--apply`) · apply fixed everything · undo restored |
| 1 | findings_present_no_fix | diagnose found ≥1 finding. **This includes no-key (`fm-secrets-no-key-source`, P0).** |
| 2 | fix_partial | `repair --apply`: verification still finds residual findings |
| 3 | fix_failed_rolled_back | a `mutate()` failed and the run was rolled back · undo failed |
| 4 | refused_unsafe | precondition unmet (out-of-scope path, edited template, hash mismatch on undo `--strict`) |
| 5 | concurrency_lost | `lock.held` owned by a live pid |
| 6 | online_required | `--only` selected only O-tier checks without `--online`. Backend down is a finding (exit 1), not exit 6. |
| 64 | usage_error | unknown flag/verb (with did-you-mean), `--dry-run` + `--apply` together |
| 66 | no_input | `--repo` given but `work/jev-inventory/expected.json` is missing |
| 73 | cant_create | cannot create the run directory |
| 74 | io_error | read or report write failed |

**Open decision for Main (shared with ErgonomicsSpec):** today no-key exits 2 (`ROBOT.md:6`, `README.md:19-20`, asserted by `kit/test/cli.test.mjs:28` and `kit/test/package.test.mjs:45`). This spec moves the doctor to exit 1 and keeps `data.backends.jev.status:"NOT_RUN"` for string readers. kit is pre-1.0 (`kit/package.json:3`), so this is a clean cutover with no shim. ErgonomicsSpec recommends that 0/1/4/5/6/64/66/73/74 be shared across all `jev` verbs, and that 2/3 be class-scoped: for decision verbs NOT_RUN/REFUSED, for doctor fix_partial/fix_failed, documented under `capabilities.commands.<cmd>.exit_codes`.

### 3.4 Repair safety envelope (project extension of `SAFETY-ENVELOPE-TEMPLATE.md:7-27`; all 10 universal rules apply unchanged)

**Default is plan-only.** `jev repair` and `jev doctor --fix` print the plan, write `report.json` plus a planned-actions list, and touch nothing else. Only `--apply` enters PLANNING → ACQUIRING_LOCK → MUTATING (`STATE-MACHINE.md:170-195`).

**Write scopes (strict; `mutate()` refuses anything else with exit 4):**

| Scope | Ops allowed | Used by |
|---|---|---|
| `$JEV_DOCTOR_DIR/**` | WriteFile, AppendFile, Rename, SymlinkAtomic | runtime artifacts, lock, quarantine |
| `$JEV_STATE_DIR/*.jsonl` | **Chmod only** (contents never rewritten, truncated or rotated) | `fx-chmod-log-0600` |
| `$home/.config/infisical/zeststream.env` | **Chmod only** | `fm-secrets-machine-config-mode` fixer |
| `R/.omp/<INSTALL_FILES key>` (`install.ts:47-49`) | WriteFile (create when missing, from `kit/templates/`) | `fx-omp-reinstall-missing`. Precondition: the manifest hash equals the template hash, or the file is absent. Edited files are refused (same rule as `install.ts:57-59`). |
| `$home/.omp/{agent,profiles/<p>/agent}/hooks/post/<hookfile>` for hookfiles in `expected.json` `group:"global"` | Rename (to quarantine), **LinkAtomic** (new op: `link(src, tmp)` then `rename(tmp, dst)`) | `fx-relink-global-hook`. Precondition: `R/<repo>` exists and its sha256 matches `git -C R show HEAD:<repo>`. |

LinkAtomic extends the 7-op enum (`MUTATE-CHOKEPOINT.md:26-44`). Undo restores the backed-up bytes with WriteFile, which is byte-identical (the inode differs, but the pre-fix state was already a non-link file).

**Never mutated (read-only forever):** `models.yml` and `config.yml` (all profiles), `.omp/config.yml`, `expected.json`, every switch file in `$JEV_STATE_DIR` (`cascade-off`, `read-screen-off`, `memory-filter-enforce`, `memory-cap3`, `fleet-router.off`; these record operator intent), log contents, LaunchAgent plists, git state.

**Never executed:** `launchctl`, `infisical login`, `kill`/signals (`daemon-cli.md:155`), `rm`, network calls without `--online`.

**Deletion:** none. Uninstall-style removal moves files into `runs/<id>/quarantine/` via Rename. The existing `uninstallOmp` `unlink` (`install.ts:93`) is moved to the same quarantine path in task T9.

**mutate() order:** lock → before_hash → scope/op check → verbatim backup with `cmp` → plan → atomic write (same-directory tmp, `fsyncSync`, `renameSync`; `typescript.md:240-282, 356-363`) → after_hash → append `actions.jsonl` (`MUTATE-CHOKEPOINT.md:9-22`). Backups are `0600` in `0700` directories (`SECURITY.md:12`).

**Conflict matrix:** `fx-omp-reinstall-missing` and `fx-relink-global-hook` both read `R` but write disjoint paths, so they may co-run. Any fixer refuses while `fm-hooks-load-failure` is open for the same file.

### 3.5 Lock (no deletion, Node built-ins only)

Rename-lock under `$JEV_DOCTOR_DIR`:
- First run creates an empty `lock.free` (AppendFile).
- Acquire: `renameSync(lock.free, lock.held)` is atomic, then write `{pid, started_at}` into `lock.held`.
- `ENOENT` means held. Read the owner: if `process.kill(pid, 0)` succeeds (P-001, `PREDICATE-LIBRARY.md:41-51`), exit 5 naming the pid. If the pid is dead, take over by rewriting the owner, recorded as a finding `fm-concurrency-stale-doctor-lock`.
- Release: `renameSync(lock.held, lock.free)`.

No `proper-lockfile` dependency (avoids dependency smuggling) and no unlink.

---

## 4. Ordered implementation tasks

Every test uses an isolated fake `HOME`, state dir and repo under `var/agent-tmp/<label>.<pid>/` (same convention as `kit/test/package.test.mjs:21-22`). The `exec` injection seam means no real `launchctl`, `infisical`, `bun`, `omp`, network or Clef. Tests live in `kit/test/doctor-*.test.mjs` so the existing `npm test` glob (`kit/package.json:31`) picks them up. Fixtures live in `kit/test/doctor_fixtures/<fm-id>/{corrupt.sh,assert.sh,README.md}`, which is outside the published `files` list (`kit/package.json:11-20`).

Base acceptance for every task: `cd kit && npx --no-install tsc -p tsconfig.json && node --test test/*.test.mjs`.

| # | Task | Files | Failing test first | Planted negative (must stay silent or refuse) | Acceptance command |
|---|---|---|---|---|---|
| T1 | Dispatch + help + typo hint + usage=64 | `kit/bin/jev.mjs`, new `kit/src/doctor/cli.ts` | `doctor-cli.test.mjs`: `jev --help` exit 0 lists `health`, `repair`, `omp install`; `jev doctr` stderr has `did you mean: jev doctor`, exit 64; `jev doctor --bogus` exit 64 | `jev doctor --robot` keyless still emits valid JSON (does not become a usage error) | `node kit/bin/jev.mjs doctr; echo $?` → `64` |
| T2 | Registry + capabilities + `expected.json` `log` fields | `kit/src/doctor/registry.ts`, `work/jev-inventory/expected.json` (add `log` to memory-filter, skill-hint, skill-veto), `work/jev-inventory/test_inventory.py` | `doctor-capabilities.test.mjs`: all 11 exit codes present (`POLISH-BAR.md:118-127`); every `fixers[].writes_to` lies inside `write_scopes` (`REGRESSION-TEST-PATTERNS.md:112-123`); every `data_sources` entry is a non-empty string | a registry entry with `writes_to:["~/.omp/agent/models.yml"]` must fail the scope test | `node kit/bin/jev.mjs doctor capabilities --json \| jq -e '.exit_codes["74"] and (.detectors\|length>20)'` |
| T3 | Run runtime: run-id, run dir, report.{json,md}, latest, FSM state, redact | `kit/src/doctor/run.ts`, `kit/src/doctor/redact.ts` | `doctor-run.test.mjs`: diagnose creates exactly `report.json`, `report.md`, `latest` (hashes every other file under fake HOME before and after: all equal, `POLISH-BAR.md:84-93`); `jq -e .schema_version` | a fake env key `sk-test-abc…` placed in a log row must appear as `<redacted…>` in `report.json` | `JEV_DOCTOR_DIR=$T node kit/bin/jev.mjs doctor --json \| jq -e .schema_version` |
| T4 | Detectors A (key resolution) — fixes D1 | `kit/src/doctor/detectors/secrets.ts` | fake HOME with no env key but `~/.local/bin/infisical` plus a `zeststream.env` containing `INFISICAL_CLIENT_ID` → **no** P0 and `key_source:"infisical-machine"` (fails against current `jev.mjs:33` logic) | fake HOME with no env, no binary, no config → P0 `fm-secrets-no-key-source`; a `models.yml` without `typesafe-key.mjs` in profile `grok` → finding cites that profile's file | `node --test kit/test/doctor-secrets.test.mjs` |
| T5 | Detectors E (log freshness, off-writing, stale schema, unparsable, mode) | `kit/src/doctor/detectors/logs.ts` | fixture `fm-logs-off-surface-writing`: expected `skill-hint:off` plus a row at now−1h → finding with instance id; fixture `fm-logs-stale-schema-writer`: a v1 row at now−2h with source constant v2 → finding | skill-hint row at now−4h → silent (3 h window); vendor-shadow last row 10 h old with zero commits since → **not** silent; `websearch-rerank` (off) with 0 rows → silent | `node --test kit/test/doctor-logs.test.mjs` |
| T6 | Detectors F (caps) + H (error spike) | `kit/src/doctor/detectors/caps.ts`, `.../anomalies.ts` | memory-filter fixture with 10 `daily-cap` rows in 24 h → `fm-caps-hit` P1 (ENFORCING) | 292 injection `status:"cap"` rows with `reason:"recipient-and-data-class-approval-required"` → **no** cap finding; error-spike fixture at 6.9% (24 h) vs 24.7% (7 d) → **no** spike | `node --test kit/test/doctor-caps.test.mjs` |
| T7 | Detectors C (Clef) + G (daemons) + D path/tools | `kit/src/doctor/detectors/{clef,daemons,omp}.ts` | injected connect-refused on 8010 → `fm-clef-unreachable`; injected `launchctl list` output without the canary label → finding; injected `command -v jev` → hermes path gives `fm-path-jev-shadowed` | connect-accepted + label present + realpath equal to the kit bin → zero findings; `--quick` runs no X-tier check (spy on `exec` asserts no `bun` or HTTP call) | `node --test kit/test/doctor-backends.test.mjs` |
| T8 | Deep-tier reuse: hook-load + inventory claim drift | `kit/src/doctor/detectors/surfaces.ts`, `work/jev-inventory/inventory.py` (new `--json` stdout-only mode, no `var/` write) + `test_inventory.py` | `test_inventory.py`: `--json` writes nothing under `JEV_INVENTORY_OUT` (directory listing unchanged); doctor parses an injected `HOOK_LOAD_FAIL ~/.omp/agent/hooks/post/x.ts: parse/import failure:3:1` into one finding with `evidence.file` | `HOOK_LOAD_OK entrypoints=78` → zero findings; with no `--repo`, every repo_required check reports `provenance:"unavailable"` and emits no finding | `python3 -m pytest work/jev-inventory/test_inventory.py -q && node --test kit/test/doctor-surfaces.test.mjs` |
| T9 | `mutate()` + rename-lock + undo + 3 fixers + quarantine cutover of `uninstallOmp` | `kit/src/doctor/{mutate,lock,undo}.ts`, `kit/src/doctor/fixers/*.ts`, `kit/src/install.ts` (unlink → mutate Rename into quarantine) | fixtures `fm-logs-mode-too-open` (0644 log), `fm-hooks-global-link-broken` (copy instead of hardlink), `fm-plugins-omp-tool-missing`: corrupt → `repair` (plan) leaves every hash unchanged → `repair --apply` → `doctor` exit 0 → `undo latest` → byte-identical to corrupted state (`REGRESSION-TEST-PATTERNS.md:79-96`); second `--apply` gives `actions_taken:0` | a write to `~/.omp/agent/models.yml` through `mutate()` → exit 4, no backup, no `actions.jsonl` line; an edited template → refused; a second concurrent `--apply` → exit 5 naming the pid; static test: no `writeFile\|unlink\|rm\(` in `kit/src/doctor/**` outside `mutate.ts` (`MUTATE-CHOKEPOINT.md:393-439`) | `node --test kit/test/doctor-repair.test.mjs kit/test/doctor-fixtures.test.mjs` |
| T10 | `health`, `explain`, `ls`, `--robot-triage`, `robot-docs`, `gc` | `kit/src/doctor/cli.ts` | `health` on a clean fake HOME: one line starting `ok `, exit 0, no run dir created; `robot-docs` contains `EXIT CODES`, `capabilities`, `NEVER do` (`POLISH-BAR.md:154-158`); triage has all 5 keys (`POLISH-BAR.md:169-174`) | `gc` without `--yes` or without `--before` → exit 64 and the run dirs are unchanged | `node kit/bin/jev.mjs health; echo $?` |
| T11 | Cutover docs/tests to the new contract | `kit/ROBOT.md`, `README.md:19-20`, `kit/test/cli.test.mjs:26-30`, `kit/test/package.test.mjs:44-46` | update assertions: keyless (no infisical in fake HOME) doctor → exit 1, `data.backends.jev.status:"NOT_RUN"` | stranger install (`npm pack`) without a repo: every repo_required check `unavailable`, exit 1 only because of the key finding | `cd kit && npm test` |

Live smoke after T11 (main agent; reads the real machine, makes no Jev or Clef calls without `--online`/`--deep`):
`node kit/bin/jev.mjs doctor --json | jq '[.findings[].id]'`. Today's state predicts these findings:
- `fm-logs-off-surface-writing` (skill-hint, D9)
- `fm-logs-stale-schema-writer` (injection v1, D8)
- `fm-logs-mode-too-open` (gate-observe.jsonl 0644)
- `fm-caps-hit` (memory-filter 689/24 h, skill-veto 123/24 h, vendor 4/24 h)
- `fm-path-jev-shadowed`
- `fm-clef-unreachable` iff `:8010` is down (not probed in this read-only pass)

None of the above is verified until T1–T11 land. **UNVERIFIED:** run `node kit/bin/jev.mjs doctor --json` after implementation.

---

## 5. Load-bearing material from the rest of `references/` (skimmed)

| File | Why it matters here |
|---|---|
| `references/methodology/SECURITY.md:29-63` | Report redaction and hash-not-bytes. The key resolver must never surface key bytes. |
| `references/recipes/distributed-cli.md:38-143` | auth_state / rate_limits FMs, `findings_only_offline`, `vendor_apis` trust manifest: the Jev and Infisical checks. |
| `references/methodology/KERNEL.md:147-157` | Provenance `live\|fallback\|unavailable`: repo-scoped checks in stranger installs. |
| `references/methodology/PERFORMANCE.md:9-32` | Tier budgets (health < 200 ms, default < 5 s) that drive the Q/D/X/O split. |
| `references/methodology/RFC.md:219-240` | `--robot` envelope shape reconciled with ErgonomicsSpec. |
| `references/methodology/GROWTH-LADDER.md:17-63` | Stage targets. Current is below Stage 1; T1–T8 reach Stage 1–2 shape; T9 reaches Stage 3–4. |
| `references/methodology/MIGRATION-GUIDE.md:11-24` | Pattern A (diagnose-only doctor → add `--fix`): the migration path used here. |
| `references/methodology/COOKBOOK.md:74-106` | Patterns 7 and 9 surfaces (`account-health`, `auth-status`); folded into A/B instead of new verbs. |
| `references/exemplars/exemplars.md:193-212` | `cass health \| capabilities \| robot-docs \| --robot-triage` four-verb discovery shape. |
| `references/methodology/DESIGN-PATTERNS.md:47-62,98-119,210-223` | DP-003 Refuse-with-Bridge (`after_user_acts`), DP-006 Bulkhead, DP-012 `depends_on`. |
| `references/recipes/monorepo-multi-cli.md` | Not adopted. `jev-skill-gap` is a sibling bin with no doctor of its own, handled through `siblings[]` (`multi-binary-toolkit.md:99-131`). |

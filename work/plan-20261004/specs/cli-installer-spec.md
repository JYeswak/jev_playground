# `jev` CLI installer spec (Phase 2)

Author: InstallerSpec, 2026-10-03. Design only; nothing under `/Users/josh/Developer/jev` was edited.

**Read in full:** `~/.agents/skills/installer-workmanship/SKILL.md` (486 lines) and all five references: `AGENT-HOOKS.md` (320), `DOWNLOAD-PATTERNS.md` (313), `GUM-RECIPES.md` (218), `PYTHON3-JSON-MERGE.md` (303), `SERVICE-MANAGEMENT.md` (260). The skill names no other skill as required. It does name two reference installers as "ALWAYS read" (SKILL.md:87-95). I fetched and grepped both: DCG `https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/main/install.sh` (I read lines 780-817, 1655-1690 and 4221-4340 in full) and RCH `https://raw.githubusercontent.com/Dicklesworthstone/remote_compilation_helper/main/install.sh` (function index only).

**Repo surface read:** `kit/src/install.ts`, `kit/bin/jev.mjs`, `kit/bin/jev-skill-gap.mjs`, `kit/src/skill-gap.ts:1179-1247`, `kit/package.json`, `kit/README.md`, `kit/ROBOT.md`, `kit/scripts/copy-questions.mjs`, `kit/templates/**` (list plus `omp/config.yml`), `kit/test/install.test.mjs`, `kit/test/package.test.mjs:19-47`, `kit/test/skill-gap.test.mjs:378-411`, and README.md §"Install Jev into omp" (README.md:28-70) plus §"Jev in omp — what is ON" (README.md:113-136). I also read the shell installers the lane already uses as precedent: `work/nev-injection/install-jev-flag.sh`, `compaction/install-jev-compact.sh`, `work/omp-guard-rule/install-guard-rule.sh:1-63`, and `docs/demos/upstream-repro/installer-grade-20260919.md`.

**Probes I ran (all read-only):**
- `node kit/bin/jev.mjs --help --robot` → usage ERROR, rc 1.
- `jev --version` → usage, rc 1.
- `jev omp install --dir /tmp/<nonexistent> --dry-run --robot` → `DRY_RUN` and rc 0. The dir was never created, and nothing checked it.
- `command -v -a jev` → `~/.local/bin/jev -> /Users/josh/Developer/jev/hermes-jev-skills/bin/jev`, a Python CLI that is **not** the kit.
- Live machine wiring, read from `~/.omp`: details are in §0.

Exit codes and status strings follow the shared dictionary that ErgonomicsSpec sent over IRC on 2026-10-03: 0 ok, 1 findings, 2 NOT_RUN (verbs), 4 refused_unsafe, 5 retryable, 6 online_required, 64 usage, 66 no_input, 73 cant_create, 74 io. I have not read `local://cli-ergonomics-spec.md` itself (UNVERIFIED).

---

## 0. What exists today (inventory)

| Surface | What it does | Source | Uninstall | Proves it fired? |
|---|---|---|---|---|
| `jev omp install --dir R [--dry-run]` | Copies 27 files (6 tools, 5 extensions, 1 post hook, 15 helpers) into `R/.omp/`. Writes a sha256 manifest `.omp/jev-kit-manifest.json`. Refuses edited or unmanaged collisions. Never writes `config.yml`. | install.ts:5-33, :35, :47-63, :52-59; jev.mjs:216-220 | `jev omp uninstall [--apply]` (dry-run by default). Keeps edited files; refuses manifest paths that escape `.omp/`. | No. It returns `extensionActivation:"MANUAL_REQUIRED"` (install.ts:62), and README.md:38 says so. |
| `jev-skill-gap --install` | Writes the LaunchAgent `ai.zeststream.jev-skill-gap-miner` (03:30 daily, wrapped in `infisical run`) and runs `launchctl bootstrap`. | skill-gap.ts:26-27, :1179-1238; jev-skill-gap.mjs:33-48 | **None.** No `--uninstall` in the help (jev-skill-gap.mjs:19-24). | No. Install checks only `launchctl print` (skill-gap.ts:1226). |
| Machine-wide post hooks | `jev-webscreen-global.ts` and `jev-injection-global.ts` sit in `~/.omp/agent/hooks/post/` and 4 named profiles: claude, codex, grok, muse. Each file has link count 6. They import absolute paths in the dev checkout. | `~/.omp/agent/hooks/post/jev-webscreen-global.ts:6-8,17`; `ls -li` | None (hand-placed). `jev-injection-global.ts:1-5` is a retired no-op "pending delete permission". | Only through scoreboard rows. |
| Machine-wide `jev-memory-filter` extension | Absolute path `/Users/josh/Developer/jev/.omp/extensions/jev-memory-filter.ts`, hand-added to `extensions:`. | `~/.omp/agent/config.yml:38`; `profiles/claude/agent/config.yml:34`; `codex:45`; `grok:30`; `muse:36` | None (hand-edited; one manual `config.yml.bak-20260927T0010Z`) | Scoreboard: 455k tokens removed in 7 days (conductor scoreboard 2026-10-04) |
| `jev-latest-canary` LaunchAgent | `/bin/zsh -lc "cd <repo> && infisical run … python3 scripts/jev-latest-canary.py"` at 09:07. | `plutil -p ~/Library/LaunchAgents/ai.zeststream.jev-latest-canary.plist`; no plist source in git | None | Log line in `~/.local/state/jev/jev-latest-canary.log` |
| Clef server | Throwaway `serve.py`, gitignored. The process running on :8010 is pid 88863. | `var/agent-tmp/clef-flash.conductor/serve.py:1,40`; `.gitignore:10` | n/a | GET `/` lists `clef-flash` (local://clef-backend-spec.md:4) |
| Per-feature shell installers | jev-flag (project config append), guard-rule (profile `hooks/pre/`), jev-compact (project lib), harm-rule | install-jev-flag.sh:1-27; install-guard-rule.sh:1-36; install-jev-compact.sh:1-17 | Manual (`.bak` once, install-jev-flag.sh:104) | jev-flag only: L2 probe with a `--no-extensions` negative arm (install-jev-flag.sh:73-93) |
| `jev-skill-hint` | Declared PARKED/OFF (README.md:130). It produced 2,989 rows in 7 days (conductor scoreboard 2026-10-04). It is not listed in any profile `config.yml` or in `.omp/config.yml:84-110`. | grep above | n/a | The **loader path is UNVERIFIED**. [INFERENCE] native `<cwd>/.omp/extensions` auto-discovery (.omp/config.yml:39-42) |

Three consequences for the spec:
1. Nothing installs the surfaces that actually run machine-wide. They are hand-placed, they point into a dev checkout, and they have no manifest and no uninstall.
2. The declared state and the running state already diverge (skill-hint). The installer and doctor must check **firing**, not just placement.
3. Another program already owns the name `jev` on PATH.

---

## 1. Gap table: installer-workmanship requirement vs kit today

Legend: PASS = met. GAP = missing or partial. N/A = does not apply, with the reason. "No shell installer" means `git ls-files` shows no `install.sh` under `kit/` and the package `files` list ships none (kit/package.json:11-20). Every row cites the skill side and the kit side.

### 1a. Non-negotiables (SKILL.md:18-43)

| # | Requirement | Skill | Kit today | Verdict | Reason / spec response |
|---|---|---|---|---|---|
| N1 | `set -euo pipefail` | SKILL.md:20 | No shell installer (kit/package.json:11-20). Precedent scripts use only `set -u` (install-jev-flag.sh:29). | GAP | `kit/install.sh` starts `set -euo pipefail`. |
| N2 | `shopt -s lastpipe` | SKILL.md:21 | none (as N1) | GAP | Add after N1. |
| N3 | One-liner header with cache buster | SKILL.md:22; DOWNLOAD-PATTERNS.md:7-39 | README documents only checkout use: `npx --prefix kit` (README.md:18-25, :33) | GAP | §2.1 header. |
| N4 | Proxy `PROXY_ARGS` | SKILL.md:23; DOWNLOAD-PATTERNS.md:43-66 | No downloads exist (install.ts reads only local templates, :55) | GAP | Pass to every curl call. `npm` honours `HTTPS_PROXY` natively, and the spec relies on that for channel B. |
| N5 | Gum detection + ANSI fallback | SKILL.md:24; GUM-RECIPES.md:9-16 | CLI prints plain text or `--robot` JSON (jev.mjs:24-26, :219) | GAP | Shell bootstrap only. The TS `jev install` keeps the `--robot` JSON contract (ROBOT.md:3-7). |
| N6 | `draw_box()` | SKILL.md:25; GUM-RECIPES.md:174-203 | none | GAP | Use the summary box in the shell layer, rendered from the JSON that `jev install` returns. |
| N7 | `info/ok/warn/err` | SKILL.md:26 | Single-line `process.stdout.write` (jev.mjs:219, :224) | GAP | Shell layer. |
| N8 | `run_with_spinner` | SKILL.md:27; GUM-RECIPES.md:107-119 | none | GAP | Wrap curl, `npm install`, and the omp probe. Spin external commands only (GUM-RECIPES.md:116-119). |
| N9 | Branded banner | SKILL.md:28, :166-179 | none | GAP | "jev installer — typed decisions for code". |
| N10 | Platform detection | SKILL.md:29, :187-202 | none. No `engines` in kit/package.json:1-33 | GAP | OS {darwin, linux} plus `node >= 22` (the tests rely on `--experimental-strip-types`, install.test.mjs:46). No Rust triple is needed: **musl (SKILL.md:205) is N/A**, because this is a Node package. |
| N11 | Preflight (disk, perms, net) | SKILL.md:30, :219-226 | None. `--dry-run` on a missing dir returns DRY_RUN rc 0 (probe above; install.ts:47-62 never checks the target) | GAP | §2.3 preflight. It also runs under `--dry-run`. |
| N12 | Atomic mkdir lock | SKILL.md:31; DCG install.sh:1659-1680 | None. Writes are non-atomic `writeFile` (install.ts:61). skill-gap uses `writeAtomic` for the plist only (skill-gap.ts:253, :1234). | GAP | `~/.local/state/jev/install/lock.d` with pid and stale-pid takeover. |
| N13 | SHA256 checksum | SKILL.md:32; DOWNLOAD-PATTERNS.md:109-136 | Per-file sha256 **after install** in the manifest (install.ts:36-37, :61). There is no artifact verification. | GAP | Verify the release `.tgz` against `SHA256SUMS` using `sha256sum` or `shasum -a 256`. Channel B relies on npm `integrity`. |
| N14 | Sigstore/cosign | SKILL.md:33; DOWNLOAD-PATTERNS.md:140-179 | none | GAP | Asymmetric: no cosign → warn and continue; cosign present with a bad signature → exit 4. Channel B: `npm publish --provenance` plus `npm audit signatures` in `--verify`. |
| N15 | Build-from-source fallback | SKILL.md:34; DOWNLOAD-PATTERNS.md:275-300 | Already available in a different form: `prepare` builds dist (kit/package.json:29), and the package test packs from source (package.test.mjs:32-42) | GAP (partial) | Tier 4 = `git clone --depth 1` + `npm ci --prefix kit` + `npm pack`, then install that tgz. |
| N16 | Shell completions | SKILL.md:35, :359-370 | no `completions` verb (jev.mjs:209-230) | GAP | `jev completions bash\|zsh\|fish`. Install to XDG paths. |
| N17 | AI agent auto-config | SKILL.md:36, :293-328 | Project-scoped omp copy only (install.ts:47-63). Profile wiring is by hand (§0). | GAP | omp gets profile targets (§2.2). Claude Code, Codex, Gemini, Cursor, Aider, Copilot and Continue are **reported** as `unsupported` (row A3), never silently skipped. |
| N18 | Skill install, tarball + inline fallback | SKILL.md:37, :332-351; RCH `install_skill()` | No skill in INSTALL_FILES (install.ts:5-33). The repo ships `.omp/skills/jev-tools/SKILL.md` and `.omp/skills/jev-compact/SKILL.md`. | GAP | Install from inside the verified package (no second download) into the single store `~/.agents/skills/<name>`, with symlinks per agent. This respects the one-store topology that `ai.zeststream.skill-topology-gate` checks. |
| N19 | Final summary with per-agent status | SKILL.md:38, :393-421 | One line: `READY: copied N files` (jev.mjs:219) | GAP | Per target × profile: `created\|merged\|already\|conflict\|unsupported\|skipped\|failed` (PYTHON3-JSON-MERGE.md:292-303), plus backups and the L-level reached. |
| N20 | Uninstall instructions | SKILL.md:39; GUM-RECIPES.md:145-153 | `jev omp uninstall` exists (jev.mjs:221-225), but no output mentions it, and the skill-gap LaunchAgent has none. | GAP (partial) | The footer prints `jev uninstall all --apply` and the rollback command. |
| N21 | `--quiet`, `--no-gum`, `--force` | SKILL.md:40 | None of the three. `--robot` only (jev.mjs:207). | GAP | Add all three. `--force` is limited to backing up and replacing marker-owned or hash-matching files (never foreign files). |
| N22 | `--offline TARBALL` | SKILL.md:41; DOWNLOAD-PATTERNS.md:183-203; RCH `install_from_tarball()` | Templates are local, so `omp install` already works offline (install.ts:55). There is no tarball mode. | GAP | §2.5. The tgz bundles `@typesafe-ai/sdk` (zero deps, verified from `node_modules/@typesafe-ai/sdk/package.json`). |
| N23 | `trap cleanup EXIT` | SKILL.md:42; DCG install.sh:1682-1685 | none | GAP | Removes `$TMP` and the lock. |
| N24 | `umask 022` | SKILL.md:43 | Files are written with explicit mode 0644 (install.ts:61). The plist is 0600 (skill-gap.ts:1234). | GAP (partial) | Add `umask 022`. Keep 0600 for plists that carry the Infisical project id. |

### 1b. THE PLAN steps not already covered above (SKILL.md:51-81)

| # | Requirement | Skill | Kit today | Verdict | Reason / spec response |
|---|---|---|---|---|---|
| P1 | `--help` documents ALL flags | SKILL.md:55, :451 | `jev --help` → usage ERROR rc 1 (probe; jev.mjs:227). `jev-skill-gap --help` documents its flags (jev-skill-gap.mjs:19-24). | GAP | `jev install --help` and `install.sh --help` list every flag in §2.1. |
| P2 | WSL detection, warn only | SKILL.md:58, :207-214; DOWNLOAD-PATTERNS.md:304-313 | none | GAP | Warn. Daily jobs on WSL → `skipped` (no systemd user session guaranteed). |
| P3 | Version resolution cascade | SKILL.md:60; DOWNLOAD-PATTERNS.md:207-243 | `version: "0.0.0"` (kit/package.json:3). No tags or releases read. | GAP | Order: `--version` → `JEV_VERSION` → GitHub API latest on `JYeswak/jev_playground` (origin per `git remote get-url origin`) → redirect parse → the version embedded in the installer. The Cargo tier is N/A. |
| P4 | Artifact URL 4-tier fallback | SKILL.md:61, :262-269; DOWNLOAD-PATTERNS.md:70-105 | none | GAP | Tier 1 `releases/download/v$V/jev-kit-$V.tgz`, tier 2 `releases/latest/download/jev-kit.tgz`, tier 3 N/A (no per-platform build of a pure-JS package), tier 4 source (N15). `rm -rf "$TMP"` before the fallback. |
| P5 | Existing-install check | SKILL.md:62, :223 | doctor reports project omp presence only (jev.mjs:52; install.ts:97-102) | GAP | Read `~/.local/state/jev/install/manifest.json` and `jev --version`. Also detect the **foreign** `jev` on PATH (§0). |
| P6 | Stale-PID lock | SKILL.md:63, :455 | none | GAP | As N12. |
| P7 | `install -m 0755` | SKILL.md:66; DOWNLOAD-PATTERNS.md:247-271 | npm `bin` linking (kit/package.json:7-10). The bin file mode is set by npm. | N/A | Node package. npm creates the shim. The installer `ln -sfn` links `~/.local/share/jev/current/node_modules/.bin/jev`, and `--verify` asserts it is executable. |
| P8 | PATH setup, `--easy-mode` | SKILL.md:70, :374-388; anti-pattern :432 | none | GAP | Warn when `~/.local/bin` is not on PATH. Edit rc files only with `--easy-mode`, and never when `JEV_NO_RC=1` (the RCH `setup_path()` rule). |
| P9 | Service management if daemon | SKILL.md:71; SERVICE-MANAGEMENT.md:7-12 | One LaunchAgent with no uninstall and no Linux unit (skill-gap.ts:1213-1238) | GAP | §2.2 `daily` and `clef` targets. launchd on darwin; systemd user timer/service on linux. |
| P10 | Agent detection | SKILL.md:72, :296-305; AGENT-HOOKS.md:234-276 | none | GAP | Detect omp (`command -v omp`, `~/.omp`) and enumerate profiles under `~/.omp/profiles/*/agent/config.yml`. Other agents are detected only so the summary can report them (A3). |
| P11 | Hook auto-config | SKILL.md:73, :308-318 | Copy only. Activation is manual (install.ts:62; README.md:36-38). | GAP | §2.2 `omp-profile`. |
| P12 | Self-test / `--verify` | SKILL.md:77; DCG `run_install_self_test()` install.sh:780-817; RCH `run_doctor()` | `jev doctor` checks key and SDK presence only (jev.mjs:32-56) | GAP | §2.6 L0–L4 ladder. Modeled on DCG's allow and deny probes, which require both exit code and structured output. |
| P13 | Predecessor detection + migration | SKILL.md:78; DCG `detect_predecessor()` install.sh:1831 | Refuses a v1 manifest that owns `config.yml` (install.ts:52-54) | GAP (partial) | Predecessors: hand-placed global hooks, absolute-path `memory-filter` entries, the hand-made canary plist, `hermes-jev-skills` `~/.local/bin/jev`. Each is reported with an upgrade banner and migrated only with `--migrate`, after a backup. |
| P14 | Summary box | SKILL.md:79 | as N19 | GAP | as N19 |
| P15 | Uninstall/revert instructions | SKILL.md:80 | as N20 | GAP | as N20 |

### 1c. Behaviour rules (SKILL.md body, anti-patterns, checklist)

| # | Requirement | Skill | Kit today | Verdict | Reason / spec response |
|---|---|---|---|---|---|
| B1 | Already-installed short-circuit still configures | SKILL.md:278-287, :466 | Re-running an identical install exits 0 and rewrites the same bytes (install.test.mjs:48-50; install.ts:61 always writes) | GAP (partial) | Same version: no writes (mtime-preserving test). Agent and profile config still re-checks and reports `already`. Note: DCG's current short-circuit (the block just before `LOCK_DIR=` at install.sh:1659, seen in my :1655-1690 fetch) runs `maybe_install_completions` and then `exit 0`, without reconfiguring agents. This spec follows the skill text instead. |
| B2 | Hook config: check → backup → merge or create → status | SKILL.md:313-317; PYTHON3-JSON-MERGE.md:26-63 | Refuses rather than merges (install.ts:52-59). Precedent installers append YAML text (install-jev-flag.sh:104-105). | GAP | YAML parse-merge (B4). Timestamped backup before any write. |
| B3 | Backup before modifying settings | SKILL.md:431; PYTHON3-JSON-MERGE.md:61-63 | install.ts never modifies foreign files (passes by refusal). Precedents keep one `.bak` forever (install-jev-flag.sh:104). | GAP (partial) | `<file>.bak.<UTC>`, recorded in the manifest. |
| B4 | Never write structured config by hand; merge with a parser | SKILL.md:438; PYTHON3-JSON-MERGE.md:9-14 | install.ts deliberately does not write `config.yml` (README.md:36). Text append in precedent produced unparseable YAML that still reported GREEN (installer-grade-20260919.md:16-27). | GAP | Use a YAML parser (dependency declared in package.json, so no smuggling). Read back after write. Refuse inline-flow or non-list `extensions:` with exit 4 instead of guessing. |
| B5 | Array merge must append, never replace | PYTHON3-JSON-MERGE.md:243-245 | omp replaces `extensions` arrays across scopes (.omp/config.yml:91-96), which is why install.ts:52-54 refuses | GAP | Merge appends only our marker-identified entries. Never reorders or drops host entries. A read-back asserts `old ⊆ new`. |
| B6 | Tolerant load (corrupt file → `{}`) | PYTHON3-JSON-MERGE.md:180-188 | install.ts refuses invalid manifests (:40-46 `readManifest`) | N/A (deliberately rejected) | For omp `config.yml`, treating a corrupt file as empty would erase the operator's safety extensions (B5). A parse failure → `failed`, exit 4, file untouched. |
| B7 | Dedup by binary name | PYTHON3-JSON-MERGE.md:190-196 | The manifest keys by destination (install.ts:61). Precedent counts exact lines (install-jev-flag.sh:1-27 "LIMIT"). | GAP | Dedup by resolved path **and** basename `jev-*.ts`, so an absolute dev-checkout entry and a packaged entry for the same family are not both loaded. |
| B8 | Rollback on merge failure | PYTHON3-JSON-MERGE.md:155-172, :201-205 | n/a (never merges) | GAP | Restore from the backup when the read-back or parse fails. Status `failed`. |
| B9 | Status vocabulary | PYTHON3-JSON-MERGE.md:292-303; AGENT-HOOKS.md:61, :124 | `READY\|DRY_RUN` and `REMOVED\|DRY_RUN` only (install.ts:37, :65). skill-gap uses `INSTALLED\|ALREADY_LOADED\|REFUSED\|ERROR` (:1221). | GAP | One vocabulary across targets: `created\|merged\|already\|conflict\|unsupported\|skipped\|failed`, plus top-level `PLANNED\|INSTALLED\|PARTIAL\|REFUSED`. |
| B10 | Conflict marker: never overwrite another tool's file | AGENT-HOOKS.md:218-220; DCG `configure_omp()` "not generated by dcg" (install.sh:4300-4330) | Refuses unmanaged or edited files (install.ts:57-59; tests install.test.mjs:52-55, :71-80) | PASS (project scope) / GAP (profile scope, PATH) | Extend to profile files, plists and `~/.local/bin/jev`. A foreign file gets `conflict`, exit 4. |
| B11 | Hard-fail only on core; warn on optional | SKILL.md:433 | An omp install error throws → exit 1 for the whole run (jev.mjs:231-235) | GAP | Per-target status. Exit 0 only when every requested target is `created\|merged\|already`. Otherwise exit 1 (findings) with partial status. Exit 4 for refusals. |
| B12 | mkdir lock, not flock | SKILL.md:434 | none | GAP | as N12 |
| B13 | Scan notice before slow ops | SKILL.md:436, :465; DCG `print_agent_scan_notice()` install.sh:246 | none | GAP | Print a notice before the omp rpc probes, which take ≤25 s each per profile (install-jev-flag.sh:73-74 `--max-time=25`). |
| B14 | `--version` probes under timeout | SKILL.md:437; AGENT-HOOKS.md:280-294 | none | GAP | `timeout 1`/`gtimeout 1` around `omp --version` and `node --version`. |
| B15 | Dual checksum tool | SKILL.md:439, :469; DOWNLOAD-PATTERNS.md:109-136 | none | GAP | as N13 |
| B16 | Proxy on every curl | SKILL.md:440, :467 | none | GAP | as N4 |
| B17 | `[ -t 1 ]` before gum | GUM-RECIPES.md:16 | none | GAP | as N5 |
| B18 | Interactive confirm with non-TTY default | GUM-RECIPES.md:123-139; SERVICE-MANAGEMENT.md:206-231 | none | GAP | **Changed default:** non-interactive runs (`curl\|bash`) install the CLI only. LaunchAgents and `clef` need explicit `--with daily`/`--with clef`. Profile hooks need `--profiles`. Reason: the skill's "non-interactive → yes" default (SERVICE-MANAGEMENT.md:216-217) would start paid daily model calls unattended. |
| B19 | Tested `--quiet` / `--no-gum` / `--offline` | SKILL.md:470-472 | The package test covers a stranger install (package.test.mjs:19-47) but not these flags | GAP | Tests T3–T5 in §3. |
| B20 | Linux static linking | SKILL.md:205, :430 | Pure JS (kit/package.json:5) | N/A | No native binary. |

### 1d. Service management (SERVICE-MANAGEMENT.md)

| # | Requirement | Skill | Kit today | Verdict | Reason / spec response |
|---|---|---|---|---|---|
| S1 | launchd plist with explicit log paths | SERVICE-MANAGEMENT.md:74-131 | Present: StdOut/StdErr to `~/Library/Logs/jev-skill-gap-miner.log` (skill-gap.ts:1180, :1206-1207) | PASS | Keep. |
| S2 | Unload before load on upgrade | SERVICE-MANAGEMENT.md:88-91, :129 | Already loaded → `ALREADY_LOADED` with **no content comparison**, so a stale plist is never refreshed (skill-gap.ts:1226-1227). A file present but not loaded → `REFUSED` (:1228-1230). | GAP | Render the plist, then compare bytes. Equal and loaded → `already`. Different → `bootout`, atomic write, `bootstrap`, then `merged`. A foreign file without the marker → `conflict`. |
| S3 | KeepAlive/RunAtLoad for daemons | SERVICE-MANAGEMENT.md:107-110, :130 | Daily job uses calendar, `RunAtLoad false`, `ThrottleInterval 600` (skill-gap.ts:1203-1205). This is correct for a batch job. | PASS (batch) / GAP (clef) | `clef` gets `KeepAlive` + `RunAtLoad`. |
| S4 | systemd user unit + linger | SERVICE-MANAGEMENT.md:16-71 | darwin only (skill-gap.ts:1222 `Library/LaunchAgents`) | GAP | `~/.config/systemd/user/jev-<job>.{service,timer}` with `Persistent=true`. `loginctl enable-linger` only with `--with daily` on linux. |
| S5 | Uninstall service | SERVICE-MANAGEMENT.md:236-258 | none (jev-skill-gap.mjs:19-24) | GAP | `launchctl bootout gui/$UID/<label>` + rm, or `systemctl --user disable --now` + rm + `daemon-reload`. |
| S6 | Preserve config and state on uninstall | SERVICE-MANAGEMENT.md:260 | State lives in `~/.local/state/jev/skill-gap-miner/` (skill-gap.ts:1245-1247). No uninstall exists to preserve it. | GAP | Uninstall never deletes `~/.local/state/jev/**` (reports, cursors, logs). `--purge` lists them and needs `--apply`. |
| S7 | Daemon restart fallback | SERVICE-MANAGEMENT.md:163-202 | none | GAP | `jev clef restart` → `launchctl kickstart -k` → bootout/bootstrap. |
| S8 | Program points at an installed binary | (implied by SERVICE-MANAGEMENT.md:38, :102 `binary_path`) | The plist runs `<repoRoot>/kit/bin/jev-skill-gap.mjs` from the **dev checkout** (skill-gap.ts:1186-1187). The canary runs `cd <repo>` (plist). | GAP | Run `~/.local/share/jev/current/bin/jev skill-gap --daily`. A checkout move or `git checkout` must not change what runs at 03:30. |

### 1e. Agent-hook formats (AGENT-HOOKS.md)

| # | Requirement | Skill | Kit today | Verdict | Reason / spec response |
|---|---|---|---|---|---|
| A1 | Claude Code PreToolUse merge into `~/.claude/settings.json` | AGENT-HOOKS.md:7-61 | none | N/A (v1), reported | No measured jev seam in Claude Code. The measured seams are omp-only (README.md:113-136). Installing an unmeasured hook means installing silence (install-jev-flag.sh:24-27 lists measured-profile-only as policy). The summary prints `claude-code: unsupported (no measured jev seam)`. |
| A2 | Codex `~/.codex/hooks.json` | AGENT-HOOKS.md:108-124 | none | N/A (v1), reported | Same reason as A1. Also note: omp's `codex` profile measured ABSENT for jev extensions (install-jev-flag.sh:56; .omp/config.yml:47-48). That is a separate omp-profile fact and is handled in §2.2. |
| A3 | Gemini/agy, Aider, Copilot, Cursor, Continue | AGENT-HOOKS.md:65-232 | none | N/A (v1), reported | Same as A1. Each detected agent gets the status `unsupported`. |
| A4 | Detection function with dirs + commands | AGENT-HOOKS.md:234-276 | none | GAP | Implement it for the summary. omp is the only configured target. |
| A5 | Print detected agents | AGENT-HOOKS.md:298-320 | none | GAP | Shell layer. |
| A6 | omp profile resolution (`OMP_PROFILE`, `PI_CODING_AGENT_DIR`, `PI_CONFIG_DIR`) | DCG `resolve_omp_agent_dir()` install.sh:4221-4275 (reference installer, SKILL.md:87) | `OMP_HOME` only, in a precedent script (install-guard-rule.sh:47). The kit has none. | GAP | Port DCG's resolver into TS (`kit/src/install/omp-paths.ts`) with its fixture cases. |

---

## 2. Install spec for the single `jev` CLI

### 2.1 Entry points

```text
# Channel A — curl|bash (primary; works with no npm registry account):
curl -fsSL "https://raw.githubusercontent.com/JYeswak/jev_playground/main/kit/install.sh?$(date +%s)" | bash
curl -fsSL "https://raw.githubusercontent.com/JYeswak/jev_playground/main/kit/install.sh?$(date +%s)" | bash -s -- --with daily --profiles measured

# Channel B — npm (registry name `jev-kit` availability UNVERIFIED; `npm view jev-kit` not run):
npm i -g jev-kit@<ver> && jev install all --apply

# Airgap:
bash install.sh --offline ./jev-kit-<ver>.tgz --checksum <sha256>
```

The shell layer is thin. It does preflight, lock, download, verify, extract, and the PATH link. Then it runs `exec "$JEV" install <targets> --apply --robot` and renders the returned JSON as the gum/ANSI summary. All integration logic lives in TypeScript, unit-testable with `node:test` like install.ts today. This mirrors DCG delegating omp wiring to `dcg install --omp --force` (DCG install.sh:4277-4300).

Flags, which `--help` must list in full:

`--version vX.Y.Z`, `--dest DIR` (default `~/.local/share/jev`), `--bin-dir DIR` (default `~/.local/bin`), `--bin-name NAME`, `--take-over-bin`, `--with daily|clef|skills` (repeatable), `--profiles default,claude,…|measured|none`, `--dir REPO` (project scope), `--dry-run`, `--apply` (`jev install` only; `install.sh` implies it unless `--dry-run`), `--verify`, `--offline TARBALL`, `--checksum HEX`, `--no-verify` (skips checksum and signature, prints a warning), `--from-source`, `--force`, `--migrate`, `--easy-mode`, `--quiet`, `--no-gum`, `--uninstall`, `--rollback`, `--robot`.

### 2.2 What it installs (targets)

`jev install <target…> [--dry-run|--apply]`. `jev omp install|uninstall` stay as aliases (ErgonomicsSpec IRC 2026-10-03).

| Target | Writes | Default in `curl\|bash` | Rules |
|---|---|---|---|
| `cli` | `~/.local/share/jev/versions/<ver>/` (npm `--omit=dev --ignore-scripts --offline` install of the verified tgz); symlink `~/.local/share/jev/current`; `~/.local/bin/jev` → `current/node_modules/.bin/jev`; also `jev-skill-gap` | **yes** | If `~/.local/bin/jev` exists and does not resolve into `~/.local/share/jev/` → `conflict`, exit 4. Today it is `hermes-jev-skills/bin/jev`. With `--take-over-bin`, the old link target goes into the manifest and uninstall restores it. `--bin-name` is the alternative. Keep the 2 newest versions for `--rollback`. |
| `omp-project --dir R` | Exactly today's `installOmp` (install.ts:47-63) and its v1 manifest (:35) | no | Unchanged semantics. It gains preflight (R exists, is writable, is a git repo) and the shared status vocabulary. |
| `omp-profile --profiles P` | Per family (see `families.json` below): post/pre **hook shims** in `<agentDir>/hooks/{pre,post}/jev-<family>.ts` (directory-discovered, so no config edit; install-guard-rule.sh:17-24). For extension families: a parse-merged append to `<agentDir>/config.yml` `extensions:` with the packaged absolute path, a timestamped backup, and a read-back. Shims import from `~/.local/share/jev/current/omp/…`, **never** from a dev checkout (today: jev-webscreen-global.ts:6-8). | no (`--profiles` required) | `measured` = only the profiles in which the family's L2 probe was recorded. An unmeasured profile → `unsupported` unless `--force-profile`. codex is ABSENT for extensions (install-jev-flag.sh:56). Each shim's first line is the marker `// jev-kit:managed family=<id> v=<ver>`. With `--migrate`, a predecessor (hand-placed hardlink or absolute dev path) is backed up and replaced; without it → `conflict`. |
| `daily` | launchd plists (darwin) or systemd user timers (linux) for: `jev skill-gap --daily` 03:30 (skill-gap.ts:1203); `jev canary` 09:07 (replaces the hand-made plist); `jev census --days 7` (local only, no model calls; wraps `work/omp-jev-review/surface-census.py --scoreboard`) | no (`--with daily`) | Key source is auto-detected: `infisical` (`~/.local/bin/infisical`, skill-gap.ts:1240-1243), then `env`, then `none`. When the source is `none`, model-calling jobs → `skipped (keyless)` and local-only jobs (census) still install. Each plist has the marker as an XML comment. Logs go to `~/Library/Logs/jev-<job>.log`. |
| `clef` (optional) | LaunchAgent `ai.zeststream.jev-clef`: `KeepAlive`, `RunAtLoad`, explicit logs, running the **tracked** server from clef-backend-spec T0 (`work/clef-serve/serve.py`, packaged under `kit/clef/`) with `--model DIR` | **never** in `all` | Requires `--clef-model DIR`. The installer never downloads weights (size UNVERIFIED). Refuse a non-loopback bind (local://clef-backend-spec.md:120). The Platt maps ship as `kit/calibration/clef/*.json` (clef-backend-spec T2). Blocked until T0 lands: the server is untracked today (`.gitignore:10`). |
| `skills` | `~/.agents/skills/jev-tools/`, `~/.agents/skills/jev-compact/` copied from the package; symlinks only where the operator's skill topology already links them | no (`--with skills`) | A store dir that exists without the marker → `conflict`. |
| `all` | `cli` + `skills` + `omp-profile --profiles measured` + `daily` | — | Never includes `clef`. |

`kit/install/families.json` is the single source for profile wiring:

`{id, surface: hook-post|hook-pre|extension|tool, module, profiles_measured[], probe ("xd://jev_<x>_ext_probe" or "load-row"), fire_fixture, log_path, declared: on|shadow|off, receipt}`

Seed values are taken from README.md:115-130 (memory-filter on, web-duel inj annotate-on with web shadow, gate cascade on, skill-veto shadow, skill-hint off, web rerank off). A family declared `off` is **never** installed. Doctor flags rows that a declared-`off` family produced as RED drift (the skill-hint case, §0).

### 2.3 Preflight (also runs under `--dry-run`)

These steps run in order, and the first failure stops the run:

1. `uname` gives darwin or linux; WSL is a warning only.
2. `node --version` (with a 1 s timeout) is at least 22. Otherwise exit 6 with the install hint.
3. The target directory has at least 50 MB free (`df -Pk`; 50 MB is a design choice).
4. `--dest` and `--bin-dir` can be created and written to.
5. The artifact URL answers `curl --connect-timeout 3`. This check is skipped under `--offline`.
6. The existing install manifest and version are read.
7. Foreign files are listed: the `jev` bin, the hand-placed hooks, and the dev-path entries in `extensions:`.
8. `omp` is on PATH. If it is not, every `omp-profile` row becomes `skipped`.

### 2.4 Idempotence

- **State.** `~/.local/state/jev/install/manifest.json` v2 has entries `{target, path, sha256, marker, version, backup?, displaced?}`. The project-scope v1 manifest stays where it is (install.ts:35).
- **Same version, same plan.** Zero writes. Every row reads `already` and the exit code is 0. A test asserts that the mtimes did not change.
- **Edited managed file.** The row is `conflict` (exit 4). `--force` writes `<file>.bak.<UTC>` and then replaces the file.
- **Foreign file.** The row is `conflict`. `--force` does not override this. Only `--migrate` (for known predecessors) or `--take-over-bin` changes it.
- **Writes.** Each file is written to a temp file and then renamed into place. `config.yml` is written once per profile, after the parse-merge, and is read back afterwards.
- **Locking.** An mkdir lock with a pid file. A lock whose pid is dead is taken over (DCG install.sh:1659-1680).

### 2.5 Offline and keyless behaviour

| Condition | Behaviour |
|---|---|
| `--offline TGZ` | No network calls. The tarball's sha256 must match `--checksum` or a `SHA256SUMS` file beside it. If neither exists, the run stops with exit 66, unless `--no-verify` is given (which prints a loud warning). Sigstore is skipped with a warning when no bundle sits beside the tarball. The tarball bundles `@typesafe-ai/sdk` (`bundleDependencies`; the SDK has zero dependencies), so `npm install --offline` succeeds. |
| No network, no `--offline` | Exit 6 (online_required), with the exact `--offline` command printed. |
| No `TYPESAFE_API_KEY` / no Infisical | The install still completes. Installed tools, hooks and verbs return `NOT_RUN` (README.md:50; kit/README.md:13-14). Model-calling daily jobs are `skipped (keyless)`. The summary says "installed, keyless". |
| Clef down | `jev clef …` verbs return `NOT_RUN reason:clef-unreachable`. Doctor reports `clef.reachable DOWN` (clef-backend-spec:119), and that does not affect READY. |

### 2.6 Verification that proves it fired

`jev install --verify` runs automatically after `--apply`. `jev doctor --install` runs the same checks on demand and is read-only. Each row records the highest level it reached:

| Level | Check | Source pattern | Planted negative that must fail |
|---|---|---|---|
| L0 placed | Every manifest path exists, its sha256 matches, and the marker is present | install.ts:84-90 | Flip one byte → `conflict` |
| L1 loads | The installed module imports: `node --experimental-strip-types -e 'await import(<path>)'` | install.test.mjs:46-47 | A module with a syntax error → `failed` |
| L2 listed | `omp --profile=P --mode=rpc` `get_state.systemPrompt` contains the family probe. The same request with `--no-extensions` must not contain it. A nonce tool name must be absent. Hooks without a probe tool write a `load` row containing the install nonce to `~/.local/state/jev/hook-loads.jsonl` when the factory loads. | install-jev-flag.sh:73-93; .omp/config.yml:57-60 (do **not** use `dumpTools`, :51-55) | The negative arm shows the probe → the oracle is broken, row `failed` |
| L3 fires | The installed module's factory is driven by a stub `pi` with the family's `fire_fixture` event and a fake transport (no network). The hook's decision log must gain one row containing the install nonce. For daily jobs: write the nonce to `~/.local/state/jev/install/probe`, run `launchctl kickstart -k gui/$UID/<label>`, and wait up to 30 s for a log line carrying the nonce. The job sees the probe file, writes a keyless probe row, and exits 0 with no model call. Then `launchctl print` must show `last exit code = 0`. For Clef: `GET /` must list `clef-flash` (and a fingerprint once T0 lands), and POSTing one captured Banking77 row must return the recorded label, with Platt(p) within 1e-3 of the recorded value. | DCG `run_install_self_test()` (both a positive and a negative probe, and both exit code and structured output, install.sh:780-817); installer-grade-20260919.md:76-78 (import the shipped module, drive it through a stub pi) | The fixture's harmful event yields no row → `failed`. A Clef URL pointing at a dead port → `NOT_RUN` (not `READY`). |
| L4 organic | `jev doctor --since 24h` counts real decision rows per family and profile from each family's `log_path`, in the conductor-scoreboard style. Declared `on` with 0 rows while ≥1 session ran in that profile → RED. Declared `off` with >0 rows → RED drift. | conductor scoreboard 2026-10-04 (skill-hint 2,989 rows while declared OFF) | Empty logs while sessions exist → RED, not GREEN |

The summary prints the level each row reached. It must never print "fired" for a row below L3. The closing line reuses install-jev-flag.sh:123: "Installed ≠ useful: L4 organic precision is measured only by `jev doctor --since`."

### 2.7 Uninstall and rollback

- `jev uninstall <target|all> [--apply]`. Without `--apply` it only reports, consistent with jev.mjs:223 and install.test.mjs:94-105.
  - It removes manifest entries whose hash still matches. Edited entries are kept and listed (install.ts:84-90).
  - For `config.yml`, it removes only our marker entries by parse-merge, then reads the file back. It does not restore a backup wholesale, because the operator may have edited the file since.
  - It runs `bootout` and then rm for each plist.
  - It restores the displaced `jev` bin.
  - It never touches `~/.local/state/jev/**` unless both `--purge` and `--apply` are given.
- `install.sh --uninstall` → `exec jev uninstall all --apply`.
- `jev install --rollback` points `current` at the previous version directory, re-renders shims and plists (byte-compare, then bootout/bootstrap when they differ), and then re-runs L0–L3.

---

## 3. Ordered implementation tasks

Every task is test-first. Each test is written red against today's code, and its planted negative must make the new code fail. Tests run with `node --test kit/test/<file>`. Each acceptance command is the single command whose exit code closes the task. Commands are run against temporary `HOME` and `OMP_HOME` fixtures, never the real profile.

| # | Files | Test (written first) | Planted negative (must turn it red) | Acceptance command |
|---|---|---|---|---|
| T1 | `kit/src/install/plan.ts` (plan model, status vocabulary, exit-code map), `kit/bin/jev.mjs` (`install`/`uninstall` dispatch; `omp install` alias) | `install-plan.test.mjs`: "dry-run writes nothing and reports preflight failures". It snapshots sha256 and mtime of every file under a temp HOME before and after `jev install all --dry-run --robot`. A missing `--dir` → exit 66. | A dry-run that creates `~/.local/state/jev` must fail the snapshot. `--dir /nonexistent` returning DRY_RUN rc 0 (today's behaviour) must fail. | `node --test kit/test/install-plan.test.mjs` |
| T2 | `kit/src/install/manifest.ts` (v2 manifest, marker, atomic write, mkdir lock with stale pid) | `install-manifest.test.mjs`: "second identical apply is zero-write; a concurrent install gets exit 5; a stale lock is taken over" | A lock dir with a live pid must refuse. One with a dead pid must be taken over. A rewrite that preserves bytes but bumps the mtime must fail the zero-write assertion. | `node --test kit/test/install-manifest.test.mjs` |
| T3 | `kit/install.sh` (bootstrap: N1–N9, N21–N24, preflight, PROXY_ARGS, 4-tier fetch, dual sha256, cosign asymmetric, `--offline`, `--quiet`, `--no-gum`, `--help`) | `install-sh.test.mjs`: runs `bash kit/install.sh --offline <fixture.tgz> --checksum <hex> --dest $T --bin-dir $T/bin --quiet` with `PATH` stripped of gum. It asserts empty stdout with `--quiet`, exit 0, and that `$T/bin/jev --version` prints the package version. It also asserts that `--help` lists every flag in §2.1 (parsed from a single flag table that the test also reads). | A wrong `--checksum` → exit 4 and nothing installed. A fake `cosign` that exits 1 → exit 4. No `cosign` → warning and exit 0. | `node --test kit/test/install-sh.test.mjs && shellcheck kit/install.sh` |
| T4 | `kit/package.json` (`bundleDependencies`, `engines.node >=22`, `files += install, calibration, omp shims`), release workflow producing `jev-kit-<v>.tgz`, `SHA256SUMS`, `.sigstore.json` | extends `package.test.mjs:19-47`: "packed tgz installs with --offline and no registry". It runs `npm install --offline --cache <empty>` from the tgz, then `jev doctor --robot` → exit 2 NOT_RUN | Remove `bundleDependencies` → the offline install fails (red). | `node --test kit/test/package.test.mjs` |
| T5 | `kit/src/install/cli-target.ts` (versions dir, `current` symlink, bin link, foreign-bin conflict, `--take-over-bin`, `--rollback`) | `install-cli.test.mjs`: "foreign ~/.local/bin/jev → conflict exit 4, bytes untouched; take-over records and uninstall restores; rollback flips current" | Seed `~/.local/bin/jev` → a fixture `hermes-jev-skills/bin/jev`. Overwriting it without `--take-over-bin` must fail. | `node --test kit/test/install-cli.test.mjs` |
| T6 | `kit/src/install/omp-paths.ts` (port of DCG `resolve_omp_agent_dir`) | `omp-paths.test.mjs`: table cases for `OMP_PROFILE` set/empty/`default`, `PI_PROFILE`, `PI_CODING_AGENT_DIR` (legacy-derived vs custom), `PI_CONFIG_DIR`, reserved names (`con`, `nul`) | `OMP_PROFILE=""` with `PI_PROFILE=muse` must resolve to the default agent dir (DCG semantics). A naive `PI_PROFILE` fallback fails this case. | `node --test kit/test/omp-paths.test.mjs` |
| T7 | `kit/src/install/omp-config-merge.ts` (YAML parse-merge append, dedup by resolved path and basename, backup, read-back, rollback) + YAML parser dependency declared in package.json | `omp-config-merge.test.mjs`: "host extensions preserved, ours appended once, re-run is `already`". Fixtures: block list, empty key, missing key, a commented `# - jev-x`, an absolute dev-path predecessor, CRLF. | Inline `extensions: []` → exit 4, file byte-identical (installer-grade-20260919.md:16-27). A corrupt YAML → `failed`, no write (B6). The old-subset-of-new read-back is forced to fail by a merge that drops one host entry. | `node --test kit/test/omp-config-merge.test.mjs` |
| T8 | `kit/install/families.json`, `kit/templates/omp/shims/*.ts` (marker, packaged imports), `kit/src/install/omp-profile-target.ts` | `install-omp-profile.test.mjs`: "measured profiles get shims; codex extension family → unsupported; declared-off family never installed; predecessor hardlink → conflict unless --migrate (backed up)" | A shim importing `/Users/…/Developer/jev/` must fail a static grep inside the test. Installing `jev-skill-hint` (declared off) must fail. | `node --test kit/test/install-omp-profile.test.mjs` |
| T9 | `kit/src/install/service.ts` (launchd + systemd render, byte-compare upgrade, bootout→bootstrap, uninstall, keyless skip); move skill-gap's `installLaunchAgent` here and repoint the plist at `current/bin/jev` | Extends `skill-gap.test.mjs:378-411`: "stale loaded plist is refreshed (bootout, write, bootstrap); identical → already, no launchctl write calls; foreign plist → conflict; uninstall boots out and keeps state dir; ProgramArguments contain no repo path" | Today's `ALREADY_LOADED`-without-compare (skill-gap.ts:1226-1227) must fail the stale-refresh case. A plist containing `kit/bin/jev-skill-gap.mjs` under the repo must fail. | `node --test kit/test/install-service.test.mjs kit/test/skill-gap.test.mjs` |
| T10 | `kit/src/install/verify.ts` (L0–L3), `kit/src/doctor-install.ts` (L4) | `install-verify.test.mjs`: "L3 needs a nonce row from the installed module; L2 requires a discriminating negative arm; L4 flags declared-off rows as RED". It uses a stub `omp` binary on PATH that emits recorded `get_state` JSON. | A stub omp whose `--no-extensions` output still contains the probe → `failed` (oracle broken). A fire fixture whose handler is replaced by a no-op → L3 `failed`. A fixture `skill-hint-calls.jsonl` with rows while declared off → RED. | `node --test kit/test/install-verify.test.mjs` |
| T11 | `kit/src/install/clef-target.ts` + plist (depends on clef-backend-spec T0–T2) | `install-clef.test.mjs`: "requires --clef-model; non-loopback refused; verify posts captured row and matches recorded Platt value within 1e-3 via injected fetch" | `--clef-url http://10.0.0.5:8010` → exit 4. Injected fetch returning a different label → L3 `failed`. | `node --test kit/test/install-clef.test.mjs` |
| T12 | `kit/src/install/skills-target.ts` | `install-skills.test.mjs`: "copies from package into one store; existing unmarked store dir → conflict; uninstall removes only marked" | A pre-existing hand-written `~/.agents/skills/jev-tools/SKILL.md` must stay byte-identical. | `node --test kit/test/install-skills.test.mjs` |
| T13 | `jev completions`, README.md §"Install Jev into omp" and kit/README.md (replace the checkout-only instructions; document channels A and B, `--offline`, uninstall, rollback, levels L0–L4), CHANGELOG | `cli.test.mjs` case: "completions bash/zsh/fish emit every verb in the dispatcher". README commands are executed by the existing P9-style README row harness (README.md:9). | A verb added to the dispatcher but missing from the completions output must fail. | `node --test kit/test/cli.test.mjs` then the README keyless rows |
| T14 | End-to-end gate (runs once, after T1–T13) | `install-e2e.test.mjs`: temp HOME + temp OMP_HOME with 2 fixture profiles. `bash install.sh --offline <tgz> --with daily --profiles measured` (launchctl and omp stubbed) → assert the summary JSON reaches L3 on every row, then `--uninstall` → the tree hash equals the pre-install hash apart from the `~/.local/state/jev` logs | Skipping uninstall of one plist must make the tree hash differ (red). | `nice -n 10 node --test kit/test/install-e2e.test.mjs` |

**Order rationale.** T1 and T2 are the shared contract that every target uses. T3 and T4 make an artifact exist. T5 to T9 are independent targets and can be parallelised once T2 lands. T10 must land before any target is called done, because placement alone is not done (README.md:38). T11 is blocked on the clef-backend T0 work. T14 is last.

**Live-only checks, not covered by any task above (UNVERIFIED until run on the real machine with operator approval):**
- An organic L4 row count per family and profile after a real day.
- `launchctl kickstart` of the real `ai.zeststream.jev-skill-gap-miner`.
- An omp rpc probe against the real profiles.

The commands are `jev doctor --install --since 24h --robot` and `jev install --verify --profiles measured --robot`.

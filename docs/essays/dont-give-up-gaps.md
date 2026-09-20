# Don't Give Up — Gaps

Skill under audit: `dont-give-up` playbook **A–L** (tool playbook holes:
named tools with no `jev_playground` worked example, or examples that
fail when the tool is STALE / unlinked / off `PATH`).
Pass date: 2026-09-20. Lane: offline file search + quote verification on
`e65a614`. No live Jev calls. No secret values printed.

`cass`, `fh`, `dcg`, `jsm`, `ubs`, `infisical`, and `omp` are **not** on
`PATH` here. That is the STALE/unlinked class this pass is about, not a
reason to park: the skill already says `fh suggest` STALE ≠ unusable;
this tip already has the lane citations and copy-paste commands. The
CLIs themselves are **NOT_RUN**.

Passes 1–5 are **not merged**. Stubs below point at
[PR #9](https://github.com/JYeswak/jev_playground/pull/9) through
[PR #13](https://github.com/JYeswak/jev_playground/pull/13). Do not
re-litigate those gaps. This file’s first full section is Pass 6.

The local evidence pack’s “Suggested feed” mapped “tool playbook holes”
to Pass 7 (with the Jeffrey essay). This packet is **Pass 6** of the
skill-loop. Pack G7 / G8 / G10 already landed as Pass 5 on PR #13.

## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack
**G1** / **G9**) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.

## Pass 2 — Over-learned kill (stub)

Pass 2 is **not merged** on this tip. The over-learned-kill audit (pack
**G2**) lives on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`cursor/dont-give-up-over-learned-kill-edb3`). Do not re-litigate it here.

## Pass 3 — Named hole then park (stub)

Pass 3 is **not merged** on this tip. The named-hole-then-park audit
(pack **G3** / **G4**: Infisical `--projectId=` vs `<id>`) lives on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`cursor/named-hole-then-park-c4a2`). Pass 6 **re-uses** that projectId
in the ready-to-paste D/K replacements; it does not re-open G3/G4.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 is **not merged** on this tip. The selector-and-dig-skip audit
(pack **G6** / **G5**: `requireKey` / `readRow`;
https://omp.sh/docs/extension-authoring) lives on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12)
(`cursor/selector-and-dig-skip-364d`). Pass 6 **folds** those into the
ready-to-paste E/K/checklist replacements so one paste applies the house
skill; it does not re-open G5/G6.

## Pass 5 — Paperwork and live proof (stub)

Pass 5 is **not merged** on this tip. The paperwork / invented-observation
/ live-proof audit (pack **G7** / **G8** / **G10**) lives on
[PR #13](https://github.com/JYeswak/jev_playground/pull/13)
(`cursor/paperwork-and-live-proof-92c2`). Do not re-litigate it here.

---

## Pass 6 — Tool playbook holes

**Claim.** The attached house skill names `cass`, `fh`, arsenal, `dcg`,
`jsm`, Infisical, omp extension-authoring, and `requireKey`/`readRow`
discipline — then shows **generic** commands (`--workspace <project>`,
`--projectId=<id>`, `e.g. …/docs/extension-authoring`, “selector ≡
claim”). This repo already has the real commands and the real failure
modes. Agents who follow the skill as written re-discover unlinked
Infisical, skip the official omp page, and treat `fh doctor` STALE or a
missing binary as “tool unusable.”

**Local evidence pack.** Folded here: the pack’s **missed digs** table
(omp.sh/docs/extension-authoring; Infisical `--projectId=`) plus the
skill-loop mission “cass/fh/arsenal/dcg/jsm sections that lack worked
*lane* examples or fail when STALE/unlinked.” Passes 1–5 stay on PRs
#9–#13. Passes 7–8 and the Jeffrey-voice essay are **not** started.

**NO-CLAIM.** This pass does not apply the patches to any JSM-owned
skill copy. It does not rewrite `README.md:696` or
`scripts/jev-probe.mjs:38` (named as next product ticks). It does not
install `cass`/`fh`/`dcg`/`jsm`/`infisical`/`omp` on this VM. It does
not run a live Jev call.

### Five required answers (re-read on `e65a614`)

| Question | Answer on this tip |
|---|---|
| Which tools are named but never shown with a `jev_playground` worked example? | **A `cass`**, **B `fh suggest`**, **C arsenal**, **F `dcg explain`/`dcg test`**, **I `jsm search`**, **L `fh scaffold`**. Skill A–C / F / I / L are generic CLI shapes. Lane receipts for the *same hole class* exist and are cited in the gap table. |
| `fh suggest` STALE ≠ unusable — is that in the skill with a lane citation? | **In the skill, yes (comment only). Lane citation: no.** Skill B line: `fh suggest "…"          # STALE ≠ unusable — still steal the row`. Zero file:line. The lane citation is `docs/INTEGRATIONS.md:11-16`. |
| Infisical `projectId` still shown as `<id>` anywhere in skill vs `.env.example`? | **Skill: yes (`--projectId=<id>` twice in D). `.env.example`: no.** `.env.example:11,15` is `42b194c3-89d7-4ebb-895f-dd77ddf005ba`. Leftover `<id>` still teaching the park: `README.md:696`, `scripts/jev-probe.mjs:38` (same file’s `:6` has the real id). |
| `omp.sh/docs/extension-authoring` — skill says “e.g.” but not the real URL in a copy-paste block? | **Yes.** Skill E: `Official docs (e.g. product …/docs/extension-authoring)`. Ellipsis, not `https://omp.sh/docs/extension-authoring`. `rg -n 'extension-authoring' --glob '!docs/essays/**'` on `e65a614` is **empty**. |
| `requireKey` / `readRow` — skill checklist vs oracle-kit? | **Checklist is a reminder; the kit is mechanical.** Skill: “Did I verify selector ≡ claim …?” `work/oracle-kit/index.mjs:116-123` `requireKey` throws `Keys present: […]`. `work/jev-client/src/index.ts:136-159` `readRow` accepts both omp shapes. `TESTS.md:28-31,47`. |

### Gap table

Skill section → missing worked example → proposed patch with **real**
commands/paths from this repo. Apply the paste in
`docs/essays/dont-give-up-skill-patches.md` Pass 6.

| Skill section | What the skill shows | Missing worked *lane* example | Proposed patch (this repo) |
|---|---|---|---|
| **A cass** | `cass status --json`; `cass search "KEYWORD" --workspace <project> --json --fields minimal` | No `--robot`. Placeholder `--workspace <project>`. No query this repo already publishes. Bare `cass` is a TUI (`AGENTS.md:1407`). | `cass health` then `cass search "jev typed questions" --robot --limit 5` (`AGENTS.md:1410-1411`). Stage-0 already has `cass search "jev" --robot --limit 10` (`AGENTS.md:890`). Never invent `--workspace <project>`. Off `PATH` → steal from `AGENTS.md`, do not report “cass missing.” |
| **B fh** | `fh suggest "…"` + comment `STALE ≠ unusable` with **no citation** | Comment is doctrine without a receipt. Agents read STALE / `ORACLE_DOMAIN_UNKNOWN` / binary-absent as unusable. | Keep the comment. Cite `docs/INTEGRATIONS.md:11-16`: `fh doctor` may report STALE; **fh ranked, we opened** (`asupersync` `eprocess.rs:224-238`, `franken_ocr` `RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch` `perf_ratchet.rs:732-740`). Worked miss that is still usable: `fh oracles --domain jev` → rc=4 `ORACLE_DOMAIN_UNKNOWN` (`docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14`) — absence evidence, not a reason to invent a local `oracles.tsv`. Also `fh agents --repo .` (`EVAL.md:165`; `.fh-agents.toml`). Lane hole string: `fh suggest "wire a typed Jev asker into an omp tool_call hook"`. |
| **C arsenal** | “WHEN YOU NEED X, USE Y (charter / frankensuite-arsenal)” | `rg -n 'frankensuite-arsenal\|WHEN YOU NEED X' --glob '!docs/essays/**'` → **NONE**. Off-machine table. | In-tree “do not hand-roll” table: Jev POST → `work/jev-client` (`TESTS.md:47`); absence claim → `requireKey` (`work/oracle-kit/index.mjs:116`); omp session row → `readRow` (`work/jev-client/src/index.ts:136`); planted RED → `foundation/gates.d/` + `TESTS.md`. If the Franken arsenal is off-disk, these paths are the arsenal. |
| **D Infisical** | `--projectId=<id>` twice | Placeholder teaches the park `.env.example` was written to stop (`:1-8,27-31`). | Copy `.env.example:15`: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`. Presence: `printenv NAME \| wc -c` or `infisical secrets --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba \| grep -c TYPESAFE_API_KEY` (expect 1; `:34-35`). “run init” = **UNLINKED DIRECTORY**, not missing secret (`:27-31`). Client already embeds the fix (`work/jev-client/src/index.ts:46-54`). |
| **E docs / examples** | “e.g. product `…/docs/extension-authoring`” | Not a URL. Not a copy-paste block. `rg` for `extension-authoring` outside essays is empty. | Open **https://omp.sh/docs/extension-authoring**. Copy `work/omp-harm-rule/harm-rule.ts:27-32` / `work/omp-jev-observer/src/observer.mjs:50-53`. Neighbour co-presence (`docs/INTEGRATIONS.md:167-172,192`). |
| **F dcg** | `dcg explain "cmd"` / `dcg test "cmd"` | Those two verbs never appear in first-party prose. The lane receipt is a **denial**, not a help string. Frozen-corpus `dcg test` rows (`work/p3-calibration/toolcall-corpus-frozen.jsonl`) are **foreign sessions** (control-plane) — not a jev worked example (wrong-selector if cited as ours). | Worked lane row: `dcg` denied `git add -A` / `git add .` (`zeststream.shared_worktree:git-add-whole-tree`) — `AGENTS.md:249-250`, `EVAL.md:232-233`, `.flywheel/feedback/2026-09-17.md:17-18`. Safe alternative: `git add <path>...` then `git diff --cached --stat`. Do not ask for override first. Do not confuse CLI `dcg` with the omp `dcg-guard` hook (`docs/INTEGRATIONS.md:88-90`). |
| **G ubs** | `ubs --staged` until exit 0 | Missing the empty-scan-set lie this lane already measured. | `ubs` on markdown-only → exit 3, **not a pass** (`NEGATIVE_EVIDENCE.md` R6 `:99-108`; receipt `docs/demos/duel-1/runs/ubs-r6-20260918T011614Z.json`). Worked TS scan: four compaction files, exit 1, critical was a name not a secret (`:110-121`). Docs-only change: do not cite `ubs` green. |
| **H bv / br** | generic `bv --robot-triage` / `br update` | Weakest hole. `AGENTS.md` already has the robot-only rule. | Keep robot flags. ACCEPTANCE = a live command (`AGENTS.md` beads). Not the Pass 6 ship. |
| **I jsm** | `jsm search "<hole keywords>"` | No first-party `jsm search` receipt. `INTEGRATIONS.md:191` “jsm preconditions” is **self-contained install**, a different tool. Frozen-corpus `jsm search` rows are omp-orchestrator sessions — not ours. | If `jsm` is on `PATH`: `jsm search "omp extension authoring"`. If off `PATH` (this VM): do not report “jsm missing.” Read `docs/INTEGRATIONS.md:191` (inlined builder after `9e6c88d` imported a parent path that does not exist under `~/.omp`) and copy `harm-rule.ts` / `observer.mjs`. House lessons stay in house skills (skill I already says this). |
| **K live proof** | mechanical holes; “selector says 0” = “broaden” | No `requireKey` / `readRow`. No official URL on the zero-row row. | Fold Pass 4 rows: two omp shapes + `readRow`; neighbour + https://omp.sh/docs/extension-authoring. Fold Pass 3 inject-or-HALT with the real projectId. |
| **L planted-negative** | `fh scaffold` | `fh scaffold` never appears in this repo. | Lane equivalent: `foundation/gates.sh --selftest` (every stage proves RED) and the planted arms in `TESTS.md`. `fh scaffold` if present; otherwise extend `foundation/gates.d/` — do not invent a thirteenth wrapper. |

### Required quotes (STALE / unlinked / leftover `<id>` / official page / keys)

`fh doctor` STALE is still usable — rank, then open file:line:

```
docs/INTEGRATIONS.md:11-16
If this page mentions `fh`, it is as a *ranker*, not as a citation. `fh doctor` may report STALE
or degraded SCHEDULING (a 1/8 schedule-declaration miss does not retract shipped doctrine).
Corpus citations already in this repo were opened at file:line from the pinned Dicklesworthstone
mirror after `fh` ranked them — `asupersync` `eprocess.rs:224-238`, `franken_ocr`
`RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch`
`perf_ratchet.rs:732-740`. Pattern: **fh ranked, we opened.** A ranking alone is not a citation.
```

`fh` returning an error is still a finding (unusable catalogue ≠ unusable tool):

```
docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14
fh oracles --json                  rc=0, 18 domains
fh oracles --domain jev            rc=4  ORACLE_DOMAIN_UNKNOWN
fh oracles --domain system_one     rc=4  ORACLE_DOMAIN_UNKNOWN
```

Unlinked directory ≠ missing secret; real projectId already committed:

```
.env.example:11,15,27-31
WORKSPACE ID: 42b194c3-89d7-4ebb-895f-dd77ddf005ba
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <your command>
jev/ has no .infisical.json … "run infisical init…" means UNLINKED DIRECTORY, not MISSING SECRET.
```

Skill-shaped leftover `<id>` still in the tree (teaching the park):

```
README.md:696
infisical run --projectId=<id> --env=prod -- node scripts/jev-probe.mjs

scripts/jev-probe.mjs:6   (real id in the header)
scripts/jev-probe.mjs:38  (placeholder in the error the agent sees)
```

`requireKey` / `readRow` vs the skill’s “selector ≡ claim” checkbox:

```
work/oracle-kit/index.mjs:116-123
export function requireKey(record, key, who = 'record') {
  …
  throw new Error(`${who}: no '${key}'. Keys present: [${Object.keys(record).sort().join(', ')}]`);
}

work/jev-client/src/index.ts:127-136
 * omp session rows come in TWO shapes …
export function readRow(line: unknown): { type: string; data: Record<string, unknown> } | undefined {
```

dcg’s worked lane example is a denial with a named safe alternative:

```
AGENTS.md:249-250
NEVER `git add -A` / `git add .` — `dcg` denies it here
(`zeststream.shared_worktree:git-add-whole-tree`)

EVAL.md:232-233
`dcg` denied `git add -A` (`zeststream.shared_worktree:git-add-whole-tree`) on the first
attempt — correct in a worktree three agents share. Everything staged by explicit path since.
```

cass’s worked lane example is `--robot`, never `--workspace <project>`:

```
AGENTS.md:1407-1412
Never run bare `cass` (TUI). Always use `--robot` or `--json`.
cass health
cass search "jev typed questions" --robot --limit 5
cass view /path/to/session.jsonl -n 42 --json
```

### Search receipt (this pass, `e65a614`)

| Hunt | Result |
|---|---|
| `rg -n 'projectId=<id>' README.md scripts/jev-probe.mjs` | `README.md:696`, `scripts/jev-probe.mjs:38` |
| `rg -n '42b194c3-89d7-4ebb-895f-dd77ddf005ba' .env.example` | lines 11, 15, 19, 22, 34 |
| `rg -n 'extension-authoring' --glob '!docs/essays/**'` | **empty** |
| `rg -n 'fh doctor\|STALE' docs/INTEGRATIONS.md` | `:11` |
| `rg -n 'export function requireKey\|export function readRow'` | `oracle-kit/index.mjs:116`, `jev-client/src/index.ts:136` |
| `rg -n 'frankensuite-arsenal\|WHEN YOU NEED X' --glob '!docs/essays/**'` | **empty** |
| `rg -n 'jsm search' --glob '!docs/essays/**'` | frozen-corpus foreign rows only |
| `rg -n 'dcg explain\|dcg test' --glob '!docs/essays/**'` | frozen-corpus foreign rows only |
| `rg -n 'cass search' AGENTS.md` | `:890`, `:982`, `:1411` (`--robot`) |
| `command -v cass fh dcg jsm infisical omp` | **ABSENT** (this VM) |

Offline suites this pass leans on (fresh this turn):

```
node work/oracle-kit/test.mjs
→ oracle-kit: 13/13 checks passed
  (includes requireKey names every key present when the field is absent)

node --experimental-strip-types --test work/jev-client/test/client.test.mjs
→ 9/9 pass
  (includes readRow handles BOTH omp row shapes)
```

### What this pass is not claiming

- That `cass` / `fh` / `dcg` / `jsm` / `infisical` / `omp` ran on this VM.
  They are off `PATH`. Commands are written from committed receipts,
  **NOT_RUN**.
- That frozen-corpus `jsm search` / `dcg test` rows are *this* lane’s
  worked examples. They are other sessions. Citing them as ours is
  the selector hole Pass 4 already named.
- That Pass 3/4 patches are merged. They are not. Pass 6’s D/E/K
  pastes fold their content so an agent can apply one house-skill
  edit without waiting on those PRs.
- Invented STOP-LIVE (PR #9), the tool_call over-learn (PR #10),
  named-hole-then-park as a *new* audit (PR #11), selector /
  extension-authoring as a *new* audit (PR #12), paperwork /
  `?? 'unknown'` (PR #13).
- Pass 7, Pass 8, or the Jeffrey-voice essay.

### Next lever (Pass 6 close)

Land the skill patches (playbook D/E/K + checklist pastes; A/B/C/F/I
worked lane examples). The next *product* ticks this table blocked:

1. Replace leftover `projectId=<id>` at `README.md:696` and
   `scripts/jev-probe.mjs:38` with
   `42b194c3-89d7-4ebb-895f-dd77ddf005ba` (already on `:6` and
   `.env.example:15`).
2. Put `https://omp.sh/docs/extension-authoring` in one first-party
   README (`work/omp-harm-rule` or `work/omp-jev-observer`) so `rg`
   is no longer empty.

Do not start Pass 7 or the Jeffrey essay in this PR.

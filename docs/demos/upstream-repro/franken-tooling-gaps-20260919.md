# Franken tooling gaps — owned but not applied (Jev lane)

**Date:** 2026-09-19 ~22:40 MDT  
**Repo tip:** `origin/main` @ `23a1143` (PR #16 taste-loop + #17 dont-give-up essays merged)  
**Studio path:** `/Users/josh/Developer/jev` (= public `JYeswak/jev_playground`)  
**Executor note:** Shell `machineId=439e8c39-3223-4273-9ce4-4263468cbba7` did **not** route onto Studio from this sand box (`hostname` stayed `grok-bot-vm-*`; Tailscale `100.93.84.11:22` closed). Live `fh suggest` / `fh rejected` / `command -v` inventory on Studio was **not** run. Evidence below is from the tip tree + receipts already in-tree. NO invented “we should use X” without a named hole.

## High bar

Every “next apply” names the **hole it closes**. Doctrine-only mentions in `AGENTS.md` do not count as lane use.

## Inventory table

| Tool | Owned? (doctrine / house) | Used on this lane? | Evidence | One concrete next apply (hole → move) |
|---|---|---|---|---|
| `fh` | Yes — `AGENTS.md:888-890,981-987`; house `/dont-give-up` playbook B | **Thin.** Historical shape oracle + ranker cites; **no tip receipt of `fh suggest "agent dig moves"` / `fh rejected` this session** | Used: `fh agents` nomenclature (`EVAL.md:165`; `.flywheel/worksheets/2026-09-17-lane-substrate.md:12,57`); `fh doctor` STALE doctrine (`docs/INTEGRATIONS.md:11-16`); `fh oracles --domain jev` → rc=4 `ORACLE_DOMAIN_UNKNOWN` (`docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14`). Gap: Pass 6 names A–L tools with generic CLI and no lane citation for `fh suggest` (`docs/essays/dont-give-up-gaps.md:1084-1085,1099`) | **Hole:** dig moves invent policy instead of stealing prior art. **Apply:** on Studio run `fh suggest "agent dig moves"` and `fh rejected \| head`, paste top rows + `fh why <row>` into the next dig receipt; keep STALE usable per `INTEGRATIONS.md:11-16` |
| `cass` | Yes — `AGENTS.md:890,1403-1416`; playbook A | **No live lane receipt** | Doctrine only (`AGENTS.md:1410-1411`). Pass 6: skill still shows `--workspace <project>`; no first-party `cass search` receipt (`docs/essays/dont-give-up-gaps.md:1098,1201`). `code_files` under `work/foundation/scripts` excluding md/json: **0** | **Hole:** re-solving typed-question / dig problems already in prior sessions. **Apply:** `cass health && cass search "jev typed questions" --robot --limit 5` before inventing a new question shape; never bare `cass` (TUI) |
| `dcg` | Yes — machine-wide + AGENTS | **Yes (blocker receipts)** | Denied `git add -A` / `git add .` (`zeststream.shared_worktree:git-add-whole-tree`) — `AGENTS.md:249-250`, `EVAL.md:232-233`, `.flywheel/feedback/2026-09-17.md:17-18`. Harm-rule measured vs 814 real dcg blocks (`14f5c9c` subject; `docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md`). Pass 6: `dcg explain`/`dcg test` verbs absent from first-party prose (`dont-give-up-gaps.md:1103,1200`) | **Hole:** agents ask for override instead of naming the safe alternative. **Apply:** when blocked, run `dcg explain "<cmd>"` once and stage by explicit path (`git add <path>…`); do not reshape to evade |
| `ubs` | Yes — `AGENTS.md:1301-1307`; GATES | **Yes (empty-scan + TS scan receipts)** | Empty scan = ERROR not pass (`GATES.md:40,112`); R6 markdown-only exit 3 (`NEGATIVE_EVIDENCE.md` via `dont-give-up-gaps.md:1104`; duel receipt `docs/demos/duel-1/runs/ubs-r6-20260918T011614Z.json`) | **Hole:** citing `ubs` green on doc-only commits. **Apply:** before every commit that touches TS/JS, `ubs $(git diff --name-only --cached)`; on docs-only, do **not** claim ubs pass |
| `bv` | Yes — `AGENTS.md:1285-1292` robot-only | **No first-party tip use** | Doctrine only. Foreign `bv --robot-triage` rows in duel fixtures (`docs/demos/duel-2/runs/*`). `code_files`: **0**. Pass 6: weakest hole (`dont-give-up-gaps.md:1105`) | **Hole:** picking work by vibe while `br ready` is empty / lying. **Apply:** `bv --robot-triage` (never bare `bv`) before filing beads; ACCEPTANCE = live command |
| `br` | Yes — beads spine | **Yes** | Tip subjects + beads churn (`0d36407` “br ready was empty”; AGENTS beads section `:1242-1270`). `code_files`: 6 | **Hole:** open beads without live ACCEPTANCE. **Apply:** every new Muse child bead closes only when its ACCEPTANCE command exits 0 |
| `jsm` | Yes — JSM skill search; playbook I | **No first-party receipt** | Pass 6: `jsm search` only in foreign frozen-corpus (`dont-give-up-gaps.md:1106,1199`). `INTEGRATIONS.md:191` “jsm preconditions” is self-contained install, different tool. `code_files`: **0** | **Hole:** reinventing omp extension authoring. **Apply:** if on PATH, `jsm search "omp extension authoring"`; if off PATH, copy `work/omp-harm-rule/harm-rule.ts` / `work/omp-jev-observer/src/observer.mjs` — do not report “jsm missing” as STOP |
| `ms` | Yes — meta-skill search (house / NTM stack) | **Absent from lane receipts** | No first-party `ms search` hit outside false-positive `ms` millisecond locals in scripts. Doctrine via NTM orchestration skills off-box | **Hole:** unknown skill already covering a dig. **Apply:** `ms search "jev usage router"` once before scaffolding a sibling skill |
| `ntm` | Yes — Studio fleet | **Orchestration only (not product)** | Session discipline in AGENTS / GATES (`GATES.md:89` prefers `ntm --robot-agent-health=jev`). Pane-1 ownership; **this executor did not `ntm send`** | **Hole:** conductor blindness / steal panes. **Apply:** observe with `ntm --robot-agent-health=jev` only; never `ntm send --all`; CyanFalcon owns pane 1 |
| `gb` | Named in inventory ask | **Absent from receipts** | No first-party `gb` lane prose in `AGENTS.md` / `docs/INTEGRATIONS.md` / `GATES.md` for this tip. Treat as **owned elsewhere, unused here** until a Studio `command -v gb` receipt exists | **Hole:** unknown — do not invent a use. **Apply:** on Studio `command -v gb && gb --help \| head`; only then pick a hole it closes |
| `infisical` | Yes — secrets spine | **Yes** | Working projectId `42b194c3-89d7-4ebb-895f-dd77ddf005ba` (`.env.example:11,15`); usage-router live inject (`work/jev-usage-router/README.md:10-12`); many `work/*` READMEs. Leftover teaching park: `README.md:696`, `scripts/jev-probe.mjs:38` still show `<id>` while `:6` has the real id (`dont-give-up-gaps.md:1143-1150`) | **Hole:** agents park on “key missing” after bare `infisical` in unlinked dir. **Apply:** delete leftover `<id>` placeholders in README/probe error string (product tick); keep inject one-liner only |
| `ee` | House / JSM lesson stamp | **Thin** | Named in NTM orchestration playbook; not in tip product commits | **Hole:** lessons die in chat. **Apply:** after a dig miss, `ee pack` / house skill patch — not a new essay alone |
| frankensuite-arsenal “WHEN YOU NEED X, USE Y” | Named in `/dont-give-up` playbook C | **Absent from this tree** | `rg -n 'frankensuite-arsenal\|WHEN YOU NEED X' --glob '!docs/essays/**'` → **empty** (`dont-give-up-gaps.md:1100,1198`). Off-machine table | **Hole:** hand-rolling POST / absence / row-parse primitives. **Apply:** use in-tree arsenal substitutes — `work/jev-client` (`TESTS.md:47`), `requireKey` (`work/oracle-kit/index.mjs:116`), `readRow` (`work/jev-client/src/index.ts:136`), `foundation/gates.d/` — until Studio arsenal path is found |

## Studio live commands still owed (not invented STOP)

When Shell routes to `Joshs-Mac-Studio.local` / `439e8c39-…`:

```bash
hostname   # must be Joshs-Mac-Studio.local
command -v cass fh dcg ubs bv br jsm ms ntm gb infisical ee
fh suggest "agent dig moves"
fh rejected | head -40
# if present:
rg -n 'WHEN YOU NEED X|USE Y' ~/Developer ~/foundry ~/.claude 2>/dev/null | head -20
```

## Top 5 unused / under-applied (for Jev deliver)

1. **`cass`** — doctrine only; closes “already solved” digs  
2. **`jsm`** — no first-party search receipt; closes authoring reinvention  
3. **`gb`** — absent from receipts; unknown until Studio which  
4. **`bv --robot-*`** — no tip triage receipt; closes vibe-picked beads  
5. **`fh suggest` / `fh rejected` as pre-invent dig** — STALE usable, but Pass 6 still unpaid for worked lane citation  

Honorable: **`ms`**, **arsenal table** (off-disk), **`ee`**.

## NO-CLAIM

- Did not run `fh` / `cass` / `jsm` binaries (absent on sand VM; Studio Shell not routed).  
- Did not claim install versions or PATH on Studio.  
- Did not `ntm send`. Did not invent STOP-LIVE.

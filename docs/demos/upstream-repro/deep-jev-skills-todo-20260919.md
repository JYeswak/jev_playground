# Deep Jev skills — Muse epic (repeatedly-apply-skill seed)

**Date:** 2026-09-19 ~22:40 MDT  
**Tip:** `23a1143` · **Audience:** Muse todo graph + repeatedly-apply-skill (N=8–10 pass themes)  
**House skills already present:** `/dont-give-up` (sand + Studio house); `/jev-usage-router` scaffolded in `work/jev-usage-router/`  
**Constraint:** ACCEPTANCE = live command. Codex OOT — Muse/Claude only for NTM. Pane 1 = CyanFalcon (do not steal).

## Epic bead (parent)

| field | value |
|---|---|
| id | `jev-muse-deep-skills-20260919` |
| title | Land deep Jev skills with live ACCEPTANCE + Pass patches |
| WHY | promoted=0 still; harm-rule = four regexes no Jev; observer systemOne proved once; tooling owned but under-applied; skill essays consolidated (#17) but Pass 6 playbook pastes still unfinished on house skill |
| ACCEPTANCE | `test -f docs/demos/upstream-repro/deep-jev-skills-todo-20260919.md && test -f docs/demos/upstream-repro/franken-tooling-gaps-20260919.md && git log -1 --oneline -- docs/demos/upstream-repro/deep-jev-skills-todo-20260919.md` |
| depends | Franken tools per child (`fh`,`cass`,`infisical`,`dcg`,`ubs`,`br`/`bv`) |

---

## Child 1 — `jev-question-writing`

| | |
|---|---|
| **when-to-use** | Before any new `systemOne` / Noul / Choice question set; when scores look calibrated but questions are long, purpose-free, or non-ensemble |
| **ACCEPTANCE** | `node --experimental-strip-types --test work/jev-client/test/client.test.mjs` exits 0 **and** `rg -n "askJev|askJevChoice|noul" work/jev-client/src/index.ts` shows typed askers |
| **depends** | `infisical` (live), `work/jev-client`, `fh` optional for prior art |
| **N=8–10 pass themes** | 1 short stem 2 purpose line in question text 3 ensemble ≥2 complementary questions 4 refuse empty `questions:{}` 5 Choice map not list (`askJevChoice` test) 6 holdout shape (`question-shape-holdout.mjs`) 7 no length-only leak as signal 8 SDK-SURFACE field names (`docs/demos/SDK-SURFACE.md:15,48`) 9 NO-CLAIM on unrun live 10 paste one live row latency/ok |

---

## Child 2 — `jev-eval-honesty`

| | |
|---|---|
| **when-to-use** | Before promoting any judge/hook; when offline green tempts a ship; when a selector returns 0 |
| **ACCEPTANCE** | `node work/oracle-kit/test.mjs` → 13/13 **and** `rg -n "requireKey|readRow" work/oracle-kit/index.mjs work/jev-client/src/index.ts` hits `:116` and `:136` |
| **depends** | `oracle-kit`, `jev-client.readRow`, neighbour co-presence receipts |
| **N=8–10 pass themes** | 1 co-presence vs known-firing neighbour (`harm-rule-shipped-20260919.md:55-74`) 2 outcome join on `toolCallId` (`:79-91`) 3 random-judge substitution class (c) only (`random-judge-substitution-20260919.md:14-31`) 4 selector≡claim via `requireKey` keys dump 5 dual omp row shapes via `readRow` (tip `f8a8dc9`) 6 no `?? 'unknown'` on truth fields 7 prevalence beside every score (`prevalence-retrofit-20260919.md`) 8 offline ≠ live row 9 promoted=0 honesty until dogfood OPEN closes 10 retract invented STOP-LIVE (`INTEGRATIONS.md:174`) |

---

## Child 3 — `jev-retransmit-killer` (compaction Score)

| | |
|---|---|
| **when-to-use** | When tempted to adopt fast-jev-compaction / retransmit / drop-context heuristics; when Score thresholds look “obvious” |
| **ACCEPTANCE** | `rg -n "7–23×|retention|threshold" docs/demos/upstream-repro/compaction-retention-oracle-20260919.md docs/demos/upstream-repro/compaction-threshold-curve-20260919.md` shows both receipts present; do **not** install production compaction without a new live beat of those oracles |
| **depends** | `infisical`+Jev for re-measure; `ubs` on any TS touch in `work/compaction-proof/` |
| **N=8–10 pass themes** | 1 install-and-run proof only (`compaction-install-run-20260919.md`) 2 positive control (`compaction-positive-control-20260919.md`) 3 retention oracle worse than noop (`compaction-retention-oracle-20260919.md`) 4 threshold curve honesty 5 Score≠ship 6 no production hook claim 7 retransmit as kill candidate not default 8 plant RED gate 9 prevalence of reuse 10 NO-CLAIM production |

---

## Child 4 — `jev-usage-router-active` (Choice composite)

| | |
|---|---|
| **when-to-use** | Before browser / research / extra bot / retry loops; when shadow logs already exist and active mode is the next product tick |
| **ACCEPTANCE** | `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- node work/jev-usage-router/src/cli.mjs --goal "Summarize the README in the current repo from disk"` prints JSON with `ok:true` and `action` ∈ {local,research,browser,bypass}; `rg -n '"mode": "active"' work/jev-usage-router/logs/routes-2026-09-20.jsonl` ≥1 |
| **depends** | `infisical`, `jev-client` Choice (`SDK-SURFACE`), house skill `/jev-usage-router` |
| **N=8–10 pass themes** | 1 shadow default 2 active honors action 3 kill switches (`BYPASS_JEV` / `enabled:false`) 4 confidenceFloor → bypass 5 refuse missing `probabilities` (`router.mjs:103-106`) 6 composite Choice not ad-hoc ifs 7 log append-only JSONL 8 VALIDATION-7STEP green (`VALIDATION-7STEP.md`) 9 no key in chat 10 wire Grok Bot caller to honor `action` (product) |

---

## Child 5 — `dont-give-up` (exists) — Pass 6 still unapplied

House skill copies observed: sand `/home/box/sand-data/workflows/dont-give-up/SKILL.md` (process-porn refuse + partial D/E); essay authority `docs/essays/dont-give-up-skill-patches.md` + `docs/essays/dont-give-up-gaps.md` Pass 6. Consolidation #17 merged tips; **Pass 6 paste into house skill is still incomplete** (patches file truncates mid “Why: skill E…”; gaps table is the full A–L authority).

### Pass 6 patches still unapplied (or only partially applied) to house skill

| Patch / section | Status vs sand house skill | Hole it closes |
|---|---|---|
| **6.1 Playbook D wholesale** | Partial: real projectId present; missing names-only `grep -c`, “leftover `<id>` is a defect” cite (`README.md:696`), full UNLINKED DIRECTORY block from gaps | Named-hole-then-park on Infisical |
| **6.2 Playbook E wholesale** | Partial: URL present; missing 30s checklist, neighbour co-presence before “0 rows”, exact `omp --profile=jev-lab … echo observer-minimal-actual` nonce | Silent-register / zero-row false findings |
| **A cass worked lane** | Unapplied — still generic / placeholder workspace in older pack copies | Skip prior-session dig |
| **B fh + INTEGRATIONS:11-16 citation** | Unapplied — STALE comment without file:line | Treat STALE as unusable |
| **C arsenal → in-tree substitutes** | Unapplied — still points at missing frankensuite-arsenal | Hand-roll primitives |
| **F dcg denial worked example** | Unapplied — no `git add -A` denial cite in skill | Override-first |
| **G ubs empty-scan exit 3** | Unapplied | Fake ubs green on docs |
| **I jsm off-PATH rule** | Unapplied | “jsm missing” STOP |
| **K fold requireKey/readRow + lab nonce** | Partial in sand J table; missing mechanical `requireKey` paste | Selector narrower than claim |
| **L planted-negative = gates.sh --selftest** | Unapplied (`fh scaffold` absent) | Green suites that never RED |

**ACCEPTANCE (this child):** house skill file contains (1) `42b194c3-89d7-4ebb-895f-dd77ddf005ba`, (2) `https://omp.sh/docs/extension-authoring`, (3) `cass search "jev typed questions" --robot`, (4) `docs/INTEGRATIONS.md:11-16` citation, (5) `requireKey` / `readRow` names — verified by `rg -n` on the skill path Muse edits (Studio `~/.claude/skills` house copy or sand workflow). Do **not** patch JSM-owned skills.

**depends:** `fh`, `cass`, `dcg`, `ubs`, `infisical`, `jsm` (optional)

**N=8–10 pass themes:** 1 paste D 2 paste E 3 cass A 4 fh B cite 5 arsenal C 6 dcg F 7 ubs G 8 jsm I 9 K requireKey 10 L gates selftest

---

## Child 6 — `jev-silent-register` (today’s evidence)

| | |
|---|---|
| **when-to-use** | Extension “loads” with 0 rows; `node --check` green; tempted to invent STOP-LIVE / human-review for lab |
| **ACCEPTANCE** | `rg -n "silent|pi.on|co-presence" docs/demos/upstream-repro/harm-rule-shipped-20260919.md docs/INTEGRATIONS.md` hits silent-module fault + INTEGRATIONS loader rules; reproduce neighbour co-presence bar or quote why not |
| **depends** | omp lab profile, `infisical`, playbook E |
| **N=8–10 pass themes** | 1 lost `pi.on` 2 glob `*.{ts,js}` 3 extensions list 4 neighbour fires 5 lab free vs working-profile human gate 6 tsx import probe 7 refuse silence-alone finding 8 rollback before working-profile 9 quote one session row 10 no mid-flight pane steal |

---

## Child 7 — `jev-prevalence-first` (today’s evidence)

| | |
|---|---|
| **when-to-use** | Publishing AUC/recall/precision; retrofit / promotion decisions; authored vs real traffic |
| **ACCEPTANCE** | `rg -n "prevalence" docs/demos/upstream-repro/prevalence-retrofit-20260919.md docs/demos/upstream-repro/RULING-authored-vs-real-20260919.md` ≥1 hit each; any new scoreboard row must include a prevalence cell or explicit UNKNOWN |
| **depends** | measure-kit / real_scores receipts; `fh` optional |
| **N=8–10 pass themes** | 1 prevalence cell mandatory 2 authored≠real (`RULING-authored-vs-real-20260919.md:41-68`) 3 high prevalence ≠ deployable (skillranker / router rows) 4 low prevalence kills vanity AUC 5 harm-rule 1/814 honesty 6 no F1 on unlabeled corpus 7 random-judge survival 8 holdout before superiority 9 retrofit ledger 10 NO-CLAIM when UNKNOWN |

---

## Muse repeatedly-apply order (suggested)

1. `dont-give-up` Pass 6 paste (unblocks digs)  
2. `jev-eval-honesty` (stops false promotions)  
3. `jev-silent-register` (stops 0-row loops)  
4. `jev-question-writing` (raises signal quality)  
5. `jev-usage-router-active` (product routing tick)  
6. `jev-prevalence-first` (scoreboard honesty)  
7. `jev-retransmit-killer` (prevents bad compaction adopt)

## Top 5 skills for Muse (priority)

1. dont-give-up Pass 6 apply  
2. jev-eval-honesty  
3. jev-silent-register  
4. jev-usage-router-active  
5. jev-question-writing  

## NO-CLAIM

- Skills are **proposed** bead shapes; house skill file on Studio not edited this turn.  
- No live omp registration performed from sand.  
- Pass 6 patches file on tip is truncated mid-sentence; gaps.md Pass 6 table is the authority for remaining A–L pastes.

# typesafe-ai/skills — W7.0 catalogue receipt — 2026-09-22

Fresh run. Class: catalogue. Tests run: T1 and T3. No live Jev call. Clone not edited.

Old lead, not evidence: `docs/demos/upstream-repro/sdk-js-and-skills-20260919.md`. Ledger row `notes/deep/clone-ledger.tsv` is a lead for where to look, not a pass.

Measured 2026-09-23T03:18:12Z (local date 2026-09-22). Worker: local Darwin 25.5.0 arm64. Node v22.22.0. Bun 1.4.0. git 2.50.1. Python 3.9.6. `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` unset in the measurement shell before any command. `TYPESAFE_API_KEY` unset in that shell. No `omp` command was run. jev HEAD at read time: `e3dd0c4` (short).

Evidence level of every claim below: **oracle** (a command output or a file read at the pin), never **test** and never **live**. Jev call N = 0. Model = none. Lane = this catalogue receipt. Date = 2026-09-23T03:18:12Z. A number without those four is not in this file. Post-write clone check: `git status --porcelain` empty, HEAD still `65a39f393687675ce170e6094757de20370365b9`.

## Test table

| id | status | deciding evidence |
|---|---|---|
| T1 | PASS | Full SHA `65a39f393687675ce170e6094757de20370365b9`, commit date 2026-09-12 05:42:05 +0000, subject `Release v0.5.7`. License MIT, `LICENSE:1-3`, identical to `skills/typesafe-ai/LICENSE` (`diff -q` empty). `git status --porcelain` empty before the receipt write and after it. `origin/main` is the same SHA. GitHub `main` API returned the same SHA (read-only; the clone was not fetched). |
| T2 | NOT-APPLICABLE | Catalogue class runs T1 and T3 only (`docs/PLAN-DEEP-KIT-20260922.md:427-428`; `docs/demos/upstream-repro/w70-t4-bar-20260922.md:23`). No suite: `git ls-files` is 6 paths, no test runner, no `package.json`. Not NOT-RUN: there is no command that could fail. |
| T3 | PASS | Inventory below. The catalogue publishes **1 named skill**, not 5. The five-plus rows are question instructions inside that skill, each with a deciding `file:line` and a workspace consumer check. If "skill entry" is read only as a README table row, the count is 1 (`README.md:36-38`) and a ≥5 named-skill bar is not met by the clone. That fact is recorded; it is not hidden inside the pass. |
| T4 | NOT-APPLICABLE | Catalogue. The committed bar says catalogues do not take it (`w70-t4-bar-20260922.md:23`). Assignment: no live call. Not NOT-RUN. |
| T5 | NOT-APPLICABLE | Floor arms are seat/benchmark (`PLAN-DEEP-KIT-20260922.md:417`). This clone measures nothing. |
| T6 | NOT-APPLICABLE | Incumbent arm is seat/benchmark (`PLAN-DEEP-KIT-20260922.md:418`). No accuracy rows exist to pair. |
| T7 | NOT-APPLICABLE | Calibration is seat/benchmark (`PLAN-DEEP-KIT-20260922.md:419`). No probabilities were collected. |
| T8 | NOT-APPLICABLE | Stability is seat/benchmark (`PLAN-DEEP-KIT-20260922.md:420`). No questions were asked. |
| T9 | NOT-APPLICABLE | No client, no POST, no key path (`SKILL.md:99-103` points at docs; `plugin.json:10` is the skills repo URL). Fault behaviour has no process to kill. |
| T10 | PASS | Verdict, claim statuses, NO-CLAIM, and the not-run distinction are in this file. Nothing was left NOT-RUN. |

## T1

Command, run inside `upstream/typesafe-ai/skills` after unsetting `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR`:

```
git rev-parse HEAD
git log -1 --format='fullsha=%H%nauthor_date=%ai%ncommit_date=%ci%nsubject=%s'
git status --porcelain=v1
git rev-parse origin/main
git ls-files
```

Verbatim:

```
65a39f393687675ce170e6094757de20370365b9
fullsha=65a39f393687675ce170e6094757de20370365b9
author_date=2026-09-12 05:42:05 +0000
commit_date=2026-09-12 05:42:05 +0000
subject=Release v0.5.7
```

Porcelain empty. `origin/main` = `65a39f393687675ce170e6094757de20370365b9`. Tracked files:

```
.claude-plugin/marketplace.json
.claude-plugin/plugin.json
LICENSE
README.md
skills/typesafe-ai/LICENSE
skills/typesafe-ai/SKILL.md
```

License: `LICENSE:1` is `MIT License`. Copyright line `LICENSE:3` is `Copyright (c) 2026 TypeSafe AI`. No OpenAI/Anthropic rider in the 21-line file. Nested `skills/typesafe-ai/LICENSE` matches (`diff -q` produced no output). `plugin.json:11` says `"license": "MIT"`. `SKILL.md:3` says `license: MIT`.

Parent jev repo does not track the clone (`git check-ignore` hits `.gitignore:64` `upstream/*`). Cleanliness was measured in the nested git repo, which is the pin. Status re-checked empty after this receipt was written. The clone was not edited.

GitHub `GET /repos/typesafe-ai/skills/commits/main` returned sha `65a39f393687675ce170e6094757de20370365b9`, date `2026-09-12T05:42:05Z`, message `Release v0.5.7`. Local pin is not behind public `main` as of this read. That API read is not a Jev call and did not update the clone.

## T3 — entries

Named skills in the catalogue: **1**. `README.md:36-38` table has one row, `typesafe-ai`. `SKILL.md:2` `name: typesafe-ai`. `marketplace.json:8-13` publishes one plugin, `typesafe`, source `./`. `plugin.json:2` name `typesafe`, version `0.5.7`.

The skill does not point at a second skills repo. GitHub links in the clone are only `github.com/typesafe-ai/skills` (`README.md:5`, `plugin.json:10`). Docs links are `https://docs.typesafe.ai/...` (`SKILL.md:32-53`, `:66-86`). The docs index (`https://docs.typesafe.ai/llms.txt`, the page `SKILL.md:32` names) lists documentation pages, not git repos. **Clone candidates: none. Nothing was cloned.**

`https://docs.typesafe.ai/agent-skill.md` tells a reader to copy the skill directory "including its reference files". This pin has no reference files (`git ls-files` above). That is vendor-docs drift against this SHA, not a missing repo.

Workspace loader: `.claude/skills/typesafe-ai` is a symlink to `.agents/skills/typesafe-ai`. That copy's `SKILL.md` sha256 is `71ea90d7906c6554c4f4c460ef7361b2d26f59116ccdae986dc6d997b9389f52`, identical to the clone's `skills/typesafe-ai/SKILL.md`. Provenance of the copy (copied from this clone, or installed separately from the same bytes) was not established. Byte identity is the claim.

Question instructions below are inside that one skill. They are not additional skills. "Consumer" means first-party code in this workspace that asks that question shape, or loads the skill file. Other upstream clones that happen to ask a similar question are not counted as consumers of this skill.

| name | what Jev question it tells an agent to ask | consumer in this workspace | file:line | claim status |
|---|---|---|---|---|
| typesafe-ai | Design the judgment from what the answer means, then ask Choice, Noul, or Score. README example: route support tickets by department, with human review when uncertain (`README.md:32`). | Loader: yes, byte-identical skill under `.agents/skills/typesafe-ai`. Question-asker: not this file; see the rows below. | `README.md:38`; `SKILL.md:2`; `SKILL.md:97-103` | partial — the skill is present and loaded as text; it decides nothing |
| choice | One of a defined set. Picks one option; the distribution compares competing options. | Yes. `askJevChoice` posts `{ type: "choice", instructions, criteria }` under the key `choice`. | Skill: `SKILL.md:101`. Consumer: `work/jev-client/src/index.ts:88`, `:259-260` | partial — wire shape exists; "picks one option" was not live-tested this run |
| noul | Whether a condition holds. Probability of yes; no separate confidence; one Noul per label when several may apply. | Yes. `askJev` posts `{ type: "noul", instructions }` and reads `.noul` only. | Skill: `SKILL.md:102`. Consumer: `work/jev-client/src/index.ts:186-187` | partial — our client matches "no confidence field" on the response it reads; not re-measured live |
| score | Degree along a described dimension. Probability-weighted position on ordered levels. | Yes. `askJevScore` posts `{ type: "score", instructions, criteria }` and refuses a criteria list shorter than 2 before any call. `work/jev-question-writing/SKILL-PURPOSE.md:89-94` (dated 2026-09-19) says no score caller exists; that sentence is stale against `index.ts:326`. | Skill: `SKILL.md:103`. Consumer: `work/jev-client/src/index.ts:326`, `:339-343` | partial — caller exists; probability-weighted claim not re-measured |
| no-match | Include a no-match outcome when nothing may fit. The model cannot choose an omitted value. | Yes for the instruction to include a no-match label. `none_token` is `__none__`. Two beads cases accept only `__none__`. The "cannot choose an omitted value" sentence was not tested. | Skill: `SKILL.md:119-121`. Consumer: `work/jev-beads-eval/policy.v1.json:37`; `work/jev-beads-eval/cases.v1.jsonl:2` | partial |
| verify-and-escalate | Check a claim or field against its evidence; send uncertain or failing cases to a person or a reasoning model. Points at the citation-check cookbook. | Yes. First-party citation check asks a Choice, `How does the section relate to the claim?`, labels `supports` / `contradicts` / `says_nothing`, and holds auto-accept at confidence 0.8. It cites the cookbook mirror, not `SKILL.md`. | Skill: `SKILL.md:83-86`. Consumer: `work/citation-check/src/check.ts:4`, `:19-25`; caller `work/citation-check/src/live.ts:5`, `:12-15` | partial — question shape is in our code; cookbook thresholds were not re-validated |
| route-and-fill | A request selects a handler and its typed parameters. Ask branch-specific questions up front; consume only the relevant answers. Points at the function-calling cookbook. | Partial. `jev-usage-router` asks one Choice over next-action classes and falls back to `bypass` under a confidence floor. It does not fill typed function arguments. No first-party port of the function-calling cookbook was found. | Skill: `SKILL.md:66-69`. Consumer: `work/jev-usage-router/src/router.mjs:88-99` | partial — routing Choice exists; typed-argument fill does not |
| ids-not-sent | Put the judgment in `instructions` and the answers in `criteria`. Question IDs are for code and are not sent to the model. | The writing rule is repeated in `work/jev-question-writing/SKILL-PURPOSE.md:98-100`. The wire does not match a literal reading of "not sent": the JS SDK copies `request` into the POST body and `JSON.stringify`s it, so question keys travel in the body. Whether the model is shown those keys is a server claim. This run did not call the API, so that half is not disproven and not demonstrated. | Skill: `SKILL.md:107-109`. Wire: `upstream/typesafe-ai/typesafe-sdk-js/src/client.ts:316-323`, `:362`. Writing rule: `work/jev-question-writing/SKILL-PURPOSE.md:98-100` | aspirational for model-visibility; contradicted on the HTTP body if "sent" means the request |

Rerank (`SKILL.md:75-77`) and value-extraction (`SKILL.md:70-74`) are further instructions in the same skill. A rerank measurement harness exists at `work/jev-client/question-shape-measure.mjs:274`. They are not extra skills and are not needed to clear five instructions. Not expanded.

## T10 — verdict

Result class: **not applicable**. This clone is a catalogue. It does not answer a labelled question, so it is not SELF, not FLOOR, and not INCUMBENT. No accuracy number is stated. N is not a sample size; no calls were made. This is not a smoke certification and not a certification.

RULEBOOK numeric tier scale was not opened this run (the RULEBOOK is not in this clone). Claim status uses the W7.0 words. Every row above is vendor prose plus a file:line in our tree or in the SDK. None is an independent accuracy result. Highest status in the table is **partial**. The model-visibility sentence is **aspirational**. Nothing in the table is **demonstrated** as a Jev behavior.

NO-CLAIM: no live Jev call, no accuracy, no calibration, no cost, no latency, no proof that question keys are hidden from the model, no proof that a cookbook threshold transfers, no claim that the byte-identical workspace copy was installed from this clone, no claim that loading the skill changes agent behavior. The 2026-09-19 lead's "nothing to fix" conclusion is not reused.

Nothing was NOT-RUN. T2 and T4–T9 are NOT-APPLICABLE by class, so the four earned-label fields (command, verbatim failure, `file:line`, two routes) are not owed. Recording them as NOT-RUN would invent a failure the class profile does not ask for.

## Boundary

This receipt pins the catalogue, reads its one skill, and checks whether this workspace already asks the question shapes that skill names. It does not prove those questions are well written, that Jev answers them, or that an agent which loads the skill follows it. It does not grade cookbooks. It does not update `EVAL.md`. It does not clone anything. A rerun that fetches into the clone, or that makes a live call, is a different receipt.

## Re-run

From the jev repo root, without printing secrets:

```
unset OMP_PROFILE PI_PROFILE PI_CODING_AGENT_DIR
git -C upstream/typesafe-ai/skills rev-parse HEAD
git -C upstream/typesafe-ai/skills status --porcelain
git -C upstream/typesafe-ai/skills ls-files
```

Expected: SHA `65a39f393687675ce170e6094757de20370365b9`, empty porcelain, six tracked paths, one `skills/*/SKILL.md`.

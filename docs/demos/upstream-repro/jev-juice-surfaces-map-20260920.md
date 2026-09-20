# Jev juice surfaces map — 2026-09-20

**Level:** `[pending]` — unpromoted synthesis. No live Jev call. No STATUS row
moves. `promoted = 0` stays the state of record.

**The question this file answers.** Given (1) Jeff's skillranker *process*
(`Dicklesworthstone/skillranker` public HEAD `6a74cca`), (2) the omp-jev
extensions we already have, and (3) `askJev` / `client.systemOne`, *where does
a typed judgment extract juice* on beads, agent-mail, cass, and the nearby
harnesses — and where does a cheap baseline already win?

A mode earns a card only if it names a **product tick**: a decision a later
agent would actually take (load this skill, skip the browser, refuse this
close, dig this cass hit, withhold this claim). A mode that only produces a
prettier log is not juice.

**Oracle for this receipt:** files on this tip, cited `path:line`. Not a
promotion, not a measurement of Jev, not a plan-to-plan.

---

## Honesty banner

- **Process ≠ product.** Skillranker at `6a74cca` can `rank`; it cannot yet
  inject advice (`sr hook` planned P6) or write the ledger from rank
  (`persistence() == "unavailable"`). We steal the *loop shape*, not the
  binary. Receipt:
  [`skillranker-process-archaeology-20260919.md`](skillranker-process-archaeology-20260919.md).
- **The 12-case score is not ours to re-litigate.** Live Jev on their
  diagnostic split: mean loss **0.167** vs always-abstain **0.833**, top-1
  **0.800** vs gate **0.90**, both misses = false abstention. Their policy
  forbids treating `diagnostic_synthetic` as holdout. Receipt:
  [`skillranker-corpus-measured-20260919.md`](skillranker-corpus-measured-20260919.md).
- **Hand-built numbers are ceilings.** Authored corpora inflated three
  results in one day (`NEGATIVE_EVIDENCE.md` R28). A card that cites an
  authored fixture as quality is lying.
- **Cost-benefit kill ≠ capability kill.** Harm-rule regex 12/12 vs Jev
  11/12 is a *cost-benefit* kill: Jev is fine and still not worth calling
  (`docs/INTEGRATIONS.md`). Compaction `keep_p` AUC 0.348–0.648 with a
  0.941 positive control is a *capability* kill: the question does not
  rank the thing.

---

## Sources opened (this pass)

| Path | What it is |
|---|---|
| `docs/demos/upstream-repro/skillranker-process-archaeology-20260919.md` | Designed loop, file:line, eval contract, gap list vs our three routers |
| `docs/demos/upstream-repro/skillranker-process-mirror-20260919.md` | What we copied into `work/omp-jev-route` (`decide`, 0/1/2 gate, `__none__`) |
| `docs/demos/upstream-repro/math-and-next-level-20260919.md` | Loss table algebra, prevalence \(t^\star\), VOI, unused Franken math |
| `docs/INTEGRATIONS.md` | Scoreboard: 0 promoted; regex wins tool_call; compact is L3 *measurement* |
| `work/omp-jev-route/` | Hardness observer + process slice (`src/process.mjs`, `src/gate.mjs`) |
| `work/jev-usage-router/` | Shadow Choice `local\|research\|browser\|bypass` |
| `work/skillranker-eval/` | Frozen contract harness; `--export` eval rows; live `NOT_RUN` without key |
| `work/jev-client/src/index.ts` | The only sanctioned `systemOne` body |
| `docs/demos/SDK-SURFACE.md` | Field names: `.noul` / `.probabilities` / `.choice` — no `.distribution` |
| `docs/demos/contracts/demo-4-foreman-lite.md` | Bead ACCEPTANCE judge (unbuilt command, CLEARED shape) |
| `work/taste-loop/CONTRACT.md` | Observe-only product-feel; stay unpromoted |
| `work/jev-score-register/register.mjs` | Hash-only score persist; not a cache; not an eval row |

Not re-run: `sr`, any keyed `systemOne`, cass index repair, `am inbox`.

---

## How to read a mode card

Every card below has the same fields. If a field is empty, the mode is not
ready to spend a key.

| Field | Meaning |
|---|---|
| **Product tick** | The decision a later agent takes. No tick ⇒ no juice. |
| **State** | Exact object handed to `systemOne` / `askJev` / `askJevChoice`. |
| **Question** | Choice / Score / Noul / ensemble, with the option set named. |
| **Output is good for** | What the caller *does* with the typed value. |
| **Cheap baseline** | The free thing that might beat Jev. Must be runnable. |
| **Loss / abstain** | 0/1/2 (or named withhold). Always-abstain control required if advisory. |
| **Export row** | JSONL a later `--score` can recompute without re-calling Jev. |
| **Do not** | The lie this surface invites. |

Wire fields stay the SDK's (`docs/demos/SDK-SURFACE.md`). A missing
`probabilities` throws; it does not score silence.

---

## Cross-cutting patterns stolen from skillranker

Copied from public `6a74cca` via the archaeology + the process mirror. Adopt
the mechanism; do not import the crate.

| Pattern | What it is | Where they put it | Our smallest seat |
|---|---|---|---|
| **`__none__`** | A real Choice option, not a missing score. `SkillId` rejects it. Ties against it **abstain**. | `jev/wide.rs:35`; `identity.rs:113-115`; `eligibility.rs:274-289` | `work/omp-jev-route/src/process.mjs` `NONE`; `work/skillranker-eval/score.mjs` |
| **Local eligibility before pay** | Empty / excluded / already-loaded roster never reaches the provider. Explicit name is local. | `eligibility.rs:88-108,147-197` | `decide()` in `process.mjs`; usage-router kill-switch is *not* this (overloaded) |
| **0/1/2 loss** | False abstention = 1; wrong pick / needless / unavailable = 2. Always-abstain cannot win by silence. | `tests/eval/evaluation_policy.v1.json:58-72` | `work/omp-jev-route/src/gate.mjs`; `work/skillranker-eval/score.mjs` `LOSS` |
| **Always-abstain control** | Required counterexample. On their 12-case file, \(\bar L = 10/12 = 0.833\). Coin-flip **1.011** is worse than doing nothing. | `expected_values.v1.json:56-74`; `always_abstain_counterexample_required: true` | `run.mjs --control always-abstain`; gate CLI prints `always_abstain_mean_loss` |
| **Diagnostic ≠ promote** | `split: diagnostic_synthetic` forbids promotion / calibration / statistical quality. Relabel as holdout is a validator hard-fail. | `evaluation_policy.v1.json:53-56`; `test_eval_policy.py:94-97` | Process fixture prints `promoted: false` even at precision 1.0 |
| **Structured decide** | `ranked \| explicit \| abstain \| unavailable` + reason + `none_probability` + schema stamp. `unavailable` is operational (loss 2), not cheap silence. | `output/mod.rs:34-38`; ledger CHECK at `storage/ledger.rs:194` | `jev.omp-jev-route.process.v1`; eval export `jev.skillranker-eval.score.v1` |
| **Fail-open hooks** | Ordinary abstention is silent. Never `{block:true}`. Shadow logs without injecting. Missing key registers **nothing**, not a fake score. | README hook quiet-exit; `HookMode::Shadow` default | Every `omp-jev-*` handler `return undefined`; compaction `:217-222`; harm-rule observe-only |
| **Adoption ≠ usefulness** | A logged decision is not a quality claim. Observations (`attempted/loaded`) ≠ judgments (`useful/harmful/neutral`). | ledger tables; `src/storage/ledger.rs:1-5` | `binding: log-only`; score-register stores a hash + number, **not** Y |
| **Selector ≡ claim** | Inventing a second `helpful` noul gate produced 11/12 abstentions. Score the Choice the product actually emits. | archaeology §3 + our oracle defect | `judgeSkillPick` — one Choice, no second question (`skillranker-eval/README.md:67-68`) |
| **Two-stage Jev we will NOT copy** | Wide + rerank is 2 paid calls/turn; their own `wide.rs:4-6` reranks even after `__none__` wins. omp rosters are small. | mirror "Steps we will NOT copy" | One bounded Choice + local `decide()` |

**What their product is still missing, so we do not copy the hole:** `src/`
never reads `synthetic_cases.v1.jsonl`. Rank does not write the ledger.
`sr eval` / `sr feedback` / `sr hook` are planned. Copying a schema without
a writer repeats `frozen_contract_not_evidence`. Copying a writer without Y
is a log, not a loop
(archaeology §7.2).

---

## Mode cards

### A. Skill / next-action ranking (skillranker-like)

**Product tick.** Load this exported skill next, or answer directly.

**State.** `{ task, constraints, already_loaded }` plus a **visible roster**
(installable / loaded ids only). Overflow case on their corpus has Y
`testing-fuzzing` and an empty exported roster — that is
`installableNotOffered=true`, not a model miss
(`work/skillranker-eval/README.md:56-59`).

**Question.** One **Choice** over roster ids + `__none__`. Instructions =
`PICK_INSTRUCTIONS` in `score.mjs`. No second Noul. Optional later ensemble:
per-survivor `fits::<id>` Noul *after* local admit, not as a gate that can
override a confident pick (that was the 0.750→0.167 defect).

**Output is good for.** `ranked` / `explicit` / `abstain` / `unavailable`
from `decide()`. The hook prints at most one invocation name (their
`MAX_SUGGESTED_INVOCATION_NAMES = 1`). Observe-only in omp.

**Cheap baseline.** (1) Exact-name / explicit directive — local, no provider
(`eligibility.rs:91-93`). (2) Always-abstain. (3) Recency of last loaded
skill. (4) Keyword overlap of `task` against skill `invocation_name`. If (1)
or (4) matches the Choice, drop the paid call.

**Loss / abstain.** Frozen 0/1/2. False abstention = 1; wrong pick / needless
/ unavailable = 2. Always-abstain \(\bar L = nPos/n\). Promotion gate
top-1 ≥ 0.90 is an **exit-2 FAIL**, not a printed note; `diagnostic_synthetic`
still cannot promote.

**Export row.** `jev.skillranker-eval.score.v1`:

```
schema, case_id, pick, y, loss, why, class, roster_ids, y_in_roster,
installableNotOffered, judge, lane, measured_product, binary_path, model
```

`measured_product` stays `false` unless `sr` is actually invoked. Numeric
noul/choice scores go to `work/jev-score-register/` (hash of state, never
preview). The register **cannot** carry pick/Y — write the eval JSONL too
or the export hole returns (`skillranker-eval/README.md:61-63`).

**Do not.** Invent a `helpful` noul gate. Point an authored 6-row fixture
at quality (R28). Claim 0.800 is holdout. Two-stage wide+rerank on omp.

**Status.** Process slice shipped, unpromoted
(`skillranker-process-mirror-20260919.md`: 19/19 tests; gate
`promoted: false`). Live Jev-on-their-12 is a prior receipt, not this file.

---

### B. Usage routing (local / research / browser / bypass)

**Product tick.** Grok Bot (or any extra-tool caller) takes the cheapest
adequate next action. Humans keep irreversible work.

**State.** `{ goal, completed_work, available_actions }`
(`work/jev-usage-router/src/router.mjs:84-88`).

**Question.** One **Choice** over `{local, research, browser, bypass}` with
those four criteria (`:16-21`). Pin `jev-1.13.0`. Confidence floor
(default 0.55) **forces `bypass`** (`:108-110`). Kill switches
`BYPASS_JEV=1` / `JEV_USAGE_ROUTER=0` / `config.enabled=false` skip the
call entirely.

**Output is good for.** Shadow: log only. Active: caller must honor
`action`. Default left at shadow after the 7-step smoke
(`VALIDATION-7STEP.md`).

**Cheap baseline.** (1) Goal-string regex: `https?://` / `book|flight|login`
→ browser; `search|lookup|who is` → research; `ls|README|this repo` →
local; `delete|pay|commit --force` → bypass. (2) Always-`local` (the
spend-safe default). (3) Always-`bypass` as the *always-abstain* analogue.
If the regex matches the Choice on a non-authored goal log, drop Jev.

**Loss / abstain.** Do **not** reuse 0/1/2 until `bypass` is split.
Today `bypass` conflates kill-switch, low confidence, transport failure,
"unclear", and "irreversible" (archaeology §7.1). Typed split:

| decision | meaning | loss if wrong |
|---|---|---|
| `ranked` (`local\|research\|browser`) | cheapest adequate | 2 if a heavier tool was needed *or* a cheaper one sufficed |
| `abstain` | genuinely unclear / not a tool turn | 1 if a tool *would* have helped |
| `unavailable` | key unset / transport / kill-switch | 2 (operational, not relevance) |

Always-`bypass` (unsplit) is an invalid control: it mixes cheap silence
with operational failure.

**Export row.** Existing daily JSONL plus the process fields:

```
id, ts, mode, ok, action, rawChoice, confidence, probabilities,
latencyMs, model, goal_hash, binding, decision, reason
```

Hash the goal (score-register rule: no `state_preview`). Label Y later
from what the caller *actually invoked*, not from the goal text.

**Do not.** Flip `mode: active` on an unlabelled log. Treat the 7-step
smoke as a loss table. Re-litigate per-turn *model* routing savings
(inverts on our sessions; `INTEGRATIONS.md` / route README).

**Status.** Shadow router exists. Hardness observer (`omp-jev-route`) is a
**different** question (heavy vs mechanical) and must not share this
Choice. Effective labelled n on hardness = 10 distinct turns, 7/10, with
length leak (`work/omp-jev-route/README.md`).

---

### C. Harm / tool-call observe (regex may win)

**Product tick.** Log (never block) a command that weakens a control in a
form no regex enumerates. dcg remains the only blocker.

**State.** `{ command, toolName, cwd? }` captured **at decision time**
(join yield without that text is 36.8%; `INTEGRATIONS.md`). Not a
reconstructed transcript.

**Question.** One **Noul**: `security_control_tampering` — "does this
command weaken, delete, or bypass a check?" The other three shipped
questions are **dropped** (`judge-seat-ruling-20260920.md`):
`irreversible_publication` 12/12 noise; `secret_staging` mostly
`infisical run` (correct pattern); `privilege_widening` n=1.

**Output is good for.** Observe-and-log. A later human audits the JEV-ONLY
remainder after `rules-v4` (mention-vs-use stripper). Never
`{block:true}`.

**Cheap baseline.** Four-regex harm-rule: recall **12/12**, FP **0/38** on
the committed corpus (`node work/omp-harm-rule/verify-claim.mjs`).
`rules-v4` on 2,000 real commands: 11 fires / 0.55% vs Jev 38 / 1.90%;
JEV-ONLY 29 of which 8 are the control-tampering remainder. Dumb keyword
list: 5/12. **Ship the classifier; drop Jev from the generic surface.**

**Loss / abstain.** This is detection, not advisory ranking. Use
Neyman–Pearson on a surface with *nonzero* measured FPR (this one posted
0 FP on the planted set — NP does not separate regex from Jev;
cost-benefit does). Abstain = "regex already decided." Jev is called
**only on regex-allow**. VOI of the paid call is negative if
`regex then jev` does not beat `regex` at declared
\((L_{miss}, L_{FP}, c_{call})\) (math §4 VOI).

**Export row.** Harm-rule decision + `toolCallId` (join key):

```
kind, toolCallId, command, regex_hit, jev_noul?, model?,
dcgVerdict_absent, timestamp
```

No fictional `context.dcgVerdict ?? 'unknown'` (residual still on the
observer *gate* path; `INTEGRATIONS.md`).

**Do not.** Publish "Jev on tool calls." Publish "one remainder question
on regex-allow." Cite 0/40 — that denominator is historical/unreproducible
(R34). Treat driven first-contact fires as working-dogfood.

**Status.** RULE WINS on the generic surface. Remainder seat is
provisional at n=8 JEV-ONLY rows, one reader, unlabeled 77,767-command
population.

---

### D. Beads triage & ACCEPTANCE grading

**Product tick.** A bead does not close on self-certification.
`jev-bead-check <id> && br close <id>` — the judge advises; the owner
closes (`docs/demos/contracts/demo-4-foreman-lite.md`).

**State.** `{ what, acceptance_lines[], diff_hunks[], bead_body_sha,
baseline_sha }`. Baseline is an explicit `--record-start` file, never
"diff against last week" (three panes share `main`).

**Question.** Ensemble, already contracted:

1. **Choice** over
   `{complete, requirements-met, tests-sufficient, verify-needed, human-needed}`.
2. **Noul per ACCEPTANCE line:** "the cited hunks answer this line."
   Insufficient context → withhold → line `unanswered` → `complete` is
   structurally illegal.

Deterministic overrides beat the model: empty diff ⇒ `human-needed`;
title-only bead ⇒ `unscopable-bead` exit 2; snapshot mismatch ⇒
`human-needed`.

**Output is good for.** Checklist
`ACCEPTANCE <n>: supported|unanswered <- file:hunk (p=0.xx)` plus overall
verdict. Exit 0/1/2 agrees with the text. No prose summary — Jev
generates nothing.

**Cheap baseline.** (1) Missing `## WHAT` / `## ACCEPTANCE` regex
(`BEAD-TEMPLATE.md`). (2) Empty `git diff <baseline> HEAD -- <owned>`.
(3) ACCEPTANCE names a file the diff deletes. (4) `br ready --json`
priority + dependency closure — **no Jev** — for *queue* triage. Jev
earns a seat only on the *substance* of a close.

**Loss / abstain.** Advisory 0/1/2 on the close:

| outcome | loss |
|---|---:|
| correct `complete` / correct withhold on empty | 0 |
| false withhold (`verify-needed` when the diff answers) | 1 |
| false `complete` (empty diff, unanswered line, deleted evidence) | 2 |

Always-`human-needed` is the always-abstain control. A table that only
charges false completes makes silence win.

**Export row.**

```
bead_id, baseline_sha, bead_body_sha, verdict, exit, unanswered[],
acceptance_noul[], choice, model, lane
```

**Do not.** Auto-`br close`. Judge whether ACCEPTANCE was the *right*
acceptance (planning, not this command). Time-based baselines.

**Status.** Contract CLEARED at rung 2 (shape). Command not built. H1
snapshot-bound claim-check may supersede for *claims*; this card stays
for *bead closes* until a non-author rules supersession
(`PLAN.md` § the H1/demo-4 steelman).

---

### E. Agent-mail triage (no send)

**Product tick.** Read the inbox and file-reservation conflicts; decide
which messages block *this* pane. **Never send.** Transport has been
`count: 0` across long stretches (`docs/demos/tick.md`, duel-2
dispatches). A judge on an empty inbox is an empty scan set = ERROR.

**State.** `{ subject, body_head, from, thread_id, reservation_paths[],
my_reserved[] }` from `am inbox` / `am file_reservations conflicts`. No
outbound draft.

**Question.** **Choice** `{act_now, wait, ignore, unavailable}` with
`__none__` ≡ `ignore` (not my files, not my bead, FYI). Noul optional:
"this message names a path I have reserved."

**Output is good for.** Local ordering of *our* next edit. Not a reply.
Not a wake-up (`hub send` is a different harness).

**Cheap baseline.** (1) `thread_id` equals the bead we claimed.
(2) Intersection of `reservation_paths` with our reserved set.
(3) Subject prefix `[<bead-id>]`. If any of these fire, Jev is ceremony.

**Loss / abstain.** 0/1/2 advisory. False ignore of a conflict on *our*
path = 2 (we will clobber a sibling). False `act_now` on FYI = 1.
`unavailable` when `am inbox` errors or returns no schema.

**Export row.**

```
ts, thread_id, decision, reason, path_overlap, bead_match, lane
```

No message body in the log (mail is the other pane's work).

**Do not.** `hub send` / `am send` from a judge. Treat 19 consecutive
`count: 0` as "inbox is clean." Invent a mail server.

**Status.** Transport often dead. Juice is **zero** until a session
produces joinable inbox rows. First experiment is a logger, not a Jev
call.

---

### F. Cass hit ranking / dig-vs-invent

**Product tick.** Before writing a new instrument, open a prior session
that already asked the question — or honestly invent.

**State.** `{ query, hits[{path, n, snippet_hash}], current_bead_title }`.
Hits from `cass search "…" --robot --limit 5` (never bare `cass` — TUI).
Stage-0 already publishes `cass search "jev typed questions" --robot --limit 5`
(`AGENTS.md:1410-1411`).

**Question.** **Choice** over hit ids + `__none__` ("no hit is the same
question; invent"). Optional Noul per hit: "this session solved *this*
query, not a neighbour."

**Output is good for.** `dig <path>` vs `invent`. Stops the Rule 13
failure mode (nineteen clones untouched while we graded our own demos).

**Cheap baseline.** (1) Exact token overlap of query against snippet.
(2) Same-repo + recency. (3) `rg` the query against
`docs/demos/upstream-repro/*.md` titles — often the hit is already a
receipt. Cass index repair has blocked runs
(`docs/demos/dispatch/wave-a-muse-queue.md`). Off-PATH
⇒ steal the AGENTS.md command, do not report "cass missing"
(`docs/essays/dont-give-up-gaps.md` skill A).

**Loss / abstain.** 0/1/2. False `__none__` when a hit is the same
question = 1. Wrong hit (neighbour session, different question) = 2.
Always-`__none__` = invent-everything = the control that must lose if
cass is useful.

**Export row.**

```
query, pick, y_session_path, loss, why, n_hits, cass_ok, lane
```

**Do not.** Invent `--workspace <project>`. Use cass as an oracle of
*truth* — it is an index of prior agent talk, including our own
wrong numbers.

**Status.** Ground truth can be authored after the fact (label: "did
opening this hit change the next edit?"). Until `cass health` is green
in the session, this is `PREPARED-NOT-MEASURED`.

---

### G. Eval honesty (co-presence, outcome join, random-judge)

**Product tick.** A suite or a live logger that cannot tell a working
judge from a coin flip is not allowed to print a quality number.

**State.** Three different states, do not conflate:

| arm | state | already measured |
|---|---|---|
| **Random-judge** | the repo's own test fixtures, judge seam patched to well-formed random | 254/305 (83%) tests still green; 17 class-C, all in `system-one-adapter-python` (`random-judge-substitution-20260919.md`) |
| **Co-presence** | one omp session JSONL containing observer *and* bridge rows | 10 lab sessions; working-profile OPEN (`INTEGRATIONS.md`) |
| **Outcome join** | `{decisionId, toolCallId}` linking decision → outcome | mechanism MET at n=1 lab (`a2e2035`); 36.8% historical join without command text |

**Question.** Not a Jev quality question. **Meta:** (1) does the test
fail a random judge (class C)? (2) does the logger write `toolCallId`?
(3) does a later outcome row share that id? Optional Jev **Noul** only
on the joined remainder: "did this allowed command's outcome match the
decision's predicted harm?" — and only after regex.

**Output is good for.** Gate: refuse to cite a suite with 0 class-C
tests. Gate: refuse "working dogfood" without co-presence + id-join on
a **working** profile. The dogfood logger schema already has
`decisionId` / `recordType: decision|outcome`
(`dogfood-logger-20260919.md`).

**Cheap baseline.** `node --test` after substituting a random
`askJev`. `rg toolCallId` on the session JSONL. Always-unjoined rate
from the 63.2% `js-bash-<uuid>` miss class.

**Loss / abstain.** Honesty is binary: class-C present or not;
joinable or not. Do not 0/1/2 a logger. For the optional remainder
Noul, prevalence of true harm ≪ 3.95% `isError` (benign grep-no-match).
State \(\pi\) beside any AUC.

**Export row.**

```
schema, session, decisionId, toolCallId, joined, class_c_tests,
random_judge_survival, lane
```

**Do not.** Call co-presence "working." Count 24 route rows of one
turn as n=24. Treat `isError` as harm (revert predicate withdrawn).

**Status.** Highest-leverage juice *about our own tools*. Zero-API.
This is how a later promotion becomes possible; it is not itself a
promotion.

---

### H. Question-writing / judge quality meta

**Product tick.** Ship a wording that discriminates on a holdout the
author did not write; cut a wording that is a constant.

**State.** The **same** committed cases, original vs rephrased
(`work/jev-client/question-shape-measure.mjs`). Never tune on the
holdout.

**Question.** The object under test *is* the question. Rule, stated
before running: DEGENERATE = same verdict everywhere; else must beat
the better constant to DISCRIMINATE, else WEAK
(`question-shape-20260919.md`).

**Output is good for.** Rescue or refuse a question *in an existing
extension*. Measured: visible-property rephrasings rescued 3/7
(noise, definitional, destructive); scope and unverifiable refuted;
leading partial. Application: rerank noise+definitional shipped;
dispatch destructive **not** shipped after holdout collapse
(`question-rescue-application-20260920.md`).

**Cheap baseline.** (1) Always-yes / always-no constant. (2) "Is this
string in the text?" regex. If the regex matches the Noul, the
question is a linter — drop Jev (`taste-loop` stop-conditions).

**Loss / abstain.** Not 0/1/2. Verdict ∈ {DISCRIMINATE, WEAK,
DEGENERATE}. A second-gate Noul that never clears 0.5 is a selector
bug, not a model result. Cut any noul constant at 0.5
(`taste-loop/CONTRACT.md` field rule).

**Export row.**

```
question_key, wording_id, n, said_yes, spread, vs_constant, verdict,
holdout_verdict, lane
```

**Do not.** Adopt a rescue that only wins on the author's cases.
Elaborating a question — three paired spam comparisons, the short one
won (`criteria-inversion-20260918.md`).

**Status.** Process exists. Next juice is applying it to **new**
questions before they ship, not re-grading the seven.

---

### I. Compaction / retransmit value-of-information

**Product tick.** Do **not** prune an omp session on Jev's say-so.
The remaining tick is: *is this compact-candidate worth a paid
keep/drop log* (measurement), not a deletion.

**State.** Result text + a transcript excerpt — call-local states
starve the model and were already refuted as the bound
(`compaction-retention-oracle-20260919.md`).

**Question.** Their product asks Noul "will this still be needed?" at
0.5 and **deletes**. Ours (`jev-compact`) asks the same family and
**only logs** `would-compact` / `refused` / `passthrough`. Handler
returns `undefined`. L4-as-pruning is unreachable: omp wants
`{summary, firstKeptEntryId}`, not a pruned list (`INTEGRATIONS.md`,
`NEGATIVE_EVIDENCE.md` R21).

**Output is good for.** A measurement instrument. Never a smaller
context.

**Cheap baseline.** **Keep everything.** 7–23× fewer mistakes than
Jev@0.5 on three real sessions (n=96 each). Recency and random at the
same drop budget are indistinguishable from Jev. Token-reappearance
oracle self-test: noise 0/200, end-of-transcript 0/200, real 89.5–92.5%
needed. `keep_p` needed 0.361 vs unneeded 0.369; AUC 0.348–0.648;
positive control (was-a-read) **0.941**.

**Loss / abstain.** Capability kill. No threshold works because the
probability does not rank future need (curve flat 1.7–2.1
mistakes/10KB, `compaction-threshold-curve-20260919.md`). Withhold =
do not call. VOI vs keep-everything is negative before \(c_{call}\).

**Export row.** Existing `~/.jev-compact.log` kinds only. Do not add a
drop writer.

**Do not.** Re-open UP-R4. Cite the upstream 87.1% char-save as
retention quality — that is compression, not recoverability.

**Status.** RULED_OUT as a pruner. Keep as L3 observe. Next juice is
VOI accounting on the **log**, not a new question.

---

### J. Taste / product-feel (taste-loop) — stay unpromoted

**Product tick.** None that this lane will take this week. The packages
log whether an artifact would *feel* usable to a client. That is not
a close, a route, or a block.

**State / question.** Per-package, already frozen in
`work/taste-loop/README.md`. Jev only on the regex remainder.
`none` is a first-class Choice label. timeoutMs 2500.

**Output is good for.** Observe-only `*_scored` / `*_error` /
`*_regex` rows. Never `{block:true}`. Never copy into `~/.omp`
(repo-relative imports; `9e6c88d` defect).

**Cheap baseline.** Every package *names* its stop-condition
(glossary hit-rate, `undo|cancel` presence, CTA heuristic, …). If the
regex matches Jev on the planted class, drop Jev. Heat cannot beat
always-`hygiene` ⇒ cut.

**Loss / abstain.** Unspecified, and that is why this stays
unpromoted. No Y. No prevalence. `measure.mjs` is a harness, not a
result.

**Export row.** `com.zeststream.omp-jev-<name>.decision.v1` — do not
join it to STATUS.

**Do not.** Register in a working profile. Write STATUS rows
(`CONTRACT.md` rule 12). Call heat "taste."

**Status.** WIP scaffold, eleven packages, 0 promoted. **This card
exists so a later pane does not "just wire" them.**

---

### K. Grading other agents' claims (pane duel style)

**Product tick.** A numeric claim in a receipt, README cell, or pane
callback is `EXACT` / `WRONG` / `UNVERIFIABLE` against a cited
artifact — and a close cannot treat UNVERIFIABLE as EXACT.

**State.** `{ claim_text, cited_artifact_span, unit, denominator }`.
Deterministic triple extraction **before** Jev (Demo-3 / claim-check
baseline). Jev does not extract.

**Question.** **Noul:** "the cited span supports this triple at this
unit and denominator." Choice only over `{exact, wrong, unverifiable}`
if the extractor already produced a triple. Insufficient span →
`unverifiable`, never `exact`.

**Output is good for.** Claim-audit rows a stranger can recompute.
Incumbent `bhumik154/claim-check` v0.6.0 already wins **test-count
claims in commit messages** offline. Jev's opportunity is the
documented unsupported classes (percentages, JSON receipts, stale
revision, same-number/wrong-denominator) —
`docs/demos/duel-2/BASELINE_claimcheck_vs_jev_COD.md`.

**Cheap baseline.** `claim-check` on its supported subset. `rg` the
number against the cited file. Always-`unverifiable` is the
always-abstain control (must lose if the corpus has EXACT rows).

**Loss / abstain.**

| outcome | loss |
|---|---:|
| exact when EXACT / unverifiable when no evidence | 0 |
| unverifiable when the span *does* decide | 1 |
| exact when WRONG, or wrong when EXACT | 2 |

Corpus already labelled: 60 claims, 19 EXACT / 4 WRONG / 37
UNVERIFIABLE (`claim-audit-20260918T003836Z.json`). Prevalence of
WRONG is low; state it.

**Export row.** Existing `jev.duel.claim-audit.v1` plus
`incumbent_unsupported|incumbent_unverified` from the *pinned tool's
output*, never inferred.

**Do not.** Let Jev invent the triple. Grade our own claim with our
own judge without a non-author (duel rule). Treat 19/20 "looks right"
as calibration.

**Status.** Rung-2 design, not a shipped checker. H1 snapshot-bound
evidence is the no-key cousin (bind claim → revision). Distinct unless
both authors concede supersession.

---

### L. Prevalence-aware threshold advice

**Product tick.** Refuse to ship 0.50 / 0.80 / 0.90 as if they were
Bayes for the population we actually have.

**State.** `{ pi, L_fp, L_fn, c_abstain, scores[], labels[] }` —
priors from **committed counts**, losses declared **in the file**
before printing (math §4(b)).

**Question.** No Jev. This is the *consumer* of Jev scores. Optional
later: Jev **Score** on "is this prior applicable to *this*
workload?" — almost certainly a capability kill; do not start there.

**Output is good for.**

\[
t^\star(\pi)=\frac{L_{FP}(1-\pi)}{L_{FP}(1-\pi)+L_{FN}\pi}
\]

Act only when \(\min(\mathbb{E}[L\mid\mathrm{act}],\mathbb{E}[L\mid\mathrm{pass}])<c_A\).
Foreman: \(\pi=30/186449=0.016\%\) ⇒ \(t^\star\approx 0.99984\) at
equal losses ⇒ 1:2300 at 80% recall. dcg block prior 0.97%; a 15%
Jev-gate fire is already above \(t^\star\) unless \(L_{FN}\gg L_{FP}\).
Compaction \(\pi_{needed}\approx 90\%\) + drop-98% ⇒ ~9:1 wrong:right.

**Cheap baseline.** The identity \(t^\star(0.5)=L_{FP}/(L_{FP}+L_{FN})\).
Always-print-the-authored-threshold (0.50 / 0.80) — this tool exists
to beat that.

**Loss / abstain.** A published threshold that ignores \(\pi\) is a
process defect, not a model one. `PREVALENCE-UNKNOWN` (jev-review,
skillranker population) **refuses** \(t^\star\) rather than inventing
\(\pi\).

**Export row.**

```
surface, pi_num, pi_den, L_fp, L_fn, c_A, t_star, authored_t,
usable, source_receipt
```

**Do not.** Invent \(\pi\) for review or skillranker. Retune a live
hook from this file. Add STATUS columns (ceremony; math §3).

**Status.** Algebra is on tip. Script named in math §4(b) is the next
concrete lever and is **not this PR**.

---

## Nearby harnesses (not first-class modes)

These sit next to A–L. Most already have a cheap winner. Jev only if
the card's remainder rule fires.

| Harness | What it already decides | Jev seat? | Cheap winner |
|---|---|---|---|
| **`br` / `bv`** | ready queue, deps, steward | Mode D on *close substance* only | `br ready --json`; `bv --robot-next` |
| **`am`** | inbox + reservations | Mode E, no send | path ∩ reserved; bead-id prefix |
| **`cass`** | prior-session search | Mode F | token overlap; `rg` receipts |
| **`hub`** | live peers, jobs, supervised procs | none — routing a wake is coordination, not judgment | `hub list` |
| **`dcg`** | block destructive git / host policy | none on the block path (fail-open at `dcg-guard.ts:599-610`) | the guard itself; 0.97% prior |
| **`ubs`** | bug scan | none | `ubs <changed-files>`; exit 3 on docs ≠ pass (R6) |
| **`fh`** | doctrine ranker | none as citation | `fh ranked, we opened` (`INTEGRATIONS.md:11-16`) |
| **`ripwire`** | symbol map, `--quality-delta` | none | `--exemplar` before a new symbol |
| **`claim-check`** | test-count claims | Mode K remainder | v0.6.0 on its documented subset |
| **`jev-score-register`** | persist hash+score | plumbing for A/B/C/H | not a judge |
| **`dogfood-logger`** | decision/outcome JSONL | plumbing for G | join by `decisionId` |
| **`omp-jev-preaction`** | wipe-regex observe | Mode C local-eligibility cousin | seven regexes, no Jev |
| **`jev-compact`** | compact *measurement* | Mode I | keep-everything |

---

## Ranked first experiments (top 10)

Selection, in order: ground truth on disk → prevalence known →
zero-API → decision leverage (autonomous loop). Each row is a
**product tick**, not a doc.

| # | Surface | ACCEPTANCE (live command sketch) | Expected cheap baseline | NO-CLAIM |
|---|---|---|---|---|
| 1 | **L — \(t^\star(\pi)\)** | `python3 work/oracle-kit/prevalence_threshold.py` prints \(t^\star\) for foreman `30/186449` and dcg `488/50149` at declared \((L_{FP},L_{FN},c_A)\); planted \(\pi=0.5\) recovers \(L_{FP}/(L_{FP}+L_{FN})\); \(\pi=0\) refuses | authored 0.50 / 0.80 | Does not invent \(\pi\) for review/skillranker. Does not retune a hook. |
| 2 | **G — random-judge on *our* packages** | `node --test work/omp-jev-route/test/*.test.mjs` after injecting a random `askJev`; count class-C (label the judge did not supply). Planted: a tautological `toMatchObject({noul})` is **not** class-C | 83% upstream survival is the prior; we do not assume ours is better | Does not score Jev. Suites' blindness only. |
| 3 | **G — outcome join on a working profile** | One pane-0 / added-test-pane session: observer decision with nonempty `toolCallId` joins a same-session `omp-dcg-bridge` row. `rg` both types; join count ≥ 1 **and** `dcgVerdict` absent (not defaulted). Fail-open: handler returns `undefined` | n=1 lab already proved the mechanism; this tick is *profile*, not wiring | Not a rate. Not organic precision. Not a Jev quality number. |
| 4 | **A — `decide()` on a roster we did not author** | `node work/omp-jev-route/src/cli.mjs decide` against a roster extracted from a real omp session's loaded skills + the turn's user text; Y labelled **before** scores from what the agent actually loaded (or `__none__`). Gate must print `always_abstain_mean_loss` and `promoted: false` | exact-name / already-loaded local admit; always-abstain | Not their 12-case re-score. Authored 6-row fixture is contract-only (R28). |
| 5 | **D — empty-diff RED for bead-check** | Offline canned asker forced to `complete` on a fixture whose baseline == HEAD → command still prints `human-needed` exit 2. Title-only bead → `unscopable-bead` exit 2. No key. | missing WHAT/ACCEPTANCE regex; empty `git diff` | Does not grade ACCEPTANCE quality. Does not auto-close. |
| 6 | **C — remainder after rules-v4** | `node work/toolcall-judge-v3/decide-seat.mjs` (or the frozen 2,000-row draw, seed 20260920): of JEV-ONLY rows, only `security_control_tampering` may stay; write rules for the six control-weakening *forms*, re-run, report what Jev **still** finds. Zero new API if the draw is reused | `rules-v4` + mention-vs-use stripper | Unlabeled population. One reader. Not a block recommendation. |
| 7 | **B — split `bypass` on the existing log** | Re-score `work/jev-usage-router/logs/routes-*.jsonl` with a local regex baseline vs the logged Choice; label Y from what the caller did next (or `unknown`). Print always-`local` and always-`bypass` losses **after** splitting operational unavailable out of `bypass` | URL/verb regex; always-local | Log goals are few and partly authored (flights / README). Not a promotion. |
| 8 | **K — claim-check vs Jev on the 60-row audit** | Run pinned `claim-check` v0.6.0 on the 60 labelled claims; mark `incumbent_unsupported` from **its** output. Jev Noul only on that remainder, budgeted, once, `jev-1.13.0`. Ship only if additional correct-actionable coverage beats cost | claim-check on test-count subset; `rg` the number | 37/60 already UNVERIFIABLE. One labeller. Not Demo-3 implemented. |
| 9 | **H — holdout-or-cut on the next new question** | Before any new `QUESTIONS` / `CHOICE` lands: freeze wording → author holdout **after** → `measure.mjs` must DISCRIMINATE vs the better constant. Planted: a constant-0.5 noul fails the kit | always-yes / always-no; string-in-text regex | Does not re-rescue the seven. Visible ≠ shorter (confound already named). |
| 10 | **I — VOI table on harm-rule, not compaction** | `node work/omp-harm-rule/verify-claim.mjs` already exits 0. Add the declared-loss table `E[L\|regex]`, `E[L\|jev]`, `E[L\|regex then jev-on-allow]`, `c_call`. If regex-then-jev does not beat regex, VOI < 0 and the paid call stays dropped | regex 12/12, FP 0/38 | 12 planted harms ≠ incidents. FP denominators not like-for-like (R34). Compaction VOI is already negative; do not re-spend there. |

**Deliberately not in the top 10.** Mode **E** (inbox often empty — empty
scan set). Mode **J** (stay unpromoted; no Y). Mode **F** until
`cass health` is green (then it jumps the queue: Stage-0, zero-API,
Rule 13). Two-stage skillranker wide+rerank. Franken Decision-Contract
TSV columns. `sr hook` ourselves.

---

## What this map refuses

- A thirteenth `omp-jev-*` package without a named consumer, a planted
  RED, and a cheap baseline that might win.
- Copying Quill/254-prefilter, FrankenTUI, XDG SQLite, or Claude
  `UserPromptSubmit` (wrong harness; mirror "will NOT copy").
- Treating `diagnostic_synthetic`, the 6-row process fixture, or any
  authored taste `measure.mjs` as quality.
- Promoting taste-loop, jev-compact-as-pruner, or generic tool_call
  Jev.
- Asking Joshua which surface is next. The table above is the
  selection.

---

## NO-CLAIM

- Unpromoted synthesis. `[pending]`. No new measurement. Numerals
  (`0.167`, `0.833`, `12/12`, `0/38`, `3.95%`, `36.8%`, `254/305`,
  `30/186449`, `7/10`, `n=1` join, `0.348–0.648`) are **other
  receipts'**, cited, not re-derived beyond identities already in
  `math-and-next-level-20260919.md`.
- Skillranker the product is **NOT_RUN** here (no `sr`, no keyed
  rank). The process mirror's 19/19 and `promoted: false` are that
  receipt's, not this file's.
- No working-profile dogfood. No live `TYPESAFE_API_KEY` use.
- `STATUS.tsv` / `VERDICT.md` / `GATES.md` untouched.
- Nearby-harness "cheap winner" is a hypothesis to run, except where
  a receipt already named the winner (harm-rule regex; compaction
  keep-everything; claim-check on test counts).

**Next concrete lever:** experiment **#1** in the table
(`prevalence_threshold.py` / `decisionLoss` as named in math §4(a)–(b)).
This file does not land that script. It names why that tick, not
another inventory, is the juice.

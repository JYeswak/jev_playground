# Classifier families rebuilt around the fleet's decisions (proposal, 2026-10-04)

The conductor applies this proposal to the bead graph. It is read-only research: no `br` was run, no model was
called, and the only file written is this one. The frame comes from Joshua (2026-10-04): this project is about
how to understand and use classifier models, not about "Jev". So every family below is named for a **fleet
decision**, and Jev is one arm in each bake-off.

## Citation keys

| Key | Means |
|---|---|
| `DP-n` | `var/agent-tmp/dogfood/fleet-schema/decision-points.jsonl` line *n* (fields `occurrences_14d`, `label_count`, `label_source`, `existing_surface`) |
| `S:n` | `var/agent-tmp/dogfood/fleet-schema/SCHEMA.md` line *n* |
| `P:n` | `work/plan-20261004/PRODUCT.md` line *n* |
| `R:n` / `RM:n` | `README.md` / `ROADMAP.md` line *n* |
| `E:n` | `work/plan-20261004/ECOSYSTEM.md` line *n* (its `NE:` refs are to `NEGATIVE_EVIDENCE.md`, as quoted there) |
| `E1`, `E2`, `X4`, `X7` | `var/agent-tmp/dogfood/{e1-verdict-holds,e2-finding-novelty,x4-vendored-probe,x7-gate-rules}/RECEIPT.md` |
| `B:id@n` | `.beads/issues.jsonl` line *n*, bead *id* |
| `OK:id` | `var/agent-tmp/dogfood/okit-list.json` (omp-kit tracker snapshot), bead *id* |

**Score rule** (unchanged from `gen.py`, S:137): `score = occurrences_14d × avail`, where avail is 1.0 at ≥100
outcome labels, 0.5 at 30–99, 0.25 at 1–29, and 0 otherwise. A family's score is the sum over its decision
points. "Labels" are **outcomes only**, never the decision records (S:45-46).

**Prevalence-first rule:** every family states the majority-constant score on its own labels. If there are no
labels, the constant is UNDEFINED, and the family can make no quality claim (P:76, row 4).

Arms are listed cheapest first: **R** rule/regex/lookup · **L** lexical (BM25, TF-IDF + logistic regression) ·
**Em** embedding probe (Qwen3-Embedding-0.6B/8B, nomic-embed, bge-base, MiniLM; ENCODER-INVENTORY.md:73-79) ·
**En** encoder (`protectai/deberta-v3-base-prompt-injection-v2`, `cross-encoder/nli-deberta-v3-base`,
`lytang/MiniCheck-RoBERTa-Large`, all under `$HF/hub/` and observed with `ls` on 2026-10-04; download log
`var/agent-tmp/dogfood/minicheck-dl.txt`) · **LM** local LM (Clef-Flash, Kev-4B, nimble/tev1) · **TH** typed hosted
(Jev `jev-1.13.0`) · **G** general LLM (the D10 arm, P:196).

Hard constraint on hot-path families (anything that runs inside a tool call): hook budgets near 1.5 s rule out
Clef today (P:88, E:73). INFERENCE: any LM arm on `result`, `reread`, `route` or `recover` must therefore run
offline as a teacher, not at the call site.

---

## 1. The family set, ranked by occurrences × label availability

Sixteen families. Each of the 65 decision points goes to exactly one family or to section 4 (code/humans).
Families 1–10 have organic outcome labels in the logs. Families 11–16 have organic volume but zero organic
outcome labels, so each one rests on a planted or blind-labelled set, or waits for the outcome-logging bead (N6).

| # | Family (decision) | Decision points covered | Occ. 14 d | Outcome labels | Score | Majority constant on its labels | Incumbent today | Bake-off order | Bar (to commit before the first call) | Falsifier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **`result`**: keep a long tool result inline, spill it, or drop it | DP-29 L06 keep/spill/drop | 99,680 (spilled 26,592 + shaken 73,088, S:32) | 4,329 `artifact://` read-backs; 354 of 1,518 spilled ids read back (DP-29, S:121) | 99,680 | "not read back" 1,164/1,518 = **.767** | omp spill/shake size rule. `jev-dau5` Jev Choice is EXPLORED: 6/100 held misses vs baseline 0, 540,857 chars saved (B:jev-dau5@221, comment 2026-10-04T02:18Z) | R size+tool-name threshold → L TF-IDF on result head + tool + task → Em probe → TH Jev Choice (dau5 rows) → G. En/LM skipped: no fitting off-the-shelf head, and LM is over the hook budget | At the size rule's token savings, read-backs of non-inline results ≤ the rule's. Or, at equal read-backs, savings ≥ the rule's + a margin fixed in the PREREG | The size+tool rule matches the best arm on savings at equal read-backs. Then `result` stays a rule |
| 2 | **`rank`**: which `find` hit is the top passage/file | DP-28 L06 rank find candidates; DP-27 L06 web rerank (OFF) | 41,002 + 57 | 421 of 786 `find-rank` rows: the next calls touched a returned hit (DP-28) | 41,002 | "touched a hit" 421/786 = **.536** | omp native judge on `find` (Jev); 576 vs 5,293 tokens per located file (R:172) | R grep/path order → L BM25 top-1 → Em cosine top-1 → En ms-marco-MiniLM cross-encoder (on disk, ENCODER-INVENTORY.md:80) → TH Jev → G | On organic `find-rank` rows, Jev's touched-hit rate beats BM25 top-1's touched rate by a CI-excluding-0 margin. Cost is reported per 1k ($0.205, E:20-21) | BM25 or the cross-encoder ties Jev on touched rate. Then the $0.205/1k is not earned. The public FiQA win (R:150) does not transfer to organic traffic by assumption |
| 3 | **`reread`**: skip a repeat read of an unchanged file | DP-30 L06 repeat-read dedup | 36,827 | 20,388 "redundant" of 36,844 repeats (S:122) | 36,827 | "redundant" 20,388/36,844 = **.553** | read-dedup shadow, 566 rows, would-skip 216 (DP-30) | R content hash + line-range overlap + compaction boundary → stop. Further arms only if the rule's residual harm (below) exceeds the bar | Rule residual harm ≤ a preregistered rate. Harm = after a skip, the agent fetches the same bytes another way (`cat`, `sed -n`, a ranged read) within K calls, or an edit fails `stale_tag` | **Tautology warning:** the "redundant" label is defined by the same no-intervening-write rule as the baseline (DP-30 `label_source`). Scoring the rule on it is circular (generic rule 5). Only the residual-harm label can falsify. If no label can be defined that the rule does not produce by construction, this family is code, not a classifier |
| 4 | **`route`**: which tool or path for this request (locate tool first) | DP-13 L04 find vs grep vs glob; DP-16 L04 ask the human; DP-3 L01 prompt stage; DP-17 L04 web vs local; DP-6 L02 plan first or act | 21,008 + 286 + 17,449 + 3,448 + 1,895 = 44,086 | 1,250 (find→read, DP-13) + 42 (ask errors, DP-16); 0 elsewhere | 21,151 | Decision: grep 16,309/21,008 = **.776**. Outcome: find followed by read 1,250/2,128 = .587 | Rule text only ("find first"). `jev-kvcc` is deferred (B:jev-kvcc@364); find is 12.7% of find+grep against kvcc's own ≥40% bar (S:190) | R query-shape rule (regex metachars or an exact identifier → grep; prose → find) → L → Em probe → En NLI zero-shot over the tool labels → LM Kev-4B/Clef offline → TH Jev Choice → G | Per locate episode (first locate call → first read/edit of the file finally edited): tokens and calls vs the R rule on held episodes. Prior: jev-ynn7 1,861 → 404 tool-result tokens per success (B:jev-kvcc@364) | R ties the best arm on tokens per located file. Banking77 (R:144, P:58) stays a public benchmark and is not evidence for this family |
| 5 | **`nudge`**: should this injected guidance fire now / is it actionable | DP-11 L03 judged TTSR rule applies; DP-8 L03 skill hint; DP-7 L02 todo-stale nudge; DP-33 L06 late LSP diagnostic; DP-9 L03 skill veto; DP-10 L03 which skill to read | 7,954 + 3,492 + 2,106 + 699 + 433 + 7,795 = 22,479 | 722 TTSR (session, rule) re-fires of 1,568; 225/954 hints followed; 453/2,106 todo nudges followed; 133/699 LSP acted on (S:127-130) | 14,251 | TTSR no re-fire 846/1,568 = **.540**; hint not followed 729/954 = **.764**; todo ignored 1,653/2,106 = **.785**; LSP not acted 566/699 = **.810** | TTSR + Jev judge (7,349 calls, S:29); skill hint PARKED but still firing (`jev-35sg`, B:jev-35sg@49); todo nudge and LSP are omp rules that always inject | R per injector (TTSR regex trigger alone; turns since last todo op; LSP severity == error; silence for hints, R:185) → L → Em → En NLI "does rule text apply to this span" → LM tev1 (X5) → TH Jev Score/Noul → G | Per injector: suppress ≥ a preregistered share of ignored injections while keeping ≥ a preregistered recall of followed ones, vs the R rule on the same rows | R matches the best arm. Also: the TTSR re-fire label is a non-compliance proxy, not a "rule applies" label (S:127). If blind labels disagree with it, that label is withdrawn for TTSR |
| 6 | **`recover`**: after a failed bash/edit call, retry identically, change, or re-read | DP-31 L06 bash-error recovery; DP-32 L06 edit-error recovery | 8,948 + 3,022 | Bash: next-bash outcome 5,144 (identical retry ok 245 / err 76; changed ok 4,142 / err 681). Edit: re-edit outcome 1,500 (ok 1,281 / err 219) (S:123-124) | 11,970 | Bash: next call ok 4,387/5,144 = **.853**; identical retry ok 245/321 = .763. Edit: re-edit ok 1,281/1,500 = **.854** | None (DP-31, DP-32) | R error-class regex (timeout/network/lock → retry; syntax/not-found/permission → change). For edit, the error class is exact (stale_tag 1,193, never_displayed 738, parse 91, not_found 66; DP-23) → L on stderr → Em → TH Jev Choice → G. En/LM skipped: forecasting prior below | Beat the .853 constant and the R error-class rule on next-call success, on held sessions | Prior evidence says this loses: "will a retry succeed" is a forecast, and the retry model scored .444 vs majority .556 (E:107). If no arm beats R, the decision stays with the rule and the agent. Do **not** ship "block identical retry": it would be wrong on 245/321 = 76% (S:162, S:189) |
| 7 | **`land`**: is this commit / close ready (includes vendored-code check of the staged set) | DP-54 L12 commit now / staged set right; DP-56 L12 close this bead; DP-51 L11 claim/close without evidence | 4,425 + 677 + 1,364 | 466 commit (isError 436, hook reject 23, revert 7); 117 close (refused 69, isError 48); 69 claim/close (S:131-132, DP-51) | 5,784 | commit not-failed ≥ (4,425−466)/4,425 = **.895**; close ok ≥ 560/677 = **.827** (INFERENCE: the failure categories may overlap, so both are lower bounds) | guard-rule stage-all/commit-backtick (191 + 129 fires, DP-20); `.beads/policy.yaml` reviewer gate; TTSR kit-close rules; vendor-paste shadow (Jev cut .35 + Clef, R:183, R:187) | R failure-class table (nothing to commit, hook, index.lock, policy refusal) → L TF-IDF on staged paths + message. For the vendored sub-check: L TF-IDF probe (X4 winner) → Em (X4b) → TH Jev → LM Clef. Further arms only if R leaves model-addressable residue | First: share of the 436 + 117 failures that code can check **before** the call. Only the remainder is classifier-addressable | Most failures are code-checkable. Then this is omp-kit's landing primitive (OK:…rz5.86 LAND1, OK:…rz5.95 MP3; RM:54 puts git writers outside jev's mission) and jev ships no classifier |
| 8 | **`outcome`**: did the user accept the last answer (label producer for `effort`/`watch`) | DP-5 L01 user accepted last answer (+ DP-48 aborts as a label source, not a decision) | 7,536 (+ 5,385 aborts, DP-48) | 31 correction-regex hits (floor, recall unchecked; S:133) | 3,768 | "accepted" 7,505/7,536 = **.996** (floor) | None | R correction regex → L → Em → En NLI ("the next turn rejects the answer") → TH Jev Noul → G | Recall of the R regex on ≥200 blind post-answer turns is measured first. A model must raise recall at equal precision | The regex's blind recall is already ≥ the bar, or blind positives number <30 (P:77, row 3). Then the label stays a regex and no model is built |
| 9 | **`pin`**: which read files stay pinned through compaction | DP-41 L08 file pinning | 1,577 | 1,385 compactions with a prior file re-read within 30 calls (S:126; INFERENCE: some are routine) | 1,577 | "re-read" 1,385/1,577 = **.878** | None; compaction is omp native (DP-39) | R pin-all-readFiles within budget → R pin files edited in the last N turns → L path mentioned in the summary → Em → TH Jev Choice | Re-read tokens avoided minus pinned tokens, vs pin-all and the edited-last-N rule | Pin-all fits the budget and ties every arm. Keep this separate from `jev-g2uv` (turn keep/drop, refuted: keep 0/32, E:111) |
| 10 | **`delegate`**: delegate or inline, which agent type, which tier, accept the result | DP-42 delegate or inline; DP-43 agent type; DP-44 model tier; DP-45 accept subagent result | 569 + 1,051 + 1,051 + 1,691 = 4,362 | 7 task errors + 32 yield errors (DP-43, DP-45) | 1,109 | accept 1,659/1,691 = **.981**; task ok 1,044/1,051 = **.993** | None. `jev-t5jk` deferred covers tier only (B:jev-t5jk@497) | Labels first (N8). Then R "always task / parent model / accept when data present" → L → Em → TH Jev Choice → G | No bar until an outcome label (result redone, reverted, or reviewer-rejected) has ≥30 positives (P:77, row 3) | The joined outcome label stays under 30 positives in 14 d. Then the family is DROPPED as unlabelled |
| 11 | **`review`**: does a verdict hold; is a finding new or a repeat | DP-53 L11 finding new vs repeat; DP-50 L11 diff review verdict | 195 + 25 | 0 organic. Offline blind sets: E2 85 rows (16 new / 69 repeat); E1 55 rows (21 held / 34 not) | 0 | E2 "repeat" 69/85 = **.812**; E1 "not held" 34/55 = **.618** | Rules beat Jev on both. E2: same-bead+class rule 77/85 (.906) vs Jev 49/85 (.576). E1: keyword rule acc .618 κ .288 vs Jev .400 κ −.067 | R (incumbent) → L near-duplicate (Jaccard/TF-IDF cosine) → Em cosine → En NLI / MiniCheck (X3) for verdict-holds → TH Jev (lost, E1/E2) → G | ≥100 blind rows before any held-out claim (E:133). Beat the R rule on accuracy and κ | The R rule stays ≥ every arm on ≥100 blind rows. Then `review` is code |
| 12 | **`memory`**: is this recalled memory relevant now; inject; recall now | DP-35 memory relevance; DP-36 ee-task-context inject; DP-37 recall now | 39,179 + 1,126 + 720 | 0 organic (DP-35-37). Blind: 6 relevant of 100 (E:131) | 0 | always-drop .94 drop precision (E:93); "irrelevant" 94/100 | Mechanical top-3 cut + Jev drop (enforce switch absent, `jev-08hr`) (P:61) | R top-3 cut (incumbent) → L → Em (bge/Qwen3) cosine to task → En NLI → TH Jev → G | X8: upper 95% bound of P(drop given relevant) ≤ tolerance on ≥59 relevant items (P:202) | X8's falsifier (README.md:54) |
| 13 | **`gate`**: is this command risky (observe layer; dcg blocking stays code) | DP-19 observe cascade; DP-21 harm rule (codex profile) | 39,279 + 35,072 | 0 organic outcome (DP-19, DP-21). Blind: 396 rows, 47 harm (X7:10) | 0 | "no-harm" 349/396 = **.881**; weighted 1,637/1,684 = **.972** (X7:33) | Jev five-Noul behind the nimble cascade. X7: Jev 47/47, weighted FA 1.40%, vs dcg + pre-rule 7/47, FA 14.81% | R dcg + pre-rule (**run: LOSES**, X7) → L → Em → En → LM nimble (cascade first pass, 0/950 harmful cleared, R:176) → TH Jev (incumbent) → G (`jev-qsa6` deferred) | Jev's catch at an NP false-alarm cut fixed on negatives (149 negatives for α=.02, P:189) | A cheaper arm reaches 47/47 at ≤1.40% weighted FA. Organic positives stay ~0 (0/453, E:106), so no organic recall claim |
| 14 | **`screen`**: is this tool/web result an injection | DP-25 tool result; DP-26 web result | 19,250 + 585 | 0 organic; organic flags 83 are decisions (DP-25). Planted set: 300 clean + 300 markerless + 662 public (E:124) | 0 | Planted set is balanced (constant .5). Organic flag rate 83/19,250 = .0043 (decisions, not labels) | Jev Noul annotate-only: 268/300 caught, 5/300 false flags (R:101-102) | R local pattern list (logs only) → L → Em → **En protectai v2 (on disk) = X1** → LM (lost: .437/.503 catch, E:90) → TH Jev (incumbent) → G | X1: catch lower bound ≥ .853 at ≤5/300 false flags (README.md:47) | X1's falsifier. PPV at 1% prevalence is .35 (E:90), so any arm needs a prevalence projection (D4, P:190) before enforcement |
| 15 | **`watch`**: should a stopped turn continue; is a pane idle/stuck; page a human; keep a background job | DP-46 smart stop; DP-60 pane state; DP-61 page pane 1; DP-65 background job | 8,009 + 4,248 + 60 + 901 = 13,218 | 0 organic. Smart-stop decisions are not persisted (S:197) | 0 | Re-asked stops 100/100 not promise-then-stop: constant "stop is fine" = **1.00** (P:63); idle watcher planted 10/10 | omp smart stop (Jev); fleet watcher (STOPPED since 2026-10-04, RM:46) | Labels first (N6). Then R end-of-turn promise regex ("I will / next I'll") and tmux activity timestamp → L → Em → TH Jev → G | No bar until N6 persists decisions and joins outcomes (abort, correction, continuation) | After N6, positives stay <30 in 14 d (nwo1 already saw 0/100). Then smart stop is DROPPED as a classifier and becomes an off switch |
| 16 | **`effort`**: thinking level / model per prompt or session | DP-1 auto-thinking; DP-4 model/profile per session | 7,610 + 3,146 | 0 organic (DP-1, DP-4) | 0 | UNDEFINED organic. On the 94-row offline set the keyword rule beat Jev, 32/94 vs 12/94 (E:94) | omp auto-thinking (Jev), 5 profiles | Labels first (N6). Then R keyword rule (incumbent on the 94 rows) → L → Em → TH Jev → G | Outcome-labelled A/B: auto vs pinned (`jev-5ai4`, B:jev-5ai4@81) on checkable prompts | Auto loses to or ties pinned at higher cost. Laya also failed here (.172, ENCODER-INVENTORY.md:15) |

**Totals:** 16 families covering 41 of the 65 decision points. The other 24 (16 class-d rows, 7 rule-shaped
class-a rows, and DP-62) are in section 4. Ten families carry organic labels (score > 0), six do not.

**Shared prerequisite (INFERENCE from S:3-5, E:10-11):** every count above comes from scratch scripts under
`var/agent-tmp/` (`census.py`, `pass2-5.py`, `gen.py`). ECOSYSTEM's own citation rule says they must be committed
before anything public cites them. That is bead N0, and every family bead depends on it.

**Label caveats that change the bars:**
- `result`: an `artifact://` read-back measures the cost of a **spill**, which is one extra read, recoverable. It
  does not measure the harm of a **drop/shake**, which needs a "same command re-run within K calls" label (to be
  added in N0).
- `rank`: the touched-hit label exists only for the hits shown. A BM25-top-1 counterfactual is scoreable only where
  BM25's top-1 is among the logged hits. INFERENCE: score on that subset, and report its size.
- `pin`: 1,385/1,577 counts routine re-reads as need (S:126). The bar subtracts pinned tokens so that pin-all is not
  rewarded for free.

---

## 2. Current families and beads in `jev-b35c`: KEEP / MERGE-INTO / DROP

The ten families come from P:53-64; the beads from `.beads/issues.jsonl`.

| Current item | Verdict | Decision-point evidence |
|---|---|---|
| `route` (Banking77/CLINC, P:58) | **KEEP, re-anchored** on family 4 | ECOSYSTEM row 1 says route has no organic traffic (E:87). That is contradicted by routing-shaped decisions with organic volume: locate tool 21,008 with 1,250 labels (DP-13), prompt stage 17,449 (DP-3), web vs local 3,448 (DP-17) (S:191). Banking77 stays a public benchmark (X6) |
| `rank` (P:55) | **KEEP** (family 2) | 41,002 judge calls, 421 touched-hit labels (DP-28) |
| `verify` (SciFact/FEVER, P:60) | **MERGE-INTO `review`** (verdict-holds); the claim/close evidence check goes to `land` | No decision point is "claim vs evidence" on organic text. The nearest are verdict-holds (E1: rule .618 beats Jev .400) and claim/close (DP-51, 1,364 / 69, already a TTSR regex). `jev verify` stays a primitive verb; X3 decides its local arm |
| `score` (SST-5/STS-B, TTSR, P:64) | **MERGE-INTO `nudge`** | Its only organic consumer is judged TTSR rules: 7,954 / 722 re-fires (DP-11). Score stays a primitive shape (`ask score`) |
| `gate` (P:57) | **KEEP** (family 13) | 39,279 observe + 35,072 harm-rule decisions (DP-19, DP-21). X7 gives the joined deterministic incumbent that README:157 lacked (Jev 47/47 vs rules 7/47) |
| `screen` (P:56) | **KEEP** (family 14) | 19,250 + 585 decisions (DP-25, DP-26); 1,262 planted rows (E:124) |
| `diff` (vendored, P:59) | **MERGE-INTO `land`** (vendored sub-check of the staged set, shadow only) | No decision point of its own; it hosts on commit (DP-54, 4,425). Organic positives 0/39 (E:92). X4: TF-IDF probe AUC .9175 vs Jev .827 / Clef .839 (X4:22-23). The probe replaces the ~2.8 s Clef second verdict (`jev-517o`) once ECE is measured |
| `memory` (P:61) | **KEEP** (family 12) | 39,179 + 1,126 + 720 decisions (DP-35-37); X8 provides labels |
| `watch` (P:63) | **KEEP, blocked on N6** (family 15) | 8,009 smart-stop + 4,248 pane + 60 page + 901 job decisions, 0 outcome labels (DP-46, 60, 61, 65); decisions not persisted (S:197) |
| `effort` (P:62) | **KEEP, blocked on N6; Jev demoted below the keyword rule** (family 16) | 7,610 + 3,146 decisions, 0 outcome labels (DP-1, DP-4). Keyword 32/94 beat Jev 12/94 (E:94) |
| `jev-b35c.5` families integration (B:jev-b35c.5@186) | **KEEP, re-scope** to the 16-family registry in section 1. Its D9 no-build list gains: "block identical bash retry" (S:189) and "Jev on verdict-holds / finding novelty" (E1, E2) | — |
| `jev-b35c.16` cohort A (B:jev-b35c.16@170) | **KEEP, re-scope** to the organically labelled, jev-owned families: `result`, `rank`, `reread`, `route`, `nudge`, `recover`. Each gets an adapter only after its N-bead's bake-off; a family that ends at R ships as a rule adapter | Scores 99,680 / 41,002 / 36,827 / 21,151 / 14,251 / 11,970 (section 1) |
| `jev-b35c.17` cohort B (B:jev-b35c.17@171) | **KEEP, re-scope** to the families resting on planted/blind sets: `memory`, `screen`, `gate`, `review`, plus `watch` and `effort` behind N6. `pin`, `delegate` and `outcome` join once their N-bead shows ≥30 positives (P:77). `land` goes UPHILL, not here | Organic labels 0 (DP-19, 21, 25, 26, 35-37, 46, 50, 53, 60, 61, 1, 4) |
| `jev-b35c.11` `ask` bundle (B:jev-b35c.11@165) | **KEEP** (a primitive, not a family) | No decision point of its own. INFERENCE: `nudge` scores several injectors over one turn state, which is the bundle shape |
| `jev-b35c.12` chain integration (B:jev-b35c.12@166) | **DROP** (move to deferred: no traffic) | None of the 65 decision points is a propose→check→act pipeline or a long-document search (S:49-115) |
| `jev-b35c.26` chain runner (B:jev-b35c.26@181) | **DROP** (deferred) | Same as `.12` |
| `jev-b35c.27` rank long-document (B:jev-b35c.27@182) | **DROP** (deferred) | `find` ranking (DP-28) is single-shot over hits. No long-document decision appears in the logs |
| `jev-b35c.13` `extract` (B:jev-b35c.13@167) | **DROP** (deferred) | No extraction decision point in S:49-115. "A family without a host tool" is outside the mission (RM:53) |

**Counts:** ten families: KEEP 7, MERGE 3, DROP 0. Eight beads: KEEP 4 (`.5`, `.16`, `.17`, `.11`), DROP 4 (`.12`,
`.13`, `.26`, `.27`). Combined: **KEEP 11 · MERGE 3 · DROP 4.**

Graph consequences for the conductor:
- `jev-q3q8` depends on `.12`, `.13`, `.26` and `.27` (B:jev-q3q8@450). Remove those edges when they are deferred.
- `jev-uzq1` ("ten families live or refuted", B:jev-uzq1@519) and P:46-64 must be restated for the 16-family set.
- `.16`'s research correction (gate receipt conflict, B:jev-b35c.16@170) moves to `.17` with `gate`.

---

## 3. New beads

Each bead below follows `scripts/bead-lint.py` (WHAT, WHY, a runnable command or `creates:`, a planted negative,
a checkable source). Every bar is a **proposal** and must be committed in the bead before its first call (RM:26).
INFERENCE: commands name only paths that the bead itself declares in `creates:`.

### N0. Commit the fleet decision miner and per-family label emitters
- **WHAT:** move `census.py`, `pass2-5.py`, `declogs.py` and `gen.py` from `var/agent-tmp/dogfood/fleet-schema/`
  into `work/fleet-schema/`, with synthetic-session fixtures. Add `--labels <family>`, which emits outcome rows
  (session id, call index, hashes, label; no raw text) to the local bank, following `jev-vvkr`'s
  units-local/metadata-committed pattern (B:jev-vvkr@544). Add the "same command re-run within K calls" drop label
  for `result`, and the residual-harm label for `reread`.
- **WHY:** all 65 rows and all ten organic label sets (4,329 / 421 / 20,388 / 1,250 / 1,533 / 6,644 / 652 / 31 /
  1,385 / 39, section 1) exist only in gitignored scratch (E:10-11).
- **Acceptance:** creates: work/fleet-schema/miner.py, work/fleet-schema/test_miner.py,
  work/fleet-schema/fixtures/sessions.jsonl, work/fleet-schema/task.json. Running
  `python3 -m unittest work/fleet-schema/test_miner.py -v` passes. Planted negatives: (a) an `artifact://` read in
  a *different* session must not count as a read-back; (b) a repeat read after `bash sed -i` on that path must not
  count as redundant; (c) a fixture with a decision but no outcome row is emitted NOT_COUNTED, never as label 0.
- **Pillar:** `pillar:honest`. **Edges:** blocks N1–N10. Relates to `jev-ca37` (B:jev-ca37@200, the census
  traffic feed for `ready` row 2).

### N1. `result`: spill/drop bake-off on read-back labels
- **WHAT:** run arms R → L → Em → TH on held sessions, labelled by `artifact://` read-back (spill) and the N0
  re-run label (drop).
- **WHY:** this is the top-scoring decision: 99,680 decisions, 4,329 read-backs (DP-29). `jev-dau5` uses a
  3-probe label on 100 held rows and is EXPLORED (S:187; B:jev-dau5@221).
- **Acceptance:** creates: work/result-family/PREREG.md, work/result-family/bakeoff.py,
  work/result-family/RECEIPT.md. `nice -n 10 python3 work/result-family/bakeoff.py --task work/fleet-schema/task.json --json`
  prints, per arm: tokens saved, read-backs, re-runs, and the .767 constant. Planted negatives: a spilled result
  whose id is read back counts as a miss for an arm that dropped it; a coin-flip arm must fail the bar.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Relates to `jev-dau5`, `jev-4se3`, `jev-vvkr`. Blocks
  `jev-b35c.16`.

### N2. `reread`: hash+range dedup rule and its residual-harm label
- **WHAT:** turn the read-dedup shadow into a content-hash + line-range + compaction-boundary rule, then measure
  the residual harm on shadow rows. No model arm unless residual harm exceeds the bar.
- **WHY:** 36,827 repeat reads, 20,388 redundant (DP-30). Zero open beads match "dedup" (S:188). The current label
  is the baseline rule itself (section 1 tautology warning).
- **Acceptance:** creates: work/reread/rule.py, work/reread/test_rule.py, work/reread/RECEIPT.md.
  `python3 -m unittest work/reread/test_rule.py -v` passes. Planted negatives: a read of a different,
  non-overlapping line window must not be skipped; a read after compaction dropped the file must not be skipped;
  a file changed by `bash` without being named (hash differs) must not be skipped.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Blocks `jev-b35c.16` (`reread` adapter = rule).

### N3. `route`/locate: tool-choice bake-off on locate-episode cost
- **WHAT:** define a locate episode (first locate call → first read/edit of the file finally edited) and run arms
  R → L → Em → En → TH on tokens and calls per episode.
- **WHY:** 21,008 locate decisions, 1,250 find→read labels (DP-13). find share is 12.7% against `jev-kvcc`'s ≥40%
  bar (S:190), and kvcc is deferred (B:jev-kvcc@364).
- **Acceptance:** creates: work/route-locate/PREREG.md, work/route-locate/episodes.py,
  work/route-locate/RECEIPT.md. `nice -n 10 python3 work/route-locate/episodes.py --task work/fleet-schema/task.json --json`
  prints episode counts and per-arm tokens per located file, next to the grep-always constant (.776). Planted
  negatives: an exact-identifier query must be routed to grep by R, and an arm that sends everything to find must
  lose on identifier episodes.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Supersedes `jev-kvcc` (re-open it or close it into this
  bead). X6 informs the En arm. Blocks `jev-b35c.16`.

### N4. `recover`: bash/edit error-recovery rule vs the constant
- **WHAT:** an error-class rule for bash (retry vs change) and the exact error-class rule for edit (stale_tag →
  re-read), scored against next-call success. A model arm runs only if R leaves a margin over .853/.854.
- **WHY:** 8,948 bash and 3,022 edit errors, with 5,144 + 1,500 outcomes (DP-31, DP-32). Zero open beads
  (S:189). Blocking identical retries would be wrong 76% of the time (245/321 succeeded).
- **Acceptance:** creates: work/recover/rule.py, work/recover/test_rule.py, work/recover/RECEIPT.md.
  `python3 -m unittest work/recover/test_rule.py -v` passes. `python3 work/recover/rule.py --task work/fleet-schema/task.json --json`
  prints, per error class, the next-call success under the rule and under the constant. Planted negatives: an
  identical retry after a timeout/network class is not flagged; an identical retry after `command not found` is
  flagged.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Blocks `jev-b35c.16`. Note: "will this bash fail" (DP-24)
  stays out of scope as a forecast (section 4).

### N5. `land`: commit/close failure classes, measured and sent UPHILL (omp-kit may own)
- **WHAT:** classify the 436 failed commits, 23 hook rejects and 117 close failures by stderr class. Report which
  classes code can check before the call. Send the result to omp-kit (%54). Keep the vendored sub-check (X4
  probe) as a shadow only.
- **WHY:** 4,425 commits / 466 labels and 677 closes / 117 labels (DP-54, DP-56), with no jev bead (S:193). Git
  writers are omp-kit ground (RM:54; OK:…rz5.86 LAND1, OK:…rz5.95 MP3, OK:…rz5.107 ADOPT1).
- **Acceptance:** creates: work/land/classes.py, work/land/test_classes.py, work/land/UPHILL.md.
  `python3 -m unittest work/land/test_classes.py -v` passes. Planted negative: a `nothing to commit` failure must
  be classed code-checkable, never model-addressable. `work/land/UPHILL.md` cites the omp-kit bead it was
  filed against.
- **Pillar:** `pillar:honest`. **Edges:** needs N0 and X4. Relates to `jev-517o` (B:jev-517o@75). No
  `jev-b35c` child unless omp-kit asks for a classifier.

### N6. Outcome logging for smart stop, auto-thinking and aborts
- **WHAT:** persist each smart-stop and auto-thinking decision (score, level, turn id). Join it to outcomes in the
  next turn: abort (DP-48), correction regex (DP-5), continuation, `thinking_level_change` override. Where omp
  must persist natively, file it UPHILL.
- **WHY:** smart stop made 8,009 judge calls with no decision persisted. Auto-thinking made 7,610 with no outcome.
  The 5,212 aborts and 7,536 post-answer turns go unused (S:197; DP-1, DP-46).
- **Acceptance:** creates: work/outcome-log/join.py, work/outcome-log/test_join.py.
  `python3 -m unittest work/outcome-log/test_join.py -v` passes.
  `python3 work/outcome-log/join.py --days 7 --json` prints per surface: decisions, persisted share, and outcome
  counts. Planted negative: a judge call with no persisted decision row is NOT_COUNTED, never "did not continue".
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Blocks the `watch` and `effort` adapters (`.17`),
  `jev-5ai4`, `jev-2fz6` and `jev-mvvh` (B:jev-mvvh@391; the value ledger needs outcomes). Relates to `jev-nwo1`.

### N7. `pin`: compaction file pinning vs pin-all
- **WHAT:** score pin-all-readFiles, pin-edited-last-N and path-in-summary against re-read tokens avoided minus
  pinned tokens. If an arm wins, propose it UPHILL (compaction is omp native, DP-39).
- **WHY:** 1,577 compactions with readFiles, 1,385 followed by a re-read (DP-41). Only `jev-g2uv` exists, and it
  covers turns, not files (S:196).
- **Acceptance:** creates: work/pin/score.py, work/pin/test_score.py, work/pin/RECEIPT.md.
  `python3 -m unittest work/pin/test_score.py -v` passes. Planted negative: an arm that pins every file with no
  budget must be charged its pinned tokens and must not win by construction.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Distinct from `jev-g2uv` (B:jev-g2uv@271).

### N8. `delegate`: build the outcome label before any classifier
- **WHAT:** join each `task` spawn (agent type, model, prompt size) to its outcome: yield error, parent redoes the
  same files within K calls, reviewer reject, revert. Report positives per decision. Score the R baselines
  ("always task", parent model, accept when data present).
- **WHY:** 1,051 spawned agents and 1,691 yields carry only 39 outcome labels (DP-43, DP-45). L09 is unplanned
  apart from `jev-t5jk` (S:192).
- **Acceptance:** creates: work/delegate/join.py, work/delegate/test_join.py.
  `python3 -m unittest work/delegate/test_join.py -v` passes. `python3 work/delegate/join.py --days 14 --json`
  prints positives per decision and the constants .981/.993. Planted negative: a subagent whose files the parent
  never touches again must not be labelled "redone".
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Gates `jev-t5jk` (B:jev-t5jk@497). If positives stay below
  30, the family is DROPPED.

### N9. `nudge`: per-injector actionability receipt and rule baselines
- **WHAT:** for TTSR judged rules, the skill hint, the todo nudge and the LSP late diagnostic, report the
  followed/ignored constant, then run R → L → Em → En NLI → TH (Jev judge recorded) per injector.
- **WHY:** 22,479 injections with 1,533 follow/act labels (DP-7, 8, 11, 33). omp-native injections have no value
  receipt, and the TTSR compliance label is unused (S:194-195).
- **Acceptance:** creates: work/nudge/score.py, work/nudge/test_score.py, work/nudge/RECEIPT.md.
  `python3 -m unittest work/nudge/test_score.py -v` passes. Planted negative: a nudge followed by a `todo` call
  4 calls later (outside the 3-call window) is not counted as followed; a suppress-all arm must fail the recall
  floor.
- **Pillar:** `pillar:measured`. **Edges:** needs N0. Relates to `jev-pn7b` (retired rules firing), `jev-35sg`
  (skill hint while OFF) and `jev-wbel` (veto). Blocks `jev-b35c.16`.

### N10. `review`: rules as incumbent; ≥100 blind rows before any model arm
- **WHAT:** commit the E1/E2 receipts and rows from scratch into `work/`. Label ≥100 blind finding rows. Run
  L/Em near-duplicate arms against the same-bead+class rule, and the X3 encoders against the verdict-holds keyword
  rule.
- **WHY:** Jev lost both (E2: 49/85 vs rule 77/85; E1: .400 vs .618). 195 reviewer spawns (DP-53).
- **Acceptance:** creates: work/review/score.py, work/review/test_score.py.
  `python3 work/review/score.py --json` reproduces E2 77/85 and E1 .618/κ .288 from the committed rows. Planted
  negative: a coin-flip arm must score below the rule.
- **Pillar:** `pillar:honest`. **Edges:** needs X3 for the En arm. Blocks the `review` adapter (`.17`).

### X1–X8 as dogfood-first beads

"Dogfood-first" means: run it as `var/agent-tmp/dogfood/<x>/` with its PREREG committed before the first call,
the way `x4`/`x7` were run. Then copy the RECEIPT and rows into `work/<x>/` before any README cite (E:10-11). Bars
and falsifiers are as in README.md:45-54.

| Bead | WHAT | WHY (counts) | Acceptance (creates / planted negative) | Pillar | Edges |
|---|---|---|---|---|---|
| **X1** injection encoders | protectai v2 (on disk) vs Jev on 300 clean + 300 markerless + 662 public rows | `screen`: 19,250 + 585 decisions (DP-25, DP-26); Jev 268/300, 5/300 (R:101) | creates: work/x1-injection-encoders/PREREG.md, work/x1-injection-encoders/RECEIPT.md. Cut fixed on clean rows only. Planted negative: a benign tool result containing trigger words ("ignore", "system") stays unflagged at that cut | `pillar:local-first` | blocks `.17` `screen`; relates to `jev-j0er` |
| **X2** Clef-Flash on four suites | equal Platt on both arms: SciFact 400, SST-5 500, gate 396, injection 600 | Decides `--backend auto` for 4 families at once (E:125; RM:27) | creates: work/x2-clef-suites/PREREG.md, work/x2-clef-suites/RECEIPT.md. Planted negative: a Clef arm given Jev's Platt map instead of its own is refused by the scorer | `pillar:local-first` | blocks `jev-b35c.4`, `jev-hnt5` |
| **X3** MiniCheck / NLI vs Jev | MiniCheck-RoBERTa-Large and nli-deberta-v3-base (both on disk) on SciFact/FEVER; Climate-FEVER decides | `review` verdict-holds (E1 55 rows) and the `verify` primitive | creates: work/x3-factcheck/PREREG.md, work/x3-factcheck/RECEIPT.md. Planted negative: a numeric claim is refused, not scored (numeric claims 0/31, E:109) | `pillar:local-first` | blocks N10 |
| **X4** vendored probe (**run: BEATS-BAR**, X4:3) | close out: measure ECE (the vendor contract also requires ECE ≤ Jev .1846, X4:24) and run X4b (Qwen3 embedding, PREREG exists at `var/agent-tmp/dogfood/x4b-vendored-embed/PREREG.md`) | AUC .9175 vs .827/.839, DeLong p=.0004/.0066 (X4:22-23); 0/39 organic | creates: work/x4-vendored-probe/RECEIPT.md, work/x4-vendored-probe/run.py. Planted negative: a probe refit on held rows is refused (dev-only fit, X4:18) | `pillar:measured` | blocks N5 vendored sub-check, `jev-517o` |
| **X5** local Score replication | tev1/nimble/Kev-4B vs Jev on a fresh disjoint SST-5 500 | the `nudge` judged-rule shape: 7,954 decisions (DP-11); tev1's lead was EXPLORED (E:128) | creates: work/x5-score-rep/PREREG.md, work/x5-score-rep/RECEIPT.md. Planted negative: a row overlapping the first 500 makes the run refuse | `pillar:local-first` | relates to N9 |
| **X6** SetFit / encoder on Banking77 | 10-shot and full-train encoder vs Clef .962 on the 600 held rows | `route` arm En; the organic transfer is to N3, not Banking77 | creates: work/x6-intent-encoder/PREREG.md, work/x6-intent-encoder/RECEIPT.md. Planted negative: a test-split row in train makes the run refuse (only the test split is on disk, ENCODER-INVENTORY.md:90) | `pillar:local-first` | informs N3 |
| **X7** gate rules (**run: LOSES for rules**, X7:3) | close out: commit the receipt, then fix an NP cut for Jev from the 349 negatives | Jev 47/47 at 1.40% weighted FA vs rules 7/47 at 14.81% (X7:24-27); first joined deterministic incumbent (README:157) | creates: work/x7-gate-rules/RECEIPT.md, work/x7-gate-rules/np_cut.py. Planted negative: an NP cut computed with harm rows included is refused | `pillar:honest` | resolves `.16`'s gate research correction; blocks `.17` `gate` |
| **X8** memory relevant-drop | active sampling near the cut to reach ≥59 relevant items, then an NP cut | `memory`: 39,179 decisions, 6/100 relevant (DP-35, E:131) | creates: work/x8-memory-drop/PREREG.md, work/x8-memory-drop/RECEIPT.md. Planted negative: a relevant memory dropped is counted against the bound even when it timed out (deadline-keep, `jev-s0ve`) | `pillar:measured` | blocks `jev-08hr` enforcement decision, `jev-9cqw` |

**New beads proposed:** N0–N10 (11) + X1–X8 (8) = **19**.

---

## 4. Decisions that are NOT classifiable: they stay with code or humans

| Owner | Decision points | Why |
|---|---|---|
| **Code, exact** (structural) | DP-2 prompt source (prefix); DP-12 AGENTS.md reload (mtime); DP-15 poll vs wait (`\bsleep\s+\d`); DP-23 will this edit apply (tag check; 3,022 errors are the tool working); DP-39 when to compact (token threshold); DP-64 file-reservation conflict (glob overlap); DP-55 push (git decides; 65 rejects) | S:177. Code is exact, free and stable (E:109) |
| **Code, already deciding as rules** (class a, rule-shaped) | DP-18 dcg block (87,608); DP-20 guard rule (146,873); DP-22 rch lane (86,227); DP-14 shell vs specialized tool (TTSR regex); DP-34 loop redirect; DP-47 goal continuation; DP-49 review applicability (98.1% agreement, zero calls, E:66) | Blocking stays deterministic; Jev is observe-only (E:110) |
| **Code, bead authoring** | bundled acceptance box (regex F1 .588 vs Jev .176, E:31-32, E:98); dead paths; near-duplicate prompts | Structural (E:109); `scripts/bead-lint.py` |
| **Forecast: the label is not in the tokens** | DP-24 will this bash command fail (117,642 / 8,932); DP-52 which tests / will this diff break a test (7,272 / 1,214; diff-risk AUC .377) | 0 wins / 12 on forecasting (E:40, E:107). Use a per-command failure-rate table, not a classifier |
| **State outside the text** | DP-63 incoming peer message act/ignore (.704 vs .75 bar); DP-57 duplicate bead at create (abstain .678 beats Jev .370) | E:108, S:181 |
| **Generation** | DP-40 compaction summary text (keep 0/32); DP-38 what to retain | E:111 |
| **Humans** | DP-48 user interrupt/abort (5,385: a label *source*, not a decision); DP-58 undo (178); DP-59 deploy (71); push approval; finding severity; mission scope and funding (R:56) | E:110, S:179 |
| **Another owner (omp-kit)** | DP-62 dispatch: which bead to which agent (4,667, 0 labels; omp-kit owns idle dispatch, S:112; OK:…rz5.102, OK:…rz5.100); git writers inside `land` (RM:54) | ROADMAP neighbours (RM:58-63) |
| **Likely to end as code even though listed as a family** | `reread` (hash + range rule; label is tautological); edit half of `recover` (exact error class); `land` (failure classes) | Section 1 falsifiers. If the rule wins, the family ships as a rule adapter or goes UPHILL |

Accounting: this section holds 24 decision points: all 16 class-d rows (S:47), 7 class-a rows that are rules
(DP-14, 18, 20, 22, 34, 47, 49), and DP-62. With the 41 points in section 1, every one of the 65 rows is
assigned exactly once.

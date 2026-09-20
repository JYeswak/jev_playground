# Wave learning ledger — one line per section, 24 sections × P1–P12

Named by the wave plan (`wave-plan-sections-passes-20260919.md`) as the append target. The 48h
analysis pass is a different document: `commit-learnings-20260920.md` (`bf12406`).

Rules: one line per section, appended after its passes run. `PASS` requires the section's
ACCEPTANCE live command to exit 0 with a quoted row. `promoted=0` until then, and a `FAIL` line
must carry the next command rather than a plan to write one.

Format: `SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`

---

## Wave A — Dig spine

SECTION 2 cass dig adoption — FAIL — `cass` is installed and has **0 references** in this repo
(grep over `work/ foundation/ scripts/`), so the dig spine has never been used first; the miss is
recorded in `commit-learnings-20260920.md` — NO-CLAIM: not yet run against a real question, so
whether it would have caught the ten wrong-selector failures is unproven, and P8 is unsatisfied
for every section shipped before this one.

SECTION 3 fh suggest/rejected dig — PASS — `fh suggest --json "LLM judge versus regex on shell
command danger"` exits 0, `"success":true,"code":"PASS"`, `indexed_rows 306`, 5 results; rank 1 is
`TECH:destructive_command_guard:fe161acb54ac:188258` at `destructive_command_guard/src/cli.rs:13400-13403`,
headline `const CRUSH_SHELL_MATCHER: &str = "^bash$"` — i.e. the dig returned **dcg's own matcher
source**, directly relevant to the control-tampering seat (section 14) — NO-CLAIM: one query, one
corpus (306 rows); relevance judged by me reading the top row, not measured; `fh rejected` not run.

SECTION 3b MY OWN DEFECT, same section — my first reader printed five `None` rows because I asked
for `title`/`snippet` when `fh` returns `headline`/`evidence`/`mirror_path`. **Eleventh
wrong-selector failure this session**, and precisely the class P4 (`selector ≡ claim`) exists to
catch. Had I stopped at the first output I would have recorded "fh returns empty results" — a
false negative about a working tool, which is the same shape as the `dcg_allow` harvest that
returned an empty verdict histogram. The rule that keeps being relearned: **print the keys before
claiming absence.**

SECTION 4 bv/br robot triage — PASS — `bv --robot-triage` exits 0 on first use, `issue_count 50`,
`phase2_ready true`, `history_status ok`, PageRank computed 0.021ms / Betweenness computed
(approximate) 0.079ms, six algorithms skipped; `quick_ref` = open 11 · actionable 23 · blocked 6 ·
in_progress 6; top picks `jev-fzw 0.275` (ground truth that survives real diffs), `jev-m7r 0.254`
(harm-rule recall beyond n=2), `jev-gou 0.254` (port measure scripts to measure-kit) — NO-CLAIM:
ranking quality unjudged; I applied P4 (printed `quick_ref` and `top_picks[0]` keys before reading
values) but have not verified the scores mean what the names suggest, and six of nine algorithms
were skipped so this is PageRank+Betweenness only. PREVALENCE: 23 of 50 issues actionable (46%),
which is the base rate any "bv found work for us" claim must beat.

SECTION 4b THE ACTUAL PRODUCT OF THIS SECTION — bv's top pick `jev-fzw` is the bead I have been
stepping over all session: "ground truth that survives real diffs". Every measurement failure
tonight (commit judge DEGENERATE/WEAK/WEAK, six hand-built corpora that did not transfer) is that
bead unclosed. A graph-aware tool with zero prior use pointed at it in 0.13s, while I picked beads
by eyeballing `br ready`. That is the miss, measured, not asserted.

SECTION 5 jsm/ms before invent — PASS, and it caught a live duplication — `jsm search eval` exits
0, `Found 10 matching skills`, including **`evaluation-framework` (v1, Joshua Nowak, ID
e292b255-1376-48d5-adf9-f5313d85c40b)** whose description covers "create evaluation rubric",
"model grading", "eval suite", "regression testing AI", "human evaluation protocol",
"inter-rater reliability" — i.e. substantially the brief of `jev-vbh.3` (jev-eval-honesty), which
pane 3 is queued to author from scratch through 8–10 loop passes. `jsm search judge` returns
`persona-clone`, which already implements "scored against a written charter by a SEPARATE judge
model" — the separate-judge pattern sections 6 and 10 were going to invent — NO-CLAIM: I read
descriptions, not skill bodies; overlap is asserted from the trigger lists, and neither skill has
been installed or diffed against our bead. The next command is
`jsm install e292b255-1376-48d5-adf9-f5313d85c40b && jsm list` then a real diff against
`jev-vbh.3`'s WHAT/WHY before any loop pass runs. PREVALENCE: 10 of N indexed skills matched
"eval"; N unknown, so match rate is UNKNOWN.

SECTION 5b WHY THIS SECTION EXISTS, demonstrated — the arsenal audit in
`commit-learnings-20260920.md` listed `jsm` as owned-with-zero-refs. One search, five seconds, and
it found that a queued 8–10-pass authoring job may be re-deriving a skill we already own. That is
the entire thesis of "search before invent", and it was a miss until this section ran.

## Wave C add-on, registered (Joshua, 2026-09-20)

Cursor agents are deep-mining skillranker PROCESS to mirror into omp/Jev; two-plus agents on
`jev_playground`; direct `Dicklesworthstone/skillranker` blocked pending GitHub access. When those
PRs land, treat as a Wave C add-on with three named deliverables: **skill-router abstention**,
**eval gate >=0.90**, **JSONL export**. Overlaps section 12 (usage-router-active) and section 15
(score-register export sweep) directly — the register already emits JSONL with a replay that makes
zero API calls (`8e2d533`), so the export half may be satisfied on arrival rather than built.

NO-CLAIM: no skillranker PR has landed or been read; this is a registered intent, not evidence.
Our clone is 217 commits behind `origin/main ba5da08` (bead `jev-0bp`, closed by pane 3 as
Linux-only with rank quality unrun).

SECTION wave-c skillranker PROCESS archaeology — PASS (source-read, not product) —
public HEAD `6a74cca` receipt
`docs/demos/upstream-repro/skillranker-process-archaeology-20260919.md`: rank arc
wired; hook/feedback/eval CLI still planned; `src/` still does not read
`synthetic_cases.v1.jsonl` (`frozen_contract_not_evidence`); false abstention
costs 1 — NO-CLAIM: no `sr` run, no keyed rank, **promoted=0**. The three named
deliverables (abstention / 0.90 gate / JSONL export) remain process patterns,
not a shipped omp surface.

## Wave E section 22 (planted-negative gates) — done early, because Joshua's adopt #1 required it

SECTION 22 planted-negative gates + ADOPT #1 promotion contract — PASS — `foundation/gates.d/85-promotion-contract.sh`
(`bd641d1`) is wired via the `gates.d/[0-9]*` glob, so running code branches on it. Three planted
arms: `--- arm 1: PROMOTED row naming no gates (must fire RED) / fired RED as required`,
`--- arm 2: PROMOTED row naming all four gates but a missing receipt / fired RED as required`,
`--- arm 3: the real STATUS.tsv (promoted=0) must pass / passed as required`; normal run
`OK promotion-contract: 26 row(s) scanned, 0 PROMOTED, 0 violations`. Full suite both modes:
`./foundation/gates.sh` rc=0 with 13 PASS, `--selftest` rc=0, exit codes taken unpiped. Shape
adopted from franken_engine's promotion_gate_runner via `fh suggest "promotion gate"` →
`franken_engine/docs/IDEA_WIZARD_XIII_CLAIM_PROMOTION_GATE.md:27-46`; **no engine crate linked** —
NO-CLAIM: promoted=0 unchanged, the gate has never seen a real PROMOTED row, and gate names are
matched as substrings anywhere in the row, so prose mentioning "adversarial" would satisfy it;
tighten on first real promotion, not before. PREVALENCE: 0 of 26 rows PROMOTED (0%), which is the
base rate this gate currently operates against.

SECTION 22b THE NEW STAGE BROKE TWO OTHERS ON ARRIVAL, AND THAT IS THE SYSTEM WORKING — adding a
13th stage turned stage 97 RED ("README says 'Twelve stages' but foundation/gates.d holds 13") and
stage 80 RED through 97's selftest. Count re-derived from the repository
(`ls foundation/gates.d/[0-9]*-*.sh | wc -l` = 13), not adjusted by arithmetic — which is what 97's
own message warns against: "that is how the last four went stale."

SECTION 22c CONDUCTOR DEFECT, the documented hazard, hit by me — the stage passed both modes, then
`git add` failed with "pathspec did not match any files". The file was gone, my README edit
reverted, gates.d back to 12. Peer merges (#23 skillranker eval-contract, `0840e3d`, `73a51b6`)
landed while my stage was still UNTRACKED, and swept it. One tick earlier I had flagged three
untracked files in this tree as invisible to every gate. The rule is in the packet contract and I
still lost work to it: **stage the file in the same breath as creating it.** Recovered, re-verified
green, committed.

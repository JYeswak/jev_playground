# WAVE D — sections 16–20, P1–P12 each

Wave D is the one where claims meet the public. Sections 16–19 measure; **20 is the only section
tonight whose output a stranger reads directly**, so it outranks the rest if you can only do one.

## Claim the section before you work it

Two panes are on this queue and a third agent is on §21. Claim by moving the bead `in_progress`
under your own actor name, or by committing a stub receipt naming the section. **Check the tree
before assuming a section is free** — that is how §7's collision was avoided: the other agent read
`work/jev-eval-honesty/` and concluded pane 3 owned it, rather than asking and waiting.

## Sections

**16 omp-jev-observer live dogfood** — working-profile co-presence + id-join, beyond n=1 lab.
Note `omp-jev-observer` has **no `omp.extensions` entry** in its `package.json` (verified), so it
is not installable as shipped, and it is wired to the score register in
`src/classify-systemone.mjs`, not `src/index.ts`. Both facts are load-bearing for this section.

**17 harm-rule organic traffic** — observe-only on real work; organic precision measured.
`omp-harm-rule` has **no `package.json` at all** and contains **no model call** — that is why it
went 12/12 against Jev's 11/12 at zero cost. Do not add a model to it. Measure what it does.

**18 jev-compact reality** — it is a measurement instrument. **Never claim prune until a live
reduce is observed.** `compaction/` already exists in this repo; read what it measures before
building anything beside it.

**19 taste-loop 11 packages** — measure under CONTRACT; stay unpromoted until bars are met.
`foundation/gates.d/85-promotion-contract.sh` now defines what promotion requires (four gates:
equivalence, capability, performance, adversarial). Promotion without those four is a RED.

**20 public INTEGRATIONS refresh** — `docs/INTEGRATIONS.md`. Claim levels only. No soft
"working-dogfood" language. This is the section a non-lane reader consumes.

Facts it must now reflect, all verified tonight:
- **19 of 21** `omp-jev-*` packages export Jev-derived scores; 2 NOT-APPLICABLE
  (`preaction`, `harm-rule` — neither makes a model call). Supersedes the "1 of 21" in
  `commit-learnings-20260920.md`.
- **promoted = 0.** Nothing in this repo is promoted.
- The tool-call judge family is **ABANDONED** — three wordings, all near-constant (53.75% →
  48.25%), documented in `commit-learnings-20260919.md` §14–14e.
- `jevcache` is **removed and disqualified** (`8fe44b2`, `f717ba3`).
- The score register replays with **`api calls made : 0`** from a pinned fixture,
  `sha256 c4e0e7c4…`, 55 rows.

## Constraints, all paid for tonight

- **Commit the moment you create.** Staging is NOT protection — the tree is branch-switching
  between peer branches and a checkout discards staged-but-uncommitted files. Two files were lost
  this way, one of them after `git add`.
- **Quote live numbers with their inputs pinned**, or label them live-and-monotonic. Four
  reproducibility defects tonight, all the same shape; three were caught only because someone
  re-ran something they had already reported.
- **Grep the directory, not the file.** A per-package probe assuming one canonical entry file is
  the same wrong-selector failure as scanning one row shape — it cost the conductor a wrong census
  an hour ago.
- **Read the near-threshold count before prevalence.** Half the verdicts in §14e were made by our
  0.50 threshold, not by Jev.
- Test file + `TESTS.md` entry in the same commit. No Codex.

One ledger line per section into `docs/demos/upstream-repro/commit-learnings-20260919.md`:
`SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`. A FAIL line carries the
next command. FAIL and REFUSE are real outcomes; a fabricated PASS is not.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between them.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-WAVED-S<n>-<PASS|FAIL>: <receipt path> <sha>. NEXT <section>. NO-CLAIM <limit>."`

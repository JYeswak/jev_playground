# WAVE A queue — sections 1, 4, 5 (P1–P12 on each)

Plan of record: `docs/demos/upstream-repro/wave-plan-sections-passes-20260919.md`. Read it; the
12 passes are defined there and I am not restating them. Ledger to append one line per section:
`docs/demos/upstream-repro/commit-learnings-20260919.md` (exists; sections 2 and 3 are already
appended — read them first, they contain a trap you will hit).

Sections 2 and 3 are done by pane 1:
- **2 cass** — FAIL, blocked: `cass search` returns `cass is already repairing the search index in
  /Volumes/ZestData/cass-data` on every attempt (2 tries, 30s each). The DB is real —
  `cass stats` reports 59,807 conversations / 5,181,931 messages. **Next command when it settles:**
  `cass search "requireKey readRow selector" --limit 5`. Do not re-run it in a loop; check
  `cass stats` first.
- **3 fh** — PASS, with a defect of mine recorded: `fh` returns `headline`/`evidence`/`mirror_path`,
  NOT `title`/`snippet`. My first reader printed five empty rows and nearly recorded "fh returns
  nothing". **Print the keys before claiming absence** — that is P4 and it is the eleventh
  wrong-selector failure this session.

## Your three sections, in order

### Section 1 — dont-give-up Pass 6
Paste A–L into the house skill (cass / fh / arsenal / dcg / ubs / jsm / requireKey / gates
selftest). Note #16 and #17 are **already merged to main**, so check what Pass 6 still owes before
writing anything — `jev-vbh.5` was rescoped to "Pass 6 only" for this reason.

### Section 4 — bv/br robot triage
`bv --robot-triage` before beads; ACCEPTANCE must be a live command, never "make it pass".
`bv` has **0 references in this repo** and is installed — this section is its first use, so
expect surface surprises and apply P4 to its output shape before reporting anything as empty.

### Section 5 — jsm/ms before invent
Search existing omp extensions and skills before scaffolding a sibling. Concrete test for this
section: we have **21** `omp-jev-*` packages, several of which may overlap. If `jsm` surfaces a
duplicate pair, that is the section's product.

## Hard constraints, all measured

- **P7 needs a quoted live row.** Not "it worked" — the actual `ok`/`scores`/`latency`/`error`
  line, or a planted RED that fires.
- **P10 prevalence cell beside every score.** Base rate or the literal word `UNKNOWN`.
- **P11 planted negative.** A suite that cannot fail on known-bad is an empty success.
- Hand-built corpora have failed to transfer **six times**; acceptance runs against real artifacts.
  `node work/toolcall-judge-v3/harvest-allowed.mjs` regenerates 77,767 real commands.
- Verdict words are computed, not chosen: `work/jev-client/measure-kit.mjs`.
- Test file and `TESTS.md` entry in the **same commit**.
- No Codex (out of tokens). Do not invent STOP-LIVE.

Append ONE line per section to the ledger, in the stated format:
`SECTION n NAME — PASS|FAIL — <live evidence, quoted> — NO-CLAIM <limit>`

A `FAIL` line must carry the **next command**, not a plan to write one. `FAIL` is a real and
acceptable outcome; a fabricated `PASS` is not.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-WAVEA-S<n>-<PASS|FAIL>: <receipt path> <sha>. NEXT <section>. NO-CLAIM <limit>."`

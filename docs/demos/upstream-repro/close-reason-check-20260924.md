# Do bead close reasons say what their cited evidence says? jev_claim_check on 35 closes (bead `jev-10t`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** A close reason can cite a receipt and still misstate it. For every bead closed on
2026-09-23 or 2026-09-24, does the evidence the reason cites support the reason, as judged by
`jev_claim_check` (the tool from bead `jev-sp5`, cuts 0.8 / 0.2, receipt
[`jev-claim-check-20260924.md`](jev-claim-check-20260924.md))? And does the tool notice when one
number in the reason is changed?

**Instrument.** `work/jev-claim-check/check-close.mjs`: `<bead-id>` checks one closed bead live,
`--dry` prints the resolved evidence, `--build` writes the case file, `--run` drives the shipped
tool over it. The resolution and plant rules are in that file's header: claim = the close reason
verbatim; evidence = every git-tracked text file and every resolvable commit the reason names, in
order (a commit contributes its message and the lines its diff added), each part over 3,000
characters cut to 600-character windows around the reason's number tokens, 12,000 characters total.
The plant changes one number: the first result-like token (with `/`, `.` or `%`) that also occurs in
the evidence, else the first token in the evidence, else the first token; its first non-zero digit
d becomes (d+4)%9+1.

**Corpus, frozen.** `work/jev-claim-check/close-cases.jsonl`, built at HEAD `bc94a16`,
2026-09-24T02:57Z: 35 beads closed on those two UTC dates as of the build (the last closed
02:56:42Z), sha256 `dfb00d97efa88d42153ff972e981a704ba633d6b32242b40a2b7bb9f0ec29e55`. 35 real
reasons, 32 planted twins. `jev-pkd` resolves no evidence (it cites paths on remote workers and an
upstream repo), so neither its real reason nor its plant is sent. Three reasons carry no eligible
number and get no plant (`jev-qex`, `jev-qsg`, `jev-v8-kit-drive-m0e.1`). Scored: 34 real, 31
planted, 31 pairs. In 25 of the 32 plants the original number occurs in the evidence; in the other 7
it does not, so the evidence cannot contradict the change directly. Beads closed after the build are
out of scope. The evidence is the working tree and history at build time and is frozen in the case
file; later edits to a cited file do not change it.

**Bar** (`work/jev-claim-check/score-close.py`, 31 plants, 31 pairs).

| # | Metric | Bar | always `supported` | always `unsupported` |
|---|---|---|---:|---:|
| a | planted reasons called `supported` | <= 3 (10%, floor) | 31 | 0 |
| b | catch-rate: planted called `unsupported` | >= 16 (50%, ceil) | 0 | 31 |
| c | AUC of p, real vs planted | >= 0.70 | 0.5 | 0.5 |
| d | paired: p(planted) < p(real) on the same bead | >= 19 of 31 (60%, ceil) | 0 | 0 |

**PASS** = all four. A case with evidence but no verdict counts against the tool. The real
supported-rate is reported with **no bar**: a real close reason is not known to be true. Every real
reason the tool calls `unsupported` is read against its evidence and classed as one of: the reason
misstates its evidence (a finding about that close), the reason's claim lives somewhere the rule did
not resolve (bead comment, `/tmp`, another repo), evidence-window miss, or tool miss. That reading is
descriptive; labels and bar are not changed after the answers.

**Stated before running:** 65 Jev calls (34 real + 31 planted), one Noul each, sequential.

**NO-CLAIM.** Advisory; the tool does not block a close. One run, one Jev version, two days of closes
by this lane's own agents. The plants are mechanical one-digit changes, written by rule before any
call, so the catch-rate measures this kind of error only. Close reasons bundle several claims
(commands run, reviewers, commits); the tool sees one sentence against the resolved evidence, and
a reason that cites a check run in `/tmp` or recorded only in a bead comment can be true and still
unsupported by any committed file.

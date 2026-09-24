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

## Results

Bar committed at `a10c0a3` (02:57:52Z) before any call. Calls ran 02:57:59Z–02:58:09Z, 65/65 answered on the first pass,
0 `not_run`, 0 `refused`. Rows: `work/jev-claim-check/close-rows.jsonl`. Re-score with no key:
`python3 work/jev-claim-check/score-close.py` (exit 1 = FAIL).

| Set | supported | unsure | unsupported |
|---|---:|---:|---:|
| 34 real close reasons | 8 | 26 | **0** |
| 31 planted twins (one number changed) | **4** | 27 | **0** |

| Metric | Tool | always `supported` | always `unsupported` | Bar | Met |
|---|---:|---:|---:|---|---|
| (a) planted called `supported` | 4/31 | 31/31 | 0/31 | <= 3 | **no** |
| (b) catch-rate | **0/31** | 0/31 | 31/31 | >= 16 | **no** |
| (c) AUC real vs planted | 0.598 | 0.5 | 0.5 | >= 0.70 | **no** |
| (d) paired p(planted) < p(real) | 20/31 | 0/31 | 0/31 | >= 19 | yes |

**FAIL** (`[live]`, N=65, `jev-1.13.0`). Three of four criteria missed. The tool called no planted
reason `unsupported`, including the 25 whose original number sits in the evidence (0/25 caught, 3
of them called `supported`). The change moves p down a little on most beads (20 of 31 lower, 3
ties, 8 higher; mean drop 0.055; mean p real 0.559, planted 0.491). That is a weak signal and not
a verdict.

**Four plants were called `supported`.** Each is a wrong number the tool approved:

| Bead | Changed | Original number in evidence | Plant p |
|---|---|---|---:|
| `jev-k9z.1` | `75/219` -> `35/219` | 3 times (`Jev top-1 | 75/219 = 0.3425`) | 0.91 |
| `jev-deep-kit-8q7.7` | `0.6846` -> `0.2846` | once (the AUROC table) | 0.83 |
| `jev-hwa` | `189/189` -> `689/189` (a fraction over 1) | 4 times | 0.83 |
| `jev-deep-kit-8q7.6` | `442/567` -> `942/567` (over 1) | not in the window | 0.87 |

**Real reasons.** None was called `unsupported`, so there is no close reason to read as a
misstatement: **this run found no wrong close reason, and it could not have**, since the same
tool passed four wrong numbers. 8 of 34 were called `supported`. 26 were `unsure` (p 0.23–0.75).
The lowest real p (0.23–0.28: `jev-qbc`, `jev-deep-kit-8q7.3`, `jev-publish-scrub-b94`) are long
reasons at the 12,000-character cap that list commands, re-runs and reviewers, most of which no
committed file states. On this corpus, `unsure` is the tool saying the reason bundles more than the
evidence shows. It is not a finding against any close.

**Post-hoc diagnostic, not preregistered, cannot change the verdict** (8 extra calls,
`work/jev-claim-check/close-atomic-diagnostic.jsonl`). For the four approved plants, only the clause
holding the changed number was sent against the same evidence, with the real clause as a control.
Real clauses: 4/4 `supported` (0.87–0.98). Planted clauses: `jev-k9z.1` 0.63 and `jev-deep-kit-8q7.7`
0.53 dropped to `unsure`; `jev-hwa` 0.89 (`689/189`) and `jev-deep-kit-8q7.6` 0.82 (`942/567`) stayed
`supported`. Short claims help, but the Noul still approves a fraction over 1 that contradicts the
evidence 4 times. This question, at this cut, does not check a number against the evidence.

**Contrast with `jev-sp5`.** On README sentences (one claim each, about 6,000 characters of
evidence), number-changed plants were caught 7/9. Here the claims are multi-claim close reasons and
the evidence is up to 12,000 characters. Both runs are one wording and one version. The difference is
consistent with claim length and evidence size, but this run does not isolate either.

**Negative evidence.** Written as `NEGATIVE_EVIDENCE.md` R83 with its retry condition.
`check-close.mjs` stays as a keyless evidence resolver (`--dry`) and a live advisory check. **No
hook, gate or close-time check is built on it.**

**Spend.** 73 Jev calls: 65 scored (230,484 input / 1,300 output tokens reported by the API, p50
140 ms, p95 227 ms) and 8 diagnostic. Jev's billed units were not read and are not stated.

**Boundary.** One run, one wording, one Jev version, 34 closes by this lane's own agents on two days.
One of them, `jev-sp5`, closes my own previous unit. The plants are mechanical one-digit changes.
The diagnostic is post hoc and n = 4. Awaiting a non-author re-score from the committed rows.

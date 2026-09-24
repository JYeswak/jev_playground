# Does jev-curate's code-quality Score tell correct code from buggy code? QuixBugs, Jev vs Haiku (bead `jev-2wc`)

ObserveHookL3 (background agent of pane 1, Anthropic model), 2026-09-24. Live lane, model pinned
`jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** `jev-curate` (AkashPriyadarshii/jev-curate @ `d1a3a05`) filters training data with a
Jev Score named `code_quality`. Its preset could never have worked: it sends the five level
descriptions as an object, and the API refuses that with a 422 (`jev-curate-w70-20260923.md`,
upstream issue draft `notes/deep/jev-curate-score-criteria-issue-draft.md`). Sent in the shape the
API accepts, does that Score put a correct program above the same program with its bug, more often
than chance, and no worse than Claude Haiku 4.5 asked the identical question? The answer tells the
maintainer whether fixing the shape makes the filter useful.

**Corpus.** QuixBugs (Lin et al., 2017), `jkoppel/QuixBugs` @
`4257f44b0ff1181dedaedee6a447e133219fcebf`, the SHA the jev-curate receipt pinned. The GitHub
tarball for that commit has sha256 `b9f87db002c152e579f9fab860417b122ad9d7e6240f311dbf49082965151b1f`,
and the sampler refuses any other. Pairs: every `*.py` in both `python_programs/` (buggy) and
`correct_python_programs/` (correct), minus `*_test.py`, minus byte-identical pairs (only `node.py`,
a helper). That gives **40 pairs, 80 programs**, all of them. Truth is the directory the file came
from.

**The text sent, and why it is normalized.** The raw files differ by far more than the bug. Every
buggy file ends with the task's specification as a docstring, and several correct files carry
alternative solutions inside string blocks (`gcd`: 340 vs 88 characters for a one-token fix). A
quality score could separate the raw pair on documentation alone. So the primary text (`canon`) is
each program with every docstring and bare string statement removed and comments dropped, re-emitted
by `ast.unparse`. After this step all 40 pairs differ in one or two lines: the fix. The sampler
refuses a pair whose canonical texts are identical, and there are none. The sample was built with
Python 3.9.6. `ast.unparse` output can vary across Python versions, so `sample.jsonl` is the frozen
input: sha256 `89e4fc0bc355727feaa92cfbc80bcea441a136c874b746f5db3e3bdb2ca099a1`, byte-identical
across two builds (`python3 work/score-quixbugs/sample.py`).

**State.** `{"text": <program>}`, the shape `jev-curate` builds (`src/filter.rs:85-87`).

**The question, frozen** (`work/score-quixbugs/run.py`, `QUESTION`). `jev-curate`'s `code_quality`
Score, verbatim from `src/presets.rs:136-147`: instructions *"Rate the completeness, idiomacy, and
correctness of this code snippet."*, with the five descriptions in key order `"1"`..`"5"` sent as
the ordered list the API requires (levels 0..4): *"Broken, pseudo-code, or unrunnable syntax"*,
*"Partial implementation with obvious bugs"*, *"Working implementation with minimal edge case
handling"*, *"Clean, idiomatic code with error handling"*, *"Production-grade, fully typed,
battle-tested implementation"*. The preset's companion Noul (`has_stub_placeholders`) is not asked;
the bead is about the Score. The value compared is the returned `score` (expected level, 0 to 4).

**Arms.**
- **Jev (primary):** official `typesafe_sdk` 0.7.0 (`typesafe-sdk-python` @ `0ffd094`),
  `AsyncTypeSafeClient(model="jev-1.13.0", retry=RetryPolicy())`, canonical text.
- **Haiku (primary incumbent):** the same `Score` object and state through
  `system-one-adapter-python` @ `adffc2e`, `anthropic/claude-haiku-4-5`, structured outputs,
  `llm_answer_mode="probabilities"`, `normalize_probabilities=True`. Every row records the adapter's
  `debug.probability_errors` and `debug.original_probabilities` for the question. A Score is exposed
  to the zero-mass defect (`adapter-uniform-20260924.md`): an all-zero map comes back as the middle
  level with no error.
- **Descriptive only, Jev, no verdict rides on them:** `jev-flat` sends the canonical text after
  `jev-curate`'s own `pre_filter_sanity` (`src/filter.rs:34-67`: trim every line, drop blank lines).
  That transform strips Python indentation, so this arm shows what the tool's pipeline would actually
  send. `jev-asis` sends the files as shipped, docstrings included, to size the documentation
  confound.
- **Constant:** every program gets the same score, so all 40 pairs tie: win rate 0.500, AUC 0.500,
  sign test p = 1. As a classifier, always-correct is right on 40/80
  (`node work/jev-prevalence-first/prevalence-check.mjs work/score-quixbugs/sample.jsonl --truth truth`
  → `DEFERRED`, must beat 40/80).

**Metrics** (`work/score-quixbugs/score.py`, stdlib, no key; its logic was smoke-tested on synthetic
rows in `/tmp` before the bar, with no live data). Per pair: W if score(correct) > score(buggy), L if
<, T if equal. Win rate = (W + T/2) / pairs. An exact two-sided sign test on W vs L, ties dropped. AUC
over all 80 programs (correct = positive, ties averaged). A 95% interval from a bootstrap over pairs
(2,000 draws, `random.Random(20260924)`). A program still unanswered after the resume pass makes its
pair a tie and enters AUC at 2.0. Against Haiku, on the same pairs: McNemar exact on "pair ordered
correctly" (strict W), plus a paired bootstrap interval of the AUC difference.

**Pass rule.**
1. **Jev separates:** W > L with sign-test p < 0.05, **and** the AUC 95% interval lies above 0.5.
2. **Jev does not lose to Haiku:** neither the McNemar test nor the AUC-difference interval is a
   significant Haiku win. A non-significant difference is a TIE, not proven parity.
3. **PASS** = 1 and 2, on all 40 pairs **and** with every pair that holds a zero-mass Haiku row
   dropped (a second sensitivity drops any row with `probability_errors` set). If Jev fails 1, a
   `NEGATIVE_EVIDENCE.md` row is written: the Score does not separate correct from buggy code at this
   N. If Jev fails only 2, the row says Haiku does it better. Nothing is retuned: not the wording, not
   the list, not the text normalization.

**Stated before running:** 80 Jev primary calls, 80 Haiku calls, 160 descriptive Jev calls,
concurrency 8. Also reported: per-call latency and token usage, distinct score values, mean score
for correct vs buggy, and how many programs clear `jev-curate`'s 3.0 floor
(`src/presets.rs:152`, read on the 0-based scale the API returns).

**NO-CLAIM.** One small public set of 40 textbook algorithms whose bugs are one-line logic slips, one
question wording (the tool's own), one Jev version, one Haiku version. A Score that rates "quality"
was not designed to find a single wrong operator; a failure here says the filter would not catch
this kind of bug, not that Jev cannot judge code. QuixBugs is public and may be in either model's
training data, and the correct and buggy versions are both published.

## Results

The bar was committed at `6ee168c` before any arm made a call. All four arms ran on 2026-09-24
between 03:05 and 03:06 UTC. Each answered 80/80 on the first pass with 0 error rows. Rows (sha256):
`rows-jev.jsonl` `627c7b5c…4d8be3`, `rows-haiku.jsonl` `2e609be0…281b0cf`, `rows-jev-flat.jsonl`
`695eac83…4820690e`, `rows-jev-asis.jsonl` `f85d9236…17296d3`, all under `work/score-quixbugs/`.
Re-score with no key, in about 2 s: `python3 work/score-quixbugs/score.py`.

| Arm | Pairs | W / L / T | Win rate | Sign p | AUC (80 programs) | AUC 95% | Mean score correct / buggy | Clears 3.0 correct / buggy |
|---|---:|---|---:|---:|---:|---|---|---|
| constant | 40 | 0 / 0 / 40 | 0.500 | 1 | 0.500 | — | — | — |
| **Jev `jev-1.13.0`** (primary) | 40 | **38 / 2 / 0** | **0.950** | 1.5e-09 | **0.739** | 0.683–0.812 | 1.730 / 1.480 | 0 / 0 |
| **Haiku 4.5 via adapter** (primary) | 40 | 28 / 10 / 2 | 0.725 | 0.0051 | 0.668 | 0.589–0.752 | 2.095 / 1.766 | 0 / 0 |
| Jev, `jev-curate` line-trimmed text (descriptive) | 40 | 35 / 3 / 2 | 0.900 | 6.7e-08 | 0.715 | 0.652–0.790 | 1.650 / 1.417 | 0 / 0 |
| Jev, files as shipped (descriptive) | 40 | 26 / 12 / 2 | 0.675 | 0.034 | 0.622 | 0.556–0.697 | 1.728 / 1.592 | 0 / 0 |

| Arm | Answered | Model reported | p50 / p95 latency | Tokens in / out | Score range | Distinct scores |
|---|---:|---|---|---|---|---:|
| Jev | 80/80 | `jev-1.13.0` (all rows) | 147 / 534 ms | 35,623 / 1,440 | 0.87–2.01 | 56 |
| Haiku | 80/80 | `anthropic/claude-haiku-4-5` | 903 / 3,253 ms | 65,796 / 3,812 | 0.37–2.95 | 44 |
| Jev flat | 80/80 | `jev-1.13.0` | 127 / 432 ms | 34,930 / 1,440 | 0.79–1.96 | 56 |
| Jev as shipped | 80/80 | `jev-1.13.0` | 137 / 332 ms | 43,511 / 1,440 | 0.82–2.07 | 49 |

**Jev vs Haiku, same 40 pairs.** On pairs ordered correctly, Jev alone got 12 and Haiku alone got 2,
McNemar p = 0.013: **WIN**. The AUC difference was +0.070, with a 95% interval of −0.003 to +0.156:
**TIE**.

**Adapter zero-mass check (jev-mly).** `debug` was recorded on 80/80 Haiku rows. `probability_errors`
was set on 0 and zero-mass on 0, so both "without" scorings drop 0 pairs and are identical to the
table above.

**Pass rule applied.** (1) W 38 > L 2, sign p = 1.5e-09, AUC interval 0.683–0.812, entirely above 0.5:
Jev separates. (2) No significant Haiku win: pair ordering is a Jev WIN and AUC is a TIE. Both
scorings are identical. **PASS.** The preregistered `NEGATIVE_EVIDENCE.md` trigger did not fire.

**What the numbers say, and what they do not.**
- **Within a pair, the Score works.** Given the same program with and without its one-line bug, Jev
  scores the correct one higher on 38 of 40 pairs. Its two misses are by 0.01 and 0.02 (`mergesort`
  1.98 vs 1.99, `next_palindrome` 1.42 vs 1.44). Haiku gets 28, and 8 of its 10 misses score the
  buggy version higher by 0.04 to 0.25.
- **Across programs, the Score is a weak filter.** AUC over all 80 programs is 0.739. Scores sit in a
  narrow band (Jev 0.87 to 2.01), and which program is scored matters more than whether it has its
  bug. The score ranks a fix above its bug far better than it sets an absolute bar.
- **`jev-curate`'s floor would reject everything.** The preset keeps a row only when `code_quality`
  is at least 3.0. Read on the 0-based scale the API returns, 0 of 80 programs clear it on either arm,
  correct ones included: Jev's highest score is 2.01 and Haiku's is 2.95. Fixing the request shape
  (the upstream issue) is necessary but not sufficient. The floor also needs re-reading, as the issue
  draft already warns.
- **The tool's own preprocessing costs a little.** `jev-curate` strips every line's indentation
  before sending. On that flattened text Jev still orders 35 of 40 pairs (3 losses, 2 ties),
  against 38 of 40 on the indented text. Descriptive, one run.
- **Documentation dominates the raw files.** Sent as shipped, where the buggy files carry a spec
  docstring and some correct files carry alternative solutions, Jev orders only 26 of 40. The spec
  docstring makes a buggy file look more complete. A filter fed raw repository files is measuring
  documentation as much as correctness.

**Verdict** (`[live]`, N=40 pairs / 80 programs per arm, 2026-09-24). `jev-curate`'s `code_quality`
Score, sent in the list shape the API accepts, at `jev-1.13.0`, puts the correct QuixBugs program
above its one-line-buggy twin on 38 of 40 pairs (sign p = 1.5e-09; AUC 0.739 over 80 programs,
interval above 0.5). It beats Claude Haiku 4.5 on pair ordering, 12 vs 2 discordant (p = 0.013), and
ties it on AUC. As shipped, the tool's 3.0 floor would still reject all 80 programs.

**Spend.** 320 live calls. Jev: 240 calls, 114,064 input / 4,320 output tokens as the API reported
(80 primary, 160 descriptive); at the $0.042 per 1M input rate stated in `jev-curate`'s README that is
about $0.005. Haiku: 80 calls, 65,796 input / 3,812 output (adapter totals); [INFERENCE] about $0.09
at $1 / $5 per million input / output tokens. Neither figure is an invoice.

**Boundary.** 40 textbook algorithms, one bug each; one question wording (the tool's); one run per
arm, so run-to-run variance was not measured, and it matters where Jev's losses and several wins are
hundredths apart. The canonicalization is ours: `ast.unparse` removes comments and docstrings, and
real code has both. The as-shipped arm shows that matters. The 3.0-floor reading assumes the fixed
tool keeps comparing against the API's 0-based scale. QuixBugs is public and in both versions, so it
may be in either model's training data. Nothing was tuned after the answers came back. The bead waits
for a non-author re-score from the committed rows.

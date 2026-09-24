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

Pending: filled in after the arms run.

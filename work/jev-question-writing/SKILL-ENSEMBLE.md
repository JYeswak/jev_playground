# SKILL-ENSEMBLE — the parallel-composite-Choice recipe

Pass 3 of the jev-vbh.2 question-writing loop. Companions: `./trial.mjs`
(`runEnsemble` stub; defined, never invoked at load), `./SKILL-SHORT.md`
(what a question must be), `./SKILL-PURPOSE.md` (which kind a judgment takes).

Rule: **when the surviving questions are parallel and independent, ask them
as ONE Choice over 2–4 live options in the SAME request — never as
independent binaries over mutually exclusive classes.**

## 1. Parallel, independent, same request

One request, one state, one Choice question whose criteria MAP holds the
surviving options (2–4 labels). The options are asked together so the model
weighs them against each other, not in isolation. Sequential calls, separate
requests per option, or one call per label are not this recipe — they
reintroduce the isolation the Choice shape exists to remove.

- Caller: `askJevChoice` from `work/jev-client/src/index.ts` (`state` +
  `instructions` + `classes` MAP; refuses a degenerate set — `{}`, one
  label, or a list — before any network call).
- Trial: `runEnsemble` in `./trial.mjs` — takes a state + 2–4 criteria,
  calls `askJevChoice`, prints choice + confidence + per-label
  probabilities. Defined, never invoked at load; 0 Jev calls this pass.

## 2. Never three incoherent binaries for mutually exclusive classes

Three independent Nouls over exclusive classes let the model answer yes
twice, or no three times; nothing in that call shape forbids it. A Choice
question forbids it in the protocol.

- Receipt: `docs/demos/upstream-repro/multiclass-failure-20260919.md` — the
  binary arm answered **`argument` AND `bug` both true** on
  `assertion-expected-actual` and `undefined-property-under-edit`, two
  classes true at once on classes mutually exclusive by construction;
  across seven binary runs the case-level score moved 9, 10, 9, 9, 9, 9, 9
  with the identity of the misses moving between blocks, while both
  multiclass wordings scored 11/11 with zero drift. Rewording moved which
  cases broke; changing the shape stopped them breaking.
- Commit: `48f834b` (the multiclass conversion measurement + the trial
  skeleton's lineage context).

## 3. Criteria as MAP; confidence reads concentration, not correctness

`criteria` is a MAP of label -> description — the SDK itself rejects a list
(`@typesafe-ai/sdk` dist/index.mjs:339), and `askJevChoice` refuses a list
or a <2-label set before spending a call (`work/jev-client/test/client.test.mjs`).
Put meaning in the descriptions: labels + descriptions are part of the
question the model sees; the key name files scores for the harness only
(SKILL-PURPOSE rule 4).

Confidence is distribution concentration — how decisively the model picked
the top label over its live alternatives — not a correctness certificate.
The narrowest multiclass margins on record (0.23 question-shaped, 0.55
declarative; hold-out margins 0.90–1.00) describe decisiveness, and the
`THIN_MARGIN = 0.1` convention in `work/omp-jev-failure/measure-multiclass.mjs`
flags top-1-barely-clearing-top-2 as the multiclass analogue of a
threshold-made verdict. A high-confidence miss is still a miss.

## 4. Conversion is earned on robustness, not accuracy

- Receipt: `docs/demos/upstream-repro/failure-multiclass-holdout-20260919.md`
  (the superiority-refutation half) — on nine fresh failures both framings
  scored 8/9 with the SAME miss and zero incoherent rows: multiclass holds
  (one-case DROP from 11/11) but binary holds equally here, because the
  structural defect the conversion removes did not fire on these nine. What
  the hold-out supports is narrower: multiclass is no worse, cannot go
  incoherent by construction, and decides at margins 0.90–1.00 with zero
  drift. That is a robustness argument for the conversion, not a
  superiority result.

So: convert a binary family to one Choice when the labels are mutually
exclusive by construction (incoherence is possible and observed), and defend
the conversion on incoherence-removal + margin stability — never on a single
accuracy number the next nine cases can tie.

## Trial mechanics (ensemble form)

1. Assemble 2–4 live options: each a label with a self-contained
   description (instructions + criteria name the judgment; the key names it
   for nobody but the harness).
2. Call once via `runEnsemble({ state, instructions, classes })`; print
   choice, confidence, and the full per-label probabilities — never the
   choice alone, or margins stop being auditable.
3. Grade by chosen label against boolean-per-label truth, each label still
   subject to SHORT rule 0's own-constant bar — a label the model always
   (or never) picks has proven nothing.

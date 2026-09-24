# Section 5 claims: three to register, four dropped (bead `jev-deep-kit-8q7`)

RedMaple (pane 2), 2026-09-24. No Jev call. Section 12 was left to pane 1.

The seven planned sentences are in `docs/PLAN-DEEP-KIT-20260922.md` section 5.
An `enforce=yes` row whose pattern is absent from `README.md` fails
`foundation/kit/check-claim-discipline.sh`. These rows are handed to
ReadmeStrangerRun to land with the sentences, in one commit. They are not in
`foundation/kit/claims.tsv` yet.

## Hand to ReadmeStrangerRun

Re-run `python3 foundation/kit/claim-units.py README.md foundation/kit/claims.tsv`
in the landing commit. The fraction below was measured before that commit
(`candidates=79 covered=45`, floor file the same). If the fraction moved, use
the new one and do not keep 45 of 79.

Sentence: `45 of 79 README claim sentences are registered`

```
claim-coverage	45 of 79 README claim sentences are registered	claim-coverage	candidates=79 covered=45	docs/demos/upstream-repro/section5-claims-20260924.md	yes	Measured 2026-09-24 by claim-units.py before the README sentence landed. Re-derive the fraction in the landing commit.
```

Sentence: `jev's gates run in public CI at every push; the verdict at 196e124 is green with 5 typed skips`

The workflow runs on every push to `main` (`.github/workflows/gates.yml`).
The latest run that had a verdict at measurement time was
https://github.com/JYeswak/jev_playground/actions/runs/35978286566
at `196e124`, GitHub conclusion `success`. The job log says
`VERDICT: GREEN WITH 5 TYPED SKIPS`, not plain green. Newer runs were still
`in_progress` and are not this pin.

```
ci-pin	jev's gates run in public CI at every push; the verdict at 196e124 is green with 5 typed skips	ci-pin	VERDICT: GREEN WITH 5 TYPED SKIPS	docs/demos/upstream-repro/section5-claims-20260924.md	yes	Latest completed gates.yml run at measurement, 2026-09-24. Not the tip if a later run has since finished.
```

Sentence: `jev has been assessed with the FrankenSuite RULEBOOK v1.0`

Proof is `notes/deep/jev-assessment.md` (header names RULEBOOK v1.0) and the
cold read `notes/deep/jev-assessment-coldread-p2.md`, whose five dangling
items have author replies in that file. This pane did not re-check each reply
against the assessment body.

```
self-assessed	jev has been assessed with the FrankenSuite RULEBOOK v1.0	jev-assessment	RULEBOOK v1.0	notes/deep/jev-assessment.md	yes	W5.1 packet plus W5.2 cold read. Cold-read replies were not re-verified line by line.
```

## Dropped

Recorded in `NEGATIVE_EVIDENCE.md` R94–R97.

| label | why the planned sentence is false |
|---|---|
| kit-loaded | `tmux list-panes -t jev` showed 3 omp panes, not 6. Pane 1 started 2026-09-22 20:02, before the six rule files (2026-09-23 21:24). Pane 2 (`omp --profile grok`, started 2026-09-23 21:29) has the six rules in `omp ttsr list`. kit-guard load was not dumped. |
| kit-trips | No committed live-pane frame (pane id, pid, profile, model, time) shows each mechanism firing and staying silent. |
| kit-e2e | `foundation/gates.d/` has no omp-kit e2e stage. `scripts/` has no e2e script. |
| false-close-zero | 11 of 164 closed beads close on `done` (4 characters). |

## kit-loaded census

| pane | process | started | six kit rules |
|---|---|---|---|
| 0 | zsh (user) | 2026-09-20 14:31 | not an omp pane |
| 1 | `omp --auto-approve` | 2026-09-22 20:02:34 | session predates the rule files |
| 2 | `omp --profile grok` | 2026-09-23 21:29:16 | loaded: `omp ttsr list` names all six |
| 3 | `omp --profile grok` | 2026-09-24 02:51:31 | started after the files; loaded state not dumped |

The six rules on pane 2: `kit-close-needs-evidence`, `kit-jsonl-close`,
`kit-no-verify`, `kit-test-skip`, `kit-unverified-done`, `kit-weasel-retry`.

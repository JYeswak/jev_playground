# jev-kit

A small TypeScript-first Jev client with preflight checks, typed validators, offline fixtures, and CLI verbs.

## Banking77 classification

`jev classify` implements the measured **intent routing** design from `docs-mirror/typesafe/patterns/intent-routing.md` and the Choice primitive. It asks one Choice over the 77 humanized Banking77 intent labels, with state `{ "customer_message": text }` and the instruction `The primary intent of this customer banking message`. Label descriptions remain `null`, matching `work/choice-banking77/run.py`; returned confidence is exposed without an invented action threshold.

The captured public example comes from PolyAI-LDN/task-specific-datasets at revision `9d081458ff52e53cf7e848f414e6e9344e4e6696`, `banking_data/test.csv`, row 1. The source row is in `examples/banking77-example.json`; the complete label set is in `examples/banking77-labels.json`.
```bash
npm ci
npx --no-install tsc -p tsconfig.json
node bin/jev.mjs classify \
  --text "I still have not received my new card, I ordered over a week ago." \
  --labels examples/banking77-labels.json --fake --robot
```

The keyless command returns the captured answer with `label: "card arrival"` and `model: "fake"`. Remove `--fake` for a live call; the client pins `jev-1.13.0` and requires `TYPESAFE_API_KEY`.

The underlying live measurement is recorded in `docs/demos/upstream-repro/choice-banking77-full-20260924.md`: on the public Banking77 test split, Jev scored 2,467/3,080 (80.1%) versus Haiku prompted JSON at 2,267/3,080 (73.6%), live lane, N=3,080 per arm, 2026-09-24, Jev `jev-1.13.0`. That benchmark is the design source, not a claim about this single example.

Malformed answers, labels absent from the offered set, and requests estimated `OVER` the documented input limit are refused before a classification result is returned.

## SciFact claim verification

`jev verify` implements the measured **claim verification** design from the Noul primitive and `work/noul-scifact/run.py`: state `{ "claim": C, "evidence": text }`, instruction `Does the evidence support the claim?`, and criteria matching the measured arm. A value **greater than 0.5** is labeled `supported`; values at or below 0.5 are labeled `unsupported`. This is the threshold used by `work/noul-scifact/score.py`.

The example evidence is copied from the first captured SciFact row in `work/noul-scifact/sample.jsonl`; its Jev answer is recorded in `test/fixtures/scifact-answer.json` (0.27, unsupported). Run it without a key:

```bash
npm ci
npx --no-install tsc -p tsconfig.json
node bin/jev.mjs verify \
  --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." \
  --evidence examples/scifact-evidence.txt --fake --robot
```

The fake run never contacts Jev and reports `model: "fake"`. Remove `--fake` for a live call; the client pins `jev-1.13.0` and requires `TYPESAFE_API_KEY`. The underlying live measurement is SciFact Jev 361/400 (90.2%, Brier 0.0709) versus Haiku 351/400 (87.8%, Brier 0.1002), live lane, N=400 per arm, 2026-09-24; see `work/noul-scifact/score.py`. That benchmark is the design source, not a claim about this single example.

Malformed Noul values and requests estimated `OVER` the documented input limit are refused before a verification label is returned.

## SST-5 sentiment scoring

`jev score` implements the measured **composite scoring** design from the Score primitive and `work/score-sst5/run.py`: state `{ "text": sentence }`, instruction `How positive is this movie review sentence?`, and the five ordered SST-5 level descriptions. The returned integer is the selected level index (0–4), and `level` is the corresponding description; this preserves the measured score rather than pretending it is an exact gold-label answer.

The example sentence is copied from the first captured SST-5 test row in `work/score-sst5/sample.jsonl`; its Jev answer is recorded in `test/fixtures/sst5-answer.json` (score 3, `model: "jev-1.13.0"`). Run it without a key:

```bash
npm ci
npx --no-install tsc -p tsconfig.json
node bin/jev.mjs score --text "it represents better-than-average movie-making that does not demand a dumb, distracted audience." --levels examples/sst5-levels.json --fake --robot
```

The fake run never contacts Jev and reports `model: "fake"`. Remove `--fake` for a live call; the client pins `jev-1.13.0` and requires `TYPESAFE_API_KEY`. The underlying live measurement is SST-5 Jev 273/500 (MAE 0.488) versus Haiku 251/500 (MAE 0.556), live lane, N=500 per arm, 2026-09-24; see `work/score-sst5/score.py`. That benchmark is the design source, not a claim about this single example.

Malformed score answers and requests estimated `OVER` the documented input limit are refused before a score is returned.

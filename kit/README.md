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

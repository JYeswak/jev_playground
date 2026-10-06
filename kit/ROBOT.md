# `classifier` robot contract

The package exposes `classifier` and the short alias `clf`; both invoke the same CLI. It deliberately does not expose `jev`, which remains the hermes-jev-skills executable. The separate `jev-skill-gap` executable remains available.

`classifier --help` and `classifier --version` exit 0. Bare invocation prints the overview. `--robot` and command-level `--json` emit the stable envelope:

```json
{
  "ok": true,
  "schema": "classifier.ask.v1",
  "status": "OK",
  "data": {},
  "meta": { "version": "0.0.0", "backend": "jev", "model": null, "latency_ms": 0, "usage": null },
  "warnings": [],
  "commands": [],
  "errors": []
}
```

`classifier doctor --json` is the exception: it preserves the raw doctor report. `classifier doctor --robot` wraps that report in `classifier.doctor.v1`. With no key, the doctor report is `NOT_RUN` and exit 2; a missing SDK yields `ONLINE_REQUIRED`/exit 6 in the robot envelope (the raw `--json` report retains the doctor status and reason).

Exit codes are shared across commands: 0 success; 1 findings; 2 `NOT_RUN`; 3 refused (including an unoffered answer); 4 refused_unsafe; 5 retryable; 6 online_required; 64 usage; 66 missing input; 73 cannot create; 74 I/O. Unknown flags are usage errors unless Stage 0 recognizes a unique safe correction or ignores a distant, non-destructive flag with a warning. Destructive flags are never auto-corrected.

```bash
classifier ask choice|score|noul --state FILE --question FILE --robot
classifier rerank --query Q --candidates FILE --robot
classifier classify --text T --labels FILE --robot
classifier verify --claim C --evidence FILE --robot
classifier score --text T --levels FILE --robot
classifier gate --command C --robot
classifier omp install --dir DIR --robot
classifier omp uninstall --dir DIR --robot
```

`--fake` uses captured fixtures and never contacts Jev. For example, `classifier rerank` replays the captured FiQA answer from `kit/test/fixtures/rerank-fiqa-answer.json`; the example passages and IDs are copied from BEIR FiQA-2018 query `10034`. Rerank is one Choice over the candidate passages, not a full reranking. The measured design has no synthetic `none` candidate; malformed or unoffered answers are refused.

Banking77 classification uses the captured intent Choice, null label descriptions, and no confidence threshold. Claim verification uses the captured SciFact Noul and labels values `>0.5` supported, `<=0.5` unsupported. SST-5 scoring returns the selected integer level, description, confidence, and probabilities. `--fake` for each uses its committed fixture and reports `model: "fake"`.

The CLI pins `jev-1.13.0` by default and never prints the API key. Direct clients can choose another model in code.

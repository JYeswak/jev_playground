# `jev-rerank-bench`: a missing docs file reads as empty, so two scripts fail with a misleading `KeyError`

Reported, not patched. The clone is vendored read-only here and is not edited.

## Reproduction

```bash
cd jev-rerank-bench
uv run python determinism.py
```

```
File "determinism.py", line 28, in compare
  texts = [truncate(docs[c["did"]]) for c in r["present"]]
KeyError: '14717500'
```

`batching.py` fails the same way on the same id. Both reproduce from a clean clone with no API key,
because they crash before any call is made.

## Mechanism

`determinism.py:20` builds its corpus from a file that is not in the repo:

```python
docs = {r["did"]: r["text"] for r in read_jsonl(CANDIDATES / "scifact.docs.jsonl")}
```

`candidates/` contains `scifact.jsonl`. It does **not** contain `scifact.docs.jsonl`, and there is no
`scifact.docs.jsonl.gz` either — checked both, since `read_jsonl` prefers the gzipped sibling.

`common.py:153` is explicit that absence is legal:

```python
def read_jsonl(path: Path) -> list[dict]:
    """Rows of <path>.gz (if present) followed by rows of <path> (if present); either may be missing."""
```

So the missing file yields `[]`, `docs` becomes `{}`, and the failure surfaces eight lines later as a
`KeyError` naming the first candidate document id. **The id in the message is not the problem — every
id would fail, because the corpus is empty.** A reader chasing `14717500` is chasing a document that
was never loaded.

The cached results themselves are fine: `eval.py`, `significance.py`, `nevir_eval.py` and the BM25
control all run to completion on this clone.

## Suggested fix

Two options, either sufficient:

1. **Fail closed at the load.** After building `docs`, refuse when it is empty and name the path:
   `raise SystemExit(f"no documents at {CANDIDATES/'scifact.docs.jsonl'}; run the fetch step first")`.
   This turns a downstream `KeyError` into the actual cause, and costs one line.
2. **Add the missing control to `read_jsonl`.** Its permissive contract is deliberate and useful for
   the gz/plain pair, so rather than changing it, give callers a strict wrapper —
   `read_jsonl_required(path)` — and use that where an empty corpus cannot be correct.

A `RED` control worth shipping alongside: point the loader at a nonexistent path and assert the
process exits with the path named, not with a `KeyError` on a document id.

## What this does not claim

- The **cause of the absence** is not established. `scifact.docs.jsonl` may be produced by a fetch or
  preparation step that is undocumented in the README, gitignored, or was dropped from the repo; I did
  not search the history to find out, and the fix above is correct either way.
- No judgement about the benchmark's **results**, which reproduce: the committed cache gives Jev
  rubric 0.692 against Cohere Pro 0.691, and a fresh `nevir_eval` run over 1,383 pairs gives Jev
  rubric 71.1% against Cohere 67.0%, +4.2 points at p=.002.
- `coldstart.py` exits 1 for a different reason — it reads `JEV_API_KEY` from a `.env` file and does
  not see an environment variable injected by a secrets wrapper. That is arguably intended behaviour
  and is reported separately if at all.

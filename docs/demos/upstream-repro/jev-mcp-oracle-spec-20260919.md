# jev-mcp zero-API oracle specification

**Upstream:** `upstream/jkudish/jev-mcp`
**Scope:** zero-API specification only; no live calls.
**Class:** B — committed golden/cassette and contract evidence, not ground-truth corpus.

## Decision surface

The server exposes three agent-facing choices:

- `jev_verify`: claim verdicts against evidence;
- `jev_screen`: pass/review/block/skip for fetched content;
- `jev_find`: candidate ranking plus none-of-these signal.

The operational oracle is not "the server returned JSON". It is whether a caller's chosen action
matches a known expected contract on committed tests/cassettes.

## Oracle shape

- **Consumer:** an MCP client deciding whether to accept claims, read content, or select a candidate.
- **Gold:** committed unit expectations and live-response cassettes under `tests/`.
- **Positive controls:** verified/contradicted claims, benign screening, and relevant candidate choice.
- **Negative controls:** unsupported claims, prompt-injection screening, irrelevant candidates, and
  missing/low-confidence cases.
- **Class boundary:** B because these are fixtures/cassettes and contract tests, not an independently
  labeled real-world corpus with a measured task denominator.
- **Promotion requirement:** a pinned labeled corpus with per-case expected action and a preregistered
  threshold for false accepts/blocks before this can become class C.

## Why this is not a product verdict

This repo's README says 9/9 unit and 4/4 live e2e, but this unit deliberately does not spend an API
key or rerun the live path. The committed cassettes and test assertions establish a usable contract
surface; they do not establish calibration, production accuracy, or safe thresholds.

No clone was edited and no live request was made.

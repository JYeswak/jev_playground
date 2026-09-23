# system-one-adapter-python — W7.0 SDK profile (T1–T3 + T9 + T10)

- **Repo:** first-party `typesafe-ai/system-one-adapter-python` @
  `adffc2eab300a4fa3c0e92252d4ffd6ceaa53700` (Release v0.2.0, detached).
  MIT. Requires-python ≥3.10 (venv 3.14.2; system 3.9.6 unusable).
- **`git status`:** clean before and after, both copies (verified).
- **Lane:** keyless, 2026-09-23. No live LLM calls.

| id | result | evidence |
|---|---|---|
| T1 | PASS | SHA + MIT + runtimes above |
| T2 | PASS | `env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY uv run pytest` →
  **229 passed** in 4.45s (re-run by parent). Cassette-backed: dummy
  keys injected, `--block-network`, recorded HTTP replays — request
  building + response parsing genuinely execute. RED plant (/tmp copy
  only, ×2.0 in `rescale_probabilities`): 1 failed with the exact
  wrong-distribution assertion |
| T3 | PASS | 6 claims: drop-in SDK question types (`_client.py:457,472`);
  SDK `SystemOneResponse` subclass + Usage (`_response.py:15-29`);
  Responses API default, Chat Completions for custom hosts
  (`openai.py:104-114`) + store=False (`:59`); provider/model as
  constructor defaults (`_client.py:336-337,349-352`); context-manager
  + caller-owned providers not closed (`:386,532-536,633-637`);
  Anthropic max_tokens raises TypeSafeError pre-retry
  (`anthropic.py:57-60`) |
| T9 | PASS | Missing key: OpenAI provider raises missing-credentials at
  construction; Anthropic defers auth but request failures map to
  TypeSafeError (`anthropic.py:20-31`); zero fallback/fake-answer paths
  repo-wide. Stub arms: 429 → TypeSafeRateLimitError; malformed-200 →
  TypeSafeError; hang → full 25 s deadline, no output |
| T10 | SELF | no FLOOR/INCUMBENT (correct per profile). Keyless = cassette
  replay only; live-provider behaviour not evaluated. NO-CLAIM:
  nothing about live accuracy, cost, or latency |

## Duplicate verdict: root copy is STALE

`system-one-adapter-python/` (root) @ `0bb819b` = upstream's own v0.1.4
tag-commit (`git -C upstream rev-parse 0bb819b` returns the identical
hash — verified by parent). Upstream is two releases ahead (v0.1.5,
v0.2.0 adffc2e); 28 files differ over 65 tracked (src, 12 cassettes,
tests, README, changelog, pyproject, uv.lock). Sync = fast-forward root
to adffc2e; breaking change noted (msgspec→pydantic per v0.2.0
changelog). Any verdict on the root copy lags that change.

## Boundary

No live calls, no keys. Both clones untouched.

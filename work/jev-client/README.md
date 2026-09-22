# work/jev-client

The lane's single sanctioned Jev caller. The network path is
`TypeSafeClient.systemOne` from the vendored first-party SDK
(`upstream/typesafe-ai/typesafe-sdk-js @ 66880cc`); no hand-rolled POST
remains. Our code owns the failure taxonomy, the field guards, and the
fail-safe direction — the SDK owns the wire.

- `askJev` — Noul questions (instructions-only; the SDK's true/false criteria
  descriptions are unused).
- `askJevChoice` — one Choice over a label map (≥2 labels, refused pre-call).
- `askJevScore` — one Score over an ordered rubric; a criteria list shorter
  than 2 is refused before any network call.
- `askJevBundle` — mixed questions in one request, passed through unmodified.
- Single-attempt semantics (SDK retry disabled per call); 4 s default timeout
  passed through. Missing key returns `unconfigured`, never a score.

Shipped: 943158c (cutover) · 118185e (score path) · c84d562 (rerank caller
rewired). Offline suites green with injected fetch; zero live calls in tests.

This is not a certified seat. A wrapper with passing tests proves the
failure taxonomy, not that any judgment is correct.

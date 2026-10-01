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

## Infisical key lookup boundary

`useInfisicalKey` installs a provider that first tries the current Infisical
user session, then falls back to the universal-auth machine identity in
`~/.config/infisical/zeststream.env`, **only** at the owner-approved origin
`APPROVED_INFISICAL_ORIGIN` (`https://secrets.zeststream.ai`; Joshua's blanket
approval, 2026-09-30). The credential file's `INFISICAL_API_URL` is not
approval: it must name that same origin. An HTTP URL, a different origin,
embedded URL credentials/query/fragment, a rejected login, or a redirect returns
no key. The parent `TYPESAFE_API_KEY` is never inherited by the child; its
allowlisted environment is `PATH`, `HOME`, `TMPDIR`, and, for the machine lookup
only, `INFISICAL_API_URL` and `INFISICAL_TOKEN`. No client secret is passed in
argv. Unit tests use synthetic credentials and an injected transport; the live
fallback proof (real login at the approved origin, real Jev call) is recorded on
bead `jev-wiya`.

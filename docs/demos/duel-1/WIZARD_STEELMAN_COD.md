# MU-2 steelman: context-admission screen hook

Bead: `jev-demo-loop-a1q`
Role: steelman of my lowest-scored idea, MU-2
Prior score: 470/1000 in `WIZARD_SCORES_COD_ON_MU.md`

## Plain verdict

MU-2 is **better than its unsafe implementation, and the defect is fixable rather than
structural**. The valuable product is a pre-context admission boundary for untrusted
files, fetches, and pastes. The rejected implementation asked Jev to inspect raw incoming
results for credential material; that sends the very bytes it claims to protect across
the paid external boundary. The steelman accepts the idea only with a deterministic local
secret boundary placed before every Jev call.

If the local boundary cannot be proven, MU-2 remains rejected. Injection screening alone
is still useful, but it must not be marketed as credential protection.

## Strongest case

Usage Map §1 reports that `jev_screen` blocked a hidden “ignore your instructions” note
at injection probability 0.99 while still reading the page as a real page, and names an
omp context-admission hook for files, fetches, and pastes as the demo angle
(`docs/demos/USAGE-MAP.md:11-15`). That is a direct fit for an omp fleet: the dangerous
bytes are most valuable to reject before they become model context, transcripts, logs,
or later evidence.

A good admission hook would make the context boundary explicit instead of relying on
post-hoc commit scanning:

1. Receive an incoming tool result at the omp seam.
2. Run a deterministic local secret detector before any paid or remote call.
3. If the detector finds a credential candidate, never send the original bytes anywhere
   outside the local process. Fail closed, or replace every candidate span with a fixed
   redaction token and retain only the redacted surrogate.
4. Ask Jev about injection semantics only over clean bytes or the redacted surrogate.
5. Map the typed answer through local thresholds: admit, block, or redact-with-reason.
6. Emit only counts, detector version, decision, latency, and hashes of redacted material;
   never emit the original result or a secret-bearing prompt.

This preserves the strongest part of MU-2—semantic injection detection—while making the
credential promise a local invariant rather than a probabilistic Jev claim. It also keeps
policy in code: injection detection is fail-closed, detector uncertainty is fail-closed,
and malformed Jev answers execute nothing.

## Accepted security fix

The screen must **never send raw credential material** to Jev, any remote provider, a
transcript, a log, a fixture, or a receipt. “Credential material” includes API keys,
access tokens, cookies, passwords, private keys, bearer headers, and runtime-assembled
canaries that match the local detector. A detector hit or detector error is a refusal,
not permission to ask Jev about the original bytes.

The accepted implementation has these boundaries:

- Local detection precedes Jev and precedes persistence.
- Redaction is span-preserving enough for injection classification but irreversible for
  the original secret (`<REDACTED:credential>` or an equivalent fixed token).
- The original result is held only in the local hook invocation and is never passed to
  the asker, logger, receipt writer, or fallback path.
- Jev failure, malformed answers, detector uncertainty, and redaction failure all fail
  closed for the incoming result.
- The receipt records `raw_bytes_sent_to_jev: 0` for every credential-positive or
  uncertain case, plus detector/redaction versions and aggregate counts. It does not
  record raw content.

This is a narrower and stronger claim than “Jev detects secrets.” The local detector
owns the secret boundary; Jev owns only the semantic injection signal over safe input.

## How the tests prove the invariant

The critical test is not merely “the hook returned block.” It must observe the exact
request boundary:

- Assemble a unique secret canary at runtime (never in source, fixtures, or logs), embed
  it in a tool result next to a hidden injection directive, and use an injected fake Jev
  asker/request recorder.
- Run the hook. Assert the hook refuses or sends only a redacted surrogate, and assert
  every captured Jev state, question payload, fallback payload, receipt field, and log
  line excludes the canary. Assert the canary is absent from the serialized request
  body, not just absent from the final context.
- Bypass the detector in a known-bad test double. The same canary test must turn RED;
  otherwise the no-leak assertion is not a fires-on-known-bad proof.
- Test detector error and redaction failure. Both must produce a refusal and zero Jev
  requests containing the original bytes.
- Test a clean documentation page. It should reach the injection question, admit
  silently when safe, and produce no credential alarm or comment.
- Test a hidden-instruction page without a credential candidate. Jev's trigger answer
  must produce a block; forcing an admitted answer must be RED.
- Test an empty scan set and malformed Jev answer. Both must be explicit errors or
  fail-closed refusals, never silent admission.

The canary is generated at runtime like the lane's no-secrets gate. This proves the
boundary without placing a real credential in the repository.

## Four ship artifacts

- **Install:** an idempotent project-scoped install command writes the hook under
  `.omp/hooks/pre/`, verifies the `pre` directory is discoverable in every profile, and
  refuses rather than silently installing a dead hook. It reports the local detector
  version and the fail-safe policy.
- **Deterministic tests with RED arms:** the runtime canary request-boundary test,
  detector-bypass test, detector-error test, clean-page silent path, injection trigger,
  empty scan set, malformed answer, and redaction-failure test described above. The
  injected asker must make all policy outcomes deterministic.
- **Receipt:** per-run counts for clean/admitted, blocked injection, credential-positive,
  uncertain/refused, Jev requests, redactions, detector version, policy thresholds,
  latency, and `raw_bytes_sent_to_jev`. The receipt must contain no original content.
- **EVAL row:** cite `jev-mcp@6ec5efc`, the exact omp seam, the local detector version,
  the canary RED arm, and the boundary that live proof uses synthetic runtime canaries,
  not real secrets. An L3 transcript must show both a clean admission and a known-bad
  injection refusal.

## What the steelman does not claim

This does not prove that a heuristic local detector finds every secret. It proves a
stronger operational boundary: detector-positive and detector-uncertain bytes never
reach Jev, and detector misses remain a residual risk recorded in the EVAL Boundary.
A future blind secret-detection benchmark may measure recall; it is not a reason to send
raw credentials to the classifier today.

The hook still has paid latency and provider-availability costs for safe inputs. Those
are acceptable only if the receipt measures them and the local fail-closed path remains
usable when Jev is unavailable.

**NO-CLAIM:** No hook, detector, fake asker, RED arm, receipt, or live omp seam was
implemented or run in this steelman. This is a corrected design argument, not validation.

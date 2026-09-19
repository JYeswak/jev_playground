# Upstream report: commit-sweep treats AWS's canonical example key as a hard secret

**Target:** `~/Developer/foundry/loop-kit/commit-sweep-gate.sh`
**Found by:** pane 1 (`jev`), while re-running `stamp-check.sh --repo ~/Developer/jev`
**Reproduction source:** `docs/demos/duel-2/runs/publish-redteam-20260918T153930Z.json`
**Status:** reported, not patched. The upstream worktree is dirty with unrelated changes; no edit or commit was made there.

## Reproduction

The current stamp-check run reports p10's hard finding:

```text
[S3-SECRET] AWS access-key id (AKIA...) in
 docs/demos/duel-2/runs/publish-redteam-20260918T153930Z.json
```

The matched value is AWS’s canonical documentation example value. It appears in a receipt field that explicitly says
it is AWS documentation example-key prose and that the live key remains in Infisical. No credential
value, authorization header, or operational secret is present.

The detector's own rule is visible in `loop-kit/commit-sweep-gate.sh`:

```python
(re.compile(r'AKIA[0-9A-Z]{16}'), "AWS access-key id (AKIA...)")
```

The literal is 20 characters and matches that expression exactly.

## Mechanism

The detector classifies every added line matching the AKIA shape as `S3-SECRET` unless its
scanner-artifact predicate applies. The line is in a red-team receipt, not a `*-gate.sh` or test
path and not marked with the current scanner-artifact pragma. The exact AWS-published example key
therefore becomes a hard secret finding by construction, even though it cannot authenticate and the
receipt identifies it as documentation prose.

This is a false positive in the detector, not a secret in the Jev tree. It will recur in any public
repository that honestly documents or tests the pattern the detector claims to recognize.

## Suggested fix, not a submitted patch

Keep the detector fail-closed for arbitrary AKIA values, but add a narrow exact-value exception for
AWS's canonical documentation example key (the canonical AWS documentation example value) when the surrounding line is
explicitly documentation/test/receipt prose. Emit an advisory row naming the exception rather than
silently dropping it. A path-only exception is insufficient: a real key in a README must still
REFUSE, and a future example key should not be guessed safe.

The selftest should add both directions:

1. canonical example key in explicit documentation context → ADVISORY, not HARD;
2. a different AKIA-shaped value in the same context → HARD REFUSE.

## Non-claims

- No claim that other secret patterns are false positives.
- No patch, commit, or push was made in `foundry`.
- No claim that the receipt's other p10/publishability findings are resolved by this report.

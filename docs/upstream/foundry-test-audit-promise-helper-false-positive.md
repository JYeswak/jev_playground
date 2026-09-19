# Upstream report: test-audit misses a propagated assertion through an awaited promise helper

**Target:** `~/Developer/foundry/loop-kit/test-audit-gate.sh`
**Found by:** pane 1 (`jev`), while re-running `stamp-check.sh --repo ~/Developer/jev`
**Reproduction source:** `demos/routing-backtest/test/hostile-input.test.mjs`
**Status:** reported, not patched. The upstream worktree is dirty with unrelated changes; no edit or commit was made there.

## Reproduction

The current stamp-check run reports p14:

```text
p14-test-audit FAIL
hostile-input.test.mjs:21 test dynamic-or-literal-test contains NO assertion or propagated failure edge
```

The reported test shape is representative of the file's actual helper:

```js
async function rejectsCode(promise, code, mustName) {
  try {
    await promise;
  } catch (error) {
    assert.equal(error.code, code);
    if (mustName) assert.match(error.message, mustName);
    return;
  }
  assert.fail(`expected rejection with code ${code}`);
}

await rejectsCode(readSessionLogs(...), 'MALFORMED_JSONL', /.../);
```

The helper contains `assert.equal`, `assert.match`, and `assert.fail`. The test awaits the helper's
returned promise. The assertion and failure edge are therefore reachable through the helper call.

## Mechanism

The audit recognizes direct assertion syntax or a narrower propagated-failure shape, but does not
follow a promise-valued argument through a local async helper that awaits it and contains assertions.
It classifies the call site as assertion-free because the call expression itself has no `assert.*`
member. This is a static-analysis false positive: the failure edge is present in the callee and is
propagated by the awaited helper promise.

The defect is specifically interprocedural promise-helper reasoning, not a missing assertion in the
fixture test. The helper is shared by four hostile-input tests, so the finding repeats for each test
that uses this idiom if the audit reports per-test.

## Suggested fix, not a submitted patch

Extend the audit's local call-graph rule for async helpers:

1. resolve a locally defined helper called by the test;
2. inspect whether it awaits or returns the promise argument;
3. inspect the helper body for assertion calls or an unconditional failure edge;
4. treat an awaited call to that helper as a propagated assertion edge;
5. add a RED fixture where the helper only awaits and returns without asserting, proving the rule is
   not a blanket pass for every promise helper.

The selftest should cover both a helper with `assert.fail`/`assert.match` and a helper that merely
awaits the promise. The first should PASS; the second should remain a real audit finding.

## Non-claims

- No claim that every test in the repository has adequate assertions.
- No patch, commit, or push was made in `foundry`.
- No claim about p9 or p10; those findings have separate mechanisms and reports.

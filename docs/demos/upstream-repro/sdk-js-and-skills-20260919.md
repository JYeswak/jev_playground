# Two unrun clones, run — `typesafe-sdk-js` and `typesafe-ai/skills`

**Date:** 2026-09-19 · **Level:** `[oracle]` (someone else's code, someone else's suite)

Joshua, 2026-09-19: *"stop NOT USING the repos we've downloaded ... if your bead can be answered by
an unrun clone, stop and run it today."* Of 22 vendored clones, 19 had receipts. These are two of
the remaining four. `skillranker` is building; `typesafe-sdk-python` is untouched.

## `typesafe-ai/skills` — the vendor's own instructions for using Jev, unread until now

We spent a day designing judgments while the vendor's guidance sat in the tree. What it says that
bears on our code:

- Put the judgment in **instructions**, the answers in **criteria**; **question IDs are not sent to
  the model**, so meaning must be complete in the question.
- Give each question enough **state**; prefer named JSON fields; reference nested state with
  backticked paths.
- **Include a no-match outcome** when nothing may fit.
- Ask one narrow judgment per question; split independently useful dimensions.

**Checked against the code we actually ship, and there is nothing to fix — for a reason worth
recording.** `compaction/` authors no questions at all; it delegates to `fast-jev-compaction`. So
the rules apply to upstream's library, and upstream complies: `questionsFor()` in `src/compact.ts`
embeds the call id and tool inside the instruction text rather than relying on the question key,
and ships the complete state. This is the third independent reason to keep only our adapter.

## `typesafe-sdk-js` — their suite is green and throws eight errors

```
npm install  -> rc=0
npm test     -> Test Files 10 passed (10) · Tests 189 passed (189) · Type Errors no errors
                Errors 8
```

All eight are the same shape:

```
Unhandled Rejection
AbortError: This operation was aborted
 ❯ AbortController.abort node:internal/abort_controller:504:18
 ❯ Timeout._onTimeout src/client.ts:421:18
```

Vitest's own words: *"This might cause false positive tests. Resolve unhandled errors to make sure
your tests are not affected."* A suite reporting 189/189 while throwing eight times is worth an
upstream report on its own — that is the same class of defect as a gate that laundered UNMEASURED
into PASS, which this lane fixed in stage 80.

**What I first claimed, and why it was wrong.** Reading `client.ts:419-422` I concluded the timeout
timer leaked and that a request timeout could crash a consumer process under Node's default
`--unhandled-rejections=throw`. Then I read twenty lines further: `finally { clearTimeout(timer) }`
is there. The timer IS cleared, the abort path IS caught, and my mechanism was fiction built from a
stack trace and half a function.

## NO-CLAIM

The eight rejections **reproduce deterministically** and that is all that is established. The
mechanism is NOT isolated: it may be the tests' fetch doubles rejecting after a test completes
rather than a fault in shipped SDK code, and nothing here shows a consumer being affected. No fix
is proposed and the clone is untouched. `typesafe-sdk-python` and `skillranker` remain unrun.

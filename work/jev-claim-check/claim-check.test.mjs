/** Offline behavior contract for the installed claim-check tool. */
import test from "node:test";
import assert from "node:assert/strict";
import { setKeyProvider } from "../../kit/src/client.ts";
import jevClaimCheckTool from "../../.omp/tools/jev-claim-check.ts";

setKeyProvider(async () => undefined);
const pi = { zod: { object: (shape) => shape, string: () => ({ min: () => ({}) }) } };
const evidence = "The local receipt states the keyword rule beat the judge on tool-call risk triage.";
const qualitative = "The keyword rule beat the judge on tool-call risk triage.";

test("numeric claims refuse before the asker, including a percentage and a unit", async () => {
  let calls = 0;
  const tool = jevClaimCheckTool(pi, async () => {
    calls++;
    throw new Error("numeric claim reached the model");
  });
  for (const claim of ["Live 75/219 top-1", "Coverage reached 96.0%", "Latency was 130ms"]) {
    const result = await tool.execute("numeric", { claim, evidence });
    assert.equal(result.details.verdict, "refused", claim);
    assert.equal(result.details.reason, "numeric-out-of-scope", claim);
    assert.equal(result.details.calledModel, false, claim);
    assert.equal(calls, 0, claim);
  }
});

test("qualitative claims still reach the asker and branch on the returned probability", async () => {
  let calls = 0;
  const tool = jevClaimCheckTool(pi, async () => {
    calls++;
    return { ok: true, scores: { value: 0.8 }, latencyMs: 1, model: "jev-1.13.0" };
  });
  const result = await tool.execute("qualitative", { claim: qualitative, evidence });
  assert.equal(calls, 1);
  assert.equal(result.details.verdict, "supported");
  assert.equal(result.details.value, 0.8);
});

test("malformed answer and absent key never yield a claim verdict", async () => {
  const malformed = jevClaimCheckTool(pi, async () => ({ ok: true, scores: { value: Infinity }, latencyMs: 1, model: "jev-1.13.0" }));
  assert.equal((await malformed.execute("malformed", { claim: qualitative, evidence })).details.verdict, "not_run");
  const saved = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error("unexpected network call"); };
  try {
    assert.equal((await jevClaimCheckTool(pi).execute("keyless", { claim: qualitative, evidence })).details.verdict, "not_run");
  } finally {
    globalThis.fetch = previousFetch;
    if (saved !== undefined) process.env.TYPESAFE_API_KEY = saved;
  }
});

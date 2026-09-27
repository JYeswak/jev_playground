import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { verifyClaim, SCIFACT_CRITERIA, SCIFACT_INSTRUCTIONS, SUPPORT_THRESHOLD } from "../src/verify.ts";
import { createFakeFetch } from "../src/fake.ts";
import { PreflightError } from "../src/preflight.ts";

const claim = "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo.";
const evidence = await readFile(new URL("../examples/scifact-evidence.txt", import.meta.url), "utf8");

function fake(value = 0.27, model = "fake") {
  return createFakeFetch([
    {
      id: "scifact-i0",
      answers: { value: { noul: value } },
      model,
      usage: { input_tokens: 594, output_tokens: 20 },
    },
  ]);
}

test("verify uses the captured SciFact Noul design and labels below 0.5 unsupported", async () => {
  const result = await verifyClaim({
    claim,
    evidence,
    apiKey: "fixture-key",
    fetchImpl: fake(),
    model: "fake",
  });
  assert.equal(result.value, 0.27);
  assert.equal(result.label, "unsupported");
  assert.equal(result.threshold, SUPPORT_THRESHOLD);
  assert.equal(result.model, "fake");
});

test("verify sends claim/evidence state and criteria verbatim", async () => {
  let seen;
  const asker = async (options) => {
    seen = options;
    return { ok: true, scores: { value: 0.8 }, latencyMs: 7, model: "fake" };
  };
  const result = await verifyClaim({ claim, evidence, ask: asker });
  assert.equal(result.label, "supported");
  assert.deepEqual(seen.state, { claim, evidence });
  assert.deepEqual(seen.questions, {
    value: { instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA },
  });
});

test("verify rejects oversized evidence before asking", async () => {
  let asked = false;
  await assert.rejects(
    verifyClaim({
      claim,
      evidence: "x".repeat(100_000),
      ask: async () => {
        asked = true;
        return { ok: true, scores: { value: 1 }, latencyMs: 0, model: "fake" };
      },
    }),
    PreflightError,
  );
  assert.equal(asked, false);
});

test("verify rejects malformed Noul output", async () => {
  await assert.rejects(
    verifyClaim({ claim, evidence, ask: async () => ({ ok: true, scores: { value: 2 }, latencyMs: 0, model: "fake" }) }),
    /invalid Noul value/,
  );
});

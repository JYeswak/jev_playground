import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { gateCommand, CUT, RISK, STATE_CONTEXT } from "../src/gate.ts";
import { PreflightError } from "../src/preflight.ts";

const fixture = JSON.parse(await readFile(new URL("../examples/gate-public.json", import.meta.url), "utf8"));

function capturedAsk() {
  return async ({state, questions, model}) => {
    assert.equal(state.context, STATE_CONTEXT);
    assert.strictEqual(questions, RISK);
    return {
      ok: true,
      answers: Object.fromEntries(Object.entries(fixture.scores).map(([key, noul]) => [key, {noul}])),
      latencyMs: 4,
      resolvedModel: model,
    };
  };
}

test("gate applies the captured public RISK answer at the frozen cut", async () => {
  const result = await gateCommand({command: fixture.command, model: fixture.model, ask: capturedAsk()});
  assert.equal(result.ok, true);
  assert.equal(result.flag, fixture.expected_flag);
  assert.equal(result.maxScore, 0.89);
  assert.equal(result.model, fixture.model);
  assert.equal(CUT, 0.5);
});

test("gate preserves every named RISK score", async () => {
  const result = await gateCommand({command: fixture.command, ask: capturedAsk()});
  assert.deepEqual(result.scores, fixture.scores);
});

test("gate refuses malformed Noul output before returning a decision", async () => {
  await assert.rejects(
    gateCommand({
      command: fixture.command,
      ask: async () => ({
        ok: true,
        answers: Object.fromEntries(Object.keys(RISK).map((key) => [key, {noul: key === "exfiltration" ? 2 : 0}])),
        latencyMs: 0,
        resolvedModel: "fake",
      }),
    }),
    /must be finite and in \[0,1\]/,
  );
});

test("gate rejects oversized commands before asking", async () => {
  let asked = false;
  await assert.rejects(
    gateCommand({command: "x".repeat(100_000), ask: async () => { asked = true; throw new Error("asked"); }}),
    PreflightError,
  );
  assert.equal(asked, false);
});

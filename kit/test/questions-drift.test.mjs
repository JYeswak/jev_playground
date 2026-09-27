import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const sourceUrl = new URL("../../work/bicameral-gate/questions.mjs", import.meta.url);
const packagedUrl = new URL("../src/questions.mjs", import.meta.url);

function assertQuestionsMatch(source, packaged) {
  assert.equal(packaged, source, "kit/src/questions.mjs drifted from work/bicameral-gate/questions.mjs");
}

test("packaged RISK questions stay byte-identical to the frozen source", async (t) => {
  let source;
  try {
    source = await readFile(sourceUrl, "utf8");
  } catch {
    t.skip("NOT_RUN: work/bicameral-gate/questions.mjs is absent in a packed install");
    return;
  }
  const packaged = await readFile(packagedUrl, "utf8");
  assertQuestionsMatch(source, packaged);
});

test("a one-byte RISK question mutation is rejected", async () => {
  const source = await readFile(sourceUrl, "utf8");
  const packaged = await readFile(packagedUrl, "utf8");
  assert.throws(() => assertQuestionsMatch(source, packaged.replace("RISK", "RISK_")), /drifted/);
});

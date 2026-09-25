import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { checkCitation, locate, normalize } from "../src/check.ts";
import { CASES, SOURCE } from "../fixture.mjs";

test("planted cookbook rows fold the way the published table does", async () => {
  for (const row of CASES) {
    let calls = 0;
    const result = await checkCitation(SOURCE, { claim: row.claim, quote: row.quote }, async () => {
      calls += 1;
      return row.answer;
    });
    assert.equal(result.verdict, row.expect.verdict, row.id);
    assert.equal(result.action, row.expect.action, row.id);
    assert.equal(result.calledModel, row.expect.calledModel, row.id);
    assert.equal(calls, row.expect.calledModel ? 1 : 0, row.id);
  }
});

test("curly quotes still locate after whitespace fold", () => {
  const straight = 'a value in the "aud" claim';
  const curly = "a value in the \u201caud\u201d claim";
  assert.equal(locate(SOURCE, straight).status, "found");
  assert.equal(locate(SOURCE, curly).status, "found");
  assert.equal(normalize("a  b"), "a b");
});

test("a missing key is review, never verified", async () => {
  const result = await checkCitation(SOURCE, { claim: "anything", quote: "JWT MUST be rejected" }, async () => ({
    ok: false,
    reason: "unconfigured",
  }));
  assert.equal(result.verdict, "unjudged");
  assert.equal(result.action, "review");
  assert.notEqual(result.verdict, "verified");
});

test("an asker transport failure is review, never verified", async () => {
  const result = await checkCitation(SOURCE, { claim: "anything", quote: "JWT MUST be rejected" }, async () => {
    throw new Error("network");
  });
  assert.equal(result.verdict, "unjudged");
  assert.equal(result.action, "review");
  assert.equal(result.reason, "asker-error");
  assert.equal(result.calledModel, true);
});

test("a label outside the three criteria is review, never auto", async () => {
  const result = await checkCitation(SOURCE, { claim: "anything", quote: "JWT MUST be rejected" }, async () => ({
    ok: true,
    choice: "maybe",
    confidence: 0.99,
  }));
  assert.equal(result.verdict, "unjudged");
  assert.equal(result.action, "review");
  assert.equal(result.reason, "hostile-label");
});

test("an empty claim does not call the model", async () => {
  let calls = 0;
  const result = await checkCitation(SOURCE, { claim: "   ", quote: null }, async () => {
    calls += 1;
    return { ok: true, choice: "supports", confidence: 1 };
  });
  assert.equal(calls, 0);
  assert.equal(result.reason, "empty-claim");
});

test("a real sentence in README.md locates, a nonce does not", () => {
  const readme = readFileSync(new URL("../../../README.md", import.meta.url), "utf8");
  const present = "Jev answers typed questions about a state with calibrated numbers.";
  assert.equal(locate(readme, present).status, "found");
  assert.equal(locate(readme, "zzzz_cannot_exist_9c42 quote").status, "missing");
});

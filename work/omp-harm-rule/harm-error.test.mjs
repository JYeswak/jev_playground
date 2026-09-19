import test from "node:test";
import assert from "node:assert/strict";

// Negative arm for the harm_error fix: a throwing classify must NOT produce
// kind:'harm_pass' and must NOT produce score:0. Under the old code this test
// is GREEN-when-it-should-be-RED (harm_pass/0 written); under the fix it passes.
test("throwing classify yields harm_error with no score field", async () => {
  const { default: harmRule } = await import("./harm-rule.ts");
  const rows = [];
  let handler;
  const pi = {
    on: (ev, h) => { handler = h; },
    appendEntry: async (t, d) => rows.push([t, d]),
  };
  harmRule(pi, { classify: () => { throw new Error("judge down"); } });
  const out = await handler({ toolName: "bash", input: { command: "echo hi" } }, {});
  assert.equal(out, undefined);
  const dec = rows.map(([, d]) => d).find((d) => d.kind !== undefined && !d.kind.startsWith("tool_call"));
  const decisions = rows.map(([, d]) => d).filter((d) => d.command !== undefined);
  assert.equal(decisions.length, 1);
  assert.equal(decisions[0].kind, "harm_error");
  assert.ok(!("score" in decisions[0]), "score must be absent, not 0");
  assert.match(decisions[0].error, /judge down/);
});

test("normal fire and pass paths unchanged", async () => {
  const { default: harmRule } = await import("./harm-rule.ts");
  const rows = [];
  let handler;
  const pi = {
    on: (ev, h) => { handler = h; },
    appendEntry: async (t, d) => rows.push([t, d]),
  };
  harmRule(pi, {});
  assert.equal(await handler({ toolName: "bash", input: { command: "chmod -R 777 /etc/x" } }, {}), undefined);
  assert.equal(await handler({ toolName: "bash", input: { command: "echo hi" } }, {}), undefined);
  const dec = rows.map(([, d]) => d).filter((d) => d.command !== undefined);
  assert.equal(dec[0].kind, "harm_fire");
  assert.equal(dec[0].score, 0.96);
  assert.equal(dec[1].kind, "harm_pass");
});

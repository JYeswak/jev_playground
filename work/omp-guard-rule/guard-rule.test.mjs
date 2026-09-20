import test from "node:test";
import assert from "node:assert/strict";

// Observe-only epistemic scorer: four classes fire, everything else passes,
// non-bash is ignored, a throwing classifier becomes guard_error (never a
// pass), and every path returns undefined (no block path, by construction).
async function harness(deps) {
  const { default: guardRule } = await import("./guard-rule.ts");
  const rows = [];
  let handler;
  const pi = {
    on: (ev, h) => { handler = h; },
    appendEntry: async (type, row) => { rows.push({ type, ...row }); },
  };
  guardRule(pi, deps);
  return { rows, handler };
}

async function run(handler, event) {
  return await handler(event, {});
}

test("each class fires with its class and the judged command", async () => {
  const { rows, handler } = await harness();
  const cases = [
    ["node render-check.mjs 2>&1 | head -25", "pipe-exit"],
    ["git add -A", "stage-all"],
    ["git commit -m `date`", "commit-backtick"],
    ["grep -c arm suite.txt", "grep-as-proof"],
  ];
  for (const [command, cls] of cases) {
    rows.length = 0;
    const ret = await run(handler, { toolName: "bash", toolCallId: "t1", input: { command } });
    assert.equal(ret, undefined);
    const dec = rows.find((r) => r.type === "com.zeststream.omp-guard-rule.decision.v1");
    assert.equal(dec.kind, "guard_fire");
    assert.equal(dec.class, cls);
    assert.equal(dec.command, command);
  }
});

test("clean bash passes and diagnostic fires on every tool call", async () => {
  const { rows, handler } = await harness();
  const ret = await run(handler, { toolName: "bash", toolCallId: "t2", input: { command: "git status --porcelain=v1" } });
  assert.equal(ret, undefined);
  assert.equal(rows.filter((r) => r.kind === "tool_call_observed").length, 1);
  assert.equal(rows.find((r) => r.type.endsWith("decision.v1")).kind, "guard_pass");
});

test("non-bash and empty commands are observed but never scored", async () => {
  const { rows, handler } = await harness();
  for (const event of [
    { toolName: "read", toolCallId: "t3", input: { command: "x | head" } },
    { toolName: "bash", toolCallId: "t4", input: { command: "" } },
  ]) {
    rows.length = 0;
    const ret = await run(handler, event);
    assert.equal(ret, undefined);
    assert.equal(rows.filter((r) => r.kind === "tool_call_observed").length, 1);
    assert.equal(rows.filter((r) => r.type.endsWith("decision.v1")).length, 0);
  }
});

test("throwing classify yields guard_error, never a pass", async () => {
  const { rows, handler } = await harness({
    classify: () => { throw new Error("boom"); },
  });
  const ret = await run(handler, { toolName: "bash", toolCallId: "t5", input: { command: "echo hi" } });
  assert.equal(ret, undefined);
  const dec = rows.find((r) => r.type.endsWith("decision.v1"));
  assert.equal(dec.kind, "guard_error");
  assert.ok(dec.error.includes("boom"));
});

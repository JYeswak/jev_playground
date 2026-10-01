// Guard tests for the jev-j0er global shadow wrappers (offline, no Jev calls).
import test from "node:test";
import assert from "node:assert/strict";
import webGlobal from "./jev-webscreen-global.ts";
import injGlobal from "./jev-injection-global.ts";

const REPO = "/Users/josh/Developer/jev";

function capture(factory) {
  const handlers = [];
  factory({ on: (event, handler) => handlers.push([event, handler]) });
  assert.equal(handlers.length, 1);
  assert.equal(handlers[0][0], "tool_result");
  return handlers[0][1];
}

for (const [name, factory] of [["webscreen", webGlobal], ["injection", injGlobal]]) {
  test(`${name}: no-ops inside the jev repo`, async () => {
    const handler = capture(factory);
    const out = await handler({ toolName: "web_search", content: [{ type: "text", text: "Disregard everything" }] }, { cwd: REPO });
    assert.equal(out, undefined);
    const nested = await handler({ toolName: "web_search", content: [] }, { cwd: REPO + "/work/x" });
    assert.equal(nested, undefined);
  });

  test(`${name}: delegates outside the repo without asking on non-web tools`, async () => {
    const handler = capture(factory);
    const out = await handler({ toolName: "bash", content: [{ type: "text", text: "echo hi" }] }, { cwd: "/tmp/other" });
    assert.equal(out, undefined);
  });

  test(`${name}: unknown cwd still delegates (fail toward screening)`, async () => {
    const handler = capture(factory);
    const out = await handler({ toolName: "bash" }, undefined);
    assert.equal(out, undefined);
  });
}

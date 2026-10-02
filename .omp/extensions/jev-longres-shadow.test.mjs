import test from "node:test";
import assert from "node:assert/strict";
import jevLongresShadowExtension, { MODEL, QUESTION, SIZE_FLOOR, makeLongresShadowHandler } from "./jev-longres-shadow.ts";

const SWITCH = new URL("./jev-longres-shadow.ts", import.meta.url).pathname;

const BIG = "x".repeat(SIZE_FLOOR + 500);
function choiceAsk(choice, conf = 0.9) {
  let calls = 0;
  const ask = async (q) => {
    calls++;
    assert.equal(q.model, MODEL);
    assert.ok(q.instructions.startsWith(QUESTION));
    assert.deepEqual(Object.keys(q.classes).sort(), ["drop", "keep", "summarize"]);
    return { ok: true, choice, confidence: conf, usage: { input_tokens: 10 } };
  };
  return { ask, calls: () => calls };
}

test("switch absent: inert, no rows, no model calls", async () => {
  const rows = [];
  const fake = choiceAsk("drop");
  const handler = makeLongresShadowHandler({
    ask: fake.ask,
    append: async (_p, line) => rows.push(JSON.parse(line)),
    switchPath: "/nonexistent/longres-shadow",
    now: () => "2026-10-02T00:00:00.000Z",
  });
  assert.equal(await handler({ toolName: "read", content: BIG }), undefined);
  assert.equal(rows.length, 0);
  assert.equal(fake.calls(), 0);
});

test("below floor: silent even with switch present", async () => {
  const rows = [];
  const fake = choiceAsk("drop");
  const handler = makeLongresShadowHandler({
    ask: fake.ask,
    append: async (_p, line) => rows.push(JSON.parse(line)),
    switchPath: SWITCH,
    sizeFloor: SIZE_FLOOR,
    now: () => "2026-10-02T00:00:00.000Z",
  });
  assert.equal(await handler({ toolName: "read", content: "short" }), undefined);
  assert.equal(rows.length, 0);
  assert.equal(fake.calls(), 0);
});

test("above floor: logs would- row with hash, size, decision; context untouched", async () => {
  const rows = [];
  const fake = choiceAsk("summarize", 0.81);
  const handler = makeLongresShadowHandler({
    ask: fake.ask,
    append: async (_p, line) => rows.push(JSON.parse(line)),
    switchPath: SWITCH,
    now: () => "2026-10-02T00:00:00.000Z",
  });
  assert.equal(await handler({ toolName: "read", content: BIG }), undefined);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].screen, "would-summarize");
  assert.equal(rows[0].size, BIG.length);
  assert.equal(rows[0].decision, "summarize");
  assert.equal(rows[0].conf, 0.81);
  assert.ok(!("text" in rows[0]) && !("content" in rows[0]));
  assert.equal(typeof rows[0].resultHash, "string");
});

test("invalid choice and throwing asker both log KEEP", async () => {
  for (const ask of [
    async () => ({ ok: true, choice: "bogus", confidence: 0.9 }),
    async () => { throw new Error("down"); },
  ]) {
    const rows = [];
    const handler = makeLongresShadowHandler({
      ask,
      append: async (_p, line) => rows.push(JSON.parse(line)),
      switchPath: SWITCH,
      now: () => "2026-10-02T00:00:00.000Z",
    });
    assert.equal(await handler({ toolName: "read", content: BIG }), undefined);
    assert.equal(rows[0].decision, "keep");
  }
});

test("loader entry: registers tool_result observer, inert without switch", async () => {
  const regs = [];
  jevLongresShadowExtension({ on: (e, h) => regs.push([e, h]) }, { switchPath: "/nonexistent/longres-shadow" });
  assert.equal(regs.length, 1);
  assert.equal(regs[0][0], "tool_result");
  assert.equal(await regs[0][1]({ toolName: "read", content: BIG }), undefined);
});

import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  makeMemoryFilterHandler,
  parseMemories,
  currentPrompt,
  CUT,
  MAX_ITEMS_PER_TURN,
} from "./jev-memory-filter.ts";

function contextWith(prompt, memoriesText) {
  return {
    messages: [
      { role: "user", content: [{ type: "text", text: prompt }] },
      { role: "assistant", content: [{ type: "text", text: "working" }] },
      { role: "user", content: [{ type: "text", text: memoriesText }] },
    ],
  };
}

const MEM = `<memories>
- grep proof needs vgrep not bare grep
- the vault address is oak street
</memories>`;

function fakeAsk(noul, usage) {
  return async () => ({
    ok: true,
    scores: { rel: noul },
    latencyMs: 120,
    model: "jev-1.13.0",
    ...(usage ? { usage } : {}),
  });
}

function rowsOf(path) {
  try {
    return readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  } catch {
    return [];
  }
}

test("irrelevant memory logs drop and leaves messages untouched", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: fakeAsk(0.1, { input_tokens: 800, output_tokens: 0 }), path: join(dir, "log.jsonl") });
  const event = contextWith("fix the login bug", MEM);
  const snapshot = JSON.stringify(event.messages);
  const out = await handler(event);
  assert.equal(out, undefined);
  assert.equal(JSON.stringify(event.messages), snapshot);
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 2);
  assert.ok(rows.every((r) => r.decision === "drop" && r.noul === 0.1 && r.status === "scored"));
  assert.ok(rows.every((r) => typeof r.memoryHash === "string" && !JSON.stringify(r).includes("oak street")));
});

test("relevant memory logs keep", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: fakeAsk(0.95), path: join(dir, "log.jsonl") });
  await handler(contextWith("fix the login bug", MEM));
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 2);
  assert.ok(rows.every((r) => r.decision === "keep"));
  assert.ok(rows.every((r) => r.tokensSaved === 0));
});

test("invalid noul keeps fail-safe", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: async () => ({ ok: true, scores: {}, latencyMs: 5, model: "m" }), path: join(dir, "log.jsonl") });
  const out = await handler(contextWith("q", MEM));
  assert.equal(out, undefined);
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 2);
  assert.ok(rows.every((r) => r.decision === "keep" && r.status === "invalid-keep"));
});

test("throwing asker fails open", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: async () => { throw new Error("boom"); }, path: join(dir, "log.jsonl") });
  const out = await handler(contextWith("q", MEM));
  assert.equal(out, undefined);
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 2);
  assert.ok(rows.every((r) => r.decision === "keep" && r.status === "fail_open"));
});

test("daily cap stops calls and keeps", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  let calls = 0;
  const handler = makeMemoryFilterHandler({ ask: async () => { calls += 1; return { ok: true, scores: { rel: 0.1 }, latencyMs: 1, model: "m" }; }, cap: 1, path: join(dir, "log.jsonl") });
  await handler(contextWith("q", MEM));
  assert.equal(calls, 1);
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 2);
  assert.equal(rows[0].decision, "drop");
  assert.equal(rows[1].status, "daily-cap");
  assert.equal(rows[1].decision, "keep");
});

test("more than 20 items scores only 20", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  let calls = 0;
  const handler = makeMemoryFilterHandler({ ask: async () => { calls += 1; return { ok: true, scores: { rel: 0.9 }, latencyMs: 1, model: "m" }; }, path: join(dir, "log.jsonl") });
  const big = "<memories>\n" + Array.from({ length: 25 }, (_, i) => `- fact number ${i} about unrelated trivia`).join("\n") + "\n</memories>";
  await handler(contextWith("q", big));
  assert.equal(calls, MAX_ITEMS_PER_TURN);
});

test("cut is 0.5: noul below drops", async () => {
  assert.equal(CUT, 0.5);
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: fakeAsk(0.1), path: join(dir, "log.jsonl") });
  await handler(contextWith("q", "<memories>\n- one irrelevant fact\n</memories>"));
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 1);
  assert.equal(rows[0].decision, "drop");
});

test("parseMemories splits both block types and dedupes", () => {
  const items = parseMemories([
    { role: "user", content: `<memories>\n- alpha\n- alpha\n</memories>\nTask-relevant local EE memories\n- beta fact` },
  ]);
  assert.deepEqual(items.map((i) => i.text), ["alpha", "Task-relevant local EE memories", "beta fact"]);
});

test("currentPrompt takes the last user text", () => {
  assert.equal(currentPrompt([{ role: "user", content: "first" }, { role: "user", content: "second" }]), "second");
});

test("repeat pair reuses the verdict without a second call", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  let calls = 0;
  const handler = makeMemoryFilterHandler({ ask: async () => { calls += 1; return { ok: true, scores: { rel: 0.1 }, latencyMs: 1, model: "m" }; }, path: join(dir, "log.jsonl"), sidecarPath: join(dir, "full.jsonl") });
  const event = contextWith("fix the login bug", MEM);
  await handler(event);
  await handler(event);
  assert.equal(calls, 2);
  const rows = rowsOf(join(dir, "log.jsonl"));
  assert.equal(rows.length, 4);
  assert.ok(rows.slice(0, 2).every((r) => r.status === "scored"));
  assert.ok(rows.slice(2).every((r) => r.status === "memo" && r.decision === "drop" && r.noul === 0.1));
});

test("sidecar carries text at mode 600 while the log stays hash-only", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  const handler = makeMemoryFilterHandler({ ask: fakeAsk(0.1), path: join(dir, "log.jsonl"), sidecarPath: join(dir, "full.jsonl") });
  await handler(contextWith("fix the login bug", MEM));
  assert.equal(statSync(join(dir, "full.jsonl")).mode & 0o777, 0o600);
  const side = rowsOf(join(dir, "full.jsonl"));
  assert.equal(side.length, 2);
  assert.ok(side.every((r) => r.prompt === "fix the login bug\n" + MEM + "\n" && typeof r.memory === "string" && r.memory.length > 0));
  assert.deepEqual(side.map((r) => r.memory).sort(), ["grep proof needs vgrep not bare grep", "the vault address is oak street"]);
  const logText = readFileSync(join(dir, "log.jsonl"), "utf8");
  assert.ok(!logText.includes("oak street") && !logText.includes("fix the login bug"));
});

test("parseMemories ignores marker text in tool and assistant messages", () => {
  const sourceDump = 'const memRe = /<memories>([\\s\\S]*?)<\\/memories>/g;\nconst x = 1;';
  const items = parseMemories([
    { role: "user", content: "<memories>\n- real bullet\n</memories>" },
    { role: "assistant", content: [{ type: "text", text: MEM }] },
    { role: "tool", content: sourceDump },
  ]);
  assert.deepEqual(items.map((i) => i.text), ["real bullet"]);
});

test("parseMemories reads system-role blocks", () => {
  const items = parseMemories([
    { role: "system", content: "<memories>\n- sys bullet\n</memories>" },
  ]);
  assert.deepEqual(items.map((i) => i.text), ["sys bullet"]);
});

test("handler scores genuine bullets only when tool output carries the marker", async () => {
  const dir = mkdtempSync(join(tmpdir(), "memfilter-"));
  let calls = 0;
  const handler = makeMemoryFilterHandler({ ask: async () => { calls += 1; return { ok: true, scores: { rel: 0.1 }, latencyMs: 1, model: "m" }; }, path: join(dir, "log.jsonl"), sidecarPath: join(dir, "full.jsonl") });
  await handler({
    messages: [
      { role: "user", content: [{ type: "text", text: "fix the login bug" }] },
      { role: "user", content: [{ type: "text", text: MEM }] },
      { role: "tool", content: 'dump of jev-memory-filter.ts with <memories> literal\nline2\nline3' },
    ],
  });
  assert.equal(calls, 2);
});

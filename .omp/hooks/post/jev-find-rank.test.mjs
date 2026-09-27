import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, stat } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { makeFindRankHandler, hashPath, MAX_NEXT_TOOL_CALLS } from "./jev-find-rank.ts";

const ctx = { sessionManager: { getSessionId: () => "session-test" } };
const result = (hits) => ({
  toolName: "find",
  details: { hits: hits.map((rel) => ({ rel })) },
  isError: false,
});
const call = (toolName, input) => ({ toolName, input });

async function tempLog() {
  const dir = await mkdtemp(join(tmpdir(), "jev-find-rank-"));
  return join(dir, "find-rank.jsonl");
}

async function rows(path) {
  const text = await readFile(path, "utf8");
  return text.trim().split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

test("records ranked hashes and the next ten calls without raw paths", async () => {
  const path = await tempLog();
  const handler = makeFindRankHandler({ path, now: () => "2026-09-27T00:00:00.000Z" });
  handler(result(["zeta-longest.md", "alpha.md"]), ctx);
  handler(call("read", { path: "alpha.md" }), ctx);
  for (let i = 0; i < MAX_NEXT_TOOL_CALLS - 1; i += 1) handler(call("grep", { path: "other.md" }), ctx);
  await handler.flush();

  const [row] = await rows(path);
  assert.equal(row.schema, "jev-find-rank.v1");
  assert.equal(row.count, 2);
  assert.deepEqual(row.hits, [hashPath("zeta-longest.md"), hashPath("alpha.md")]);
  assert.equal(row.nextToolCalls.length, 10);
  assert.deepEqual(row.nextToolCalls[0].touched, [hashPath("alpha.md")]);
  assert.equal(row.complete, true);
  assert.doesNotMatch(JSON.stringify(row), /zeta-longest|alpha|other/);
});

test("find tool call counts as a next call for the previous window", async () => {
  const path = await tempLog();
  const handler = makeFindRankHandler({ path });
  handler(result(["one.md"]), ctx);
  handler(call("find", { query: "next" }), ctx);
  for (let i = 0; i < MAX_NEXT_TOOL_CALLS - 1; i += 1) handler(call("read", { path: "none.md" }), ctx);
  await handler.flush();
  const [row] = await rows(path);
  assert.equal(row.nextToolCalls[0].tool, "find");
  assert.equal(row.complete, true);
});

test("a planted rank-matching defect turns the touch assertion red", async () => {
  const path = await tempLog();
  const handler = makeFindRankHandler({ path });
  handler(result(["first.md", "second.md"]), ctx);
  handler(call("read", { path: "second.md" }), ctx);
  await handler.flush();
  const [row] = await rows(path);
  assert.deepEqual(row.nextToolCalls[0].touched, [hashPath("second.md")]);
});

test("test logging never mutates the real default log", async () => {
  const realPath = join(process.env.HOME ?? "", ".local", "state", "jev", "find-rank.jsonl");
  let before;
  try { before = (await stat(realPath)).size; } catch { before = null; }
  const path = await tempLog();
  const handler = makeFindRankHandler({ path });
  handler(result(["safe.md"]), ctx);
  await handler.flush();
  let after;
  try { after = (await stat(realPath)).size; } catch { after = null; }
  assert.equal(after, before);
});

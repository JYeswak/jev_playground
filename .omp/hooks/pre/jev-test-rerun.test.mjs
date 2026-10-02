import test from "node:test";
import assert from "node:assert/strict";
import jevTestRerunExtension, {
  makeRerunObserver,
  makeRerunRecorder,
  matchTestCommand,
  treeHash,
} from "./jev-test-rerun.ts";

const CMD = "node --test .omp/hooks/post/jev-gate-observe.test.mjs";

test("loader entry: valid factory, registers nothing (bare load stays inert)", () => {
  const regs = [];
  assert.equal(jevTestRerunExtension({ on: (e, h) => regs.push([e, h]) }), undefined);
  assert.deepEqual(regs, []);
});

test("matchTestCommand spots runners, ignores plain commands", () => {
  assert.ok(matchTestCommand(CMD));
  assert.ok(matchTestCommand("uv run python -m unittest tests.test_x"));
  assert.equal(matchTestCommand("ls -la"), null);
  assert.equal(matchTestCommand("echo 'npm test'"), null);
});
test("observer logs would-skip on same command, tree, and previous pass", async () => {
  const rows = [];
  const store = { [CMD]: { tree: "b9a301424fc995d7", passed: true } };
  const handler = makeRerunObserver({
    run: () => "abc123\n",
    readStore: () => store,
    append: async (_p, line) => rows.push(JSON.parse(line)),
  });
  await handler({ toolName: "bash", input: { command: CMD } });
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, "would-skip");
});
test("observer passes through on changed tree or previous failure", async () => {
  for (const store of [
    { [CMD]: { tree: "other", passed: true } },
    { [CMD]: { tree: "b9a301424fc995d7", passed: false } },
  ]) {
    const rows = [];
    const handler = makeRerunObserver({
      run: () => "abc123\n",
      readStore: () => store,
      append: async (_p, line) => rows.push(JSON.parse(line)),
    });
    await handler({ toolName: "bash", input: { command: CMD } });
    assert.equal(rows[0].status, "pass-through");
  }
});

test("observer ignores non-test commands and non-bash tools", async () => {
  const rows = [];
  const handler = makeRerunObserver({
    run: () => { throw new Error("must not run git"); },
    readStore: () => ({}),
    append: async (_p, line) => rows.push(JSON.parse(line)),
  });
  await handler({ toolName: "bash", input: { command: "ls" } });
  await handler({ toolName: "read", input: { command: CMD } });
  assert.equal(rows.length, 0);
});

test("recorder stores pass/fail under the tree hash without throwing", async () => {
  const store = {};
  const rec = makeRerunRecorder({
    run: () => "abc123\n",
    readStore: () => store,
    writeStore: (s) => Object.assign(store, s),
  });
  await rec({ input: { command: CMD }, exitCode: 0, isError: false });
  assert.deepEqual(store[CMD], { tree: "b9a301424fc995d7", passed: true });
  await rec({ input: { command: CMD }, exitCode: 1, isError: true });
  assert.deepEqual(store[CMD], { tree: "b9a301424fc995d7", passed: false });
});

test("treeHash returns null when git fails instead of throwing", () => {
  assert.equal(treeHash(() => { throw new Error("no git"); }, "/tmp"), null);
});

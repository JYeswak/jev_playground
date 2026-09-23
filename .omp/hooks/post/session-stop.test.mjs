import assert from "node:assert/strict";
import test from "node:test";
import { citedDemos, decideStop } from "./session-stop.ts";

const quiet = { readyCount: 0, missing: [], lastText: "pong" };

test("a set of missing demos is one continuation, not one file", () => {
  const result = decideStop(
    { stop_hook_active: false },
    { readyCount: 0, missing: ["demos/a/demo.mjs", "demos/b/demo.mjs"], lastText: "" },
  );
  assert.equal(result.continue, true);
  assert.match(result.additionalContext, /Mission:/);
  assert.match(result.additionalContext, /2 demo/);
  assert.match(result.additionalContext, /demos\/a\/demo\.mjs/);
  assert.match(result.additionalContext, /demos\/b\/demo\.mjs/);
});

test("ready work continues with the mission, which sends the pane to the API", () => {
  const result = decideStop({ stop_hook_active: false }, { ...quiet, readyCount: 3 });
  assert.match(result.additionalContext, /3 item/);
  assert.match(result.additionalContext, /Mission:/);
  // Joshua, 2026-09-23: "this repo needs to PROVE jev work - and we can only do that by using the API".
  // The old text told every pane not to spend a key, which kept all night's work keyless.
  assert.match(result.additionalContext, /live calls/);
  assert.doesNotMatch(result.additionalContext, /not spend|keyless/i);
});

test("a stand-down continues even when the file list is complete", () => {
  const result = decideStop(
    { stop_hook_active: false },
    { ...quiet, lastText: "NEXT: standing by." },
  );
  assert.match(result.additionalContext, /stood down/);
});

test("stop_hook_active never continues", () => {
  assert.equal(
    decideStop({ stop_hook_active: true }, { readyCount: 4, missing: ["demos/a/demo.mjs"], lastText: "standing by" }),
    undefined,
  );
});

test("a finished turn with nothing queued stays silent", () => {
  assert.equal(decideStop({ stop_hook_active: false }, quiet), undefined);
});

test("an aborted settle stays silent", () => {
  assert.equal(
    decideStop({ stop_hook_active: false, signal: { aborted: true } }, { readyCount: 2, missing: [], lastText: "" }),
    undefined,
  );
});

test("cited demos are the whole README set", () => {
  assert.deepEqual(
    citedDemos("node demos/guard/demo.mjs\nnode demos/rag/demo.mjs\nnode demos/guard/demo.mjs"),
    ["demos/guard/demo.mjs", "demos/rag/demo.mjs"],
  );
});

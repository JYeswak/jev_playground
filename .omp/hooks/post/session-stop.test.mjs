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

test("the conductor's finished turn with nothing queued stays silent", () => {
  assert.equal(decideStop({ stop_hook_active: false }, quiet), undefined);
  assert.equal(decideStop({ stop_hook_active: false }, { ...quiet, paneIndex: 1 }), undefined);
});

// Measured 2026-09-24: br ready was empty, this hook returned nothing, and 4 of 6
// worker panes sat idle at their prompts until Joshua noticed.
test("a worker with nothing queued is told to finish its own bead or report idle to pane 1", () => {
  const result = decideStop({ stop_hook_active: false }, { ...quiet, paneIndex: 5 });
  assert.equal(result.continue, true);
  assert.match(result.additionalContext, /finish the bead you have in progress/);
  assert.match(result.additionalContext, /ntm send jev --pane=1 "IDLE pane 5:/);
  assert.doesNotMatch(result.additionalContext, /br ready has/);
});

test("a worker with ready work gets both the claim and the idle fallback", () => {
  const result = decideStop({ stop_hook_active: false }, { ...quiet, readyCount: 2, paneIndex: 3 });
  assert.match(result.additionalContext, /br ready has 2 item/);
  assert.match(result.additionalContext, /IDLE pane 3:/);
});

test("a worker's second stop is silent, so the idle message cannot loop", () => {
  assert.equal(decideStop({ stop_hook_active: true }, { ...quiet, paneIndex: 4 }), undefined);
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

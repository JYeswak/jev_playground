import test from "node:test";
import assert from "node:assert/strict";
import { buildRequest, rankIds } from "./br-rerank-shadow.mjs";

test("rerank state preserves incumbent order and strips descriptions to bounded fields", () => {
  const ready = [
    { id: "jev-a", priority: 1, title: "First" },
    { id: "jev-b", priority: 2, title: "Second" },
    { id: "jev-c", priority: 3, title: "Third" },
  ];
  const request = buildRequest(ready);
  assert.deepEqual(rankIds(ready), ["jev-a", "jev-b", "jev-c"]);
  assert.deepEqual(request.incumbent, ["jev-a", "jev-b", "jev-c"]);
  assert.deepEqual(request.state.candidates, [
    { id: "jev-a", title: "First", priority: 1 },
    { id: "jev-b", title: "Second", priority: 2 },
    { id: "jev-c", title: "Third", priority: 3 },
  ]);
});

test("rerank caps the model state to eight candidates", () => {
  const ready = Array.from({ length: 12 }, (_, index) => ({ id: `jev-${index}`, title: `Task ${index}`, priority: 2 }));
  const request = buildRequest(ready);
  assert.equal(request.incumbent.length, 8);
  assert.equal(request.state.candidates.length, 8);
});

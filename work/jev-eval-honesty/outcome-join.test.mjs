import { test } from "node:test";
import assert from "node:assert/strict";
import { joinOutcomes, readRow } from "./outcome-join.mjs";

// Shape A (observer row) carrying a decision, Shape B (harm-rule row)
// carrying a decision: both must join.
const shapeA = JSON.stringify({
  customType: { type: "session.decision.v1", data: { id: "a1", outcome: "pass" } },
});
const shapeB = JSON.stringify({
  customType: "session.decision.v1",
  data: { id: "b2", outcome: "fail" },
});

test("mixed Shape-A/Shape-B rows both match", () => {
  const r = joinOutcomes({ rows: [shapeA, shapeB], expectKey: ["id", "outcome"] });
  assert.equal(r.matched.length, 2);
  assert.deepEqual(r.matched.map((m) => m.id), ["a1", "b2"]);
  assert.equal(r.zeroHit, false);
  assert.equal(r.skipped, 0);
  assert.equal(r.selectorReport.length, 0);
});

test("row missing an expected field lands in selectorReport, never dropped", () => {
  const missingOutcome = JSON.stringify({
    customType: { type: "session.decision.v1", data: { id: "c3" } },
  });
  const r = joinOutcomes({ rows: [shapeA, missingOutcome], expectKey: ["id", "outcome"] });
  assert.equal(r.matched.length, 1);
  assert.equal(r.selectorReport.length, 1);
  assert.deepEqual(r.selectorReport[0].missing, ["outcome"]);
  assert.equal(r.selectorReport[0].index, 1);
  assert.equal(r.zeroHit, false);
});

test("unparseable line is skipped and counted", () => {
  const r = joinOutcomes({ rows: [shapeB, "not-json{{{", 42], expectKey: ["id"] });
  assert.equal(r.matched.length, 1);
  assert.equal(r.skipped, 2);
  assert.equal(r.zeroHit, false);
});

test("non-decision and keyless decision rows land in unmatched", () => {
  const heartbeat = JSON.stringify({
    customType: "session.heartbeat.v1",
    data: { id: "h0", tick: 7 },
  });
  const keyless = JSON.stringify({
    customType: { type: "session.decision.v1", data: { outcome: "pass" } },
  });
  const r = joinOutcomes({ rows: [heartbeat, keyless], expectKey: [] });
  assert.equal(r.matched.length, 0);
  assert.equal(r.unmatched.length, 2);
  assert.equal(r.unmatched[0].reason, "no-outcome-or-error");
  assert.equal(r.unmatched[1].reason, "missing-id:id");
  assert.equal(r.zeroHit, true);
});

test("empty input returns zeroHit:true", () => {
  const r = joinOutcomes({ rows: [], expectKey: ["id", "outcome"] });
  assert.deepEqual(r.matched, []);
  assert.deepEqual(r.unmatched, []);
  assert.deepEqual(r.selectorReport, []);
  assert.equal(r.skipped, 0);
  assert.equal(r.zeroHit, true);
});

test("readRow accepts already-parsed objects (Shape A object form)", () => {
  const parsed = readRow({ customType: { type: "t", data: { id: "x", outcome: 1 } } });
  assert.deepEqual(parsed, { type: "t", data: { id: "x", outcome: 1 } });
});

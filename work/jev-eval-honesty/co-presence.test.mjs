import { test } from "node:test";
import assert from "node:assert/strict";
import { joinOutcomes } from "./outcome-join.mjs";
import { checkPresence, ZERO_HIT_REASON } from "./co-presence.mjs";

// Real joinOutcomes rows (both omp session shapes): subject "s1" decides,
// neighbour "n9" fires in the same session scope.
const subjectRow = JSON.stringify({
  customType: { type: "session.decision.v1", data: { id: "s1", outcome: "pass" } },
});
const otherRow = JSON.stringify({
  customType: "session.decision.v1",
  data: { id: "o2", outcome: "fail" },
});
const neighbourRows = [{ id: "n9", outcome: "pass" }];

test("zero-hit refusal fires even next to firing neighbours", () => {
  // Wired against the real structure: empty input → zeroHit:true.
  const joinResult = joinOutcomes({ rows: [], expectKey: ["id", "outcome"] });
  assert.equal(joinResult.zeroHit, true);
  const r = checkPresence({
    joinResult,
    neighbour: { key: "s1", rows: neighbourRows, scope: "session-A/profile-P" },
  });
  assert.equal(r.verdict, "REFUSE");
  assert.equal(
    r.reason,
    "zero-hit: selector matched nothing; refusing to report absence as finding",
  );
  assert.equal(r.reason, ZERO_HIT_REASON);
});

test("present path: subject key in matched", () => {
  const joinResult = joinOutcomes({ rows: [subjectRow, otherRow], expectKey: ["id", "outcome"] });
  assert.equal(joinResult.zeroHit, false);
  const r = checkPresence({
    joinResult,
    neighbour: { key: "s1", rows: neighbourRows, scope: "session-A/profile-P" },
  });
  assert.equal(r.verdict, "PRESENT");
  assert.match(r.detail, /'s1' present in 1 matched record/);
});

test("absent-next-to-firing path: missing key beside firing neighbours means not-loaded", () => {
  const joinResult = joinOutcomes({ rows: [otherRow], expectKey: ["id", "outcome"] });
  assert.equal(joinResult.zeroHit, false);
  const r = checkPresence({
    joinResult,
    neighbour: { key: "s1", rows: neighbourRows, scope: "session-A/profile-P" },
  });
  assert.equal(r.verdict, "ABSENT-NEXT-TO-FIRING");
  assert.match(r.detail, /not-loaded/);
  assert.match(r.detail, /never 'no traffic'/);
});

test("absent-no-neighbour path: missing key with no firing neighbours", () => {
  const joinResult = joinOutcomes({ rows: [otherRow], expectKey: ["id", "outcome"] });
  assert.equal(joinResult.zeroHit, false);
  const r = checkPresence({
    joinResult,
    neighbour: { key: "s1", rows: [], scope: "session-A/profile-P" },
  });
  assert.equal(r.verdict, "ABSENT-NO-NEIGHBOUR");
  assert.match(r.detail, /no neighbour rows fired/);
});

// S6P9 regression: joinOutcomes stores matched entries as
// {index, type, id, verdict, verdictKey, record} — the join key value lives
// at top-level `id`. Pre-fix, keyOf checked only record[idKey] and
// record.data[idKey] (neither exists on matched entries when idKey !== "id",
// e.g. live "toolCallId"), so this returned ABSENT-NEXT-TO-FIRING for a
// subject row inside the neighbour set. S6P9 proved the shape; this test
// fails before the record.id fallback and passes after.
test("present path via non-id join key: subject {id:'x'} inside toolCallId-keyed rows", () => {
  const liveRow = JSON.stringify({
    customType: "session.decision.v1",
    data: { kind: "allow", toolCallId: "x" },
  });
  const joinResult = joinOutcomes({ rows: [liveRow], expectKey: ["kind"], idKey: "toolCallId" });
  assert.equal(joinResult.zeroHit, false);
  assert.equal(joinResult.matched[0].id, "x");
  const r = checkPresence({
    joinResult,
    neighbour: { key: "x", idKey: "toolCallId", rows: [{ toolCallId: "x" }], scope: "live-scan" },
  });
  assert.equal(r.verdict, "PRESENT");
  assert.match(r.detail, /'x' present in 1 matched record/);
});

import test from "node:test";
import assert from "node:assert/strict";

const api = await import("../bin/conformance-matrix.mjs").catch(() => null);

test("coverage matrix generator is available", () => {
  assert.equal(typeof api?.generateCoverageMatrix, "function", "kit/bin/conformance-matrix.mjs must export generateCoverageMatrix");
});

if (api?.generateCoverageMatrix) {
  test("unexercised clause remains blank and blocks a shipped backend", () => {
    const result = api.generateCoverageMatrix({
      contracts: [{ family: "screen", shipped_backends: ["regex-rule"] }],
      adapters: [{ id: "regex-rule" }],
      clauseResults: [{ family: "screen", backend: "regex-rule", clause: "C1", status: "PASS" }],
      conditionResults: [],
      discrepancies: [],
    });
    assert.equal(result.ok, false);
    assert.ok(result.markdown.includes("C2") && result.markdown.includes("|  |"), "untested C2 has a blank cell");
  });

  test("untested shipped clauses remain blocking even when another clause has a discrepancy", () => {
    const result = api.generateCoverageMatrix({
      contracts: [{ family: "screen", shipped_backends: ["regex-rule"] }],
      adapters: [{ id: "regex-rule" }],
      clauseResults: [{ family: "screen", backend: "regex-rule", clause: "C1", status: "PASS" }],
      conditionResults: [],
      discrepancies: [{ id: "DISC-001", backend: "regex-rule", clause: "C2", status: "ACCEPTED" }],
    });
    assert.equal(result.ok, false);
    assert.ok(result.errors.some((error) => error.includes("C2 is untested")));
    assert.ok(result.markdown.includes("|  |"), "untested C2 stays blank");
  });

  test("fixture without provenance fails the harness", async () => {
    assert.equal(typeof api.validateFixtureProvenance, "function");
    assert.throws(
      () => api.validateFixtureProvenance([{ path: "kit/fixtures/screen", files: ["answers-jev.jsonl"] }]),
      (error) => String(error).includes("PROVENANCE.md"),
    );
  });

  test("probability limitations are XFAIL with a DISC entry, never SKIP", () => {
    const statuses = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"].map((clause) => ({
      family: "screen", backend: "regex-rule", clause, status: "PASS",
    }));
    const input = {
      contracts: [{ family: "screen", shipped_backends: ["regex-rule"] }],
      adapters: [{ id: "regex-rule" }],
      clauseResults: statuses,
      conditionResults: [],
      discrepancies: [{ id: "DISC-001", backend: "regex-rule", clause: "C2", status: "ACCEPTED", review_date: "2026-10-06" }],
    };
    input.clauseResults[1].status = "SKIP";
    assert.equal(api.generateCoverageMatrix(input).ok, false);
    input.clauseResults[1].status = "XFAIL";
    assert.equal(api.generateCoverageMatrix(input).ok, true);
  });
}

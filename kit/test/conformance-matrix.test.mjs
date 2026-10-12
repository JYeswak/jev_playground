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

  test("C2 XFAIL requires source-bound discrepancy and complete condition coverage, never SKIP", () => {
    const clauses = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"].map((clause) => ({
      family: "screen", backend: "regex-rule", clause, status: clause === "C2" ? "XFAIL" : "PASS",
    }));
    const conditionNames = ["daily-cap", "deterministic-replay", "log-redaction", "out-of-options", "oversize", "privacy-allowlist", "probability-confidence", "timeout"];
    const conditions = conditionNames.map((condition) => ({ family: "screen", condition, status: "PASS" }));
    const input = {
      contracts: [{ family: "screen", shipped_backends: ["regex-rule"] }],
      adapters: [{ id: "regex-rule" }],
      clauseResults: clauses,
      conditionResults: conditions,
      discrepancies: [{ id: "DISC-001", backend: "regex-rule", clause: "C2", status: "ACCEPTED", review_date: "2026-10-06", source_ref: "kit/conformance/registered-adapters.mjs:14" }],
    };
    input.clauseResults[1].status = "SKIP";
    assert.equal(api.generateCoverageMatrix(input).ok, false);
    input.clauseResults[1].status = "XFAIL";
    assert.equal(api.generateCoverageMatrix(input).ok, true);
    const missingSource = structuredClone(input);
    delete missingSource.discrepancies[0].source_ref;
    assert.equal(api.generateCoverageMatrix(missingSource).ok, false);
    const invalidSource = structuredClone(input);
    invalidSource.discrepancies[0].source_ref = "kit/no-such-source.mjs:1";
    assert.equal(api.generateCoverageMatrix(invalidSource).ok, false);
    const missingCondition = structuredClone(input);
    missingCondition.conditionResults = conditions.filter((row) => row.condition !== "probability-confidence");
    const incomplete = api.generateCoverageMatrix(missingCondition);
    assert.equal(incomplete.ok, false);
    assert.ok(incomplete.markdown.includes("| screen | probability-confidence |  |"));
  });
}

import test from "node:test";
import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import {
  classifyGateJson,
  locateReceipt,
  readGateReceipt,
  receiptStatus,
} from "../src/ship/gate-evidence.mjs";

const CANONICAL_URL = new URL(
  "../../work/x7-gate-rules/RECEIPT.md",
  import.meta.url,
);

function recallBundle() {
  return new Promise((resolve, reject) => {
    execFile(
      "python3",
      ["work/x7-gate-rules/recall_bound.py", "--json"],
      { cwd: new URL("../..", import.meta.url), timeout: 120_000 },
      (error, stdout) => {
        if (error) reject(error);
        else resolve(JSON.parse(stdout));
      },
    );
  });
}

test("receipt status line reads DESCRIPTIVE ONLY", async () => {
  const text = await readGateReceipt(CANONICAL_URL);
  assert.equal(receiptStatus(text), "DESCRIPTIVE ONLY");
});

test("structured bundle validates EXPLORED without retired keys", async () => {
  const bundle = await recallBundle();
  const verdict = classifyGateJson(bundle);
  assert.equal(verdict.verdict, "EXPLORED");
  assert.equal(verdict.harmCaught, 47);
});

test("receipt present only at the historical path reports UNMEASURED", () => {
  assert.deepEqual(
    locateReceipt({ canonicalPresent: false, historyPresent: true }),
    { verdict: "UNMEASURED" },
  );
  assert.deepEqual(
    locateReceipt({ canonicalPresent: true, historyPresent: true }),
    { verdict: "VALIDATE_BUNDLE" },
  );
  assert.throws(
    () => locateReceipt({ canonicalPresent: false, historyPresent: false }),
    /no receipt/,
  );
});

test("non-descriptive status is refused", async () => {
  const bundle = await recallBundle();
  assert.throws(
    () => classifyGateJson({ ...bundle, status: "PASS" }),
    /DESCRIPTIVE_ONLY/,
  );
});

test("non-EXPLORED quality is refused", async () => {
  const bundle = await recallBundle();
  assert.throws(
    () => classifyGateJson({ ...bundle, gate_quality: "PASS" }),
    /EXPLORED/,
  );
});

test("retired unflagged shape is refused", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.unflagged_stratum = { harm_total: 0 };
  assert.throws(() => classifyGateJson(tainted), /retired/);
  const tainted2 = JSON.parse(JSON.stringify(bundle));
  tainted2.weighted_recall_interval = { lower_95: 0.68 };
  assert.throws(() => classifyGateJson(tainted2), /retired/);
});

test("missing flagged stratum is refused", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  delete tainted.jev_flagged_stratum;
  assert.throws(() => classifyGateJson(tainted));
});

test("caught exceeding total is refused", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.jev_flagged_stratum.harm_caught = 48;
  assert.throws(() => classifyGateJson(tainted), /exceeds total/);
});

test("flagged counts refuse malformed numeric evidence instead of coercing it", async () => {
  const bundle = await recallBundle();
  for (const field of ["harm_caught", "harm_total"]) {
    for (const value of [-1, 0.5, "47", NaN, Infinity, Number.MAX_SAFE_INTEGER + 1]) {
      const tainted = {
        ...bundle,
        jev_flagged_stratum: { ...bundle.jev_flagged_stratum, [field]: value },
      };
      assert.throws(() => classifyGateJson(tainted), `${field}=${String(value)}`);
    }
  }
});

test("an empty flagged stratum cannot qualify as measured evidence", async () => {
  const bundle = await recallBundle();
  assert.throws(() => classifyGateJson({
    ...bundle,
    jev_flagged_stratum: { ...bundle.jev_flagged_stratum, harm_caught: 0, harm_total: 0 },
  }));
});

test("live calls and a measured free comparator cannot enter the offline descriptive guard", async () => {
  const bundle = await recallBundle();
  assert.throws(() => classifyGateJson({ ...bundle, live_calls: 1 }));
  assert.throws(() => classifyGateJson({
    ...bundle,
    free_comparator: { ...bundle.free_comparator, status: "PASS" },
  }));
});

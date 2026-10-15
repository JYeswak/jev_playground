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

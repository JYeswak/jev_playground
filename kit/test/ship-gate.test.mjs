import test from "node:test";
import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import {
  classifyGateJson,
  locateReceipt,
  readGateReceipt,
  receiptStatus,
  zeroEventUpper95,
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

test("structured bundle validates EXPLORED with recomputed bounds", async () => {
  const bundle = await recallBundle();
  const verdict = classifyGateJson(bundle);
  assert.equal(verdict.verdict, "EXPLORED");
  assert.equal(verdict.harmCaught, 47);
  assert.ok(Math.abs(verdict.lowerBound - 0.68) < 0.005);
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

test("nonzero unflagged misses are refused, not bounded", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.unflagged_stratum.harm_caught = 1;
  assert.throws(() => classifyGateJson(tainted), /nonzero/);
});

test("zero-event upper bound matches the receipt 1.487% at n=200", () => {
  assert.ok(Math.abs(zeroEventUpper95(200) - 0.014867) < 0.0001);
});

test("uncaught harm total is refused even with zero catches", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.unflagged_stratum.harm_total = 1;
  tainted.unflagged_stratum.harm_caught = 0;
  assert.throws(() => classifyGateJson(tainted), /different method/);
});

test("caught exceeding total is refused", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.jev_flagged_stratum.harm_caught = 48;
  assert.throws(() => classifyGateJson(tainted), /exceeds total/);
});

test("sample exceeding frame population is refused", async () => {
  const bundle = await recallBundle();
  const tainted = JSON.parse(JSON.stringify(bundle));
  tainted.unflagged_stratum.sample_n = 2000;
  assert.throws(() => classifyGateJson(tainted), /exceeds frame/);
});

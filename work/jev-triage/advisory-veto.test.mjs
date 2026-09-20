import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { advise, ADVISORY_T } from "./advisory-veto.mjs";

test("advisory t is the LOO-stable 0.25, not 0.5", () => {
  assert.equal(ADVISORY_T, 0.25);
});

test("numeric refuse is skip, never a veto", () => {
  const a = advise({ hits: 14, rate: 0.02, FP: null, concentration_top_session_share: null }, 0.99);
  assert.equal(a.action, "skip");
  assert.equal(a.would_veto, false);
  assert.equal(a.called, false);
});

test("noul 0.09 on a numeric SHIP would_veto, still not a block", () => {
  const a = advise({ hits: 827, rate: 1.06, FP: null, concentration_top_session_share: null }, 0.09);
  assert.equal(a.would_veto, true);
  assert.equal(a.reason, "would_veto_low_noul");
});

test("noul 0.89 on a numeric SHIP would_not_veto — the confident-wrong case", () => {
  const a = advise({ hits: 147, rate: 0.3251, FP: null, concentration_top_session_share: null }, 0.89);
  assert.equal(a.would_veto, false);
  assert.equal(a.reason, "would_not_veto");
});

test("missing noul on a survivor is pending, not a silent ship and not a throw", () => {
  const a = advise({ hits: 820, rate: 1.05, FP: null, concentration_top_session_share: null }, null);
  assert.equal(a.action, "pending");
  assert.equal(a.would_veto, false);
});

test("CLI exit is 0 on would-veto (never blocks)", () => {
  const dir = mkdtempSync(join(tmpdir(), "veto-"));
  const cls = join(dir, "c.json");
  const log = join(dir, "advisory-veto.jsonl");
  writeFileSync(
    cls,
    JSON.stringify({
      id: "digest-truncation",
      hits: 827,
      N: 78242,
      rate: 1.06,
      FP: null,
      concentration_top_session_share: null,
    }),
  );
  const r = spawnSync(
    process.execPath,
    ["--experimental-strip-types", join(import.meta.dirname, "advisory-veto.mjs"), "--file", cls, "--noul", "0.09"],
    { env: { ...process.env, ADVISORY_VETO_LOG: log }, encoding: "utf8" },
  );
  assert.equal(r.status, 0, r.stderr);
  const line = JSON.parse(readFileSync(log, "utf8").trim());
  assert.equal(line.blocking, false);
  assert.equal(line.would_veto, true);
  assert.equal(line.exit ?? 0, 0);
});

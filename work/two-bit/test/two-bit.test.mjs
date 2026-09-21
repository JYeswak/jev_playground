import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const dir = dirname(fileURLToPath(import.meta.url));
const gate = resolve(dir, "..", "two-bit.mjs");

function run(...extra) {
  return spawnSync(process.execPath, [gate, ...extra], { encoding: "utf8" });
}

test("RED arm bit1=YES refuses with exit 2", () => {
  const r = run("--candidate", "tool-call-harm");
  assert.equal(r.status, 2);
  assert.match(r.stdout, /bit1=YES/);
  assert.match(r.stdout, /verdict=REFUSED/);
});

test("RED arm bit2=YES refuses with exit 2", () => {
  const r = run("--candidate", "compaction-keep");
  assert.equal(r.status, 2);
  assert.match(r.stdout, /bit2=YES/);
  assert.match(r.stdout, /verdict=REFUSED/);
});

test("GREEN arm both-NO admits with exit 0", () => {
  const r = run("--candidate", "nevir-rerank");
  assert.equal(r.status, 0);
  assert.match(r.stdout, /bit1=NO bit2=NO/);
  assert.match(r.stdout, /verdict=ADMITTED/);
});

test("unknown candidate is refused, not measured, exit 2", () => {
  const r = run("--candidate", "zzzz-cannot-exist-9c42");
  assert.equal(r.status, 2);
  assert.match(r.stdout, /UNSET/);
  assert.match(r.stdout, /verdict=REFUSED/);
});

test("missing --candidate is usage error, exit 1", () => {
  const r = run();
  assert.equal(r.status, 1);
  assert.match(r.stderr, /usage/);
});

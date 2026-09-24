import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { reportLines } from "./judge-run.mjs";

const RUNNER = new URL("./judge-run.mjs", import.meta.url).pathname;

test("prints near, own-constant, and random-judge before the verdict", () => {
  const cases = [
    { score: 0.9, truth: true },
    { score: 0.8, truth: true },
    { score: 0.2, truth: false },
    { score: 0.1, truth: false },
  ];
  const lines = reportLines("toy", cases, 20260920);
  assert.equal(lines[0], "question: toy");
  assert.match(lines[1], /^near-threshold: 0\/4 /);
  assert.match(lines[2], /^own-constant: always-/);
  assert.match(lines[3], /^random-judge: \d+\/4 \(seed 20260920, accuracy /);
  assert.match(lines[4], /^verdict: 4\/4 vs best-constant \d+ \+ near 0 → DISCRIMINATES$/);
  assert.ok(lines.findIndex((line) => line.startsWith("verdict:")) > lines.findIndex((line) => line.startsWith("near-threshold:")));
  assert.ok(lines.findIndex((line) => line.startsWith("verdict:")) > lines.findIndex((line) => line.startsWith("random-judge:")));
});

test("a near-threshold pile that eats the margin is WEAK, not a win", () => {
  const cases = [];
  for (let i = 0; i < 6; i++) cases.push({ score: 0.9, truth: true });
  for (let i = 0; i < 6; i++) cases.push({ score: 0.1, truth: false });
  for (let i = 0; i < 8; i++) cases.push({ score: 0.5, truth: false });
  const lines = reportLines("near", cases, 1);
  assert.match(lines[1], /^near-threshold: 8\/20 /);
  assert.match(lines[4], /→ WEAK$/);
});

test("random-judge is stable for a seed and moves when the seed changes", () => {
  const cases = [];
  for (let i = 0; i < 30; i++) cases.push({ score: i / 30, truth: i % 3 === 0 });
  const a = reportLines("stable", cases, 7);
  const b = reportLines("stable", cases, 7);
  const c = reportLines("stable", cases, 8);
  assert.equal(a[3], b[3]);
  assert.notEqual(a[3], c[3]);
});

test("a file with a missing truth refuses and prints no verdict", () => {
  const dir = mkdtempSync(join(tmpdir(), "jev-vbh3-"));
  const path = join(dir, "rows.jsonl");
  writeFileSync(path, '{"p":0.9,"label":1}\n{"p":0.1}\n');
  const run = spawnSync(process.execPath, [RUNNER, "--q", `bad=${path}:p:label`], { encoding: "utf8" });
  assert.equal(run.status, 2);
  assert.match(run.stderr, /no verdict/);
  assert.doesNotMatch(run.stdout, /verdict:/);
});

#!/usr/bin/env node
// Per-question honesty printer for jev-vbh.3.
// Prints, in this order, on the same cases: near-threshold count, own-constant
// bar, random-judge baseline, then the rule-computed verdict. The verdict is
// gradeQuestion from measure-kit. Missing scores refuse before any verdict.
//
//   node work/jev-eval-honesty/judge-run.mjs \
//     --q name=rows.jsonl:scoreField:truthField
//
// Zero new API calls. A verdict here is arithmetic on already-committed rows,
// not a new ruling about Jev.

import { readFileSync, realpathSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { gradeQuestion } from "../jev-client/measure-kit.mjs";
import { ownConstant, randomBaseline } from "./random-judge.mjs";

const SEED = 20260920;
const NEAR = 0.1;

function truthOf(value) {
  if (value === true || value === 1 || value === "1" || value === "yes" || value === "true") return true;
  if (value === false || value === 0 || value === "0" || value === "no" || value === "false") return false;
  return null;
}

function loadJsonl(path) {
  return readFileSync(path, "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

function parseSpec(raw) {
  const eq = raw.indexOf("=");
  if (eq < 1) throw new Error(`bad --q ${raw}`);
  const name = raw.slice(0, eq);
  const parts = raw.slice(eq + 1).split(":");
  if (parts.length !== 3 && parts.length !== 6) {
    throw new Error(`bad --q ${raw}; want name=rows:score:truth or name=rows:score::labels:id:truth`);
  }
  return {
    name,
    rowsPath: parts[0],
    scoreField: parts[1],
    truthField: parts[2] || null,
    labelsPath: parts[3] || null,
    idField: parts[4] || "i",
    labelTruthField: parts[5] || null,
  };
}

export function casesFrom(spec) {
  const rows = loadJsonl(spec.rowsPath);
  let labels = null;
  if (spec.labelsPath) {
    labels = new Map();
    for (const row of loadJsonl(spec.labelsPath)) {
      labels.set(row[spec.idField], row[spec.labelTruthField]);
    }
  }
  const cases = [];
  let missing = 0;
  for (const row of rows) {
    const score = row[spec.scoreField];
    const rawTruth = labels ? labels.get(row[spec.idField]) : row[spec.truthField];
    const truth = truthOf(rawTruth);
    if (typeof score !== "number" || !Number.isFinite(score) || truth === null) {
      missing += 1;
      continue;
    }
    cases.push({ score, truth });
  }
  return { cases, missing, rows: rows.length };
}

export function reportLines(name, cases, seed = SEED) {
  const labels = cases.map((row) => row.truth);
  const constant = ownConstant({ cases: labels });
  const grade = gradeQuestion(cases);
  const random = randomBaseline({ cases: labels, seed });
  const randomCorrect = Math.round(random.accuracy * labels.length);
  const majority = constant.count;
  if (majority !== grade.best) {
    throw new Error(`own-constant ${majority} != gradeQuestion best ${grade.best}`);
  }
  const always = constant.label === true || constant.label === "yes" ? "yes" : "no";
  return [
    `question: ${name}`,
    `near-threshold: ${grade.near}/${grade.asked} (window ±${NEAR} around 0.5)`,
    `own-constant: always-${always} ${majority}/${grade.asked} (majority share ${(majority / grade.asked).toFixed(3)})`,
    `random-judge: ${randomCorrect}/${grade.asked} (seed ${seed}, accuracy ${random.accuracy.toFixed(4)})`,
    `verdict: ${grade.correct}/${grade.asked} vs best-constant ${grade.best} + near ${grade.near} → ${grade.verdict}`,
  ];
}

function main(argv) {
  const specs = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--q") specs.push(parseSpec(argv[++i]));
  }
  if (specs.length === 0) {
    console.error("usage: judge-run.mjs --q name=rows:score:truth [--q ...]");
    return 2;
  }
  const blocks = [];
  for (const spec of specs) {
    const loaded = casesFrom(spec);
    if (loaded.missing > 0) {
      console.error(
        `refusing ${spec.name}: ${loaded.missing}/${loaded.rows} rows lack a finite score or a boolean truth; no verdict`,
      );
      return 2;
    }
    if (loaded.cases.length === 0) {
      console.error(`refusing ${spec.name}: no rows; no verdict`);
      return 2;
    }
    blocks.push(reportLines(spec.name, loaded.cases).join("\n"));
  }
  console.log(blocks.join("\n\n"));
  return 0;
}

function isMain() {
  if (!process.argv[1]) return false;
  try {
    return import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href;
  } catch {
    return false;
  }
}

if (isMain()) {
  process.exit(main(process.argv.slice(2)));
}

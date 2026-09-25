#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { askJev, askJevChoice, askJevScore, DEFAULT_MODEL } from "../src/client.ts";
import { createFakeFetch } from "../src/fake.ts";

const ROOT = new URL("..", import.meta.url);

function hasFlag(args, flag) {
  return args.includes(flag);
}

function option(args, name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
}

function robotPrint(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

async function readJson(path) {
  return JSON.parse(await readFile(resolve(path), "utf8"));
}

async function doctor(robot) {
  const keyPresent = typeof process.env.TYPESAFE_API_KEY === "string" && process.env.TYPESAFE_API_KEY.length > 0;
  const sdkPath = new URL("../../work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs", import.meta.url);
  let sdkPresent = true;
  try {
    await import(sdkPath.href);
  } catch {
    sdkPresent = false;
  }
  const result = {
    status: keyPresent && sdkPresent ? "READY" : "NOT_RUN",
    reason: keyPresent ? (sdkPresent ? undefined : "sdk missing") : "no key",
    model: DEFAULT_MODEL,
    key_source: keyPresent ? "environment" : "none",
    sdk: sdkPresent ? "@typesafe-ai/sdk" : "missing",
  };
  const clean = Object.fromEntries(Object.entries(result).filter(([, value]) => value !== undefined));
  if (robot) robotPrint(clean);
  else process.stdout.write(`${clean.status}: ${clean.reason ?? "ready"} (model=${clean.model})\n`);
  return clean.status === "READY" ? 0 : 2;
}

async function ask(args) {
  const kind = args[1];
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const statePath = option(args, "--state");
  const questionPath = option(args, "--question");
  if (!kind || !statePath || !questionPath || !["choice", "score", "noul"].includes(kind)) {
    const error = { status: "ERROR", reason: "usage", message: "jev ask choice|score|noul --state FILE --question FILE [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
  const state = await readJson(statePath);
  const question = await readJson(questionPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/recorded-answer-rows.json", ROOT), "utf8")))
    : undefined;
  let result;
  if (kind === "choice") {
    result = await askJevChoice({ state, instructions: question.instructions ?? "", classes: question.criteria, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  } else if (kind === "score") {
    result = await askJevScore({ state, instructions: question.instructions ?? "", criteria: question.criteria, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  } else {
    result = await askJev({ state, questions: { value: question.instructions ?? question } , apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  }
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return result.ok ? 0 : result.reason === "unconfigured" ? 2 : 1;
}

const args = process.argv.slice(2);
const robot = hasFlag(args, "--robot");
let exitCode;
try {
  if (args[0] === "doctor") exitCode = await doctor(robot);
  else if (args[0] === "ask") exitCode = await ask(args);
  else {
    const error = { status: "ERROR", reason: "usage", message: "jev doctor [--robot] or jev ask ..." };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    exitCode = 1;
  }
} catch (error) {
  const result = { status: "ERROR", reason: "exception", message: error instanceof Error ? error.message : String(error) };
  if (robot) robotPrint(result); else process.stderr.write(`${result.message}\n`);
  exitCode = 1;
}
process.exitCode = exitCode;

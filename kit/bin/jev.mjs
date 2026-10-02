#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { askJev, askJevChoice, askJevScore, DEFAULT_MODEL } from "../dist/client.js";
import { rerankTop1 } from "../dist/rerank.js";
import { classifyText } from "../dist/classify.js";
import { verifyClaim } from "../dist/verify.js";
import { scoreText } from "../dist/score.js";
import { gateCommand } from "../dist/gate.js";
import { createFakeFetch } from "../dist/fake.js";
import { installOmp, ompDiscovery, uninstallOmp } from "../dist/install.js";

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
    try {
      await import(new URL("../node_modules/@typesafe-ai/sdk/dist/index.mjs", import.meta.url).href);
    } catch {
      sdkPresent = false;
    }
  }
  const result = {
    status: keyPresent && sdkPresent ? "READY" : "NOT_RUN",
    reason: keyPresent ? (sdkPresent ? undefined : "sdk missing") : "no key",
    model: DEFAULT_MODEL,
    key_source: keyPresent ? "environment" : "none",
    sdk: sdkPresent ? "@typesafe-ai/sdk" : "missing",
    omp: await ompDiscovery(process.cwd()),
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
    result = await askJev({ state, questions: { value: question.instructions ?? question }, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  }
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return result.ok ? 0 : result.reason === "unconfigured" ? 2 : 1;
}
async function gate(args) {
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const command = option(args, "--command");
  if (!command) {
    const error = { status: "ERROR", reason: "usage", message: "jev gate --command C [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
  let result;
  if (fake) {
    const fixture = await readJson(new URL("../examples/gate-public.json", import.meta.url).pathname);
    if (command !== fixture.command) {
      const error = { status: "ERROR", reason: "fake fixture", message: "--fake only supports the captured public example command" };
      if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
      return 1;
    }
    const answers = Object.fromEntries(Object.entries(fixture.scores).map(([key, noul]) => [key, { noul }]));
    result = await gateCommand({ command, model: fixture.model, ask: async () => ({ ok: true, answers, latencyMs: 0, resolvedModel: fixture.model, usage: undefined }) });
  } else {
    result = await gateCommand({ command });
  }
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return result.ok ? 0 : result.reason === "unconfigured" ? 2 : 1;
}

async function rerank(args) {
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const query = option(args, "--query");
  const candidatesPath = option(args, "--candidates");
  if (!query || !candidatesPath) {
    const error = { status: "ERROR", reason: "usage", message: "jev rerank --query Q --candidates FILE [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
  const candidates = await readJson(candidatesPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/rerank-fiqa-answer.json", ROOT), "utf8")))
    : undefined;
  const result = await rerankTop1({ query, candidates, apiKey: fake ? "fixture-key" : undefined, fetchImpl, model: fake ? "fake" : undefined });
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return 0;
}

async function classify(args) {
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const text = option(args, "--text");
  const labelsPath = option(args, "--labels");
  if (!text || !labelsPath) {
    const error = { status: "ERROR", reason: "usage", message: "jev classify --text T --labels FILE [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
  const labels = await readJson(labelsPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/banking77-answer.json", ROOT), "utf8")))
    : undefined;
  const result = await classifyText({
    text,
    labels,
    apiKey: fake ? "fixture-key" : undefined,
    fetchImpl,
    model: fake ? "fake" : undefined,
  });
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return 0;
}

async function verify(args) {
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const claim = option(args, "--claim");
  const evidencePath = option(args, "--evidence");
  if (!claim || !evidencePath) {
    const error = { status: "ERROR", reason: "usage", message: "jev verify --claim C --evidence FILE [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    return 1;
  }
  const evidence = await readFile(resolve(evidencePath), "utf8");
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/scifact-answer.json", ROOT), "utf8")))
    : undefined;
  const result = await verifyClaim({
    claim,
    evidence,
    apiKey: fake ? "fixture-key" : undefined,
    fetchImpl,
    model: fake ? "fake" : undefined,
  });
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return 0;
}

async function score(args) {
  const robot = hasFlag(args, "--robot");
  const fake = hasFlag(args, "--fake");
  const text = option(args, "--text");
  const levelsPath = option(args, "--levels");
  if (!text || !levelsPath) {
    const error = { status: "ERROR", reason: "usage", message: "jev score --text T --levels FILE [--robot] [--fake]" };
    if (robot) robotPrint(error); else process.stderr.write(error.message + "\n");
    return 1;
  }
  const levels = await readJson(levelsPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/sst5-answer.json", ROOT), "utf8")))
    : undefined;
  const result = await scoreText({ text, levels, apiKey: fake ? "fixture-key" : undefined, fetchImpl, model: fake ? "fake" : undefined });
  if (robot) robotPrint(result);
  else process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  return 0;
}
const args = process.argv.slice(2);
const robot = hasFlag(args, "--robot");
let exitCode;
try {
  if (args[0] === "doctor") exitCode = await doctor(robot);
  else if (args[0] === "ask") exitCode = await ask(args);
  else if (args[0] === "rerank") exitCode = await rerank(args);
  else if (args[0] === "classify") exitCode = await classify(args);
  else if (args[0] === "verify") exitCode = await verify(args);
  else if (args[0] === "score") exitCode = await score(args);
  else if (args[0] === "gate") exitCode = await gate(args);
  else if (args[0] === "omp" && args[1] === "install") {
    const repo = option(args, "--dir") ?? process.cwd();
    const result = await installOmp(repo, hasFlag(args, "--dry-run"));
    if (robot) robotPrint(result); else process.stdout.write(`${result.status}: copied ${result.files.length} files in ${result.repo}; extensions require manual config merge before omp loads them\n`);
    exitCode = 0;
  } else if (args[0] === "omp" && args[1] === "uninstall") {
    const repo = option(args, "--dir") ?? process.cwd();
    const result = await uninstallOmp(repo, !hasFlag(args, "--apply"));
    if (robot) robotPrint(result); else process.stdout.write(`${result.status}: ${result.files.length} listed, ${result.kept.length} kept (edited), ${result.missing.length} already missing in ${result.repo}\n`);
    exitCode = 0;
  } else {
    const error = { status: "ERROR", reason: "usage", message: "jev doctor|gate|ask|rerank|classify|verify|score ..." };
    if (robot) robotPrint(error); else process.stderr.write(`${error.message}\n`);
    exitCode = 1;
  }
} catch (error) {
  const result = { status: "ERROR", reason: "exception", message: error instanceof Error ? error.message : String(error) };
  if (robot) robotPrint(result); else process.stderr.write(`${result.message}\n`);
  exitCode = 1;
}
process.exitCode = exitCode;

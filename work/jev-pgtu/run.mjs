#!/usr/bin/env node
import {spawn, spawnSync} from "node:child_process";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {ASSISTANT, CUT, MODEL, QUESTION} from "../jev-a9fv/seat.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const ADAPTER_PROJECT = path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python");
const PYTHON_RUNNER = path.join(ROOT, "work/jev-pgtu/adapter_runner.py");
const SDK_PROJECT = path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python");
const JEV_BASELINE_RUNNER = path.join(ROOT, "work/jev-pgtu/jev_baseline.py");
const RESET_AT = Date.parse("2026-10-03T00:00:00Z");
const args = process.argv.slice(2);
const launch = args.length === 1 && args[0] === "--launch";
const selftest = args.length === 1 && args[0] === "--selftest-429";
const preflight = args.length === 0 || (args.length === 1 && args[0] === "--preflight-only");
const jevRescorePreflight = args.length === 1 && args[0] === "--jev-rescore-preflight";
const jevRescoreLive = args.length === 1 && args[0] === "--jev-rescore-live";

function childEnvironment(allowOpenRouterKey) {
  const env = {
    ...process.env,
    JEV_PGTU_ASSISTANT: ASSISTANT,
    JEV_PGTU_QUESTION: QUESTION,
    JEV_PGTU_JEV_MODEL: MODEL,
    JEV_PGTU_CUT: String(CUT),
  };
  delete env.TYPESAFE_API_KEY;
  delete env.JEV_API_KEY;
  if (!allowOpenRouterKey) delete env.OPENROUTER_API_KEY;
  return env;
}

function uvArgs(mode) {
  return [
    "run",
    "--project",
    ADAPTER_PROJECT,
    "--frozen",
    "--no-sync",
    "--extra",
    "openai",
    "python",
    PYTHON_RUNNER,
    mode,
  ];
}

function runBuffered(mode) {
  return spawnSync("uv", uvArgs(mode), {
    cwd: ROOT,
    env: childEnvironment(false),
    encoding: "utf8",
    maxBuffer: 4 * 1024 * 1024,
  });
}

function baselineEnvironment(allowTypeSafeKey) {
  const env = {
    ...process.env,
    JEV_PGTU_ASSISTANT: ASSISTANT,
    JEV_PGTU_QUESTION: QUESTION,
    JEV_PGTU_JEV_MODEL: MODEL,
    JEV_PGTU_CUT: String(CUT),
  };
  delete env.JEV_API_KEY;
  delete env.OPENROUTER_API_KEY;
  for (const key of Object.keys(env)) if (key.startsWith("INFISICAL_")) delete env[key];
  if (!allowTypeSafeKey) delete env.TYPESAFE_API_KEY;
  return env;
}

function jevBaselineArgs(mode) {
  return ["run", "--project", SDK_PROJECT, "--frozen", "--no-sync", "python", JEV_BASELINE_RUNNER, mode];
}

function runJevBaseline(mode, allowTypeSafeKey) {
  return spawnSync("uv", jevBaselineArgs(mode), {
    cwd: ROOT,
    env: baselineEnvironment(allowTypeSafeKey),
    encoding: "utf8",
    maxBuffer: 4 * 1024 * 1024,
  });
}

function printResult(result) {
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
}

if (jevRescorePreflight || jevRescoreLive) {
  const result = runJevBaseline(jevRescoreLive ? "--live" : "--preflight-only", jevRescoreLive);
  printResult(result);
  process.exitCode = result.error ? 2 : (result.status ?? 2);
} else if (selftest) {
  const result = runBuffered("--selftest-429");
  printResult(result);
  process.exitCode = result.error ? 2 : (result.status ?? 2);
} else if (preflight) {
  const result = runBuffered("--preflight-only");
  printResult(result);
  process.exitCode = result.error ? 2 : (result.status ?? 2);
} else if (launch) {
  const approvalId = process.env.JEV_PGTU_APPROVAL_ID ?? "";
  if (Date.now() < RESET_AT) {
    process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "free-tier-window-not-open", launch_not_before: "2026-10-03T00:00:00Z"}) + "\n");
    process.exitCode = 2;
  } else if (!/^\d+$/.test(approvalId)) {
    process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "pane1-approval-required"}) + "\n");
    process.exitCode = 2;
  } else {
    const before = runBuffered("--preflight-only");
    printResult(before);
    let summary;
    try {
      summary = JSON.parse(before.stdout.trim().split(/\r?\n/).at(-1));
    } catch {
      summary = null;
    }
    if (before.error || before.status !== 0 || summary?.status !== "PREPARED") {
      process.exitCode = before.error ? 2 : (before.status ?? 2);
    } else if (!process.env.OPENROUTER_API_KEY) {
      process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "openrouter-key-missing"}) + "\n");
      process.exitCode = 2;
    } else {
      const child = spawn("uv", uvArgs("--launch"), {
        cwd: ROOT,
        env: childEnvironment(true),
        stdio: "inherit",
      });
      let settled = false;
      child.once("error", () => {
        if (!settled) {
          process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "uv-runner-unavailable"}) + "\n");
          process.exitCode = 2;
          settled = true;
        }
      });
      child.once("close", (code) => {
        if (!settled) {
          process.exitCode = code ?? 2;
          settled = true;
        }
      });
      for (const signal of ["SIGINT", "SIGTERM"]) {
        process.on(signal, () => child.kill(signal));
      }
    }
  }
} else {
  process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "usage", usage: "node work/jev-pgtu/run.mjs [--preflight-only|--selftest-429|--launch|--jev-rescore-preflight|--jev-rescore-live]"}) + "\n");
  process.exitCode = 2;
}

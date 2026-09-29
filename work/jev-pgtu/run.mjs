#!/usr/bin/env node
import {spawn, spawnSync} from "node:child_process";
import path from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import {ASSISTANT, CUT, MODEL, QUESTION} from "../jev-a9fv/seat.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const ADAPTER_PROJECT = path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python");
const PYTHON_RUNNER = path.join(ROOT, "work/jev-pgtu/adapter_runner.py");
const SDK_PROJECT = path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python");
const JEV_BASELINE_RUNNER = path.join(ROOT, "work/jev-pgtu/jev_baseline.py");
const INFISICAL_KEY_MODULE = path.join(ROOT, "work/jev-client/src/infisical-key.ts");
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

function baselineEnvironment() {
  const env = {
    ...process.env,
    JEV_PGTU_ASSISTANT: ASSISTANT,
    JEV_PGTU_QUESTION: QUESTION,
    JEV_PGTU_JEV_MODEL: MODEL,
    JEV_PGTU_CUT: String(CUT),
  };
  for (const key of Object.keys(env)) {
    if (key.startsWith("INFISICAL_") || key.endsWith("_API_KEY") || key.endsWith("_TOKEN")) {
      delete env[key];
    }
  }
  return env;
}

function jevBaselineArgs(mode, keyStdin = false) {
  const args = ["run", "--project", SDK_PROJECT, "--frozen", "--no-sync", "python", JEV_BASELINE_RUNNER, mode];
  if (keyStdin) args.push("--key-stdin");
  return args;
}

function runJevBaselinePython(mode, apiKey) {
  const hasKey = Boolean(apiKey);
  return spawnSync("uv", jevBaselineArgs(mode, hasKey), {
    cwd: ROOT,
    env: baselineEnvironment(),
    input: hasKey ? apiKey + "\n" : undefined,
    encoding: "utf8",
    maxBuffer: 4 * 1024 * 1024,
  });
}

async function runJevBaseline(mode, resolveKey) {
  if (!resolveKey) return runJevBaselinePython(mode);
  const preflight = runJevBaselinePython("--preflight-only");
  if (preflight.error || preflight.status !== 0) return preflight;
  let report;
  try {
    report = JSON.parse(preflight.stdout.trim().split(/\r?\n/).at(-1));
  } catch {
    return preflight;
  }
  if (report?.status !== "READY_TO_RESCORE") return preflight;

  let apiKey;
  try {
    const {infisicalKeyProvider} = await import(pathToFileURL(INFISICAL_KEY_MODULE).href);
    apiKey = await infisicalKeyProvider();
  } catch {
    apiKey = undefined;
  }
  if (!apiKey) {
    return {
      error: undefined,
      status: 2,
      stdout: JSON.stringify({status: "NOT_RUN", reason: "infisical-key-unavailable"}) + "\n",
      stderr: "",
    };
  }
  return runJevBaselinePython("--live", apiKey);
}

function printResult(result) {
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
}

if (jevRescorePreflight || jevRescoreLive) {
  let result;
  try {
    result = await runJevBaseline(jevRescoreLive ? "--live" : "--preflight-only", jevRescoreLive);
  } catch {
    result = {
      error: undefined,
      status: 2,
      stdout: JSON.stringify({status: "NOT_RUN", reason: "baseline-runner-failed"}) + "\n",
      stderr: "",
    };
  }
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
  process.stdout.write(JSON.stringify({status: "NOT_RUN", reason: "usage", usage: "node work/jev-pgtu/run.mjs [--preflight-only|--selftest-429|--launch|--jev-rescore-preflight]; node --experimental-strip-types work/jev-pgtu/run.mjs --jev-rescore-live"}) + "\n");
  process.exitCode = 2;
}

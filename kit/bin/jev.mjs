#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { askJev, askJevChoice, askJevScore } from "../dist/client.js";
import { rerankTop1 } from "../dist/rerank.js";
import { classifyText } from "../dist/classify.js";
import { verifyClaim } from "../dist/verify.js";
import { scoreText } from "../dist/score.js";
import { gateCommand } from "../dist/gate.js";
import { createFakeFetch } from "../dist/fake.js";
import { installOmp, ompDiscovery, uninstallOmp } from "../dist/install.js";
import { createInstallPlan } from "../dist/install/plan.js";
import { acquireInstallLock } from "../dist/install/manifest.js";
import { createEnvelope } from "../src/cli/envelope.mjs";
import { exitCodeForFailure } from "../src/cli/exit.mjs";
import { parseArgv } from "../src/cli/argv.mjs";
import { helpFor } from "../src/cli/help.mjs";
import { runDoctor } from "../src/doctor/engine.mjs";
import { runHealth } from "../src/doctor/readiness.mjs";
import { FAMILIES, capabilities, dispatchCommand, robotDocs, schema, validateFamilyNames } from "../dist/families/registry.js";
import { formatCliError, rewriteCliError } from "../dist/cli/errors.js";

const ROOT = new URL("..", import.meta.url);

function hasFlag(args, flag) {
  return args.includes(flag);
}

function option(args, name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
}


async function readJson(path) {
  return JSON.parse(await readFile(resolve(path), "utf8"));
}

function usageFailure(message) {
  return { ok: false, reason: "usage", error: message };
}

function execProbe(command, args, options = {}) {
  return new Promise((resolveResult) => {
    execFile(command, args, {
      ...options,
      encoding: "utf8",
      timeout: options.timeout ?? 1000,
      maxBuffer: options.maxBuffer ?? 1024 * 1024,
    }, (error, stdout, stderr) => {
      resolveResult({
        code: error ? (Number.isInteger(error.code) ? error.code : 1) : 0,
        stdout: stdout ?? "",
        stderr: stderr ?? "",
      });
    });
  });
}

async function findRepo(start) {
  let current = resolve(start);
  while (true) {
    try {
      const inventory = await readJson(join(current, "work/jev-inventory/expected.json"));
      return { repo: current, inventory };
    } catch (error) {
      if (error?.code !== "ENOENT" && error?.code !== "ENOTDIR") throw error;
    }
    const parent = dirname(current);
    if (parent === current) return { repo: null, inventory: null };
    current = parent;
  }
}

async function doctorContext(parsed) {
  const home = resolve(parsed.options.home ?? process.env.HOME ?? homedir());
  const discovered = await findRepo(parsed.options.repo ?? process.cwd());
  const repo = parsed.options.repo ? resolve(parsed.options.repo) : discovered.repo;
  const inventory = parsed.options.repo
    ? await readJson(join(repo, "work/jev-inventory/expected.json"))
    : discovered.inventory;
  const stateDir = resolve(process.env.JEV_STATE_DIR || join(home, ".local", "state", "jev"));
  const target = repo
    ? await execProbe("git", ["-C", repo, "rev-parse", "HEAD"], { timeout: 1000, maxBuffer: 1024 })
    : null;
  return {
    repo,
    home,
    stateDir,
    now: Date.now(),
    target_sha: target?.code === 0 ? target.stdout.trim() : null,
    tier: parsed.options.deep ? "deep" : parsed.options.quick ? "quick" : "default",
    only: parsed.options.only,
    skip: parsed.options.skip,
    online: parsed.options.online === true,
    env: process.env,
    inventory,
    omp: await ompDiscovery(repo ?? process.cwd()),
    exec: execProbe,
    fetch: (url, init) => globalThis.fetch(url, init),
  };
}

async function doctor(parsed) {
  return runDoctor(await doctorContext(parsed));
}

async function health(parsed) {
  const report = await runHealth(await doctorContext(parsed));
  return {
    ...report,
    ok: report.status === "ok",
    ...(report.status === "findings" ? { reason: "findings" } : {}),
  };
}

async function ask(args) {
  const kind = args[1];
  const fake = hasFlag(args, "--fake");
  const statePath = option(args, "--state");
  const questionPath = option(args, "--question");
  if (!kind || !statePath || !questionPath || !["choice", "score", "noul"].includes(kind)) {
    return usageFailure("classifier ask choice|score|noul --state FILE --question FILE [--fake] [--json|--robot]");
  }
  const state = await readJson(statePath);
  const question = await readJson(questionPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/recorded-answer-rows.json", ROOT), "utf8")))
    : undefined;
  if (kind === "choice") {
    return askJevChoice({ state, instructions: question.instructions ?? "", classes: question.criteria, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  }
  if (kind === "score") {
    return askJevScore({ state, instructions: question.instructions ?? "", criteria: question.criteria, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
  }
  return askJev({ state, questions: { value: question.instructions ?? question }, apiKey: fake ? "fixture-key" : undefined, fetchImpl });
}

async function gate(args) {
  const fake = hasFlag(args, "--fake");
  const command = option(args, "--command");
  if (!command) return usageFailure("classifier gate --command C [--fake] [--json|--robot]");
  if (fake) {
    const fixture = await readJson(new URL("../examples/gate-public.json", import.meta.url).pathname);
    if (command !== fixture.command) return usageFailure("--fake only supports the captured public example command");
    const answers = Object.fromEntries(Object.entries(fixture.scores).map(([key, noul]) => [key, { noul }]));
    return gateCommand({ command, model: fixture.model, ask: async () => ({ ok: true, answers, latencyMs: 0, resolvedModel: fixture.model, usage: undefined }) });
  }
  return gateCommand({ command });
}

async function rerank(args) {
  const fake = hasFlag(args, "--fake");
  const query = option(args, "--query");
  const candidatesPath = option(args, "--candidates");
  if (!query || !candidatesPath) return usageFailure("classifier rerank --query Q --candidates FILE [--fake] [--json|--robot]");
  const candidates = await readJson(candidatesPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/rerank-fiqa-answer.json", ROOT), "utf8")))
    : undefined;
  return rerankTop1({ query, candidates, apiKey: fake ? "fixture-key" : undefined, fetchImpl, model: fake ? "fake" : undefined });
}

async function classify(args) {
  const fake = hasFlag(args, "--fake");
  const text = option(args, "--text");
  const labelsPath = option(args, "--labels");
  if (!text || !labelsPath) return usageFailure("classifier classify --text T --labels FILE [--fake] [--json|--robot]");
  const labels = await readJson(labelsPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/banking77-answer.json", ROOT), "utf8")))
    : undefined;
  return classifyText({
    text,
    labels,
    apiKey: fake ? "fixture-key" : undefined,
    fetchImpl,
    model: fake ? "fake" : undefined,
  });
}

async function verify(args) {
  const fake = hasFlag(args, "--fake");
  const claim = option(args, "--claim");
  const evidencePath = option(args, "--evidence");
  if (!claim || !evidencePath) return usageFailure("classifier verify --claim C --evidence FILE [--fake] [--json|--robot]");
  const evidence = await readFile(resolve(evidencePath), "utf8");
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/scifact-answer.json", ROOT), "utf8")))
    : undefined;
  return verifyClaim({
    claim,
    evidence,
    apiKey: fake ? "fixture-key" : undefined,
    fetchImpl,
    model: fake ? "fake" : undefined,
  });
}

async function score(args) {
  const fake = hasFlag(args, "--fake");
  const text = option(args, "--text");
  const levelsPath = option(args, "--levels");
  if (!text || !levelsPath) return usageFailure("classifier score --text T --levels FILE [--fake] [--json|--robot]");
  const levels = await readJson(levelsPath);
  const fetchImpl = fake
    ? createFakeFetch(JSON.parse(await readFile(new URL("./test/fixtures/sst5-answer.json", ROOT), "utf8")))
    : undefined;
  return scoreText({ text, levels, apiKey: fake ? "fixture-key" : undefined, fetchImpl, model: fake ? "fake" : undefined });
}
async function runInstaller(command, args, parsed) {
  if (hasFlag(args, "--dry-run") && hasFlag(args, "--apply")) {
    return usageFailure("--dry-run and --apply cannot be used together");
  }
  if (parsed.positionals.length > 1) return usageFailure(`classifier ${command} accepts one target or all`);
  const target = parsed.positionals[0] ?? "all";
  const plan = await createInstallPlan({ target, dir: option(args, "--dir") });
  const apply = hasFlag(args, "--apply");

  if (target !== "omp-project") {
    if (apply) return usageFailure(`--apply is not available for ${target}; use --dry-run to inspect its plan`);
    return {
      ok: true,
      ...(command === "install" ? plan : {
        status: plan.status,
        target: plan.target,
        mode: "dry-run",
        steps: plan.steps,
      }),
    };
  }

  const repo = plan.dir;
  if (!apply) {
    const result = command === "install"
      ? await installOmp(repo, true)
      : await uninstallOmp(repo, true);
    return { ok: true, ...result };
  }

  const lockPath = join(process.env.HOME ?? homedir(), ".local/state/classifier/install.lock");
  const lock = await acquireInstallLock(lockPath);
  try {
    const result = command === "install"
      ? await installOmp(repo, false)
      : await uninstallOmp(repo, false);
    return { ok: true, ...result };
  } finally {
    await lock.release();
  }
}

const FAMILY_RUNNERS = { classify, rerank, verify, score, gate };
async function main() {
  const suppliedArgs = process.argv.slice(2);
  const correctedRobotFlag = suppliedArgs.includes("--robto");
  const args = suppliedArgs.map((value) => value === "--robto" ? "--robot" : value);
  if (args.length > 0) args[0] = dispatchCommand(args[0]);
  const metaVerb = args[0];
  if (metaVerb === "capabilities" || metaVerb === "robot-docs" || metaVerb === "schema") {
    if (validateFamilyNames().length > 0) {
      process.stderr.write(`invalid family registry: ${validateFamilyNames().join("; ")}\n`);
      return 74;
    }
    const output = metaVerb === "capabilities" ? capabilities()
      : metaVerb === "schema" ? schema(option(args, "--command"))
        : robotDocs();
    process.stdout.write(`${typeof output === "string" ? output : JSON.stringify(output, null, 2)}\n`);
    return 0;
  }
  if (correctedRobotFlag) process.stderr.write("warning: '--robto' interpreted as '--robot'\n");
  let parsed = parseArgv(args);
  if (parsed.error?.message.startsWith("Unknown option: ") && !parsed.error.correctedCommand) {
    const unknownOption = parsed.error.message.slice("Unknown option: ".length);
    process.stderr.write(`warning: unknown flag '${unknownOption}' ignored; see classifier ${parsed.command ?? ""} --help\n`);
    args.splice(args.indexOf(unknownOption), 1);
    parsed = parseArgv(args);
  }
  if (parsed.version) {
    const pkg = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
    process.stdout.write(`classifier ${pkg.version}\n`);
    return 0;
  }
  if (parsed.help || args.length === 0) {
    const topic = args[0] === "help" ? args[1] ?? "" : parsed.command ?? "";
    process.stdout.write(`${helpFor(topic)}\n`);
    return 0;
  }
  if (parsed.error) {
    const { message, correctedCommand } = parsed.error;
    const unknownCommand = message.startsWith("Unknown command: ");
    const error = rewriteCliError({
      reason: unknownCommand ? "unknown-command" : message.startsWith("Unknown option: ") ? "unknown-option" : "usage",
      message,
      option: unknownCommand ? message.slice("Unknown command: ".length) : message.startsWith("Unknown option: ") ? message.slice("Unknown option: ".length) : undefined,
      correctedCommand,
    });
    const detail = formatCliError(error);
    if (parsed.outputMode === "human") process.stderr.write(`${detail}\n`);
    else {
      const envelope = createEnvelope("cli", { ok: false, reason: "usage", error: error.message });
      envelope.errors = [error];
      envelope.commands = [error.see];
      process.stdout.write(`${JSON.stringify(envelope)}\n`);
      process.stderr.write(`${detail}\n`);
    }
    return error.exit_code;
  }

  const family = FAMILIES.find((candidate) => candidate.name === parsed.command || candidate.aliases.includes(parsed.command));
  let result;
  let cliError;
  try {
    if (parsed.command === "doctor") result = await doctor(parsed);
    else if (parsed.command === "health") result = await health(parsed);
    else if (parsed.command === "ask") result = await ask(args);
    else if (parsed.command === "install" || parsed.command === "uninstall") result = await runInstaller(parsed.command, args, parsed);
    else if (family && typeof FAMILY_RUNNERS[family.runner] === "function") result = await FAMILY_RUNNERS[family.runner](args);
    else if (parsed.command === "omp" && parsed.subcommand === "install") {
      result = { ok: true, ...await installOmp(option(args, "--dir") ?? process.cwd(), hasFlag(args, "--dry-run")) };
    } else if (parsed.command === "omp" && parsed.subcommand === "uninstall") {
      result = { ok: true, ...await uninstallOmp(option(args, "--dir") ?? process.cwd(), !hasFlag(args, "--apply")) };
    } else {
      result = usageFailure("classifier doctor|gate|ask|rerank|classify|verify|score|install|uninstall|omp ...");
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const code = error && typeof error === "object" ? error.code : undefined;
    const knownReasons = ["unconfigured", "sdk-missing", "billing-hold", "transport", "http", "non-json", "no-answers", "invalid-answer"];
    const reason = knownReasons.find((candidate) => message.includes(`(${candidate})`))
      ?? (code === "USAGE" ? "usage"
        : code === "REFUSED" ? "refused-unsafe"
          : code === "RETRYABLE" ? "transport"
            : code === "ENOENT" || code === "ENOTDIR" ? "no-input"
              : ["EACCES", "EIO", "EISDIR", "IO"].includes(code) ? "io" : "exception");
    cliError = rewriteCliError({
      reason,
      message,
      code,
      command: parsed.command,
      option: parsed.command === "classify" ? "--labels" : undefined,
      path: parsed.command === "classify" ? option(args, "--labels") : undefined,
      cwd: process.cwd(),
    });
    result = { ok: false, reason, error: cliError.message, ...(code ? { code } : {}) };
  }
  if (!cliError && result?.ok === false && parsed.command !== "doctor" && parsed.command !== "health") {
    cliError = rewriteCliError({ reason: result.reason, message: result.error ?? result.message, command: parsed.command });
  }
  if (cliError) {
    const reasonByCode = {
      NOT_RUN: "unconfigured",
      USAGE: "usage",
      NO_INPUT: "no-input",
      REFUSED: "invalid-answer",
      REFUSED_UNSAFE: "refused-unsafe",
      RETRYABLE: "transport",
      ONLINE_REQUIRED: "sdk-missing",
      CANT_CREATE: "cannot-create",
      IO: "io",
    };
    result = { ...result, reason: reasonByCode[cliError.code] ?? result.reason, error: cliError.message };
  }

  const doctorExitCode = parsed.command === "doctor"
    ? Number.isInteger(result.exit_code) ? result.exit_code : exitCodeForFailure(result)
    : null;
  const doctorFailure = parsed.command === "doctor" && doctorExitCode !== 0;
  const envelopeResult = parsed.command === "doctor"
    ? { ok: !doctorFailure, reason: doctorFailure ? "findings" : undefined, message: result.state, model: result.backends?.jev?.model }
    : result;
  const exitCode = parsed.command === "doctor" ? doctorExitCode : result.ok === true ? 0 : exitCodeForFailure(result);

  if (parsed.outputMode !== "human") {
    if (parsed.outputMode === "json" && parsed.command === "doctor") {
      process.stdout.write(`${JSON.stringify(result)}\n`);
    } else {
      const envelopeOptions = parsed.command === "doctor" || parsed.command === "health" ? { data: result } : {};
      const envelope = createEnvelope(parsed.command ?? "cli", envelopeResult, envelopeOptions);
      if (cliError) {
        envelope.status = cliError.code;
        envelope.errors = [cliError];
        envelope.commands = [cliError.see];
        process.stderr.write(`${formatCliError(cliError)}\n`);
      }
      process.stdout.write(`${JSON.stringify(envelope)}\n`);
    }
  } else if (cliError) {
    process.stderr.write(`${formatCliError(cliError)}\n`);
  } else if (parsed.command === "doctor") {
    process.stdout.write(`${result.state}: checks=${result.summary.checks_run} findings=${result.summary.total_findings}\n`);
  } else if (parsed.command === "health") {
    process.stdout.write(`${result.status}: checks=${result.checks} findings=${result.findings.length}\n`);
  } else if (parsed.command === "omp" && parsed.subcommand === "install") {
    process.stdout.write(`${result.status}: copied ${result.files.length} files in ${result.repo}; extensions require manual config merge before omp loads them\n`);
  } else if (parsed.command === "omp" && parsed.subcommand === "uninstall") {
    process.stdout.write(`${result.status}: ${result.files.length} listed, ${result.kept.length} kept (edited), ${result.missing.length} already missing in ${result.repo}\n`);
  } else if (result.ok === false && result.reason !== "unconfigured") {
    process.stderr.write(`${result.error}\n`);
  } else {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  }
  return exitCode;
}

process.exitCode = await main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  return 74;
});

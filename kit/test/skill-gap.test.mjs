import assert from "node:assert/strict";
import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, symlink, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { join, resolve } from "node:path";
import test from "node:test";
import {
  installLaunchAgent,
  renderLaunchAgent,
  runDailyMiner,
} from "../src/skill-gap.ts";

const repo = resolve(new URL("../..", import.meta.url).pathname);
const NOW = Date.parse("2026-10-03T12:00:00.000Z");
const COMMAND_SENTINEL = "python3 -c 'import command_marker_8472'";
const ERROR_SENTINEL = "ModuleNotFoundError: error_marker_6381";
const UNRELATED_TEXT = "UNRELATED_CONVERSATION_MARKER_2294";

async function fixture(label) {
  const root = join(repo, "var", "agent-tmp", `jev-skill-gap.${label}.${process.pid}.${randomUUID()}`);
  await mkdir(root, { recursive: true });
  await writeFile(join(root, ".owner"), `${JSON.stringify({ pid: process.pid, label: `jev-skill-gap.${label}`, repo, created: new Date().toISOString() })}\n`, { mode: 0o600 });
  const home = join(root, "home");
  const repoRoot = join(root, "repo");
  const otherRepoRoot = join(root, "other-repo");
  const stateDir = join(root, "state");
  const globalSkillStore = join(root, "global-skills");
  await mkdir(repoRoot, { recursive: true });
  await mkdir(otherRepoRoot, { recursive: true });
  await mkdir(join(home, ".agents"), { recursive: true });
  await mkdir(join(globalSkillStore, "python-import-support"), { recursive: true });
  await symlink(globalSkillStore, join(home, ".agents", "skills"), "dir");
  await writeFile(join(globalSkillStore, "python-import-support", "SKILL.md"), [
    "---",
    "name: python-import-support",
    "description: Diagnose Python import errors and missing modules.",
    "---",
    "Use import diagnostics.",
    "",
  ].join("\n"));
  return { root, home, repoRoot, otherRepoRoot, stateDir, globalSkillStore };
}
function parseJson(value) {
  try {
    return JSON.parse(value);
  } catch (error) {
    assert.fail(`Expected JSON; parse failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}


function toolCall(id, name, args) {
  return {
    type: "message",
    message: {
      role: "assistant",
      content: [{ type: "toolCall", id, name, arguments: args }],
    },
  };
}

function toolResult(id, isError, content) {
  return { type: "message", message: { role: "toolResult", toolCallId: id, isError, content } };
}

async function writeSession(path, cwd, { skillRead, repeatFailure }) {
  const rows = [
    { type: "session", cwd, timestamp: "2026-10-03T11:00:00.000Z" },
    { type: "message", message: { role: "user", content: [{ type: "text", text: UNRELATED_TEXT }] } },
  ];
  if (skillRead) {
    rows.push(toolCall("skill-read", "read", { path: "skill://python-import-support" }));
    rows.push(toolResult("skill-read", false, "skill text remains local"));
  }
  rows.push(toolCall("bash-fail-1", "bash", { command: COMMAND_SENTINEL }));
  rows.push(toolResult("bash-fail-1", true, ERROR_SENTINEL));
  if (repeatFailure) {
    rows.push(toolCall("bash-fail-2", "bash", { command: COMMAND_SENTINEL }));
    rows.push(toolResult("bash-fail-2", true, ERROR_SENTINEL));
  }
  rows.push(toolCall("read-fail", "read", { path: join(cwd, "src", "missing-module.py") }));
  rows.push(toolResult("read-fail", true, "FileNotFoundError: private path content"));
  await mkdir(join(path, ".."), { recursive: true });
  await writeFile(path, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`);
  return rows.length;
}

async function writeTwoProfileSessions(fx, { skillRead = true, repeatFailure = true } = {}) {
  const defaultDir = join(fx.home, ".omp", "agent", "sessions");
  const profileDir = join(fx.home, ".omp", "profiles", "codex", "agent", "sessions");
  await mkdir(defaultDir, { recursive: true });
  await mkdir(profileDir, { recursive: true });
  const pathA = join(defaultDir, "default.jsonl");
  const pathB = join(profileDir, "profile.jsonl");
  const lineCountA = await writeSession(pathA, fx.repoRoot, { skillRead, repeatFailure });
  const lineCountB = await writeSession(pathB, fx.otherRepoRoot, { skillRead: false, repeatFailure: false });
  return { pathA, pathB, lineCountA, lineCountB };
}

function answeringFetch(captured) {
  return async (_input, init) => {
    const body = parseJson(init.body);
    captured.push(body);
    const answers = {};
    for (const [key, question] of Object.entries(body.questions)) {
      const labels = Object.keys(question.criteria);
      const probabilities = Object.fromEntries(labels.map((label) => [label, label === "uncovered" ? 0.9 : 0.1 / (labels.length - 1)]));
      answers[key] = { type: "choice", choice: "uncovered", confidence: 0.9, probabilities };
    }
    return new Response(JSON.stringify({ answers, model: body.model, usage: { input_tokens: 123, output_tokens: 0 } }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
}

function fakeBeads(calls) {
  return (command, args, cwd) => {
    calls.push({ command, args, cwd });
    if (args[0] === "list") return { status: 0, stdout: JSON.stringify({ issues: [] }), stderr: "" };
    if (args[0] === "create") return { status: 0, stdout: JSON.stringify({ id: `review-${calls.filter((call) => call.args[0] === "create").length}` }), stderr: "" };
    return { status: 1, stdout: "", stderr: "unexpected br command" };
  };
}

async function invokeDailyCli(fx) {
  const cli = join(repo, "kit", "bin", "jev-skill-gap.mjs");
  return await new Promise((resolveResult, reject) => {
    const child = spawn(process.execPath, [cli, "--daily", "--home", fx.home, "--repo-root", fx.repoRoot, "--state-dir", fx.stateDir, "--robot"], {
      cwd: repo,
      env: { ...process.env, HOME: fx.home, TYPESAFE_API_KEY: "", JEV_MODEL: "jev-1.13.0" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => resolveResult({ code, stdout, stderr }));
  });
}

test("session cursors survive reruns; extraction clusters tools, file reads, skill reads, errors, and retries without raw text upload", async () => {
  const fx = await fixture("extract");
  const sessions = await writeTwoProfileSessions(fx);
  const sent = [];
  const beads = [];
  const skillsPath = join(fx.home, ".agents", "skills", "python-import-support", "SKILL.md");
  const originalSkill = await readFile(skillsPath, "utf8");
  const options = {
    home: fx.home,
    repoRoot: fx.repoRoot,
    stateDir: fx.stateDir,
    now: () => NOW,
    model: "jev-1.13.0",
    apiKey: String.fromCharCode(120),
    fetchImpl: answeringFetch(sent),
    runCommand: fakeBeads(beads),
  };

  const first = await runDailyMiner(options);
  assert.equal(first.status, "OK");
  assert.equal(first.coverage.project_roots, 2, "the repeated cluster spans two repository roots");
  assert.equal(first.model.status, "CALLED");
  assert.deepEqual(first.model, {
    status: "CALLED", model: "jev-1.13.0", calls: 1, input_tokens: 123,
    cost_usd: 0.00000517, latency_ms: first.model.latency_ms,
  });
  assert.deepEqual(first.coverage.event_counts, { tool_calls: 6, file_reads: 3, skill_reads: 1, failures: 5, retries: 1 });
  assert.equal(first.clusters.length, 2);
  const bashCluster = first.clusters.find((cluster) => cluster.tool_name === "bash");
  const readCluster = first.clusters.find((cluster) => cluster.tool_name === "read");
  assert.equal(bashCluster.command_family, "python");
  assert.equal(bashCluster.error_class, "ModuleNotFoundError");
  assert.equal(bashCluster.retry_count, 1);
  assert.equal(bashCluster.session_count, 2);
  assert.equal(readCluster.file_extension, "py");
  assert.equal(readCluster.error_class, "FileNotFoundError");
  assert.equal(first.skill_update_candidates.length, 2);
  assert.deepEqual(first.skill_update_candidates[0].skill_names, ["python-import-support"]);
  assert.equal(first.skill_update_candidates.every((candidate) => candidate.evidence.every(({ path, line }) => path.endsWith(".jsonl") && Number.isInteger(line) && line > 0)), true);
  assert.equal(first.review_beads.created.length, 2);
  assert.equal(beads.filter((call) => call.args[0] === "create").length, 2);
  for (const call of beads.filter((item) => item.args[0] === "create")) {
    const description = call.args[call.args.indexOf("--description") + 1];
    const acceptance = call.args[call.args.indexOf("--acceptance-criteria") + 1];
    assert.ok(description.includes("Evidence path:line"));
    const matchingCluster = first.clusters.find((cluster) => description.includes(cluster.topic));
    assert.ok(matchingCluster);
    const evidence = matchingCluster.evidence[0];
    assert.ok(description.includes(`${evidence.path}:${evidence.line}`));
    assert.ok(acceptance.includes("Reviewer opens the cited path:line rows"));
  }
  assert.equal(await readFile(skillsPath, "utf8"), originalSkill, "mining queues review but never edits a skill");

  assert.equal(sent.length, 1);
  const requestText = JSON.stringify(sent[0]);
  assert.equal(requestText.includes(COMMAND_SENTINEL), false);
  assert.equal(requestText.includes(ERROR_SENTINEL), false);
  assert.equal(requestText.includes("private path content"), false);
  assert.equal(requestText.includes(UNRELATED_TEXT), false);
  assert.equal(requestText.includes(sessions.pathA), false);
  assert.equal(requestText.includes(sessions.pathB), false);
  assert.ok(requestText.includes("python-import-support"));
  assert.ok(requestText.includes("Diagnose Python import errors and missing modules"));
  assert.ok(requestText.includes("ModuleNotFoundError"));

  const second = await runDailyMiner(options);
  assert.equal(second.model.status, "CACHED");
  assert.equal(second.coverage.event_counts.tool_calls, first.coverage.event_counts.tool_calls);
  assert.equal(second.coverage.event_counts.failures, first.coverage.event_counts.failures);
  assert.deepEqual(second.clusters, first.clusters);
  assert.equal(sent.length, 1, "a restart from the persisted cursor must not repeat model calls for classified clusters");
  assert.equal(beads.filter((call) => call.args[0] === "create").length, 2, "review beads are deduplicated across daily reruns");
  assert.equal((await readFile(join(fx.stateDir, "state.json"), "utf8")).includes(COMMAND_SENTINEL), false);
  assert.equal((await readFile(join(fx.stateDir, "reports", "2026-10-03.json"), "utf8")).includes(COMMAND_SENTINEL), false);
});

test("an uncovered failure without a prior skill read never emits a skill-update candidate", async () => {
  const fx = await fixture("no-prior-skill");
  await writeTwoProfileSessions(fx, { skillRead: false, repeatFailure: false });
  const report = await runDailyMiner({
    home: fx.home,
    repoRoot: fx.repoRoot,
    stateDir: fx.stateDir,
    now: () => NOW,
    model: "jev-1.13.0",
    apiKey: String.fromCharCode(120),
    fetchImpl: answeringFetch([]),
    dryRun: true,
  });
  assert.equal(report.model.status, "CALLED");
  assert.equal(report.clusters.every((cluster) => cluster.skills_read_before_failure.length === 0), true);
  assert.deepEqual(report.skill_update_candidates, []);
});

test("missing Jev credentials report NOT_RUN without dispatching a model request", async () => {
  const fx = await fixture("no-key");
  await writeTwoProfileSessions(fx);
  let requests = 0;
  const report = await runDailyMiner({
    home: fx.home,
    repoRoot: fx.repoRoot,
    stateDir: fx.stateDir,
    now: () => NOW,
    model: "jev-1.13.0",
    apiKey: "",
    fetchImpl: async () => { requests += 1; throw new Error("must not dispatch"); },
    dryRun: true,
  });
  assert.equal(report.status, "PARTIAL");
  assert.equal(report.model.status, "NOT_RUN");
  assert.equal(report.model.reason, "api-key-unavailable");
  assert.equal(report.model.calls, 0);
  assert.equal(requests, 0);
  assert.ok(report.errors.includes("jev-model-not-run"));
});

test("daily CLI persists an explicit NOT_RUN report when session roots are unavailable", async () => {
  const fx = await fixture("cli-no-sessions");
  const result = await invokeDailyCli(fx);
  assert.equal(result.code, 2, result.stderr);
  const output = parseJson(result.stdout);
  assert.equal(output.status, "NOT_RUN");
  assert.ok(output.errors.includes("session-roots-unavailable"));
  const saved = parseJson(await readFile(join(fx.stateDir, "reports", `${output.date}.json`), "utf8"));
  assert.equal(saved.status, "NOT_RUN");
  assert.equal(saved.model.calls, 0);
});

test("separate daily CLI processes resume cursors and enforce one model attempt per day", async () => {
  const fx = await fixture("cli-restart");
  await writeTwoProfileSessions(fx);
  const firstResult = await invokeDailyCli(fx);
  const first = parseJson(firstResult.stdout);
  assert.equal(firstResult.code, 1);
  assert.equal(first.status, "PARTIAL");
  assert.equal(first.model.status, "NOT_RUN");
  assert.equal(first.model.reason, "api-key-unavailable");
  const secondResult = await invokeDailyCli(fx);
  const second = parseJson(secondResult.stdout);
  assert.equal(secondResult.code, 1);
  assert.equal(second.status, "PARTIAL");
  assert.equal(second.model.status, "NOT_RUN");
  assert.equal(second.model.reason, "daily-model-call-cap");
  assert.deepEqual(second.coverage.event_counts, first.coverage.event_counts);
  assert.equal(second.coverage.files_discovered, first.coverage.files_discovered);
  assert.equal(second.coverage.files_scanned, 0, "an unchanged session file is not rescanned after restart");
  assert.deepEqual(second.clusters, first.clusters);
});
test("daily miner hashes normalized error signatures and ranks DCG blocks from the linked global inventory", async () => {
  const fx = await fixture("dcg-signature");
  const sessions = await writeTwoProfileSessions(fx);
  const dcgSkillPath = join(fx.globalSkillStore, "dcg", "SKILL.md");
  const compactSkillPath = join(fx.repoRoot, ".omp", "skills", "jev-compact", "SKILL.md");
  await mkdir(join(fx.globalSkillStore, "dcg"), { recursive: true });
  await mkdir(join(fx.repoRoot, ".omp", "skills", "jev-compact"), { recursive: true });
  await writeFile(dcgSkillPath, [
    "---",
    "name: dcg",
    "description: Handle blocked destructive commands. Use when dcg blocks rm -rf, git reset --hard, DROP DATABASE, kubectl delete, or when configuring agent safety guardrails.",
    "---",
    "",
  ].join("\n"));
  await writeFile(compactSkillPath, [
    "---",
    "name: jev-compact",
    "description: Jev-judged pre-compaction for omp sessions. Use when asked about compacting a session with calibrated keep/drop judgment, installing the compaction hook, or reading the compaction decision log.",
    "---",
    "",
  ].join("\n"));

  const dcgResult = "shell redirect to a dynamic or escaped path may truncate a sensitive file and requires human approval.\n\nRule: core.filesystem:redirect-truncate-dynamic-path";
  const pathErrors = [
    "FileNotFoundError: [Errno 2] No such file or directory: 'work/jev-claim-check/numeric-cases.jsonl'",
    "FileNotFoundError: [Errno 2] No such file or directory: 'work/jev-claim-check/numeric-v2-cases.jsonl'",
  ];
  for (const [sessionPath, pathError] of [[sessions.pathA, pathErrors[0]], [sessions.pathB, pathErrors[1]]]) {
    const rows = (await readFile(sessionPath, "utf8")).trim().split("\n").map(JSON.parse);
    for (const row of rows) {
      const message = row.message;
      const call = Array.isArray(message?.content) ? message.content.find((part) => part.type === "toolCall") : undefined;
      if (call?.id?.startsWith("bash-fail")) {
        call.arguments.command = "rm -rf /tmp/sr-cleanroom && mkdir -p /tmp/sr-cleanroom";
      } else if (message?.role === "toolResult" && message.toolCallId?.startsWith("bash-fail")) {
        message.content = dcgResult;
      } else if (message?.role === "toolResult" && message.toolCallId === "read-fail") {
        message.content = pathError;
      }
    }
    await writeFile(sessionPath, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`);
  }

  const report = await runDailyMiner({
    home: fx.home,
    repoRoot: fx.repoRoot,
    stateDir: fx.stateDir,
    now: () => NOW,
    model: "jev-1.13.0",
    apiKey: "",
    runCommand: fakeBeads([]),
  });
  const dcgCluster = report.clusters.find((cluster) => cluster.error_class === "ToolError");
  assert.equal(dcgCluster?.session_count, 2);
  assert.equal(dcgCluster?.nearest_existing_skill?.name, "dcg");
  const signature = JSON.stringify({
    dcgRuleId: "core.filesystem:redirect-truncate-dynamic-path",
    exitCodeClass: "unknown",
    firstErrorLine: "shell redirect to a dynamic or escaped path may truncate a sensitive file and requires human approval.",
  });
  const clusterKey = JSON.stringify([
    "bash",
    "ToolError",
    "bash",
    "",
    createHash("sha256").update(signature).digest("hex"),
  ]);
  assert.equal(dcgCluster?.id, `gap-${createHash("sha256").update(clusterKey).digest("hex").slice(0, 12)}`);

  const pathCluster = report.clusters.find((cluster) => cluster.error_class === "FileNotFoundError");
  assert.equal(pathCluster?.session_count, 2);
  const pathSignature = JSON.stringify({
    dcgRuleId: "",
    exitCodeClass: "unknown",
    firstErrorLine: "FileNotFoundError: [Errno <n>] No such file or directory: '<path>'",
  });
  const pathClusterKey = JSON.stringify([
    "read",
    "FileNotFoundError",
    "read",
    "py",
    createHash("sha256").update(pathSignature).digest("hex"),
  ]);
  assert.equal(pathCluster?.id, `gap-${createHash("sha256").update(pathClusterKey).digest("hex").slice(0, 12)}`);
});



test("legacy session cursors are fully reindexed before signature clusters are reused", async () => {
  const fx = await fixture("legacy-signatures");
  await writeTwoProfileSessions(fx);
  const options = {
    home: fx.home,
    repoRoot: fx.repoRoot,
    stateDir: fx.stateDir,
    now: () => NOW,
    model: "jev-1.13.0",
    apiKey: "",
    dryRun: true,
  };
  const before = await runDailyMiner(options);
  const statePath = join(fx.stateDir, "state.json");
  const state = parseJson(await readFile(statePath, "utf8"));
  for (const cursor of Object.values(state.cursors)) delete cursor.errorSignatureVersion;
  const legacyKeys = new Map();
  for (const event of state.events) {
    if (event.kind !== "failure") continue;
    const legacyKey = JSON.stringify([event.toolName, event.errorClass, event.commandFamily, event.fileExtension ?? ""]);
    legacyKeys.set(event.clusterKey, legacyKey);
    event.clusterKey = legacyKey;
    delete event.errorSignature;
  }
  for (const event of state.events) {
    if (event.kind === "retry") event.clusterKey = legacyKeys.get(event.clusterKey) ?? event.clusterKey;
  }
  await writeFile(statePath, `${JSON.stringify(state)}\n`);

  const after = await runDailyMiner(options);
  const reindexed = parseJson(await readFile(statePath, "utf8"));
  assert.deepEqual(after.coverage.event_counts, before.coverage.event_counts);
  assert.deepEqual(after.clusters, before.clusters);
  assert.equal(after.coverage.files_scanned, 2);
  assert.equal(after.errors.includes("error-signature-reindex-in-progress"), false);
  assert.equal(Object.values(reindexed.cursors).every((cursor) => cursor.errorSignatureVersion === 1), true);
});

test("LaunchAgent install schedules a bounded daily invocation and is idempotent", async () => {
  const fx = await fixture("launch-agent");
  const nodePath = "/opt/homebrew/bin/node";
  const infisicalPath = join(fx.home, ".local", "bin", "infisical");
  const plist = renderLaunchAgent({ home: fx.home, repoRoot: fx.repoRoot, nodePath, infisicalPath });
  assert.ok(plist.includes("<key>Hour</key><integer>3</integer><key>Minute</key><integer>30</integer>"));
  assert.ok(plist.includes("<string>--daily</string>"));
  assert.ok(plist.includes("42b194c3-89d7-4ebb-895f-dd77ddf005ba"));
  assert.ok(!plist.includes("TYPESAFE_API_KEY"));

  const calls = [];
  let loaded = false;
  const options = {
    home: fx.home,
    repoRoot: fx.repoRoot,
    nodePath,
    infisicalPath,
    launchctl: "launchctl-test",
    uid: 501,
    runCommand: (_command, args, cwd) => {
      calls.push({ args, cwd });
      if (args[0] === "print") return { status: loaded ? 0 : 113, stdout: "", stderr: "" };
      loaded = true;
      return { status: 0, stdout: "", stderr: "" };
    },
  };
  const first = await installLaunchAgent(options);
  assert.equal(first.status, "INSTALLED");
  assert.deepEqual(calls.map((call) => call.args[0]), ["print", "bootstrap"]);
  assert.equal(await readFile(first.path, "utf8"), plist);
  const second = await installLaunchAgent(options);
  assert.equal(second.status, "ALREADY_LOADED");
  assert.deepEqual(calls.map((call) => call.args[0]), ["print", "bootstrap", "print"]);
});

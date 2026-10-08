import {appendFileSync, chmodSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {execFileSync} from "node:child_process";
import {dirname, isAbsolute, join, relative, resolve} from "node:path";
import {fileURLToPath, pathToFileURL} from "node:url";
import {askJevBundle, setKeyProvider} from "../../kit/src/client.ts";
import {sizePreflight, SIZE_LIMIT_TOKENS} from "../../kit/src/preflight.ts";
import {infisicalKeyProvider} from "../../work/jev-client/src/infisical-key.ts";
import {CUT, RISK, STATE_CONTEXT} from "../bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_CALLS = 400;
export const MAX_INPUT_TOKENS = SIZE_LIMIT_TOKENS;
export const SPEND_CAP_USD = 0.05;
export const INPUT_PRICE_PER_MILLION = 0.042;
const QUESTIONS = RISK;
const QUESTION_KEYS = Object.keys(QUESTIONS);

function fail(message) {
  throw new Error(message);
}

function labelMap(sample, labelSet) {
  if (!labelSet || typeof labelSet.labeler_id !== "string" || !labelSet.labeler_id.trim() || !Array.isArray(labelSet.labels)) {
    fail("label set must identify its human labeler and include labels");
  }
  const sampleIds = new Set(sample.map((row) => row.event_id));
  const labels = new Map();
  for (const row of labelSet.labels) {
    if (!row || !sampleIds.has(row.event_id)) fail("label set contains an unknown event");
    if (labels.has(row.event_id)) fail("label set contains a duplicate event");
    if (row.label !== "harm" && row.label !== "no-harm") fail("labels must be harm or no-harm");
    labels.set(row.event_id, row.label);
  }
  for (const id of sampleIds) {
    if (!labels.has(id)) fail("label set is missing a sampled event");
  }
  return {labelerId: labelSet.labeler_id, labels};
}

export function resolveLabels(sample, labelSets, adjudications) {
  if (!Array.isArray(labelSets) || labelSets.length !== 2) fail("two independent human label sets are required");
  const first = labelMap(sample, labelSets[0]);
  const second = labelMap(sample, labelSets[1]);
  if (first.labelerId === second.labelerId) fail("two independent labeler IDs are required");
  if (!Array.isArray(adjudications)) fail("adjudications must be an array");
  const needsAdjudication = new Set();
  const result = new Map();
  for (const row of sample) {
    const left = first.labels.get(row.event_id);
    const right = second.labels.get(row.event_id);
    if (left === right) result.set(row.event_id, left);
    else needsAdjudication.add(row.event_id);
  }
  if (needsAdjudication.size === 0 && adjudications.length !== 0) fail("adjudication supplied for an agreed label");
  if (needsAdjudication.size > 0 && adjudications.length === 0) fail("a third independent adjudicator is required for disagreements");
  for (const row of adjudications) {
    if (!row || !needsAdjudication.has(row.event_id)) fail("adjudication contains an agreed or unknown event");
    if (result.has(row.event_id)) fail("duplicate adjudication for an event");
    if (row.label !== "harm" && row.label !== "no-harm") fail("adjudication label must be harm or no-harm");
    if (typeof row.labeler_id !== "string" || !row.labeler_id.trim()) fail("adjudication must identify its human labeler");
    if (row.labeler_id === first.labelerId || row.labeler_id === second.labelerId) fail("adjudicator must be independent of both labelers");
    result.set(row.event_id, row.label);
  }
  for (const id of needsAdjudication) {
    if (!result.has(id)) fail("disagreement is missing third-person adjudication");
  }
  return result;
}

function getCommand(commandByEventId, eventId) {
  return commandByEventId instanceof Map ? commandByEventId.get(eventId) : commandByEventId?.[eventId];
}

function validAnswers(answers) {
  if (!answers || typeof answers !== "object" || Array.isArray(answers)) return null;
  const scores = {};
  for (const key of QUESTION_KEYS) {
    const answer = answers[key];
    const score = answer?.noul;
    const confidence = answer?.confidence;
    if (answer?.type !== "noul" || !Number.isFinite(score) || score < 0 || score > 1 || !Number.isFinite(confidence) || confidence < 0 || confidence > 1) return null;
    scores[key] = score;
  }
  if (Object.keys(answers).length !== QUESTION_KEYS.length || Object.keys(answers).some((key) => !QUESTION_KEYS.includes(key))) return null;
  return scores;
}

function httpRefusal(result) {
  const error = typeof result?.error === "string" ? result.error : "";
  for (const status of [401, 402, 403]) {
    if (error.includes(`HTTP ${status}`)) return status;
  }
  return null;
}

function validInputTokens(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function makeRow(event, label, result, scores, tokens, spendUsd, status, reason, recordedAt) {
  const row = {
    event_id: event.event_id,
    cmd_sha: event.cmd_sha,
    stratum: event.stratum ?? event.dcg_decision,
    label,
    model: typeof result?.model === "string" ? result.model : MODEL,
    resolved_model: typeof result?.resolvedModel === "string" ? result.resolvedModel : null,
    recorded_at: recordedAt,
    status,
    input_tokens: tokens,
    spend_usd: spendUsd,
    latency_ms: Number.isFinite(result?.latencyMs) ? result.latencyMs : null,
  };
  if (scores) {
    row.scores = scores;
    row.max_score = Math.max(...Object.values(scores));
    row.jevFlag = row.max_score > CUT;
  }
  if (reason) row.reason = reason;
  return row;
}
export async function runSample({
  sample,
  labelSets,
  adjudications,
  commandByEventId,
  askBundle,
  appendRow,
  now = () => new Date().toISOString(),
  spendCapUsd = SPEND_CAP_USD,
  callCap = MAX_CALLS,
}) {
  if (!Array.isArray(sample)) fail("sample must be an array");
  if (typeof askBundle !== "function" || typeof appendRow !== "function") fail("askBundle and appendRow are required");
  if (!Number.isFinite(spendCapUsd) || spendCapUsd < 0 || !Number.isInteger(callCap) || callCap < 0) fail("invalid request budget");
  const ids = new Set();
  for (const event of sample) {
    if (!event || typeof event.event_id !== "string" || !event.event_id || typeof event.cmd_sha !== "string" || !event.cmd_sha) fail("sample event is missing its ID or command hash");
    if (ids.has(event.event_id)) fail("sample event IDs must be unique");
    ids.add(event.event_id);
    if (event.dcg_decision !== "deny" && event.dcg_decision !== "allow") fail("sample contains a non-eligible DCG stratum");
  }
  const labels = resolveLabels(sample, labelSets, adjudications);
  const commands = new Map();
  for (const event of sample) {
    const command = getCommand(commandByEventId, event.event_id);
    if (typeof command !== "string") fail("private command pack is missing a sampled event");
    sizePreflight({command, context: STATE_CONTEXT}, QUESTIONS);
    commands.set(event.event_id, command);
  }

  let attempts = 0;
  let inputTokens = 0;
  let spendUsd = 0;
  let stopReason = "complete";
  const maxCallUsd = MAX_INPUT_TOKENS * INPUT_PRICE_PER_MILLION / 1_000_000;
  for (const event of sample) {
    if (attempts >= callCap) {
      stopReason = "call-cap";
      break;
    }
    if (spendUsd + maxCallUsd > spendCapUsd + Number.EPSILON) {
      stopReason = "spend-cap";
      break;
    }
    attempts += 1;
    let result;
    try {
      result = await askBundle({
        state: {command: commands.get(event.event_id), context: STATE_CONTEXT},
        questions: QUESTIONS,
        model: MODEL,
        timeoutMs: 20_000,
        retry: {maxRetries: 0},
      });
    } catch {
      result = {ok: false, reason: "transport", latencyMs: null};
    }

    const refusal = httpRefusal(result);
    const reportedTokens = result?.ok && validInputTokens(result.usage?.input_tokens) ? result.usage.input_tokens : null;
    const cost = reportedTokens === null ? null : reportedTokens * INPUT_PRICE_PER_MILLION / 1_000_000;
    if (reportedTokens !== null) {
      inputTokens += reportedTokens;
      spendUsd += cost;
    }
    let scores = result?.ok && result.model === MODEL && result.resolvedModel === MODEL ? validAnswers(result.answers) : null;
    let status = scores ? "scored" : "not_scored";
    let reason = null;
    if (refusal !== null) {
      reason = `http-${refusal}`;
      stopReason = reason;
    } else if (!result?.ok) {
      reason = ["unconfigured", "billing-hold", "http", "transport", "timeout", "no-answers", "non-json"].includes(result?.reason) ? result.reason : "request-failed";
      stopReason = `request-${reason}`;
    } else if (reportedTokens === null) {
      status = "not_scored";
      scores = null;
      reason = "usage-unavailable";
      stopReason = reason;
    } else if (reportedTokens > MAX_INPUT_TOKENS) {
      status = "not_scored";
      scores = null;
      reason = "reported-input-over-limit";
      stopReason = reason;
    } else if (!scores) {
      reason = "invalid-answer-or-model";
    }
    const row = makeRow(event, labels.get(event.event_id), result, status === "scored" ? scores : null, reportedTokens, cost, status, reason, now());
    await appendRow(row);
    if (refusal !== null || !result?.ok || stopReason === "usage-unavailable" || stopReason === "reported-input-over-limit") break;
  }
  return {attempts, inputTokens, spendUsd, stopReason};
}

function sha256(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
  }
  return value;
}

function canonicalJsonl(rows) {
  return rows.length ? `${rows.map((row) => JSON.stringify(stableValue(row))).join("\n")}\n` : "";
}

function git(...args) {
  try {
    return execFileSync("git", args, {cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"]}).trim();
  } catch {
    fail("cannot verify committed X7 inputs");
  }
}

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const PREP = "work/x7-gate-rules/prepare.py";
const RUN = "work/x7-gate-rules/run.mjs";
const PREREG = "work/x7-gate-rules/unflagged-PREREG.md";
const FRAME = "work/x7-gate-rules/frame.jsonl";
const FRAME_MANIFEST = "work/x7-gate-rules/frame-manifest.json";
const SAMPLE = "work/x7-gate-rules/sample.jsonl";
const SAMPLE_MANIFEST = "work/x7-gate-rules/sample-manifest.json";
const LIVE_CONTRACT_INPUTS = [
  "work/bicameral-gate/questions.mjs",
  "kit/src/client.ts",
  "kit/src/validate.ts",
  "kit/src/preflight.ts",
  "work/jev-client/src/infisical-key.ts",
];

function assertCommittedClean(paths) {
  if (git("branch", "--show-current") !== "main") fail("X7 live calls are allowed only from main");
  const repoPaths = paths.map((path) => relative(ROOT, resolve(path)));
  if (repoPaths.some((path) => path === ".." || path.startsWith(`..${process.platform === "win32" ? "\\" : "/"}`))) fail("X7 input is outside the repository");
  git("ls-files", "--error-unmatch", "--", ...repoPaths);
  try {
    execFileSync("git", ["diff", "--quiet", "HEAD", "--", ...repoPaths], {cwd: ROOT, stdio: "ignore"});
  } catch {
    fail("required X7 input has uncommitted changes");
  }
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function parseJsonl(path) {
  return readFileSync(path, "utf8").split("\n").filter((line) => line.trim()).map((line) => JSON.parse(line));
}

function checkPrivatePack(path) {
  const resolved = resolve(path);
  const scratch = resolve(ROOT, "var", "agent-tmp");
  const rel = relative(scratch, resolved);
  if (!rel || rel.startsWith("..") || isAbsolute(rel)) fail("command pack must be under var/agent-tmp");
  const parent = dirname(resolved);
  if (!existsSync(join(parent, ".owner"))) fail("private command pack directory needs its .owner file");
  const dirMode = statSync(parent).mode & 0o777;
  const fileMode = statSync(resolved).mode & 0o777;
  if ((dirMode & 0o077) !== 0 || (fileMode & 0o077) !== 0) fail("private command pack permissions must be 0700/0600");
  return resolved;
}

function committedInputs({samplePath, sampleManifestPath, framePath, frameManifestPath, preregPath, preparePath, runPath, labelPaths}) {
  const paths = [preregPath, preparePath, runPath, ...LIVE_CONTRACT_INPUTS, framePath, frameManifestPath, samplePath, sampleManifestPath, ...labelPaths];
  assertCommittedClean(paths);
  const manifest = readJson(sampleManifestPath);
  for (const recordedCommit of [manifest.frame_commit, manifest.sample_selection_commit]) {
    if (typeof recordedCommit !== "string" || recordedCommit.length !== 40 || [...recordedCommit].some((character) => !"0123456789abcdef".includes(character))) fail("sample manifest lacks a committed input SHA");
    try {
      execFileSync("git", ["merge-base", "--is-ancestor", recordedCommit, "HEAD"], {cwd: ROOT, stdio: "ignore"});
    } catch {
      fail("sample selection input commit is not an ancestor of HEAD");
    }
  }
}

function loadInputs(options) {
  const samplePath = resolve(options.sample ?? join(ROOT, SAMPLE));
  const sampleManifestPath = resolve(options.sampleManifest ?? join(ROOT, SAMPLE_MANIFEST));
  const framePath = resolve(options.frame ?? join(ROOT, FRAME));
  const frameManifestPath = resolve(options.frameManifest ?? join(ROOT, FRAME_MANIFEST));
  const preregPath = resolve(options.prereg ?? join(ROOT, PREREG));
  const preparePath = resolve(options.prepare ?? join(ROOT, PREP));
  const runPath = resolve(options.runner ?? join(ROOT, RUN));
  const labelsAPath = resolve(options.labelsA);
  const labelsBPath = resolve(options.labelsB);
  const adjudicationsPath = options.adjudications ? resolve(options.adjudications) : null;
  const labelPaths = [labelsAPath, labelsBPath, ...(adjudicationsPath ? [adjudicationsPath] : [])];
  committedInputs({samplePath, sampleManifestPath, framePath, frameManifestPath, preregPath, preparePath, runPath, labelPaths});
  const sample = parseJsonl(samplePath);
  const sampleManifest = readJson(sampleManifestPath);
  const frameManifest = readJson(frameManifestPath);
  const frame = parseJsonl(framePath);
  if (sha256(canonicalJsonl(sample)) !== sampleManifest.sample_sha256) fail("committed sample does not match its manifest");
  if (sha256(canonicalJsonl(frame)) !== frameManifest.frame_sha256 || frameManifest.frame_sha256 !== sampleManifest.frame_sha256) fail("committed frame does not match its manifests");
  if (sampleManifest.prereg_sha256 !== sha256(readFileSync(preregPath, "utf8"))) fail("sample refers to a changed preregistration");
  if (sampleManifest.prereg_commit !== git("log", "-1", "--format=%H", "--", relative(ROOT, preregPath))) fail("sample refers to a different preregistration commit");
  if (sample.length > MAX_CALLS) fail("sample exceeds the preregistered 400-event maximum");
  const labelsA = readJson(labelsAPath);
  const labelsB = readJson(labelsBPath);
  const adjudications = adjudicationsPath ? readJson(adjudicationsPath) : [];
  const packPath = checkPrivatePack(options.commandPack);
  const packed = parseJsonl(packPath);
  if (packed.length !== sample.length) fail("private command pack does not exactly cover the sample");
  const sampleById = new Map(sample.map((row) => [row.event_id, row]));
  const commandByEventId = new Map();
  for (const row of packed) {
    const sampleRow = sampleById.get(row.event_id);
    if (!sampleRow || row.cmd_sha !== sampleRow.cmd_sha || typeof row.command !== "string") fail("private command pack has an invalid row");
    if (sha256(row.command) !== row.cmd_sha || commandByEventId.has(row.event_id)) fail("private command pack identity is invalid");
    commandByEventId.set(row.event_id, row.command);
  }
  return {sample, sampleManifest, labelSets: [labelsA, labelsB], adjudications, commandByEventId};
}

const OPTION_NAMES = new Map([
  ["--command-pack", "commandPack"],
  ["--labels-a", "labelsA"],
  ["--labels-b", "labelsB"],
  ["--adjudications", "adjudications"],
  ["--output", "output"],
  ["--sample", "sample"],
  ["--sample-manifest", "sampleManifest"],
  ["--frame", "frame"],
  ["--frame-manifest", "frameManifest"],
  ["--prereg", "prereg"],
  ["--prepare", "prepare"],
  ["--runner", "runner"],
]);

function parseArgs(argv) {
  const options = {mode: null};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") return {mode: "help"};
    if (arg === "check" || arg === "live") {
      if (options.mode !== null) fail("choose one mode: check or live");
      options.mode = arg;
    } else if (OPTION_NAMES.has(arg) && index + 1 < argv.length) {
      options[OPTION_NAMES.get(arg)] = argv[++index];
    } else {
      fail("unknown X7 runner argument");
    }
  }
  if (!options.mode) fail("choose check or live; use --help for options");
  return options;
}

function usage() {
  return [
    "Usage: node --experimental-strip-types work/x7-gate-rules/run.mjs <check|live>",
    "  --command-pack PATH --labels-a PATH --labels-b PATH [--adjudications PATH]",
    "  --output PATH [--sample PATH --sample-manifest PATH --frame PATH --frame-manifest PATH]",
    "check validates committed inputs and labels without a Jev request; live sends at most 400 single-attempt requests.",
  ].join("\n");
}

async function main(argv) {
  const options = parseArgs(argv);
  if (options.mode === "help") {
    console.log(usage());
    return 0;
  }
  if (!options.commandPack || !options.labelsA || !options.labelsB) fail("command pack and both independent label files are required");
  const inputs = loadInputs(options);
  const labels = resolveLabels(inputs.sample, inputs.labelSets, inputs.adjudications);
  if (labels.size !== inputs.sample.length) fail("human labels do not cover the frozen sample");
  if (options.mode === "check") {
    console.log(JSON.stringify({sample_rows: inputs.sample.length, frame_sha256: inputs.sampleManifest.frame_sha256, label_rows: labels.size, live_calls: 0, status: "prerequisites-valid"}));
    return 0;
  }
  if (options.mode !== "live") fail("invalid X7 mode");
  setKeyProvider(infisicalKeyProvider);
  const output = resolve(options.output ?? join(ROOT, "work/x7-gate-rules/results.jsonl"));
  if (existsSync(output)) fail("results file already exists; this runner does not resume or duplicate paid calls");
  mkdirSync(dirname(output), {recursive: true, mode: 0o700});
  writeFileSync(output, "", {flag: "wx", mode: 0o600});
  chmodSync(output, 0o600);
  let attempts = 0;
  const result = await runSample({
    ...inputs,
    askBundle: askJevBundle,
    appendRow: async (row) => {
      appendFileSync(output, `${JSON.stringify(row)}\n`, {mode: 0o600});
      attempts += 1;
    },
  });
  console.log(JSON.stringify({attempts, input_tokens: result.inputTokens, spend_usd: result.spendUsd, stop_reason: result.stopReason, result_file: relative(ROOT, output)}));
  return 0;
}


if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).then((code) => {
    process.exitCode = code;
  }).catch((error) => {
    console.error(`ERROR ${error instanceof Error ? error.message : "X7 runner failed"}`);
    process.exitCode = 2;
  });
}

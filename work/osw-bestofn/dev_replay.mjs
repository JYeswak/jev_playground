import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { askJevBundle } from "../../work/jev-client/src/index.ts";

const variant = process.argv[2];
const allowedVariants = new Set(["original", "goal", "neutral", "noul"]);
if (!allowedVariants.has(variant)) {
  throw new Error(`variant must be one of ${[...allowedVariants].join(", ")}`);
}

const statePath = process.env.OSW_STATE_FILE;
const slicePath = process.env.OSW_SLICE_FILE;
const outputPath = process.env.OSW_DEV_RECEIPT;
if (!statePath || !slicePath || !outputPath) {
  throw new Error("OSW_STATE_FILE, OSW_SLICE_FILE and OSW_DEV_RECEIPT are required");
}

const states = (await readFile(statePath, "utf8"))
  .trim()
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));
const slice = JSON.parse(await readFile(slicePath, "utf8"));
const stateByTask = new Map(states.map((state) => [state.task, state]));
const selected = slice.tasks.map((task) => {
  const state = stateByTask.get(task);
  if (!state) throw new Error(`missing state for ${task}`);
  return state;
});
const candidateCount = selected[0]?.candidates.length ?? 0;
if (candidateCount < 2 || selected.some((state) => state.candidates.length !== candidateCount)) {
  throw new Error("all selected states must have the same candidate count >= 2");
}
const model = "jev-1.13.0";
const publicClasses = Object.fromEntries(
  selected[0].candidates.map((_, index) => [`c${index}`, `Candidate ${index + 1}`]),
);
const neutralClasses = Object.fromEntries(
  Array.from({ length: candidateCount }, (_, index) => [`c${index}`, `Candidate ${index + 1}; use only its supplied action and runtime evidence`]),
);
const noneDescription = "No candidate has enough evidence of completing the stated task; abstain.";
const instructions = "Which candidate trajectory completed the stated OSWorld task? Compare the candidate action histories and final runtime evidence. Choose none when the evidence is insufficient. Do not use candidate IDs, archive names, or any result field as a proxy for correctness; judge completion of the stated task from the supplied evidence.";
const noulInstruction = "Does this candidate's supplied action history and bounded final runtime evidence establish that it completed the stated OSWorld task? Answer yes only when the evidence itself supports completion; do not use candidate IDs, archive names, or any result field as a proxy.";

function stateFor(state) {
  const { task_instruction, candidates, ...base } = state;
  const cleanCandidates = candidates.map(({ archive: _archive, ...candidate }) => candidate);
  return variant === "goal"
    ? { ...base, task_instruction, candidates: cleanCandidates }
    : { ...base, candidates: cleanCandidates };
}

function questionsFor() {
  if (variant === "noul") {
    return Object.fromEntries(
      Array.from({ length: candidateCount }, (_, index) => [
        `candidate_${index}`,
        {
          type: "noul",
          instructions: noulInstruction,
          criteria: {
            true: "The supplied evidence establishes successful completion of the stated task.",
            false: "The supplied evidence does not establish successful completion of the stated task.",
          },
        },
      ]),
    );
  }
  const classes = variant === "neutral" ? neutralClasses : publicClasses;
  return {
    choice: {
      type: "choice",
      instructions,
      criteria: { ...classes, none: noneDescription },
    },
  };
}

function validateChoice(answers, classes) {
  const answer = answers?.choice;
  if (!answer || answer.type !== "choice" || typeof answer.choice !== "string" || !(answer.choice in classes)) {
    throw new Error("malformed Choice answer");
  }
  if (!answer.probabilities || typeof answer.probabilities !== "object") throw new Error("missing Choice probabilities");
  for (const label of Object.keys(classes)) {
    const value = answer.probabilities[label];
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
      throw new Error(`invalid Choice probability for ${label}`);
    }
  }
  return { choice: answer.choice, confidence: answer.confidence, probabilities: answer.probabilities };
}

function validateNouls(answers) {
  const nouls = {};
  for (let index = 0; index < candidateCount; index += 1) {
    const answer = answers?.[`candidate_${index}`];
    if (!answer || answer.type !== "noul" || typeof answer.noul !== "number" || !Number.isFinite(answer.noul) || answer.noul < 0 || answer.noul > 1) {
      throw new Error(`malformed Noul answer for candidate_${index}`);
    }
    nouls[`c${index}`] = answer.noul;
  }
  const [choice, score] = Object.entries(nouls).sort((left, right) => right[1] - left[1])[0];
  return { choice: score >= 0.5 ? choice : "none", nouls };
}


const rows = [];
let inputTokens = 0;
let outputTokens = 0;
let failures = 0;
const resolvedModels = new Set();
const started = Date.now();
const questions = questionsFor();
for (const state of selected) {
  const result = await askJevBundle({
    model,
    state: stateFor(state),
    questions,
    timeoutMs: 20_000,
    retry: { maxRetries: 0 },
  });
  if (!result.ok) {
    failures += 1;
    rows.push({ task: state.task, ok: false, reason: result.reason, error: result.error, model: result.model, resolvedModel: null });
    continue;
  }
  resolvedModels.add(result.resolvedModel);
  const usage = result.usage ?? null;
  inputTokens += Number(usage?.input_tokens ?? 0);
  outputTokens += Number(usage?.output_tokens ?? 0);
  try {
    const judgment = variant === "noul"
      ? validateNouls(result.answers)
      : validateChoice(result.answers, { ...((variant === "neutral" ? neutralClasses : publicClasses)), none: noneDescription });
    rows.push({ task: state.task, ok: true, ...judgment, latencyMs: result.latencyMs, model: result.model, resolvedModel: result.resolvedModel, usage });
  } catch (error) {
    failures += 1;
    rows.push({ task: state.task, ok: false, reason: "validation", error: String(error), model: result.model, resolvedModel: result.resolvedModel, usage });
  }
}
const receipt = {
  variant,
  model,
  tasks: selected.length,
  slice_sha256: createHash("sha256").update(JSON.stringify({ ...slice, slice_sha256: undefined })).digest("hex"),
  source_sha: slice.source_sha,
  calls: selected.length,
  failures,
  usage: { input_tokens: inputTokens, output_tokens: outputTokens },
  spend_usd_estimate: inputTokens * 0.042 / 1_000_000,
  latency: { wall_ms: Date.now() - started },
  resolved_models: [...resolvedModels],
  rows,
};
await writeFile(outputPath, JSON.stringify(receipt, null, 2) + "\n");
console.log(JSON.stringify({ variant, tasks: receipt.tasks, calls: receipt.calls, failures, usage: receipt.usage, spend_usd_estimate: receipt.spend_usd_estimate, resolved_models: receipt.resolved_models }, null, 2));

import { readFile, writeFile } from "node:fs/promises";
import { askJevChoice } from "../../work/jev-client/src/index.ts";

const statePath = process.env.OSW_STATE_FILE ?? "/tmp/jev-osw-bestofn-states.jsonl";
const floorPath = process.env.OSW_FLOOR_RECEIPT ?? "work/osw-bestofn/floor_receipt.json";
const outputPath = process.env.OSW_LIVE_RECEIPT ?? "work/osw-bestofn/live_receipt.json";
const model = "jev-1.13.0";
const floor = JSON.parse(await readFile(floorPath, "utf8"));
const rows = floor.results_by_task;
const lines = (await readFile(statePath, "utf8")).trim().split("\n").filter(Boolean);
const classes = Object.fromEntries(
  floor.selected_archives.map((archive, index) => [`c${index}`, `Candidate ${index + 1}; public archive ${archive}`]),
);
classes.none = "No candidate has enough evidence of completing the task; abstain.";
const picks = {};
let inputTokens = 0;
let outputTokens = 0;
let latencyMs = 0;
let failures = 0;
const started = Date.now();

for (const line of lines) {
  const state = JSON.parse(line);
  const result = await askJevChoice({
    model,
    state,
    classes,
    timeoutMs: 20_000,
    instructions: "Which candidate trajectory completed the OSWorld task? Compare the candidate action histories and final runtime evidence. Choose none when the evidence is insufficient. Do not use candidate IDs, archive names, or any result field as a proxy for correctness; judge completion of the stated task from the evidence.",
  });
  if (!result.ok) {
    failures += 1;
    picks[state.task] = { ok: false, reason: result.reason, error: result.error };
    continue;
  }
  const usage = result.usage ?? {};
  inputTokens += Number(usage.input_tokens ?? 0);
  outputTokens += Number(usage.output_tokens ?? 0);
  latencyMs += result.latencyMs;
  picks[state.task] = {
    ok: true,
    choice: result.choice,
    confidence: result.confidence,
    probabilities: result.probabilities,
    latencyMs: result.latencyMs,
    usage: result.usage ?? null,
  };
}

function reward(task, choice) {
  return choice && choice !== "none" ? Number(rows[task]?.[floor.selected_archives[Number(choice.slice(1))]] ?? 0) : 0;
}
function exact(task, choice) {
  return reward(task, choice) >= 1.0 ? 1 : 0;
}
function exactMcNemar(baselineChoice) {
  let b = 0;
  let c = 0;
  for (const task of Object.keys(rows)) {
    const a = exact(task, picks[task]?.choice);
    const d = exact(task, baselineChoice(task));
    if (a === 1 && d === 0) b += 1;
    if (a === 0 && d === 1) c += 1;
  }
  const n = b + c;
  if (n === 0) return { b, c, p: 1 };
  let tail = 0;
  for (let k = 0; k <= Math.min(b, c); k += 1) tail += binomial(n, k) / 2 ** n;
  return { b, c, p: Math.min(1, 2 * tail) };
}
function binomial(n, k) {
  let value = 1;
  for (let i = 1; i <= k; i += 1) value = (value * (n - i + 1)) / i;
  return value;
}
const selectedRewardSum = Object.keys(rows).reduce((sum, task) => sum + reward(task, picks[task]?.choice), 0);
const selectedExactTasks = Object.keys(rows).reduce((sum, task) => sum + exact(task, picks[task]?.choice), 0);
const best = Number(floor.best_single_reward_sum);
const oracle = Number(floor.oracle_reward_sum);
const claims = Number(floor.floors.claims_success.reward_sum);
const bestChoice = () => floor.best_single_archive;
const claimsChoice = (task) => floor.picks[task].claims_success;
const delta = selectedRewardSum / floor.tasks - best / floor.tasks;
const gap = oracle / floor.tasks - best / floor.tasks;
const deltaVsClaims = selectedRewardSum / floor.tasks - claims / floor.tasks;
const receipt = {
  model,
  tasks: floor.tasks,
  n_candidates: floor.n,
  selected_archives: floor.selected_archives,
  calls: lines.length,
  failures,
  selected_reward_sum: selectedRewardSum,
  selected_mean_reward: selectedRewardSum / floor.tasks,
  selected_exact_tasks: selectedExactTasks,
  best_single_reward_sum: best,
  best_single_mean_reward: best / floor.tasks,
  oracle_reward_sum: oracle,
  oracle_mean_reward: oracle / floor.tasks,
  delta_vs_best_single: delta,
  gap_closed: gap === 0 ? null : delta / gap,
  mcnemar_vs_best_single: exactMcNemar(bestChoice),
  claims_success_reward_sum: claims,
  claims_success_mean_reward: claims / floor.tasks,
  delta_vs_claims_success: deltaVsClaims,
  mcnemar_vs_claims_success: exactMcNemar(claimsChoice),
  usage: { input_tokens: inputTokens, output_tokens: outputTokens },
  latency: { total_ms: latencyMs, mean_ms: latencyMs / Math.max(1, lines.length), wall_ms: Date.now() - started },
  spend_usd_estimate: inputTokens * 0.042 / 1_000_000,
  picks,
  raw_state_committed: false,
};
await writeFile(outputPath, JSON.stringify(receipt, null, 2) + "\n");
console.log(JSON.stringify({
  tasks: receipt.tasks,
  calls: receipt.calls,
  failures: receipt.failures,
  selected_reward_sum: receipt.selected_reward_sum,
  selected_mean_reward: receipt.selected_mean_reward,
  selected_exact_tasks: receipt.selected_exact_tasks,
  delta_vs_best_single: receipt.delta_vs_best_single,
  gap_closed: receipt.gap_closed,
  mcnemar_vs_best_single: receipt.mcnemar_vs_best_single,
  delta_vs_claims_success: receipt.delta_vs_claims_success,
  mcnemar_vs_claims_success: receipt.mcnemar_vs_claims_success,
  usage: receipt.usage,
  spend_usd_estimate: receipt.spend_usd_estimate,
}, null, 2));

import { createHash } from "node:crypto";
import { performance } from "node:perf_hooks";
import { validateContract, type DecisionContract, type SafeAction } from "./contracts.ts";

export type BackendAnswer = {
  choice?: string;
  probabilities?: Record<string, number>;
  modelId?: string;
  costUsd?: number | null;
};

export type AdapterRequest = {
  state: Record<string, unknown>;
  question: DecisionContract["question"];
  signal: AbortSignal;
};

export type BackendAdapter = {
  id: string;
  modelId: string;
  probabilities: "required" | "unsupported";
  usesTransport?: boolean;
  evaluate: (request: AdapterRequest, transport: (request: AdapterRequest) => Promise<BackendAnswer>) => Promise<BackendAnswer>;
};

export type DecisionLogRow = {
  backend_id: string;
  model_id: string;
  latency_ms: number;
  cost_usd: number | null;
  input_sha256: string | null;
  status: string;
  action: SafeAction;
  reason?: string;
};

export type DecisionResult = {
  status: "answered" | "refused" | "timeout" | "transport-error" | "daily-cap";
  action: SafeAction;
  reason?: string;
  choice?: string;
  probabilities?: Record<string, number>;
  backendId: string;
  modelId: string;
  latencyMs: number;
  costUsd: number | null;
  result?: unknown;
  logRow: DecisionLogRow;
};

export type DecideOptions = {
  contract: DecisionContract | unknown;
  adapter: BackendAdapter;
  state: Record<string, unknown>;
  result?: unknown;
  callsUsedToday?: number;
  transport: (request: AdapterRequest) => Promise<BackendAnswer>;
  logger?: (row: DecisionLogRow) => void;
};

const record = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (record(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  const encoded = JSON.stringify(value);
  if (encoded === undefined) throw new TypeError("state contains a non-JSON value");
  return encoded;
}

function probabilityError(answer: BackendAnswer, contract: DecisionContract, adapter: BackendAdapter): string | undefined {
  const options = contract.question.options;
  if (!options) return undefined;
  if (typeof answer.choice !== "string" || !Object.hasOwn(options, answer.choice)) return "choice-out-of-options";
  if (adapter.probabilities === "unsupported" && answer.probabilities === undefined) return undefined;
  if (answer.probabilities === undefined) return "probabilities-missing";
  const ids = Object.keys(options);
  const probabilities = answer.probabilities;
  if (!record(probabilities) || Object.keys(probabilities).length !== ids.length ||
    ids.some((id) => !Object.hasOwn(probabilities, id))) return "probabilities-invalid-shape";
  let total = 0;
  let maximum = -Infinity;
  for (const id of ids) {
    const probability = probabilities[id];
    if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) return "probabilities-invalid-value";
    total += probability;
    if (probability > maximum) maximum = probability;
  }
  if (Math.abs(total - 1) > 0.02 + Number.EPSILON * 2) return "probabilities-do-not-sum-to-one";
  if ((probabilities[answer.choice] as number) < maximum) return "choice-not-max-probability";
  return undefined;
}

function stateError(state: unknown, contract: DecisionContract): string | undefined {
  if (!record(state)) return "state-invalid";
  const allowed = new Set(contract.state.privacy_allowlist);
  if (Object.keys(state).some((key) => !allowed.has(key))) return "state-not-allowlisted";
  if (contract.state.fields.some((field) => !Object.hasOwn(state, field))) return "state-missing-field";
  try {
    if (new TextEncoder().encode(canonicalJson(state)).byteLength > contract.state.maximum_state_text_bytes) return "state-too-large";
  } catch {
    return "state-invalid";
  }
  return undefined;
}

export async function decide(options: DecideOptions): Promise<DecisionResult> {
  const contract = validateContract(options.contract);
  const started = performance.now();
  let answer: BackendAnswer | undefined;
  let stateHash: string | null;
  try {
    stateHash = createHash("sha256").update(canonicalJson(options.state)).digest("hex");
  } catch {
    stateHash = null;
  }

  const finish = (status: DecisionResult["status"], action: SafeAction, reason?: string): DecisionResult => {
    const latencyMs = Math.max(0, performance.now() - started);
    const modelId = answer?.modelId ?? options.adapter.modelId;
    const costUsd = typeof answer?.costUsd === "number" && Number.isFinite(answer.costUsd) && answer.costUsd >= 0 ? answer.costUsd : null;
    const logRow: DecisionLogRow = {
      backend_id: options.adapter.id,
      model_id: modelId,
      latency_ms: latencyMs,
      cost_usd: costUsd,
      input_sha256: stateHash,
      status,
      action,
      ...(reason ? { reason } : {}),
    };
    options.logger?.(logRow);
    return {
      status,
      action,
      ...(reason ? { reason } : {}),
      ...(answer?.choice ? { choice: answer.choice } : {}),
      ...(answer?.probabilities ? { probabilities: answer.probabilities } : {}),
      backendId: options.adapter.id,
      modelId,
      latencyMs,
      costUsd,
      ...(action === "pass" && options.result !== undefined ? { result: options.result } : {}),
      logRow,
    };
  };

  const invalidState = stateError(options.state, contract);
  if (invalidState) return finish("refused", contract.safe_side, invalidState);
  if ((options.callsUsedToday ?? 0) >= contract.budget.daily_call_cap) {
    return finish("daily-cap", contract.budget.cap_reached_action, "daily-cap");
  }

  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timedOut = Symbol("timed-out");
  const timeout = new Promise<typeof timedOut>((resolve) => {
    timer = setTimeout(() => {
      controller.abort();
      resolve(timedOut);
    }, contract.budget.latency_budget_ms);
  });
  try {
    const pending = Promise.resolve().then(() => options.adapter.evaluate(
      { state: options.state, question: contract.question, signal: controller.signal },
      options.transport,
    ));
    const result = await Promise.race([pending, timeout]);
    if (result === timedOut) return finish("timeout", contract.safe_side, "timeout");
    answer = result;
    const invalidAnswer = probabilityError(answer, contract, options.adapter);
    if (invalidAnswer) return finish("refused", contract.safe_side, invalidAnswer);
    if (answer.costUsd !== undefined && answer.costUsd !== null &&
      (typeof answer.costUsd !== "number" || !Number.isFinite(answer.costUsd) || answer.costUsd < 0)) {
      return finish("refused", contract.safe_side, "cost-invalid");
    }
    const action = contract.question.options?.[answer.choice ?? ""]?.action ?? contract.safe_side;
    return finish("answered", action);
  } catch (error) {
    const code = record(error) ? error.code : undefined;
    const reason = code === "missing-key" ? "missing-key" : "transport";
    return finish("transport-error", contract.safe_side, reason);
  } finally {
    clearTimeout(timer);
  }
}

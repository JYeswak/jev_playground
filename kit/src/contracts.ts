export type SurfaceType = "command-gate" | "result-screen" | "memory-screen" | "advisory";
export type SafeAction = "pass" | "refuse";
export type ContractOption = { description: string; action: SafeAction };

export type DecisionContract = {
  family: string;
  question: {
    type: "choice" | "score" | "noul" | "rule";
    instructions: string;
    decision: string;
    options?: Record<string, ContractOption>;
  };
  state: {
    fields: string[];
    privacy_allowlist: string[];
    maximum_state_text_bytes: number;
    raw_transcript_allowed: false;
  };
  surface_type: SurfaceType;
  safe_side: SafeAction;
  budget: {
    latency_budget_ms: number;
    daily_call_cap: number;
    cap_reached_action: SafeAction;
  };
  labels: { source: string; [key: string]: unknown };
  bar: { source: string; [key: string]: unknown };
  host: string;
  consumer: string;
};

const record = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const fail = (field: string, message: string): never => {
  throw new TypeError(`contract.${field}: ${message}`);
};

const nonempty = (value: unknown): value is string => typeof value === "string" && value.trim().length > 0;
const safeActions = ["pass", "refuse"] as const;
const surfaces = ["command-gate", "result-screen", "memory-screen", "advisory"] as const;
const questionTypes = ["choice", "score", "noul", "rule"] as const;

function isHex(value: string): boolean {
  return value.length >= 7 && value.length <= 40 && [...value].every((char) => "0123456789abcdefABCDEF".includes(char));
}

export function validateContract(value: unknown): DecisionContract {
  if (!record(value)) return fail("", "must be an object");
  const contract = value;
  for (const field of ["family", "host", "consumer"] as const) {
    if (!nonempty(contract[field])) return fail(field, "is required and must be non-empty");
  }
  if (!record(contract.question)) return fail("question", "must be an object");
  const question = contract.question;
  if (!questionTypes.includes(question.type as (typeof questionTypes)[number])) return fail("question.type", "is unsupported");
  if (!nonempty(question.instructions)) return fail("question.instructions", "is required");
  if (!nonempty(question.decision)) return fail("question.decision", "is required");
  if (question.type === "choice") {
    if (!record(question.options) || Object.keys(question.options).length < 2) return fail("question.options", "choice questions need at least two options");
    for (const [id, option] of Object.entries(question.options)) {
      if (!id || !record(option) || !nonempty(option.description) || !safeActions.includes(option.action as SafeAction)) {
        return fail(`question.options.${id}`, "needs a description and pass/refuse action");
      }
    }
  }
  if (!record(contract.state)) return fail("state", "must be an object");
  const state = contract.state;
  const fields = state.fields;
  if (!Array.isArray(fields) || fields.length === 0 || !fields.every(nonempty)) return fail("state.fields", "must list fields");
  const privacyAllowlist = state.privacy_allowlist;
  if (!Array.isArray(privacyAllowlist) || privacyAllowlist.length === 0 || !privacyAllowlist.every(nonempty)) return fail("state.privacy_allowlist", "must list allowed fields");
  if (!privacyAllowlist.every((field: string) => fields.includes(field))) return fail("state.privacy_allowlist", "must be a subset of state.fields");
  if (!Number.isSafeInteger(state.maximum_state_text_bytes) || (state.maximum_state_text_bytes as number) < 1) return fail("state.maximum_state_text_bytes", "must be a positive integer");
  if (state.raw_transcript_allowed !== false) return fail("state.raw_transcript_allowed", "must be false");
  if (!surfaces.includes(contract.surface_type as SurfaceType)) return fail("surface_type", "is unsupported");
  if (!safeActions.includes(contract.safe_side as SafeAction)) return fail("safe_side", "must be pass or refuse");
  if (contract.surface_type !== "command-gate" && contract.safe_side !== "pass") return fail("safe_side", "screen and advisory surfaces must fail open with pass");
  if (!record(contract.budget)) return fail("budget", "must be an object");
  const budget = contract.budget;
  if (!Number.isSafeInteger(budget.latency_budget_ms) || (budget.latency_budget_ms as number) < 1) return fail("budget.latency_budget_ms", "must be a positive integer");
  if (!Number.isSafeInteger(budget.daily_call_cap) || (budget.daily_call_cap as number) < 0) return fail("budget.daily_call_cap", "must be a non-negative integer");
  if (!safeActions.includes(budget.cap_reached_action as SafeAction)) return fail("budget.cap_reached_action", "must be pass or refuse");
  if (contract.surface_type !== "command-gate" && budget.cap_reached_action !== "pass") return fail("budget.cap_reached_action", "screens and advisory surfaces must pass at the cap");
  if (budget.cap_reached_action === "refuse") {
    const evidence = record(contract.bar) ? contract.bar.cap_never_reached_evidence : undefined;
    if (contract.surface_type !== "command-gate" || !record(evidence)) return fail("budget.cap_reached_action", "refusal requires command-gate never-reached evidence");
    const cap = budget.daily_call_cap as number;
    if (!nonempty(evidence.source) || !nonempty(evidence.commit) || !isHex(evidence.commit) ||
      !Number.isSafeInteger(evidence.max_observed_per_session) || (evidence.max_observed_per_session as number) >= cap) {
      return fail("bar.cap_never_reached_evidence", "must cite a commit and an observed per-session maximum below the cap");
    }
  }
  if (!record(contract.labels) || !nonempty(contract.labels.source)) return fail("labels.source", "is required");
  if (!record(contract.bar) || !nonempty(contract.bar.source)) return fail("bar.source", "is required");
  return contract as unknown as DecisionContract;
}

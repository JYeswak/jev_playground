// Routing policy from docs-mirror/typesafe/cookbooks/llm_guardrails.md.
// TypeSafe returns probabilities. This file decides pass, review, block, or support.

export const HAZARD_ACTION = {
  jailbreak: "block",
  broke_policy: "block",
  harmful_request: "block",
  medical_advice: "review",
  self_harm: "support",
};

export const PRECEDENCE = ["support", "block", "review", "pass"];

export const POLICIES = {
  strict: { review_threshold: 0.35, action_threshold: 0.7, severity_block: 2 },
  permissive: { review_threshold: 0.35, action_threshold: 0.85, severity_block: 2 },
};

export function route(nouls, severity, policy) {
  const triggered = [];
  for (const [hazard, probability] of Object.entries(nouls)) {
    if (probability >= policy.action_threshold) triggered.push(HAZARD_ACTION[hazard] ?? "review");
    else if (probability >= policy.review_threshold) triggered.push("review");
  }
  const actions =
    severity >= policy.severity_block
      ? triggered.map((action) => (action === "review" ? "block" : action))
      : triggered;
  return PRECEDENCE.find((action) => actions.includes(action)) ?? "pass";
}

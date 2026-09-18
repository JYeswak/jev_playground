import { scan } from './redact.mjs';

// Pre-action gate: transcript in, typed verdict out. Never throws on
// judgment input; only on programmer errors (missing policy shape).
// Outcome space: pass | pass-through | withhold | escalate | block | error.
export async function judge({ tool_call, state, policy, asker }) {
  if (!tool_call || typeof tool_call.name !== 'string' || !tool_call.name) {
    return { outcome: 'error', reason_code: 'empty-input', jev_called: false, probability: null };
  }
  if (!policy.scope_tools.includes(tool_call.name)) {
    return { outcome: 'pass-through', reason_code: 'scoped-out', jev_called: false, probability: null };
  }

  const flat = JSON.stringify({ args: tool_call.arguments ?? {}, state: (state ?? []).slice(-policy.state_window_messages) });

  // Deterministic block patterns are authored against raw command text
  // (anchors like /$ never match inside JSON serialization), so bash is
  // matched on its command string; other tools on serialized arguments.
  const args = tool_call.arguments ?? {};
  const haystack = tool_call.name === 'bash' && typeof args.command === 'string'
    ? args.command
    : JSON.stringify(args);
  for (const rule of policy.deterministic_block_patterns) {
    if (new RegExp(rule.pattern).test(haystack)) {
      return { outcome: 'block', reason_code: `deterministic-block:${rule.id}`, jev_called: false, probability: null };
    }
  }

  const found = scan(flat);
  if (found.credential_present) {
    return {
      outcome: 'withhold',
      reason_code: 'credential-present',
      jev_called: false,
      probability: null,
      redactions: found.hits.map((h) => ({ pattern_id: h.pattern_id, span_hash: h.span_hash })),
    };
  }

  const windowed = (state ?? []).slice(-policy.state_window_messages);
  const questions = {
    licensed: {
      type: 'noul',
      instructions: `${policy.question.instructions}\nTool call: ${JSON.stringify(tool_call)}\nEvidence: <${windowed.length} most recent messages in state>`,
      criteria: { true: policy.question.criteria_true, false: policy.question.criteria_false },
    },
  };
  let p;
  try {
    const response = await asker.ask({ redacted_context: found.redacted }, questions);
    p = readNoul(response);
  } catch (err) {
    return { outcome: 'withhold', reason_code: 'asker-malformed', jev_called: true, probability: null, detail: String(err?.message ?? err) };
  }
  if (p >= policy.mapping.pass_at_or_above) {
    return { outcome: 'pass', reason_code: 'licensed', jev_called: true, probability: p };
  }
  if (p >= policy.mapping.escalate_below) {
    return { outcome: 'withhold', reason_code: 'low-confidence', jev_called: true, probability: p };
  }
  return { outcome: 'escalate', reason_code: 'high-risk-unlicensed', jev_called: true, probability: p };
}

function readNoul(response) {
  const a = response?.answers?.licensed;
  if (!a || !('noul' in a) || typeof a.noul !== 'number' || !Number.isFinite(a.noul)) {
    throw new Error('Invalid Jev answer for licensed');
  }
  return a.noul;
}

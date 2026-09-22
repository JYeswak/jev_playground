import { createHash, randomUUID } from 'node:crypto';
import { createSystemOneClassify } from './classify-systemone.mjs';

const SCHEMA_VERSION = 1;
const DECISION_TYPE = 'com.zeststream.omp-jev-observer.decision.v1';
const DIAGNOSTIC_TYPE = 'com.zeststream.omp-jev-observer.diagnostic.v1';

function stable(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(',')}}`;
}
function digest(value) { return createHash('sha256').update(stable(value)).digest('hex'); }
function raw(value) { try { return JSON.stringify(value); } catch { return '[unserializable]'; } }

/**
 * Append one row to the host, never throwing into it.
 *
 * WAS MISSING ENTIRELY. §16's dogfood (docs/demos/upstream-repro/waved-s16-observer-dogfood-20260920.md,
 * 11ff17b) found four call sites — lines 61, 71, 88, 91 — and zero definitions, so the FIRST
 * tool_call threw ReferenceError into the outer catch and the observer produced deterministic
 * total silence. No shipped-tree run had ever emitted a row; the lab's n=1 claim had run against
 * an older deployed copy. Silence read as "observing quietly" for an entire session.
 *
 * An observer must never break its host, so a failed append is swallowed — but that is exactly
 * what hid this defect, which is why the package now has a test asserting rows ARE produced
 * rather than asserting nothing throws.
 */
async function safeAppend(pi, type, data) {
  try {
    await pi.appendEntry(type, data);
    return true;
  } catch {
    return false;
  }
}
function makeRecord(command, error, context, latencyMs, toolCallId, costUsd) {
  if (typeof toolCallId !== 'string' || toolCallId.length === 0) throw new TypeError('toolCallId required');
  const sessionId = context?.sessionId;
  return { schemaVersion: SCHEMA_VERSION, recordType: 'decision', decisionId: randomUUID(), timestamp: new Date().toISOString(), ...(sessionId ? { sessionId } : {}), tool: 'bash', toolCallId, argsDigest: digest({ command }), questionSet: ['privilege widening', 'secret staging', 'irreversible publication', 'security-control tampering'], probabilities: { flag: null, pass: null }, latencyMs, ...(costUsd === undefined ? {} : { costUsd }), error };
}
export function withTimeout(promise, timeoutMs) {
  let timer;
  const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`observer timeout after ${timeoutMs}ms`)), timeoutMs); });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

 /**
 * The JEV_OBSERVER_ENDPOINT fallback is an operator-configured LOCAL webhook,
 * not the TypeSafe API — routing it via work/jev-client askJev would redirect
 * local traffic to the vendor and break offline use (same exempt class as
 * gate-44's local-server exemption). It stays fetch(). What askJev owns and
 * this must match: a malformed answer never becomes a score. Non-numeric
 * flag/pass become null (no score); a missing probabilities object throws
 * into the error row.
 */
function checkedEndpointBody(body) {
  const probs = body?.probabilities;
  if (!probs || typeof probs !== 'object') throw new Error('Invalid endpoint answer: probabilities missing');
  const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);
  const out = {
    questionSet: Array.isArray(body.questionSet) ? body.questionSet : ['observer flag question'],
    probabilities: { flag: num(probs.flag), pass: num(probs.pass) },
  };
  if (typeof body.costUsd === 'number' && Number.isFinite(body.costUsd)) out.costUsd = body.costUsd;
  return out;
}
export function createObserver({ logger, dcg, classify, enabled = true, timeoutMs = 750, now = () => new Date().toISOString(), diagnostic = async () => {} }) {
  let rawEmitted = false;
  return async function observeToolCall(event, context = {}) {
    try {
      if (!rawEmitted) { rawEmitted = true; await diagnostic({ kind: 'tool_call_observed', event: raw(event) }); }
      if (!enabled || (event?.toolName ?? event?.name) !== 'bash') return undefined;
      const command = event?.input?.command ?? event?.command ?? event?.input?.cmd;
      if (typeof command !== 'string' || command.length === 0) return undefined;
      const gate = await dcg(event, context);
      const verdict = typeof gate === 'string' ? gate : gate?.verdict;
      if (verdict === 'block') return undefined;
      const started = performance.now();
      let result;
      try { result = await withTimeout(classify({ command, event, context }), timeoutMs); } catch (error) { result = { questionSet: ['observer flag question'], probabilities: { flag: null, pass: null }, error: String(error) }; }
      try { await logger.append({ ...makeRecord(command, result.error ?? null, context, performance.now() - started, event?.toolCallId, result.costUsd), timestamp: now(), questionSet: result.questionSet, probabilities: result.probabilities }); } catch {}
      return undefined;
    } catch { return undefined; }
  };
}
export async function installObserver(pi, options = {}) {
  const endpoint = options.endpoint ?? process.env.JEV_OBSERVER_ENDPOINT;
  let classify = options.classify;
  if (!classify) {
    if (process.env.TYPESAFE_API_KEY) {
      classify = await createSystemOneClassify({ apiKey: process.env.TYPESAFE_API_KEY, model: process.env.JEV_OBSERVER_MODEL });
      classify = async ({ command }) => {
        const response = await fetch(endpoint, { method: 'POST', body: JSON.stringify({ command }), signal: AbortSignal.timeout(options.timeoutMs ?? 750) });
        if (!response.ok) throw new Error(`Jev HTTP ${response.status}`);
        return checkedEndpointBody(await response.json());
      };
    } else {
      classify = async () => { throw new Error('TYPESAFE_API_KEY (preferred) or JEV_OBSERVER_ENDPOINT is not configured'); };
    }
  }
  const observer = createObserver({ enabled: options.enabled ?? process.env.OMP_JEV_OBSERVER_DISABLED !== '1', timeoutMs: options.timeoutMs ?? 750, classify, dcg: options.dcg ?? (async (_e, context) => context.dcgVerdict), logger: options.logger ?? { append: (record) => safeAppend(pi, DECISION_TYPE, record) }, diagnostic: options.diagnostic ?? ((data) => safeAppend(pi, DIAGNOSTIC_TYPE, data)) });
  pi.on('tool_call', observer);
}
export default function ompJevObserver(pi) {
  const enabled = process.env.OMP_JEV_OBSERVER_DISABLED !== '1';
  const endpoint = process.env.JEV_OBSERVER_ENDPOINT;
  pi.on('tool_call', async (event, context = {}) => {
    try {
      const toolName = event?.toolName ?? event?.name;
      const command = event?.input?.command ?? event?.command ?? event?.input?.cmd;
      await safeAppend(pi, DIAGNOSTIC_TYPE, { kind: 'tool_call_observed', toolName, event: raw(event) });
      if (!enabled || toolName !== 'bash' || typeof command !== 'string' || command.length === 0) return undefined;
      if (context?.dcgVerdict === 'block') return undefined;
      const started = performance.now();
      let error = null;
      try {
        let result;
        if (process.env.TYPESAFE_API_KEY) {
          const classify = await createSystemOneClassify({ apiKey: process.env.TYPESAFE_API_KEY, model: process.env.JEV_OBSERVER_MODEL });
          result = await classify({ command });
        } else if (endpoint) {
          const response = await fetch(endpoint, { method: 'POST', body: JSON.stringify({ command }), signal: AbortSignal.timeout(750) });
          if (!response.ok) throw new Error(`Jev HTTP ${response.status}`);
          result = checkedEndpointBody(await response.json());
        } else {
          throw new Error('TYPESAFE_API_KEY (preferred) or JEV_OBSERVER_ENDPOINT is not configured');
        }
        await safeAppend(pi, DECISION_TYPE, { ...makeRecord(command, null, context, performance.now() - started, event?.toolCallId, result.costUsd), questionSet: result.questionSet, probabilities: result.probabilities });
        return undefined;
      } catch (caught) { error = String(caught); }
      await safeAppend(pi, DECISION_TYPE, makeRecord(command, error, context, performance.now() - started, event?.toolCallId));
      return undefined;
    } catch { return undefined; }
  });
}

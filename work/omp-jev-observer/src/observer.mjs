import { decisionRecord } from '../../dogfood-logger/src/logger.mjs';

export function withTimeout(promise, timeoutMs) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`observer timeout after ${timeoutMs}ms`)), timeoutMs);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

export function createObserver({ logger, dcg, classify, enabled = true, timeoutMs = 750, now = () => new Date().toISOString() }) {
  return async function observeToolCall(event, context = {}) {
    try {
      if (!enabled || event?.toolName !== 'bash') return undefined;
      const command = event?.input?.command;
      if (typeof command !== 'string' || command.length === 0) return undefined;
      const gate = await dcg(event, context);
      const verdict = typeof gate === 'string' ? gate : gate?.verdict;
      if (verdict === 'block') return undefined;
      const started = performance.now();
      const decisionId = crypto.randomUUID();
      let result;
      try {
        result = await withTimeout(classify({ command, event, context }), timeoutMs);
      } catch (error) {
        result = {
          questionSet: ['observer flag question'],
          probabilities: { flag: null, pass: null },
          costUsd: 0,
          error: String(error),
        };
      }
      await logger.append(decisionRecord({
        decisionId,
        timestamp: now(),
        sessionId: context.sessionId ?? 'unknown',
        tool: 'bash',
        args: { command },
        dcgVerdict: verdict ?? 'unknown',
        questionSet: result.questionSet,
        probabilities: result.probabilities,
        latencyMs: performance.now() - started,
        costUsd: result.costUsd ?? 0,
        error: result.error ?? null,
      }));
      return undefined;
    } catch {
      return undefined;
    }
  };
}

export function installObserver(pi, options = {}) {
  const enabled = options.enabled ?? process.env.OMP_JEV_OBSERVER_DISABLED !== '1';
  const appendEntry = pi.appendEntry;
  const logger = options.logger ?? {
    append: async (record) => {
      if (typeof appendEntry !== 'function') return false;
      try {
        await appendEntry('com.zeststream.omp-jev-observer.decision.v1', record);
        return true;
      } catch {
        return false;
      }
    },
  };
  const endpoint = options.endpoint ?? process.env.JEV_OBSERVER_ENDPOINT;
  const classify = options.classify ?? (async ({ command }) => {
    if (!endpoint) throw new Error('JEV_OBSERVER_ENDPOINT is not configured');
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ command }),
    });
    if (!response.ok) throw new Error(`Jev HTTP ${response.status}`);
    return await response.json();
  });
  const dcg = options.dcg ?? (async (_event, context) => context.dcgVerdict ?? 'unknown');
  pi.on('tool_call', createObserver({
    logger,
    dcg,
    classify,
    enabled,
    timeoutMs: options.timeoutMs ?? 750,
  }));
}

export default function ompJevObserver(pi) {
  installObserver(pi);
}

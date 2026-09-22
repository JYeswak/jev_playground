/**
 * Screen decision log for jev_screen (bead jev-v6j).
 *
 * Schema (committed here, versioned by SCREEN_SCHEMA_VERSION):
 *   { schemaVersion: 1, recordType: 'com.zeststream.jev-screen.screen.v1',
 *     screenId, timestamp, sessionId, verdict, p, latencyMs, textHash }
 * verdict ∈ {flag, pass, review}; p is the tool's probability or null;
 * latencyMs is the tool's reported latency or null.
 *
 * PRIVACY — what is stored and what is NOT:
 *   STORED: verdict, probability, latency, sha256 hash of the screened text,
 *     session id (links rows within one session only), timestamp.
 *   NEVER STORED: the screened text itself (only its hash), API keys,
 *     model internals, or anything outside the row above. Full input text
 *     lives only where session logging already covers it (the omp session),
 *     never in this log. Log file is created 0600 via JsonlDecisionLog.
 *
 * Fail-open: a logging failure never alters or blocks the screen verdict —
 * recordingScreen returns the tool's result object by reference, unchanged.
 */
import { randomUUID } from 'node:crypto';
import { JsonlDecisionLog, digest } from '../dogfood-logger/src/logger.mjs';

export const SCREEN_SCHEMA_VERSION = 1;
export const SCREEN_RECORD_TYPE = 'com.zeststream.jev-screen.screen.v1';

export function screenRecord({ sessionId, verdict, probability = null, latencyMs = null, text = '', timestamp = new Date().toISOString(), screenId = randomUUID() }) {
  if (!sessionId) throw new TypeError('sessionId required');
  if (!['flag', 'pass', 'review'].includes(verdict)) throw new TypeError(`unknown verdict: ${verdict}`);
  return {
    schemaVersion: SCREEN_SCHEMA_VERSION,
    recordType: SCREEN_RECORD_TYPE,
    screenId,
    timestamp,
    sessionId,
    verdict,
    p: probability,
    latencyMs,
    textHash: digest({ text }),
  };
}

/**
 * Wrap a jev_screen-like tool ({ execute(id, params) }) with logging.
 * The tool's result is returned by REFERENCE, unchanged — logging observes.
 */
export function recordingScreen(tool, { log, sessionId }) {
  if (!tool || typeof tool.execute !== 'function') throw new TypeError('tool with execute() required');
  if (!log || typeof log.append !== 'function') throw new TypeError('log with append() required');
  if (!sessionId) throw new TypeError('sessionId required');
  return {
    ...tool,
    async execute(id, params) {
      const result = await tool.execute(id, params);
      const details = result?.details ?? {};
      await log.append(screenRecord({
        sessionId,
        verdict: ['flag', 'pass', 'review'].includes(details.verdict) ? details.verdict : 'review',
        probability: typeof details.probability === 'number' ? details.probability : null,
        latencyMs: typeof details.latencyMs === 'number' ? details.latencyMs : null,
        text: typeof params?.text === 'string' ? params.text : '',
      }));
      return result;
    },
  };
}

export { JsonlDecisionLog };

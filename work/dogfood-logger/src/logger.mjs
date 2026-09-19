import { createHash, randomUUID } from 'node:crypto';
import { mkdir, open, rename, stat } from 'node:fs/promises';
import { dirname } from 'node:path';

export const SCHEMA_VERSION = 1;

function stable(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  return `{${Object.keys(value).sort().map((k) => `${JSON.stringify(k)}:${stable(value[k])}`).join(',')}}`;
}

export function digest(value) {
  return createHash('sha256').update(stable(value)).digest('hex');
}

export function decisionRecord({ sessionId, tool, args, dcgVerdict, questionSet, probabilities, latencyMs = null, costUsd = null, error = null, timestamp = new Date().toISOString(), decisionId = randomUUID() }) {
  if (!decisionId) throw new TypeError('decisionId required');
  if (!sessionId || !tool) throw new TypeError('sessionId and tool required');
  return {
    schemaVersion: SCHEMA_VERSION,
    recordType: 'decision',
    decisionId,
    timestamp,
    sessionId,
    tool,
    argsDigest: digest(args ?? null),
    dcgVerdict,
    questionSet,
    probabilities,
    latencyMs,
    costUsd,
    error,
  };
}

export function outcomeRecord({ decisionId, status, exitStatus = null, timestamp = new Date().toISOString(), error = null }) {
  if (!decisionId) throw new TypeError('decisionId required');
  if (!['proceeded', 'cancelled', 'failed'].includes(status)) throw new TypeError('invalid outcome status');
  return { schemaVersion: SCHEMA_VERSION, recordType: 'outcome', decisionId, timestamp, status, exitStatus, error };
}

export class JsonlDecisionLog {
  #path;
  #rotateBytes;
  #sequence = 0;
  #tail = Promise.resolve();
  constructor({ path, rotateBytes = 10 * 1024 * 1024 }) {
    if (!path) throw new TypeError('path required');
    this.#path = path;
    this.#rotateBytes = rotateBytes;
  }
  append(record) {
    const operation = this.#tail.then(() => this.#appendOne(record));
    this.#tail = operation.catch(() => false);
    return operation.catch(() => false);
  }
  async #appendOne(record) {
    try {
      await mkdir(dirname(this.#path), { recursive: true });
      const line = `${JSON.stringify(record)}\n`;
      const handle = await open(this.#path, 'a', 0o600);
      try { await handle.write(line); } finally { await handle.close(); }
      this.#sequence += 1;
      await this.#maybeRotate();
      return true;
    } catch {
      return false;
    }
  }
  async #maybeRotate() {
    try {
      const size = (await stat(this.#path)).size;
      if (size <= this.#rotateBytes) return;
      const suffix = `${Date.now()}-${process.pid}-${this.#sequence}`;
      await rename(this.#path, `${this.#path}.${suffix}`);
    } catch {
      // Logger is fail-open by contract. A concurrent writer may have rotated it.
    }
  }
}

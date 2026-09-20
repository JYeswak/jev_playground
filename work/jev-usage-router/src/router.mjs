/**
 * jev-usage-router — one Choice call, typed result, append-only JSONL log.
 * Field names from SDK-SURFACE.md: ChoiceResponse.{choice,confidence,probabilities}
 * Kill switch: config.enabled=false OR process.env.BYPASS_JEV=1 OR process.env.JEV_USAGE_ROUTER=0
 */
import { createRequire } from 'node:module';
import { appendFile, mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SDK_PKG = path.resolve(ROOT, '../sdk/package.json');

const CRITERIA = {
  local: 'Answerable from local context, files, or memory without network.',
  research: 'Needs web search, corpus lookup, or multi-source gathering.',
  browser: 'Needs interactive browser, booking UI, or live page actions.',
  bypass: 'Unclear, irreversible, or should stay with a human / full agent.',
};

function loadSdk() {
  const require = createRequire(SDK_PKG);
  return require('@typesafe-ai/sdk');
}

export async function loadConfig(configPath = path.join(ROOT, 'config.json')) {
  const raw = JSON.parse(await readFile(configPath, 'utf8'));
  return raw;
}

export function shouldBypass(config) {
  if (process.env.BYPASS_JEV === '1') return { bypass: true, reason: 'BYPASS_JEV=1' };
  if (process.env.JEV_USAGE_ROUTER === '0') return { bypass: true, reason: 'JEV_USAGE_ROUTER=0' };
  if (config?.enabled === false) return { bypass: true, reason: 'config.enabled=false' };
  return { bypass: false };
}

/**
 * @param {{ goal: string, completedWork?: string, candidates?: string[], config?: object }} input
 */
export async function routeUsage(input) {
  const config = input.config ?? (await loadConfig());
  const started = Date.now();
  const id = randomUUID();
  const kill = shouldBypass(config);
  if (kill.bypass) {
    const row = {
      id,
      ts: new Date().toISOString(),
      mode: config.mode ?? 'shadow',
      ok: true,
      bypassed: true,
      reason: kill.reason,
      action: 'bypass',
      confidence: null,
      latencyMs: Date.now() - started,
      goal: input.goal,
    };
    await appendLog(config, row);
    return row;
  }

  const apiKey = process.env.TYPESAFE_API_KEY;
  if (!apiKey) {
    const row = {
      id,
      ts: new Date().toISOString(),
      mode: config.mode ?? 'shadow',
      ok: false,
      reason: 'unconfigured',
      error: 'TYPESAFE_API_KEY unset — infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>',
      action: 'bypass',
      latencyMs: Date.now() - started,
      goal: input.goal,
    };
    await appendLog(config, row);
    return row;
  }

  const { TypeSafeClient, choice } = loadSdk();
  const client = new TypeSafeClient({ apiKey });
  const state = {
    goal: input.goal,
    completed_work: input.completedWork ?? 'Nothing yet.',
    available_actions: input.candidates ?? Object.keys(CRITERIA),
  };

  try {
    const r = await client.systemOne({
      model: config.model ?? 'jev-1.13.0',
      state,
      questions: {
        route: choice(
          'Choose the cheapest adequate next action for this job. Prefer local when possible. Use bypass when unclear or irreversible.',
          CRITERIA,
        ),
      },
    });
    const a = r.answers?.route;
    if (!a || a.type !== 'choice' || typeof a.choice !== 'string') {
      throw new Error('ChoiceResponse missing choice (see SDK-SURFACE.md — not .distribution)');
    }
    if (!a.probabilities || typeof a.probabilities !== 'object') {
      throw new Error('ChoiceResponse missing probabilities — refuse silent null scoring');
    }
    const floor = config.confidenceFloor ?? 0.55;
    let action = a.choice;
    if (typeof a.confidence === 'number' && a.confidence < floor) action = 'bypass';

    const row = {
      id,
      ts: new Date().toISOString(),
      mode: config.mode ?? 'shadow',
      ok: true,
      bypassed: false,
      action,
      rawChoice: a.choice,
      confidence: a.confidence,
      probabilities: a.probabilities,
      latencyMs: Date.now() - started,
      model: config.model ?? 'jev-1.13.0',
      goal: input.goal,
      binding: (config.mode ?? 'shadow') === 'active' ? 'caller-must-honor' : 'log-only',
    };
    await appendLog(config, row);
    return row;
  } catch (err) {
    const row = {
      id,
      ts: new Date().toISOString(),
      mode: config.mode ?? 'shadow',
      ok: false,
      reason: 'transport',
      error: String(err),
      action: 'bypass',
      latencyMs: Date.now() - started,
      goal: input.goal,
    };
    await appendLog(config, row);
    return row;
  }
}

async function appendLog(config, row) {
  const dir = path.isAbsolute(config.logDir) ? config.logDir : path.join(ROOT, config.logDir ?? 'logs');
  await mkdir(dir, { recursive: true });
  const day = row.ts.slice(0, 10);
  await appendFile(path.join(dir, `routes-${day}.jsonl`), JSON.stringify(row) + '\n');
}

/**
 * jev-usage-router — one Choice call, typed result, append-only JSONL log.
 * Field names from SDK-SURFACE.md: ChoiceResponse.{choice,confidence,probabilities}
 * Kill switch: config.enabled=false OR process.env.BYPASS_JEV=1 OR process.env.JEV_USAGE_ROUTER=0
 *
 * Routed via work/jev-client askJevChoice (single-attempt, timeout, unconfigured
 * handling owned there). askJevChoice refuses an off-label choice and a
 * non-numeric confidence instead of coercing either — both surface here as a
 * transport row with action bypass (fail-safe: never act on an unreadable answer).
 */
import { appendFile, mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { askJevChoice } from '../../jev-client/src/index.ts';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const CRITERIA = {
  local: 'Answerable from local context, files, or memory without network.',
  research: 'Needs web search, corpus lookup, or multi-source gathering.',
  browser: 'Needs interactive browser, booking UI, or live page actions.',
  bypass: 'Unclear, irreversible, or should stay with a human / full agent.',
};
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

  const classes = CRITERIA;
  const state = {
    goal: input.goal,
    completed_work: input.completedWork ?? 'Nothing yet.',
    available_actions: input.candidates ?? Object.keys(CRITERIA),
  };

  try {
    const r = await askJevChoice({
      state,
      instructions:
        'Choose the cheapest adequate next action for this job. Prefer local when possible. Use bypass when unclear or irreversible.',
      classes,
      model: config.model ?? 'jev-1.13.0',
      apiKey,
    });
    if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
    const floor = config.confidenceFloor ?? 0.55;
    let action = r.choice;
    if (r.confidence < floor) action = 'bypass';

    const row = {
      id,
      ts: new Date().toISOString(),
      mode: config.mode ?? 'shadow',
      ok: true,
      bypassed: false,
      action,
      rawChoice: r.choice,
      confidence: r.confidence,
      probabilities: r.probabilities,
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

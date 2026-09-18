import { createHash } from 'node:crypto';
import { readFile, readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';
import { validateUsage, measureTurn } from './whatif-core.mjs';

export async function jsonlFiles(input) {
  const info = await stat(input);
  if (info.isFile()) return input.endsWith('.jsonl') ? [input] : [];
  const entries = await readdir(input, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => jsonlFiles(join(input, entry.name))));
  return nested.flat().sort();
}

export async function readUsageFiles(inputs) {
  const files = (await Promise.all(inputs.map(jsonlFiles))).flat().sort();
  const sessions = [];
  const failures = [];
  let assistantTurns = 0;
  let turnsWithUsage = 0;
  let turnsWithoutUsage = 0;
  let nonTurnRecords = 0;
  for (const file of files) {
    const text = await readFile(file, 'utf8');
    const session = { source: file, sessionId: null, turns: [], models: new Set() };
    for (const [index, line] of text.split(/\r?\n/).entries()) {
      if (!line.trim()) continue;
      let row;
      try { row = JSON.parse(line); }
      catch (error) { failures.push({ code: 'MALFORMED_JSONL', source: file, line: index + 1, message: error.message }); continue; }
      if (row.type === 'session') { session.sessionId = row.id ?? row.sessionId ?? null; continue; }
      if (row?.message?.role !== 'assistant') { nonTurnRecords += 1; continue; }
      assistantTurns += 1;
      const usage = row.message.usage;
      if (!usage) { turnsWithoutUsage += 1; continue; }
      const normalizedUsage = {
        input: usage.input_tokens ?? usage.input,
        cacheRead: usage.cache_read_input_tokens ?? usage.cacheRead,
        cacheWrite: usage.cache_creation_input_tokens ?? usage.cacheWrite,
        output: usage.output_tokens ?? usage.output,
      };
      try { validateUsage(normalizedUsage, file, index + 1); }
      catch (error) { failures.push({ code: 'INVALID_USAGE', source: file, line: index + 1, message: error.message }); continue; }
      const model = row.message.model ?? 'unknown';
      session.models.add(model);
      turnsWithUsage += 1;
      session.turns.push({ line: index + 1, model, ...measureTurn(normalizedUsage) });
    }
    if (session.turns.length) sessions.push({ ...session, models: [...session.models] });
  }
  return { files, sessions, failures, denominator: { files: files.length, sessions: sessions.length, assistantTurns, turnsWithUsage, turnsWithoutUsage, nonTurnRecords } };
}

export async function inputHashes(files) {
  return Promise.all(files.map(async (path) => ({ path, sha256: createHash('sha256').update(await readFile(path)).digest('hex') })));
}

/**
 * Harvest REAL dcg allow-verdict commands from omp session logs.
 *
 * Why: criteria-v3 scopes the judge to commands dcg does NOT block. Every number
 * we have for this judge came from score.mjs, which is a regex simulator over a
 * 21-record hand-built corpus — it never called Jev. Hand-built corpora have
 * failed to transfer to real traffic five times this session, so this judge gets
 * measured on real allowed traffic or not at all.
 *
 * Shape note, learned the hard way: the dcg bridge row carries only
 * {kind, toolCallId}. The command lives on a separate `toolCall` content part in
 * a `message` row. This joins them by id, same as work/omp-harm-rule/dcg-recall.mjs.
 *
 * DATA ONLY. Commands are read as text and never executed.
 *
 * Run: node work/toolcall-judge-v3/harvest-allowed.mjs [limit]
 */
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

const limit = Number(process.argv[2] ?? 0);

const glob = execSync(`find $HOME/.omp/profiles -path '*agent/sessions*' -name '*.jsonl'`, {
  encoding: 'utf8',
  maxBuffer: 64 * 1024 * 1024,
})
  .split('\n')
  .filter(Boolean);

/** Accepts BOTH omp custom-row shapes. */
function readRow(line) {
  let parsed;
  try {
    parsed = JSON.parse(line);
  } catch {
    return undefined;
  }
  if (!parsed || typeof parsed !== 'object' || !('customType' in parsed)) return undefined;
  const custom = parsed.customType;
  if (typeof custom === 'string') {
    if (!custom.includes('omp-dcg-bridge')) return undefined;
    return parsed.data && typeof parsed.data === 'object' ? parsed.data : undefined;
  }
  if (custom && typeof custom === 'object' && typeof custom.type === 'string') {
    if (!custom.type.includes('omp-dcg-bridge')) return undefined;
    return custom.data && typeof custom.data === 'object' ? { ...custom.data } : undefined;
  }
  return undefined;
}

const want = new Map(); // toolCallId -> 'allow' | 'block'
const files = [];
let allowRows = 0;
let blockRows = 0;

for (const file of glob) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    continue;
  }
  if (!text.includes('omp-dcg-bridge')) continue;
  files.push(file);
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('omp-dcg-bridge')) continue;
    const data = readRow(line);
    if (!data) continue;
    if (data.kind === 'dcg_block') {
      blockRows += 1;
      if (!want.has(data.toolCallId)) want.set(data.toolCallId, 'block');
    } else if (data.kind === 'dcg_allow') {
      allowRows += 1;
      if (!want.has(data.toolCallId)) want.set(data.toolCallId, 'allow');
    }
  }
}

const cmds = new Map();
for (const file of files) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    continue;
  }
  if (!text.includes('toolCall')) continue;
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('toolCall')) continue;
    let row;
    try {
      row = JSON.parse(line);
    } catch {
      continue;
    }
    if (row.type !== 'message') continue;
    const content = row.message && Array.isArray(row.message.content) ? row.message.content : [];
    for (const part of content) {
      if (!part || typeof part !== 'object' || part.type !== 'toolCall') continue;
      if (!want.has(part.id)) continue;
      const args = part.arguments || part.input || {};
      const command = args && typeof args === 'object' ? args.command : undefined;
      if (typeof command === 'string' && command.trim()) {
        cmds.set(part.id, { tool: part.name, command });
      }
    }
  }
}

const byCommand = new Map();
for (const [id, kind] of want) {
  if (kind !== 'allow') continue;
  const entry = cmds.get(id);
  if (!entry) continue;
  const existing = byCommand.get(entry.command);
  if (existing) {
    existing.seen += 1;
  } else {
    byCommand.set(entry.command, { command: entry.command, tool: entry.tool, seen: 1 });
  }
}

const all = [...byCommand.values()].sort((a, b) => b.seen - a.seen);
const out = limit > 0 ? all.slice(0, limit) : all;

console.log('files with bridge rows :', files.length);
console.log('bridge rows            : allow', allowRows, 'block', blockRows);
console.log('joined allow commands  :', [...want.values()].filter((k) => k === 'allow').length);
console.log('distinct allow commands:', all.length);
console.log('emitted                :', out.length);

writeFileSync(
  new URL('./real-allowed.json', import.meta.url),
  `${JSON.stringify(
    {
      description: 'DATA ONLY. Real dcg allow-verdict commands, deduped. Never executed.',
      harvestedAt: new Date().toISOString(),
      records: out,
    },
    null,
    2,
  )}\n`,
);
console.log('wrote real-allowed.json');

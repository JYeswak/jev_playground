/**
 * jev-m7r: is there a corpus of genuinely dangerous commands, in OUR FOUR CLASSES, that were
 * actually typed here?
 *
 * The bead's objection to the old 1/814 number is exact: 204 of those blocks are approval-gated
 * bulk deletions OUTSIDE our four classes, so that denominator measures POLICY OVERLAP with dcg,
 * not harm recall. dcg blocks what dcg blocks; our rule answers four specific questions.
 *
 * So this does not compute a recall figure against dcg's denominator. It partitions the real
 * blocked commands by whether they are even IN SCOPE for our four classes, and reports the
 * in-scope count. If that count is ~0, the honest output is the ruling the bead already
 * sanctions: no such corpus exists here, and 12/12 stays scoped to the constructed set.
 *
 * DATA ONLY. Commands are read as text and never executed.
 *
 * Run: node work/omp-harm-rule/block-corpus.mjs
 */
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const files = execSync(`find $HOME/.omp/profiles -path '*agent/sessions*' -name '*.jsonl'`, {
  encoding: 'utf8',
  maxBuffer: 64 * 1024 * 1024,
}).split('\n').filter(Boolean);

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

const want = new Map();
const touched = [];
for (const file of files) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    continue;
  }
  if (!text.includes('omp-dcg-bridge')) continue;
  touched.push(file);
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('omp-dcg-bridge')) continue;
    const data = readRow(line);
    if (data?.kind === 'dcg_block' && !want.has(data.toolCallId)) want.set(data.toolCallId, true);
  }
}

const commands = new Map();
for (const file of touched) {
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
    for (const part of row.message?.content ?? []) {
      if (part?.type !== 'toolCall' || !want.has(part.id)) continue;
      const cmd = (part.arguments ?? part.input ?? {}).command;
      if (typeof cmd === 'string' && cmd.trim()) commands.set(part.id, cmd);
    }
  }
}

/**
 * IN SCOPE = the command plausibly asks one of our four questions. Deliberately GENEROUS:
 * it is a scope filter, not the rule under test, so it must not quietly exclude cases the rule
 * would have been asked about.
 */
const SCOPE = {
  privilege_widening: /\b(chmod|chown|setfacl|sudo|visudo|usermod|launchctl\s+(load|bootstrap))\b/i,
  secret_staging: /\b(pem|id_rsa|private[_-]?key|credentials|\.env\b|secrets?|token|keychain)\b/i,
  irreversible_publication: /\b(npm\s+publish|git\s+push|gh\s+release|docker\s+push|scp|rsync|curl\s+-[A-Za-z]*T)\b/i,
  security_control_tampering: /\b(\.git\/hooks|gatekeeper|firewall|csrutil|spctl|--no-verify|verify\s*=\s*false)\b/i,
};

const uniq = [...new Set(commands.values())];
const inScope = [];
for (const command of uniq) {
  const hits = Object.entries(SCOPE).filter(([, re]) => re.test(command)).map(([k]) => k);
  if (hits.length) inScope.push({ command, classes: hits });
}

console.log(`session files with bridge rows : ${touched.length}`);
console.log(`distinct dcg_block tool calls  : ${want.size}`);
console.log(`of those, command text joined  : ${commands.size}`);
console.log(`distinct blocked commands      : ${uniq.length}`);
console.log(`IN SCOPE for our four classes  : ${inScope.length}`);
console.log('');
for (const row of inScope.slice(0, 25)) {
  console.log(`  [${row.classes.join(',')}] ${row.command.slice(0, 110).replace(/\n/g, ' ')}`);
}
if (inScope.length === 0) {
  console.log('  (none — the ruling the bead sanctions applies)');
}

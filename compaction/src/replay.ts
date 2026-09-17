#!/usr/bin/env tsx
/**
 * Live replay: omp JSONL transcript -> adapt -> compactMessages() with the
 * REAL Jev client -> contract assertions -> receipt JSON.
 *
 * The library contract (read from src/compact.ts applyDecisions):
 * - Texts are NEVER altered or lost: every input message with non-blank text
 *   survives verbatim; only messages emptied by drops are pruned.
 * - Tool results are kept byte-exact, truncated (shorter), or removed with
 *   their call; ids are never invented.
 * - Message count may SHRINK (pruned empties). Count equality is NOT asserted.
 *
 * Usage: npm run replay -- <transcript.jsonl> [--out receipt.json]
 * Key comes from TYPESAFE_API_KEY. Exit nonzero on any assertion failure.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { compactMessages, type Message } from 'fast-jev-compaction';
import { adaptOmpTranscript, type OmpEvent } from './omp-adapter.js';

if (!process.env.TYPESAFE_API_KEY) {
  console.error('TYPESAFE_API_KEY is not set.');
  process.exit(2);
}
const file = process.argv[2];
if (!file) {
  console.error('usage: replay <transcript.jsonl> [--out receipt.json]');
  process.exit(2);
}
const events: OmpEvent[] = readFileSync(file, 'utf8')
  .split('\n')
  .filter((line) => line.trim())
  .map((line) => JSON.parse(line) as OmpEvent);

const { messages, stats } = adaptOmpTranscript(events);
const result = await compactMessages(messages, {
  keepThreshold: 0.5,
  maxStateTokens: 20000,
  truncateHeadChars: 500,
});

const failures: string[] = [];
const check = (name: string, ok: boolean) => {
  console.error(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  if (!ok) failures.push(name);
};

const inUses = new Map(messages.flatMap((m) => m.toolUses.map((u) => [u.tool_use_id, u] as const)));
const inResults = new Map(
  messages.flatMap((m) => (m.toolResults ?? []).map((r) => [r.tool_use_id, r] as const)),
);

// 1. Output texts are a subsequence of input texts (verbatim, order-preserving).
{
  const texts = messages.map((m) => m.text);
  let j = 0;
  let ok = true;
  for (const m of result.messages) {
    while (j < texts.length && texts[j] !== m.text) j++;
    if (j >= texts.length) {
      ok = false;
      break;
    }
    j++;
  }
  check('output texts are verbatim input subsequence', ok);
}
// 2. No text loss: every non-blank input text survives (multiset-safe).
{
  const outCount = new Map<string, number>();
  for (const m of result.messages) outCount.set(m.text, (outCount.get(m.text) ?? 0) + 1);
  const inCount = new Map<string, number>();
  for (const m of messages) {
    if (m.text.trim().length > 0) inCount.set(m.text, (inCount.get(m.text) ?? 0) + 1);
  }
  let ok = true;
  for (const [t, n] of inCount) if ((outCount.get(t) ?? 0) < n) ok = false;
  check('every non-blank input text survives', ok);
}
// 3. No invented ids; results exact or shortened.
{
  let ok = true;
  for (const m of result.messages) {
    for (const u of m.toolUses) if (!inUses.has(u.tool_use_id)) ok = false;
    for (const r of m.toolResults ?? []) {
      const o = inResults.get(r.tool_use_id);
      if (!o) ok = false;
      else if (r.text !== o.text && r.text.length >= o.text.length) ok = false;
    }
  }
  check('no invented ids; results exact or truncated', ok);
}
// 4. Dropped messages were empty of text (only pruned empties vanish).
{
  const outTexts = result.messages.map((m) => m.text);
  let j = 0;
  let ok = true;
  for (const m of messages) {
    if (j < outTexts.length && outTexts[j] === m.text) {
      j++;
      continue;
    }
    if (m.text.trim().length !== 0) ok = false; // a text-carrying message vanished
  }
  check('vanished messages carried no text', ok);
}
// 5. Liveness: unpinned candidates imply Jev was actually consulted.
check(
  'candidates imply requests',
  result.stats.calls - result.stats.pinned <= 0 || result.stats.requests > 0,
);
check('library saw tool calls', result.stats.calls > 0);

const receipt = {
  transcript: file,
  eventsIn: stats.eventsIn,
  messagesIn: stats.messagesIn,
  thinkingCharsDropped: stats.thinkingCharsDropped,
  resultsPaired: stats.resultsPaired,
  resultsTrailing: stats.resultsTrailing,
  lib: result.stats,
  failures,
};
const outIdx = process.argv.indexOf('--out');
if (outIdx >= 0 && process.argv[outIdx + 1]) {
  writeFileSync(process.argv[outIdx + 1], JSON.stringify(receipt, null, 2));
  console.error(`receipt -> ${process.argv[outIdx + 1]}`);
} else {
  console.error(JSON.stringify(receipt, null, 2));
}
process.exit(failures.length > 0 ? 1 : 0);

import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  sha256, parseJsonl, selectObserverFrame, indexSession, joinEpisodes,
  publicPreflight, recoverFrozenFrame,
} from './recover.mjs';

// Anonymized structural controls from observed v3 session and find-rank.v1
// shapes. These are parser/regression controls, NOT historical/live proof.
const stamp = '2026-10-05T09:45:27.284Z';
const path = 'fixture/file.ts';
function episode(overrides = {}) {
  return { line: 1, value: {
    schema: 'jev-find-rank.v1', ts: stamp, session: 'control-session',
    hits: [sha256(path)], count: 1,
    nextToolCalls: Array.from({ length: 10 }, (_, i) => ({
      ordinal: i + 1, tool: 'read', touched: i === 0 ? [sha256(path)] : [],
    })), complete: true, ...overrides,
  } };
}
function source({ duplicateStart = false, duplicateCall = false, pruned = false,
  secondResult = false, wrongQuery = false } = {}) {
  const call = { type: 'toolCall', name: 'find', id: 'control-call',
    arguments: { i: 'Locating control code', query: 'control query', grep_keywords: [], path: '.' } };
  const rows = [
    { type: 'title', v: 1, title: '' },
    { type: 'session', version: 3, id: 'control-session', timestamp: stamp, cwd: '/control' },
    { type: 'message', timestamp: '2026-10-05T09:45:20.000Z',
      message: { role: 'assistant', content: duplicateCall ? [call, call] : [call] } },
    { type: 'custom', customType: 'tool_execution_start', data: {
      toolName: 'find', toolCallId: 'control-call', startedAt: '2026-10-05T09:45:21.000Z',
    } },
  ];
  if (duplicateStart) rows.push(structuredClone(rows[3]));
  const result = { type: 'message', timestamp: '2026-10-05T09:45:59.521Z', message: {
    role: 'toolResult', toolName: 'find', toolCallId: 'control-call', isError: false,
    timestamp: Date.parse('2026-10-05T09:45:59.521Z'), content: [{ type: 'text', text: '' }],
    details: pruned ? null : { query: wrongQuery ? 'different query' : 'control query',
      keywords: [], threshold: 0.5, hits: [{ rel: path, nameScore: 0.8, contentScore: 0.9,
        ranges: [[1, 2]], linesSeen: 2, truncated: false }], stats: {}, elapsedMs: 100,
      cwd: '/control', scopePath: '/control' },
    ...(pruned ? { prunedAt: Date.parse(stamp) } : {}),
  } };
  rows.push(result);
  if (secondResult) rows.push(structuredClone(result));
  return indexSession(parseJsonl(rows.map(JSON.stringify).join('\n')), sha256('control-source'));
}
const searched = { inventoryComplete: true };

test('JSONL preserves physical line pointers and rejects malformed records without echoing payloads', () => {
  assert.equal(parseJsonl('\n{"type":"session"}\n')[0].line, 2);
  assert.throws(() => parseJsonl('private malformed query'), /^Error: INVALID_JSONL_LINE_1$/);
});

test('observer selection uses inclusive exact bounds, schema and complete flag', () => {
  const a = episode();
  const rows = [a, episode({ complete: false }), episode({ schema: 'other' }),
    episode({ ts: '2026-10-05T09:45:27.283Z' }), episode({ ts: '2026-10-05T09:45:27.285Z' })];
  assert.deepEqual(selectObserverFrame(rows, stamp, stamp), [a]);
  assert.throws(() => selectObserverFrame([episode({ count: 9 })], stamp, stamp), /INVALID_OBSERVER_ROW/);
  assert.throws(() => selectObserverFrame([episode({ nextToolCalls: [] })], stamp, stamp), /INVALID_OBSERVER_ROW/);
});

test('census microsecond boundaries do not admit a neighboring observation', () => {
  const at = '2026-09-29T04:55:45.560638Z';
  const rows = [
    episode({ ts: '2026-09-29T04:55:45.560637Z' }),
    episode({ ts: at }),
    episode({ ts: '2026-09-29T04:55:45.560639Z' }),
  ];
  assert.deepEqual(selectObserverFrame(rows, at, at), [rows[1]]);
  assert.throws(() => selectObserverFrame([episode({ ts: 'x'.repeat(50000) })], at, at),
    /INVALID_OBSERVER_TIMESTAMP/);
});

test('recovery refuses an unauthenticated baseline before using observer data', () => {
  assert.throws(() => recoverFrozenFrame(JSON.stringify(episode().value), '{}'), /BASELINE_SHA_MISMATCH/);
});

test('causal start/end bracket accepts actual delayed persistence, not a nearest-time tolerance', () => {
  const result = joinEpisodes([episode()], [source()], searched);
  assert.equal(result.counts.joined, 1);
  assert.equal(result.matches[0].callLine, 3);
  assert.equal(result.matches[0].startLine, 4);
  assert.equal(result.matches[0].resultLine, 5);
  assert.equal(joinEpisodes([episode({ ts: '2026-10-05T09:45:20.999Z' })], [source()], searched).counts.missingResult, 1);
  assert.equal(joinEpisodes([episode({ ts: '2026-10-05T09:45:59.522Z' })], [source()], searched).counts.missingResult, 1);
});

test('ordered hashes are not interchangeable with unordered candidate sets', () => {
  const row = episode({ hits: [sha256('other'), sha256(path)], count: 2 });
  assert.equal(joinEpisodes([row], [source()], searched).counts.missingResult, 1);
});

test('missing, unsearched and duplicate sources remain separate', () => {
  assert.equal(joinEpisodes([episode()], [], searched).counts.missingSource, 1);
  assert.equal(joinEpisodes([episode()], []).counts.unsearched, 1);
  assert.equal(joinEpisodes([episode()], [source(), source()], searched).counts.duplicateSource, 1);
});

test('duplicate calls/starts/results and pruned details fail closed', () => {
  for (const opts of [{ duplicateStart: true }, { duplicateCall: true }, { secondResult: true }]) {
    assert.equal(joinEpisodes([episode()], [source(opts)], searched).counts.ambiguous, 1);
  }
  const result = joinEpisodes([episode()], [source({ pruned: true })], searched);
  assert.equal(result.counts.missingResult, 1);
  assert.equal(result.counts.prunedResultEpisodes, 1);
  assert.equal(joinEpisodes([episode()], [source({ wrongQuery: true })], searched).counts.missingResult, 1);
});

test('one result cannot silently satisfy two observer identities', () => {
  const result = joinEpisodes([episode(), episode({ ts: '2026-10-05T09:45:28.000Z' })], [source()], searched);
  assert.equal(result.counts.joined, 0);
  assert.equal(result.counts.ambiguous, 2);
});

test('forced one-to-one elimination resolves overlaps without nearest-time guessing', () => {
  const s = source();
  const c = structuredClone(s.calls[0]); c.id = 'control-call-2'; c.line = 6;
  const st = structuredClone(s.starts[0]); st.id = c.id; st.line = 7;
  st.time = Date.parse('2026-10-05T09:45:26.000Z');
  const r = structuredClone(s.results[0]); r.id = c.id; r.line = 8;
  s.calls.push(c); s.starts.push(st); s.results.push(r);
  const result = joinEpisodes([episode({ ts: '2026-10-05T09:45:25.000Z' }), episode()], [s], searched);
  assert.equal(result.counts.joined, 2);
  assert.deepEqual(result.matches.map(m => m.callId), ['control-call', 'control-call-2']);
});

test('hashed preflight never promotes recovered identity to native request or source fidelity', () => {
  const joined = joinEpisodes([episode()], [source()], searched);
  const report = publicPreflight({ rows: [episode()], observerSha256: sha256('observer'),
    baselineSha256: sha256('baseline'), frameSha256: sha256('frame'), authenticated: false }, joined);
  const text = JSON.stringify(report);
  for (const secret of ['control-session', 'control-call', 'control query', path, '/control']) {
    assert.equal(text.includes(secret), false);
  }
  assert.equal(report.scoringAllowed, false);
  assert.equal(report.fullRequestAuthority, 'UNKNOWN');
  assert.equal(report.sourceFidelity, 'UNKNOWN');
  assert.equal(report.N_capture, 0);
  assert.equal(report.N_paired, 0);
  assert.equal(report.status, 'INCOMPLETE');
});

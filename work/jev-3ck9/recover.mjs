import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, opendir, realpath } from 'node:fs/promises';
import { createInterface } from 'node:readline';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

export const FROZEN = Object.freeze({
  baselineSha256: 'fa821c712122adb144df2d12d851a5ce0795e5507ff8251bbb4d93eeb0005e29',
  baselineLine: 383,
  baselinePointer: 'message.details.jobs[0].resultText',
  from: '2026-09-29T04:55:45.560638+00:00',
  through: '2026-10-06T04:55:45.560638+00:00',
  episodes: 999, sessions: 57, windows: 1034, followed: 559,
  frameSha256: 'eaa9904b124ab19a618dadb4713763d2b9dc3a4c9d454211dcf16778021ac5a0',
});
export const sha256 = value => createHash('sha256').update(value).digest('hex');
const fail = code => { throw new Error(code); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const hashPattern = /^[a-f0-9]{64}$/;

export function parseJsonl(text) {
  const records = [];
  for (const [index, line] of text.split('\n').entries()) {
    if (!line.trim()) continue;
    let value;
    try { value = JSON.parse(line); } catch { fail(`INVALID_JSONL_LINE_${index + 1}`); }
    if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`INVALID_JSONL_LINE_${index + 1}`);
    records.push({ line: index + 1, value });
  }
  return records;
}

// Microseconds matter at the census boundary; Date.parse alone rounds it down.
function micros(value) {
  if (typeof value !== 'string' || value.length > 40) return null;
  const match = /^(.*T\d\d:\d\d:\d\d)(?:\.(\d{1,6}))?(Z|[+-]\d\d:\d\d)$/.exec(value);
  if (!match) return null;
  const seconds = Date.parse(match[1] + match[3]);
  return Number.isFinite(seconds) ? BigInt(seconds) * 1000n + BigInt((match[2] ?? '').padEnd(6, '0')) : null;
}

export function selectObserverFrame(records, from, through) {
  const low = micros(from), high = micros(through);
  if (low === null || high === null || low > high) fail('INVALID_WINDOW');
  return records.filter(({ value: row }) => {
    if (row.schema !== 'jev-find-rank.v1' || row.complete !== true) return false;
    const time = micros(row.ts);
    if (time === null) fail('INVALID_OBSERVER_TIMESTAMP');
    if (time < low || time > high) return false;
    if (typeof row.session !== 'string' || !row.session || !Array.isArray(row.hits)
      || row.hits.some(h => typeof h !== 'string' || h.length !== 64 || !hashPattern.test(h))
      || row.count !== row.hits.length || !Array.isArray(row.nextToolCalls)
      || row.nextToolCalls.length !== 10 || row.nextToolCalls.some((call, i) =>
        call?.ordinal !== i + 1 || typeof call.tool !== 'string' || !Array.isArray(call.touched)
        || call.touched.some(h => !row.hits.includes(h)))) fail('INVALID_OBSERVER_ROW');
    return true;
  });
}

/** Raw rows stay in memory. Only publicPreflight's hashed projection is safe to publish. */
export function recoverFrozenFrame(observerText, baselineText) {
  const baselineSha256 = sha256(baselineText);
  if (baselineSha256 !== FROZEN.baselineSha256) fail('BASELINE_SHA_MISMATCH');
  const baseline = parseJsonl(baselineText).find(r => r.line === FROZEN.baselineLine)?.value;
  const evidence = baseline?.message?.details?.jobs?.[0]?.resultText;
  if (typeof evidence !== 'string'
    || !evidence.startsWith(`# local omp scoreboard: 7d ending ${FROZEN.through}`)
    || !evidence.split('\n').some(line => line.startsWith(
      '# find-rank windows=1034 complete=999 follow_through=559/999 '))) fail('BASELINE_CENSUS_MISMATCH');
  const rows = selectObserverFrame(parseJsonl(observerText), FROZEN.from, FROZEN.through);
  const frameSha256 = sha256(JSON.stringify(rows.map(r => r.value)));
  if (rows.length !== FROZEN.episodes) fail('FRAME_COUNT_MISMATCH');
  if (new Set(rows.map(r => r.value.session)).size !== FROZEN.sessions) fail('FRAME_SESSION_COUNT_MISMATCH');
  const identities = rows.map(r => sha256(JSON.stringify(r.value)));
  if (new Set(identities).size !== identities.length) fail('DUPLICATE_OBSERVER_EPISODE');
  if (rows.filter(r => r.value.nextToolCalls.some(c => c.touched.length)).length !== FROZEN.followed)
    fail('FRAME_FOLLOW_THROUGH_MISMATCH');
  if (frameSha256 !== FROZEN.frameSha256) fail('FRAME_SHA_MISMATCH');
  return { rows, frameSha256, baselineSha256, observerSha256: sha256(observerText), authenticated: true };
}

/** Index only original records. No prompt regeneration, filesystem replay or cache guessing. */
export function indexSession(records, sourceSha256) {
  const headers = records.filter(r => r.value.type === 'session');
  const session = headers.length === 1 && typeof headers[0].value.id === 'string' ? headers[0].value.id : null;
  const calls = [], starts = [], results = [];
  for (const { line, value: entry } of records) {
    const m = entry.message;
    if (m?.role === 'assistant' && Array.isArray(m.content)) {
      m.content.forEach((c, contentIndex) => {
        if (c?.type === 'toolCall' && c.name === 'find') calls.push({
          id: c.id, line, contentIndex, args: c.arguments,
        });
      });
    }
    if (entry.type === 'custom' && entry.customType === 'tool_execution_start' && entry.data?.toolName === 'find') {
      starts.push({ id: entry.data.toolCallId, line, time: Date.parse(entry.data.startedAt) });
    }
    if (m?.role === 'toolResult' && m.toolName === 'find') {
      const rawHits = Array.isArray(m.details?.hits) ? m.details.hits.flatMap(hit =>
        typeof hit?.rel === 'string' && hit.rel ? [hit.rel] : []) : null;
      results.push({ id: m.toolCallId, line, time: Date.parse(entry.timestamp),
        isError: m.isError === true, hashes: rawHits?.map(sha256) ?? null,
        query: m.details?.query, pruned: rawHits === null,
      });
    }
  }
  return { session, headerLine: headers[0]?.line ?? null, sourceSha256, calls, starts, results };
}

function candidates(row, source) {
  const at = Date.parse(row.ts), found = [];
  for (const result of source.results) {
    if (result.isError || !result.hashes || !same(result.hashes, row.hits)) continue;
    const calls = source.calls.filter(c => c.id === result.id);
    const starts = source.starts.filter(s => s.id === result.id);
    const ends = source.results.filter(r => r.id === result.id);
    for (const call of calls) for (const start of starts) {
      if (!Number.isFinite(start.time) || !Number.isFinite(result.time)
        || start.time > at || at > result.time || !(call.line < start.line && start.line < result.line)) continue;
      if (typeof call.id !== 'string' || !call.id || typeof call.args?.query !== 'string'
        || (result.query !== undefined && result.query !== call.args.query)) continue;
      found.push({ sourceSha256: source.sourceSha256, headerLine: source.headerLine,
        callId: call.id, query: call.args.query, args: call.args,
        callLine: call.line, contentIndex: call.contentIndex, startLine: start.line, resultLine: result.line,
        duplicateIdentity: calls.length !== 1 || starts.length !== 1 || ends.length !== 1,
        key: `${source.sourceSha256}:${call.id}`,
      });
    }
  }
  return found;
}

/** Pure causal matching. Unique forced assignments remove collisions; no nearest-time tie breaker. */
export function joinEpisodes(rows, sources, { inventoryComplete = false } = {}) {
  const bySession = new Map();
  for (const source of sources) {
    if (!source.session) continue;
    const list = bySession.get(source.session) ?? [];
    list.push(source); bySession.set(source.session, list);
  }
  const matches = rows.map(record => {
    const row = record.value, found = bySession.get(row.session) ?? [];
    let status, choices = [];
    if (!found.length) status = inventoryComplete ? 'missingSource' : 'unsearched';
    else if (found.length > 1) status = 'duplicateSource';
    else choices = candidates(row, found[0]);
    return { record, status, choices,
      prunedResult: found.length === 1 && found[0].results.some(r => r.pruned),
    };
  });
  const assigned = new Set();
  let changed = true;
  while (changed) {
    changed = false;
    const pending = matches.filter(m => !m.status);
    for (const match of pending) match.choices = match.choices.filter(c => !assigned.has(c.key));
    const forced = pending.filter(m => m.choices.length === 1 && !m.choices[0].duplicateIdentity);
    const multiplicity = new Map();
    for (const m of forced) multiplicity.set(m.choices[0].key, (multiplicity.get(m.choices[0].key) ?? 0) + 1);
    for (const match of forced) {
      const choice = match.choices[0];
      if (multiplicity.get(choice.key) !== 1) continue;
      Object.assign(match, choice, { status: 'joined' }); assigned.add(choice.key); changed = true;
    }
  }
  const counts = { joined: 0, missingSource: 0, duplicateSource: 0, unsearched: 0,
    missingResult: 0, ambiguous: 0, prunedResultEpisodes: 0 };
  for (const match of matches) {
    match.status ??= match.choices.length ? 'ambiguous' : 'missingResult';
    counts[match.status]++;
    if (match.status === 'missingResult' && match.prunedResult) counts.prunedResultEpisodes++;
  }
  return { matches, counts, invalidSources: sources.filter(s => !s.session).length, inventoryComplete };
}

export function publicPreflight(frame, joined, inventory = {}) {
  const identitiesComplete = frame.authenticated === true && joined.counts.joined === FROZEN.episodes
    && !joined.invalidSources && inventory.complete !== false;
  return {
    schema: 'jev.find-recovery.v1', status: identitiesComplete ? 'IDENTITIES_RECOVERED_REQUEST_AUTHORITY_UNKNOWN' : 'INCOMPLETE',
    authenticatedFrame: frame.authenticated === true, scoringAllowed: false,
    fullRequestAuthority: 'UNKNOWN', sourceFidelity: 'UNKNOWN',
    N_frame: frame.rows.length, N_capture: 0, N_labeled: 0, N_paired: 0,
    distinctSessions: new Set(frame.rows.map(r => r.value.session)).size,
    observerFollowThrough: frame.rows.filter(r => r.value.nextToolCalls.some(c => c.touched.length)).length,
    observerSha256: frame.observerSha256, baselineSha256: frame.baselineSha256,
    baselineLine: FROZEN.baselineLine, baselinePointer: FROZEN.baselinePointer,
    frameSha256: frame.frameSha256, counts: joined.counts, invalidSources: joined.invalidSources,
    inventory: { complete: joined.inventoryComplete, ...inventory },
    episodes: joined.matches.map(m => ({
      episodeSha256: sha256(JSON.stringify(m.record.value)), observerLine: m.record.line,
      sessionSha256: sha256(m.record.value.session), status: m.status,
      orderedHitsSha256: sha256(JSON.stringify(m.record.value.hits)),
      ...(m.status === 'joined' ? {
        sourceSha256: m.sourceSha256, headerLine: m.headerLine,
        callSha256: sha256(m.callId), querySha256: sha256(m.query),
        argumentsSha256: sha256(JSON.stringify(m.args)),
        callLine: m.callLine, callPointer: `message.content[${m.contentIndex}]`,
        startLine: m.startLine, startPointer: 'data.startedAt',
        resultLine: m.resultLine, resultPointer: 'message.details.hits[].rel',
      } : {}),
    })),
  };
}

// Read first four physical lines, as observed title/session headers occupy lines 1/2.
async function sessionHeader(path) {
  const stream = createReadStream(path, { encoding: 'utf8' });
  const lines = createInterface({ input: stream, crlfDelay: Infinity });
  try {
    let n = 0;
    for await (const text of lines) {
      n++;
      if (text.trim()) {
        let value;
        try { value = JSON.parse(text); } catch { fail('INVALID_SOURCE_HEADER'); }
        if (value?.type === 'session') return value.id;
      }
      if (n >= 4) break;
    }
    return null;
  } finally { lines.close(); stream.destroy(); }
}

async function* sessionFiles(root) {
  const directory = await opendir(root);
  for await (const entry of directory) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) yield* sessionFiles(path);
    else if (entry.isFile() && entry.name.endsWith('.jsonl')) yield path;
    // Symlinks are not traversed. Operators must supply their resolved roots.
  }
}

/** Local read-only inventory; roots are explicit so omitted trees are never claimed searched. */
export async function recoverFromPaths({ observer, baseline, sessionRoots = [] }) {
  const frame = recoverFrozenFrame(await readFile(observer, 'utf8'), await readFile(baseline, 'utf8'));
  const wanted = new Set(frame.rows.map(r => r.value.session));
  const sources = [], seenPaths = new Set();
  const inventory = { complete: sessionRoots.length > 0, roots: [], filesExamined: 0,
    unreadableFiles: 0, unreadableRoots: 0, unrecognizedHeaders: 0 };
  for (const root of sessionRoots) {
    inventory.roots.push(sha256(resolve(root)));
    try {
      for await (const path of sessionFiles(root)) {
        try {
          const canonical = await realpath(path);
          if (seenPaths.has(canonical)) continue;
          seenPaths.add(canonical); inventory.filesExamined++;
          const id = await sessionHeader(path);
          if (!id) { inventory.unrecognizedHeaders++; inventory.complete = false; continue; }
          if (!wanted.has(id)) continue;
          const raw = await readFile(path);
          const source = indexSession(parseJsonl(raw.toString('utf8')), sha256(raw));
          if (source.session !== id) { inventory.complete = false; inventory.unrecognizedHeaders++; }
          sources.push(source);
        } catch { inventory.unreadableFiles++; inventory.complete = false; }
      }
    } catch { inventory.unreadableRoots++; inventory.complete = false; }
  }
  const joined = joinEpisodes(frame.rows, sources, { inventoryComplete: inventory.complete });
  return publicPreflight(frame, joined, inventory);
}

async function main(args) {
  if (args.length === 1 && args[0] === '--help') {
    process.stdout.write(
      'Usage: node recover.mjs --observer FILE --baseline FILE [--sessions-root DIR ...]\n'
      + 'Recover the frozen 999-episode find frame and original event identities.\n'
      + 'Read-only; stdout contains hashes and counts, never raw queries. No scoring or model calls.\n'
      + 'Missing or ambiguous source records exit 2. Recovered identity never authorizes scoring.\n',
    );
    return;
  }
  const options = { sessionRoots: [] };
  for (let i = 0; i < args.length; i++) {
    const key = args[i], value = args[++i];
    if (!value || value.startsWith('--')) fail('INVALID_ARGUMENTS');
    if (key === '--observer') options.observer = value;
    else if (key === '--baseline') options.baseline = value;
    else if (key === '--sessions-root') options.sessionRoots.push(value);
    else fail('INVALID_ARGUMENTS');
  }
  if (!options.observer || !options.baseline) fail('REQUIRED_OBSERVER_AND_BASELINE');
  const report = await recoverFromPaths(options);
  process.stdout.write(JSON.stringify(report) + '\n');
  process.exitCode = report.status === 'INCOMPLETE' ? 2 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => {
    const message = typeof error?.message === 'string' ? error.message : '';
    const code = message.length <= 128 && /^[A-Z][A-Z0-9_]*$/.test(message) ? message : 'LOCAL_INPUT_UNREADABLE';
    process.stdout.write(JSON.stringify({ schema: 'jev.find-recovery.v1', status: 'INCOMPLETE',
      scoringAllowed: false, N_capture: 0, N_paired: 0, error: code }) + '\n');
    process.exitCode = 2;
  });
}

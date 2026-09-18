import assert from 'node:assert/strict';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { readSessionLogs } from '../src/transcript-reader.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const fixture = (name) => path.join(dir, '..', 'fixtures', name);

async function rejectsCode(promise, code, mustName) {
  try {
    await promise;
  } catch (error) {
    assert.equal(error.code, code);
    if (mustName) assert.match(error.message, mustName);
    return;
  }
  assert.fail(`expected rejection with code ${code}`);
}

test('truncated JSONL refuses MALFORMED_JSONL naming file and line, never prices the prefix', async () => {
  await rejectsCode(
    readSessionLogs([fixture('hostile-truncated.jsonl')]),
    'MALFORMED_JSONL',
    /hostile-truncated\.jsonl.*line 3/,
  );
});

test('negative token count refuses INVALID_USAGE_TOKENS naming field, never sums it', async () => {
  await rejectsCode(
    readSessionLogs([fixture('hostile-negative-tokens.jsonl')]),
    'INVALID_USAGE_TOKENS',
    /input=-50/,
  );
});

test('non-string session id refuses NON_STRING_SESSION_ID', async () => {
  await rejectsCode(
    readSessionLogs([fixture('hostile-nonstring-session-id.jsonl')]),
    'NON_STRING_SESSION_ID',
    /12345/,
  );
});

test('same session id in two files refuses DUPLICATE_SESSION_ID naming both', async () => {
  await rejectsCode(
    readSessionLogs([
      fixture('hostile-duplicate-session-a.jsonl'),
      fixture('hostile-duplicate-session-b.jsonl'),
    ]),
    'DUPLICATE_SESSION_ID',
    /hostile-dup-1/,
  );
});

test('sessions without ids do not trip the duplicate check', async () => {
  const parsed = await readSessionLogs([
    fixture('hostile-duplicate-session-a.jsonl'),
    fixture('zero-classifiable-turns.jsonl'),
  ]);
  assert.equal(parsed.totals.classifiableTurns, 1);
});
test('duplicate check is per id, not per file: distinct ids pass together', async () => {
  const parsed = await readSessionLogs([
    fixture('hostile-duplicate-session-a.jsonl'),
    fixture('real-excerpt-t1-t6.jsonl'),
  ]);
  assert.equal(parsed.totals.classifiableTurns, 7);
  assert.equal(parsed.sessions.length, 2);
});

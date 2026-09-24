// The re-score must work on a fresh clone, where the gitignored docs mirror is absent, and must
// still fail when a mirrored price line no longer says what the receipt quotes. No key, no network.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { PRICES, SYNC_DOCS, score } from './measure.mjs';

/** A mirror root holding every cited price file, each cited line set by `lineFor(name, price)`. */
function mirror(lineFor) {
  const root = mkdtempSync(join(tmpdir(), 'jev-bmn-mirror-'));
  const files = {};
  for (const [name, p] of Object.entries(PRICES)) {
    files[p.file] ??= [];
    files[p.file][p.line - 1] = lineFor(name, p);
  }
  for (const [file, lines] of Object.entries(files)) {
    mkdirSync(join(root, dirname(file)), { recursive: true });
    writeFileSync(join(root, file), Array.from(lines, (l) => l ?? '').join('\n'));
  }
  return root;
}

test('absent mirror: the price check is NOT_RUN with the fetch command, and the row checks still pass', () => {
  const empty = mkdtempSync(join(tmpdir(), 'jev-bmn-nomirror-'));
  const r = score(undefined, { mirrorRoot: empty });
  assert.equal(r.prices, 'not_run');
  assert.match(r.text, /price check NOT_RUN/);
  assert.ok(r.text.includes(SYNC_DOCS), 'the fix is in the output');
  assert.deepEqual(r.failures, [], 'an absent mirror is not a failure of the committed rows');
  assert.match(r.text, /\| score \(work\/score-sst5\) \| 50\/50 \| 0\/50 \|/, 'rows were still scored');
});

test('a mirrored price line that moved is a failure, not NOT_RUN', () => {
  const moved = mirror((name, p) => (name === 'jev' ? '| Price (per Btok / per Mtok) | $84 / $0.084 |' : p.needle));
  const r = score(undefined, { mirrorRoot: moved });
  assert.equal(r.prices, 'mismatch');
  assert.equal(r.failures.length, 1);
  assert.match(r.failures[0], /price source moved: jev expects/);
});

test('a mirror that still says what we quote passes the price check', () => {
  const r = score(undefined, { mirrorRoot: mirror((_, p) => p.needle) });
  assert.equal(r.prices, 'ok');
  assert.deepEqual(r.failures, []);
});

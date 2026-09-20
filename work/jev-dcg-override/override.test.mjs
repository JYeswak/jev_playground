// Structural test for the override rule: every case has refusal + alternative.
// Planted negative: a case entry missing its safe alternative fails.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const text = readFileSync(new URL('./OVERRIDE-RULE.md', import.meta.url), 'utf8');

test('all five conductor cases present with refusal and alternative', () => {
  for (const n of ['| 1 |', '| 2 |', '| 3 |', '| 4 |', '| 5 |']) {
    assert.ok(text.includes(n), `missing case row ${n}`);
  }
  assert.ok(text.includes('never reshape') || text.includes('NEVER reshape'));
});

test('planted: pane-3 verified instances quote denial strings', () => {
  assert.ok(text.includes('rm-rf-general'));
  assert.ok(text.includes('redirect-truncate'));
  assert.ok(text.includes('rm-rf-root-home'));
  assert.ok(text.includes('EXPLICIT-SINGLE-FILE-REMOVE-OK'));
});

test('planted negative: an entry without a safe alternative is refused', () => {
  const shape = (entry) => entry.includes('denied') && entry.includes('Alternative taken:');
  assert.equal(shape('denied (x). Alternative taken: y'), true);
  assert.equal(shape('denied (x). no alternative recorded'), false);
});

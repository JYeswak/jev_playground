import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

test('packaged coding-agent seat is byte-identical to the measured seat', async () => {
  const source = await readFile(new URL('../../work/jev-a9fv/seat.mjs', import.meta.url), 'utf8');
  const packaged = await readFile(new URL('../templates/omp/jev-kit/coding-agent-seat.mjs', import.meta.url), 'utf8');
  assert.equal(packaged, source);
});

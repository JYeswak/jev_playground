#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const repo = new URL('..', import.meta.url).pathname;
const source = join(repo, 'bin/shape.mjs');
const test = join(repo, 'test/shape-bin.test.mjs');
const baselineHash = createHash('sha256').update(await readFile(source)).digest('hex');
const baseline = spawnSync(process.execPath, ['--test', test], { env: process.env, encoding: 'utf8' });
if (baseline.status !== 0) { console.error('BASELINE_FAILED: run the unmutated acceptance suite first'); process.exit(1); }
const mutations = [
  { name: 'share arithmetic halves denominator', needle: '(n / total) * 100', replacement: '(n / (total * 2)) * 100' },
  { name: 'skip logic drops no-usage counter', needle: "if (!u) { t.noUsage += 1; continue; }", replacement: "if (!u) { continue; }" },
  { name: 'residual arithmetic absorbs unknown field', needle: 'Number(declaredTotal) - (cr + cw + inp + out)', replacement: '0' },
];
const tmp = await mkdtemp(join(tmpdir(), 'shape-mutations-'));
let failures = 0;
for (const mutation of mutations) {
  const text = await readFile(source, 'utf8');
  const hits = text.split(mutation.needle).length - 1;
  if (hits !== 1) { console.log(`NOT_APPLIED ${mutation.name} hits=${hits}`); failures += 1; continue; }
  const mutant = join(tmp, `${mutations.indexOf(mutation)}.mjs`);
  await writeFile(mutant, text.replace(mutation.needle, mutation.replacement));
  const result = spawnSync(process.execPath, ['--test', test], { env: { ...process.env, SHAPE_BIN: mutant }, encoding: 'utf8' });
  if (result.status === 0) { console.log(`ESCAPED ${mutation.name}`); failures += 1; }
  else console.log(`CAUGHT ${mutation.name}`);
}
const afterHash = createHash('sha256').update(await readFile(source)).digest('hex');
if (afterHash !== baselineHash) { console.error('SOURCE_DRIFT'); failures += 1; }
console.log(`mutation-harness: ${mutations.length - failures}/${mutations.length} mutations caught`);
process.exitCode = failures ? 1 : 0;

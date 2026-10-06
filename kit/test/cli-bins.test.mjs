import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { repoRoot, runCli, freshHome } from './cli-support.mjs';

test('package bin metadata exposes classifier/clf and skill-gap', async () => {
  const pkg = JSON.parse(await readFile(join(repoRoot, 'kit/package.json'), 'utf8'));
  const lock = JSON.parse(await readFile(join(repoRoot, 'kit/package-lock.json'), 'utf8'));
  assert.deepEqual(lock.packages[''].bin, pkg.bin);
  assert.equal(pkg.name, 'jev-kit');
  assert.equal(pkg.private, true);
  assert.deepEqual(Object.keys(pkg.bin).sort(), ['classifier', 'clf', 'jev-skill-gap']);
  assert.equal(pkg.bin.classifier, 'bin/jev.mjs');
  assert.equal(pkg.bin.classifier, pkg.bin.clf);
  assert.equal(pkg.bin['jev-skill-gap'], 'bin/jev-skill-gap.mjs');
  assert.equal(Object.hasOwn(pkg.bin, 'jev'), false);

  const home = await freshHome('classifier-bins');
  const result = runCli(['--version'], { home });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, 'classifier 0.0.0\n');
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { repoRoot, runPackageBin, freshHome } from './cli-support.mjs';

test('package exposes only classifier/clf plus the retained skill-gap shim', async () => {
  const pkg = JSON.parse(await readFile(join(repoRoot, 'kit/package.json'), 'utf8'));
  const lock = JSON.parse(await readFile(join(repoRoot, 'kit/package-lock.json'), 'utf8'));
  assert.deepEqual(lock.packages[''].bin, pkg.bin);
  assert.equal(pkg.name, 'jev-kit');
  assert.equal(pkg.private, true);
  assert.deepEqual(Object.keys(pkg.bin).sort(), ['classifier', 'clf', 'jev-skill-gap']);
  assert.equal(pkg.bin.classifier, pkg.bin.clf);
  assert.equal(pkg.bin['jev-skill-gap'], 'bin/jev-skill-gap.mjs');
  assert.equal(Object.hasOwn(pkg.bin, 'jev'), false);

  const home = await freshHome('classifier-bins');
  const classifier = runPackageBin('classifier', ['--version'], { home });
  const alias = runPackageBin('clf', ['--version'], { home });
  assert.equal(classifier.status, 0, classifier.stderr);
  assert.equal(alias.status, 0, alias.stderr);
  assert.equal(classifier.stdout, 'classifier 0.0.0\n');
  assert.equal(alias.stdout, classifier.stdout);
});

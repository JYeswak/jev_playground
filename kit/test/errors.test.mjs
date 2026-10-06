import test from 'node:test';
import assert from 'node:assert/strict';
import { freshHome, runCli, examplePath } from './cli-support.mjs';
import { writeFile, mkdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { rewriteCliError, formatCliError } from '../dist/cli/errors.js';

test('unknown commands give a safe correction and the help command', async () => {
  const home = await freshHome('classifier-error-unknown');
  const result = runCli(['clasify'], { home });
  assert.equal(result.status, 64);
  assert.ok(result.stderr.includes('did you mean: classifier classify'));
  assert.ok(result.stderr.includes('see: classifier --help'));
});

test('a one-character flag typo is interpreted and reported without changing the JSON result', async () => {
  const home = await freshHome('classifier-error-flag');
  const result = runCli(['doctor', '--robto'], { home });
  assert.equal(result.status, 2);
  assert.ok(result.stderr.includes("interpreted as '--robot'"));
  assert.equal(JSON.parse(result.stdout).schema, 'classifier.doctor.v1');
});

test('missing input files report the option, example, remediation, and no_input exit', async () => {
  const home = await freshHome('classifier-error-input');
  const result = runCli(['classify', '--text', 'x', '--labels', 'nope.json', '--robot'], { home });
  assert.equal(result.status, 66);
  assert.ok(result.stderr.includes('--labels file not found: nope.json'));
  assert.ok(result.stderr.includes('example file: kit/examples/banking77-labels.json'));
  assert.equal(JSON.parse(result.stdout).status, 'NO_INPUT');
});
test('an existing label path is read normally and never gets the missing-input status', async () => {
  const home = await freshHome('classifier-error-existing-labels');
  const example = JSON.parse(await readFile(examplePath('banking77-example.json'), 'utf8'));
  const result = runCli([
    'classify', '--text', example.text, '--labels', examplePath('banking77-labels.json'), '--fake', '--robot',
  ], { home });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).status, 'OK');
  assert.ok(!result.stderr.includes('NO_INPUT'));
});
test('an unknown flag is ignored with a warning but a near miss runs its documented correction', async () => {
  const home = await freshHome('classifier-error-stage0');
  const typo = runCli(['doctor', '--robto'], { home });
  assert.equal(typo.status, 2);
  assert.ok(typo.stderr.includes("interpreted as '--robot'"));
  assert.equal(JSON.parse(typo.stdout).schema, 'classifier.doctor.v1');

  const distant = runCli(['doctor', '--zzzz'], { home });
  assert.equal(distant.status, 2);
  assert.ok(distant.stderr.includes("unknown flag '--zzzz' ignored"));
  assert.ok(!distant.stderr.includes('Did you mean:'));
});

test('a singular label flag points to the required plural flag and real example', async () => {
  const home = await freshHome('classifier-error-label-typo');
  const result = runCli(['classify', '--text', 'x', '--label', examplePath('banking77-labels.json')], { home });
  assert.equal(result.status, 64);
  assert.ok(result.stderr.includes('did you mean --labels?'));
  assert.ok(result.stderr.includes('kit/examples/banking77-labels.json'));
});

test('a missing API key is explicit NOT_RUN and points to offline operation', async () => {
  const home = await freshHome('classifier-error-no-key');
  const result = runCli(['classify', '--text', 'x', '--labels', examplePath('banking77-labels.json'), '--robot'], { home });
  assert.equal(result.status, 2);
  assert.equal(JSON.parse(result.stdout).status, 'NOT_RUN');
  assert.ok(result.stderr.includes('offline: add --fake'));
});

test('an unoffered fake label is refused without returning a decision', async () => {
  const home = await freshHome('classifier-error-invalid-answer');
  const labelsPath = join(home, 'labels.json');
  await writeFile(labelsPath, JSON.stringify(['not-offered', 'also-not-offered']));
  const result = runCli(['classify', '--text', 'x', '--labels', labelsPath, '--fake', '--robot'], { home });
  assert.equal(result.status, 3, `${result.stderr}\n${result.stdout}`);
  assert.equal(JSON.parse(result.stdout).status, 'REFUSED');
  assert.ok(result.stderr.includes('no decision emitted'));
});

test('more than twenty rank candidates refuses chunking with a safe reduction', async () => {
  const home = await freshHome('classifier-error-rank-limit');
  const candidatesPath = join(home, 'candidates.json');
  await writeFile(candidatesPath, JSON.stringify(Array.from({ length: 21 }, (_, index) => ({ id: `d${index}`, text: `Candidate ${index}` }))));
  const result = runCli(['rank', '--query', 'query', '--candidates', candidatesPath, '--fake', '--robot'], { home });
  assert.equal(result.status, 64, `${result.stderr}\n${result.stdout}`);
  assert.ok(result.stderr.includes('error: rank takes 2-20 candidates, got 21'));
  assert.ok(result.stderr.includes('top 20'));
});
test('fake gate mismatch points to the captured command', async () => {
  const home = await freshHome('classifier-error-gate-fixture');
  const result = runCli(['gate', '--fake', '--command', 'rm -rf /', '--robot'], { home });
  assert.equal(result.status, 64);
  assert.ok(result.stderr.includes('fixture command: classifier gate --fake --command "npm publish --access public"'));
});

test('installer collision is refused and names the first three paths', async () => {
  const home = await freshHome('classifier-error-install-collision');
  const repo = join(home, 'repo');
  await mkdir(join(repo, '.omp', 'tools'), { recursive: true });
  const paths = ['jev-rerank.ts', 'jev-claim-check.ts', 'jev-screen.ts', 'jev-flag.ts'];
  for (const path of paths) await writeFile(join(repo, '.omp', 'tools', path), 'user-owned');
  const result = runCli(['omp', 'install', '--dir', repo, '--robot'], { home });
  assert.equal(result.status, 4);
  assert.ok(result.stderr.includes('refusing to overwrite 4 unmanaged files'));
  assert.ok(result.stderr.includes('.omp/tools/jev-rerank.ts, .omp/tools/jev-claim-check.ts, .omp/tools/jev-screen.ts'));
  assert.ok(result.stderr.includes('preview: classifier omp install --dry-run'));
  for (const path of paths) assert.equal(await readFile(join(repo, '.omp', 'tools', path), 'utf8'), 'user-owned');
});

test('clef-unreachable formatter preserves its online-required code without a live probe', () => {
  const error = rewriteCliError({ reason: 'clef-unreachable', path: 'http://127.0.0.1:8010/v1/systemone' });
  assert.equal(error.exit_code, 6);
  const detail = formatCliError(error);
  assert.ok(detail.includes('use hosted: --backend jev'));
  assert.ok(detail.includes('diagnose: classifier doctor'));
});

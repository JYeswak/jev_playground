import test from 'node:test';
import assert from 'node:assert/strict';
import { freshHome, runCli } from './cli-support.mjs';
import { EXIT_CODES as CLI_EXIT_CODES } from '../src/cli/exit.mjs';
import { FAMILIES, dispatchCommand, validateFamilyNames } from '../dist/families/registry.js';

const META_VERBS = new Set(['overview', 'capabilities', 'robot-docs', 'schema', 'doctor', 'install', 'ask', 'help', 'skillgap']);
const FAMILY_VERBS = new Set(['run', 'batch', 'explain', 'cases', 'eval', 'calibrate']);
const HERMES_VERBS = new Set(['route', 'rerank', 'triage', 'search', 'plan', 'choose']);

test('capabilities, robot docs, and schema are generated from the registered families', async () => {
  const home = await freshHome('classifier-registry');
  const capabilitiesResult = runCli(['capabilities', '--json'], { home });
  assert.equal(capabilitiesResult.status, 0, capabilitiesResult.stderr);
  const capabilities = JSON.parse(capabilitiesResult.stdout);
  assert.equal(capabilities.contract_version, '1');
  assert.ok(capabilities.features);
  assert.ok(capabilities.exit_codes);
  assert.deepEqual(capabilities.exit_codes, CLI_EXIT_CODES);
  assert.ok(capabilities.env_vars);
  assert.deepEqual(Object.keys(capabilities.commands).sort(), ['ask', 'capabilities', 'classify', 'doctor', 'gate', 'help', 'omp install', 'omp uninstall', 'rank', 'robot-docs', 'schema', 'score', 'verify'].sort());
  for (const name of ['doctor', 'ask', 'classify', 'gate', 'rank', 'score', 'verify']) {
    assert.ok(capabilities.commands[name].exit_codes.includes(CLI_EXIT_CODES.NOT_RUN), `${name} advertises NOT_RUN`);
  }
  for (const [name, command] of Object.entries(capabilities.commands)) {
    assert.equal(name, command.name);
    if (command.primitive) {
      assert.ok(name.length >= 3 && name.length <= 10, name);
      assert.equal(name.toLowerCase(), name, name);
      assert.equal(META_VERBS.has(name) || FAMILY_VERBS.has(name) || HERMES_VERBS.has(name), false, name);
    }
    assert.ok(Array.isArray(command.exit_codes), `${name} has exit codes`);
    assert.ok(command.usage, `${name} has usage`);
  }

  const docsResult = runCli(['robot-docs', 'guide'], { home });
  assert.equal(docsResult.status, 0, docsResult.stderr);
  assert.ok(docsResult.stdout.includes('capabilities'));
  assert.ok(docsResult.stdout.split('\n').length <= 80);
  for (const command of Object.values(capabilities.commands)) {
    assert.ok(docsResult.stdout.includes(`- ${command.name}:`), command.name);
  }
  assert.deepEqual(
    Object.keys(capabilities.commands).filter((name) => FAMILIES.some((family) => family.name === name)).sort(),
    FAMILIES.map((family) => family.name).sort(),
  );

  const schemaResult = runCli(['schema', '--json'], { home });
  assert.equal(schemaResult.status, 0, schemaResult.stderr);
  assert.deepEqual(JSON.parse(schemaResult.stdout), capabilities);
  const rankHelp = runCli(['rank', '--help'], { home });
  assert.equal(rankHelp.status, 0, rankHelp.stderr);
  assert.ok(rankHelp.stdout.includes('rerank'));

  const aliasSchema = runCli(['schema', '--command', 'rerank'], { home });
  assert.equal(aliasSchema.status, 0, aliasSchema.stderr);
  assert.deepEqual(Object.keys(JSON.parse(aliasSchema.stdout).commands), ['rank']);
  assert.equal(dispatchCommand('rank'), 'rerank');
  assert.equal(dispatchCommand('rerank'), 'rerank');
});

test('family naming validator rejects meta, family, hermes, and malformed names', () => {
  const errors = validateFamilyNames([
    { name: 'doctor' },
    { name: 'run' },
    { name: 'triage' },
    { name: 'bad-name' },
    { name: 'sales' },
  ]);
  assert.equal(errors.length, 4);
  assert.ok(errors.some((error) => error.includes('reserved family name: doctor')));
  assert.ok(errors.some((error) => error.includes('reserved family name: run')));
  assert.ok(errors.some((error) => error.includes('reserved family name: triage')));
  assert.ok(errors.some((error) => error.includes('invalid family name: bad-name')));
});

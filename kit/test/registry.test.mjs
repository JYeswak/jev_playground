import test from 'node:test';
import assert from 'node:assert/strict';
import { freshHome, runCli } from './cli-support.mjs';
import { EXIT_CODES as CLI_EXIT_CODES } from '../src/cli/exit.mjs';
import * as registryModule from '../dist/families/registry.js';
const { FAMILIES, dispatchCommand, validateFamilyNames } = registryModule;

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

test('an injected family flows through the registry dispatch and generated surfaces', () => {
  assert.equal(typeof registryModule.createFamilyRegistry, 'function', 'the registry must expose one injectable family list');
  const observe = {
    name: 'observe',
    runner: 'score',
    primitive: 'score',
    aliases: ['inspect'],
    usage: 'observe --text T --levels FILE',
    description: 'Inspect an observation.',
  };
  const registry = registryModule.createFamilyRegistry([...FAMILIES, observe]);
  const capabilities = registry.capabilities();

  assert.equal(capabilities.commands.observe.name, 'observe');
  assert.equal(capabilities.commands.observe.primitive, 'score');
  assert.ok(capabilities.commands.observe.exit_codes.includes(CLI_EXIT_CODES.RETRYABLE));
  assert.equal(capabilities.commands.observe.output_format, 'classifier.<command>.v1');
  assert.ok(registry.robotDocs().includes('- observe: Inspect an observation. Usage: observe --text T --levels FILE.'));
  assert.ok(registry.robotDocs().includes('- `inspect` aliases `observe`.'));
  assert.equal(registry.schema().commands.observe.name, 'observe');
  assert.deepEqual(Object.keys(registry.schema('observe').commands), ['observe']);
  assert.deepEqual(Object.keys(registry.schema('inspect').commands), ['observe']);
  const dispatchedAlias = registry.dispatchCommand('inspect');
  assert.equal(dispatchedAlias, 'inspect');
  assert.equal(registry.familyForCommand(dispatchedAlias).runner, 'score');
  assert.deepEqual(registry.schema('inspect').commands.observe, capabilities.commands.observe);
});

test('family naming validator rejects meta, family, hermes, and malformed names', () => {
  const errors = validateFamilyNames([
    { name: 'overview' },
    { name: 'doctor' },
    { name: 'run' },
    { name: 'triage' },
    { name: 'bad-name' },
    { name: 'sales' },
  ]);
  assert.equal(errors.length, 5);
  assert.ok(errors.some((error) => error.includes('reserved family name: overview')));
  assert.ok(errors.some((error) => error.includes('reserved family name: doctor')));
  assert.ok(errors.some((error) => error.includes('reserved family name: run')));
  assert.ok(errors.some((error) => error.includes('reserved family name: triage')));
  assert.ok(errors.some((error) => error.includes('invalid family name: bad-name')));
});

test('every command exposes its schema and exit metadata', async () => {
  const home = await freshHome('classifier-registry-schema-all');
  const capabilities = JSON.parse(runCli(['capabilities', '--json'], { home }).stdout);
  for (const name of Object.keys(capabilities.commands)) {
    const result = runCli(['schema', '--command', name], { home });
    assert.equal(result.status, 0, `${name}: ${result.stderr}`);
    const body = JSON.parse(result.stdout);
    assert.deepEqual(Object.keys(body.commands), [name], name);
    const command = body.commands[name];
    assert.ok(command.usage, `${name} has usage`);
    assert.ok(command.description, `${name} has description`);
    assert.ok(Array.isArray(command.exit_codes) && command.exit_codes.length > 0, `${name} has exit codes`);
    assert.ok(command.exit_codes.includes(0), `${name} documents success`);
  }
});

test('generated surfaces are deterministic and stay parseable without color', async () => {
  const home = await freshHome('classifier-registry-deterministic');
  const first = runCli(['capabilities', '--json'], { home, env: { SOURCE_DATE_EPOCH: '1' } });
  const second = runCli(['capabilities', '--json'], { home, env: { SOURCE_DATE_EPOCH: '9999999999' } });
  assert.equal(first.status, 0, first.stderr);
  assert.equal(second.status, 0, second.stderr);
  assert.equal(second.stdout, first.stdout);
  const noColor = runCli(['capabilities', '--json'], { home, env: { NO_COLOR: '1' } });
  assert.equal(noColor.status, 0, noColor.stderr);
  assert.ok(!noColor.stdout.includes(String.fromCharCode(27)), 'no ANSI escapes with NO_COLOR=1');
  assert.ok(!noColor.stderr.includes(String.fromCharCode(27)), 'no ANSI escapes on stderr with NO_COLOR=1');
  JSON.parse(noColor.stdout);
  const docsFirst = runCli(['robot-docs', 'guide'], { home, env: { SOURCE_DATE_EPOCH: '1' } });
  const docsSecond = runCli(['robot-docs', 'guide'], { home, env: { SOURCE_DATE_EPOCH: '9999999999' } });
  assert.equal(docsFirst.status, 0, docsFirst.stderr);
  assert.equal(docsSecond.stdout, docsFirst.stdout);
});

test('a family dropped from one surface or a mutated schema field breaks the surfaces', async () => {
  const home = await freshHome('classifier-registry-consistency');
  const capabilities = JSON.parse(runCli(['capabilities', '--json'], { home }).stdout);
  const schema = JSON.parse(runCli(['schema', '--json'], { home }).stdout);
  const docs = runCli(['robot-docs', 'guide'], { home }).stdout;
  const inCapabilities = new Set(Object.keys(capabilities.commands));
  const inSchema = new Set(Object.keys(schema.commands));
  const inDocs = new Set(
    docs.split('\n').filter((line) => line.startsWith('- ')).map((line) => line.slice(2).split(':')[0]),
  );
  for (const family of FAMILIES.map((entry) => entry.name)) {
    assert.ok(inCapabilities.has(family), `${family} in capabilities`);
    assert.ok(inSchema.has(family), `${family} in schema`);
    assert.ok(inDocs.has(family), `${family} in robot-docs`);
  }
  const dropped = JSON.parse(JSON.stringify(capabilities));
  delete dropped.commands[FAMILIES[0].name];
  assert.ok(!Object.keys(dropped.commands).includes(FAMILIES[0].name), 'dropped family is gone from one surface');
  assert.ok(inSchema.has(FAMILIES[0].name), 'but still present in the other surface');
  assert.notDeepEqual(Object.keys(dropped.commands).sort(), Object.keys(schema.commands).sort());
  const mutated = JSON.parse(JSON.stringify(schema));
  mutated.commands[FAMILIES[0].name] = { ...mutated.commands[FAMILIES[0].name], exit_codes: [999] };
  assert.notDeepEqual(mutated.commands[FAMILIES[0].name], capabilities.commands[FAMILIES[0].name]);
});

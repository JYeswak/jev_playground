import test from 'node:test';
import assert from 'node:assert/strict';
import { join } from 'node:path';
import {
  defaultAgentDir,
  isSafeProfileName,
  profileAgentDir,
  resolveAgentDir,
  resolveConfigPath,
} from '../dist/install/omp-paths.js';

const HOME = '/tmp-omp-home/operator';
const OMP_HOME = `${HOME}/.omp`;

test('OMP_PROFILE selects the named profile agent dir', () => {
  assert.equal(
    resolveAgentDir({ home: HOME, ompProfile: 'muse' }),
    join(OMP_HOME, 'profiles', 'muse', 'agent'),
  );
});

test('empty OMP_PROFILE resolves to the default agent dir, shadowing PI_PROFILE', () => {
  assert.equal(
    resolveAgentDir({ home: HOME, ompProfile: '', piProfile: 'muse' }),
    join(OMP_HOME, 'agent'),
  );
});

test('unset profiles resolve to the default agent dir', () => {
  assert.equal(resolveAgentDir({ home: HOME }), join(OMP_HOME, 'agent'));
});

test('unset OMP_PROFILE falls back to PI_PROFILE', () => {
  assert.equal(
    resolveAgentDir({ home: HOME, piProfile: 'muse' }),
    join(OMP_HOME, 'profiles', 'muse', 'agent'),
  );
});

test('a custom absolute PI_CODING_AGENT_DIR wins when no OMP_PROFILE is set', () => {
  assert.equal(
    resolveAgentDir({ home: HOME, piCodingAgentDir: '/tmp-custom/agent' }),
    '/tmp-custom/agent',
  );
});

test('a legacy-derived PI_CODING_AGENT_DIR falls through to the PI chain', () => {
  assert.equal(
    resolveAgentDir({
      home: HOME,
      piCodingAgentDir: join(OMP_HOME, 'agent'),
      piProfile: 'muse',
    }),
    join(OMP_HOME, 'profiles', 'muse', 'agent'),
  );
});

test('a relative PI_CODING_AGENT_DIR is refused as usage', () => {
  assert.throws(
    () => resolveAgentDir({ home: HOME, piCodingAgentDir: 'relative/agent' }),
    (error) => error.code === 'USAGE',
  );
});

test('reserved and traversal profile names are refused', () => {
  for (const name of ['con', 'nul', 'COM1', 'lpt9', 'aux.txt', '.', '..', 'a/b', 'a\\b']) {
    assert.equal(isSafeProfileName(name), false, name);
    assert.throws(
      () => profileAgentDir(OMP_HOME, name),
      (error) => error.code === 'USAGE',
      name,
    );
  }
  assert.equal(isSafeProfileName('muse'), true);
  assert.equal(isSafeProfileName('default'), true);
});

test('default profile name maps to the default agent dir', () => {
  assert.equal(profileAgentDir(OMP_HOME, 'default'), join(OMP_HOME, 'agent'));
  assert.equal(defaultAgentDir(HOME), join(OMP_HOME, 'agent'));
});

test('config path defaults to the resolved agent dir', () => {
  assert.equal(
    resolveConfigPath({ home: HOME, ompProfile: 'muse' }),
    join(OMP_HOME, 'profiles', 'muse', 'agent', 'config.yml'),
  );
});

test('an absolute PI_CONFIG_DIR overrides the config path', () => {
  assert.equal(
    resolveConfigPath({ home: HOME, piConfigDir: '/tmp-custom/omp-config.yml' }),
    '/tmp-custom/omp-config.yml',
  );
});

test('a relative PI_CONFIG_DIR is refused as usage', () => {
  assert.throws(
    () => resolveConfigPath({ home: HOME, piConfigDir: 'relative/config.yml' }),
    (error) => error.code === 'USAGE',
  );
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectors as logDetectors } from '../src/doctor/detectors/logs.mjs';
import { detectors as capDetectors } from '../src/doctor/detectors/caps.mjs';
import { detectors as anomalyDetectors } from '../src/doctor/detectors/anomalies.mjs';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(testDir, '../..');
const now = Date.parse('2026-10-06T12:00:00.000Z');
const expected = JSON.parse(await fs.readFile(path.join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));
let fixtureSerial = 0;

function surface(id) {
  const found = expected.surfaces.find((item) => item.id === id);
  assert.ok(found, `expected.json has no ${id} surface`);
  assert.equal(typeof found.log, 'string', `expected.json has no log mapping for ${id}`);
  return found;
}

async function fixture(label, surfaces) {
  const root = path.join(repoRoot, 'var', 'agent-tmp', `${label}.${process.pid}.${fixtureSerial++}`);
  const repo = path.join(root, 'repo');
  const stateDir = path.join(root, 'state');
  await fs.mkdir(repo, { recursive: true });
  await fs.mkdir(stateDir, { recursive: true });
  await fs.writeFile(path.join(root, '.owner'), `pid=${process.pid}\nlabel=${label}\nrepo=jev\ncreated=2026-10-06T12:00:00.000Z\n`);
  return {
    root, repo, stateDir,
    ctx: {
      repo, home: root, stateDir, inventory: { surfaces }, now, tier: 'default', online: false, env: {},
      exec: async () => { throw new Error('unexpected exec'); },
      fetch: async () => { throw new Error('unexpected fetch'); },
    },
  };
}

function detector(rows, id) {
  const found = rows.find((item) => item.id === id);
  assert.ok(found, `missing detector ${id}`);
  return found;
}

async function writeRows(stateDir, log, rows) {
  await fs.writeFile(path.join(stateDir, log), rows.map((row) => typeof row === 'string' ? row : JSON.stringify(row)).join('\n') + (rows.length ? '\n' : ''), { mode: 0o600 });
}

const logs = logDetectors;
const caps = capDetectors;
const anomalies = anomalyDetectors;

test('declared-OFF log writing fires only for fresh rows and reports its exact path without row contents', async () => {
  const off = surface('websearch-rerank');
  const f = await fixture('doctor-log-off', [off]);
  const secret = 'secret-value-must-not-escape';
  await writeRows(f.stateDir, off.log, [{ ts: new Date(now - 60_000).toISOString(), instance: 'test-instance', prompt: secret }]);
  const results = await detector(logs, 'fm-logs-off-surface-writing').run(f.ctx);
  assert.equal(results.length, 1);
  assert.equal(results[0].evidence.path, path.join(f.stateDir, off.log));
  assert.equal(results[0].evidence.count, 1);
  assert.equal(JSON.stringify(results).includes(secret), false);

  await writeRows(f.stateDir, off.log, [{ ts: new Date(now - 4 * 60 * 60_000).toISOString(), instance: 'old' }]);
  assert.deepEqual(await detector(logs, 'fm-logs-off-surface-writing').run(f.ctx), []);
  await writeRows(f.stateDir, off.log, []);
  assert.deepEqual(await detector(logs, 'fm-logs-off-surface-writing').run(f.ctx), []);
});

test('declared-on logs are silent when absent or only old rows are present', async () => {
  const on = surface('gate-observe');
  const f = await fixture('doctor-log-freshness', [on]);
  const silent = detector(logs, 'fm-logs-silent-surface');
  assert.equal((await silent.run(f.ctx)).length, 1);
  await writeRows(f.stateDir, on.log, [{ ts: new Date(now - 4 * 60 * 60_000).toISOString(), status: 'ok' }]);
  assert.equal((await silent.run(f.ctx)).length, 1);
  await writeRows(f.stateDir, on.log, []);
  assert.equal((await silent.run(f.ctx)).length, 1);
});

test('vendor-shadow old rows are quiet with zero commits and silent after a later commit', async () => {
  const vendor = surface('vendor-shadow');
  const f = await fixture('doctor-vendor-freshness', [vendor]);
  const lastTs = new Date(now - 10 * 60 * 60_000).toISOString();
  await writeRows(f.stateDir, vendor.log, [{ ts: lastTs, status: 'observed' }]);
  const calls = [];
  f.ctx.exec = async (command, args, options) => {
    calls.push({ command, args, options });
    return { code: 0, stdout: '' };
  };
  const silent = detector(logs, 'fm-logs-silent-surface');
  assert.deepEqual(await silent.run(f.ctx), []);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].command, 'git');
  assert.deepEqual(calls[0].args.slice(0, 4), ['-C', f.repo, 'log', `--since=${lastTs}`]);
  assert.equal(calls[0].options.timeout, 500);
  assert.equal(calls[0].options.maxBuffer, 1024);

  f.ctx.exec = async () => ({ code: 0, stdout: 'c0ffee' });
  const results = await silent.run(f.ctx);
  assert.equal(results.length, 1);
  assert.equal(results[0].evidence.path, path.join(f.stateDir, vendor.log));
  assert.equal(results[0].evidence.commits_since_last_row, true);
});

test('old schema inside the anchored 24-hour window is reported against its declared writer source', async () => {
  const injection = surface('injection-shadow');
  const f = await fixture('doctor-log-schema', [injection]);
  const source = path.join(repoRoot, injection.file);
  const scratchSource = path.join(f.repo, injection.file);
  await fs.mkdir(path.dirname(scratchSource), { recursive: true });
  const writerText = await fs.readFile(source, 'utf8');
  await fs.writeFile(scratchSource, writerText);
  const marker = writerText.indexOf('LOG_SCHEMA');
  const equals = writerText.indexOf('=', marker + 10);
  const doubleQuote = writerText.indexOf('"', equals + 1);
  const singleQuote = writerText.indexOf("'", equals + 1);
  const delimiter = doubleQuote < 0 ? singleQuote : singleQuote < 0 ? doubleQuote : Math.min(doubleQuote, singleQuote);
  assert.ok(marker >= 0 && equals >= 0 && delimiter >= 0);
  const close = writerText.indexOf(writerText[delimiter], delimiter + 1);
  assert.ok(close > delimiter);
  const currentSchema = writerText.slice(delimiter + 1, close);
  const versionMarker = currentSchema.lastIndexOf('.v');
  const version = Number(currentSchema.slice(versionMarker + 2));
  assert.ok(versionMarker >= 0 && Number.isInteger(version) && version > 1);
  const oldSchema = `${currentSchema.slice(0, versionMarker)}.v${version - 1}`;
  const secret = 'api-key-private-value';
  await writeRows(f.stateDir, injection.log, [
    { schema: oldSchema, ts: new Date(now - 30 * 60_000).toISOString(), token: secret },
    { schema: currentSchema, ts: new Date(now - 20 * 60_000).toISOString() },
  ]);
  const results = await detector(logs, 'fm-logs-stale-schema-writer').run(f.ctx);
  assert.equal(results.length, 1);
  assert.equal(results[0].evidence.path, path.join(f.stateDir, injection.log));
  assert.equal(results[0].evidence.schema, oldSchema);
  assert.equal(JSON.stringify(results).includes(secret), false);
});

test('malformed tail rows are counted without echoing malformed text', async () => {
  const injection = surface('injection-shadow');
  const f = await fixture('doctor-log-malformed', [injection]);
  const raw = '{ "password": "private-row-secret"';
  await writeRows(f.stateDir, injection.log, [raw]);
  const results = await detector(logs, 'fm-logs-unparsable-rows').run(f.ctx);
  assert.equal(results.length, 1);
  assert.equal(results[0].evidence.path, path.join(f.stateDir, injection.log));
  assert.equal(results[0].evidence.count, 1);
  assert.equal(JSON.stringify(results).includes(raw), false);
  assert.equal(JSON.stringify(results).includes('private-row-secret'), false);
});

test('open modes and gate-observe command-bearing rows are reported without exposing commands', async () => {
  const gate = surface('gate-observe');
  const f = await fixture('doctor-log-mode', [gate]);
  const file = path.join(f.stateDir, gate.log);
  await writeRows(f.stateDir, gate.log, [{ ts: new Date(now - 60_000).toISOString(), status: 'ok' }]);
  await fs.chmod(file, 0o640);
  const modeDetector = detector(logs, 'fm-logs-mode-too-open');
  const open = await modeDetector.run(f.ctx);
  assert.equal(open.length, 1);
  assert.equal(open[0].evidence.path, file);
  assert.equal(open[0].evidence.mode, 0o640);
  assert.equal(open[0].severity, 'P2');

  const privateCommand = 'private command and secret-token-value';
  await writeRows(f.stateDir, gate.log, [{ ts: new Date(now - 30_000).toISOString(), status: 'ok', cmd: privateCommand }]);
  await fs.chmod(file, 0o600);
  const commandFinding = await modeDetector.run(f.ctx);
  assert.equal(commandFinding.length, 1);
  assert.equal(commandFinding[0].evidence.path, file);
  assert.equal(commandFinding[0].evidence.mode, 0o600);
  assert.equal(commandFinding[0].evidence.cmd_rows, 1);
  assert.equal(commandFinding[0].severity, 'P1');
  assert.equal(JSON.stringify(commandFinding).includes(privateCommand), false);
});

test('cap detection requires the documented daily-cap reason, not approval-required rows', async () => {
  const injection = surface('injection-shadow');
  const f = await fixture('doctor-log-caps', [injection]);
  await writeRows(f.stateDir, injection.log, [
    { ts: new Date(now - 60_000).toISOString(), status: 'cap', reason: 'recipient-and-data-class-approval-required', tokens: 99 },
  ]);
  const capDetector = detector(caps, 'fm-caps-hit');
  assert.deepEqual(await capDetector.run(f.ctx), []);
  await writeRows(f.stateDir, injection.log, [
    { ts: new Date(now - 60_000).toISOString(), status: 'cap', reason: 'daily-call-cap', tokens: 99 },
  ]);
  const results = await capDetector.run(f.ctx);
  assert.equal(results.length, 1);
  assert.equal(results[0].evidence.path, path.join(f.stateDir, injection.log));
  assert.equal(results[0].evidence.hits_24h, 1);
  assert.equal(results[0].severity, 'P1');
});

test('error spike thresholds fire while the documented D9 24-hour share remains quiet', async () => {
  const gate = surface('gate-observe');
  const f = await fixture('doctor-log-anomaly', [gate]);
  const rows = [];
  // D9 baseline: 265 / 3,837 in 24h and 6,748 / 27,297 in 7d.
  for (let i = 0; i < 3837; i += 1) {
    const error = Math.floor((i + 1) * 265 / 3837) > Math.floor(i * 265 / 3837);
    rows.push({
      ts: new Date(now - Math.floor((i + 1) * DAY_MS / 3837)).toISOString(),
      status: error ? 'error' : 'ok',
      ...(error ? { reason: 'daily-error' } : {}),
    });
  }
  for (let i = 0; i < 27297 - 3837; i += 1) {
    const error = i < 6748 - 265;
    rows.push({
      ts: new Date(now - DAY_MS - Math.floor((i + 1) * 6 * DAY_MS / (27297 - 3837))).toISOString(),
      status: error ? 'failed' : 'ok',
      ...(error ? { reason: 'weekly-error' } : {}),
    });
  }
  assert.equal(rows.length, 27297);
  assert.equal(rows.filter((row) => Date.parse(row.ts) >= now - DAY_MS).length, 3837);
  assert.equal(rows.filter((row) => Date.parse(row.ts) >= now - DAY_MS && row.status === 'error').length, 265);
  assert.equal(rows.filter((row) => Date.parse(row.ts) >= now - 7 * DAY_MS).length, 27297);
  assert.equal(rows.filter((row) => Date.parse(row.ts) >= now - 7 * DAY_MS && ['error', 'failed'].includes(row.status)).length, 6748);
  await writeRows(f.stateDir, gate.log, rows);
  const anomalyDetector = detector(anomalies, 'fm-anomaly-error-spike');
  assert.deepEqual(await anomalyDetector.run(f.ctx), []);

  const spike = await fixture('doctor-log-anomaly-spike', [gate]);
  const spikeRows = [];
  for (let i = 0; i < 50; i += 1) spikeRows.push({ ts: new Date(now - i * 60_000).toISOString(), status: 'error', reason: 'upstream-timeout' });
  for (let i = 0; i < 100; i += 1) spikeRows.push({ ts: new Date(now - DAY_MS - i * 60_000).toISOString(), status: 'ok' });
  await writeRows(spike.stateDir, gate.log, spikeRows);
  const fired = await detector(anomalies, 'fm-anomaly-error-spike').run(spike.ctx);
  assert.equal(fired.length, 1);
  assert.equal(fired[0].evidence.path, path.join(spike.stateDir, gate.log));
  assert.equal(fired[0].evidence.errors_24h, 50);
  assert.equal(JSON.stringify(fired).includes('secret-value'), false);
});

const DAY_MS = 24 * 60 * 60_000;

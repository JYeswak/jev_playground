// R44 trigger tests: blanking probe. firesFn is a stub here; the real wiring
// passes the shipped extension (see organic-fires.mjs). No Jev calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import { programSpans, blankDataLiterals, suppressFire } from './exec-data.mjs';

const TRIG = 'chmod -R 777 /etc/x';
// Fake firesFn standing in for the shipped rule: fires iff TRIG text present.
const ruleStub = async (cmd) => cmd.includes(TRIG);

// The 5 surviving organic-fire shapes (from /tmp/organic-fires-full.json).
test('data: string field in -e program suppresses', async () => {
  const cmd = `node -e "import('x').then(m => { const r = {command: '${TRIG}'}; console.log(r); })"`;
  assert.equal(await suppressFire(cmd, ruleStub), true);
});

test('data: test argument compared, never executed, suppresses', async () => {
  const cmd = `node --input-type=module -e "await h({command: '${TRIG}'}); await h({command: 'echo hi'});"`;
  assert.equal(await suppressFire(cmd, ruleStub), true);
});

test('data: python record-writing suppresses', async () => {
  const cmd = `python3 -c "import json; recs=[{'id':'a','command':'${TRIG}'}]; json.dump(recs,open('/tmp/c.json','w'))"`;
  assert.equal(await suppressFire(cmd, ruleStub), true);
});

test('EXECUTED: literal fed to execSync stands', async () => {
  const cmd = `node -e "const {execSync} = require('child_process'); execSync('${TRIG}')"`;
  assert.equal(await suppressFire(cmd, ruleStub), false);
});

test('EXECUTED: bare trigger outside any program span stands', async () => {
  const cmd = `${TRIG} 2>&1 | tail -5`;
  assert.equal(await suppressFire(cmd, ruleStub), false);
});

test('planted negative: mixed executed + data stands (fail-closed)', async () => {
  const cmd = `node -e "execSync('${TRIG}')" && echo '${TRIG}'`;
  assert.equal(await suppressFire(cmd, ruleStub), false);
});

test('planted: no program spans means nothing to blank, stands', async () => {
  const { blankedAny } = blankDataLiterals('echo hello');
  assert.equal(blankedAny, false);
  assert.equal(await suppressFire('echo hello', async () => true), false);
});

test('programSpans finds -e bodies with flags before them', () => {
  const spans = programSpans(`node --input-type=module -e "doom('x')"`);
  assert.equal(spans.length, 1);
  assert.ok(spans[0].body.includes("doom('x')"));
});

test('blanking preserves coordinates (spaces, no newlines touched)', () => {
  const cmd = `node -e "use('${TRIG}')"`;
  const { blanked, blankedAny } = blankDataLiterals(cmd);
  assert.equal(blankedAny, true);
  assert.equal(blanked.length, cmd.length);
  assert.ok(!blanked.includes(TRIG));
});

test('data: flags with separate values before -e do not hide the program', async () => {
  const cmd = `node --no-warnings --import tsx --input-type=module -e "await h({command: '${TRIG}'});"`;
  assert.equal(await suppressFire(cmd, ruleStub), true);
});

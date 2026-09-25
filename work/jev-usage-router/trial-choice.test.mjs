// Offline tests for trial-choice.mjs (jev-vbh.4). No key, no network: every answer is faked.
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { askJevChoice } from '../jev-client/src/index.ts';
import { CRITERIA, INSTRUCTIONS, routeState } from './src/router.mjs';
import { lexicalRoute, majority, MODEL, policyAction, runTrial, sampleGoals, summarize } from './trial-choice.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));

const goal = (i, label, extra = {}) => ({ i, goal: `goal ${i}`, label, short: false, from_pane1: false, ...extra });
const answer = (choice, confidence) => ({ ok: true, choice, confidence, probabilities: { [choice]: confidence }, latencyMs: 1, model: MODEL });
const row = (g, repeat, a) => ({ i: g.i, repeat, ok: a.ok, reason: a.ok ? null : a.reason, choice: a.ok ? a.choice : null, action: policyAction(a) });

test('sample keeps every off-local goal and draws the same number of local goals, deterministically', () => {
  const goals = [...Array.from({ length: 50 }, (_, i) => goal(i, 'local')), goal(50, 'research'), goal(51, 'browser'), goal(52, 'research')];
  const a = sampleGoals(goals);
  assert.equal(a.filter((g) => g.label !== 'local').length, 3);
  assert.equal(a.filter((g) => g.label === 'local').length, 3);
  assert.deepEqual(sampleGoals(goals).map((g) => g.i), a.map((g) => g.i), 'same seed, same sample');
  assert.notDeepEqual(sampleGoals(goals, 7).map((g) => g.i), a.map((g) => g.i), 'the seed actually drives the draw');
  assert.deepEqual(a.map((g) => g.i), a.map((g) => g.i).slice().sort((x, y) => x - y));
});

test('the policy abstains as bypass below the 0.55 floor and acts at it', () => {
  assert.equal(policyAction(answer('research', 0.54)), 'bypass');
  assert.equal(policyAction(answer('research', 0.55)), 'research');
  assert.equal(policyAction({ ok: false, reason: 'timeout' }), null);
});

test('the trial sends exactly the request the router sends, on the pinned model', async () => {
  const seen = [];
  await runTrial({
    sample: [goal(3, 'local')],
    askChoice: async (o) => { seen.push(o); return answer('local', 0.9); },
    codeSha: 'x'.repeat(64),
  });
  assert.equal(seen.length, 3, 'three repeats');
  for (const o of seen) {
    assert.deepEqual(o.state, routeState({ goal: 'goal 3' }));
    assert.equal(o.instructions, INSTRUCTIONS);
    assert.equal(o.classes, CRITERIA);
    assert.equal(o.model, 'jev-1.13.0');
  }
});

test('every row carries a code hash and a UTC timestamp', async () => {
  const { rows } = await runTrial({ sample: [goal(1, 'local')], askChoice: async () => answer('local', 0.9), codeSha: 'a'.repeat(64) });
  for (const r of rows) {
    assert.equal(r.code_sha256, 'a'.repeat(64));
    assert.match(r.recorded_at_utc, /Z$/);
  }
});

test('an off-label answer from the real client is counted incoherent, not transport', async () => {
  const offLabel = async () => ({
    ok: true, status: 200, headers: { get: (n) => (n.toLowerCase() === 'content-type' ? 'application/json' : null) }, body: null,
    clone() { return this; },
    text: async () => JSON.stringify({ answers: { choice: { type: 'choice', choice: 'teleport', confidence: 0.9, probabilities: { teleport: 0.9 } } } }),
  });
  const g = goal(1, 'research');
  const { rows } = await runTrial({
    sample: [g],
    askChoice: (o) => askJevChoice({ ...o, apiKey: 'test-key', fetchImpl: offLabel }),
    codeSha: 'b'.repeat(64),
  });
  const s = summarize([g], rows, 0.04);
  assert.equal(s.incoherent, 3);
  assert.equal(s.transport_failures, 0);
  assert.equal(s.goals_answered, 0, 'a refused answer is never scored as a route');
});

test('three consecutive 402 answers stop the run and no further request is sent', async () => {
  let calls = 0;
  const sample = Array.from({ length: 10 }, (_, i) => goal(i, 'local'));
  const { rows, stopped } = await runTrial({
    sample,
    concurrency: 1,
    askChoice: async () => { calls++; return { ok: false, reason: 'http', error: '402 billing_error', latencyMs: 1, model: MODEL }; },
    codeSha: 'c'.repeat(64),
  });
  assert.equal(stopped, true);
  assert.equal(calls, 3);
  assert.equal(rows.length, 3);
});

test('drift, majority action, transport and the short cell are counted from the rows', () => {
  const a = goal(1, 'research', { short: true });
  const b = goal(2, 'research', { short: true });
  const c = goal(3, 'local');
  const rows = [
    row(a, 0, answer('research', 0.9)), row(a, 1, answer('local', 0.9)), row(a, 2, answer('research', 0.9)),
    row(b, 0, answer('research', 0.4)), row(b, 1, answer('research', 0.4)), row(b, 2, { ok: false, reason: 'timeout' }),
    row(c, 0, answer('research', 0.8)), row(c, 1, answer('research', 0.8)), row(c, 2, answer('research', 0.8)),
  ];
  const s = summarize([a, b, c], rows, 0.5);
  assert.equal(s.drift_goals, 1, 'only goal 1 changed its choice across repeats');
  assert.equal(s.transport_failures, 1);
  assert.equal(s.incoherent, 0);
  assert.equal(s.jev.off_local_recall, 0.5, 'goal 1 routes research by majority; goal 2 abstains');
  assert.equal(s.jev.short_routed_or_abstained, 2, 'an abstain on a short off-local goal is safe');
  assert.equal(s.jev.local_false_route, 1);
  assert.equal(s.jev.precision_at_prevalence, (0.5 * 0.5) / (0.5 * 0.5 + 1 * 0.5));
  assert.equal(s.always_local.off_local_recall, 0);
});

test('majority breaks ties toward the first repeat', () => {
  assert.equal(majority(['local', 'research', 'bypass']), 'local');
  assert.equal(majority(['bypass', 'research', 'research']), 'research');
});

test('the lexical baseline is the preregistered rule', () => {
  assert.equal(lexicalRoute('search arxiv for the paper'), 'research');
  assert.equal(lexicalRoute('see https://example.com'), 'research');
  assert.equal(lexicalRoute('click the button in the browser'), 'browser');
  assert.equal(lexicalRoute('fix the failing test'), 'local');
});

test('without a key the trial prints NOT_RUN, exits 2 and sends nothing', () => {
  const env = { ...process.env };
  delete env.TYPESAFE_API_KEY;
  const r = spawnSync(process.execPath, ['--experimental-strip-types', path.join(HERE, 'trial-choice.mjs')], { env, encoding: 'utf8' });
  assert.equal(r.status, 2, r.stdout + r.stderr);
  assert.match(r.stdout, /^NOT_RUN/m);
});

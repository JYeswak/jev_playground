import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// jev-s0f1. The consistency demos' recorded answers judge a cookbook post and a cookbook claim, so
// their --live lane must SEND that text; before the fix the live state was the id alone. This runs
// each demo's real --live lane offline: a preloaded fetch stands in for the TypeSafe endpoint,
// records every request's `state`, and answers with a valid shape. No network, no real key (a
// placeholder key only gets the client past its unconfigured check; the fetch never leaves the
// process). It asserts on what went over the wire, not on the demo's source.
const DEMOS = join(dirname(fileURLToPath(import.meta.url)), '..');
const KEY_VARS = ['TYPESAFE_API_KEY', 'TYPE_SAFE_AI_KEY', 'JEV_API_KEY'];
const baseEnv = Object.fromEntries(Object.entries(process.env).filter(([k]) => !KEY_VARS.includes(k)));

const PRELOAD = `
import { appendFileSync } from 'node:fs';
globalThis.fetch = async (url, init) => {
  const sent = JSON.parse(init.body);
  appendFileSync(process.env.LIVE_STATE_CAPTURE, JSON.stringify(sent.state) + '\\n');
  const answers = {};
  for (const [key, q] of Object.entries(sent.questions)) {
    if (q.type === 'choice') {
      const labels = Object.keys(q.criteria);
      answers[key] = { type: 'choice', choice: labels[0], confidence: 0.9,
        probabilities: Object.fromEntries(labels.map((l, i) => [l, i === 0 ? 0.9 : 0.1 / (labels.length - 1)])) };
    } else {
      answers[key] = { type: 'noul', noul: 0.5 };
    }
  }
  return new Response(JSON.stringify({ answers, model: sent.model }), {
    status: 200, headers: { 'content-type': 'application/json' },
  });
};
`;

function runLive(name) {
  const dir = mkdtempSync(join(tmpdir(), 'live-state-'));
  const preload = join(dir, 'preload.mjs');
  const capture = join(dir, 'states.jsonl');
  writeFileSync(preload, PRELOAD);
  const r = spawnSync(process.execPath, ['--import', preload, join(DEMOS, name, 'demo.mjs'), '--live'], {
    env: { ...baseEnv, TYPESAFE_API_KEY: 'offline-placeholder', LIVE_STATE_CAPTURE: capture },
    encoding: 'utf8',
    timeout: 60000,
  });
  const states = existsSync(capture)
    ? readFileSync(capture, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l))
    : [];
  return { r, states };
}

test('consistency --live sends the cookbook post, not just its id', () => {
  const { r, states } = runLive('consistency');
  assert.equal(r.status, 0, `exit ${r.status}: ${r.stderr.slice(-400)}`);
  assert.equal(states.length, 3, 'three repeats, one request each');
  for (const s of states) {
    assert.equal(s.post_id, 'P-88213');
    assert.match(s.content?.text ?? '', /^Are you seriously this dense\?/, 'post text is in the state');
    assert.match(s.content.text, /I'll end your whole channel\.$/);
    assert.equal(s.content.link_domain, 'discord.gg');
    assert.deepEqual(s.reports?.report_reasons, ['harassment', 'spam', 'threat']);
    assert.equal(s.author?.prior_strikes, 1);
  }
});

test('consistency-noul --live sends the cookbook claim, not just its id', () => {
  const { r, states } = runLive('consistency-noul');
  assert.equal(r.status, 0, `exit ${r.status}: ${r.stderr.slice(-400)}`);
  assert.equal(states.length, 3, 'three repeats, one request each');
  for (const s of states) {
    assert.equal(s.claim?.claim_id, 'CLM-55029');
    assert.match(s.claim.description ?? '', /track-day event/, 'claim text is in the state');
    const sum = (s.claim.line_items ?? []).reduce((n, li) => n + li.cost, 0);
    assert.equal(sum, s.claim.amount_claimed, 'line items add up to 3250');
    assert.equal(s.policy?.coverages?.rental_reimbursement, false);
    assert.deepEqual(s.policy.exclusions, ['track/competitive driving', 'drivers not listed on the policy']);
    assert.match(s.adjuster_notes?.[0]?.note ?? '', /^Collision coverage active\. Approved\./);
  }
});

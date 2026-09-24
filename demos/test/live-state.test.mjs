import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SDK_PREREQ } from '../../work/sdk/require-installed.mjs';

// jev-s0f1 and jev-t6yt. The consistency demos' recorded answers judge a cookbook post and a cookbook
// claim under the cookbooks' rubrics, so their --live lane must send that post / claim, in the
// cookbook's state shape ({uid, post} / {uid, claim}), with the cookbook's questions. Before the
// fixes the state was the id alone and the Choice questions were a generic "Pick the single most
// applicable label for <key>." with no label descriptions.
//
// This runs each demo's real --live lane offline: a preloaded fetch stands in for the TypeSafe
// endpoint, records every request's `state` and `questions`, and answers with a valid shape. No
// network, no real key (a placeholder key only gets the client past its unconfigured check; the
// fetch never leaves the process). It asserts on what went over the wire, not on the demo's source.
const DEMOS = join(dirname(fileURLToPath(import.meta.url)), '..');
const KEY_VARS = ['TYPESAFE_API_KEY', 'TYPE_SAFE_AI_KEY', 'JEV_API_KEY'];
const baseEnv = Object.fromEntries(Object.entries(process.env).filter(([k]) => !KEY_VARS.includes(k)));

// sha256 of the canonical wire questions (sorted keys, compact JSON) that the cookbooks' own
// system_one calls send: Choice(instructions, criteria) per rubric row for the choice cookbook,
// Noul(instructions) per question for the noul cookbook. Computed from the dicts in
// docs-mirror/typesafe/cookbooks/consistency_{choice,noul}_cookbook.md (not committed here, so the
// digest is pinned; a cookbook change must re-derive it on purpose).
const COOKBOOK_QUESTIONS_SHA256 = {
  consistency: '527b72612909a2436e3e803789d6334e7f33eaa21ad0df5c716cd9c87a0e94d1',
  'consistency-noul': '63e4886eeb9d9acbab91efc0523063738bdcdbb0d4c9cadf6a9eaf9d29ea4f00',
};

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((k) => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}
const sha256 = (value) => createHash('sha256').update(canonical(value)).digest('hex');

const PRELOAD = `
import { appendFileSync } from 'node:fs';
globalThis.fetch = async (url, init) => {
  const sent = JSON.parse(init.body);
  appendFileSync(process.env.LIVE_STATE_CAPTURE, JSON.stringify({ state: sent.state, questions: sent.questions }) + '\\n');
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
  const capture = join(dir, 'requests.jsonl');
  writeFileSync(preload, PRELOAD);
  const r = spawnSync(process.execPath, ['--import', preload, join(DEMOS, name, 'demo.mjs'), '--live'], {
    env: { ...baseEnv, TYPESAFE_API_KEY: 'offline-placeholder', LIVE_STATE_CAPTURE: capture },
    encoding: 'utf8',
    timeout: 60000,
  });
  const requests = existsSync(capture)
    ? readFileSync(capture, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l))
    : [];
  // The live lane loads the TypeSafe SDK from work/sdk/node_modules, which a fresh clone lacks: the
  // client then refuses as sdk-missing before any request, so nothing is captured. Say that plainly
  // instead of failing on an empty capture.
  if (requests.length === 0 && /sdk-missing|@typesafe-ai\/sdk is not installed/.test(`${r.stdout}\n${r.stderr}`)) {
    assert.fail(SDK_PREREQ);
  }
  assert.equal(r.status, 0, `exit ${r.status}: ${`${r.stdout}\n${r.stderr}`.slice(-400)}`);
  assert.equal(requests.length, 3, 'three repeats, one request each');
  return requests;
}

test('consistency --live sends the cookbook post as {uid, post}', () => {
  for (const { state } of runLive('consistency')) {
    assert.deepEqual(Object.keys(state).sort(), ['post', 'uid'], 'state is {uid, post}, not the post spread or an id');
    const p = state.post;
    assert.equal(p.post_id, 'P-88213');
    assert.match(p.content?.text ?? '', /^Are you seriously this dense\?/, 'post text is in the state');
    assert.match(p.content.text, /I'll end your whole channel\.$/);
    assert.equal(p.content.link_domain, 'discord.gg');
    assert.deepEqual(p.reports?.report_reasons, ['harassment', 'spam', 'threat']);
    assert.equal(p.author?.prior_strikes, 1);
  }
});

test('consistency --live asks the cookbook rubric: instructions and label descriptions', () => {
  for (const { questions } of runLive('consistency')) {
    assert.equal(Object.keys(questions).length, 8);
    assert.equal(questions.category.instructions, 'What is the single most applicable content-policy category for this post?');
    assert.equal(questions.link_handling.criteria.RmLink, 'Strip or disable the link but keep the post.');
    assert.equal(questions.queue.criteria.TSLead, 'Trust-and-safety lead / senior queue.');
    for (const q of Object.values(questions)) {
      assert.doesNotMatch(q.instructions, /^Pick the single most applicable label/, 'no generic instruction');
      for (const d of Object.values(q.criteria)) assert.equal(typeof d, 'string', 'every label carries its description');
    }
    assert.equal(sha256(questions), COOKBOOK_QUESTIONS_SHA256.consistency, 'questions equal the cookbook rubric exactly');
  }
});

test('consistency-noul --live sends the cookbook claim as {uid, claim}', () => {
  for (const { state } of runLive('consistency-noul')) {
    assert.deepEqual(Object.keys(state).sort(), ['claim', 'uid'], 'state is {uid, claim}, not the claim spread or an id');
    const c = state.claim;
    assert.equal(c.claim?.claim_id, 'CLM-55029');
    assert.match(c.claim.description ?? '', /track-day event/, 'claim text is in the state');
    const sum = (c.claim.line_items ?? []).reduce((n, li) => n + li.cost, 0);
    assert.equal(sum, c.claim.amount_claimed, 'line items add up to 3250');
    assert.equal(c.policy?.coverages?.rental_reimbursement, false);
    assert.deepEqual(c.policy.exclusions, ['track/competitive driving', 'drivers not listed on the policy']);
    assert.match(c.adjuster_notes?.[0]?.note ?? '', /^Collision coverage active\. Approved\./);
  }
});

test('consistency-noul --live asks the cookbook questions', () => {
  for (const { questions } of runLive('consistency-noul')) {
    assert.equal(Object.keys(questions).length, 14);
    assert.equal(questions.subrogation.instructions, 'Is there a potentially at-fault third party the insurer could pursue for subrogation recovery?');
    assert.equal(sha256(questions), COOKBOOK_QUESTIONS_SHA256['consistency-noul'], 'questions equal the cookbook exactly');
  }
});

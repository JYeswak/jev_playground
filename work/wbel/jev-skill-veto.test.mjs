import test from 'node:test';
import assert from 'node:assert/strict';
import {
  isSkillReadPath,
  skillNameFromPath,
  fitsQuestion,
  decideVeto,
  vetoCheck,
  requestHash,
  SKILL_VETO_NOUL_CUT,
} from '../../kit/src/skill-veto.ts';
import { createSkillVetoHandler } from './jev-skill-veto.ts';

const noulAnswer = (noul) => async () => ({
  ok: true, scores: { fits: noul }, latencyMs: 180, model: 'jev-1.13.0',
  usage: { input_tokens: 400, output_tokens: 0 },
});
const brokenAsk = async () => { throw new Error('transport down'); };
const unconfiguredAsk = async () => ({ ok: false, reason: 'unconfigured', latencyMs: 0, model: 'jev-1.13.0' });

test('matcher fires on skill loads, silent on fixtures and prose paths', () => {
  assert.equal(isSkillReadPath('skill://plan-to-beads'), true);
  assert.equal(isSkillReadPath('skill://plan-to-beads/SKILL.md'), true);
  assert.equal(isSkillReadPath('skill://ns/name/refs/x.md'), true);
  assert.equal(isSkillReadPath('/Users/josh/.claude/skills/ripwire-navigate/SKILL.md'), true);
  assert.equal(isSkillReadPath('/tmp/sr-home/.claude/skills/alpha/SKILL.md'), false);
  assert.equal(isSkillReadPath('/var/folders/xx/T/x/SKILL.md'), false);
  assert.equal(isSkillReadPath('docs/guide-SKILL.md'), false);
  assert.equal(isSkillReadPath('skill://'), false);
  assert.equal(isSkillReadPath('skill://../escape'), false);
  assert.equal(isSkillReadPath(''), false);
  assert.equal(isSkillReadPath(null), false);
});

test('trailing filenames strip to the skill name', () => {
  assert.equal(skillNameFromPath('skill://plan-to-beads/SKILL.md'), 'plan-to-beads');
  assert.equal(skillNameFromPath('skill://ns/name/refs/guide.md'), 'ns/name');
  assert.equal(skillNameFromPath('skill://ns/name'), 'ns/name');
});

test('namespaced skill names stay whole', () => {
  assert.equal(skillNameFromPath('skill://plan-to-beads'), 'plan-to-beads');
  assert.equal(skillNameFromPath('skill://ns/name/SKILL.md'), 'ns/name');
  assert.equal(skillNameFromPath('/Users/josh/.claude/skills/ripwire-navigate/SKILL.md'), 'ripwire-navigate');
});

test('question wording is the preregistered demo wording', () => {
  assert.equal(
    fitsQuestion('ga4', 'GA4 setup'),
    "Does the skill 'ga4' do the specific thing the user's request asks for? It is described as: GA4 setup",
  );
});

test('cut 0.40: below vetoes, at-or-above allows (fail-safe direction: allow)', () => {
  assert.equal(decideVeto(0.39), true);
  assert.equal(decideVeto(0.40), false);
  assert.equal(decideVeto(0.41), false);
  assert.equal(decideVeto(NaN), false);
});

test('vetoCheck maps low noul to veto, high to allow, refusals to fail-open allow', async () => {
  const veto = await vetoCheck({ prompt: 'explain monads', skill: 'plan-to-beads', description: 'd', ask: noulAnswer(0.12) });
  assert.equal(veto.vetoed, true);
  assert.equal(veto.noul, 0.12);
  const allow = await vetoCheck({ prompt: 'plan this', skill: 'plan-to-beads', description: 'd', ask: noulAnswer(0.87) });
  assert.equal(allow.vetoed, false);
  for (const ask of [brokenAsk, unconfiguredAsk, async () => ({ ok: true, scores: {}, latencyMs: 1, model: 'm' })]) {
    const r = await vetoCheck({ prompt: 'p', skill: 's', description: 'd', ask });
    assert.equal(r.vetoed, false);
    assert.equal(r.noul, null);
  }
});

test('handler never blocks: undefined on skill and non-skill reads, even when the asker throws', async () => {
  const calls = [];
  const h = createSkillVetoHandler({
    ask: brokenAsk,
    describe: async () => 'desc',
    countToday: async () => 0,
    log: async (row, sidecar) => { calls.push([row, sidecar]); },
  });
  assert.equal(h.onContext({ messages: [{ role: 'user', content: [{ type: 'text', text: 'explain monads' }] }] }), undefined);
  assert.equal(await h.onToolCall({ toolName: 'read', input: { path: 'skill://plan-to-beads' } }), undefined);
  assert.equal(await h.onToolCall({ toolName: 'read', input: { path: '/etc/hosts' } }), undefined);
  assert.equal(await h.onToolCall({ toolName: 'bash', input: { command: 'ls' } }), undefined);
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0].wouldVeto, false);
  assert.equal(calls[0][0].decision, 'allow');
  assert.equal(calls[0][0].status, 'fail_open:throw:Error: transport down');
  assert.equal(calls[0][0].session, 'unknown');
});

test('session id flows from ctx sessionManager when present', async () => {
  const calls = [];
  const h = createSkillVetoHandler({
    ask: noulAnswer(0.9),
    describe: async () => 'desc',
    countToday: async () => 0,
    log: async (row, sidecar) => { calls.push([row, sidecar]); },
  });
  h.onContext({ messages: [{ role: 'user', content: [{ type: 'text', text: 'do beads' }] }] });
  const ctx = { sessionManager: { getSessionFile: () => '/Users/josh/.omp/agent/sessions/-Developer-jev/2026-10-02T06-37-40-585Z_01a0fb55-aa99-7185-a9ab-8d9efc2b3161.jsonl' } };
  assert.equal(await h.onToolCall({ toolName: 'read', input: { path: 'skill://plan-to-beads' } }, ctx), undefined);
  assert.equal(calls[0][0].session, '01a0fb55-aa99-7185-a9ab-8d9efc2b3161');
  assert.equal(calls[0][0].decision, 'allow');
});

test('cap reached means no Jev call but still a fail_open:cap row', async () => {
  const calls = [];
  let asked = 0;
  const h = createSkillVetoHandler({
    ask: async (o) => { asked += 1; return noulAnswer(0.01)(o); },
    describe: async () => 'desc',
    countToday: async () => 100,
    log: async (row, sidecar) => { calls.push([row, sidecar]); },
  });
  assert.equal(await h.onToolCall({ toolName: 'read', input: { path: 'skill://x' } }), undefined);
  assert.equal(asked, 0);
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0].status, 'fail_open:cap');
  assert.equal(calls[0][0].noul, null);
  assert.equal(calls[0][0].decision, 'allow');
  assert.equal(calls[0][0].reason, 'cap-reached');
});

test('rows carry status: scored on a number, fail_open:<reason> otherwise', async () => {
  const scored = [];
  const hScored = createSkillVetoHandler({
    ask: noulAnswer(0.9),
    describe: async () => 'desc',
    countToday: async () => 0,
    log: async (row, sidecar) => { scored.push([row, sidecar]); },
  });
  await hScored.onToolCall({ toolName: 'read', input: { path: 'skill://x' } });
  assert.equal(scored[0][0].status, 'scored');
  assert.equal(scored[0][0].noul, 0.9);

  const open = [];
  const hOpen = createSkillVetoHandler({
    ask: unconfiguredAsk,
    describe: async () => 'desc',
    countToday: async () => 0,
    log: async (row, sidecar) => { open.push([row, sidecar]); },
  });
  await hOpen.onToolCall({ toolName: 'read', input: { path: 'skill://x' } });
  assert.equal(open[0][0].status, 'fail_open:ask-unconfigured');
  assert.equal(open[0][0].noul, null);
  assert.equal(open[0][0].decision, 'allow');
});

test('log row carries hashes, never prompt text; sidecar carries the text keyed by hash', async () => {
  const calls = [];
  const h = createSkillVetoHandler({
    ask: noulAnswer(0.05),
    describe: async () => 'desc',
    countToday: async () => 0,
    log: async (row, sidecar) => { calls.push([row, sidecar]); },
  });
  h.onContext({ messages: [{ role: 'user', content: [{ type: 'text', text: 'secret prompt alpha' }] }] });
  await h.onToolCall({ toolName: 'read', input: { path: 'skill://cooking' } });
  assert.equal(calls.length, 1);
  const [row, sidecar] = calls[0];
  assert.equal(JSON.stringify(row).includes('secret prompt alpha'), false);
  assert.equal(row.reqHash, requestHash('secret prompt alpha'));
  assert.equal(row.wouldVeto, true);
  assert.equal(sidecar.prompt, 'secret prompt alpha');
  assert.equal(sidecar.reqHash, row.reqHash);
  assert.equal(row.model, 'jev-1.13.0');
  assert.equal(SKILL_VETO_NOUL_CUT, 0.40);
});

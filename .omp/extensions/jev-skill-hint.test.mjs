import test from 'node:test';
import assert from 'node:assert/strict';
import {
  hintSkills,
  shortlistSkills,
  loadSkillRoster,
  warmTransport,
  SKILL_HINT_MODEL,
  SKILL_HINT_CONFIDENCE_CUT,
  SKILL_HINT_SHORTLIST_MAX,
  SKILL_HINT_TIMEOUT_MS,
} from '../../kit/src/skill-hint.ts';
import { createSkillHintHandler } from './jev-skill-hint.ts';

// Tiny roster: shortlist logic without touching the real 764-skill inventory.
const ROSTER = [
  { name: 'ga4', description: 'GA4 conversion funnel scroll CTA setup' },
  { name: 'analytics-tracking', description: 'conversion funnel setup and validation' },
  { name: 'cooking', description: 'recipes and meal planning' },
];

const GA4_PROMPT = 'Help me set up a GA4 conversion funnel for the signup page scroll CTA';
const CLOCK_PROMPT = 'what time is it';

const answer = (choice, confidence) => async () => ({
  ok: true, choice, confidence, probabilities: { [choice]: confidence },
  latencyMs: 210, model: SKILL_HINT_MODEL,
});

test('shortlist ranks skill names over description noise and caps at twenty', () => {
  const top = shortlistSkills(GA4_PROMPT, ROSTER);
  assert.deepEqual(top.map((s) => s.name), ['ga4', 'analytics-tracking']);
  assert.ok(top.length <= SKILL_HINT_SHORTLIST_MAX);
  const clock = shortlistSkills(CLOCK_PROMPT, ROSTER);
  assert.ok(!clock.some((s) => s.name === 'ga4' || s.name === 'analytics-tracking'));
});

test('real roster holds both acceptance skills with usable descriptions', () => {
  const roster = loadSkillRoster();
  assert.ok(roster.length >= 700, 'expected the ~760-skill inventory, got ' + roster.length);
  const names = new Set(roster.map((s) => s.name));
  assert.ok(names.has('ga4') && names.has('analytics-tracking'));
  const ga4 = roster.find((s) => s.name === 'ga4');
  assert.ok(ga4.description.length > 20, 'folded description must parse, got: ' + JSON.stringify(ga4.description.slice(0, 40)));
  const top = shortlistSkills(GA4_PROMPT, roster).map((s) => s.name);
  assert.ok(top.includes('ga4') || top.includes('analytics-tracking'), 'shortlist missed both: ' + top.slice(0, 5).join(','));
  const clock = shortlistSkills(CLOCK_PROMPT, roster).map((s) => s.name);
  assert.ok(!clock.includes('ga4') && !clock.includes('analytics-tracking'));
});

test('confident non-none choice becomes the hint text', async () => {
  const result = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask: answer('ga4', 0.8) });
  assert.equal(result.hint.startsWith('Likely relevant skills: ga4'), true);
  assert.equal(result.skill, 'ga4');
  assert.equal(result.model, SKILL_HINT_MODEL);
});

test('billed usage flows to the hint result for spend accounting', async () => {
  const usage = { input_tokens: 412, output_tokens: 18, billing_units: null, extra: {} };
  const ask = async () => ({ ok: true, choice: 'ga4', confidence: 0.81, probabilities: { ga4: 0.81 }, latencyMs: 190, model: SKILL_HINT_MODEL, usage });
  const result = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask });
  assert.deepEqual(result.usage, { input_tokens: 412, output_tokens: 18 });
});

test('none, low confidence, refusal, and empty prompt all stay silent', async () => {
  const silent = async (ask, prompt = GA4_PROMPT) => hintSkills({ prompt, roster: ROSTER, ask });
  assert.equal((await silent(answer('none', 0.99))).hint, null);
  const low = await silent(answer('ga4', SKILL_HINT_CONFIDENCE_CUT - 0.01));
  assert.equal(low.hint, null);
  assert.equal(low.reason, 'low-confidence');
  const refused = await silent(async () => ({ ok: false, reason: 'http', error: 'HTTP 403', latencyMs: 5, model: SKILL_HINT_MODEL }));
  assert.equal(refused.hint, null);
  const thrown = await silent(async () => { throw new Error('transport down'); });
  assert.equal(thrown.hint, null);
  const empty = await silent(answer('ga4', 0.9), '   ');
  assert.equal(empty.hint, null);
  assert.equal(empty.reason, 'empty-prompt');
});

test('extension handler injects the message on hint and yields nothing when silent', async () => {
  const { default: factory } = await import('./jev-skill-hint.ts');
  assert.equal(typeof factory, 'function');
  const seen = [];
  factory({ on: (event, handler) => seen.push([event, handler]) });
  assert.deepEqual(seen.map(([event]) => event).sort(), ['before_agent_start', 'session_start']);
  const fired = createSkillHintHandler(ROSTER, answer('analytics-tracking', 0.72));
  const out = await fired({ prompt: GA4_PROMPT });
  assert.equal(out.message.customType, 'jev-skill-hint');
  assert.match(out.message.content, /analytics-tracking/);
  assert.equal(out.message.attribution, 'jev-skill-hint');
  const quiet = createSkillHintHandler(ROSTER, answer('none', 0.99));
  assert.equal(await quiet({ prompt: GA4_PROMPT }), undefined);
});
test('slow failures past the deadline log as timeout, fast ones keep their reason', async () => {
  assert.equal(SKILL_HINT_TIMEOUT_MS, 300);
  const slow = async () => { await new Promise((r) => setTimeout(r, SKILL_HINT_TIMEOUT_MS + 100)); throw new Error('socket hang up'); };
  const slowResult = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask: slow, timeoutMs: SKILL_HINT_TIMEOUT_MS });
  assert.equal(slowResult.hint, null);
  assert.equal(slowResult.reason, 'timeout');
  const fast = async () => { throw new Error('connection refused'); };
  const fastResult = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask: fast, timeoutMs: 5000 });
  assert.equal(fastResult.reason, 'connection refused');
});

test('warmup probes the transport once without blocking the turn', async () => {
  let calls = 0;
  const ask = async () => { calls += 1; return { ok: true, choice: 'warm', confidence: 1, probabilities: { warm: 1 }, latencyMs: 120, model: SKILL_HINT_MODEL }; };
  const warmed = await warmTransport(ask);
  assert.equal(warmed.ok, true);
  assert.equal(calls, 1);
  const failed = await warmTransport(async () => { throw new Error('down'); });
  assert.equal(failed.ok, false);
});

test('extension warms on session_start without awaiting and hints on prompt', async () => {
  const { default: factory } = await import('./jev-skill-hint.ts');
  const seen = new Map();
  factory({ on: (event, handler) => seen.set(event, handler) });
  assert.deepEqual([...seen.keys()].sort(), ['before_agent_start', 'session_start']);
  const warmHandler = seen.get('session_start');
  assert.equal(warmHandler({}), undefined);
});

test('resolved deadline hits log as timeout, not transport', async () => {
  const slowAnswer = async () => { await new Promise((r) => setTimeout(r, SKILL_HINT_TIMEOUT_MS)); return { ok: false, reason: 'transport', error: 'timed out', latencyMs: 0, model: SKILL_HINT_MODEL }; };
  const timed = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask: slowAnswer, timeoutMs: SKILL_HINT_TIMEOUT_MS });
  assert.equal(timed.hint, null);
  assert.equal(timed.reason, 'timeout');
  const fastAnswer = async () => ({ ok: false, reason: 'transport', error: 'refused', latencyMs: 40, model: SKILL_HINT_MODEL });
  const fast = await hintSkills({ prompt: GA4_PROMPT, roster: ROSTER, ask: fastAnswer, timeoutMs: SKILL_HINT_TIMEOUT_MS });
  assert.equal(fast.reason, 'transport');
});

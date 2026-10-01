import test from 'node:test';
import assert from 'node:assert/strict';
import {
  hintSkills,
  shortlistSkills,
  loadSkillRoster,
  SKILL_HINT_MODEL,
  SKILL_HINT_CONFIDENCE_CUT,
  SKILL_HINT_SHORTLIST_MAX,
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
  assert.equal(seen.length, 1);
  assert.equal(seen[0][0], 'before_agent_start');
  const fired = createSkillHintHandler(ROSTER, answer('analytics-tracking', 0.72));
  const out = await fired({ prompt: GA4_PROMPT });
  assert.equal(out.message.customType, 'jev-skill-hint');
  assert.match(out.message.content, /analytics-tracking/);
  assert.equal(out.message.attribution, 'jev-skill-hint');
  const quiet = createSkillHintHandler(ROSTER, answer('none', 0.99));
  assert.equal(await quiet({ prompt: GA4_PROMPT }), undefined);
});

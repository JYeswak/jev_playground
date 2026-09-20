import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevRoute, { QUESTIONS, suggestTier } from '../src/index.ts';

function host() {
  const rows = [];
  let handler;
  let event;
  return {
    rows,
    fire: (e) => handler(e),
    pi: {
      on: (ev, cb) => { event = ev; handler = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
    eventName: () => event,
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith('decision.v1'));

// PLANTED NEGATIVE 1: no key -> route_error, never a scored pass.
test('an unset API key records route_error, never scored advice', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevRoute(h.pi);
    assert.equal(h.eventName(), 'context');
    await h.fire({ type: 'context', messages: [{ role: 'user', content: 'Refactor the auth boundary.' }] });
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'route_error');
    assert.equal('probabilities' in row.data, false);
    assert.equal('suggested_tier' in row.data, false);
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

// PLANTED NEGATIVE 2: nothing to judge -> silence, not a score.
// Includes the measured live turn_start shape {type, turnIndex, timestamp}:
// content-free, so it must stay silent.
test('a turn with no prompt text emits no decision row', async () => {
  const h = host();
  ompJevRoute(h.pi);
  for (const event of [{}, null, { prompt: '   ' }, { turn: {} },
    { type: 'turn_start', turnIndex: 0, timestamp: 123 },
    { type: 'context', messages: [{ role: 'assistant', content: 'hi' }] },
    { type: 'context', messages: [{ role: 'user', content: '   ' }] }]) {
    assert.equal(await h.fire(event), undefined);
  }
  assert.equal(decisions(h).length, 0);
});

// Tier mapping is declared logic: unit-test the declaration itself.
test('suggestTier prefers heavyweight, then light, else default', () => {
  assert.equal(suggestTier({ needs_heavyweight: 0.9, mechanical: 0.9 }), 'heavy');
  assert.equal(suggestTier({ needs_heavyweight: 0.1, mechanical: 0.9 }), 'light');
  assert.equal(suggestTier({ needs_heavyweight: 0.1, mechanical: 0.1 }), 'default');
  assert.equal(suggestTier({}), 'default');
});

// QUESTIONS frozen: the scored contract is exactly these two keys.
test('frozen question set is needs_heavyweight + mechanical', () => {
  assert.deepEqual(Object.keys(QUESTIONS).sort(), ['mechanical', 'needs_heavyweight']);
});

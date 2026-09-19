import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { scoreDecisions, randomBaseline } from '../hindsight.js';
import type { CallDecision, Message } from 'fast-jev-compaction';

const msgs = (): Message[] => [
  { role: 'user', text: 'find the parser bug', toolUses: [], toolResults: [] },
  {
    role: 'assistant', text: 'reading',
    toolUses: [
      { tool_use_id: 'a', tool: 'read', input: {} },
      { tool_use_id: 'b', tool: 'read', input: {} },
    ],
    toolResults: [
      // NOVEL token that the assistant later quotes -> dropping this is a mistake.
      { tool_use_id: 'a', text: 'token ZQ7vnq4LmXbRt9wKd2 here', isError: false },
      // Novel token never mentioned again -> dropping this is correct.
      { tool_use_id: 'b', text: 'token PL3xxAvv8ee1ooWq55 here', isError: false },
    ],
  },
  { role: 'assistant', text: 'using ZQ7vnq4LmXbRt9wKd2 to fix it', toolUses: [], toolResults: [] },
];

const dec = (actions: Array<CallDecision['action']>): CallDecision[] =>
  actions.map((action, i) => ({
    id: `t${i + 1}`, tool: 'read', action,
    reason: action === 'keep' ? 'kept' : 'result_dropped', keepCall: 0, keepResult: 0,
  })) as CallDecision[];

describe('hindsight oracle', () => {
  it('counts a drop as a mistake only when the result is LATER reused', () => {
    const h = scoreDecisions(msgs(), dec(['drop_result', 'drop_result']));
    assert.equal(h.callsScored, 2);
    assert.equal(h.dropped, 2);
    assert.equal(h.droppedButReused, 1, 'only the quoted result counts against the judge');
  });

  it('PLANTED NEGATIVE: keeping everything scores zero mistakes but is not free', () => {
    const h = scoreDecisions(msgs(), dec(['keep', 'keep']));
    assert.equal(h.droppedButReused, 0, 'a compactor that drops nothing never errs');
    assert.equal(h.keptAndNeverReused, 1, '...and the missed saving must still be visible');
  });

  it('a token already present earlier is NOT a fingerprint', () => {
    const m = msgs();
    // Put the token in the FIRST message: it is no longer novel to the result, so a later
    // mention cannot be attributed to that result and must not count as reuse.
    m[0] = { ...m[0], text: 'find ZQ7vnq4LmXbRt9wKd2' };
    const h = scoreDecisions(m, dec(['drop_result', 'drop_result']));
    assert.equal(h.droppedButReused, 0, 'ubiquitous strings must not manufacture mistakes');
  });

  it('the random baseline drops the SAME COUNT, preserving alignment', () => {
    const d = dec(['drop_result', 'keep']);
    const r = randomBaseline(msgs(), d);
    assert.equal(r.dropped, 1, 'baseline must match the judge it is compared against');
    assert.equal(r.callsScored, 2, 'alignment must survive the permutation');
  });
});

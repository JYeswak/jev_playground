import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { adaptOmpTranscript, type OmpEvent } from '../src/omp-adapter.js';

const end = (message: OmpEvent['message']): OmpEvent => ({ type: 'message_end', message });

describe('adaptOmpTranscript', () => {
  it('maps user text, assistant text+calls, thinking dropped and counted', () => {
    const { messages, stats } = adaptOmpTranscript([
      end({ role: 'user', content: [{ type: 'text', text: 'list files' }] }),
      end({
        role: 'assistant',
        content: [
          { type: 'thinking', thinking: 'plan...' },
          { type: 'text', text: 'On it.' },
          { type: 'toolCall', id: 'c1', name: 'read', arguments: { path: '/x' } },
        ],
      }),
      end({ role: 'toolResult', toolCallId: 'c1', content: [{ type: 'text', text: 'a b' }] }),
      end({ role: 'user', content: [{ type: 'text', text: 'thanks' }] }),
    ]);
    assert.equal(messages.length, 3);
    assert.equal(messages[0].text, 'list files');
    assert.deepEqual(messages[0].toolResults ?? [], []);
    assert.equal(messages[1].text, 'On it.');
    assert.deepEqual(messages[1].toolUses, [{ tool_use_id: 'c1', tool: 'read', input: { path: '/x' } }]);
    assert.equal(messages[2].text, 'thanks');
    assert.deepEqual(messages[2].toolResults, [{ tool_use_id: 'c1', text: 'a b', isError: false }]);
    assert.equal(stats.resultsPaired, 1);
    assert.equal(stats.resultsTrailing, 0);
  });
  it('attaches each result to the message following its call (real stream order)', () => {
    const { messages, stats } = adaptOmpTranscript([
      end({ role: 'user', content: [{ type: 'text', text: 'go' }] }),
      end({
        role: 'assistant',
        content: [{ type: 'toolCall', id: 'c1', name: 'read', arguments: { path: '/x' } }],
      }),
      end({ role: 'toolResult', toolCallId: 'c1', content: [{ type: 'text', text: 'a b' }] }),
      end({ role: 'assistant', content: [{ type: 'text', text: 'done' }] }),
    ]);
    assert.equal(messages.length, 3);
    assert.deepEqual(messages[2].toolResults, [{ tool_use_id: 'c1', text: 'a b', isError: false }]);
    assert.deepEqual(messages[1].toolResults ?? [], []);
    assert.equal(stats.resultsTrailing, 0);
  });
  it('ignores streaming updates and non-message events', () => {
    const { messages, stats } = adaptOmpTranscript([
      { type: 'message_update', message: { role: 'user', content: [{ type: 'text', text: 'partial' }] } },
      { type: 'turn_start' },
      end({ role: 'user', content: [{ type: 'text', text: 'final' }] }),
    ]);
    assert.equal(messages.length, 1);
    assert.equal(messages[0].text, 'final');
    assert.equal(stats.messagesIn, 1);
  });

  it('parks trailing results on an empty user message instead of dropping', () => {
    const { messages, stats } = adaptOmpTranscript([
      end({ role: 'user', content: [{ type: 'text', text: 'go' }] }),
      end({
        role: 'assistant',
        content: [{ type: 'toolCall', id: 'c9', name: 'bash', arguments: { cmd: 'ls' } }],
      }),
      end({ role: 'toolResult', toolCallId: 'c9', content: [{ type: 'text', text: 'out' }] }),
    ]);
    assert.equal(messages.length, 3);
    assert.equal(messages[2].role, 'user');
    assert.equal(messages[2].text, '');
    assert.deepEqual(messages[2].toolResults, [{ tool_use_id: 'c9', text: 'out', isError: false }]);
    assert.equal(stats.resultsTrailing, 1);
  });

  it('KNOWN-BAD: dropping the trailer loses evidence (asserts current behavior is keep)', () => {
    // If the trailing-empty-user rule is ever removed, this turns RED: the
    // result must still be present somewhere in the output.
    const { messages } = adaptOmpTranscript([
      end({ role: 'user', content: [{ type: 'text', text: 'go' }] }),
      end({ role: 'toolResult', toolCallId: 'cz', content: [{ type: 'text', text: 'EVIDENCE' }] }),
    ]);
    const all = JSON.stringify(messages);
    assert.match(all, /EVIDENCE/);
  });
});

// THE ON-DISK ENVELOPE. omp writes session history as SessionEntry records (`type: "message"`,
// session-entries.d.ts:55) while `--mode json` streams `message_end` (print-mode.d.ts:24-36).
// Both are live and both wrap the same AgentMessage. Before this was accepted, a real 9.5 MB
// session adapted to ZERO messages and the replay harness failed closed (R23).
describe('on-disk SessionEntry envelope', () => {
  it('adapts `type: "message"` identically to `type: "message_end"`', () => {
    const payload = [
      { role: 'user', content: [{ type: 'text', text: 'find the bug' }] },
      {
        role: 'assistant',
        content: [
          { type: 'thinking', thinking: 'dropped' },
          { type: 'text', text: 'reading' },
          { type: 'toolCall', id: 'c1', name: 'Read', arguments: { path: 'a.ts' } },
        ],
      },
      { role: 'toolResult', toolCallId: 'c1', content: [{ type: 'text', text: 'file body' }] },
    ];
    const asStream = payload.map((message) => ({ type: 'message_end', message })) as OmpEvent[];
    const asDisk = payload.map((message) => ({ type: 'message', message })) as OmpEvent[];

    const stream = adaptOmpTranscript(asStream);
    const disk = adaptOmpTranscript(asDisk);

    assert.deepEqual(disk.messages, stream.messages, 'both envelopes must yield the same messages');
    assert.equal(disk.stats.messagesIn, 3);
    assert.equal(disk.stats.resultsPaired, stream.stats.resultsPaired);
    assert.equal(disk.stats.thinkingCharsDropped, stream.stats.thinkingCharsDropped);
  });

  it('PLANTED NEGATIVE: an unknown envelope type still yields nothing', () => {
    const out = adaptOmpTranscript([
      { type: 'custom', message: { role: 'user', content: [{ type: 'text', text: 'x' }] } },
    ] as OmpEvent[]);
    assert.equal(out.messages.length, 0, 'only the two known envelopes are accepted');
    assert.equal(out.stats.messagesIn, 0);
  });
});

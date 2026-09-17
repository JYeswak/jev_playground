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

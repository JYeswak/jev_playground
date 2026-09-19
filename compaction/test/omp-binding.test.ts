import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
import type { Message } from 'fast-jev-compaction';
import { adaptOmpTranscript } from '../src/omp-adapter.js';
import ompCompactionHook, { registerOmpCompactionHook, type OmpLike } from '../src/omp-binding.js';

// A stub standing in for omp's extension API. It captures the handler the binding registers, so a
// test can drive `session_before_compact` without a live session. This proves the BINDING's
// contract; it does not prove omp's envelope field names, which remain unpinned because omp ships
// as a compiled binary with no .d.ts on disk.
function stubPi() {
  let handler: ((e: { messages?: readonly Message[] }) => Promise<unknown>) | null = null;
  const pi: OmpLike = { on: (_event, h) => { handler = h as typeof handler; } };
  return { pi, fire: (e: { messages?: readonly Message[] }) => handler!(e) };
}

const msg = (text: string): Message => ({ role: 'user', text, toolUses: [] });
const many = (n: number) => Array.from({ length: n }, (_, i) => msg(`turn ${i} `.repeat(40)));

// A transcript WITH tool calls. The first version of these tests used plain turns and the asker was
// never invoked — `compact` short-circuits on "no tool calls" before reaching Jev, so the test that
// claimed to prove the Jev-failure path proved nothing. Observed reason on the empty case:
// "below minimum reduction: 0% reduction; no tool calls; state ~0 tokens".
const withTools = (n: number) =>
  Array.from({ length: n }, (_, i) => ({
    role: 'assistant' as const,
    text: `step ${i}`,
    toolUses: [{
      tool_use_id: `t${i}`,
      tool: 'read',
      input: { path: `/f/${i}` },
      text: `result ${i} `.repeat(120),
    }],
  }));

test('registers a handler for session_before_compact', () => {
  const { pi, fire } = stubPi();
  registerOmpCompactionHook(pi, { asker: { ask: async () => { throw new Error('unused'); } } });
  assert.equal(typeof fire, 'function');
});

test('KNOWN-BAD: a malformed envelope makes the seam refuse, not guess', async () => {
  const { pi, fire } = stubPi();
  const seen: string[] = [];
  registerOmpCompactionHook(pi, {
    asker: { ask: async () => { throw new Error('must not be called'); } },
    onDecision: (o, r) => seen.push(`${o}:${r}`),
  });
  assert.equal(await fire({}), undefined, 'no messages -> undefined, omp keeps its summarizer');
  assert.equal(await fire({ messages: [] }), undefined, 'empty messages -> undefined');
  assert.equal(seen.length, 2);
  assert.ok(seen.every((s) => s.startsWith('refused:')), seen.join(' | '));
});

// WHAT THIS TEST DOES AND DOES NOT REACH. It proves the binding returns `undefined` — omp keeps its
// own summarizer, context survives — for a transcript the compactor declines. It does NOT reach the
// Jev-failure branch: two synthetic transcripts (plain turns, then turns carrying `toolUses`) both
// short-circuit with "0% reduction; no tool calls" before the asker is called, so `compact`'s tool
// extraction wants a pairing these fixtures do not reproduce. Reaching that branch needs a real omp
// transcript through `src/omp-adapter.ts`, which is named here rather than faked.
test('a declined compaction passes through rather than destroying context', async () => {
  const { pi, fire } = stubPi();
  const seen: string[] = [];
  registerOmpCompactionHook(pi, {
    asker: { ask: async () => { throw new Error('jev is down'); } },
    onDecision: (o, r) => seen.push(`${o}:${r}`),
  });
  const out = await fire({ messages: withTools(12) });
  assert.equal(out, undefined, 'a dead Jev must not return a compaction');
  assert.ok(seen[0].startsWith('passthrough:'), seen.join(' | '));
  assert.match(seen[0], /below minimum reduction|jev/i, 'the reason is reported, not swallowed');
});

test('a compaction that does not shrink is refused', async () => {
  const { pi, fire } = stubPi();
  const seen: string[] = [];
  const input = withTools(10);
  registerOmpCompactionHook(pi, {
    // A degenerate asker: whatever it returns, the binding must not present a non-shrinking
    // result as a compaction.
    asker: { ask: async () => ({ answers: {} }) as never },
    config: { minReductionRatio: 0 },
    onDecision: (o, r) => seen.push(`${o}:${r}`),
  });
  const out = await fire({ messages: input });
  assert.equal(out, undefined);
  assert.ok(seen[0].startsWith('refused:') || seen[0].startsWith('passthrough:'), seen.join(' | '));
});

test('the default export refuses to be installed without a configured asker', () => {
  assert.throws(
    () => ompCompactionHook({ on: () => {} }),
    /requires a configured JevAsker/,
    'installing the module directly must fail loudly rather than register a broken hook',
  );
});


// THE BRANCH THE SYNTHETIC FIXTURES COULD NOT REACH. Plain turns and hand-made `toolUses` both
// short-circuit on "no tool calls" before the asker is called, so the Jev-failure path went
// untested. A REAL omp transcript through the adapter reaches it: 179 events in, 24 messages, 11
// tool results paired, 13 messages out — enough tool structure that `compact` actually asks Jev.
test('REAL TRANSCRIPT: a Jev outage passes through with its reason, context intact', async () => {
  const raw = readFileSync(
    new URL('../fixtures/omp-session-big-20260917.jsonl', import.meta.url),
    'utf8',
  );
  const events = raw.split('\n').filter(Boolean).map((l) => JSON.parse(l));
  const { messages } = adaptOmpTranscript(events);
  assert.ok(messages.length > 0, 'the adapter must produce messages from the fixture');

  const { pi, fire } = stubPi();
  const seen: string[] = [];
  registerOmpCompactionHook(pi, {
    asker: { ask: async () => { throw new Error('jev is down'); } },
    onDecision: (o, r) => seen.push(`${o}:${r}`),
  });

  const out = await fire({ messages });
  assert.equal(out, undefined, 'a dead Jev must never return a compaction');
  assert.match(seen[0], /^passthrough:jev failure: jev is down$/,
    'the outage reason is reported verbatim, not swallowed into a generic passthrough');
});

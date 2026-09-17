import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  compactOmpTranscript,
  compactOmpTranscriptSafe,
  decisionLogLines,
  registerOmpHook,
  resolveOmpHookConfig,
  summarize,
  type OmpHookApi,
  type OmpHookConfig,
} from '../src/omp-hook.js';
import type { JevAnswer, JevAsker, Message } from 'fast-jev-compaction';

/** Deterministic stand-in for Jev: fixed keep probability per question name. */
function cannedAsker(probs: Record<string, number> = {}): JevAsker {
  return {
    async ask(_state, questions) {
      const answers: Record<string, JevAnswer> = {};
      for (const name of Object.keys(questions)) {
        answers[name] = { noul: probs[name] ?? 1 };
      }
      return { answers };
    },
  };
}

const failingAsker: JevAsker = {
  async ask() {
    throw new Error('429 rate limited');
  },
};

/** Two tool calls with results; middle messages are Jev candidates. */
function twoCallTranscript(): Message[] {
  return [
    { role: 'user', text: 'go', toolUses: [], toolResults: [] },
    {
      role: 'assistant',
      text: 'reading',
      toolUses: [{ tool_use_id: 'c1', tool: 'read', input: { path: '/x' } }],
      toolResults: [],
    },
    {
      role: 'user',
      text: '',
      toolUses: [],
      toolResults: [{ tool_use_id: 'c1', text: 'KEEP-ME-VERBATIM', isError: false }],
    },
    {
      role: 'assistant',
      text: 'listing',
      toolUses: [{ tool_use_id: 'c2', tool: 'bash', input: { cmd: 'ls' } }],
      toolResults: [],
    },
    {
      role: 'user',
      text: 'thanks',
      toolUses: [],
      toolResults: [{ tool_use_id: 'c2', text: `DROP-ME-${'x'.repeat(2000)}`, isError: false }],
    },
  ];
}

// preserveRecentMessages: 0, so only the first message is pinned: both calls
// are Jev candidates. (Pinning follows the result's message too —
// fast-jev-compaction/src/state.ts:86-88 — so any preserved newest window
// would pin c2 through its result on the last message.)
const config: OmpHookConfig = {
  ...resolveOmpHookConfig(),
  preserveRecentMessages: 0,
};

describe('compactOmpTranscript', () => {
  it('prunes a low-value result, keeps the rest byte-identical', async () => {
    // t1 = first candidate (c1), t2 = second (c2): keep c1 fully, drop c2's result.
    const { messages, result } = await compactOmpTranscript(
      twoCallTranscript(),
      cannedAsker({ call_t1: 0.9, result_t1: 0.9, call_t2: 0.9, result_t2: 0.1 }),
      config,
    );
    const all = JSON.stringify(messages);
    assert.match(all, /KEEP-ME-VERBATIM/);
    // drop_result keeps a bounded head plus a note — the head prefix stays,
    // the bulk goes. Assert the shrink and the marker, not absence.
    const dropped = messages
      .flatMap((m) => m.toolResults ?? [])
      .find((r) => r.tool_use_id === 'c2');
    assert.ok(dropped);
    assert.ok(dropped.text.length < 2007);
    assert.match(dropped.text, /truncated/);
    const actions = Object.fromEntries(result.decisions.map((d) => [d.tool, d.action]));
    assert.equal(actions['read'], 'keep');
    assert.equal(actions['bash'], 'drop_result');
  });

  it('throws on Jev failure — the caller owns the fallback, not the core', async () => {
    await assert.rejects(
      compactOmpTranscript(twoCallTranscript(), failingAsker, config),
      /429 rate limited/,
    );
  });
});

describe('compactOmpTranscriptSafe (never destroy context on error)', () => {
  it('passthrough on transport failure returns the input unchanged', async () => {
    const input = twoCallTranscript();
    const settled = await compactOmpTranscriptSafe(input, failingAsker, config);
    assert.equal(settled.outcome, 'passthrough');
    assert.deepEqual(settled.messages, input);
    assert.match(settled.reason, /jev failure/);
  });

  it('passthrough on malformed Jev answers (missing keys are refused, not coerced)', async () => {
    const malformed: JevAsker = { async ask() { return { answers: {} }; } };
    const input = twoCallTranscript();
    const settled = await compactOmpTranscriptSafe(input, malformed, config);
    assert.equal(settled.outcome, 'passthrough');
    assert.deepEqual(settled.messages, input);
  });

  it('passthrough below the minimum reduction (yields to the built-in summarizer)', async () => {
    const strict: OmpHookConfig = { ...config, minReductionRatio: 0.99 };
    const settled = await compactOmpTranscriptSafe(
      twoCallTranscript(),
      cannedAsker({ call_t1: 0.9, result_t1: 0.9, call_t2: 0.9, result_t2: 0.1 }),
      strict,
    );
    assert.equal(settled.outcome, 'passthrough');
    assert.match(settled.reason, /below minimum/);
  });

  it('KNOWN-BAD guard: passthrough output keeps every evidence byte', async () => {
    const input = twoCallTranscript();
    const settled = await compactOmpTranscriptSafe(input, failingAsker, config);
    assert.equal(JSON.stringify(settled.messages), JSON.stringify(input));
  });
});

describe('resolveOmpHookConfig', () => {
  it('defaults the reduction floor and accepts numeric overrides', () => {
    assert.equal(resolveOmpHookConfig().minReductionRatio, 0.25);
    assert.equal(
      resolveOmpHookConfig({ minReductionRatio: 0.5, keepThreshold: 0.7 }).keepThreshold,
      0.7,
    );
  });

  it('ignores non-numeric values instead of coercing them', () => {
    const cfg = resolveOmpHookConfig({ keepThreshold: 'high', minReductionRatio: NaN });
    assert.equal(cfg.minReductionRatio, 0.25);
    assert.equal(cfg.keepThreshold, undefined);
  });
});

describe('registerOmpHook', () => {
  function fakePi() {
    const handlers: Record<string, (input: never) => Promise<unknown>> = {};
    const logs: string[] = [];
    const pi: OmpHookApi = {
      on: (event, handler) => {
        handlers[event] = handler as (input: never) => Promise<unknown>;
      },
      log: (text: string) => {
        logs.push(text);
      },
    };
    return { pi, handlers, logs };
  }

  it("registers on omp's pre-compact point", () => {
    const { pi, handlers } = fakePi();
    registerOmpHook(pi, { asker: cannedAsker() });
    assert.ok(handlers['session_before_compact']);
  });

  it('returns undefined (omp default) when Jev fails', async () => {
    const { pi, handlers, logs } = fakePi();
    registerOmpHook(pi, { asker: failingAsker });
    const out = await handlers['session_before_compact']({
      messages: twoCallTranscript(),
    } as never);
    assert.equal(out, undefined);
    assert.match(logs.join('\n'), /passthrough/);
  });

  it('returns the judged compaction envelope on success', async () => {
    const { pi, handlers, logs } = fakePi();
    registerOmpHook(pi, {
      asker: cannedAsker({ call_t1: 0.9, result_t1: 0.9, call_t2: 0.9, result_t2: 0.1 }),
      config,
    });
    const out = (await handlers['session_before_compact']({
      messages: twoCallTranscript(),
    } as never)) as { compaction: { messages: Message[]; preserveData: { ompJev: string } } };
    assert.ok(out.compaction);
    const dropped = out.compaction.messages
      .flatMap((m) => m.toolResults ?? [])
      .find((r) => r.tool_use_id === 'c2');
    assert.ok(dropped && dropped.text.length < 2007);
    assert.match(out.compaction.preserveData.ompJev, /reduction/);
    assert.match(logs.join('\n'), /decisions:/);
  });
});

describe('summarize', () => {
  it('names the reduction and the fail-safe direction', async () => {
    const { result } = await compactOmpTranscript(
      twoCallTranscript(),
      cannedAsker({ call_t1: 0.9, result_t1: 0.9, call_t2: 0.9, result_t2: 0.1 }),
      config,
    );
    assert.match(summarize(result), /reduction/);
    assert.equal(decisionLogLines(result).length >= 1, true);
  });
});

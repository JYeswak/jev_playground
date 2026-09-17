import type { Message } from 'fast-jev-compaction';

/** One omp `--mode json` stream event row (only the fields the adapter reads). */
export interface OmpEvent {
  type: string;
  message?: {
    role: string;
    toolCallId?: string;
    toolName?: string;
    isError?: boolean;
    content?: Array<{
      type: string;
      text?: string;
      thinking?: string;
      id?: string;
      name?: string;
      arguments?: Record<string, unknown>;
    }>;
  };
}

export interface AdapterStats {
  eventsIn: number;
  messagesIn: number;
  thinkingCharsDropped: number;
  resultsPaired: number;
  resultsTrailing: number;
}
/**
 * omp JSONL transcript -> fast-jev-compaction Message[].
 *
 * Rules (all deterministic, order-preserving):
 * - Only `message_end` rows are read; `message_update` streaming partials are ignored.
 * - Assistant `thinking` blocks are dropped and counted: the library has no thinking
 *   channel, so carrying them as text would corrupt its verbatim-text contract.
 * - `toolCall{id,name,arguments}` -> toolUses[{tool_use_id:id, tool:name, input}].
 * - Each standalone `toolResult` attaches to the message immediately FOLLOWING its
 *   call's message (any role; the library pairs by id, role-free). Call-adjacent
 *   placement keeps the result in the call's own pin window: herding results onto
 *   a later user turn would pin every call through its result (measured
 *   2026-09-17: 11/11 pinned, zero Jev candidates). A result whose call is in the
 *   final message lands on one trailing empty user message and is counted, never
 *   silently dropped.
 */
export function adaptOmpTranscript(events: OmpEvent[]): { messages: Message[]; stats: AdapterStats } {
  const stats: AdapterStats = {
    eventsIn: events.length,
    messagesIn: 0,
    thinkingCharsDropped: 0,
    resultsPaired: 0,
    resultsTrailing: 0,
  };
  const messages: Message[] = [];
  // results recorded with the emitted length at encounter time (= index of the
  // next emitted message, or messages.length when nothing follows yet).
  const pending: Array<{ id: string; text: string; isError: boolean; at: number }> = [];

  for (const event of events) {
    if (event.type !== 'message_end' || !event.message) continue;
    const msg = event.message;
    stats.messagesIn += 1;
    if (msg.role === 'user') {
      const text = (msg.content ?? [])
        .filter((c) => c.type === 'text')
        .map((c) => c.text ?? '')
        .join('\n');
      messages.push({ role: 'user', text, toolUses: [], toolResults: [] });
    } else if (msg.role === 'assistant') {
      const parts: string[] = [];
      const toolUses: Message['toolUses'] = [];
      for (const c of msg.content ?? []) {
        if (c.type === 'text') parts.push(c.text ?? '');
        else if (c.type === 'thinking') stats.thinkingCharsDropped += c.thinking?.length ?? 0;
        else if (c.type === 'toolCall' && c.id) {
          toolUses.push({ tool_use_id: c.id, tool: c.name ?? 'unknown', input: c.arguments ?? {} });
        }
      }
      messages.push({ role: 'assistant', text: parts.join('\n'), toolUses, toolResults: [] });
    } else if (msg.role === 'toolResult' && msg.toolCallId) {
      const text = (msg.content ?? [])
        .filter((c) => c.type === 'text')
        .map((c) => c.text ?? '')
        .join('\n');
      pending.push({ id: msg.toolCallId, text, isError: !!msg.isError, at: messages.length });
    }
  }
  for (const r of pending) {
    const target = r.at < messages.length ? messages[r.at] : undefined;
    if (target) {
      target.toolResults = [...(target.toolResults ?? []), { tool_use_id: r.id, text: r.text, isError: r.isError }];
      stats.resultsPaired += 1;
    } else {
      messages.push({ role: 'user', text: '', toolUses: [], toolResults: [{ tool_use_id: r.id, text: r.text, isError: r.isError }] });
      stats.resultsTrailing += 1;
    }
  }
  return { messages, stats };
}

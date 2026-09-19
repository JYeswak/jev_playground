/**
 * The omp hook BINDING — the piece that was missing between `omp-hook.ts` and a real session.
 *
 * `omp-hook.ts` has always carried an honest claim level: "L0 offline-verified … L2/L3 — the
 * binding loads and fires in a real session — is a named follow-up, not claimed here." That
 * follow-up was never built, which is why AGENTS.md §4's omp clause has gone unmet all day:
 * "if it is an omp seam: the seam fires in a real omp session, and a known-bad input makes it
 * refuse".
 *
 * Module shape is copied from a hook that demonstrably loads in this harness:
 * `~/.omp/agent/extensions/dcg-guard.ts:430` is `export default function dcgGuard(pi) { pi.on(…) }`.
 * That file proves the factory contract; it says nothing about `session_before_compact`, whose
 * envelope comes from omp's in-session docs and remains the unpinned part.
 *
 * WHY THIS FILE DOES NOT INSTALL ITSELF. Installing an untested hook into the live session is how
 * the conductor loses the session: earlier today `pi install npm:pi-subagents` made EVERY `pi`
 * invocation fail, and the documented removal reported success without fixing it. A hook at
 * `<cwd>/.omp/hooks/pre/` runs inside the agent that would have to repair it. So this ships as a
 * module with a stub-driven proof, and the live install is a gated step a human takes.
 */
import { appendFileSync } from 'node:fs';
import type { JevAsker, Message } from 'fast-jev-compaction';
import { adaptOmpTranscript } from './omp-adapter.js';
import { compactOmpTranscriptSafe, OMP_HOOK_DEFAULTS, type OmpHookConfig } from './omp-hook.js';

/** The subset of omp's extension API this binding touches. */
/**
 * The envelope omp actually sends, discovered by logging its keys from a real `/compact` on
 * 2026-09-19 — NOT from documentation. In-session docs described `{ messages }`; production sends
 * `{ type, preparation, branchEntries, customInstructions, signal }`, and the transcript lives at
 * `preparation.messagesToSummarize` alongside `recentMessages`, `tokensBefore` and `previousSummary`.
 *
 * Both shapes are accepted: `messages` first for whatever omp version documented it, then the
 * observed path. A field name taken from docs and never fired is a guess; this one has a log line.
 */
export interface OmpCompactEvent {
  messages?: readonly Message[];
  preparation?: {
    messagesToSummarize?: readonly Message[];
    recentMessages?: readonly Message[];
    tokensBefore?: number;
  };
}

export interface OmpLike {
  on(
    event: 'session_before_compact',
    handler: (event: OmpCompactEvent) => Promise<OmpCompactReturn | undefined>,
  ): void;
}

/** omp's documented return contract for `session_before_compact`. */
export interface OmpCompactReturn {
  cancel?: boolean;
  compaction?: { messages: readonly Message[] };
}

export interface BindingDeps {
  asker: JevAsker;
  config?: Partial<OmpHookConfig>;
  /** Injected so a test can observe decisions without a log scraper. */
  onDecision?: (outcome: string, reason: string) => void;
  /**
   * Append one line per decision here. Lives in THIS module, not in the hook file, because a sink
   * in the hook is unreachable by any test: the hook sits outside `compaction/`'s package scope and
   * node refuses to resolve it from here. An observability feature nothing can test is the shape
   * this repo spent the day removing.
   *
   * Never receives the key or the transcript — outcome and reason only.
   */
  decisionLogPath?: string;
}

/**
 * Registers the pre-compaction handler.
 *
 * The handler NEVER throws and NEVER returns fewer messages than it was given unless compaction
 * actually succeeded. On any failure it returns `undefined`, which leaves omp's own summarizer in
 * charge — the fail-safe side `omp-hook.ts` documents, and the reason a Jev outage degrades this
 * seam to "no improvement" rather than "context destroyed".
 */
export function registerOmpCompactionHook(pi: OmpLike, deps: BindingDeps): void {
  const config: OmpHookConfig = { ...OMP_HOOK_DEFAULTS, ...(deps.config ?? {}) } as OmpHookConfig;

  const record = (outcome: string, reason: string): void => {
    deps.onDecision?.(outcome, reason);
    if (!deps.decisionLogPath) return;
    try {
      appendFileSync(deps.decisionLogPath, `${new Date().toISOString()} ${outcome}: ${reason}\n`);
    } catch {
      // A log that cannot be written must never break compaction.
    }
  };

  pi.on('session_before_compact', async (event) => {
    const messages = event?.messages ?? event?.preparation?.messagesToSummarize;
    // ADAPT, do not assume. omp's live messages are {role, customType, content, display,
    // details, attribution, timestamp} — observed from a real /compact — and are NOT
    // fast-jev-compaction's Message {role, text, toolUses}. Handing them over raw failed in
    // production with "undefined is not an object (evaluating 'tool of message.toolUses')".
    //
    // src/omp-adapter.ts already flattens exactly this content shape; it consumes `message_end`
    // events, so the live messages are wrapped into that form rather than given a third mapper.
    let adapted: readonly Message[] | undefined;
    if (Array.isArray(messages) && messages.length > 0) {
      const looksAdapted = typeof (messages[0] as { text?: unknown }).text === 'string'
        && Array.isArray((messages[0] as { toolUses?: unknown }).toolUses);
      if (looksAdapted) {
        adapted = messages as readonly Message[];
      } else {
        try {
          adapted = adaptOmpTranscript(
            (messages as unknown[]).map((m) => ({ type: 'message_end', message: m as never })),
          ).messages;
        } catch (error) {
          record('refused', `could not adapt omp messages: ${error instanceof Error ? error.message : String(error)}`);
          return undefined;
        }
        if (!adapted || adapted.length === 0) {
          // The adapter ran and produced nothing: the content-part shape differs too. Report the
          // first message's role and its parts' `type` values — names only, never their text.
          const m0 = messages[0] as { role?: unknown; content?: unknown };
          const parts = Array.isArray(m0?.content)
            ? (m0.content as Array<{ type?: unknown }>).map((c) => String(c?.type)).slice(0, 8).join('/')
            : typeof m0?.content;
          record('refused', `adapter yielded 0 of ${messages.length}; role=${String(m0?.role)} parts=${parts}`);
          return undefined;
        }
      }
    }

    // A malformed envelope is a KNOWN-BAD INPUT and must make the seam refuse, not guess.
    if (!Array.isArray(adapted) || adapted.length === 0) {
      // NAME WHAT ARRIVED. The first production firing (2026-09-19, three events from one
      // `/compact`) refused every one with "no messages on the event envelope" — which was true and
      // useless: it proved `event.messages` is not where omp puts the transcript, and gave nothing
      // to fix it with. Logging the envelope's top-level KEYS (never their values, which are the
      // transcript) turns the next refusal into the field name we need.
      const shape = event && typeof event === 'object'
        ? Object.keys(event as Record<string, unknown>).join(',') || '<no keys>'
        : typeof event;
      // One level deeper, still keys-and-counts only: which field holds the transcript?
      const ev = (event ?? {}) as Record<string, unknown>;
      const describe = (v: unknown): string =>
        Array.isArray(v) ? `array[${v.length}]`
          : v && typeof v === 'object' ? `{${Object.keys(v as object).slice(0, 12).join(',')}}`
            : typeof v;
      const detail = ['preparation', 'branchEntries']
        .map((k) => `${k}=${describe(ev[k])}`)
        .join(' ');
      record('refused', `no messages on the event envelope; envelope keys: ${shape}; ${detail}`);
      return undefined;
    }

    const outcome = await compactOmpTranscriptSafe(adapted, deps.asker, config);
    if (outcome.outcome !== 'compacted') {
      record('passthrough', outcome.reason);
      return undefined;
    }
    if (outcome.messages.length >= adapted.length) {
      // Defensive: a "compaction" that does not shrink is not a compaction.
      record('refused', 'compacted output was not smaller than its input');
      return undefined;
    }
    record('compacted', `${adapted.length} -> ${outcome.messages.length}`);
    return { compaction: { messages: outcome.messages } };
  });
}

export default function ompCompactionHook(_pi: OmpLike): void {
  throw new Error(
    'omp-binding: default export requires a configured JevAsker; call registerOmpCompactionHook(pi, deps) '
      + 'from a hook file that supplies one. Installing this module directly is deliberately not supported.',
  );
}

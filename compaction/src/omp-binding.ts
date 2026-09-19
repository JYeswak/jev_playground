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
import type { JevAsker, Message } from 'fast-jev-compaction';
import { compactOmpTranscriptSafe, OMP_HOOK_DEFAULTS, type OmpHookConfig } from './omp-hook.js';

/** The subset of omp's extension API this binding touches. */
export interface OmpLike {
  on(
    event: 'session_before_compact',
    handler: (event: { messages?: readonly Message[] }) => Promise<OmpCompactReturn | undefined>,
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

  pi.on('session_before_compact', async (event) => {
    const messages = event?.messages;
    // A malformed envelope is a KNOWN-BAD INPUT and must make the seam refuse, not guess.
    if (!Array.isArray(messages) || messages.length === 0) {
      deps.onDecision?.('refused', 'no messages on the event envelope');
      return undefined;
    }

    const outcome = await compactOmpTranscriptSafe(messages, deps.asker, config);
    if (outcome.outcome !== 'compacted') {
      deps.onDecision?.('passthrough', outcome.reason);
      return undefined;
    }
    if (outcome.messages.length >= messages.length) {
      // Defensive: a "compaction" that does not shrink is not a compaction.
      deps.onDecision?.('refused', 'compacted output was not smaller than its input');
      return undefined;
    }
    deps.onDecision?.('compacted', `${messages.length} -> ${outcome.messages.length}`);
    return { compaction: { messages: outcome.messages } };
  });
}

export default function ompCompactionHook(_pi: OmpLike): void {
  throw new Error(
    'omp-binding: default export requires a configured JevAsker; call registerOmpCompactionHook(pi, deps) '
      + 'from a hook file that supplies one. Installing this module directly is deliberately not supported.',
  );
}

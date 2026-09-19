import { compact, reductionRatio } from 'fast-jev-compaction';
import type {
  CompactOptions,
  CompactResult,
  JevAsker,
  Message,
} from 'fast-jev-compaction';

/**
 * omp pre-compact adapter: the `session_before_compact` half of
 * `fast-jev-compaction/hooks/fast-jev.ts`.
 *
 * Recon (see `runs/hook-recon-20260917.md`): omp exposes a pre-compaction
 * interception point, `session_before_compact`, which may return
 * `{ cancel?: boolean; compaction?: CompactionResult }`. The event name and
 * return contract come from omp's in-session docs, quoted verbatim in the
 * receipt. `~/.omp/agent/extensions/dcg-guard.ts:430-431` proves only the
 * module shape both use — a default-export factory calling `pi.on(...)`
 * (there, for `tool_call`) — discovered at `<cwd>/.omp/hooks/pre/*.ts`.
 *
 * Contract, mirroring `compactSession` in `fast-jev.ts`:
 * - transcript in (`Message[]` — the same shape `src/omp-adapter.ts`
 *   produces from an omp JSONL transcript), pruned messages out;
 * - throws when Jev fails — the caller decides whether to fall back
 *   (`compact` documents exactly this at `compact.ts:250-257`);
 * - the `Safe` wrapper below is the fail-safe side: on ANY error it returns
 *   the input unchanged. A compaction hook must never destroy context on
 *   error, so the hook binding only ever calls the safe path.
 *
 * Claim level: L0 offline-verified. The `session_before_compact` envelope
 * field names come from omp's in-session docs (omp ships as a compiled
 * binary; no `.d.ts` to pin against on disk), so L2/L3 — the binding loads
 * and fires in a real session — is a named follow-up, not claimed here.
 */

export const OMP_HOOK_DEFAULTS = {
  /** Below this reduction the hook yields to omp's built-in summarizer. */
  minReductionRatio: 0.25,
} as const;

export type OmpHookConfig = CompactOptions & {
  minReductionRatio: number;
};

/** Reads plain host-provided values; anything missing takes the defaults. */
export function resolveOmpHookConfig(
  options: Record<string, unknown> = {},
): OmpHookConfig {
  const config: OmpHookConfig = {
    minReductionRatio: OMP_HOOK_DEFAULTS.minReductionRatio,
  };
  for (const key of [
    'keepThreshold',
    'preserveRecentMessages',
    'maxStateTokens',
    'maxRequestTokens',
    'truncateHeadChars',
  ] as const) {
    const value = options[key];
    if (typeof value === 'number' && Number.isFinite(value)) config[key] = value;
  }
  const ratio = options['minReductionRatio'];
  if (typeof ratio === 'number' && Number.isFinite(ratio)) {
    config.minReductionRatio = ratio;
  }
  const goal = options['goal'];
  if (typeof goal === 'string' && goal.length > 0) config.goal = goal;
  return config;
}

export type OmpCompaction = {
  result: CompactResult;
  messages: Message[];
};

/**
 * Runs the library over an omp-shaped transcript. Throws when Jev fails —
 * use `compactOmpTranscriptSafe` at the hook boundary instead.
 */
export async function compactOmpTranscript(
  messages: readonly Message[],
  asker: JevAsker,
  config: OmpHookConfig,
): Promise<OmpCompaction> {
  const result = await compact(messages, asker, config);
  return { result, messages: result.messages };
}

export type OmpSafeOutcome =
  | { outcome: 'compacted'; result: CompactResult; messages: Message[] }
  | { outcome: 'passthrough'; messages: readonly Message[]; reason: string };

/**
 * Fail-safe side of the hook: never throws, never drops context on error.
 * Passthrough triggers: Jev/transport failure, below-minimum reduction
 * (omp's own summarizer then does the job), or an empty candidate set with
 * nothing to judge. The returned `messages` on passthrough is the input.
 */
export async function compactOmpTranscriptSafe(
  messages: readonly Message[],
  asker: JevAsker,
  config: OmpHookConfig,
): Promise<OmpSafeOutcome> {
  let result: CompactResult;
  try {
    result = await compact(messages, asker, config);
  } catch (error) {
    return {
      outcome: 'passthrough',
      messages,
      reason: `jev failure: ${error instanceof Error ? error.message : String(error)}`,
    };
  }
  if (reductionRatio(result) < config.minReductionRatio) {
    return {
      outcome: 'passthrough',
      messages,
      reason: `below minimum reduction: ${summarize(result)}`,
    };
  }
  return { outcome: 'compacted', result, messages: result.messages };
}

function percent(ratio: number): string {
  return `${Math.round(ratio * 100)}%`;
}

export function summarize(result: CompactResult): string {
  const { stats } = result;
  const parts = [
    stats.kept > 0 ? `${stats.kept} kept` : '',
    stats.resultsDropped > 0 ? `${stats.resultsDropped} results truncated` : '',
    stats.callsDropped > 0 ? `${stats.callsDropped} call_dropped` : '',
    stats.pinned > 0 ? `${stats.pinned} pinned` : '',
  ].filter(Boolean);
  return `${percent(reductionRatio(result))} reduction; ${
    parts.join(', ') || 'no tool calls'
  }; state ~${stats.stateTokens} tokens (${stats.stateStage}) in ${stats.requests} request(s)`;
}

export function decisionLog(result: CompactResult): string {
  return result.decisions
    .filter((d) => d.reason !== 'pinned')
    .map(
      (d) =>
        `${d.id}:${d.tool}:${d.action}/call=${d.keepCall.toFixed(2)}/result=${d.keepResult.toFixed(2)}`,
    )
    .join(' ');
}

const UI_LOG_MAX_CHARS = 4096;

export function decisionLogLines(
  result: CompactResult,
  maxChars: number = UI_LOG_MAX_CHARS,
): string[] {
  const entries = decisionLog(result).split(' ').filter(Boolean);
  if (entries.length === 0) return ['decisions: (none)'];
  const chunks: string[] = [];
  let current = '';
  for (const entry of entries) {
    const next = current ? `${current} ${entry}` : entry;
    if (current && next.length > maxChars - 24) {
      chunks.push(current);
      current = entry;
    } else current = next;
  }
  chunks.push(current);
  return chunks.map((chunk, index) =>
    chunks.length === 1
      ? `decisions: ${chunk}`
      : `decisions (${index + 1}/${chunks.length}): ${chunk}`,
  );
}

/** Minimal structural surface the binding needs; real `pi` satisfies this. */
export type OmpHookApi = {
  on: (
    event: 'session_before_compact',
    handler: (input: {
      messages: Message[];
      customInstructions?: string;
    }) => Promise<{ compaction?: unknown } | undefined | void> | { compaction?: unknown } | undefined | void,
  ) => void;
  log?: (text: string) => void;
};

export type OmpHookDeps = {
  asker: JevAsker;
  config?: OmpHookConfig;
  log?: (text: string) => void;
};

/**
 * Binds the safe path to omp's pre-compact point. Returns `undefined` (omp default behavior) on
 * every path — passthrough on error or decline, and honest yield on a compact verdict, because
 * the seam carries summary plus keep-boundary only. Named follow-up, not done here: prove L2/L3
 * in a live session with this file installed at `<repo>/.omp/hooks/pre/omp-jev.ts`.
 */
export function registerOmpHook(pi: OmpHookApi, deps: OmpHookDeps): void {
  const config = deps.config ?? resolveOmpHookConfig();
  const log = deps.log ?? pi.log ?? (() => {});
  pi.on('session_before_compact', async (input) => {
    // omp's HookRunner awaits this handler and reads its return (the same
    // async-listener shape as dcg-guard.ts:431). The outer try/catch is
    // belt-and-braces: even a throwing host `log` must yield passthrough,
    // never a rejected hook that takes the session's context down with it.
    try {
      const settled = await compactOmpTranscriptSafe(input.messages, deps.asker, {
        ...config,
        goal: config.goal ?? input.customInstructions,
      });
      if (settled.outcome === 'passthrough') {
        log(`omp-jev passthrough (${settled.reason})`);
        return undefined;
      }
      // Honest yield, same reason omp-binding.ts documents against the runtime: the seam has no
      // pruned-message channel, so a verdict is logged, never returned. omp's own summarizer
      // keeps the job; the decision log keeps the measurement.
      log(`omp-jev would-compact (${summarize(settled.result)}) — yielded to the built-in summarizer`);
      for (const line of decisionLogLines(settled.result)) log(line);
      return undefined;
    } catch (error) {
      try {
        log(`omp-jev passthrough (unexpected: ${error instanceof Error ? error.message : String(error)})`);
      } catch {
        // Host log itself failed; still yield default behavior silently.
      }
      return undefined;
    }
  });
}

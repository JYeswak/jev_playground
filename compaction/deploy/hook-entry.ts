/**
 * jev-compact hook entry — installed by `compaction/install-jev-compact.sh`.
 * Do not hand-edit the deployed copy; re-run the installer to upgrade.
 *
 * Source of truth: `compaction/src/omp-binding.ts`
 * (`registerOmpCompactionHookFromEnv`). All safety lives there: never throws,
 * registers nothing without TYPESAFE_API_KEY, and the handler only ever yields
 * (`undefined`) — omp's own summarizer keeps every job while Jev's verdict is
 * measured in the decision log.
 */
import type { OmpLike } from '../../lib/jev-compact/omp-binding.js';

// Lazy, guarded load: a missing optional dependency declines the hook instead of crashing the
// session at load time. Only the type import above is static, and it is erased at runtime.
type Binding = { registerOmpCompactionHookFromEnv: (pi: OmpLike) => void };

export interface EntryDeps {
  load?: () => Promise<Binding>;
  warn?: (message: string) => void;
}

const loadBinding = (): Promise<Binding> => import('../../lib/jev-compact/omp-binding.js');
const writeWarning = (message: string): void => { process.stderr.write(`${message}\n`); };

export default async function jevCompactHook(
  pi: OmpLike,
  { load = loadBinding, warn = writeWarning }: EntryDeps = {},
): Promise<void> {
  try {
    const { registerOmpCompactionHookFromEnv } = await load();
    registerOmpCompactionHookFromEnv(pi);
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    warn(
      `jev-compact: not loaded, /compact keeps omp's own summarizer (${reason}). ` +
        'If fast-jev-compaction is missing, run ./compaction/install-jev-compact.sh or `npm ci --prefix compaction`.',
    );
  }
}

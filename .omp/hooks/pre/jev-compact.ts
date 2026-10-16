/**
 * Live omp binding for the Jev pre-compaction seam.
 *
 * Installed 2026-09-18 on Joshua's instruction ("lets install it"), closing the half of
 * `AGENTS.md` §4 that `docs/demos/omp-seam-live-20260918.md` recorded as open: the seam's logic was
 * proven against real data and a live model at L2+, but omp had never loaded it.
 *
 * 2026-09-19: environment handling moved into `registerOmpCompactionHookFromEnv`
 * (`compaction/src/omp-binding.ts`, tested) — this file is now the same minimal entry every
 * installed repo gets (template: `compaction/deploy/hook-entry.ts`). One env reader, tested once,
 * deployed everywhere. Skill: `skill://jev-compact`.
 *
 * SAFETY IS THE WHOLE DESIGN OF THIS FILE. It runs inside the agent that would have to repair it,
 * and today an untested `pi` extension made every invocation of that host fail while its documented
 * removal reported success without fixing it. So:
 *
 *   - this module NEVER throws out of the entry;
 *   - with no `TYPESAFE_API_KEY` in the environment it registers NOTHING and returns quietly, so a
 *     keyless session behaves exactly as it did before this file existed;
 *   - the handler only ever yields (`undefined`), which leaves omp's own summarizer in charge.
 *     A compaction hook must cost a missed optimisation at worst, never a lost transcript — and,
 *     measured 2026-09-19 against the shipped runtime, the seam carries summary plus keep-boundary
 *     only, so a returned pruning would arrive malformed. Verdicts are measured, not shipped.
 *
 * The compaction logic itself is not here: it is `compaction/src/omp-binding.ts`, tested at
 * `compaction/test/omp-binding.test.ts` (real-transcript arms included), and the library core was
 * exercised live at 13 messages to 8 in 1,282 ms.
 */
import type { OmpLike } from '../../../compaction/src/omp-binding.js';

// The binding imports `fast-jev-compaction`, an optional pinned dependency installed from our own
// clone. A static import made a missing package crash the whole session at load (observed
// 2026-10-13, every pane after the kit 0.2.28 restart). The load is lazy and guarded instead: if it
// fails the entry declines, registers nothing, and names the repair. omp keeps its own summarizer.
// Only the type import above is static, and it is erased at runtime.
type Binding = { registerOmpCompactionHookFromEnv: (pi: OmpLike) => void };

export interface EntryDeps {
  load?: () => Promise<Binding>;
  warn?: (message: string) => void;
}

const loadBinding = (): Promise<Binding> => import('../../../compaction/src/omp-binding.js');
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

/**
 * Live omp binding for the Jev pre-compaction seam.
 *
 * Installed 2026-09-18 on Joshua's instruction ("lets install it"), closing the half of
 * `AGENTS.md` §4 that `docs/demos/omp-seam-live-20260918.md` recorded as open: the seam's logic was
 * proven against real data and a live model at L2+, but omp had never loaded it.
 *
 * SAFETY IS THE WHOLE DESIGN OF THIS FILE. It runs inside the agent that would have to repair it,
 * and today an untested `pi` extension made every invocation of that host fail while its documented
 * removal reported success without fixing it. So:
 *
 *   - every path is wrapped; this module NEVER throws out of `register` or out of the handler;
 *   - with no `TYPESAFE_API_KEY` in the environment it registers NOTHING and returns quietly, so a
 *     keyless session behaves exactly as it did before this file existed;
 *   - the handler returns `undefined` on any failure, which leaves omp's own summarizer in charge.
 *     A compaction hook that errors must cost a missed optimisation, never a lost transcript.
 *
 * The compaction logic itself is not here: it is `compaction/src/omp-binding.ts`, tested at
 * `compaction/test/omp-binding.test.ts` (6 tests, including a real-transcript Jev-outage arm), and
 * exercised live at 13 messages to 8 in 1,282 ms.
 */
// RELATIVE, not a bare specifier. A hook at .omp/hooks/pre/ is outside compaction/'s package
// scope, so `from 'fast-jev-compaction'` fails to resolve — omp reported exactly that and, to
// its credit, kept the session alive and answered the prompt anyway. omp fails OPEN on a broken
// hook, which is the opposite of what pi did with a broken extension today.
import { JevClient } from '../../../compaction/node_modules/fast-jev-compaction/dist/index.js';
import { registerOmpCompactionHook, type OmpLike } from '../../../compaction/src/omp-binding.js';

export default function jevCompactHook(pi: OmpLike): void {
  try {
    const apiKey = process.env.TYPESAFE_API_KEY;
    if (!apiKey) {
      // Not an error: the offline lane is the default, and a keyless session must be unchanged.
      return;
    }
    registerOmpCompactionHook(pi, {
      asker: new JevClient({ apiKey }),
      onDecision: (outcome, reason) => {
        // stderr only, and never the key or the transcript.
        process.stderr.write(`[jev-compact] ${outcome}: ${reason}\n`);
      },
    });
  } catch (error) {
    process.stderr.write(
      `[jev-compact] disabled, registration failed: ${error instanceof Error ? error.message : String(error)}\n`,
    );
  }
}

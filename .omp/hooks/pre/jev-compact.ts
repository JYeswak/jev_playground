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
import {
  registerOmpCompactionHookFromEnv,
  type OmpLike,
} from '../../../compaction/src/omp-binding.js';

export default function jevCompactHook(pi: OmpLike): void {
  registerOmpCompactionHookFromEnv(pi);
}

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
import {
  registerOmpCompactionHookFromEnv,
  type OmpLike,
} from '../../lib/jev-compact/omp-binding.js';

export default function jevCompactHook(pi: OmpLike): void {
  registerOmpCompactionHookFromEnv(pi);
}

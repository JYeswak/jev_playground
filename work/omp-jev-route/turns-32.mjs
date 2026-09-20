/**
 * eww turn set v1 — 32 distinct turns, LABELLED BEFORE ANY SCORE WAS READ.
 * Pinned inputs: commit this file first, then score. Do not edit after scoring;
 * a v2 with new turns supersedes, never amends.
 *
 * Classes (named subsets for re-testing the length-leak finding):
 *   heavy-clear   — plainly multi-step reasoning, unfamiliar code, hard judgment
 *   mech-clear    — plainly mechanical or read-only
 *   trap-short    — looks trivial (short), heavy by construction knowledge
 *   trap-long     — looks heavy (long), trivial actual ask
 * Truth: {heavyweight: bool, mechanical: bool} per turn, from the prompt alone.
 * Turns 1-10 are the P3-35 set, relabelled here unchanged.
 */
export const TURNS = [
  // --- 1-10: P3-35 set, labels as pre-registered there ---
  { id: 'port-retry-asyncgen', cls: 'heavy-clear', prompt: 'Port the retry helper to support async generators without breaking its three existing call sites.', truth: { heavyweight: true, mechanical: false } },
  { id: 'shared-state-leak', cls: 'heavy-clear', prompt: 'Three test files fail only when run together but pass individually. Find the shared-state leak.', truth: { heavyweight: true, mechanical: false } },
  { id: 'sqlite-migration-plan', cls: 'heavy-clear', prompt: 'Design a zero-downtime migration plan for moving the session store from JSONL to SQLite, with rollback.', truth: { heavyweight: true, mechanical: false } },
  { id: 'rename-tmp', cls: 'mech-clear', prompt: 'Rename the variable tmp to pendingCount.', truth: { heavyweight: false, mechanical: true } },
  { id: 'typo-funciton', cls: 'mech-clear', prompt: 'Fix this typo: funciton should be function.', truth: { heavyweight: false, mechanical: true } },
  { id: 'rerun-tests', cls: 'mech-clear', prompt: 'Re-run the failing test suite and report the pass and fail counts.', truth: { heavyweight: false, mechanical: true } },
  { id: 'bump-version', cls: 'trap-short', prompt: 'Just bump the version to 2.4.1.', truth: { heavyweight: true, mechanical: false }, note: 'construction: version compiled into CLI binary, installer manifest, update endpoint' },
  { id: 'auth-grace', cls: 'trap-short', prompt: 'Quick fix on the auth path: allow expired tokens a 30-second grace period.', truth: { heavyweight: true, mechanical: false }, note: 'construction: replay-window + revocation judgment' },
  { id: 'verbose-typo', cls: 'trap-long', prompt: 'Some background so this reads naturally. Our project started two years ago as a single script and has grown into a small service with a dozen modules. We follow conventional commits, we review every PR, and we keep a changelog. The retry helper lives in the shared library next to the HTTP client. Last quarter we migrated the test runner and nothing broke. Next quarter we plan to revisit the docs. None of that matters for this ask, which is small: fix the typo where the word seperate appears — it should be separate.', truth: { heavyweight: false, mechanical: true } },
  { id: 'verbose-rename', cls: 'trap-long', prompt: "A little history first. The user record used to carry a display name, then we split it into given and family names, then we added a preferred name override, and the mobile client still sends the old shape. Three migrations have touched this table and two more are planned. The admin console reads all four variants. This is context only. The actual ask: rename the field usr to user.", truth: { heavyweight: false, mechanical: true } },
  // --- 11-32: new turns, labelled now ---
  { id: 'deadlock-two-services', cls: 'heavy-clear', prompt: 'Two services deadlock under load about once a day. Find the lock-order inversion and fix it without serializing the hot path.', truth: { heavyweight: true, mechanical: false } },
  { id: 'schema-migration-backfill', cls: 'heavy-clear', prompt: 'Add a non-nullable column to the 40M-row events table with a backfill, no downtime, no long-held locks.', truth: { heavyweight: true, mechanical: false } },
  { id: 'regex-dos-audit', cls: 'heavy-clear', prompt: 'Audit these six regexes for catastrophic backtracking on untrusted input and rewrite the vulnerable ones without changing what they accept.', truth: { heavyweight: true, mechanical: false } },
  { id: 'incident-timeline', cls: 'heavy-clear', prompt: "Reconstruct what happened in yesterday's outage from these three contradictory timelines and name the root cause.", truth: { heavyweight: true, mechanical: false } },
  { id: 'api-rate-redesign', cls: 'heavy-clear', prompt: 'Redesign the rate limiter so bursty tenants stop starving steady ones, and prove the new bounds with a simulation.', truth: { heavyweight: true, mechanical: false } },
  { id: 'secret-rotation', cls: 'heavy-clear', prompt: 'Rotate the signing keys with zero downtime: dual-accept window, ordered rollout, and a rollback that cannot brick old tokens.', truth: { heavyweight: true, mechanical: false } },
  { id: 'query-planner-regression', cls: 'heavy-clear', prompt: 'This query got 100x slower after the upgrade. Explain the planner regression and rewrite it without hints.', truth: { heavyweight: true, mechanical: false } },
  { id: 'sort-imports', cls: 'mech-clear', prompt: 'Sort the imports in this file alphabetically.', truth: { heavyweight: false, mechanical: true } },
  { id: 'bump-year', cls: 'mech-clear', prompt: 'Update the copyright year from 2025 to 2026 in the license header.', truth: { heavyweight: false, mechanical: true } },
  { id: 'delete-branch', cls: 'mech-clear', prompt: 'Delete the merged feature branch.', truth: { heavyweight: false, mechanical: true } },
  { id: 'json-format', cls: 'mech-clear', prompt: 'Pretty-print this minified JSON file with 2-space indent.', truth: { heavyweight: false, mechanical: true } },
  { id: 'list-files', cls: 'mech-clear', prompt: 'What files are in the migrations directory?', truth: { heavyweight: false, mechanical: true } },
  { id: 'restart-service', cls: 'mech-clear', prompt: 'Restart the staging web service and confirm it responds on its health endpoint.', truth: { heavyweight: false, mechanical: true } },
  { id: 'chmod-script', cls: 'mech-clear', prompt: 'Make this shell script executable.', truth: { heavyweight: false, mechanical: true } },
  { id: 'dep-bump-patch', cls: 'trap-short', prompt: 'Bump lodash to the latest patch release.', truth: { heavyweight: true, mechanical: false }, note: 'construction: patch contains a breaking change to a function we monkey-patch; blind bump breaks prod' },
  { id: 'one-line-config', cls: 'trap-short', prompt: 'Flip the feature flag on.', truth: { heavyweight: true, mechanical: false }, note: 'construction: flag gates an irreversible migration that runs on first boot after flip' },
  { id: 'quick-index', cls: 'trap-short', prompt: 'Just add an index on that column.', truth: { heavyweight: true, mechanical: false }, note: 'construction: write-heavy table, index locks writes; needs concurrent build + load analysis' },
  { id: 'env-var', cls: 'trap-short', prompt: 'Add the missing env var.', truth: { heavyweight: true, mechanical: false }, note: 'construction: var name collides with a reserved one in production; value must come from the vault, not plaintext' },
  { id: 'verbose-comment', cls: 'trap-long', prompt: 'For context: this module handles session persistence across three backends with failover, and the team debated the retry policy for two sprints before settling on exponential backoff with jitter capped at 30 seconds. The on-call runbook references this file in three places. The metrics dashboard has a panel per backend. All of that is background. The ask: add a one-line comment above the retry constant stating its unit is seconds.', truth: { heavyweight: false, mechanical: true } },
  { id: 'verbose-echo', cls: 'trap-long', prompt: 'Some history on this script: it was written during the migration, patched twice during incidents, and is now run by cron every night at 2am with output mailed to the team. There was a proposal to rewrite it in Python but it was rejected as unnecessary churn. The cron entry lives in the deploy repo. None of that changes the task: append one echo line at the end printing DONE.', truth: { heavyweight: false, mechanical: true } },
  { id: 'verbose-pin', cls: 'trap-long', prompt: 'Context on our dependency policy: we pin all direct dependencies, review lockfile diffs in PRs, and have a weekly job that opens bump PRs. Last month a transitive bump broke the build for a day, so now CI runs the full suite on bump PRs. The policy doc is linked from the README. The actual request: change the pinned version of leftpad from 1.3.0 to 1.3.1 in package.json.', truth: { heavyweight: false, mechanical: true } },
  { id: 'verbose-grep', cls: 'trap-long', prompt: 'Background: the log aggregator samples debug logs at 1% and the team has been asking for better search. We evaluated three vendors and stayed with grep on rotated files because the volume is low. The runbook documents the exact invocation. Forget all that for now: run grep -c ERROR on today\u2019s log file and report the number.', truth: { heavyweight: false, mechanical: true } },
];

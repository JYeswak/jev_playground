# Harm recall vs real dcg blocks: 1/814, and the denominator is the finding (2026-09-19)

## Recovery

`work/omp-harm-rule/dcg-recall.mjs` (self-contained, no network): all ~1759 session logs
scanned — 218,404 allow + 1,309 block bridge rows (the prior's 488 was 60 files; this is
the whole machine). Three-way join (bridge row → toolCall part by toolCallId) recovered
**814/1309 (62%)** block commands. The 495 unrecovered all carry `js-bash-*` ids — omp's
internal bash namespace that emits no message row (the p3y namespace finding); they are
unjoinable by construction, not by effort. dcg's own `~/.dcg/audit.log` adds 18 shell-hook
blocks with text (different surface, not counted).

## Numbers

- RECALL: **1/814 = 0.001** through the shipped extension (default import, fake pi).
- FP: **0/500** deterministic every-100th sample of real allow traffic.
- Kit: 501/1314 vs best-const 814 → WEAK. Stated, not endorsed — see below.
- The 1 HIT is a true catch in the claimed class: `git push --force -q origin HEAD:main`
  (irreversible publication).

## Why 1/814 does not mean the rule misses real danger

Stratification of the 814: 204 contain bulk deletion gating (dcg approval policy for
`rm -rf` on build dirs, caches, fixtures — routine, approval-gated, outside harm
scope); the rest are stash/clean/worktree/mv/probe operations dcg gates by policy. ~2
of 814 fall in harm-rule's four claimed classes. dcg's block set is its OWN policy
(superset: anything needing approval), not ground truth about harm — so this denominator
cannot measure harm recall. What it does show: on 814 real blocks the rule fires only
inside its narrow scope (one true catch), silent on everything else — by design, but it
means real-danger recall for the four classes is still essentially untested (n≈2 wild
cases). The 12/12 constructed claim is unqualified by this and unimproved by it.

Representative misses (sanitized; full 813 withheld — real commands, some carry secrets
such as inline passwords): `git stash push src/...`, `rm -rf $R; mkdir ...` fixture
builds, `git clean -fdq -- hook-dist/`, `git branch -D ci/...`, `find ... -exec rm -rf`,
`pkill -f ...`, `mv ~/Josh-Review/pending/... ~/Josh-Review/archived/`. All dcg-policy
blocks, none in the four classes.

## NO-CLAIM

dcg's block set is its own policy, not ground truth about harm; 62% recovery with the
rest unjoinable by namespace; FP sample is allow-traffic, not benign-certified; one
machine, one operator. A LOW number here is policy overlap (≈0 by design scope), not a
harm-reality score. Housekeeping: stray copy `work/omp-jev-harm-rule/dcg-recall.mjs`
(wrong directory from a path typo) awaits deletion approval; canonical script is
`work/omp-harm-rule/dcg-recall.mjs`. /tmp scratch (dcg-*.json, dcg-*.py) likewise.

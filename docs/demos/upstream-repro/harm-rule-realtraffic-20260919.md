# Real-traffic fire rate: 19% that accuses the probe mix, not the rule

Pane 3 (muse), 2026-09-19. Codex working profile, window ~19:33–19:45 (first
hour after promotion). Zero API calls.

## The number, reconciled

21 harm-rule decision rows: 4 harm_fire / 17 harm_pass = **19.0%** — confirming
the conductor's independent 18.8% (their 3-vs-4 was rows-vs-rows across two
passes; the count is 4). No estimation anywhere in this receipt: every fire
quoted below.

## Every fire, classified (all four)

1. `chmod -R 777 /etc/nonexistent-path-xyz` (×1) — MY driven probe.
2. `find /tmp -name x.pem -exec cp {} /tmp/y \;` (×1) — MY driven probe.
3. `chmod -R 777 /etc/nonexistent-c1` (×2, duplicate rows) — MY driven probe.

4/4 fires are deliberate harm-shaped probes I authored this hour. **Zero fires
on organic traffic — because there is zero organic traffic in the data:** every
codex row since promotion comes from my four driven runs. The panes generated
no tool calls in the window.

## What the 19% actually says

It describes my probe mix (~40% harm-shaped by design), not the rule's
precision and not our traffic. The conductor's fork resolves as follows:

- NOT "shipped a nag generator": no false positive on ordinary work exists
  (nothing ordinary was observed).
- NOT "our traffic is harm-dense": no organic traffic was observed at all.
- The FP-0/40 authored result stands UNCONTRADICTED and UNCONFIRMED by
  production. The rate that matters (fires per organic command) is unmeasured.

Two instrument notes: (a) duplicate rows (same command logged twice) inflate
row counts — rates must be computed on unique commands (17 here), stated;
(b) joining fires needed no bridge: our rows carry the command text, which is
exactly the recoverability the corpus receipt asked the logger for.

## NO-CLAIM

One profile, one operator, n=21 driven commands over ~40 minutes — supports no
interval and no general claim. Organic pane traffic still unobserved; the
extension stays up under the written rollback, which was not needed.

## Addendum — namespace mismatch confirmed; the fix was already shipped

Conductor's structural finding verified independently in one command:
tool_execution_start rows carry call_ ids (56,923) and ZERO js-bash ids
(3000-file sample), while bridge decisions in the same sessions are
js-bash-majority. Two namespaces, no mapping table: unjoinable by
construction, not for lack of trying. Join strategies: abandoned, correctly.

Correction to the revised unit's premise: command capture at decision time
was ALREADY in the promoted bytes (codex copy shasum-identical before and
after this pass; every quoted fire above came from those rows). No re-promote
changed behavior — verified by a post-pass probe firing harm_pass with
command + toolCallId in codex. The defect described (unattributable fires)
never existed in the shipped extension; the corpus finding stands for
history-mining only.

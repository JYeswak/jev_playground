# Q64 — Ruling: §5 prose means — RETIRE as state-of-record, keep spread as context, tripwire on staleness

**Question (1): did any mean-score move upward across history?**
No — and stronger: **no mean value was ever modified at all.** Full `git log -p --follow`
(69 commits touching PLAN.md), every diff line matching `mean \d+\.\d+`:

| # | Commit | Sign | Line |
|---|---|---|---|
| 1 | 0a0b329b | + | old-form "Why this one first… mean 853.8" (creation) |
| 2–9 | 90d9bfee | − then 8× + | v2 rewrite: old form removed, eight `### §5.N … mean X` headings created |
| 10 | 0ea34ed0 | + | "mean 1.06/repo" — MU-H1 marker density, a measurement, not a candidate score |

Decomposition of the "11 edits": 8 creations + 1 restructure pair + 1 creation + 1 unrelated.
**Modifications: 0. Upward moves: 0. Downward moves: 0.** Means are write-once. The table scores'
all-downward pattern (Q63) has no prose counterpart because prose means never move — including when
they should: demo-7 was REPRICED (§3p: transferable claim ~3 points) yet its heading still reads
712.5. The observed failure mode is **staleness, not smuggling** — frozen rank info, harmless once,
misleading by default over time.

**Locatability bound:** headings match `^### §5\.\d+.*mean` reliably since the v2 rewrite; 8 of 9
carry means (§5.9 UNSCORED, exempt). History is complete for `mean \d+\.\d+` line shapes.
**Residual blind spot, named not hidden:** integer score prose ("score 905", "820 non-author",
"re-scored", "repriced") was NOT traced — a boost smuggled as integer prose trips neither the
STATUS watcher nor any mean check. That is the next unit, not this one.

**Question (2): MECHANISE or RETIRE? Ruling: RETIRE as state-of-record.**

- STATUS.tsv is already the state of record for order (RULING's own tables rank by STATUS scores:
  905/900/895/885…). The §5 means duplicate the ranking function while rotting (demo-7 proves it).
  Retiring a surface is cheaper than watching it, and this lane deleted a dead gate (§3h) rather
  than venerating it — same principle.
- What is NOT retired: the grader-spread annotations (N graders, range, "widest spread 740→845").
  STATUS holds one score; spread is disagreement information the table cannot carry. Keep as
  non-load-bearing context, explicitly not ranking input.
- **Staleness tripwire (the mechanical remainder):** any repricing/scoring event that changes what a
  heading asserts must update-or-strike the heading line in the same commit. Checkable form for a
  future lane-status extension: every `mean X` heading line must cite its aggregation basis
  (grader count + range already present satisfy this); a commit touching a candidate's score
  receipts that leaves its heading line untouched must state why in the message. Until that check
  exists, the rule is guidance — recorded as such per Q61's standard, not banked as mechanism.

**Net:** the blind spot is smaller than disclosed (0 modifications, not 11 live lines) but real in
the staleness direction; retirement removes the rot surface; the integer-prose residual is bounded
above and assigned onward. No upward smuggling occurred — the first-uploaded-means problem never
arose because means were never touched again.

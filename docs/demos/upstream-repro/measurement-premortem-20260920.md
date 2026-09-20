# Measurement pre-mortem: every tool call, observed and reportable `[receipt]`

**Verdict: NARROW.** No new capture (correct), no private log (wrong sink),
no model (no judgment class), no unqualified "every". What survives: a
reporter over session JSONL with per-surface denominators, goldens per the
table, and guardpack's four classes re-homed from a private log into
decision rows.

## Denominator defect, resolved with commands (the load-bearing part)

Conductor's baseline (3,291 observed vs 3,167 ids) mixed two different
things, and so did my first recount — substring matching caught
`diagnostic.v1` rows that merely mention the string. Measured properly
(decision-type rows only, jev-lab):

- 842 decision rows across 9 extensions; **80 distinct toolCallIds**.
- The 1,131 "id-less" rows are diagnostics, not observations.
- The "duplicates" (max 2) are two extensions co-observing one call
  (harm-rule + preaction on the same id) — the A11 lesson, not double-write.

So the denominator for "every tool call" is **distinct toolCallIds in
decision rows, per surface**: bash-via-dcg (221,722 decisions, all
profiles) and tool-calls-via-observer (profiles running it). Any report
claiming "every" without the per-surface qualifier repeats the `oracle`-
on-97-commits overclaim. "Coverage" = toolCallIds with ≥1 decision row
÷ distinct toolCallIds seen — both numbers from the same scan.

## Attack verdicts

1. **Guardpack tier-1 vs harm-rule: NOT redundant — refuted on the
   classes.** Tier-1: pipe-exit, stage-all, commit-backtick, grep-as-proof
   (agent-hygiene mistakes). Harm-rule: privilege_widening,
   secret_staging, irreversible_publication, security_control_tampering
   (destructive commands). Zero overlap; deleting tier-1 loses all four.
   What SHOULD be folded is the emission sink: tier-1 writes to
   `~/.guardpack/warnings.jsonl`, a private log with one reader, while
   harm-rule writes decision rows with an install receipt and live proof
   (115 pass, 14 fire). Adopt the row shape, keep the classes and the
   PreToolUse placement.
2. **S/N is not measurable; FP-rate is.** The usage script already states
   "a warning is not a prevented defect." Count firings (done), and
   measure false-positive rate against a labelled sample of real commands
   (harm corpus + organic labels exist; guardpack classes runnable over
   the 78k harvest the same way). "Did it help" is unobservable — report
   fire-rate with denominators and FP-rate on samples, never "prevented."
3. **Denominator above.** Per-surface or nothing.
4. **No model.** Every class on the table is a regex, and the harm
   precedent is a model losing to four regexes by one recall point. No
   class here names a judgment a regex cannot express. A Jev seat would
   be ceremony — stated so it does not get added later by default.

## Goldens (per table, agreed with one correction)

Shape-exact, counts-structural, volatile-scrubbed, pinned-fixture-exact —
with the correction that the pinned session must come from decision rows
(denominator-real), not a raw session slice, or the golden bakes in the
diagnostic contamination measured above. `UPDATE_GOLDENS=1` regenerates;
git diff is the review gate; `*.actual` ignored; PROVENANCE records
generator + fixture sha.

## NO-CLAIM

Pre-mortem: no code written. Denominator measured on jev-lab decision
rows (my glob; conductor's 3,167 counted a different cut — method
stated, not reconciled). Guardpack files read-only (another pane's live
work, untouched). `[receipt]` used.

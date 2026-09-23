# Planning review round 1 — pane 3 (TopazRaven), with W4.1+W4.2 measurement in hand

Scope: the integrated draft at `66f6ea5`. p5 (R1-1..R1-6) and p2 (6 changes)
covered W1/W2/W3/W6 and are integrated; this review does not relitigate them.
W7 is unreviewed (landed in round 1.5) and takes most of this pass. Numbering
continues p5's (R1-7+). Every change cites evidence or is marked [Inference].

## R1-7 (ADD): W7.1 ledger cannot feed the W7.4 ranking — two columns missing

W7.4 ranks by AGENTS.md's selection rule: ground truth exists today,
prevalence of the positive class, cost to measure, decision leverage. W7.1's
column list (`repo, sha, owner, license, jev_surface, what_it_decides,
own_suite_command, run_status, incumbent_arm, what_it_teaches_about_jev,
transferable_mechanism, application_in_our_systems, action`) carries none of
the four as data — `incumbent_arm` touches ground truth obliquely, and
prevalence and cost appear nowhere. The ranking will be argued from prose,
which is exactly what the rule exists to prevent. Evidence: W7.4 text vs
W7.1 column list (plan §4, W7).

```diff
 **W7.1 Clone ledger.** `notes/deep/clone-ledger.tsv`, one row per clone: `repo, sha, owner, license,
 jev_surface (choice|score|noul; SDK or hand-rolled POST), what_it_decides, own_suite_command,
 run_status (receipt path or never), incumbent_arm (Rule 14: what a person would ship instead, and
 whether the clone measured it), what_it_teaches_about_jev (one sentence, cited file:line),
-transferable_mechanism, application_in_our_systems (named omp surface or product path), action`.
+transferable_mechanism, application_in_our_systems (named omp surface or product path),
+prevalence_of_positive_class (with denominator, or unknown), cost_to_measure (keyless/live/RCH-worker),
+action`.
```

## R1-8 (CHANGE): W7.2's never-rows have owners nobody assigns

W7.1 acceptance: "every `run_status=never` row has an owner in W7.2." W7.2
assigns no one — the W7 header says "owners assigned as panes free", which
is a hope, not an assignment. Eight never-rows (plan §4 W7 census) with no
named owner will sit until Phase C. Evidence: W7.1 acceptance vs W7.2 text;
the 8 clones are named but no pane is.

```diff
 **W7.1 Clone ledger.** ... Acceptance: 28
-rows, every `run_status=never` row has an owner in W7.2.
+rows, every `run_status=never` row names its W7.2 owner in the `owner` column
+at ledger time (conductor assigns leftovers in Phase C, or the row stays open).
```

## R1-9 (REMOVE): one cold read, not two — merge W5.2 into W6.2(d)

W5.2 (cold read of the self-assessment) and W6.2 oracle (d) (cold read of
the rewritten README by "a pane on a different model") are the same
cognitive act — a cold pane reading a stranger-facing document with a
checklist — scheduled as two wave-2 operations on two panes. The README
cold read is already "dispatched to pane 5 as a one-file cold read" (W6.2
landing note). Evidence: W5.2 text; W6.2 acceptance (d) + landing note.
```diff
 **W5.2 Cold read (wave 2).** A pane on a different model reads W5.1 with no other context and lists
 every dangling reference and every claim whose tier it cannot reproduce. The packet is not
-publishable until that list is empty or each item is answered.
+publishable until that list is empty or each item is answered. Runs as one session with the W6.2(d)
+README cold read (same pane, two checklists): the pane answers "what is this and what do I run"
+without opening another file, then works the W5.1 dangling list. One scheduling cost, both
+acceptance targets kept.
```

## R1-10 (CHANGE): §2 should permit what the depth directive already allowed

My W4.1 transcript cell went BLOCKED → RESOLVED only because the
DEPTH-DIRECTIVE re-read the dispatch scope: session dirs named for the
launch cwd are the jev panes' own transcripts. Plan §2 forbids *writes*
under `~/.omp/...` but says nothing explicit about *reads* of those dirs,
so the next pane will re-block the same way. Evidence:
`notes/deep/franken-deps.md` Depth update; DEPTH-DIRECTIVE.md pane-3
section; §2 text (write-ban only).

```diff
 - It does **not** write to `~/.omp/agent/` or any `~/.omp/profiles/<name>/agent/` path. ...
+- Reading the jev panes' own session transcripts
+  (`~/.omp/profiles/<profile>/agent/sessions/-Developer-jev/`,
+  `~/.omp/agent/sessions/-Developer-jev/`) is in-scope: the directory name
+  is the launch cwd, so these are jev-session records, not another pane's
+  substrate. Any other profile path stays out.
```

## R1-11 (FLAG): W4.1 acceptance is satisfiable by exclusion alone — mine proves it

W4.1 acceptance: "every citation found by `rg` has a row or a stated
reason it is not a dependency." My artifact meets it with 2316 lines, of
which the DATA-CORPORA + BOOKKEEPING exclusions cover the bulk and ~30
relied-upon rows carry the substance. A future pane can meet the same
acceptance with one giant exclusion row and zero verdicts. The acceptance
cannot fail as written. Evidence: `notes/deep/franken-deps.tsv` (50 rows
at depth close) vs the acceptance text.

```diff
 Oracle: the packet text quoted with its tier. Acceptance:
 every citation found by `rg -n 'franken|asupersync' <tracked jev files>` has a row or a stated
-reason it is not a dependency.
+reason it is not a dependency, AND the artifact states the relied-upon row count beside the
+excluded-line count (this pass: ~30 relied-upon rows with packet verdicts against ~2300 cited
+lines). An audit with zero relied-upon rows is a census, not an audit.
```

## R1-12 (CHANGE): W7.2 receipt names collide on rerun — add worker+outcome

W7.2 receipts are `docs/demos/upstream-repro/<clone>-<date>.md`. The s1-rs
rerun I am executing now targets the same name as the existing
`s1-rs-rch-20260922.md` (1661c73): same clone, same date, different worker,
possibly different verdict. First-writer-wins naming loses the rerun or
forces an ad-hoc rename. Evidence: this turn's W7.2 task (a) running now.

```diff
 Receipt per clone in
-`docs/demos/upstream-repro/<clone>-<date>.md`, `Boundary` line included. Depth rule applies: a
+`docs/demos/upstream-repro/<clone>-<date>[-<worker>[-<outcome>]].md`
+(existing `s1-rs-rch-20260922.md` keeps its name; my rerun lands beside it, never over it),
+`Boundary` line included. Depth rule applies: a
 clone that will not run gets the four earned-label fields.
```

## Packets reviewed without changes proposed

W1 (p2's six, integrated at 66f6ea5 — verified the diff hunks match the
review file), W2 (p5's R1-2/R1-3), W3 (p5's R1-6 + method change),
W5 (assessment protocol is the RULEBOOK's own; nothing to add from W4),
W6 (R1-2 entry rule + landing notes read correctly), W0, §5–§12 (the
§5 rows-stay-planned rule already covers the W2.3 timing question).
No change in this pass removes a packet: the one removal (R1-9) merges two
operations into one session and keeps both acceptance targets.

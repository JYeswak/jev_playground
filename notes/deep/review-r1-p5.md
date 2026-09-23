# Planning review round 1 — pane 5 (SunnyTiger), with W5.1 measurement in hand

Prompt run verbatim on the whole of `docs/PLAN-DEEP-KIT-20260922.md` (500 lines, read §§1–12 + Appendices A–E). Evidence: `notes/deep/jev-assessment.md` (8b09086), pin 33fe6ae run outputs, and `file:line` below. Anything without evidence is labelled `[Inference]`.

---

## R1-1 (REMOVE): Drop W1.8 `/loop` dogfood from wave 5 — it cannot legally run there

**Analysis.** W1.8 drives "the Phase-D bead queue", but Phase D entry is Phase C exit (§10: every §4 packet is a bead, `br ready` non-empty), and Phase C entry is Phase B exit (two review rounds integrated, round-to-round diff down to wording). A wave-5 loop over a queue that cannot exist before waves 2–3 of *planning* is scheduled fiction. Worse, its own Risk admits the delivery mechanism (`ntm send` of a slash command) is untested by the kit author — so the packet's oracle (`.omp/loop-state` iterations) depends on an experiment it also promises to run ("record whether `ntm send` works as a separate finding"). A packet that both needs and tests its own delivery path has no acceptance leg to stand on: if delivery fails there is no loop, and if the loop fails there is no delivery finding. Shrink to what is actually available in wave 5: a bounded manual `/loop --while` trial by one pane on one bead, typed by hand, with the three stop reasons observed. The `ntm send` delivery question becomes a W1.1-style census row (one command, observed once), not half of W1.8's oracle.

```diff
-**W1.8 `/loop --while` dogfooded (wave 5).** Goal: the kit's continuation gate driving real work.
-One pane runs `/loop --while 'sh scripts/omp-continue.sh'` on the Phase-D bead queue. Oracle:
-`.omp/loop-state` shows iterations; the loop stops on `.omp/STOP`, on 3 stalled iterations, and on
-a red claim gate — each stop observed once. Risk: the kit README marks `ntm send` delivery of a slash
-command untested; deliver `/loop` by typing in the pane, then record whether `ntm send` works as a
-separate finding. Acceptance: three stop reasons observed with `.omp/loop-state` and the stop line.
+**W1.8 `/loop --while` trial, bounded (wave 5, earliest).** Goal: learn whether the kit's
+continuation gate can drive one real bead. One pane types `/loop --while
+'sh scripts/omp-continue.sh'` by hand on one bead and watches for the three stop reasons
+(`.omp/STOP`, 3 stalled iterations, red claim gate). The `ntm send` delivery question is NOT part
+of this packet: it is a single W1.1-style census row (send one slash command once, record delivered
+or not). Rationale: the Phase-D queue does not exist until Phase C exits (§10), and a packet
+that both needs and tests its own delivery path cannot fail cleanly. Full dogfood waits for a
+Phase-D bead queue that is non-empty. Acceptance: three stop reasons observed once each, typed by
+hand, with `.omp/loop-state` and the stop line; delivery finding recorded separately.
```

---

## R1-2 (CHANGE): W6.2 cannot start while §9's release gate is tripped — say which moves first

**Analysis.** Measured tonight at pin 33fe6ae: `foundation/gates.sh` FAILING, stage `97-readme-counts` RED rc=1 silent (`notes/deep/jev-assessment.md` §4.4). Plan §9: "Nothing in §5 reaches README.md while … a `foundation/gates.sh` stage [is] red at the pin" — non-waivable. W6.2 (README rewrite, wave 1, "runs beside the panes") writes README.md while the gate it must satisfy is red. That is a plan that violates its own release gate on the first wave. Either the RED is a five-minute count fix (likely: pane 3's new stage moved a denominator the README hand-typed) or it is real drift — but W6.2's entry must name it. Otherwise pane 1 faces exactly the pressure D3 exists to prevent: a rewrite blocked on a red gate it is told to ship beside.

```diff
 **W6.2 README rewrite (wave 1, runs beside the panes).** Goal: a stranger understands in two
 minutes what Jev is, what this lane found, what they can run in one command, and where the
 evidence lives. Anchor: current `README.md` (read in full first) and `skill://readme-update`,
 `skill://readme-writing`, `skill://stop-slop`. Target: `README.md` only; worklog-shaped content moves
 out, not deeper. Oracle: (a) every command under "The thing to run" exits 0 from a clean checkout
 with no key (`jev-cx5` acceptance); (b) every numeral in the README is registered in
 `foundation/kit/claims.tsv` or cut (feeds W2.3); (c) `foundation/gates.d/97-readme-counts.sh` stays
 green; (d) a cold read by a pane on a different model (wave 2) answers "what is this and what do I
 run" correctly without opening another file. Fixture: the current README as the known-bad input —
 the rewrite is measured against it, not against taste alone. Risk: README counts are gated by stage
 97 and a numerals ratchet (stage 95); a rewrite that deletes a counted numeral must update the
 registry in the same commit, never loosen the gate. Acceptance: (a)–(c) observed, (d) in round 1.
+Entry: stage 97 green at the rewrite's base commit, or a §9-shape waiver recorded first (97 is RED
+at pin 33fe6ae — `notes/deep/jev-assessment.md` §4.4). The rewrite does not start red against its
+own oracle.
```

---

## R1-3 (FLAG): Two acceptances that cannot fail — W2.3's floor and W2.4's advisory mode

**Analysis.** The dispatch demands flagging any §4 acceptance that cannot fail. (a) W2.3: "Ratchet, not a target: the first floor is whatever W2.1 measured." A floor set at the measured value passes by construction on landing day; the packet's acceptance (stage green + selftest RED) then certifies a tautology plus a selftest. The selftest is the only falsifiable part — say so, and require the floor's first *rise* (or first RED on a real regression) before the claim-coverage row can go `enforce=yes`. (b) W2.4: cadence is "advisory (non-blocking) until one resurrection has been acted on." A non-blocking check cannot fail, so W2.4 as written always lands. Either make the advisory output a counted census line that W2.1's successor must reconcile (so silence is visible), or mark W2.4 `PREPARED-NOT-MEASURED` until the first acted-on resurrection. Fixing the flag, not the packets:

```diff
 **W2.3 Claim-coverage ratchet (wave 3).** Stage `foundation/gates.d/18-claim-coverage.sh`: coverage
 fraction from W2.1(b) as a floor that may only rise; `--selftest` plants an unregistered numeric
 README sentence and requires RED naming it. Ratchet, not a target: the first floor is whatever W2.1
-measured.
+measured. The landing acceptance (stage green + selftest RED) certifies the selftest only; the
+ratchet itself is proven the first time the floor rises on a real measurement or fires RED on a
+real regression. The §5 claim-coverage row stays `planned` until then.
```

```diff
 **W2.4 Ledger resurrection (wave 3).** `scripts/ledger-resurrect.sh`: lists NEGATIVE_EVIDENCE rows
 whose SHA/version predicate is now satisfied; cadence = every `foundation/gates.sh` run, advisory
-(non-blocking) until one resurrection has been acted on. `--selftest` plants a row whose pinned SHA
-moved in a fixture manifest.
+(non-blocking) until one resurrection has been acted on — and while non-blocking it cannot fail,
+so it lands as `PREPARED-NOT-MEASURED`: each run appends its candidate count to a census line the
+next W2.1-successor reconciles, making silence visible instead of green. `--selftest` plants a row
+whose pinned SHA moved in a fixture manifest.
```

---

## R1-4 (CHANGE): Single-source the 12 pattern names — W1.5 as specified creates two doctrines

**Analysis.** Problem item 5: AGENTS.md carries 10 adapted patterns; kit-guard A9 demands 12 verbatim names. W1.5 resolves this by *adding three names to AGENTS.md with jev definitions* — leaving the lane with an adapted-10 doctrine in prose and a verbatim-12 doctrine in the guard, i.e. the exact "second convention beside the existing" shape AGENTS.md prohibits ("second convention beside existing is PROHIBITED" is lane law for code; the same logic governs doctrine an agent must satisfy twice). The durable fix is single-sourcing: one file both surfaces read. Concretely, `foundation/kit/reward-hacking.md` holds the 12 verbatim names (kit's requirement, machine-checked), AGENTS.md keeps its 10 adapted names plus a pointer line, and the A9 check reads the kit file — so a future 13th name has one home. Evidence: `docs/PLAN-DEEP-KIT-20260922.md:48-49` (the 9/12 grep), W1.5 text at plan line 177-185.

```diff
 **W1.5 Re-anchor and A9 made true (wave 3).** Goal: the compaction message names files that exist
 and the pattern check names patterns we hold. Decision (Rule 12, adopt by default): add the three
 missing names to AGENTS.md's reward-hacking list with jev definitions — `close-pump abuse` is
 Problem item 6 in our own tree, `scope-splitting` and `bench-path hardcoding` have no jev instance
-yet and get one line each. `reanchorFiles` = `AGENTS.md` (§4 Definition of Done), the bead, and
-`GATES.md`. No second DoD file (no proliferation). Anchor: Problem items 4–5. Target: `AGENTS.md`
-(reserve first), `.omp/kit-guard.json`. Oracle: `/kit-guard` command reports `12/12 present`;
-a planted AGENTS.md edit that deletes one name returns the A9 `isError` frame. Acceptance: both
-directions observed in a live pane (L3).
+yet and get one line each — in ONE file, not two: `foundation/kit/reward-hacking.md` holds the 12
+verbatim names (the machine-checked source of truth for the A9 check); AGENTS.md keeps its adapted
+list plus a one-line pointer and does not duplicate the names. Two doctrines for one rule is how a
+future 13th name gets added to exactly one of them. `reanchorFiles` = `AGENTS.md` (§4 Definition of
+Done), the bead, and `GATES.md`. No second DoD file (no proliferation). Anchor: Problem items 4–5.
+Target: `foundation/kit/reward-hacking.md` (new), `AGENTS.md` (pointer line only, reserve first),
+`.omp/kit-guard.json`. Oracle: `/kit-guard` command reports `12/12 present` against the kit file;
+a planted edit deleting one name from the kit file returns the A9 `isError` frame. Acceptance: both
+directions observed in a live pane (L3).
```

---

## R1-5 (CHANGE): W1.1 must define "loaded" without the RPC proxy — the proxy cannot see a live pane

**Analysis.** W1.1's oracle leans on "a fresh `--mode=rpc --max-time` session per profile" as "the loaded-at-start proxy". But the lane has measured (AGENTS.md, RPC section) that `--mode=rpc` **spawns a new session** — it never attaches to a live pane. A proxy that by construction cannot observe the thing being measured (what is loaded in panes 2–6, started before the install commit) will report green for a session that is not any worker pane. The honest loaded-test for a live pane is narrower: (start-time after install commit) AND (mechanism observable from inside that pane's own session: `get_available_commands` listing kit-guard, or one planted benign interrupt frame). Where neither is obtainable without restarting the pane, the cell is UNMEASURED — and the packet already provides the word. This does not weaken W1.1; it stops the proxy from manufacturing six loaded rows.

```diff
 **W1.1 Load census (wave 1).** Goal: for each of the six jev panes, is each kit mechanism *loaded*,
 not merely present on disk? Anchor: Problem items 1–3. Target: `notes/deep/omp-kit-load-census.tsv`
 (pane, pid, profile, launch dir, start time, rules discovered, disabled rules, ttsr.repeatMode and
 repeatGap as that profile resolves them, kit-guard listed in `get_available_commands`). Oracle:
 `tests/doctor.sh` from the kit run with the pane's own `--profile`, plus `omp --profile <p> ttsr list`;
-a fresh `--mode=rpc --max-time` session per profile is the loaded-at-start proxy, and the pane's
-start time vs the install commit is the live-pane answer. Fixture: happy = pane 1 (started after the
-rules commit); edge = a profile with `ttsr.disabledRules` (grok disables `absence-from-one-probe`,
-muse disables `bash-structural-def-search`); adversarial = launch one probe from `jev/notes/` to
-confirm the subdirectory trap. Risk: `--mode=rpc` scans a session per call; bound with `--max-time`.
-Acceptance: 6 rows, every cell measured or `UNMEASURED` with the command that failed; a row that
-says loaded without an RPC or doctor line is a defect.
+a fresh `--mode=rpc --max-time` session per profile proves a *new* session would load the kit — it
+is not evidence about any live pane (`--mode=rpc` spawns; it never attaches — AGENTS.md). The
+live-pane answer is start-time vs the install commit plus a mechanism observed from inside that
+pane's own session (kit-guard in its `available_commands`, or one planted benign frame); where
+neither is obtainable short of restart, the cell is UNMEASURED, not proxied. Fixture:
+happy = pane 1 (started after the rules commit); edge = a profile with `ttsr.disabledRules` (grok
+disables `absence-from-one-probe`, muse disables `bash-structural-def-search`); adversarial =
+launch one probe from `jev/notes/` to confirm the subdirectory trap. Risk: `--mode=rpc` spawns a
+session per call; bound with `--max-time`. Acceptance: 6 rows, every cell measured or `UNMEASURED`
+with the command that failed; a row that says loaded for a live pane on RPC-proxy evidence alone
+is a defect.
```

---

## R1-6 (CHANGE): W3.1's 88-row matrix does not fit one wave-1 pane — split it or it ships thin

**Analysis.** W3.1 demands 14 concepts + 23 gates + 12 checklist items + 11 patterns + 28 A–B rows = 88 rows, each with source, evidence, executes receipt, honest-version, cost, defect class, and falsification experiment — in wave 1, beside five sibling panes doing the same. My W5.1 (12 claims, 5 re-runs, no executes-receipts beyond exit codes) consumed a full session; 88 rows with `executes` receipts is two to three sessions at that rate, and a matrix finished in one session will be 88 HAVE-by-assertion rows — the exact failure mode its own `executes` column exists to prevent. Split by falsifiability per-FIX: wave 1 covers the 14 concepts + 23 gates (37 rows, the pack's novel content); the 12 checklist items, 11 patterns, and A–B re-score ride wave 2 with W3.2, where each GAP already becomes a bead carrying its row. No content is cut; the denominator is phased so the executes column stays honest.

```diff
 **W3.1 Mechanism transfer matrix (wave 1).** Goal: every transferable item in the pack scored
 against jev with a file:line. Rows: the 14 cross-pollination concepts, the 23 execution-readiness
-gates, the 12 composite-checklist items, the 11 negative patterns, and A1–B14 re-scored (correcting
-the stale B5 row). Columns: `id, source(file:section), jev_status(HAVE|PARTIAL|GAP|NA),
-evidence(path:line or command), executes(yes|no|unknown), smallest_honest_version, cost,
-defect_class_it_catches, falsification_experiment(adapted from the synthesis)`. The `executes`
-column is the point: synthesis finding 2 is "mechanism existence is systematically ahead of
-execution", and that is a claim about us until measured. Oracle: the file on disk and a command run
-now; a HAVE without an `executes=yes` receipt is PARTIAL. Acceptance: every source row present
-(count them), no HAVE without evidence, every GAP carries a Rule 12 adoption line or a refusal with
-all three fields.
+Wave 1 rows: the 14 cross-pollination concepts and the 23 execution-readiness gates (37 rows —
+the pack's novel content). The 12 composite-checklist items, the 11 negative patterns, and the
+A1–B14 re-score (correcting the stale B5 row) ride wave 2 with W3.2, where each GAP becomes a bead
+carrying its row. Rationale: 88 rows with executes-receipts is two to three sessions at the W5.1
+rate (12 claims per session); a single-session 88-row matrix ships HAVE-by-assertion, the failure
+its own `executes` column exists to prevent. Columns: `id, source(file:section),
+jev_status(HAVE|PARTIAL|GAP|NA), evidence(path:line or command), executes(yes|no|unknown),
+smallest_honest_version, cost, defect_class_it_catches, falsification_experiment(adapted from the
+synthesis)`. The `executes` column is the point: synthesis finding 2 is "mechanism existence is
+systematically ahead of execution", and that is a claim about us until measured. Oracle: the file
+on disk and a command run now; a HAVE without an `executes=yes` receipt is PARTIAL. Acceptance per
+wave: every source row for that wave present (count them), no HAVE without evidence, every GAP
+carries a Rule 12 adoption line or a refusal with all three fields.
```

---

## Packets reviewed without changes proposed

W2.1 (census with denominators, no judgment model — the right shape; its three numbers unblock W2.3/W2.4 honestly), W2.2 (folds existing repair beads; oracle is a rerun, not prose), W2.5 (canary-first hook lane — the one gate edit with a self-proving order), W2.6 (C4→C2 honest provided the run page shows the verdict whatever it is — but see R1-2: do not push beside a RED gate silently), W4.1/W4.2 (facts-only rider handling with the escalation path already named), W5.2 (cold read by a different model family is the correct backstop for W5.1's self-grading), W6.1 (fast-forward discipline is right; needs the R1-2 sentence so RED pins push RED verdicts, not rewrites).

NO-CLAIM: a review is not a measurement. Every change above cites plan lines, W5.1 outputs, or lane law; the one inference (W3.1 session-rate math) is labelled by its basis.

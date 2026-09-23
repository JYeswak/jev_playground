# Mechanism transfer matrix (W3.1) — franken mechanisms scored against jev

HEAD run at: `33fe6ae` (dispatch said `572e3eb`; tree moved — every receipt below names the HEAD it ran at).
Pins: omp-kit `/Users/josh/Downloads/omp-kit (1).zip` sha256 `cea66f8bcb616737`; franken-assessments `/Users/josh/Downloads/franken-assessments-44-v8.zip` sha256 `70628b1f9a6d6f61`. Both extracted read-only at `/tmp/jev-intake/`.
Bead: `jev-deep-kit-8q7.3`. Scope: jev repo only.

## Preregistered (written before the executes battery and before subagent returns)

- Source counts, stated so a reader can check completeness: 14 concepts
  (`synthesis/cross-pollination.md` §1–§14), 23 gates
  (`synthesis/planning/execution-readiness.md` Gate 1–23), 12 composite items
  (same file, "Strongest-observed composite checklist" 1–12), 11 negative
  patterns (`synthesis/negative-patterns.md` P1–P11), 28 checklist items
  (`starter-kit/CHECKLIST.md` A1–A14, B1–B14). Total 88 rows + header.
- Scoring rule, from the packet: a HAVE with `executes=unknown` is PARTIAL.
  `executes=yes` requires a command run now with observed output, not a file
  read. For P-rows (patterns), HAVE means jev exhibits the pattern, GAP means
  it does not; `executes` there records whether the observation command ran.
- Predicted PARTIALs before running: C1 (registry, no SHA-mismatch arm), C9
  (skip lanes exist, suite green — expected HAVE pending suite run), G6 (hook
  live, no claim lane), G7 (adapter vendored, arm unrun), G16 (taxonomy prose,
  unenforced), G19 (stage-17 slice only). Predicted GAPs: C2, C5, C6, C10–C13,
  G11, G15, G23, B11–B13.
- Feasibility arms (must pass or the instrument is blind): G1 (`br ready`
  returns rows), C3 (ledger rows with retry predicates exist), B1 (beads file
  non-empty). A zero on any of these invalidates the whole pass.
- Planted negative (packet §6): one HAVE row broken in a /tmp copy; the
  execution_evidence command must report the break. Chosen target: G9 via
  `foundation/kit/check-claim-discipline.sh` on a planted unmatched
## Depth pass (directive 2026-09-22): what changed after the first draft

The first draft carried 35 `executes=unknown` cells. All are earned now: five
subagents (one per source list, re-fanned on the working agent after the scout
fleet died on a 404 model) re-ran every HAVE, and pane 4 re-ran each decisive
command. Corrections the verifiers forced into the TSV:
- Counts drift on a live tree: `br ready` 5→4, beads 105→107
  (70 closed / 18 in_progress / 14 blocked / 5 open), thin closes 14→11 with
  ids, ledger R1-R5→R1-R77+ (83 headers, 97 retry lines, 64 retry-condition).
- K11/A9/G18: 3 kit items absent, not 2 — close-pump abuse,
  scope-splitting, bench-path hardcoding. AGENTS's 10th is its own
  Cherry-picked N.
- P4's named instance was repaired mid-pass (preparsed --live lane +
  receipt landed); the row now cites the live one (kit-gap B5's false
  "no pre-commit hook").
- P7: `notes/deep/jev-assessment.md` EXISTS (W5.1 landed); only the W5.2
  cold read is unverified. Status stays HAVE.
- G7/K1 demoted back to PARTIAL on second-worker dissent: the keyless arm
  ran green today but the defining live head-to-head did not (keyed per
  test_client_with_live_apis.py:16-17). Promotion on a fake-model arm was
  hasty; the dissent stands in the rows.
- B7 corrected: 20 gate-touching commits exist; per-change two-direction
  evidence unassessed (was: "no gate-changing commit").
- A10 falsified upward: 1/107 beads carries `acceptance_criteria`.
- Stage 70 is GREEN now (repair `073372f` post-pin); no matrix row routes
  through it. GatesVerifier-2 ran the full `gates.sh`: 17/17 ALL GREEN,
  exit 0 (239s), stage 80 passing (202s) — pin-time REDs are all repaired,
  and rows routed through 80 cite direct per-stage exits anyway.
- Stage 97 live check PASSes; its --selftest exit is nondeterministic
  (1,1,0,0,0,0,0, identical arms-ok output; trap theory refuted, root cause
  not isolated) — recorded as flaky, not green.
- Final split: 31 HAVE / 41 PARTIAL / 15 GAP / 1 NA; zero `unknown` remain.
  Every `no` carries the command that verified the absence.

## Top 5 adoption candidates, ranked by (defect already observed in jev) × (cost)

1. **B13 false-closure sweep** → `scripts/` sweep + debt beads. Defect live:
   11 thin closes with ids. Cost: 1 script + beads.
2. **C2 freshness decay** → `claims.tsv` proof_date column + check-demotion
   expiry arm (D6 mechanical). Defect class live: P4 drift instances.
   Cost: 1 column + 1 arm.
3. **G12 coverage cadence + 97-selftest flake fix** → repair the wrapper exit
   path, then a quarterly coverage number. Defect live: nondeterministic
   selftest exit; one-shot audits. Cost: 1 fix + cadence.
4. **G4 CI backstop** → `.github/workflows/` + `.gitignore` allowlist change.
   Defect live: README.md:168, every gate `--no-verify`-bypassable. Cost:
   1 workflow + allowlist.
5. **B2 close-evidence lint** → hook lane or beads policy (reason length +
   token). Defect live: 11/70 thin. Cost: 1 lint.

## NO-CLAIM

The live head-to-head (G7/K1) is receipted 2026-09-21, not re-run now
(keyed); only its fake-model arm ran today (40/40). The 97-selftest flake
root cause is not isolated. Full `gates.sh` aggregate ran 17/17 ALL GREEN
(second worker, 239s) — pin-time REDs repaired on the live tree. Counts
recounted at commit HEAD; the tree moves under every number here.

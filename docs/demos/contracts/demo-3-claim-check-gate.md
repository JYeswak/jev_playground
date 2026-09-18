# Demo-3 contract — claim-check commit gate, CC-2 form

Mean 835.0 (2 graders). Source: `PLAN.md` §5.3. Standalone specification:
an implementer executing from it never opens `PLAN.md`.

## Goal and ownership

Deliver a git hook lane that extracts number/unit/cited-artifact triples
from a staged commit message and checks each triple against the cited
receipt, exiting nonzero on a contradiction — so a commit message can no
longer assert a number its own evidence does not contain. In product terms:
every commit carrying a numeric claim gets a mechanical check of that claim
against the artifact it cites, with contradictions refused at the gate,
insufficient evidence withheld (never approved), and infrastructure outage
degrading to a named skip rather than a fleet-wide block.

Explicit file ownership (new files only):
- `demos/claim-check-gate/` — the demo tree: hook script, extractor,
  injected-asker test suite, receipt writer.
- `<repo>/githooks/claim-check` — the installed lane entrypoint (wired
  through the existing `core.hooksPath` mechanism alongside the two live
  lanes; no new hook mechanism).
- `demos/claim-check-gate/runs/claim-check-<ISO8601>.json` — receipts.

Explicit non-goals:
- **Prose, reasoning, and uncited claims are out of scope.** The lane
  checks numbers against cited artifacts. A claim with no citation is
  `insufficient` by rule, and the lane does not attempt to judge it.
- **No second gate, no dashboard, no server.** One lane, exit codes, receipts.
- **No threshold tuning in this demo.** Initial thresholds below are
  stated with provenance and a re-derivation rule, not calibrated values.

Pane ownership: contract authored pane 3 (muse). Implementation pane
unassigned — conductor dispatches. Stage explicit paths only; `%an`
cannot attribute a commit.

## Product context and guardrails

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Offline lane first. Live calls are budgeted and stated in the receipt.
> The API key lives only in the environment as `TYPESAFE_API_KEY` and its value is never recorded
> in any artifact — names are expected, values are not.
>
> **Evidence rules.** A claim with no re-derivation path is not evidence. An empty scan set is an
> ERROR, never a pass. A one-item scan set is not a demonstration. A timeout is not a verdict.
> Exit code must agree with verdict text. These are implementation requirements, **not statements
> that any code or gate has passed.**
>
> **Shared worktree.** Three agents share this checkout and all commit as the same git identity,
> so `%an` cannot attribute a commit. Stage explicit paths, own files only, never `git add -A`,
> never amend, never rewrite shared history. Preserve peer changes: if a file you need belongs to
> another lane, message its owner with the exact replacement text rather than editing it.
>
> **Blocker protocol.** If a prerequisite is unavailable, report the exact blocker with the command
> and its verbatim output. Never substitute a stub for evidence, never weaken an adversarial
> assertion, and never let a missing capability be reported as passing check.

## Embedded contract

Facts carried (each measured; each constrains the design):
- **Why this exists, in this lane's own evidence.** A claim audit of 60
  numeric claims across four documents found **19 EXACT, 4 WRONG, 37
  UNVERIFIABLE** — and two of the four wrong ones were *residual
  instances* of an error already corrected elsewhere in the same file.
  Fixing a claim is not fixing its instances. This lane asserts numbers
  constantly (witness counts, reductions, ECE values) and verifies none
  of them mechanically; the 37 unverifiables are the standing debt this
  lane installs against. The lane already refuses a commit subject with
  no verification level and requires a close reason to *carry* proof —
  both check **form**. Nothing checks whether "8/8 witnesses" or "45%
  reduction" in a message matches the receipt it cites. That is the gap.
- **Adopted from MU-4: insufficient context ⇒ withhold, never approve.**
  That one rule separates a checker from a rubber stamp. A triple the
  evidence cannot decide is refused with reason `insufficient` (exit 2),
  never passed silently and never coerced into support.
- **Named skip path, specified as a requirement.** `CLAIM_CHECK_SKIPPED`
  on one stderr line with the cause (no key, API unreachable, timeout),
  exit 0. A pre-commit lane that blocks the whole fleet during a paid
  outage is unshippable — the skip path is a ship requirement, not a
  fallback, and its own RED arm (below) proves it fires.
- **It must not fire on its own source.** `30-no-secrets` once matched
  the key pattern written inside its own script; the fix (assemble test
  plants at runtime, assert the RED output names the plant file) is the
  pattern here too. Every test plant — fake receipts with wrong numbers,
  missing artifacts, unlabeled citations — is assembled at runtime in a
  scratch dir and the assertions match on the plant's path.

Mechanism, stage by stage:
1. **Install point: the commit-msg stage, not pre-commit.** Called the
   "pre-commit lane" in §5.3; installed at commit-msg because the staged
   message file exists only there (passed as `$1`). A pre-commit hook
   cannot reliably read a message that has not been written yet, and a
   lane built on guessing the message file is broken by construction.
   The installer wires `githooks/claim-check` through the existing
   `core.hooksPath` mechanism beside the two live lanes. If the hooks
   path is undiscoverable, the installer exits 2 naming the path —
   never a silent non-install.
2. **Extraction (deterministic, ours).** Parse the message file for
   `(number, unit, cited-artifact)` triples with fixed patterns:
   percentages (`\d+(?:\.\d+)?%`), counts (`\d+/\d+`), bare decimals
   adjacent to units (ms, s, chars, tokens, witnesses, calls), and
   artifact paths matching `(runs|fixtures|gates)/[\w./-]+\.(json|log|ts)`.
   Extraction is regex over text — no model, fully coverable offline. A
   message with zero triples exits 0 silently (nothing checkable is not
   a failure); the receipt still records `triples: 0` so "no claims
   found" is auditable, never assumed.
3. **Artifact load.** Resolve each cited path against the repo root. A
   cited artifact that does not exist ⇒ refuse that triple with reason
   `missing-artifact` (exit 1 naming both the claim and the path).
   Artifacts load as JSON where parseable, raw text otherwise; load
   failure ⇒ `insufficient`, never support.
4. **Jev question (exact), one per triple.** Pinned model `jev-1.13.0`
   (never `jev-latest`; record the resolved version). Noul with
   instructions: *"The commit message asserts the numeric claim <number
   unit>. The cited artifact content follows. The artifact supports the
   claim only if the number appears in it under the same meaning — same
   quantity, same denominator, same units."* plus the artifact content
   as the judged state. Mapping: support probability ≥0.75 ⇒ pass;
   ≤0.40 ⇒ contradicted (exit 1 naming claim, artifact, and both
   numbers); the open band (0.40, 0.75) ⇒ **withhold** (exit 2,
   reason `insufficient`). Malformed answer ⇒ withhold, counted. The
   0.75/0.40 pair is initial with provenance (mirrors the lane's keep
   thresholds) and moves only by the calibration rule in Open risks.
5. **Verdict aggregation.** Any contradicted ⇒ exit 1. Else any
   withhold ⇒ exit 2. Else exit 0, silent on the healthy path (a gate
   that comments on truthful commits gets uninstalled). Skip path:
   key/API failure before the first Jev call ⇒ `CLAIM_CHECK_SKIPPED`
   + cause on stderr, exit 0, counted in the receipt — never a block,
   never silent.

Cost and budget, in provider units: one Noul request per triple; typical
commits carry 0–3 triples, so the lane costs 0–3 input-sized requests
per commit with output free. Offline lane (injected asker, recorded
verdicts) spends $0 and proves extraction, mapping, all RED arms, and
the skip path. Live lane states calls, model version, and wall time per
run in the receipt.

API contract if Jev is called: endpoint
`POST https://api.typesafe.ai/v1/systemone`, Bearer `TYPESAFE_API_KEY`
from environment only, model pinned `jev-1.13.0`, one Noul per triple as
worded above; insufficient-context answers map to **withhold, never
approve** — exit 2 with reason, counted, never exit 0.

## Focused verification

Third-party commands (demo tree; no key, no network):
- `npm run install -- --dry-run` — install plan without writing.
- `npm test` — full suite with injected asker and runtime-assembled
  plants, including every RED arm below.
- `npm run check -- <message-file> --evidence <dir> --out runs/` —
  the manual pass whose receipt is the format reference.

RED arms (plants assembled at runtime in a scratch dir; each assertion
matches on the plant path):
- **Contradicted triple refuses.** Plant receipt `{"witnesses":
  {"passed": 7, "total": 8}}` + message claiming `8/8 witnesses`,
  canned asker 0.08 support ⇒ exit 1 naming `8/8`, the plant path, and
  the recorded `7`. A refusal that names only one side fails the run.
- **Empty evidence dir ⇒ ERROR.** Evidence dir with zero loadable files
  ⇒ exit 2 `EMPTY_EVIDENCE`, never "all supported". An empty scan set
  is an error, not a pass.
- **Claim citing no file ⇒ insufficient.** Triple with no artifact path
  ⇒ exit 2 `insufficient`, never supported. The rubber-stamp direction
  fails the run.
- **Residual-instance check.** Two message files asserting the same
  wrong number against two receipts (one wrong, one since corrected) ⇒
  both refused. Fixing one instance must not pass the other; this arm
  exists because the lane's own audit found exactly this shape twice.
- **Skip path fires.** Asker transport forced down (injected failure,
  no network touched) ⇒ `CLAIM_CHECK_SKIPPED` on stderr, exit 0.
  Blocking on infra failure fails the run.
- **Self-fire guard.** A plant containing the lane's own refusal strings
  (`CLAIM_CHECK_SKIPPED`, `EMPTY_EVIDENCE`) as *data* must not trip the
  lane's own matchers — the assertions bind to the plant file path, so
  a match outside the plant fails the run (the `30-no-secrets`
  self-match lesson, mechanized).

Denominator per run: triples extracted, artifacts loaded, Jev calls,
passed/contradicted/withheld/skipped, wall time. Exit code agrees with
verdict text in every arm. Who verifies: a non-author pane; the
contradiction plants are authored by the verifier, not the implementer.

## Evidence and logging

- Receipt path: `demos/claim-check-gate/runs/claim-check-<ISO8601>.json`.
  Schema: `inputs` (message sha, evidence dir listing with shas, model
  version, thresholds), `triples` (per triple: claim text, artifact,
  probability, verdict), `denominator` (counts above),
  `failures: []` (verbatim errors, never summaries).
- Commit subject level: `[test]` offline (suite green, no key);
  `[live]` only with N, model version, latency, budget. Never bare
  "verified".
- Boundary for `EVAL.md`: checks numbers against cited artifacts only.
  Does not check prose, reasoning, uncited claims, or whether the
  artifact itself is true. A receipt can be wrong; the lane checks the
  message against it, not the world against either.
- Never retro-edit a receipt. Supersede by re-running.
- No secret values, no operator home paths, no machine names anywhere —
  plants assembled at runtime, recorded responses scrubbed.

## Open risks with concrete resolution

- **Thresholds 0.75/0.40 are uncalibrated.** Resolution: accumulate
  contradiction verdicts — `npm run calibrate -- runs/claim-check-*.json`
  prints support-probability histograms for upheld vs overturned
  verdicts (overturned = author appealed with corrected evidence);
  move thresholds only when bins separate, and re-run the full suite
  plus a fresh plant set before landing.
- **False positives blocking real commits.** Resolution: the FP-rate
  EVAL row after 30 days of shadow (log-only) operation —
  `npm run fp-report -- runs/` prints FP/FN estimates with denominators;
  enforcement (nonzero exits) stays off until a human approves the row
  in a bead comment. Shadow-first, like the screen hook.
- **Message-file availability across clients.** IDE commits, `--amend`,
  and merge commits reach commit-msg differently. Resolution: the
  installer probes `git --version` client behaviors in CI; merge commits
  (multi-parent) are explicitly skipped with reason `merge-commit`
  (counted, exit 0) — reviewing generated merge text is out of scope,
  stated, not silently passed.

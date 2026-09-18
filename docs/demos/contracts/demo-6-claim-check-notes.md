# Demo-6 contract — claim-check notes form, MU-4

Mean 767.5 (2 graders). Source: `PLAN.md` §5.6. Standalone specification:
an implementer executing from it never opens `PLAN.md`.

## Goal and ownership

Deliver `jev-claims <notes.md> --evidence <dir>`: a writer-facing command
that checks working-file claims against a cited evidence directory and
reports supported / contradicted / insufficient with confidence, exiting
nonzero on any contradicted claim — so a working file gets the same
mechanical claim discipline as a commit message, at the moment of writing
rather than at the moment of committing. In product terms: EVAL rows,
duel files, receipts, and close-out reports carry checkable claims before
anyone publishes them, with insufficient evidence withholding approval
instead of waving it through.

Explicit file ownership (new files only):
- `demos/claim-check-notes/` — the demo tree: extractor, checker,
  injected-asker suite, receipt writer. Nothing outside this tree.
- `demos/claim-check-notes/runs/claims-<ISO8601>.json` — receipts.

Explicit non-goals:
- **Not a second demo-3.** Demo-3 (commit gate) checks staged
  commit-message triples at commit time; this checks a notes file
  against an evidence directory at writing time. Different trigger,
  parser, evidence contract, failure boundary — adjacent, not shared.
  Only one gets built (build condition below); building both is two
  demos wearing one mechanism and is refused up front.
- **No arbitrary-prose extraction.** v1 requires explicit claim blocks
  with structured citation paths (mechanism below). Generic extraction
  from free prose is an unsolved parser problem, not a feature to
  promise and miss.
- **No dashboard, no server, no CI gate in this demo.** One command,
  exit codes, receipts.

Pane ownership: contract authored pane 3 (muse). Implementation pane
unassigned — conductor dispatches. Stage explicit paths only.

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

Facts carried:
- **Adjacent but distinct from demo-3, by an arms-length ruling** — and
  only one gets built. Demo-3 is commit-triggered and parses
  commit-message triples; this is writer-facing over a notes file and
  an evidence directory. Different trigger, parser, evidence contract,
  failure boundary. The build condition is explicit and pre-registered:
  **demo-3 first, and this only if demo-3 proves the seam valuable**
  (measured: contradiction catch rate on real commits over 30 days of
  shadow operation, FP rate published, human approval in a bead
  comment). If demo-3's numbers do not clear that bar, this contract
  stays a contract — building the twin of a seam that failed to pay
  is how a backlog doubles.
- **Its stage-1 defect is the same one demo-5 had.** "Extracts
  verifiable working points" is not a mechanism — it hides a stage,
  and RED arms guarding stages 2+ of a pipeline whose stage 1 is
  unnamed certify nothing. So v1 does not extract from prose at all:
  claims arrive as **explicit claim blocks** with structured citation
  paths, in this exact record shape —
  `CLAIM(<id>): <verifiable sentence>  EVIDENCE: <path> [<path> ...]`
  — one block per claim, citation paths relative to `--evidence`.
  Anything not in a claim block is not a claim the tool sees (counted
  as `unparsed_lines`, never judged, never passed). The deterministic
  stage is therefore real: parse blocks (regex, fully coverable
  offline) → **Choice** over candidate evidence spans where span
  selection is ambiguous → **Noul** verification per
  claim-evidence pair. If a future version attempts free-prose
  extraction, that version re-opens this contract; it does not extend
  it silently.
- **Inherited rule from demo-3: insufficient context ⇒ withhold, never
  approve.** That one rule separates a checker from a rubber stamp,
  and it transfers unchanged: a claim the evidence cannot decide is
  refused with reason `insufficient` (exit 2), never passed, never
  coerced. Withhold is a first-class outcome with its own receipt
  count.
- The lane's own evidence for wanting this: the 60-claim audit (19
  EXACT, 4 WRONG, 37 UNVERIFIABLE, two residuals) plus the standing
  observation that EVAL rows, duel files, and close-out reports are
  where the lane's substantive claims actually live — commit messages
  carry the fewest checkable numbers per byte. Demo-3 guards the
  smallest surface; this guards the largest. That ordering (small
  surface first) is deliberate: prove the seam cheap before aiming it
  at everything.

Mechanism, stage by stage:
1. **Parse (deterministic, ours).** Read the notes file; extract
   `CLAIM(<id>)` blocks with `EVIDENCE:` paths; resolve paths against
   `--evidence`. Malformed blocks (missing id, missing evidence line,
   unresolvable path) ⇒ that claim `insufficient` with reason naming
   the defect — never skipped silently, never judged. Lines outside
   blocks ⇒ `unparsed_lines` count only.
2. **Load.** Read each cited file (JSON parsed, else raw text; load
   failure ⇒ `insufficient`). Missing file ⇒ refuse that claim with
   reason `missing-evidence` (exit 1 naming claim id and path).
3. **Span disambiguation (Choice, only when needed).** When a claim
   could match multiple evidence spans, a **Choice** over the
   candidate spans selects which the Noul judges — Choice returns a
   member, so paraphrase is impossible by construction. Single-span
   claims skip this stage (counted separately: `choice_calls` may be
   zero, and zero is reported, not hidden).
4. **Jev Noul per claim-evidence pair (exact).** Pinned model
   `jev-1.13.0` (never `jev-latest`; version recorded). Instructions:
   *"Working point: <claim sentence>. Cited evidence content follows.
   The evidence supports the claim only if the asserted content appears
   in it under the same meaning — same quantities, same names, same
   scope."* criteria.true: *"the evidence contains the claimed
   content"*; criteria.false: *"the evidence contradicts it or does
   not contain it."* Mapping: support ≥0.75 ⇒ supported; ≤0.40 ⇒
   contradicted (exit 1 naming claim id, evidence path, and the
   mismatch); open band ⇒ **withhold** (exit 2). Malformed answer ⇒
   withhold, counted. Thresholds initial with provenance (lane keep
   thresholds), moving only by the calibration rule in Open risks.
5. **Verdict aggregation.** Any contradicted ⇒ exit 1. Else any
   withhold ⇒ exit 2. Else exit 0, silent on the healthy path. A
   citation-span-mismatch arm (below) ensures a claim cannot pass
   merely because *some other* evidence file contains the same words:
   support must come from the *cited* path, and the receipt records
   which path supported which claim.

Cost and budget, in provider units: one Noul per claim plus one Choice
per ambiguous claim (typical notes file: 5–15 claims ⇒ single-digit
requests, output free). Offline lane (injected asker) spends $0 and
proves parsing, mapping, all RED arms. Live lane states calls, model
version, wall time per run.

API contract if Jev is called: endpoint
`POST https://api.typesafe.ai/v1/systemone`, Bearer `TYPESAFE_API_KEY`
from environment only, model pinned `jev-1.13.0`, Choice-then-Noul as
worded above; insufficient-context ⇒ withhold ⇒ exit 2, counted,
never exit 0.

## Focused verification

Third-party commands (demo tree; no key, no network):
- `npm test` — full suite with injected asker and runtime-assembled
  corpus, including every RED arm below.
- `jev-claims fixtures/notes.md --evidence fixtures/evidence/ --out runs/` —
  the manual pass whose receipt is the format reference.

RED arms (corpus assembled at runtime in a scratch dir; assertions
match on plant paths):
- **Supported pair passes.** Claim block citing an evidence file that
  contains the asserted content, canned support 0.9 ⇒ exit 0 with
  the claim id in the supported list. A pass that cannot name which
  claim passed fails the run.
- **Contradicted pair refuses.** Claim asserting a number the cited
  evidence contradicts (city-ordinance style: assert X, evidence says
  not-X), canned 0.1 ⇒ exit 1 naming claim id, evidence path, and
  both values. Refusal naming only one side fails the run.
- **Insufficient withholds.** Claim whose evidence is topically near
  but non-decisive, canned mid-band ⇒ exit 2 `insufficient`, never 0.
  The rubber-stamp direction fails the run.
- **Citation-span mismatch refused.** Claim text present in an
  *uncited* evidence file but absent from the *cited* one ⇒ must not
  pass. Support must come from the cited path; the receipt must show
  which path supported which claim, and a pass on cross-file leakage
  fails the run.
- **Empty evidence dir ⇒ ERROR.** Zero loadable files ⇒ exit 2
  `EMPTY_EVIDENCE`, never "all supported". Unlabeled block (no
  EVIDENCE line) ⇒ `insufficient`, never supported.
- **Malformed block handling.** Block missing id or with unresolvable
  path ⇒ `insufficient` naming the defect; the run continues over
  remaining claims (one bad block must not void the file, and must
  not pass silently either).

Denominator per run: blocks parsed, malformed, claims judged,
Choice calls, Noul calls, supported/contradicted/withheld,
unparsed_lines, wall time. Exit code agrees with verdict text. Who
verifies: a non-author pane; the corpus (supported/contradicted/
insufficient triplets) is authored by the verifier.

## Evidence and logging

- Receipt path: `demos/claim-check-notes/runs/claims-<ISO8601>.json`.
  Schema: `inputs` (notes sha, evidence dir listing with shas, model
  version, thresholds), `claims` (per claim: id, cited paths,
  supporting path, probability, verdict), `denominator` (counts
  above), `failures: []` (verbatim errors).
- Commit subject level: `[test]` offline; `[live]` only with N,
  model version, latency, budget. Never bare "verified".
- Boundary for `EVAL.md`: checks working-file claims against cited
  evidence only. Does not check prose outside claim blocks,
  reasoning quality, uncited claims, or whether cited evidence is
  itself true. Explicit-block v1 only; free-prose extraction would
  be a different demo with a different contract.
- Never retro-edit a receipt. Supersede by re-running.
- No secret values, no operator home paths, no machine names. Corpus
  assembled at runtime.

## Open risks with concrete resolution

- **Build condition unmet until demo-3 reports.** Resolution: the
  condition is a Boolean on demo-3's shadow receipt, evaluated by
  `npm run seam-check -- ../claim-check-gate/runs/` printing
  `BUILDABLE|WAIT` with the contradiction rate, FP rate, and the
  human-approval bead reference. WAIT is a valid, committable
  outcome — it keeps this contract a contract, which is cheaper
  than building the twin of a failed seam.
- **Claim-block syntax adoption.** Writers must write `CLAIM(id)` +
  `EVIDENCE:` lines or the tool sees nothing (by design — but an
  empty tool is a dead tool). Resolution: `jev-claims --lint
  <notes.md>` reports block coverage (`claims_found`,
  `unparsed_lines`) in seconds with no key; adoption is measured
  before any accuracy claim, and a file with zero blocks is a usage
  finding, not a tool failure.
- **Thresholds uncalibrated (0.75/0.40).** Resolution: same
  calibration rule as demo-3 — accumulate verdicts, print
  support-probability histograms for upheld vs overturned,
  move only on separation, re-run full suite + fresh plants
  before landing.

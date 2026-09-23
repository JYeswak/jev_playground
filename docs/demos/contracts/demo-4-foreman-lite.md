# Demo-4 contract — foreman-lite completion judge

Mean 812.5 (2 graders). Source: `PLAN.md` §5.4. Standalone specification:
an implementer executing from it never opens `PLAN.md`.

## Goal and ownership

Deliver `jev-bead-check <bead-id>`: a command that reads a bead's
WHAT/ACCEPTANCE via `br show`, diffs the work done since the bead started,
and returns a typed verdict plus an evidence checklist mapping each diff
hunk to the acceptance line it answers — composing as
`jev-bead-check <id> && br close <id>`. In product terms: no bead in this
lane closes on self-certification alone ever again; every close carries an
independent typed judgment with per-hunk evidence a human audits in
seconds, while the human keeps the final word (the judge advises, the
owner closes).

Explicit file ownership (new files only):
- `demos/foreman-lite/jev-bead-check` — the command (single bin, no
  daemon, no server, no second review service).
- `demos/foreman-lite/` — tests with canned asker, calibration corpus
  tooling, receipt writer. Nothing outside this tree.
- `.beads/baselines/<id>` — per-bead baseline records written by
  `jev-bead-check --record-start` (commit sha + bead body sha at check
  start; see Embedded contract). Created by the tool, read by the tool.
- `demos/foreman-lite/runs/bead-check-<ISO8601>.json` — receipts.

Explicit non-goals:
- **No automatic close.** The judge never runs `br close`, never bypasses
  a gate on high confidence, and never turns a Jev probability into
  permission. Verdict `complete` is advice; the bead owner still closes.
- **No second review service, no daemon.** One command, invoked by hand
  or by the human, exiting with a verdict. Anything ambient is out.
- **No judgment of acceptance quality.** The judge checks evidence
  against stated acceptance (see Boundary). Whether the acceptance was
  the right acceptance is a planning question for beads-before-code.

Pane ownership: contract authored pane 3 (muse). Implementation pane
unassigned — conductor dispatches. Stage explicit paths only.

## Product context and guardrails

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Claims about Jev come from live calls; the receipt states the calls made and what they cost.
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
- **The duel's best RED arm, verbatim requirement.** A bead with an
  **empty diff must return human-needed, never complete.** Our
  `close-evidence-gate` checks a close reason's *form* (carries proof);
  nothing checks its *substance* (proof answers acceptance). This demo
  is the substance check, and the empty-diff arm is what makes it a
  gate rather than a second opinion phrased politely.
- Verdict dimensions are the foreman set (usage map §6,
  `foreman@2c43982`): `complete` / `requirements-met` /
  `tests-sufficient` / `verify-needed` / `human-needed`. The overall
  verdict is a **Choice over these supplied candidates** — Choice
  returns a member of a set, so paraphrase is impossible by
  construction, and a bare chat-model "looks good" (untyped, unthresh-
  olded, unauditable) is explicitly not an acceptable judge output.
- The evidence checklist is per acceptance line, not per verdict: for
  each ACCEPTANCE line in the bead body, the checklist names the diff
  hunks answering it (by file + hunk header) with a per-line Noul
  support probability, or marks the line `unanswered`. A `complete`
  verdict with any line `unanswered` is a contradiction the command
  must refuse to emit (exit 2, reason `checklist-incomplete`).

Mechanism, stage by stage:
1. **Baseline resolution (explicit, never guessed).** "The diff since
   the bead started" is ambiguous with three panes committing, so the
   command resolves it thus: `jev-bead-check --record-start <id>`
   writes `.beads/baselines/<id>` containing the current HEAD sha and
   the bead body sha; `jev-bead-check <id>` diffs recorded-baseline
   HEAD against current HEAD (`git diff <base> HEAD -- <paths>`,
   paths restricted to the bead's owned files where declared). No
   baseline file ⇒ ERROR `no-baseline` (exit 2), never "diff against
   last week" or any other guess. Rationale recorded here so it is not
   re-litigated: time-based baselines (`git rev-list --before=<ts>`)
   misattribute sibling commits; branch points do not exist on a
   single-branch lane; an explicit recorded baseline is the only
   definition all three panes can share.
2. **Bead read.** `br show <id>` (JSON) supplies WHAT, ACCEPTANCE lines,
   and status. Title-only body (no WHAT/ACCEPTANCE sections) ⇒ ERROR
   `unscopable-bead` (exit 2): a bead whose body is just its title
   cannot be judged and must not be closable through this command.
3. **Snapshot at check start.** Hash the bead body sha + the diff bytes
   (`sha256`) into the receipt preamble. Re-hash both at verdict time;
   on mismatch ⇒ verdict `human-needed`, reason `bead-moved-during-
   check`, exit 2. Shared worktrees make a moving HEAD and a closing
   bead the dangerous pair; the snapshot turns "did the ground move"
   from a worry into a field. Snapshot mismatch is never retried
   silently — the human re-runs the command.
4. **Jev questions (exact).** Pinned model `jev-1.13.0`, endpoint
   `POST https://api.typesafe.ai/v1/systemone`, Bearer from
   environment. First a **Choice** over the five verdict candidates
   with instructions: *"Given the bead's WHAT and ACCEPTANCE below and
   the diff summary that follows, select the judgment that best
   describes the work state. `complete` requires every acceptance line
   answered with evidence; `requirements-met` means behavior done,
   verification thin; `tests-sufficient` means verified but
   under-evidenced elsewhere; `verify-needed` means specific named
   gaps block closing; `human-needed` means the evidence cannot decide
   (empty diff, moved ground, unscopable bead)."* Then one **Noul per
   acceptance line**: *"Acceptance line: <line>. The cited diff hunks
   are: <hunks>. The hunks answer the line."* with
   criteria.true *"the hunks implement or verify what the line
   requires"* / criteria.false *"the hunks are unrelated to the line"*.
   Insufficient-context answers map to **withhold, never approve**: an
   acceptance line whose Noul withholds is marked `unanswered`, which
   blocks `complete` per the checklist rule above.
5. **Verdict assembly.** Overall = the Choice result, constrained:
   empty diff ⇒ force `human-needed` regardless of the Choice output
   (the RED arm is structural, not probabilistic); any line
   `unanswered` ⇒ cap at `verify-needed`; snapshot mismatch ⇒
   `human-needed`. Exit codes: 0 `complete`, 0 with checklist printed
   for `requirements-met`/`tests-sufficient` (advisory pass, human
   closes), 1 `verify-needed` (names the gaps), 2 `human-needed` or
   any ERROR. Exit code agrees with verdict text, always.
6. **Checklist output.** Human-readable lines `ACCEPTANCE <n>:
   <supported|unanswered> <- <file:hunk> (p=0.xx)` plus the overall
   verdict line. No prose summary — Jev generates nothing here; every
   word the command prints is template text around judged values.

Cost and budget, in provider units: one Choice + one Noul per
acceptance line per check (typical bead: 3–6 acceptance lines ⇒ 4–7
input-sized requests, output free). Offline lane (injected asker)
spends $0 and proves baseline handling, all RED arms, snapshot logic,
and checklist assembly. Live lane states calls, model version, and
wall time in the receipt.

API contract if Jev is called: endpoint, Bearer, pinned model as
above; one Choice + N per-line Nouls as worded; insufficient-context
⇒ withhold ⇒ line `unanswered` ⇒ `complete` impossible. Withhold is a
first-class outcome with its own receipt count, not an error path.

## Focused verification

Third-party commands (demo tree; no key, no network):
- `jev-bead-check --help` — documents baseline/record/check/exit codes.
- `npm test` — full suite with canned asker: baseline, snapshot,
  all RED arms, checklist assembly, exit-code agreement.
- `jev-bead-check <fixture-bead> --baseline <fixture-sha>` — manual
  pass against committed fixtures whose receipts are the format
  reference.

RED arms (canned asker; each asserts the verdict string AND the exit
code, since agreement is the requirement):
- **Empty diff ⇒ human-needed, never complete.** Fixture bead with a
  recorded baseline equal to HEAD (zero-hunk diff), canned asker
  forced to `complete` ⇒ command must still print `human-needed`
  exit 2. A structural arm must beat the model, not agree with it.
- **Deleted acceptance file ⇒ verify-needed.** Fixture where the only
  hunk deletes the file an acceptance line names ⇒ verdict
  `verify-needed` exit 1 naming the file. Destruction presented as
  completion fails the run.
- **Title-only bead ⇒ ERROR.** Fixture bead body with no WHAT/
  ACCEPTANCE ⇒ exit 2 `unscopable-bead`, never a verdict of any kind.
- **Moved ground ⇒ human-needed.** Fixture harness mutates the diff
  between snapshot and verdict (append a hunk mid-run via the
  injected transport hook) ⇒ exit 2 `bead-moved-during-check`.
  Silent re-snapshot fails the run.
- **Checklist contradiction refused.** Canned Choice `complete` with
  one Noul `unanswered` ⇒ exit 2 `checklist-incomplete`, never
  `complete`. The assembly constraint is tested, not trusted.
- **Empty scan set ⇒ ERROR.** Bead id that does not exist ⇒ exit 2,
  never a verdict. A one-acceptance bead reports but is not a
  demonstration; the receipt's denominator says so.

Denominator per run: acceptance lines, Noul calls, Choice calls,
supported/unanswered/withheld counts, snapshot match/mismatch, wall
time. Who verifies: a non-author pane; the fixture beads and their
planted diffs are authored by the verifier, and the forced-`complete`
canned asker above is the verifier's instrument, not the
implementer's optimism.

## Evidence and logging

- Receipt path: `demos/foreman-lite/runs/bead-check-<ISO8601>.json`.
  Schema: `inputs` (bead id, bead body sha, baseline sha, HEAD sha,
  model version, thresholds), `snapshot` (pre/post hashes, match),
  `decisions` (Choice verdict + confidence, per-line Noul
  probabilities, checklist), `denominator` (counts above),
  `failures: []` (verbatim errors).
- Commit subject level: `[test]` offline (suite green, no key);
  `[live]` only with N, model version, latency, budget. Never bare
  "verified".
- Boundary for `EVAL.md`: judges evidence against stated acceptance.
  Does not judge whether the acceptance was the right acceptance, does
  not detect work outside the diff, and cannot see uncommitted intent.
  A `complete` verdict is advice to the owner, not permission to skip
  every other gate.
- Never retro-edit a receipt. Supersede by re-running.
- No secret values, no operator home paths, no machine names anywhere.

## Open risks with concrete resolution

- **Biased labelled set.** Our own closed beads are positives-only: we
  closed them, so nearly all carry "complete" and negatives exist only
  where a follow-up bug appeared — sparse and lagging, so the judge's
  false-complete rate is unmeasurable until it fails in production.
  Resolution, as commands: mine negatives with
  `git log --oneline --grep="fixup\|revert\|follow-up" | head -50`,
  link each to its bead id, and require a pre-registered minimum of
  10 negatives before any accuracy claim is published
  (`npm run calibration -- --min-negatives 10` refuses with the
  current count until met). Until then the receipt reports raw
  verdict counts only — no accuracy, no calibration, no exceptions.
- **Ambiguous baseline.** "The diff since the bead started" has no
  meaning all three panes share without a record. Resolution: the
  `--record-start` / `.beads/baselines/<id>` mechanism above is
  mandatory, not advisory — `jev-bead-check <id>` with no baseline
  file exits 2 (`br show <id>` proves the bead exists; nothing proves
  where its work starts). Conductor records the baseline at dispatch
  time; the receipt carries both shas so any later reader can
  re-derive the exact diff with `git diff <base> HEAD`.
- **Confidence laundering.** A high Choice confidence could tempt a
  future change to auto-close. Resolution: structural, not cultural —
  the command contains no code path that invokes `br close`, and any
  commit adding one fails the `close-evidence-gate` review by policy
  (record that policy in the demo README so the refusal is citable,
  not tribal).

# REVIEW-PERSONAS — the review lenses that own this lane's doc sets (RULEBOOK-18 P6, persona half)

## Why personas own docs

A review lens with no owner is a lens nobody applies. Each persona below names one lens and the ONE
doc in this repo that a change on that lens is graded against — so "is this reviewed?" has a fixed
answer instead of a feeling, and the checklist lives where the change lands.

This lane's specific risk shape: **~20 vendored clones we must not edit, a metered probabilistic
API, three agents in one worktree, and two live git hooks that can block all three.** The personas
are chosen against that, not copied from a generic list.

## The persona registry (id · lens · owns: `<doc>`)

Each row: a stable id, the review lens it covers, and the repo-relative doc that persona owns.

Each row is ONE line: the machine contract is that a persona id and its `owns:` mapping co-occur on
the same line, so a wrapped row counts as zero.

- **P-maintainability** — readability, scope discipline, edit-in-place over file proliferation, never patching a vendored clone to make our demo pass — owns: `AGENTS.md` (§0 is explicitly the convention contract this lane is graded against)
- **P-security** — the paid surface: the key never entering the tree/log/fixture/message, fail-closed gates, no unattended live loop, adversarial-answer handling before any action — owns: `GATES.md` (§ Fail-closed rules plus the `30-no-secrets` lane)
- **P-performance** — Jev call count per session, the live-call budget, hook-path latency (two hooks now run on every commit), and no re-derivation of a corpus we already mirrored — owns: `TESTS.md` (§3 names what only a live call can show, which is where cost is decided)
- **P-ai-smells** — false-confidence tests, tool-reported-not-verified, self-report theater, an acknowledgement read as an effect, an empty scan set read as a pass — owns: `NEGATIVE_EVIDENCE.md` (four of its eight rows are instrument errors this lens caught)
- **P-domain** — domain fidelity of a Jev claim: calibration, thresholds, and whether a number is graded by an external oracle rather than by our own engineering rigor — owns: `foundation/CALIBRATION.md`

## Contract (what the gate checks, mechanically)

`cross-lineage-review-gate.sh --personas <repo>` checks **presence and shape**: ≥5 personas, each
with an id matching `P-[a-z-]+` and an `owns:` doc path. It does not grade the review quality inside
each doc — that is human taste.

Leg 1 of P6 is separate and stricter: every substrate-mutating close/verdict receipt must carry a
`reviewer_lineage` that differs from its `author_lineage`. This lane currently emits no receipt of
that shape, so leg 1 is **N-A**, not satisfied.

## Honest scope, and the open gap this file does not close

Named ownership is a coverage mechanism, not an attestation. The `reviewer_lineage` field is
author-typed and forgeable; the un-forgeable root is a human reading the change.

**The real gap, stated rather than papered over:** this session mutated substrate hard — `git init`,
an absolute `core.hooksPath`, two live git hooks, seven gate stages — and **all of it was authored
and graded by one lineage (Claude Opus).** That is precisely the self-grade case P6 leg 1 exists to
refuse. A distinct-lineage review of the hook wiring (`githooks/pre-commit`, `githooks/commit-msg`,
`core.hooksPath`) is the correct next step and is tracked as a bead, not assumed away.

## Cross-references

- Gate inventory and every RED arm: [`GATES.md`](GATES.md)
- Refuted hypotheses and retractions: [`NEGATIVE_EVIDENCE.md`](NEGATIVE_EVIDENCE.md)
- Acceptance bar: [`AGENTS.md`](AGENTS.md) §4
- Canonical upstream registry this is modelled on: `~/Developer/foundry/loop-kit/REVIEW-PERSONAS.md`

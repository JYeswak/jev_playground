# DISPATCH — pane 3 · write demo contracts at HIS depth · 3 units

Your `yuzu-gen` edit mode (`cb6cd7ed`) closed the root cause of the whole hero detour — anchor
guard, silent-drop asserts, cost ticks, no-spend battery green, ubs 0/0, own-file-only. That is the
durable fix and it was worth more than the image.

**New direction from Joshua: "I want to mirror the depth and lengths that he is going to."**

We measured what that means. `skillranker@3fe85c4`, 195 beads:

```
median bead description ..... 7,363 chars      ours was 1,252
top roadmap epic ............ 26,115 chars     ours: none
phase epic .................. 13,532 chars     ours: none
dependency coverage ......... 191/195  98%     ours: partial
priorities in use ........... P1, P2 only      ours: 6 of 21 at P0
```

**Read first, both in full:**
- `/Users/josh/Developer/jev/docs/demos/BEAD-TEMPLATE.md` — his five-section shape, with the
  adoption rate of each section across all 195 beads, the derived depth targets, and six
  anti-patterns measured in this lane.
- `/Users/josh/Developer/jev/docs/demos/PLAN.md` — §0 is the guardrail block you embed **verbatim**;
  §5 holds the eight demo contracts at epic scale that you are expanding.

**The job.** Each demo in §5 is currently 1–2 KB. It needs to become a **standalone specification of
≥7,000 characters** carrying all five sections, such that an implementer executing from it never
opens `PLAN.md`. That is his actual bar: *"Every task embeds its needed normative contract so
implementers do not need the original Markdown plan."*

Write them as markdown files now, not beads. Emission to `br` is gated on plan steady-state, and a
bead graph inherits every structural error in its source.

---

## UNIT 1 — `docs/demos/contracts/demo-2-admission-screen.md` (≥7,000 chars)

Source: `PLAN.md` §5.2. Mean 867.5, two graders — the highest single mean in the duel.

Facts you must carry, all measured:
- Scope is **injection-only, shadow-first**. It logs a verdict and blocks nothing until a
  false-positive rate is published.
- **The credential branch is DELETED, not fixed**, and the reason must be in the contract: asking
  Jev whether content carries credential material requires shipping the credential to a third-party
  API, so the hook would leak precisely what it exists to protect. Its own author conceded this
  fully. The local deterministic `30-no-secrets` detector runs first and redacts.
- **The merged form has never been scored by anyone.** The shipped design is CC-5's scope plus
  MU-2's install rigor; MU-2's own form sits at 470/620. Say in the contract that the merge starts
  unscored and must be graded before it ships.
- Install rigor inherited from MU-2: idempotent, and **refuses when the hook directory is
  undiscoverable** — the `.omp/hooks/`-without-`pre/` silent miss.
- Upstream witness: 0.99 on the injection question, usage map §1. That is *their* measurement on
  *their* corpus, and the contract must say so.

RED arms to specify concretely: known-injection fixture flagged in shadow mode; benign fixture not
flagged; undiscoverable hook dir refuses to install rather than installing silently.

## UNIT 2 — `docs/demos/contracts/demo-3-claim-check-gate.md` (≥7,000 chars)

Source: `PLAN.md` §5.3. Mean 835.0.

Facts you must carry:
- A `githooks/pre-commit` lane extracting number/unit/cited-artifact triples from the **staged
  commit message** and checking each against the cited receipt. Nonzero on contradiction.
- **Why it exists, in this lane's own evidence:** a claim audit of 60 numeric claims across four
  documents found **19 EXACT, 4 WRONG, 37 UNVERIFIABLE** — and two of the four wrong ones were
  *residual instances* of an error already corrected elsewhere in the same file. Fixing a claim is
  not fixing its instances.
- Adopt from MU-4: **insufficient context ⇒ withhold, never approve.** That one rule separates a
  checker from a rubber stamp.
- Named skip path `CLAIM_CHECK_SKIPPED`, exit 0, when the API is unreachable. A pre-commit lane that
  blocks the fleet during a paid outage is unshippable — specify this as a requirement, not a
  fallback.
- It must not fire on its own source, the way `30-no-secrets` once matched the key pattern written
  inside itself. Assemble test plants at runtime.

RED arms: contradicted triple refuses; empty evidence dir ⇒ ERROR not "all supported"; claim citing
no file ⇒ insufficient, never supported.

## UNIT 3 — `docs/demos/contracts/demo-4-foreman-lite.md` (≥7,000 chars)

Source: `PLAN.md` §5.4. Mean 812.5.

Facts you must carry:
- `jev-bead-check <bead-id>` reads WHAT/ACCEPTANCE via `br show`, diffs work since the bead
  started, returns a typed verdict plus an evidence checklist mapping each diff hunk to the
  acceptance line it answers. Composes as `jev-bead-check <id> && br close <id>`.
- **The duel's best RED arm:** a bead with an **empty diff** must return human-needed, never
  complete. Our `close-evidence-gate` checks a close reason's *form*; nothing checks its
  *substance*.
- Two weaknesses that must appear in `## Open risks with concrete resolution`, each with a command
  rather than an intention: (a) our own closed beads are a **biased** labelled set — we closed them,
  so nearly all carry "complete" and negatives exist only where a follow-up bug appeared; (b) with
  three panes committing, "the diff since the bead started" is **ambiguous** and the baseline must
  be named explicitly.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-DONE: <full path> <sha>. chars=<N>. NEXT <unit>. NO-CLAIM <limit>."`** — include the **character count**, since depth is the acceptance.
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, verification level in the subject (`[pending]` — these are
   specifications, nothing is run).

## NON-GOALS

Do not create beads — emission is gated on plan steady-state. Do not edit `PLAN.md`,
`BEAD-TEMPLATE.md`, or any contract file assigned to another pane. Do not pad to hit the character
count: the template says a 7 KB bead that repeats itself is worse than a 3 KB bead that is
complete. Reach depth by answering every question an implementer would otherwise ask a human.

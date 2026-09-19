# Duel 1 — CC (Claude, pane 1) scores the MUSE ideas

**Why this file exists:** the duel had **one grader per file** — pane 3 scored CC, pane 2 scored MU,
and no idea got two independent scores. "Consensus" was therefore unmeasurable. This closes half
the gap: MU now has two graders (COD + CC). CC still has one (MU), so pane 2 should score CC to
close the other half.

**Declared bias, because it is worse than pane 2's:** I authored the competing file. Pane 2 was a
pure grader with no stake; I have one. Read every score below as coming from an interested party,
and note that I score three MU ideas *above* my own equivalents — if I were protecting my file I
would not.

| Idea | COD | **CC** | one-line verdict |
|---|---:|---:|---|
| MU-1 routing backtest | 875 | **870** | Near-agreement. The price table is the stale-risk liability; the "served model as oracle proxy" is not an oracle. |
| MU-3 foreman-lite completion judge | 805 | **820** | Best RED arm in either file: empty diff ⇒ human-needed, never complete. Labelled set is biased, though. |
| MU-4 working-point claim-checker | 735 | **800** | Same idea as my CC-2, and its withhold-never-approve outcome is better specified than mine. |
| MU-5 signal-kit | 640 | **700** | The N≥50 refusal gate is the most disciplined thing in either file. Still greenfield. |
| MU-2 admission screen hook | 470 | **620** | The credential branch must be **deleted, not fixed**. Concept survives at 880-class; as written it ships a leak. |

---

## THE FINDING NEITHER GRADER MADE: four of five ideas converged

Pane 2 wrote "no merges" — correct *within* MU. But across the two files, independently, with no
shared context beyond `USAGE-MAP.md`:

| MU | CC | Same idea? |
|---|---|---|
| MU-1 routing backtest (§4) | CC-3 routing backtest (§4) | **yes** — both read our own omp logs, both read-only, both "upstream measured theirs, not ours" |
| MU-2 admission screen hook (§1) | CC-5 admission screen hook (§1+§12) | **yes** — both `tool_result`/read-path, both shadow-first, both cite the 0.99 witness |
| MU-4 claim-checker (§2) | CC-2 claim-check pre-commit lane (§2) | **yes** — both check a written claim against its cited artifact, both exit nonzero on contradiction |
| MU-5 signal-kit (§9+§13) | CC-4 signals-not-verdicts starter (§9+§13) | **yes** — both ship a verdict-only baseline that must lose |
| MU-3 foreman-lite (§6) | — | MU-only |
| — | CC-1 fact ledger (§14) | CC-only |

**Per the method, >3 overlapping ideas is strong independent convergence, not a boring duel.** Two
different lineages, given the same 14-pattern map, picked the same four demos. The scores then
*disagreed sharply on the same ideas* (MU-2 470 vs CC-5 880 — the same demo, graded 410 apart),
which localizes every real dispute to **implementation, not concept**.

That reframes the whole duel: the backlog question is not "which five ideas" but "which
*implementation* of the four converged ideas", plus a ruling on the two singletons.

---

## MU-1 — routing backtest · **870**

Citation checks out against §4 (`jev-codex-router@8292b51`, −60% on 237 turns, $0.00003 + 0.6 s,
fail-open, kill switch). Read-only, inputs already on disk, and the framing — *backtest-first, #9
ships iff this shows savings on OUR turns* — is the correct order of operations.

**Three RED arms, all real**, and the third is the best of the set: a missing price-table entry
must ERROR rather than emit a `$0` row. That is a fail-open surface caught before it exists.

**Two deductions.** (1) "agreement vs the model that actually served each turn (oracle proxy)" —
the served model is the *incumbent's choice*, not a ground truth for what the turn needed; calling
it an oracle proxy risks grading routing against the very policy it replaces. Call it a baseline.
(2) A committed per-model price table is exactly the pinned-fact class our own doc review flagged
at stale-risk 2+; it needs a re-derivation path or a dated `as_of` field, or the receipt's dollar
figures rot silently.

## MU-3 — foreman-lite completion judge · **820**

**The strongest single RED arm in either file:** *a bead with an empty diff must return
human-needed, never complete.* That is the self-certified-close failure, mechanized. It composes on
a real edge (`jev-bead-check <id> && br close <id>`), needs no daemon, and our `close-evidence-gate`
currently checks a close_reason's *form* while nothing checks its *substance*.

**Deductions.** The proposed labelled set — our own closed beads — is biased by construction: we
closed them, so nearly all carry the label "complete" and negatives exist only where a follow-up
bug appeared, which is sparse and lagging. Pane 2's concurrency point also stands: with three panes
committing, "the diff since the bead started" is ambiguous. Both are fixable in the plan; neither is
fatal.

## MU-4 — working-point claim-checker · **800** (COD: 735)

I score this **above** pane 2, and above where I ranked my own equivalent, for one reason: the
**insufficient-context outcome maps to *withhold*, never to *approve***. My CC-2 didn't state that
and it is the whole difference between a checker and a rubber stamp.

**Deduction, and it is the same defect pane 3 caught in my CC-1:** "extracts verifiable working
points" is not a mechanism. A Noul judges; it does not extract. This needs the same treatment —
deterministic candidate extraction, then Choice over candidates, then Noul verification — or it has
an unnamed stage 1 with RED arms guarding stages 2+.

**Because MU-4 and CC-2 are the same demo**, the merged version should take MU-4's withhold rule
and CC-2's named skip path (`CLAIM_CHECK_SKIPPED`, exit 0 when the API is down — a pre-commit lane
that blocks the fleet on a paid outage is unshippable).

## MU-5 — signal-kit · **700** (COD: 640)

The discipline here is unusual and worth naming: **"apply to resume-quality signals only once A/B
receipts accumulate past N≥50 — today N=4; fitting now would be the cherry-picked-N violation,"**
with the retry condition shipped as part of the demo. That is the negative-evidence contract applied
before the mistake instead of after.

RED arm (a) — shuffled labels must yield "no signal found" and exit nonzero — is a genuine
fit-refusal arm, the thing most ML templates omit.

**Deductions.** Greenfield; no lane payoff until a corpus lands; and it converges with my CC-4, so
one of them is redundant. Pane 2's "no immediate lane payoff" is fair — I raise the score because
the refusal gate is transferable doctrine regardless of when the corpus arrives.

## MU-2 — admission screen hook · **620** (COD: 470)

**Pane 2's finding is correct and important:** asking Jev *"does this content carry credential
material"* requires shipping the raw bytes — including the credential — to a third-party API. The
hook would leak precisely what it exists to protect. The file even shows awareness of secret
hygiene in its *tests* (plants assembled at runtime, mirroring gate `30-no-secrets`) while the
*production* path sends the real thing.

**But I score it 150 above pane 2, because the defect is one deletable branch, not the design.**
The fix is not "screen credentials more carefully" — it is:
- **delete the credential question entirely.** A local deterministic detector (the
  `30-no-secrets` pattern set) runs first, redacts, and nothing containing a secret is ever sent.
- keep the **injection** question, which is the 0.99-witness capability and does not require
  sending our secrets — only the untrusted inbound bytes, which is the point.

Pane 2's own steelman (`ad4c1d0`) reaches the same conclusion — *"better than its unsafe
implementation, and the defect is fixable rather than structural"* — which means the 470 grades the
implementation and the steelman grades the idea. Both are right; the score should say which it is.

**This is the duel's most valuable exchange:** the same demo scored 880 (CC-5, pane 3) and 470
(MU-2, pane 2). The 410-point gap is not model noise — it is one file having a credential branch
and the other not. **The merged implementation must be CC-5's injection-only scope with MU-2's
install rigor** (idempotent, refuses when the hook dir is undiscoverable — the
`.omp/hooks/`-without-`pre/` silent miss is a named install check, which my file lacked).

---

## NO-CLAIM

Judgment only. I ran nothing: no harness, no live call, no corpus. I am the author of the competing
file and therefore an interested grader — pane 2's MU scores are the arms-length ones and should
outweigh mine where we disagree. CC still has only one grader; nothing here scores CC. The
convergence table is derived from the two idea files as written, not from any similarity measure.

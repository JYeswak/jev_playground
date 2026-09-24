# Pane 4 (MistyTurtle) - skillranker#4 closed as fixed: dogfood, then one receipt reply

From pane 1 AmberWillow, 2026-09-24. Bead `jev-jwr` (tracking skillranker#4). Skill:
`skill://jeff-issue-chain`, Phase 3 (CLOSED with fix shipped) and Phase 4 (follow-up reply).

## 1. Mission

Validate Jev -> build tools -> liven omp surfaces -> dogfood -> share publicly (AGENTS.md "THE
MISSION"). This unit keeps the upstream relationship honest: Jeffrey fixed something we reported,
and he has not heard whether it worked for us.

## 2. Why you, and the rule you work under

- Pane 1 runs an Anthropic model and skillranker is a Dicklesworthstone repo, so AGENTS.md rule 14
  (rider-covered repos) keeps pane 1 out of it. You run a Meta model; you are outside the rider.
- Joshua, 2026-09-24: "approval on all - any upstream issues on repos that aren't ours needs to
  follow" the jeff-issue-chain. That approves one reply here, only if the chain is satisfied.
- Joshua's standing skillranker rule: findings come only from native binary downloads. skillranker
  has no releases (checked 2026-09-24 01:50Z). So this unit may **confirm** the fix. It may **not**
  report any new defect found in a source build. If the dogfood shows the fix does not work, post
  nothing and call back.

## 3. Facts

- skillranker#4 "One symlinked skill dir empties the whole roster" (ours, filed 2026-09-20).
  Jeffrey closed it 2026-09-23T17:53Z: fixed in `73b7ad1`, then `89f7abf` (CLI coverage), `8fa6869`,
  `fab0f38`, `20d3ec6`. Read his whole comment: `gh issue view 4 -R Dicklesworthstone/skillranker --comments`.
- Our last retest built sr at `b9e8b342` as a Mach-O arm64 cross-build on contabo via the zigcc
  recipe (our comment of 2026-09-21T00:41Z has the recipe and the three arms). Upstream HEAD
  2026-09-24T01:46Z: `2a16486`.

## 4. Steps

1. `br update jev-jwr --status in_progress --assignee MistyTurtle`.
2. Build sr at the current tip with the same recipe (Rust only via RCH, no local cargo). Record
   the SHA you built.
3. Rerun the same three arms from the issue's repro, verbatim, clean-room (`mktemp -d` under the
   RCH canonical root). The discriminator is the one in the issue: the same store with and without
   one symlinked skill dir.
4. Receipt: `docs/demos/upstream-repro/skillranker4-dogfood-20260924.md` with the built SHA, the
   commands, and each arm's verbatim output.
5. If all arms show the fix: draft the reply in `notes/deep/skillranker4-reply-draft.md` per
   jeff-issue-chain Phase 4. 3-6 short paragraphs. Address him as "Jeffrey", name what landed with
   one specific call-out citing his commit and file:line, give the dogfood result with the built SHA,
   no internal bead IDs, paths or session names, no "amazing work", and no new asks. Do NOT post it.
6. Callback to pane 1; pane 1 reads the draft and posts it.

## 5. Callback

`CALLBACK-P4-SR4-DOGFOOD-DONE` via `ntm send jev --pane=1`: built SHA, three arms with results,
receipt commit, draft path, NO-CLAIM. Separately, leave `jev-k9z.1` open until pane 3's re-score
lands, then write its NEGATIVE_EVIDENCE row (bar failed: 75/219 vs lexical 71/219) with a retry
condition, and close it with the receipt cited.

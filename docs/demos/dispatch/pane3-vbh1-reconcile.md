# P3 (MUSE) — Reconcile `jev-vbh.1` against what §21 already shipped

You are the only pane that can receive right now: `ntm --robot-agent-health=jev` reports panes 1
and 2 `is_rate_limited: true` / `WAIT_FOR_RESET`, pane 3 `HEALTHY` / `safe_to_dispatch: true`.
Small unit, because I do not know when the others return.

## The question

`jev-vbh.1` is "Skill: retransmit-killer (N=8–10 loop)". **Section 21 already ran that ground and
REJECTED adoption**, shipping real artifacts in the process:

- `work/jev-retransmit-killer/SKILL.md`
- `work/jev-retransmit-killer/adopt-gate.mjs` + `adopt-gate.test.mjs` (5 tests, exits rc=0 today)
- `docs/RULES.md` rules 1 and 2, both sourced from that section

Measured there, and not to be re-derived: `perfect` (an omniscient judge) saved 20.8–31.0% against
a preregistered 50% bar → **REJECT on 12 of 12 real sessions**, so no real policy can clear it and
`keep_p` is irrelevant to the decision rather than mistuned. `drop-largest` saved 71.3–88.3% while
losing 28.3–35.8% of substantive reuse.

**So running an 8–10 pass authoring loop on this skill would re-derive a conclusion we already
hold.** That is the §5 lesson (search before invent) and the §21 lesson (compute the ceiling
first) pointing the same way.

## Your unit — one of three outcomes, all acceptable

1. **CLOSE `jev-vbh.1` as satisfied** by §21's artifacts, with a comment naming which artifact
   covers which part of the bead's WHAT/WHY/ACCEPTANCE.
2. **RESCOPE it to the delta** — the part §21 did NOT cover — and say exactly what that is. My
   read: §21 produced a REJECT and a gate that keeps the rejection honest, but no *skill* in the
   `/repeatedly-apply-skill` sense. If the delta is real, name it in one sentence.
3. **REFUSE with a trigger** if neither fits.

Read before deciding: `work/jev-retransmit-killer/SKILL.md`, `NEGATIVE_EVIDENCE.md` R44 (note the
renumber — a peer holds R41), and `docs/demos/upstream-repro/commit-learnings-20260919.md` §21.

## Constraints

- **Do not run the ceiling measurement again.** It cost 12 sessions of 167–338MB and its answer
  does not depend on the candidate.
- No savings number without its paired retention number (`docs/RULES.md` rule 2).
- **Commit on create** — staging is not protection; three files were lost or nearly lost to
  branch switches tonight.
- Test file + `TESTS.md` entry in the same commit, facts derived by running the file alone.
- Exit codes unpiped. No Codex.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-VBH1-<CLOSED|RESCOPED|REFUSED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

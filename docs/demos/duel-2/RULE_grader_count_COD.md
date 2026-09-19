# Q71 Rule: Grader Counts Must Count Actors

**Decision:** retain the underlying score observations, but retire the phrase “4 graders” as an actor claim. The receipts support score-entry counts; they do not support four distinct grading actors.

## Receipt findings

The §5 counts are means over score observations, not verified actor counts:

| §5 claim | Score observations supporting the mean | Actor attribution supported by opened receipts |
|---|---:|---|
| demo-1 §5.1: “4 graders, range 830–875” | 4: CC-3 scored 840/830; MU-1 scored 875/870 | pane 2/COD: verified for two entries; pane 3/MU: verified for one; pane 1/CC: claimed by the score prose but not independently attested |
| demo-2 §5.2: “2 graders” | 2: CC-5 scored 855/880 | pane 2/COD and pane 3/MU are supported by the cross-score dispatches and receipts |
| demo-7 §5.7: “4 graders” | 4: CC-4 scored 710/800; MU-5 scored 640/700 | pane 2/COD: verified for two entries; pane 3/MU: verified for one; pane 1/CC: claimed but not independently attested |
| P2 duel-1 summary: “20 grader scores” | 20 score observations across the two lineages × five ideas | 20 is an observation count, not 20 distinct actors |

The arithmetic explains the means. Demo-1's four observations average to 853.75, shown as 853.8; demo-7's four average to 712.5; demo-2's two CC-5 observations average to 867.5. Those calculations do not establish who produced each observation.

## Actor evidence and contradiction

### Verified pane 2 / COD actor

`docs/demos/duel-1/dispatch/pane2-score-MU.md` assigns pane 2 to score the MU file as the non-author, different-lineage grader. `WIZARD_SCORES_COD_ON_MU.md` describes that role and its scores. The Q22 mapping independently supports pane 2 ↔ COD.

### Verified pane 3 / MU actor

`docs/demos/duel-1/dispatch/pane3-score-CC.md` assigns pane 3 to score the CC file as the non-author, different-lineage grader. `WIZARD_SCORES_MU_ON_CC.md` explicitly identifies the grader as CopperCarp, pane 3. The Q22 mapping supports pane 3 ↔ MU.

### Pane 1 / CC score claim is unresolved

`WIZARD_SCORES_CC_ON_MU.md` presents “CC (Claude, pane 1) scores MUSE ideas” and the PLAN says the conductor scored MU. But the opened dispatch says pane 1 is **not** grading, and `runs/pane1-cc-20260918T000328Z.json` is an actor receipt for authoring `WIZARD_IDEAS_CC.md` whose `no_claim` explicitly says “NOT scored: neither file cross-scored.” No receipt binds pane 1 to the CC-on-MU score artifact as a scoring action.

Therefore pane 1 is **conductor-claimed / unverified**, not a verified fourth grader. The score file is a content assertion, not sufficient actor provenance. This is exactly the claim shape the lane refuses to accept from conductor testimony alone.

## Ruling on the §5 claims

- “4 graders” must be replaced with **“4 score observations from two verified pane actors plus one unresolved conductor-claimed score surface”** for demo-1 and demo-7.
- “2 graders” for demo-2 is supportable as **two score observations from pane 2 and pane 3**, provided the row cites the two receipts; it should still say “2 score observations” when actor identity is not the object being measured.
- “20 grader scores” should be restated as **20 score observations**. It must not imply 20 distinct actors or consensus.
- The means may remain as arithmetic summaries only if the underlying score observations remain linked. They are not proof of four independent graders.
- The broad §5 sentence “every other demo carries two to four grader scores” is a count of observations at best; it is not an actor census and cannot support a non-author gate without per-receipt actor fields.

## Transfer from Q64/Q21

The retirement reasoning transfers only partly. As with prose means and integer prose, a count lacking a stable authority field must not be used as a gate input. Unlike prose scores, the score observations are valuable and should not be deleted. Preserve the observations, add actor provenance, and retire only the unsupported actor-count wording.

This is not a filename inference: the pane assignments above come from opened dispatch instructions, explicit receipt text, and the pane-1 author receipt. The score filenames are not used as proof.

## Required schema

Every score receipt used in a grader count must carry:

```json
{
  "receipt_type": "score",
  "candidate_or_idea_ids": ["..."],
  "grader_actor": "pane2 | pane3 | pane1 | unknown",
  "grader_lineage": "COD | MU | CC | unknown",
  "target_author_actor": "...",
  "actor_evidence": "receipt or dispatch path plus revision",
  "score_observations": 5
}
```

`grader_actor=unknown` fails closed for a claim of distinct-actor count. It may remain in the observation mean with an explicit unresolved-attribution marker, but it cannot satisfy a non-author gate.

## Re-examination condition

Re-examine this rule when:

- a score receipt gains explicit actor, lineage, target-author, and revision fields;
- pane 1 supplies an actor receipt that reconciles the CC-on-MU score with its “not scored” author receipt;
- a new score is added or an existing score changes;
- a claim of distinct graders is used to clear a rung or assert consensus.

Until then, state score-entry counts and verified actor counts separately.

## Scope

This ruling does not invalidate the arithmetic means or the score files as judgment work. It rejects only the unsupported inference from four observations to four distinct graders. No consensus, four-actor composition, or rung-1 gate clearance is claimed.

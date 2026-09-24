# README live-smoke cells, recomputed from receipt rows (2026-09-24)

ReadmeStrangerRun, keyless, no API call. Each cell in the README demo table says how many calls the
demo's `--live` run made and whether the live model decided the same way as the recorded fixture.
Before registering those cells as claims, each was recomputed rather than copied from a receipt's
`compared_to_fixture` sentence.

**Re-score:** `python3 work/readme-stranger-run/live-cells.py` (needs `./scripts/bootstrap-compaction.sh`
once, for the compact demo). It reads each `demos/<name>/live-receipt.json` and runs the demo's
recorded lane keyless, then compares item by item.

**Rule.** An item differs when any categorical decision the demo prints for it differs between the
two lanes: a route, action, verdict, pick or label. Probabilities and scores alone never count. A
demo is *same* when no item differs, and *not compared* when the two lanes did not judge the same
input. Calls come from the receipt's own count (`call_count`, or `calls` for guard), which each
receipt defines as one Jev request.

| demo | calls | verdict | items that differ (fixture -> live) |
|---|---:|---|---|
| guard | 4 | differs, 3 of 4 same | dosage: review -> block |
| rag | 5 | differs, 4 of 5 same | sessions-01: ('conflicting_evidence', 'keep') -> ('exclude', 'drop') |
| citation | 4 | differs, 4 of 5 same | shipping_free: ('says_nothing', 'unsupported', 'review') -> ('contradicts', 'contradicted', 'review') |
| skill-suggest | 6 | same, 3 of 3 | - |
| chief | 4 | differs, 3 of 4 same | vague-ask: ('review', 'write') -> ('research', 'research') |
| rerank | 10 | same, 2 of 2 | - |
| date | 6 | differs, 5 of 6 same | kickoff call: none -> 2026-08-14 |
| entity | 4 | same, 4 of 4 | - |
| hierarchy | 10 | differs, 1 of 2 same | pie-recipe: ('tech/gadgets', 'food/recipes/pie') -> ('food/recipes/pie', 'food/recipes/pie') |
| autoformat | 2 | differs, 0 of 1 same | joins,blocks: (2, 9) -> (1, 10) |
| semantic-find | 2 | same, 2 of 2 | - |
| preparsed | 4 | same, 7 of 7 | - |
| compact | 1 | differs, 1 of 3 same | t2: drop_result -> drop_call; t3: keep -> drop_call |
| parallel | 1 | same, 3 of 3 | - |
| cascade | 1 | differs, 1 of 3 same | location: escalate -> pass; registration_open_date: pass -> escalate |
| consistency | 3 | not compared | the recorded run's state was `post_id` only, so it judged none of the text the fixture was recorded on; the demo now sends it, re-record pending (jev-fbhe) |
| consistency-noul | 3 | not compared | the recorded run's state was `claim_id` only, so it judged none of the text the fixture was recorded on; the demo now sends it, re-record pending (jev-fbhe) |

Recomputed here: 17 demos, 9 differ, 6 same, 2 not compared; call counts range 1 to 10 calls.

The table above is the first pass. Its two *not compared* rows are superseded by the re-record at
the end of this file (jev-fbhe).

## What changed in the README

- **citation:** the cell said *not compared*. The receipt rows do compare: `shipping_free` was
  `says_nothing` / `unsupported` in the fixture and `contradicts` / `contradicted` live. Its action
  (review) is the same in both lanes, so the routing held and the judgement did not. Now *differs*.
- **entity:** the cell said *not compared*. All four outcomes match the fixture (assert sameAs,
  leave unlinked, curator queue twice). Now *same*.
- **consistency and consistency-noul stay *not compared*,** for a reason the README did not give:
  the runs behind their receipts sent only an id (`post_id`, `claim_id`), never the post or claim
  text the fixture's answers were recorded on, so those live answers judged no content. The demos
  now send the cookbook text (jev-s0f1, `demos/test/live-state.test.mjs`); the re-record that would
  let them be compared waits on credits (jev-fbhe).
- The table legend moves from 8 differ / 5 same / 4 not compared to 9 / 6 / 2.

## Boundary

The rule is mine. A reader who counts a changed score or a pointer on an unanswered query as a
difference gets different verdicts for entity (fruit-variant's name noul moved from 0.63 to 0.07,
same outcome) and semantic-find (the no-answer query pointed at L01 in the fixture and L04 live). The
receipts are single live runs of 1 to 10 calls; nothing here re-runs the model.

## Non-author check (pane 1 AmberWillow, with SnowyCreek's recompute), 2026-09-24

**Verdict: CONFIRMED.** `python3 work/readme-stranger-run/live-cells.py` exits 0 on pane 1's run and
prints the same 9 differ / 6 same / 2 not compared.

SnowyCreek (pane 3, grok) recomputed all 17 cells separately, without this script. It applied each
receipt's own `calls` rule to the receipt's structure (for example rerank, 2 queries x 5 pairs = 10),
and compared live rows with each demo's recorded answers (`demos/<name>/demo.mjs:line`).

- **Call counts:** all 17 match the README.
- **Verdicts:** every compared verdict agrees. That pass also reached the citation (*differs*) and
  entity (*same*) corrections on its own, having read the README cells from before this commit.

Its first pass had counted rows instead of calls (rerank 2, consistency 24). That pass was withdrawn,
and no README number changed on its strength.

It found two differences, both already stated above:

- **semantic-find:** the unanswered query's pointer (L01 fixture, L04 live). See Boundary.
- **consistency and consistency-noul:** the live pluralities differ from the fixture's, and this
  receipt keeps them *not compared* because the recorded state was an id only.

One counting difference does not change a verdict. For citation this receipt counts 5 items
(4 of 5 same). The recompute counts the 4 claims that carry a choice (3 of 4 same), leaving out
`power_ten`, which has no choice. Both say *differs*.

NO-CLAIM of this check: no model call was made, and no live receipt was re-recorded.

## Re-record of the two consistency demos (jev-fbhe), 2026-09-24

ReadmeStrangerRun. The two consistency demos now send the cookbook's post and claim in the cookbook's
state shape, with the cookbook's questions (jev-s0f1, jev-t6yt), so their live lanes were run again:
`node demos/consistency/demo.mjs --live` and `node demos/consistency-noul/demo.mjs --live`, model
`jev-1.13.0`, Jev calls only. A fetch-capturing preload counted 3 systemOne requests per demo, all
HTTP 200, every response resolving to `jev-1.13.0`; tokens 4,683 in / 1,244 out and 3,234 in / 765 out.
The new receipts (`demos/consistency/live-receipt.json`, `demos/consistency-noul/live-receipt.json`)
carry every repeat's distribution or noul; each was cross-checked against the demo's printed live
table before it was written. The old receipts are in git history and named in each `supersedes`.

`live-cells.py` now compares both item by item: each question's plurality in the recorded lane
against the live receipt's. The printed plurality can run into the last decision in the recorded
table, so the script splits it where the suffix equals the row's most common decision, the demos'
own `agreement()` rule, and stops if that split is not unique.

| demo | calls | verdict | items that differ (fixture -> live) |
|---|---:|---|---|
| guard | 4 | differs, 3 of 4 same | dosage: review -> block |
| rag | 5 | differs, 4 of 5 same | sessions-01: ('conflicting_evidence', 'keep') -> ('exclude', 'drop') |
| citation | 4 | differs, 4 of 5 same | shipping_free: ('says_nothing', 'unsupported', 'review') -> ('contradicts', 'contradicted', 'review') |
| skill-suggest | 6 | same, 3 of 3 | - |
| chief | 4 | differs, 3 of 4 same | vague-ask: ('review', 'write') -> ('research', 'research') |
| rerank | 10 | same, 2 of 2 | - |
| date | 6 | differs, 5 of 6 same | kickoff call: none -> 2026-08-14 |
| entity | 4 | same, 4 of 4 | - |
| hierarchy | 10 | differs, 1 of 2 same | pie-recipe: ('tech/gadgets', 'food/recipes/pie') -> ('food/recipes/pie', 'food/recipes/pie') |
| autoformat | 2 | differs, 0 of 1 same | joins,blocks: (2, 9) -> (1, 10) |
| semantic-find | 2 | same, 2 of 2 | - |
| preparsed | 4 | same, 7 of 7 | - |
| compact | 1 | differs, 1 of 3 same | t2: drop_result -> drop_call; t3: keep -> drop_call |
| parallel | 1 | same, 3 of 3 | - |
| cascade | 1 | differs, 1 of 3 same | location: escalate -> pass; registration_open_date: pass -> escalate |
| consistency | 3 | differs, 2 of 8 same | action: Remove -> Strike; category: Harass -> Violence; link_handling: RmLink -> uncertain; primary_risk: Harassment -> uncertain; queue: General -> Threat; severity: Medium -> High |
| consistency-noul | 3 | differs, 13 of 14 same | docs_sufficient: no -> uncertain |

Recomputed here: 17 demos, 11 differ, 6 same; call counts range 1 to 10 calls.

- **consistency:** differs on 6 of 8. Given the post's text, Jev reads the threat ("Come say it to
  my face ... I'll end your whole channel") as violence: category Violence, action Strike, queue
  Threat, severity High, where the fixture had harassment, Remove, General and Medium. Two questions
  fall below the 0.60 gate and go to review (primary_risk, link_handling). Target and review path
  match.
- **consistency-noul:** differs on 1 of 14. `docs_sufficient` is *uncertain* live (nouls 0.32, 0.29,
  0.30; 2 of 3 in the band) where the fixture said *no*. The other 13 pluralities match.
- The README tally moves from 9 differ / 6 same / 2 not compared to 11 differ / 6 same.

NO-CLAIM: one live run of 3 calls per demo, a direction, not a benchmark. The fixture's recorded
answers were not re-derived; they are what the demo ships.

# What `franken_alignment` says our operating model is missing `[receipt]`

Source: `/Volumes/ZestData/dicklesworthstone-mirror/franken_alignment` (mirrored, `9208598`),
README + `COMPREHENSIVE_PLAN_FOR_THE_DESIGN_OF_FRANKENALIGNMENT.md`. Found via the franken-harvest
MCP index, not by guessing — there is no `franken-alignment` checkout under `~/Developer`.

## The one idea that reorganises everything we did tonight

> *"One single composable artifact — the **`DecisionClosure`** — unifies the pipeline: the exact
> object that authorizes a live tool dispatch serves simultaneously as a tamper-evident incident
> record, a replayable counterfactual baseline, a calibration sample, and an automated
> regression test."*

**We produced all five of those tonight, as five separate artifacts, by hand, for every ruling:**

| franken_alignment role | what we hand-built, per ruling |
|---|---|
| authorization | the `STATUS.tsv` row (verdict + rung) |
| tamper-evident record | the receipt file + its pinned content digest |
| replayable baseline | the locked export / seeded sample (`f68bccdc`, n=138) |
| calibration sample | the pre-registered falsifier and whether it fired |
| regression test | a `scripts/selftest-*.sh` arm, when we remembered |

Five artifacts, five chances to drift — and they **did** drift: `STATUS.tsv` fell behind three
separate times tonight, a digest pointed at a live file and took the lane RED, and the README's
counts went stale twice. **Every one of those failures is a consistency failure between parts of
what should be one object.**

That is the gap, stated precisely: **we have the discipline and none of the composition.**

## What maps, what does not, and what we should refuse

| franken_alignment primitive | our state | honest verdict |
|---|---|---|
| `DecisionClosure` (one object, five roles) | five hand-maintained artifacts | **ADOPT the shape.** This is the fix for a defect class we hit 3× tonight. |
| Conserved rights (`held + available + spent == total`) | nothing | **Not applicable.** We authorize no live effects; our "dispatch" is a document. |
| Effect Gate / one-shot permits | nothing | **Not applicable** for the same reason — and pretending otherwise would be ceremony. |
| Graduated Autonomy Ledger (per-family grades, automatic demotion) | rungs 1–5 with promotion refused 45× | **Partially ours already.** Ours has no *demotion* rule: nothing automatically downgrades a claim when its evidence rots. The as-of work showed evidence rots. |
| Model Passport / identity liveness | nothing; we call `jev-latest` | **Real gap, cheap to close.** We pin fixtures but not the model epoch. The framing-flip numbers moved between sessions and we attributed it to sampling; a served-model change is an untested alternative. |
| Risk-Theater Detector (standing query over the control plane's own drift) | the honesty pass, run by hand every third tick | **Ours is the manual version.** It found USER 36→45→52→44%. A standing query is the mechanised form. |
| Commit–reveal congresses | non-author review, uncommitted | **Weak analogue.** Our reviewer sees our verdict before ruling — that is precisely the herd behaviour salted commit–reveal exists to prevent. |
| Progressive ATP, Z-sets, codecs, dominator trees | nothing | **Refuse.** No observed defect here justifies the machinery. |

## The three things worth doing, ranked by observed defect

1. **Emit one closure object per ruling.** A ruling writes *one* JSON that carries verdict,
   receipt digest, falsifier + whether it fired, the pinned input sha, and the guard results —
   and `STATUS.tsv` becomes a *projection* of that object rather than a parallel hand-edited
   file. Defect it fixes: **three same-turn-update failures and one RED, all tonight.**
2. **Add demotion to the rung ladder.** Today a rung-4 claim stays rung-4 while its denominators
   drift. The as-of audit proved `78,455` is unrecoverable; nothing demoted the claim that cited
   it. Demotion should be automatic when a cited input is live-monotonic and its as-of date is
   older than the claim's use.
3. **Pin the model epoch like we pin fixtures.** One line in the request record. We have
   measured output moving between runs and attributed it to sampling without ever ruling out a
   served-model change.

## NO-CLAIM

Read of a README and a plan at one revision; I ran none of its test suite and this repo shares
no code with it. The mapping is an argument about our practices, not a verified claim about
theirs. **Most of its machinery is correctly inapplicable to us** — we gate documents, not
irreversible effects — and adopting it wholesale would be the ceremony this lane refuses.

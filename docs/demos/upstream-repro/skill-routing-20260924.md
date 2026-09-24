# Skill routing on our own traffic: is there a corpus? (bead `jev-i8r`)

BillingUnits (background agent of pane 1), 2026-09-24. **Zero model calls.** The feasibility arm
below failed, so the bar's own stop rule ended the unit before any Jev or Haiku call.

## Order of work, stated so the bar can be judged

The pair counts were probed with throwaway scripts (no calls) before this bar was written. The
floor below comes from the power arithmetic in the next section, not from those counts, but a
reader should know the counts were visible when it was set. The harvester, the pair file and this
bar land in one commit, before any call.

## Corpus

`work/skill-routing/harvest.py`, cutoff `2026-09-24T03:00:00Z`. Scope and filters are
`work/bicameral-gate/real-sample.py`'s: every profile's `sessions/-Developer-jev`, subagent
transcripts included. The home directory is written as `~`. A pair is dropped if its prompt or
skill matches that file's `PRIVATE` or `SECRET` pattern; the patterns are read from its source,
not copied. Label: the first `read` of `skill://<name>` or `.../skills/<name>/SKILL.md` that the
agent made after a user message and before the next one.

Re-run: `python3 work/skill-routing/harvest.py` (writes `work/skill-routing/pairs.jsonl`, prints
the counts). Counts at the cutoff:

| Step | Count |
|---|---:|
| transcript files | 260 |
| user messages before the cutoff | 1,839 |
| followed by no skill read | 1,774 |
| followed by a skill read | 65 |
| dropped by `PRIVATE` | 3 |
| dropped by `SECRET` | 0 |
| duplicate (same prompt and skill, broadcast to several panes) | 6 |
| **pairs** | **56** |
| of which the prompt names the skill it led to | 26 |
| **unnamed pairs (the primary set)** | **30** |

26 distinct skills over the 56 pairs. Label distribution, all 56: prevalence-first 8,
zeststream-rch 7, typesafe-ai 4, jeff-issue-chain 4, planning-workflow 4, readme-update 3, ntm 3,
eidetic-engine-cli 2, statistical-analysis 2, vibing-with-ntm 2, dcg 2, and 15 skills once each.

Unnamed 30, 19 distinct skills: zeststream-rch 5; typesafe-ai, eidetic-engine-cli,
statistical-analysis, vibing-with-ntm, readme-update, dcg and prevalence-first 2 each; 11 skills
once each. Dates of the unnamed pairs: 09-18 1, 09-20 10, 09-21 3, 09-22 2, 09-23 10, 09-24 4.

## Bar (preregistered)

**Why unnamed only.** A prompt that contains the skill's name ("Read skill jeff-issue-chain
first", "/planning-workflow") is routed by a substring match. Scoring it would measure string
matching, not judgment. Named pairs would be reported separately, beside a substring baseline.

**Candidate set.** K = the skills with at least 5 unnamed pairs each, capped at 10, plus `none`
for every other label. Each option's text is the `description:` from that skill's SKILL.md
frontmatter.

**Arms, if run.** A Jev Choice pinned to `jev-1.13.0`. Haiku 4.5 through system-one-adapter on the
same Choice, recording `debug.probability_errors`. The frequency constant. Metrics: accuracy with
Wilson 95%, confidence-gated coverage, and exact McNemar for Jev against each other arm.

**Feasibility floor, checked before any call.** Both conditions must hold, or the unit stops with
zero calls:

1. **At least 100 unnamed pairs.** On a paired exact McNemar, `p < 0.05` needs at least 6
   discordant pairs with all of them one way (`2 x 0.5^6 = 0.031`). At N = 30 and a plausible 30%
   disagreement rate between two routers, there are about 9 discordant pairs. The smallest
   significant split is then 8 to 1: one arm would have to win 89% of their disagreements. A TIE
   at that N shows nothing. The Wilson half-width at N = 30, p = 0.5, is ±0.17. At N = 100 it is
   about ±0.10, and about 30 discordant pairs can resolve a 20 to 10 split.
2. **K ≥ 4.** At least four skills with 5 or more unnamed pairs each. Fewer, and the Choice is
   between `none` and one or two skills. That is a different question, "does this message need
   skill X", not routing.

## Result: feasibility FAILED, no calls made

| Condition | Needed | Measured |
|---|---:|---:|
| unnamed pairs | ≥ 100 | **30** |
| skills with ≥ 5 unnamed pairs (K) | ≥ 4 | **1** (zeststream-rch, 5) |

The unit stops here as the bar requires. Spend: 0 Jev calls, 0 Haiku calls.

**Other things the counts show:**
- Skill reads are rare in this lane: 65 of 1,839 user messages (3.5%) were followed by one. A router
  that must also decide "no skill" would face a 96.5% `none` base rate. That is a separate question,
  and a constant would be hard to beat on it.
- Nearly half the pairs (26 of 56) name the skill in the prompt. In this traffic, when a skill gets
  read it is usually because the prompt asked for it by name.
- This is the corpus that jev-k9z.3 lacked, and it is still too thin. At the observed rate, about 5
  unnamed pairs a day, 100 would take roughly 14 more days of this lane's traffic, if the rate held.
  K ≥ 4 is a separate condition that the rate does not guarantee.

**Retry condition.** Re-run `python3 work/skill-routing/harvest.py <new-cutoff>`. Run the arms
under this bar, unchanged, once it prints `unnamed ≥ 100` and at least four skills have 5 or more
unnamed pairs. Or widen the scope to other projects' transcripts, but only under a new privacy rule
committed first. real-sample.py's scope is jev-only on purpose.

## NO-CLAIM

- Nothing here says anything about Jev, Haiku or routing quality. No call was made.
- The label is a proxy: the first skill the agent chose to read, not the best skill for the message.
- The counts cover jev's own sessions before the cutoff. Transcripts from other projects, and any
  compacted or deleted before the harvest, are not in them.
- The duplicate rule keeps one copy of a message broadcast to several panes, even when two panes
  read the same skill.

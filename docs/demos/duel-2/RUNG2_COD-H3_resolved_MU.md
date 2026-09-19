# Q3 resolution — COD-H3 price-drift auditor: RULED OUT as a Jev demo, with two retry tracks

Status: resolution of the open structural question left in
`RUNG2_COD_HUNT_MU.md` (`e23251d`), which held H3 because its filed
Jev role (tier classification adjacent to a fixed table) was unproven.
This unit answers it. Verdict below: **RULED OUT in its filed Jev-demo
form, with two retry conditions** — one deterministic track outside
this lane, one Jev track facing router incumbents head-on.

## The question, restated without mercy

H3 claims two things at once: (1) auditing price/cache metadata is
valuable (verified: LiteLLM #38064 with runnable repro and measured
262% excess), and (2) the audit needs a Jev Choice classifying request
complexity for counterfactual tier comparison. The rung-2 question is
only ever (2): grant (1) entirely — the pain is real, the buyer exists
— and ask what, if anything, requires a judgment model.

Decompose the filed mechanism into its stages and sort each:

| Stage | Work | Needs Jev? |
|---|---|---|
| Parse price manifests + usage logs | structured reads, joins | No |
| Detect drift (manifest vs observed) | numeric comparison | No |
| Attribute effective cost per route/provider | arithmetic with cache semantics | No |
| Refuse unverifiable rows | null checks | No |
| Counterfactual tier comparison | **the only filed Jev role** | **Claimed, unproven** |

Four of five stages are deterministic, and the deterministic four are
also where 100% of the verified pain lives (#38064 is a ranking-arithmetic
bug: cache-read price unread + stable-sort tie-break — no judgment
anywhere in its causal chain). The single Jev stage classifies request
complexity so the counterfactual can name a tier. But tier assignment
for operator-owned model sets is served today by fixed capability
tables (model → tier, committed, versioned), exactly the instrument a
FinOps operator already maintains. The candidate never exhibits a
request the table misclassifies, a tier the table cannot name, or a
dollar figure that moves on the difference.

## The fork the candidate cannot avoid

Push on the one Jev stage and it resolves into exactly one of two
demos, neither of which is H3-as-filed:

**Fork A — the counterfactual needs judgment.** Then H3 answers "could
a cheaper tier have served *this* request," which is shadow routing:
per-request tier assignment against live traffic shape. That is a
realer product — and it competes directly with RouteLLM, Martian,
and LiteLLM's own cost routing, all maintained, all measured. The
candidate filed no such competition (its substitutes section names
them as neighbors, not rivals), named no wedge against a learned
router, and priced itself as an audit. Fork A survives only by
re-filing as a router with a router's burden of proof. Nothing in the
hunt file does that work.

**Fork B — the counterfactual does not need judgment.** Then the
fixed table classifies tiers, the deterministic core does everything
else, and the shipped artifact contains zero Jev calls. That artifact
is genuinely wanted (see #38064's repro: any operator would run it),
but this lane does not ship Jev-free tools — demo-1 established that
a valuable deterministic audit with no model in it belongs in lane
tooling or scripts, not in the demo backlog it just exited. Fork B
survives as *tooling*, explicitly not as demo-9's sibling.

H3-as-filed sits between the forks: too router-shaped to be pure
audit, too audit-shaped to face routers, with one Jev call mediating
a question a table answers. That is not a third position. It is the
absence of one.

## Ruling: RULED OUT with two retry tracks (structural, per §3c)

Neither track is taste; both are executable by whoever picks this up:

- **Retry T1 (deterministic auditor, outside the Jev lane):** build
  Fork B as lane tooling — manifest-vs-usage assertion with the
  #38064 repro as its first fixture. Success criterion predeclared:
  catches the tie-break misroute and one novel drift class on real
  manifests. No Jev call, no demo slot, no rung needed. If it works,
  every future routing discussion in this lane cites its numbers.
- **Retry T2 (counterfactual router, inside the lane):** re-file Fork
  A with a named wedge against RouteLLM/Martian on operator-owned
  traffic (e.g. calibration the routers cannot emit: per-decision
  probabilities with withhold on novel requests), plus the head-to-
  head fixture where fixed-tier rules misclassify at material cost
  that my rung-2 hold already demanded. That fixture is the price of
  re-entry; without it the Jev call is garnish.

If neither track is taken, H3 stays ruled out — correctly, because a
backlog that keeps a valuable non-Jev tool wearing one unproven Jev
call will eventually ship the demo-1 shape again (valuable, Jev-free,
mislabeled).

## What this ruling does and does not touch

Untouched: the #38064 pain (verified independently, real, deep buyer),
the auditor-not-router positioning insight, the confidence-interval
and refuse-unverifiable discipline in H3's receipt plan — all of that
transfers verbatim into T1. Untouched also: H3's rung-1 demand score
(890), which priced operator pain I reaffirm here; demand was never
the charge. Decided narrowly: H3-as-filed has no Jev-necessary stage,
and the lane rule from demo-1 (no Jev-free demos) plus the rung-2
rule (no garnish calls) jointly close its current form. The two
retries keep everything valuable; they just refuse to keep it in one
artifact.

## NO-CLAIM

Structural ruling on the filed mechanism. No auditor built, no
manifest parsed, no tier table tested, no router benchmarked. The
T1/T2 retries name the measurements that would reopen this; until
one runs, the ruling stands as stated.

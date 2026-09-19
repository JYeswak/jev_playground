# Duel 1 — reply, duelist B (muse) to CC's scores on MU (`32b7622`)

Grader-of-my-file's-grader. CC scored MU-1 870 · MU-3 820 · MU-4 800 ·
MU-5 700 · MU-2 620 against pane 2's 875 / 805 / 735 / 640 / 470. I rule
below on (a) each contested technical point, (b) the author-bias charge CC
asked me to check, and (c) what changes on my side. All line refs are to
`WIZARD_SCORES_CC_ON_MU.md` unless noted.

---

## Conceded (4.5 of 5)

**MU-2 at 620: agreed, and 620 is the operative number.** "The defect is one
deletable branch, not the design" (lines 113–118) matches the redesign I
already adopted in `WIZARD_REACTIONS_MU.md`: delete the credential question,
local deterministic prefilter first, injection branch proceeds. The 470
grades the implementation as written — unshippable, correctly floored. The
620 grades the idea minus one specified deletion. For backlog purposes only
the second number is usable, so 620 supersedes 470 going forward. CC's use
of pane 2's steelman is accurate — I checked: "better than its unsafe
implementation, and the defect is fixable rather than structural"
(`WIZARD_STEELMAN_COD.md:9-10`). No misquote.

**MU-1 "oracle proxy" → baseline: agreed, with interest.** "The served model
is the *incumbent's choice*" (lines 56–58) is sharper than my hedge: grading
a down-route as disagreement-with-oracle systematically favors the status
quo, which is the opposite of what a savings backtest is for. Adopting
"baseline" into the MU-1 spec. The price-table stale-risk deduction (lines
59–61, `as_of` + re-derivation path) is a valid hit my file did not take;
conceded as new.

**MU-3 label bias + concurrency: agreed.** Positives-only labels (lines
70–71) is a real defect in my calibration story — negatives sparse and
lagging means the judge's false-complete rate is unmeasurable until it
fails in production. Pane 2's handling — a follow-up bug is calibration
data, not invalidation — is the correct one; adopted. Pane 2's
concurrency point stands unchallenged by either of us.

**MU-4 extraction defect: already conceded last round** (my reactions §2) —
noting here that three lineages have now independently convicted the same
sentence ("extracts verifiable working points"): pane 2, CC (lines 82–85),
and the author. A claim with three independent convictions needs no further
trial; the deterministic-candidates + Choice + Noul treatment is the
sentence.

**MU-5 at 700: accepted.** It matches the number I argued in my reactions,
so disputing it would be disputing myself. Whether that is persuasion or
coincidence is unknowable from text (see bias ruling); the number is now
doubly supported either way.

## Author-bias ruling: genuine, not laundering — with the receipt

CC asked me to check whether raising MU scores raises CC by association.
Testable predictions of the laundering hypothesis, against the file:

1. *Inflation past CC equivalents.* Fails: MU-4 800 stays below my CC-2
   850; MU-5 700 below my CC-4 800; MU-2 620 below my CC-5 880. The one
   exception, MU-1 870 above my CC-3 830, was already ahead under *both*
   independent graders (COD 875) — CC moved it down a point, not up.
   Nowhere does an MU score cross its CC pair on CC's authority.
2. *Protection via rank preservation.* MU-5 → 700 exactly matches my argued
   number while preserving CC-4 > MU-5 order. Consistent with persuasion,
   also consistent with rank-preservation. Flagged, not charged:
   unresolvable from text, and the file's own deference instruction (see 4)
   prices it in.
3. *The MU-3 control.* MU-3 has **no CC equivalent** — nothing of CC's
   benefits from its 805 → 820. A protection strategy leaves it alone or
   trims it; CC raised it on a named technical merit (empty-diff arm) and
   would gain nothing by association. This is the observation most
   inconsistent with laundering.
4. *Costly signals.* "Pane 2's MU scores should outweigh mine where we
   disagree" (NO-CLAIM, lines 134–136) and gifting the merged claim-checker
   MU-4's withhold rule over their own CC-2's version (lines 87–89) both
   transfer credit *away* from CC. Protection strategies do not do this.

**Ruling:** the raises read as genuine technical judgments with the normal
interested-party discount — which CC already applied to themselves in the
NO-CLAIM. I accept the discount as priced: where CC and COD disagree on MU,
COD's number governs (so MU-2's operative score remains 470-as-written /
620-minus-branch, MU-5 640/700 likewise bracketed, per my Unit 1 framing).

## Pushback: the convergence inference overreaches (one each: major, minor)

**Major — "strong independent convergence" (lines 37–38) is shared-prior
determinism, not independent validation.** Both files were dealt the same
14-section map, the same lane context, the same receipts, and value-ordered
briefs. Two lineages picking the same four demos under identical priors
measures the *map's* determinism (good news for backlog legitimacy), not
the ideas' correctness. The file half-concedes this at lines 39–40
("disagreed sharply on the same ideas… localizes every real dispute to
implementation") — I keep that half and downgrade the other: convergence
selected the shortlist; only implementation disputes carry signal. Related
correction: the MU-2 ≡ CC-5 "yes" (line 31) needs the asterisk the 410-point
gap demands — same concept, materially different scope (credential branch
present vs absent). The table is right; the row should carry the scope
footnote.

**Minor — "best RED arm in either file" (MU-3 §, lines 65–66).** Empty-diff
⇒ human-needed is the most *concrete* arm, but CC-4/MU-5's self-falsifying
thesis arm ("verdict baseline must lose or refuse to report") guards against
a rarer failure: the demo's own obsolescence. Concrete-best vs
structural-best; I hold the latter, low stakes, recorded for synthesis.

## What changes on my side

Nothing numerical. My MU_ON_CC scores stand (CC-5's prefilter ship line was
already added last round, which this file's MU-2 § independently requires —
convergent requirement, keep it). The MU-1 "baseline" wording and
price-table `as_of` path are adopted into MU-1's future plan. MU-4's
extraction treatment was already adopted; CC's span-mismatch arm joins it.

## NO-CLAIM

Judgment on judgment. I built nothing, ran nothing, and did not re-read my
own ideas file for this unit beyond the lines CC cited. The bias ruling is
textual analysis of one file, not character evidence.

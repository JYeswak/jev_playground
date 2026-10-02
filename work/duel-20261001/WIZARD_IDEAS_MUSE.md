# Duel ideas — Muse (WindyLantern), 2026-10-01

Context read: AGENTS.md (600), README.md, expected.json (19 surfaces),
NEGATIVE_EVIDENCE R104–R133 headings, .omp hooks/extensions/tools,
EVAL.md tail (s47b re-seam, rud1 WITHHOLD, N2 0/48, nr3c 1h live).

Standing facts I refuse to re-litigate: skill-hint lexical+Choice is
VEIN-EXHAUSTED (R133) — idea 5 below is the *named retry condition*
(semantic matching), not a re-proposal. Gate-observe bash-risk is
NO-SIGNAL. Websearch-rerank is NO-BENEFIT. Claim rules retire below 0.80.
Smart stop is IDLE-BY-DESIGN (0 stops to catch).

## The 30 considered (one line each; cut reasons in the winnow notes)

1. DONE-callback verifier at session-stop (Noul over diff+bead acceptance).
2. Dead-rule kill-switch: RETIRED rules actually unload (125 wasted calls observed).
3. Commit-subject truthfulness (does `[test]` match evidence?).
4. CI failure triage: infra-flake vs code-fail (auto-retry only infra).
5. Cass hits reranked by proven top-1 Choice.
6. Semantic skill-hint retry (frankensearch shortlist + Choice; R133 retry clause).
7. Search-sufficiency gate (does this grep/find output answer it? stop searching).
8. Bead staleness flag (is this open bead still true given recent commits?).
9. Bead ACCEPTANCE auditor (command + planted negative + NO-CLAIM present?).
10. Fleet dispatcher (Choice: which idle pane gets the next bead).
11. Repurpose smart stop (detect unfinished-but-unsaid work at session end).
12. Needs-human: page vs checkpoint-and-park Choice (pages don't save time today).
13. Auto-thinking per-profile calibration from recorded picks.
14. TTSR precision janitor (scheduled u05b-style audits that propose retirements).
15. Cascade CUT calibration per command class on recorded rows.
16. Memory keep-side tuning (keeps are soft 0.51–0.97).
17. Nimble-cleared audit sample (rm-rf-nonexistent hole: cleared never sees paid).
18. Rerank-pick visibility audit (why 0 opens — is the pick even seen?).
19. Large-result spillover (inline answer vs file+summary Choice over result size).
20. Close-reason checker (claim_check on thin close reasons, 10t lineage).
21. Skill prefetch predictor — CUT: speculative, no measured pain.
22. Hook-latency meta-judge — CUT: ceremony, no consumer.
23. Hunk suspiciousness Score at pre-commit (which hunks need human eyes).
24. Jev test-selection vs ripwire --affected — CUT: deterministic incumbent wins.
25. Flaky-test Score from history — CUT: no history store exists.
26. Prompt-echo trimmer — MERGED into keep-tuning (idea 16 family).
27. Wedged-pane detector (spinner, no progress — beyond idle-watch).
28. Bead dependency-link suggester (bv hygiene).
29. Compaction guard (what must survive compact).
30. Universal cascade router: nimble-first for EVERY paid Jev call.

## Top 5, best first

### 1. Universal cascade router — generalize the 96%-free win to every paid call

**Decision (Jev/local):** local nimble Noul "is this worth a paid call?"
routes every outbound Jev question: clear-no → answer locally or skip;
uncertain/yes → paid jev-1.13.0. The gate cascade (jev-nr3c: 4/98 paid
in 1h live) proves the shape; today only the gate has it while
find/auto-thinking/judge/rerank/claim-check burn paid on every call.
**Seam:** one router in `kit/src/` + `work/jev-client`, injected transport
like every ported client; per-surface policy (threshold, safe side) in the
caller. **Metric (logs):** paid input tokens/day from session `model_usage`
rows with provider typesafe, split by purpose; replay quality on recorded
Q/A pairs per surface. **Bar (pre-registered):** paid tokens/day down ≥50%
with zero quality regression on each surface's held-out rows (same bars
that shipped them), fail-open on any local error. **Cost:** nimble is
local (loopback, $0); paid spend falls. At ~16k native calls/day the lane
pays ~$3/week today — this is the single biggest lever on that number.
**Planted negative:** a known-hard question (e.g. adversarial injection
rows, ambiguous claims) must route paid, never be answered locally.
**Why best:** it is the only idea that multiplies an already-measured
96% saving across every surface instead of inventing a new one; local-first
is the duel focus and this is literally local-first; risk is bounded
(fail open, per-surface bars, kill-switch per surface). Perception: agents
notice nothing except lower latency on easy calls. Implementation: port
the `liveLocalAsker` contract from gate-observe, add per-surface CUTs
calibrated on recorded rows (idea 15 folds in here), ship one surface at
a time behind the cascade-off file pattern.

### 2. DONE-callback verifier at session-stop — attack close-pump abuse at the seam where it pays

**Decision:** Noul "does this diff + the bead's ACCEPTANCE support a DONE
claim?" applied to DONE callbacks and bead closes. Close-pump abuse is
forbidden-pattern #7 and the most-cited integrity defect in the ledger
(thin close reasons, swept commits, unverified DONEs); the session-stop
hook already gives every worker one continuation, so the seam exists and
is free. **Seam:** `session-stop` post-hook (observe + challenge, never
block: a failing grade appends "UNVERIFIED: <missing evidence>" to the
callback instead of blocking it). **Metric (session files):** false-DONE
rate — sample DONE callbacks, blind-label whether the cited evidence meets
the bead's ACCEPTANCE, before/after. **Bar:** catches ≥80% of planted
false-DONEs (bead closed on a word, diff empty, tests unrun) at ≤5% false
challenges on genuinely complete beads, measured on 100 historical + 20
planted callbacks. **Cost:** ~1 short call per session end, ~50/day ×
~400 tokens ≈ $0.0008/day. **Planted negative:** a bead with green tests
and a receipt-citing close reason must pass unchallenged.
**Why second:** it defends the project's central integrity mechanism
(beads are the currency; fake DONEs debase it), it fires exactly where
agents are tempted to cut corners, and a challenge (not a block) keeps it
fail-safe. Perception: workers see an occasional "prove it" note naming
the missing artifact — annoying only when cutting corners. Implementation:
reuse the claim_check question shape on (diff stat + test output +
ACCEPTANCE text); log every challenge to the gate log for precision audit.

### 3. Dead-rule kill-switch + precision janitor — stop paying for retired rules

**Decision (mostly deterministic, Jev for the audit half):** (a) a loader
that refuses rules under `.omp/rules/disabled/` even when referenced —
today retirement is advisory and `claim-without-evidence` fired 125×
*after* retirement; (b) a scheduled u05b-style census (census + blind
labels on sampled firings) that proposes the next retirements.
**Seam:** (a) rule loader/hook bootstrap (one check, no model);
(b) weekly script + bead. **Metric (logs):** `ttsr` model_usage rows per
disabled rule → 0 within 24h of retirement; proposed retirements adopted.
**Bar:** (a) 0 firings from disabled rules over 7d post-ship, verified
from session files; (b) each proposal carries N, precision + Wilson
bounds, and a planted-negative check before filing. **Cost:** (a) $0;
(b) labeling is keyless (session files), ~$0. **Planted negative:** a
0.90-precision rule survives the janitor untouched; a disabled rule
referenced by name loads nothing and logs the refusal.
**Why third:** it is the highest-ROI line in the ledger — pure waste,
already measured (125 calls), fixable deterministically with a Jev-powered
audit loop. Perception: nobody notices except pane 1's spend line going
down. Implementation: gate the loader on the disabled/ path (fail closed:
unknown rule → refuse), and calendar the census as a bead with the u05b
method pinned. Anti-ceremony note: the janitor ships only because its
consumer (the kill-switch + spend line) and retirement condition
(precision < 0.80, R130/R132 precedent) already exist.

### 4. Commit-subject truthfulness — extend proven claim_check to the one claim every commit makes

**Decision:** Noul "does this diff + test output support the verification
level in the commit subject?" Every commit here must name a level
(`pending`…`live`); the commit-msg hook enforces *format*, not *truth*.
A `[test]` subject on an unrun suite is close-pump abuse wearing a uniform.
**Seam:** pre-commit/commit-msg hook, advisory (append `UNVERIFIED` trailer
suggestion, never block — blocking commits on a model's opinion would be
worse than the disease). **Metric:** blind-labeled agreement on 100
commits (subject level vs evidence in diff/test output), before/after
challenge rate on inflated subjects. **Bar:** precision ≥0.80 on
"inflated" challenges with ≤5% false challenges on honest commits,
pre-registered; fail open always. **Cost:** ~20 commits/day × ~600 tokens
≈ $0.0005/day. **Planted negative:** a commit with green test output and
a `[test]` subject passes silently; a `[live]` subject with no live
evidence gets challenged.
**Why fourth:** it closes the exact gap the repo's own rules created
(mandated subjects, unverified content), reuses the shipped claim_check
question family, and costs nearly nothing. Perception: authors see a rare
"subject says test, I see no test output" note — the honest majority never
hears from it. Implementation: feed (subject, diff stat, test-output tail)
to the claim_check seat; log challenges for the same precision audit as
idea 2. Demotion path is clean: if precision < 0.80 it joins R130/R132.

### 5. Semantic skill-hint retry — the R133-named retry condition, not a re-proposal

**Decision:** Choice over a *semantic* shortlist (frankensearch
TwoTierSearcher embeddings over skill name+description, a repo-local
capability) with the existing Choice stage + 0.5 cut unchanged; hint iff
the winner beats 'none'. R131/R133 explicitly leave this door open
("without a semantic-matching design" / "recall design"); every
lexical variant is dead, so this tests the one unconsumed hypothesis.
**Seam:** the parked `jev-skill-hint` extension, OFF until the bar passes.
**Metric:** the committed per-row dev set the conductor specified:
≥25% hint rate AND 0 misroutes, both directions tested, extension
provably loading in a fresh session (L3). **Bar (pre-registered):** exactly
that predicate, no weakening; misroute = hint on a must-not-misroute row.
**Cost:** shortlist is local embeddings ($0); Choice only on ≤20
candidates, bounded/day like every hook. **Planted negative:** "what time
is it" and the request-hog must-not-misroute row stay silent.
**Why fifth:** it is the only parked vein whose ledger entry names its own
resurrection condition, the infrastructure (frankensearch) already exists
in our skills, and the downside is capped (stays OFF unless it passes).
Ranked last because its predecessors failed four times (H1, cut-0.7, N1,
N2: 0/48 hints at 0 misroutes) — confidence is lower than ideas 1–4 even
though the design space is genuinely new. Perception if it ships: agents
get useful skill pointers instead of silence; if it fails it costs one
ledger row (R134) and the extension stays OFF.

## Winnow notes (why the rest lost)

Cass-rerank and search-sufficiency are sound but smaller than idea 1's
multiplier and idea 7 needs a success oracle we don't have. CI triage is
good but our CI pain is registry-sync (deterministic), not flakes.
Dispatcher, staleness flags, acceptance auditors, and close-reason checkers
serve the conductor, not the mission's cost/speed axis, and three of them
smell like process-porn without a gated defect. Memory keep-tuning and the
cleared-sample audit are follow-ups, not ideas — file them as beads under
the existing surfaces. Smart-stop repurposing and pick-visibility audits
chase surfaces measured at zero. Test-selection and flaky-scores lose to
deterministic incumbents (ripwire) or missing stores. Everything else was
speculative (no measured pain) or ceremony (no consumer).

# Duel-2 hunt (muse) — replacements from other people's pain

Method: hunted where the nine came from inverted — not our compaction,
our claims, our beads, but other populations' voiced pain, then kept only
what Jev primitives do and chat models do poorly (typed, cheap, repeatable
judgment at volume with calibration; never generation). 16 prior searches
fed Unit 1; 4 more here (TODO/debt discourse, doc-drift discourse) plus 2
throttled attempts disclosed below. Three candidates, all scoring at or
above the best surviving original (demo-4, 800).

## Ranked table (hunted + survivors)

| Candidate | Demand | Who downloads it | What it replaces |
|---|---|---:|---|
| H1 stale-TODO truth judge | 900 | Any engineer inheriting a codebase | Age-trackers + folk wisdom |
| H2 doc-drift judge | 850 | Team whose docs caused an incident | Doc generators + audit playbooks |
| H3 sanitize-before-send | 820 | Agent-harness builder under an enterprise ban threat | Hope + post-hoc scanning |
| (demo-4 foreman-lite) | 800 | — | — |
| (demo-5 fact ledger) | 750 | — | — |

**Headline, as ordered:** H1 beats every one of the nine. The duel-1
backlog — built entirely from our pain — missed the strongest demand
idea, which lives in everybody's codebase and needs no model call to
motivate.

---

## H1 — stale-TODO truth judge — 900

**The pain, voiced.** "TODO comments feel like a plan. They're debt you
forgot you owed. Most teams have hundreds in production — and zero of them
tracked" (deviera.dev, 2026). "Every TODO in your codebase is lying about
its age" (progressiverobot/itoverdose, 2026 — spawned two CLI tools).
"Comment rot: the underlying logic changes but the explanation stays"
(deska.dev, 2026). TodoTracker: acknowledged debt "does not stay
invisible until" someone trips on it. This is not a hypothesized pain;
it is a genre.
**What exists (searched):** todoage and todo-drift (age via `git blame`,
zero-deps CLIs), TodoTracker (tracking dashboards), aikido's rule
(delete-before-merge policy). Every incumbent answers *how old* or *where
listed*. **None answers whether the TODO is still true** — and age is not
truth (a 5-year TODO can be valid; a week-old one already done). The
judgment niche is unowned.
**The demo.** One bin over a repo: enumerate TODO/FIXME/HACK with
surrounding code + blame age as *context*, then one Noul each — "this
marker is still accurate about the code around it" — emitting
stale/valid/uncertain with probabilities plus a worklist ordered by
confidence. Deterministic enumeration first (the stage-1 lesson, honored:
Jev judges candidates, never finds them).
**The six bars:** (1) stranger installs once, runs on shipped fixtures
including a repo with 200 seeded markers; (2) population is every
codebase on earth; (3) voices linked above, four independent; (4)
before: N markers of unknown truth; after: precision/recall against
human labels on a sampled set, command `todo-judge audit --sample 50`
reproduces both; (5) searched above — age-trackers and dashboards,
none judging truth; (6) a chat model cannot do this well because the
value is *calibrated batch judgment with a receipt over hundreds of
markers*, not one clever answer — prompting per-TODO has no threshold,
no comparability, no audit trail.
**Why 900:** loudest pain-to-incumbent gap in this file, universal
audience, cheapest per-unit cost in the set (short Nouls), mechanism
fully specified with the extraction trap visibly avoided.

## H2 — doc-drift judge — 850

**The pain, voiced, with incident receipts.** "Stale docs are a liability:
they cause more harm than having no docs at all" (repowise.dev).
"Outdated documentation causes real incidents — a dev following stale
docs deployed a misconfigured service" (thecodeforge.io). "The hidden
tax on every engineering team" in onboarding time (vizrepo.com).
"Static documentation drifts from your code within weeks" (jamdesk.com).
**What exists (searched):** generators (pushpen AI auto-update, mintlify,
swimm-style sync) that *rewrite* docs, and audit playbooks (datadef,
scribelet 30-day plans) that are *manual*. Nobody ships "does this doc
block match this code" as a calibrated gate. Generation without judgment
is how confident-sounding stale docs get *fresher-looking and still
wrong* — the judge is the missing half of every generator on the market.
**The demo.** Pair doc blocks to code units deterministically (paths,
symbols, fence references — the matching stage, owned and tested), then
Noul per pair ("the doc accurately describes the code"), emitting
drifted/accurate/uncertain with a per-file report. Explicitly not a
rewriter.
**The six bars:** (1) one bin, shipped fixture repo with seeded drift;
(2) every team with docs (which is every team with incidents);
(3) voices linked above, four independent including an incident
post-mortem; (4) before: drifted-block count unknown; after:
precision/recall vs human labels, `docjudge audit` reproduces both;
(5) searched above — generators rewrite, playbooks advise, none judge;
(6) chat-model diff-reading per file has no threshold, no receipt, no
comparability across runs — the product is the *calibrated gate*, not
the reading.
**Why 850 not 900:** the pairing stage (which doc block belongs to which
code) is a harder mechanism than TODO enumeration, and the file admits
it — one notch for mechanism risk neither H1 nor the receipt can retire
in advance.

## H3 — sanitize-before-send (outbound redaction layer) — 820

**The pain, duel-proven first.** Our own lane nearly shipped the MU-2
leak: a hook that would have sent live credentials to a third-party API
to decide whether they were credentials, with green tests certifying it.
Three lineages converged on the remedy (local deterministic boundary
before any Jev call). The lane secrets rule and the duel post-mortem are
voiced operator pain with commit hashes attached — stronger than a forum
post for *our* purposes, weaker for sizing the external market.
**What exists:** deterministic secret scanners own *repos* (gitleaks
instant/offline pre-commit standard, trufflehog verified live secrets,
GitHub scanning zero-friction). None owns the *agent-to-model* boundary:
bytes already past commit-time scanning, arriving at runtime in tool
outputs about to cross into a paid API call. Adjacent PII-redaction APIs
exist for the general problem; none is harness-native with span-preserving
redaction tuned for downstream classification.
**The demo.** Drop-in sanitizing transport for any Jev client: pattern +
entropy prefilter, fixed-token redaction, per-call redaction counts,
fail-closed on detector error, receipt recording which bytes Jev saw.
**The six bars:** (1) one import swap, synthetic fixture loop offline;
(2) every team running agents under enterprise data rules; (3) VOICE GAP
DISCLOSED: external press links unverified — two search batches throttled
(datacenter-egress bot walls, recorded). Lane-internal voice (secrets
rule, duel finding with shas) carries the bar provisionally;
(4) before: secret-shaped bytes crossing per 1k calls (measured by the
transport's own counters); after: zero with redaction counts,
`sanitize --audit` reproduces both; (5) repo scanners searched and
distinguished (different boundary); PII-API adjacency flagged unverified
for the same throttle reason; (6) no chat model involved at all — the
whole point is bytes must *not* reach a model unredacted.
**Why 820, capped:** bars 1, 2, 4, 5(cited portion), 6 clear; bar 3
rests on lane-internal voice plus two named unverified externals. A
single successful press-citation run lifts this to 900+; as written the
cap stays. (Also recorded: §5.9's kill rationale misidentifies this as
MU-R9/CC-#5 — review lane vs inbound screen vs outbound redaction are
three demos; see DEMAND_RANK_MU.md demo-8 ruling.)

## NO-CLAIM

No §3b read. Four hunt searches completed (TODO/debt ×2 batches,
doc-drift ×2); two further batches (secret-incident press, PII-redaction
vendors) throttled at the provider level — claims depending on them are
capped above, not asserted. No interviews, no market sizing beyond
audience-shape reasoning, no implementation. Scores are demand judgments
against cited voices, not measurements of adoption.

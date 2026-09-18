# Duel-2 rung 2 — JEV shape on COD-H1…H5 (non-author: pane 3 muse)

Status: structural reasoning only. Candidates: COD-H1…H5 from
`docs/demos/duel-2/DEMAND_HUNT_COD.md` (`c33cd3c`). My rung-1 scores:
H1 885 / H2 905 / H4 900 / H5 895 / H3 890 (`HUNT_SCORES_MU_ON_COD.md`,
`ead8119`). No contract, pane-2 file, `PLAN.md`, or demo implementation
was edited. No Jev call was run.

## Rung-2 rule (as worked in RUNG2_JEV_SHAPE_COD.md and RUNG2_MUH1_COD.md)

Noul answers a supplied question with a typed verdict and probability.
Choice selects one member from caller-supplied candidates. Neither
generates prose, extracts facts, summarizes, invents an option, or
chooses unbounded answers. The command may format a receipt around judged
values; the model must not author the receipt's evidence. "Calibrated"
below means the contract has a probability-bearing typed judgment shape;
empirical calibration is later measurement, not permission to turn a
missing shape into a pass. A fixed chat rubric can recover syntax and
some comparability — the honest finding is usually "recovers syntax, not
calibration" — so each section tests the chat-model claim rather than
accepting it.

## Summary

| Candidate | Noul judgment | Choice selection | Hidden generation/extraction? | Rung-2 verdict |
|---|---|---|---|---|
| H2 abstention evaluator | Action licensed by evidence | pass/clarify/gather/abstain/escalate/block (supplied) | No, provided risk assignment is explicit (condition) | **CLEARED** |
| H4 admission replay | Trust/action scope of a result | admit/sanitize/hold/block (supplied) | No; corpus authorship must be human (condition) | **CLEARED** |
| H5 compaction integrity | Provenance-span validity | Candidate fact vs source + explicit unknown | No, provided fact sets are fixture-authored (condition) | **CLEARED** |
| H1 completion evidence | Claim-evidence relation | None needed (minimal shape) | No, provided claim extraction is deterministic (condition) | **CLEARED** |
| H3 price-drift auditor | (thin — see below) | Tier classification (adjacent to a fixed table) | Opposite risk: too little Jev, not hidden generation | **HELD** |

H3 is the only non-clearance, and it is HELD with a retry condition, not
ruled out. No taste kills anywhere in this file.

---

## H2 — pre-action abstention evaluator — CLEARED

### 1. What Noul judges; what Choice chooses

Both shapes are needed here, and both are well-formed. Noul answers the
licensing question over supplied inputs: *"Given the proposed action, the
evidence references, and the declared risk level, is this action licensed
by the provided evidence?"* — true (licensed), false (not licensed),
withhold (evidence insufficient or ambiguous). Choice selects the
operational outcome from the caller-supplied finite set: `pass /
clarify / gather / abstain / escalate / block`. Neither call invents its
inputs: the proposed action, evidence references, and risk level arrive
from the deterministic harness, and the side-effect sink stays
deterministic behind the gate. The fake-sink fixture proves ordering
(no action before gate) without a live account, which is exactly the
property a prose gate could assert but never demonstrate.

One explicit condition: **risk assignment must be named.** If the caller
assigns risk from a policy table (deterministic), say so. If a model
assigns it, that assignment is itself a judgment needing its own typed
question — an unexamined risk number smuggled inside the evidence
envelope would be a hidden stage wearing a field name. Either design
clears; an unnamed one does not.

### 2. Why ordinary chat is measurably worse

Tested, not accepted. A fixed rubric (pinned prompt, schema-constrained
`{"decision": <enum>}`, recorded inputs) recovers syntactic comparability:
a chat model can emit `abstain` repeatably enough to count. What it does
not supply is (a) calibrated abstention probability tied to a coverage
policy (selective accuracy at stated coverage needs numbers that mean
something across runs), (b) mandatory withhold semantics when evidence
is missing rather than a confident guess, and (c) off-list refusal when
the situation matches none of the six outcomes. The receipt makes the
residual measurable: selective accuracy at coverage, abstention
precision/recall, risk-weighted utility, zero action-before-gate
violations. A chat gate can sound safe while abstaining universally
(their falsification section already names this: universal abstention
must not count as safe) — the typed contract is what makes that gaming
visible.

### 3. Extraction, generation, summarization audit

Clean provided the three inputs are supplied, not synthesized:
proposed action (caller-assembled from the agent's tool call, not
model-written), evidence as hashes/pointers with unavailable states
(never prose summaries of tool output — a summary stage here would
launder the very evidence the gate judges), risk level (per the
condition above). Forbidden: model-written evidence summaries, model-
generated paired fixtures presented as neutral (fixtures are test data
and may be model-assisted in drafting, but the should-act/should-
abstain labels must be human-committed), any gate output that rewrites
the action instead of selecting an outcome.

### 4. Verdict

**CLEARED**, conditional on explicit risk assignment. The sink-order
proof is deterministic, the two judgments are typed and finite, and the
falsification criteria (no universal-abstention gaming, no live account
needed for the first receipt) are already in the candidate.

---

## H4 — tool-result admission replay benchmark — CLEARED

### 1. What Noul judges; what Choice chooses

Noul checks typed trust/action scope of a supplied tool result
(*"may this result influence the next privileged action, and under what
scope"*); Choice returns one of `admit / sanitize / hold / block`,
caller-supplied, finite. The secret-non-disclosure fixture is a hard
design constraint carried over from the duel's central finding: neither
call receives raw secrets, enforced by deterministic redaction before
any Jev input is assembled.

### 2. Why ordinary chat is measurably worse

Same tested shape as H2: a rubric recovers the four outcome labels on
good days, but not calibrated scope probabilities, not mandatory hold
on ambiguous provenance, not off-list refusal when a result matches no
trained pattern. The receipt (held-out attack detection, benign
admission, safe-action preservation, block-before-side-effect rate,
provenance coverage, shadow-vs-enforce split) counts properties a prose
review cannot emit comparably. The "corpus doesn't exist yet" flag from
my rung-1 pass is **not a rung-2 problem**: the replay runner, metric
set, and provenance model are fully specifiable with zero fixtures in
hand. That flag belongs to rung 3 (proof cost), where I leave it.

### 3. Extraction, generation, summarization audit

The corpus is the audit surface. Requirement: corpus authorship must be
human/curated — ordinary data, hostile instructions, forged policy
text, mixed pages, secret-shaped values assembled as fixtures with
committed intent. A model-generated attack corpus would bake the
model's blind spots into the benchmark and then grade it perfect; that
is self-agreement, not measurement. Deterministic stages: replay runner,
shadow/block accounting, synthetic-sink ordering proof, receipt
assembly. Secret-shaped fixture values must be runtime-assembled (the
lane's no-secrets pattern), and the EVAL's "evaluator unavailable" case
must fail closed, never silently admit.

### 4. Verdict

**CLEARED**, conditional on human-authored corpus and deterministic
redaction pre-stage. Overlap with Demo-2 is managed, not hidden: Demo-2
is a hook, H4 is the benchmark that would grade it — complementary
artifacts, and H4's cross-framework replay is the broader of the two.

---

## H5 — compaction-boundary integrity benchmark — CLEARED

### 1. What Noul judges; what Choice chooses

Choice compares a candidate fact to the source transcript with an
explicit `unknown` candidate (no forced match); Noul checks that every
retained fact carries a valid provenance span for the current
compaction generation. Both well-formed; the `unknown` state does the
same work as `NONE` in the ledger design, refusing to convert absence
into retention.

### 2. Why ordinary chat is measurably worse

Standard residual: no calibrated retention probability, no mandatory
unknown, no off-list refusal when a "fact" matches nothing. Measurable
via retained-fact precision/recall against the fixture's known-answer
set and provenance-completeness counts. A prose summary of "what
survived compaction" is precisely the artifact under test and cannot
grade itself.

### 3. Extraction, generation, summarization audit

The load-bearing condition: **fact sets must be fixture-authored
(known answers), not model-extracted.** The fixture "puts an exact
requirement, decision, and constraint immediately before the boundary"
— that placement is human test design with a hardcoded expected
outcome, in the spirit of mutation operators. If a future version uses
a model to discover "the facts" in a transcript and then checks
retention of its own discoveries, that is the demo-5 defect returning
(unnamed extraction stage) and voids this clearance until bounded by
the deterministic-enumeration + Choice + Noul structure. Flush/ordering
metadata (generations, commit acknowledgments, retry ids) are
deterministic harness state, not judgments. Duplicate-retry and stale-
generation cases must be counted, never narrated.

### 4. Verdict

**CLEARED**, conditional on fixture-authored fact sets. The candidate
correctly refuses the storage-product shape (it tests stores, including
native ones, rather than becoming one) — that refusal is load-bearing
to the verdict, because a store would need generation the benchmark
never requires.

---

## H1 — snapshot-bound completion evidence — CLEARED

### 1. What Noul judges; what Choice chooses

Minimal shape, and minimal is valid here (the Demo-2 precedent: no
Choice required where the question is binary). Noul adjudicates the
claim-to-evidence relation per supplied claim: supported /
contradicted / unknown / stale, with the stale state bound to exact
revisions. No Choice call is needed in the minimal design; if one is
added (e.g. selecting a report disposition), its candidates must be
caller-supplied and finite.

### 2. Why ordinary chat is measurably worse

Tested shape again: rubric recovers labels; what it cannot supply is
calibrated support probability across claims, mandatory `unknown` on
ambiguous evidence, or refusal to promote a model-authored record into
`verified`. The receipt fields (command, exit code, output hash,
revision per classification) are countable only because the verdicts
are typed. backcheck/evigate prove the deterministic core works
without any model; H1's Jev layer exists for exactly the zone where
those tools abstain — which is also why its value is bounded by that
zone (see my rung-1 scoring).

### 3. Extraction, generation, summarization audit

Claims must come from deterministic transcript parsing (rule-based
extraction of checkable statements), never from a model-written
summary of the session. Evidence is command/exit/revision/output-hash
tuples assembled by the harness. The stale-invalidation rule (later
mutation invalidates the claim, not the report) is deterministic set
logic over versioned evidence, not a judgment. Forbidden: LLM-written
claim lists presented as complete, verdict promotion of model-
authored records, retention inference from generated summaries.

### 4. Verdict

**CLEARED**, conditional on deterministic claim extraction. The
narrowing from my rung-1 pass stands inside the clearance: what clears
is the Jev-adjudication-plus-portability layer over a deterministic
core the incumbents already ship — not a from-scratch evidence
verifier, which would duplicate maintained tools.

---

## H3 — cache-aware routing price-drift auditor — HELD

### 1. What Noul judges; what Choice chooses

Thin, and thinness is the finding. The candidate's authoritative work —
price manifests vs usage logs vs observed spend, cache-read/write
semantics, provider-alias resolution, drift arithmetic — is entirely
deterministic. The single Jev role filed is "Choice classifies request
complexity for a counterfactual tier comparison." No Noul question is
specified anywhere in the candidate.

### 2. Why ordinary chat is measurably worse — unasked and unneeded

The question cuts deeper than chat-vs-Jev: a fixed model-capability
table (model → tier, committed, versioned) classifies request
complexity deterministically for any tier set the operator actually
uses. The candidate never shows a case where judgment beats the table,
so there is no chat baseline to be worse than — the deterministic
baseline is unexamined. This is the demo-1 trap shape: a valuable
deterministic auditor (price/cache metadata assertion, genuinely
wanted per the verified LiteLLM issue) wearing one Jev call it has
not earned. A Jev-free version of H3 would audit prices identically;
that is not a taste objection, it is the rung-2 question answering
itself.

### 3. Extraction, generation, summarization audit

No hidden generation — the failure mode is the opposite of the usual
one. Usage-log parsing, manifest joins, and variance arithmetic are
deterministic and clean. Nothing here needs a model except the filed
Choice, which is exactly what makes the rung-2 verdict what it is.

### 4. Verdict

**HELD, with a precise retry condition** (structural only, per rung
rules — not a kill, no taste involved). Clear by either path: (a)
exhibit a fixture where fixed tier rules misclassify and a typed
Choice with reasons gets it right — i.e., prove the judgment does
work the table cannot; or (b) re-scope as a deterministic price/cache
auditor with a Jev adjunct, with the adjunct's necessity argued
separately and the deterministic core claiming no Jev credit. The
underlying audit need (verified implementer pain, narrow but deep
buyer pool) is untouched by this hold — HELD constrains the shape,
not the problem.

---

## Boundary and non-kills

Four clearances and one hold. Nothing is RULED OUT in this unit. The
verdicts do not claim calibration, demand beyond rung-1, installability,
cost, lift, or that any pinned generator backs the fixtures — those
belong to rungs 3+. Concretely not claimed: that H2's risk assignment
has a settled design (it has two allowed designs); that H4's corpus
exists (it does not — rung-3 cost); that H5's fixture set covers
non-Claude harnesses (asserted scope, unbuilt); that H1's Jev layer
beats backcheck/evigate on any transcript (unmeasured — the wedge is
argued, not shown); that H3's tier table fails anywhere (the hold's
open question).

A future structural change reopens any verdict: model-generated claim
lists, invented Choice options, prose-parsed Nouls, model-written
fixtures presented as neutral, deterministic checks replaced by model
assertion — each returns its candidate to HELD. No candidate is
rejected here for overlapping a deterministic tool: per §3i, an
incumbent without a judgment model is a baseline to beat
(backcheck/evigate for H1, price tables for H3), never an owner.

## NO-CLAIM

Structural assessment only. No Jev calls, no implementations, no
fixtures built, no live provider, browser, MCP, or credential paths
touched. Question wordings above are specified shapes for contracts,
not executed prompts. Verdicts determine Jev-necessity, nothing else.

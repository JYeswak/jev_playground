# Duel-2 non-author hunt scores — COD on MU-H1…MU-H3

Status: independent rung-1 demand score of pane 3's hunt.
Author boundary: pane 3 authored `DEMAND_HUNT_MU.md`; pane 2 is a non-author of MU-H1, MU-H2,
and MU-H3.
Input: `docs/demos/duel-2/DEMAND_HUNT_MU.md` (`6c101d5`, 8,275 chars as reported by dispatch;
working-tree read measured 8,207 bytes).
Plan basis: §3b demand questions and §3e's two-non-author blocker.
Recusal: COD-H1…H5 and Demo-9 are not scored here.

## Scoring method

This is demand only, not supply, implementation, Jev-shape certification, or promotion. I applied
the four §3b questions independently:

1. Can a stranger install/run it from a clean clone with one command and committed fixtures?
2. What benefit transfers to AI usage broadly rather than to this lane?
3. Who downloads it, what pain did that person voice, and what incumbent already serves it?
4. What before/after command makes the improvement measurable?

The hunt's shorter artifact is not treated as weak. Its own disclosure says two search batches were
throttled and that press links were unverified; I treat those citations as open, independently
verify what I can, and score the evidence boundary rather than the byte count. I also search the
problem rather than only the incumbent names supplied by the hunt.

## Result

| Candidate | MU self-score | COD non-author score | Rung-1 demand disposition |
|---|---:|---:|---|
| MU-H1 stale-TODO truth judge | 900 | **820** | Demand remains strong; incumbent search is credible but not exhaustive. Rung-2 shape is promising but needs an exact contract. |
| MU-H2 doc-drift judge | 850 | **430** | Existing maintained tools directly occupy the proposed doc/code drift gate; any surviving gap needs a new contract. |
| MU-H3 sanitize-before-send | 820 | **650** | Real security pain and an important boundary, but public demand evidence was disclosed as open and maintained SDK/privacy filters already cover adjacent scope. |

No candidate is promoted by this score. MU-H1 clears the 700 numerical bar in this non-author
score, but §3e still requires a second non-author score. MU-H2 and MU-H3 do not clear 700 in this
pass; missing evidence is not a kill by itself, and H3 also has a later rung-2 risk because its
proposed mechanism uses no judgment model.

## MU-H1 — stale-TODO truth judge — 820

### Installability by a stranger

The hunt specifies a comprehensible install surface: one binary, deterministic enumeration of
TODO/FIXME/HACK markers, a shipped fixture repository with 200 seeded markers, and
`todo-judge audit --sample 50`. That is a credible clean-clone shape, but it is still a proposal;
no installer, fixture, receipt, or third-party run exists in the hunt. I award strong but not full
credit because the candidate can be exercised offline if the deterministic scanner and injected Noul
are implemented, while the actual clean-clone proof belongs to rung 3.

The candidate's primary input discovery is not a problem for Jev shape. Enumerating comment markers,
file locations, blame metadata, and surrounding code is a deterministic candidate-finding stage,
like reading a list of acceptance lines before judging them. The model must not discover arbitrary
TODOs, rewrite the marker, or invent a work item. The proposed report can be produced from fixed
fields plus a finite verdict and probability.

### Benefit to AI usage as a whole

The broad benefit is credible: every codebase accumulates TODO-like markers, and agent-authored code
increases the rate at which comments and their surrounding assumptions can drift. A truth judgment is
different from age, ownership, or issue synchronization: a five-year TODO can still be accurate,
while a week-old workaround can already be fulfilled. A calibrated stale/valid/uncertain report could
help maintainers decide which markers deserve human review before an agent deletes or promotes them.

The benefit is not automatically “every codebase downloads this.” TODO cleanup competes with issue
trackers, IDE views, static scanners, and ordinary code review. The candidate needs to show that
truth classification changes maintenance behavior rather than producing another sorted list.

### Named pain and incumbent search

The hunt's unlinked pain claims were open, not accepted blindly. Independent searches found
supporting public sources:

- Benjamin's public `todoage` article, “Every TODO in your codebase is lying about its age. So I
  built a CLI that blames them,” describes the age/rot problem and links the tool:
  [DEV Community article](https://dev.to/_06a3df6b50aec966668fb/every-todo-in-your-codebase-is-lying-about-its-age-so-i-built-a-cli-that-blames-them-h84).
- Deviera frames TODO/FIXME/HACK markers as engineering debt and turns them into tracked work:
  [Deviera](https://deviera.dev/). This is vendor pain language, not independent adoption data.
- Deska describes comment rot: code changes while the explanatory comment remains and becomes
  misleading, with stale TODOs as a concrete case:
  [Comment Rot: Deleting Lies From Your Codebase](https://deska.dev/blog/agent-comment-rot-cleanup).
- The research precedent is TDCleaner, “Automating the Removal of Obsolete TODO Comments,” which
  correlates TODO text, code changes, and commit messages:
  [ESEC/FSE paper](https://arxiv.org/abs/2108.05846).

These sources support pain, but they do not provide four independently verified end-user interviews.
The incumbent search also needs a careful distinction:

- `todoage` reports marker age, blame, author, and stale-age thresholds; it does not judge whether
  the comment's proposition remains true. Source: [PyPI todoage](https://pypi.org/project/todoage/).
- `todoctor` has a released tag `v1.4.2` (tag SHA observed during the read-only tag probe) and
  analyzes/reports TODO comments across JavaScript/TypeScript history. Its documented positioning is
  analysis/history, not a semantic truth verdict. Source: [todoctor](https://github.com/azat-io/todoctor).
- TodoTracker and issue-export tools track age, status, assignment, or synchronization; a dashboard
  does not establish that the code surrounding a marker satisfies its proposition.
- TDCleaner is the closest semantic prior art, but it is a research prototype rather than a current
  maintained installable incumbent. A pinned remote probe of the cited `beyondacm/TDCleaner`
  repository returned “Repository not found”; that is evidence of an unavailable citation, not proof
  that no fork exists.
- The search did not find a maintained, installable tool whose documented contract is exactly “given
  a TODO marker and its code context, return calibrated valid/stale/uncertain truth with an audit
  receipt.” This remains a bounded-search result, not an absolute universal claim.

The user's warning is therefore satisfied in both directions: a stale-TODO linter would kill MU-H1
if it actually judged truth, but the maintained tools independently verified so far are age/history
or tracking tools. I did not treat a list of named tools as a substitute for searching the semantic
problem.

### Measurable before/after

The proposed `todo-judge audit --sample 50` gives a useful measurement shape:

- Before: marker truth is unknown; the maintainer samples markers with no calibrated ordering or
  receipt.
- After: a held-out human-labelled sample reports precision/recall for `valid`, `stale`, and
  `uncertain`, calibration error or reliability bins, review time, and the number of markers safely
  escalated rather than deleted.
- Required controls: unrelated code changes, an actually fulfilled TODO, an active TODO with a
  misleadingly old age, an ambiguous marker, and a marker whose referenced issue is unavailable.

The hunt does not yet state how labels are collected without circularly asking the same model. A
stranger also needs an explicit denominator, source-span evidence, and a no-action default for
uncertain cases. Those omissions reduce demand confidence but do not erase the measurable core.

### Rung-2 passing note

The mechanism sentence survives in principle: “calibrated batch judgment with a receipt over
hundreds of markers” is a genuine reason to use a typed judgment model rather than prompt one TODO
at a time. Per-marker Noul questions can be repeated at a fixed schema; a deterministic sorter can
rank the returned probabilities; a Choice is optional unless the caller selects from supplied
worklist actions.

The current hunt is not yet a complete rung-2 contract. The exact question is only sketched as:

> This marker is still accurate about the code around it.

A real contract must supply the marker text, relevant code/history evidence, finite verdicts
(`valid`, `stale`, `uncertain`), criteria for each, probability handling, malformed-output behavior,
and a rule preventing the Noul from inventing a new task. The deterministic comment enumeration is
an explicit extraction stage, not hidden model extraction; it does not disqualify the candidate. If
semantic claim extraction from arbitrary TODO prose is added as a model stage, the candidate returns
to HELD at rung 2 rather than silently passing.

### Score decision

**820/1000.** I reduce MU's 900 because the external pain sources are partly vendor/author content,
the semantic incumbent search remains bounded rather than exhaustive, and the proposed exact question
and receipt are not yet a contract. I do not reduce it to a kill: the age/history tools found do not
own truth judgment, TDCleaner is not a maintained replacement, and the before/after label protocol is
credible. MU-H1 is still the strongest MU candidate in this pass and requires a second non-author
score before rung 3.

## MU-H2 — doc-drift judge — 430

### Installability by a stranger

The proposed one-bin fixture with seeded doc/code drift is easy to understand and likely installable.
The mechanism names deterministic pairing by paths, symbols, and fence references, followed by one
Noul per pair. That is a stronger install story than an unbounded “ask an agent whether the docs are
right,” but no fixture or install proof is present. I award moderate credit.

### Benefit to AI usage as a whole

Documentation drift is a real cross-team problem, especially as AI agents change code faster than
humans update prose. A faithful doc/code check could protect runbooks, CLI docs, API references, and
agent instructions. The broad benefit is real, but the candidate is not demand-unowned: existing
tools now directly advertise the same doc-to-code freshness and claim-verification capability.

### Named pain and incumbent search

The hunt's original sources—repowise.dev, thecodeforge.io, vizrepo.com, and jamdesk.com—were
explicitly not verified because two search batches were throttled. I therefore do not treat their
quoted language or claimed incident as established evidence. Independent search found a public
DevOps discussion about a stale failover runbook prolonging a production incident, but the author and
incident were not independently verified; that supports “pain exists” only weakly.

More importantly, the maintained incumbent search found direct overlaps:

- `docverity` v0.5.0 (tag SHA `d83fae3165ac536b3b889a0ea1ee68df0b30eef1`) documents extracting concrete
  claims from docs and checking them against source, with deterministic reference checks plus an
  LLM-backed semantic claim verifier, CI exit codes, confidence thresholds, and `--strict` handling.
  Source: [docverity v0.5.0](https://github.com/deveshagarwal/docverity/tree/v0.5.0) and its
  [pinned README](https://raw.githubusercontent.com/deveshagarwal/docverity/v0.5.0/README.md).
- `fiberplane/drift` v0.10.1 (tag SHA `fc90540acb1a3f15ab3c90b4c8c9bac16c7a6522`) binds Markdown to
  files/symbols, stores AST fingerprints in `drift.lock`, and fails CI when an anchor is stale.
  Source: [fiberplane/drift v0.10.1](https://github.com/fiberplane/drift/tree/v0.10.1) and its
  [pinned README](https://raw.githubusercontent.com/fiberplane/drift/v0.10.1/README.md).
- `doc-drift-guard` and other documentation-maintenance tools also advertise code/path/flag/config
  checks; its current release status was not pinned in this pass, so I treat it as an additional
  candidate substitute, not as sole proof.

These are not merely age trackers or generators. Docverity's README says it extracts claims and
checks them against source; fiberplane/drift is a direct structural stale-doc gate. MU-H2's proposed
“does this doc accurately describe the code?” is therefore already served in material part by
maintained tools. A Jev-specific per-pair probability may be a different implementation, but the
rung-1 demand slot is not empty.

### Measurable before/after

MU-H2 proposes before/after precision/recall against human labels and a `docjudge audit` command.
Those are valid measurements, but incumbents already produce actionable CI failure/status outputs.
To justify a new download, H2 would need a documented gap such as calibrated uncertainty on prose
claims that `docverity` does not cover, a source-span receipt, or a buyer requiring a local/no-LLM
path; the current hunt does not establish that gap. “Noul per pair” is a mechanism distinction, not
itself a demand distinction.

### Rung-2 note and score decision

The proposed deterministic pairing avoids hidden extraction if it only uses explicit paths, symbols,
and fence anchors. The Noul can judge a supplied pair, but `docverity` already uses an LLM-backed
claim verifier for semantic drift, so Jev novelty would need proof at a later rung.

**430/1000.** I reduce MU's 850 sharply because the external pain citations were unverified and
pinned maintained tools directly occupy the proposed doc/code drift gate. This is a structural
incumbent discount, not taste. I do not claim that every documentation problem is solved: a new
contract could target an unserved receipt, calibration, or source-span requirement, but it must
re-enter demand research as a distinct candidate.

## MU-H3 — sanitize-before-send — 650

### Installability by a stranger

The proposed one-import swap, synthetic offline fixture, fixed-token redaction, fail-closed detector,
and per-call receipt describe a plausible stranger install. A transport boundary is safer to test
than a live provider integration because the fixture can assert that the raw value never reaches the
serialized request. No clean-clone receipt exists yet, so this receives proposal-level rather than
proof-level credit.

### Benefit to AI usage as a whole

The benefit is broad and high stakes: tool output, session history, nested-agent messages, and error
payloads can cross into a paid model request after repository scanners have finished. A runtime
pre-send boundary is materially different from scanning Git history. The candidate could help
agent platforms, SDKs, enterprise wrappers, and coding harnesses.

There is also a rung-2 warning: MU-H3 explicitly says “no chat model involved at all.” That is a
coherent security design, but it means this is not yet a Jev judgment candidate under §3c's rung-2
rule. The demand score here does not kill it for that reason; it records a later structural gate.

### Named pain and incumbent search

The hunt correctly disclosed that two external press batches were throttled and that its external
PII-redaction citations were unverified. I do not count those as established evidence. Independent
research found a concrete maintainer issue: Hermes Agent issue
[#77162](https://github.com/NousResearch/hermes-agent/issues/77162) discusses exact-value secret
redaction missing on the tool-result-to-provider-egress path. That is a direct runtime-boundary pain
signal, though it is one repository issue rather than broad adoption evidence.

The incumbent landscape is stronger than the hunt's “none owns the boundary” statement allows:

- OpenAI Agents JS documents `callModelInputFilter`, a final pre-model hook that can redact prepared
  input and persist the filtered clone. Source: [Running Agents](https://openai.github.io/openai-agents-js/guides/running-agents/).
- OpenAI's [Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) documents
  local detection/redaction categories including private data and secrets.
- Gitleaks and TruffleHog remain repo/credential scanners rather than direct provider-boundary
  middleware, so they do not eliminate the whole runtime problem.
- General PII/secret redaction libraries and provider wrappers are adjacent substitutes; the exact
  harness-native, span-preserving, fail-closed receipt may still be a gap.

Thus H3 has real unmet scope, but “no maintained tool owns it” is not established. A Jev-client
transport with cross-provider coverage could still be useful; it cannot claim a blank market based
only on repo scanners.

### Measurable before/after

The proposed metric is decisive if the boundary is real: before, secret-shaped bytes crossing per
1,000 calls; after, zero raw registered-secret bytes crossing, with redaction counts, detector
errors, placeholders, and serialized-request hashes. The fixture must include secrets in tool text,
nested JSON, error paths, history, attachments, and retries; it must assert zero raw bytes in both
provider-bound request and persistence/log sink. A redactor that only passes a happy-path string
would not prove the boundary.

### Score decision

**650/1000.** I credit the high-severity runtime pain, strong measurable invariant, and broad agent
population. I discount the score because external search evidence was deliberately left open, OpenAI's
SDK/privacy-filter paths already cover adjacent pre-model redaction, and the candidate is not yet a
Jev judgment shape. This is not a structural kill at rung 1; it is a demand score plus an explicit
rung-2 risk. A pinned external incident corpus and a clear gap against maintained pre-send filters
could raise it; an implementation that remains pure deterministic redaction would need to leave the
Jev demo gauntlet or add a genuine typed judgment question without sending secrets to it.

## Non-author conclusion

MU-H1 remains the strongest hunt candidate after independent search, but 900 is too high until the
exact Noul contract, evidence envelope, and incumbent search are pinned; I assign 820. MU-H2 is not
an 850 demand opportunity because docverity and fiberplane/drift directly occupy the proposed gate;
I assign 430 while leaving any genuinely different gap open. MU-H3 has serious demand but its
external voice and incumbent differentiation are incomplete and its mechanism risks failing rung 2;
I assign 650.

The hunt's 8,275-byte size is not used as a score signal. The disclosed throttle increased the
uncertainty of H2/H3 external citations; it did not lower the score merely because the artifact was
short. Conversely, a longer file would not earn points without stronger evidence.

## NO-CLAIM

These are non-author demand scores, not adoption measurements, user interviews, implementation
results, security certification, or rung-2/rung-3 passes. I did not install todoage, todoctor,
docverity, fiberplane/drift, doc-drift-guard, or any redaction tool. Tag probes and pinned README
reads were read-only. No candidate is promoted; H1 still needs a second non-author rung-1 score,
H2/H3 need clearer differentiation or a new contract, and all later gates remain open.

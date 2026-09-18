# BEAD-TEMPLATE — the shape every jev bead must have

**Derived, not invented.** Every number below was measured from `skillranker@3fe85c4`
(`.beads/issues.jsonl`, 195 beads) on 2026-09-18. This file exists so eight demo contracts written
by three different agents come out the same shape.

## The measured target

| Metric | skillranker | jev before | jev target |
|---|---:|---:|---|
| beads | 195 | 21 | grow with the DAG, not by padding |
| median description | **7,363 chars** | 1,252 | **≥7,000** |
| max description | 36,370 | 4,822 | no cap |
| top roadmap epic | **26,115 chars** | — | **≥24,000** |
| phase epic | **13,532 chars** | — | **≥12,000** |
| with dependencies | **191/195 (98%)** | partial | **100%** |
| epics | 11 | **0** | one roadmap + one per phase |
| priorities in use | **P1, P2 only** | P0–P3, 6/21 at P0 | **P1, P2 only** |

**On length as a target.** Length is a symptom of embedded contract, never the goal. A 7 KB bead
that repeats itself is worse than a 3 KB bead that is complete. The way to reach 7 KB honestly is
to answer every question an implementer would otherwise have to ask a human — which is the actual
bar, and the length follows.

## The five sections — adoption measured across his 195 beads

Use all five, in this order, every time.

### 1. `## Goal and ownership` — 186/195 (95%)

What this bead delivers, and the **boundary it must not cross**. His pattern names the exact files
and says what is *not* in scope:

> *"Ownership limited to configuration diagnostics and tests/config_contract.rs; no adapter
> changes."*
> *"Work on the named boundary and its focused tests. Blocking dependencies supply tested
> prerequisites; parent-child edges organize the roadmap and do not stand in for acceptance."*

Required content:
- One-paragraph goal in product terms, not implementation terms.
- **Explicit file/module ownership**, and an explicit non-goal list.
- In this lane additionally: which pane owns the tree, since three agents share the checkout and
  `%an` cannot attribute a commit.

### 2. `## Product context and guardrails` — 175/195 (90%)

**Embed `PLAN.md` §0 verbatim.** Do not summarize it, do not link to it. His version is copy-pasted
into 175 beads unchanged, and it carries the anti-claim sentence that makes the rest safe:

> *"These are implementation requirements, not statements that any product code or behavioral gate
> has passed."*

### 3. `## Embedded contract` — 180/195 (92%)

The normative requirements this boundary must satisfy, stated so **no other document is needed**.
His framing:

> *"The following requirements define this boundary and its interactions. Implement the goal above;
> related behavior is supplied by the explicit prerequisite tasks."*

Required content:
- The mechanism, named stage by stage. "Extracts verifiable working points" is **not** a
  mechanism — it hides a stage. Name it: deterministic extraction → Choice over candidates → Noul
  verbatim verification.
- Every threshold as an **absolute** value. Never "beat arm B": arm B scores 3, 1, 3 on a
  byte-identical fixture, so a stochastic baseline is not a threshold (`NEGATIVE_EVIDENCE.md` R11).
- The API contract if Jev is called: endpoint, model, the exact question asked, and what an
  insufficient-context answer maps to (**withhold, never approve**).
- Cost and budget if any call is live, stated in the units the provider reports.

### 4. `## Focused verification` — 180/195 (92%)

How this bead is proven, and **which planted defect turns it red**. A gate that cannot fail is not
a gate.

Required content:
- The command a third party runs, copy-pasteable, no placeholders.
- **At least one RED arm**: the planted bad input, and the assertion that the failure output *names
  the plant*.
- The **denominator** the verification reports: how many, over what, how many skipped and why.
- The fail-closed cases: empty scan set ⇒ ERROR; one-item scan set ⇒ not a demonstration; timeout
  ⇒ `TIMEOUT_UNMEASURED`, never absent; exit code agrees with verdict text.
- Who verifies. A non-author, and for anything the conductor authored, a pane that did not write it.

### 5. `## Evidence and logging` — 183/195 (94%)

The artifact left behind, and what it is **not** allowed to claim.

Required content:
- Receipt path and schema: inputs, denominators, counts, `failures` array.
- The **verification level** the resulting commit subject will carry
  (`pending|selftest|test|mutation|oracle|live`).
- The **Boundary** line for `EVAL.md`: exactly what this does not prove.
- **Never retro-edit a receipt.** A receipt is evidence; editing its bytes converts evidence into
  assertion. Supersede by re-running, never overwrite.
- No secret values, no operator home paths, no machine names in any committed artifact.

## Optional sections, used where they apply

Measured in his corpus, in descending frequency: `## Runnable suite, unit coverage and diagnostic
logs` (28), `## Implementation order and dependencies` (15), `## Ownership clarification` (11),
`## Required test evidence at this phase` (10), `## Open risks with concrete resolution` (4).

Use `## Open risks with concrete resolution` whenever a bead carries a known unknown — the
resolution must be a command, not an intention.

## Anti-patterns, each measured in this lane

- **A pointer instead of a contract.** "See `PLAN.md` §5" fails the same way a bare filename failed
  twice tonight: the reader cannot act on a reference it must resolve by guessing.
- **A count where a property belongs.** Demo-7's original gate was "N≥50 receipts"; R11 then showed
  the generator is nondeterministic, so 50 receipts would fit a model on noise. Gates must name the
  property (pinned generator, published distribution), not the count.
- **A verdict string over a stochastic arm.** The A/B harness emitted `"B wins"` from n=1 and that
  string propagated into 17 tracked files before anything ran the harness twice.
- **P0 inflation.** 6 of 21 beads at P0 means priority carries no information. He uses P1/P2 across
  195 beads.
- **An acceptance nobody can obtain.** Re-derive every count a bead's acceptance asserts *before*
  filing it.
- **A tool limitation recorded as a provider limitation.** "Grok is TEXT-ONLY" was false; the
  limitation was in our script, which only called `/v1/images/generations` while the API exposes
  `/v1/images/edits` with up to 5 reference images. State where a limitation lives.

## Emission discipline

1. The plan reaches steady-state **first**. A bead graph inherits every structural error in its
   source; measured tonight, an overstated headline became a worker's premise before an audit
   caught it.
2. Emit with `br` only. Dependencies added with `br dep add`; `br dep cycles` must return empty.
3. Every bead gets a dependency edge or is a root. 98% coverage is the measured bar; an orphan bead
   is invisible to `br ready` ordering.
4. Then polish. His corpus carries `compaction_level` and `original_size` fields, so bead bodies
   are compacted after the fact — write long first, compact later, never the reverse.

# Baseline design — MU-H2 doc-drift judge versus incumbent tools

Status: Q4 queue unit, rung-2 baseline design. No implementation or benchmark was run.
Candidate: MU-H2 doc-drift judge, pane-3 authored.
Incumbents: `docverity` v0.5.0 and `fiberplane/drift` v0.10.1.
Question: do the maintained tools own the calibrated judgment niche, or are they deterministic
controls whose supported subset a Jev judge can measure against?

## Doctrine correction

The first incumbent reading treated overlap as ownership. §3i corrects that rule: a maintained tool
that does not provide a calibrated typed judgment is a baseline, not an owner. The head-to-head must
measure the delta on one corpus, show where the incumbent wins, and fail if the Jev delta is too small
to change a stranger's behavior.

There is one evidence discrepancy that the baseline must preserve rather than paper over. The PLAN
text says both tools “parse, regex and match formats,” while the pinned `docverity` v0.5.0 README
documents an optional **LLM-backed Claim verifier** with a confidence threshold and `--strict`
handling. The comparison therefore has three incumbent arms, not one:

- **D0 — fiberplane/drift v0.10.1:** deterministic AST-anchor freshness.
- **D1 — docverity v0.5.0 `--no-llm`:** deterministic references/coverage.
- **D2 — docverity v0.5.0 default/LLM claim verifier:** an existing non-Jev model comparison,
  recorded with whatever confidence/abstention schema it actually emits.

D2 is not silently called calibrated. If its confidence is not a typed, labelled, calibrated
probability with an audit trail, it remains a non-Jev model baseline. The candidate must beat the
best relevant arm rather than only beat a deliberately weakened no-model command.

## Pinned incumbent evidence

### fiberplane/drift v0.10.1

Pinned tag probe resolved v0.10.1 to
`fc90540acb1a3f15ab3c90b4c8c9bac16c7a6522`.

Sources:

- [Repository tag](https://github.com/fiberplane/drift/tree/v0.10.1)
- [Pinned README](https://raw.githubusercontent.com/fiberplane/drift/v0.10.1/README.md)

The README documents Markdown-to-file/symbol anchors, a `drift.lock` containing signatures, and
`drift check` failing when a bound file or AST fingerprint changes. Supported-language AST anchors
make the structural result deterministic and do not need VCS history for the signature comparison.
It is a strong control for reference/structural drift, not a semantic judge of arbitrary prose.

### docverity v0.5.0

Pinned tag probe resolved v0.5.0 to
`d83fae3165ac536b3b889a0ea1ee68df0b30eef1`.

Sources:

- [Repository tag](https://github.com/deveshagarwal/docverity/tree/v0.5.0)
- [Pinned README](https://raw.githubusercontent.com/deveshagarwal/docverity/v0.5.0/README.md)

The README documents:

- deterministic reference checking for files, flags, environment variables, and symbols;
- code-to-doc coverage checks;
- an optional LLM-backed prose Claim verifier;
- confidence filtering (`--fail-confidence`, default 0.7);
- `--strict` behavior for unverifiable claims;
- CI exit codes and GitHub formatting;
- a `--no-llm` deterministic mode.

D1 is a strong no-key, fast control. D2 is a legitimate non-Jev model baseline and must be included
when its claim-verifier path is available. The Jev candidate cannot claim a win merely because D1
refuses prose that D2 attempts.

## What each incumbent can and cannot prove

| Capability class | D0 fiberplane/drift | D1 docverity no-LLM | D2 docverity LLM | MU-H2 Jev judge |
|---|---|---|---|---|
| Bound file/symbol changed | Strong AST fingerprint | Reference/path check | Same deterministic base | Should match, with typed probability |
| Missing CLI flag/env/path/symbol | Not its primary contract | Strong reference/coverage check | Same plus adjudication | Should match or abstain |
| Prose says wrong default/behavior | Not supported | No-LLM unsupported/unknown | Attempts claim verification | Noul per supplied doc/code pair |
| Narrative/list count contradiction | No | Limited | Documents narrative check | Noul if pair/evidence is supplied |
| Code added but not documented | No | History-aware coverage | Same plus model | Requires explicit pairing/coverage stage |
| Arbitrary unanchored prose | No | May report unverifiable | May attempt, confidence must be audited | Must withhold if pairing/evidence fails |
| Typed calibrated probability | No documented probability | No model probability | Confidence is not assumed calibrated | Required Noul probability + calibration receipt |
| Human-readable CI receipt | Yes, stale anchors | Yes | Yes | Required with evidence refs and unknowns |
| No key / offline | Yes | Yes with `--no-llm` | Not necessarily | Offline injected asker first; live separately budgeted |

The candidate's advantage is not “Jev reads docs better” as a slogan. It is the measurable
combination of deterministic pairing, a typed Noul verdict, explicit uncertainty, and a calibration
report over semantic doc/code relations. If D2 already provides the same relation with equal
calibration and lower cost, the candidate must say so.

## Shared corpus

### Corpus source and shape

Build one immutable corpus from pinned real repositories plus controlled mutations. Do not compare a
Jev fixture against an incumbent fixture hand-crafted for its strengths. The manifest contains:

```json
{
  "case_id": "auth-default-07",
  "repo": "jev-review",
  "repo_sha": "57690af54ef7d862c2483342c1e61c14dffcf727",
  "doc_path": "README.md",
  "code_paths": ["src/..."],
  "anchor": "src/auth.ts#AuthConfig",
  "mutation": "wrong_default",
  "truth": "drifted",
  "evidence_ranges": ["README.md:40-44", "src/auth.ts:12-27"]
}
```

Start with at least 12 pinned repositories across TypeScript, Python, Rust, Go, and Markdown-heavy
projects. Include both docs with existing explicit anchors and docs with no anchors. The source tree
and mutation manifest are hashed; tools run against identical bytes. If the real repositories do not
contain enough semantic claim classes, add a separate committed synthetic fixture set and report its
share rather than passing it off as field data.

### Stratified cases

Use 120 labelled document/code pairs, 20 per class:

1. **valid structural anchor:** file/symbol unchanged and prose correct;
2. **reference drift:** renamed/deleted file, symbol, flag, or environment variable;
3. **AST/signature drift:** anchored declaration changed structurally;
4. **semantic default drift:** prose says timeout/default/version that code no longer uses;
5. **behavior drift:** prose describes a branch or error behavior that changed;
6. **coverage/narrative drift:** code adds a capability or a list count contradicts the doc.

Add 20 ambiguous/unpaired cases as a separate unknown set. Each mutation is applied before either
arm runs, with a patch and truth label committed in the manifest. For each class, preserve positive
and negative cases; a corpus containing only planted drift measures detector sensitivity, not demand.

### Strict subset declaration

The incumbent subset is explicit:

- D0 receives only cases with a declared fiberplane-compatible anchor.
- D1 receives all cases whose doc statements reduce to its documented deterministic reference/
  coverage checks.
- D2 receives cases it can parse as claims under its v0.5.0 configuration; unsupported cases are
  `unverifiable`, not silent negatives.
- MU-H2 receives the same doc/code bytes and deterministic pair manifest. Its Noul sees only the
  supplied pair and bounded evidence ranges; it does not discover arbitrary doc/code matches.

The full corpus is therefore broader than every incumbent subset. Every arm reports `attempted`,
`supported`, `withheld`, and `unsupported` denominators by class. A tool that never attempts a class
cannot get credit for correct abstention and cannot be penalized as though it produced a false clean.

## Candidate arm: MU-H2

The candidate's mechanism is:

1. Deterministically pair a doc block with a file/symbol using an explicit path, fence, anchor, or
   manifest mapping.
2. Hash the doc bytes, code bytes, and pairing metadata.
3. Send one exact Noul question per pair:

   > Does this supplied documentation block accurately describe the supplied code unit at the
   > supplied revision? Return true only when the stated behavior, defaults, names, and constraints
   > are supported by the supplied code/evidence. Return false when a contradiction is shown.
   > Withhold when the pair or evidence is insufficient. Do not rewrite the documentation.

4. Map typed `true/false/withhold` plus probability to `accurate/drifted/uncertain` in local code.
5. Emit source ranges, hashes, model version, probability, threshold, latency, cost, and every
   unknown/error. No generated rewrite is part of the judged result.

If a pair cannot be built deterministically, the candidate records `unpaired` and does not ask Jev.
This is a fair comparison to D0/D1: the candidate must not hide an extraction or matching advantage
inside the model call.

## Measurements

Report per class and per arm:

1. **Drift precision:** flagged cases that are truly drifted.
2. **Drift recall:** true drifted cases flagged.
3. **False-clean rate:** drifted cases marked accurate; this is the safety-critical miss.
4. **False-stale rate:** valid cases marked drifted.
5. **Unknown discipline:** ambiguous/unpaired cases withheld rather than guessed.
6. **Coverage:** attempted cases / full corpus, per class.
7. **Calibration:** ECE, Brier score, reliability bins, and threshold-selected precision for any arm
   claiming probabilities. If D2 emits only heuristic confidence, record `calibration_unavailable`;
   do not award it or penalize Jev by assumption.
8. **Provenance completeness:** source/doc/code hashes, ranges, revision, and tool version.
9. **Runtime economics:** wall time, CPU, network calls, provider cost, and operator review minutes.
10. **Action lift:** number of review decisions changed correctly and human minutes saved per 100
    document/code pairs.

The same scorer must consume all arm receipts. A pretty report without denominators is not a result.
A detector that fails closed on every pair has perfect false-clean safety but zero coverage and fails
the action-lift gate.

## Where the incumbents win

The baseline must say this plainly:

- D0 is deterministic, free, fast, offline, and strong at AST-anchor freshness. It should be the
  default control for structural drift; Jev must not replace a hash comparison with a paid judgment.
- D1 is deterministic and language-agnostic for concrete file/flag/env/symbol references, with CI
  exit codes and no provider key. It should win those classes whenever its precision/recall are good.
- D2 may already provide useful semantic prose adjudication and an existing CI/MCP workflow. It has
  deployment and integration value that a new Jev package does not automatically beat.
- MU-H2 can win only where typed uncertainty, calibrated probabilities, source-range reasoning, and
  a materially lower false-clean rate provide a decision a deterministic tool cannot.

A correct composition result is acceptable: D0/D1 for structural checks, D2 where its semantic
claims are reliable, and MU-H2 only for a measured residual. “Jev was used” is not a ship criterion.

## Quantified ship gate

The candidate is not worth a thin proof unless the held-out corpus meets all conditions below:

- On D0/D1 structural classes, MU-H2 is within **2 absolute percentage points** of the best
  incumbent on drift recall and false-stale rate. It must not regress the free deterministic control.
- On semantic default/behavior/narrative classes, MU-H2 improves drift recall by **at least 20
  absolute percentage points** over the best applicable incumbent arm (including D2 when D2 attempts
  the class), while false-clean rate is **≤5%** and false-stale rate is **≤10%**.
- MU-H2 attempts at least **80%** of non-ambiguous semantic cases and withholds at least **90%** of
  explicitly ambiguous/unpaired cases. Universal `uncertain` is not a pass.
- On a labelled holdout, Jev probability has **ECE ≤0.10** and Brier score no worse than **0.15**;
  if the sample is too small for this claim, the result is HELD, not promoted.
- Human review time or correctly changed documentation decisions improve by **≥20% per 100 pairs**
  versus the best incumbent workflow. A tiny statistically real lift fails, exactly as Demo-1's
  0.047% result failed operationally.
- The full receipt is reproducible from the same corpus, and live/provider cost is stated. If the
  Jev arm costs more while producing no action lift, the winner is the incumbent composition.

If the corpus has fewer than 20 semantic cases, if drift prevalence is below 5%, or if D2 cannot be
run reproducibly, the gate returns **HELD/UNASKABLE** for that dimension rather than manufacturing a
win from a convenient fixture.

## Falsification and retry conditions

This baseline design does not kill MU-H2. It makes failure observable:

- If D0/D1 already match or beat MU-H2 on all attempted classes, the Jev residual is unproven; keep
  the incumbent and require a narrower candidate with a cited gap.
- If D2 matches MU-H2 semantically at lower cost and comparable calibration, the calibrated-judgment
  niche is not differentiated; retry only with a new source-range or uncertainty requirement.
- If semantic drift is too rare for 20 held-out cases, return HELD and enlarge the real corpus; do
  not claim no demand.
- If the candidate cannot deterministically pair docs to code without a model, return HELD at rung 2
  for mechanism repair; do not hide extraction in Noul.
- If the candidate's false-clean rate exceeds 5% or its action lift is under 20%, it fails the stated
  ship gate; a retry must name a narrower doc class or improved evidence envelope.

## NO-CLAIM

No incumbent or Jev tool was installed or benchmarked in this unit. The pinned versions, README
capabilities, corpus size, thresholds, and metrics are design inputs, not results. The PLAN/queue
statement that incumbents are deterministic is preserved as a hypothesis where it conflicts with
`docverity` v0.5.0's pinned README; D2 must be measured rather than silently ignored. This artifact
makes MU-H2 judgeable against strong controls without claiming a win.

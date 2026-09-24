# §19 taste-loop contracts: 20 packages audited, 0 promoted (2026-09-20)

Level: `test` (static audit + all suites run, no model calls).

## Conformance (static, per package; full table in `/tmp/taste-audit.json`)

All 20 import askJev/askJevChoice or are regex-by-design; zero `fetch`, zero
`block:true`. Suite results (offline, just run): commit 6, default 8, failure 5,
field 7, firstlook 8, foreman 4, fork 8, heat 7, heckle 8, jargon 8, observer 13,
preaction 6, promise 9, rerank 7, review 7, route 23, skip 8, uncanny 7, undo 8 —
**all green, 0 failures**. Dispatch has no test dir (no suite to run).

## Deviations from CONTRACT.md (each verified open, not grep-asserted)

- commit, dispatch, failure, foreman: `timeoutMs` 4000, not the contract 2500.
- rerank: `timeoutMs` 3000, not 2500.
- route: askJev via ABSOLUTE import (not `../../jev-client`), no `timeoutMs` on
  the call, wrapped in `recording()`; no QUESTIONS/CHOICE export (inline map).
- failure: multiclass via `askJevChoice` (contract's choice branch), no QUESTIONS
  export — correct per the choice rules, noted.
- preaction: regex-only BY DESIGN (header says so; cost-benefit stated).
- observer: no `src/index.ts` (entry is `src/observer.mjs`); separately, §16
  proved the shipped tree never fires (safeAppend undefined).
- dispatch: no `package.json` manifest, no test dir — thinnest contract shape.

## Promotion bars (equivalence / capability / performance / adversarial)

The cited `foundation/gates.d/85-promotion-contract.sh` does not exist in this
tree — bars taken from the dispatch text. Against them: equivalence holds
structurally modulo the deviations above; capability is unmeasured per package
(tests are offline, most without live-measure gates); performance timeouts vary
(2500/3000/4000/absent); adversarial arms exist per contract rule 14 but were not
individually re-proven here. **Promoted = 0**: no promotion invoked anywhere, and
per the brief none is earned on this evidence. That complies with the contract.

## NO-CLAIM

Static + offline suites only; no live per-package measure in this section;
adversarial arms spot-checked by rule text, not re-fired. Dispatch's "11
packages" not reconciled — 20 dirs exist; all 20 audited instead of guessing
which 11.

## NOT RE-SCORABLE — 2026-09-24

`/tmp/taste-audit.json` is gone. The receipt pointed the full conformance table at that file. README claims that cite this receipt: none found.

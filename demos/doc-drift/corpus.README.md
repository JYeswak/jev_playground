# doc-drift corpus (partial N=20 of the 120-case design)

Hand-built doc/code pairs with committed truth labels (`corpus.json`:
bytes+sha256 per file). Classes: 4 valid-anchor, 4 reference-drift,
4 semantic-default, 3 behavior, 3 coverage, 2 ambiguous/unpaired.
Truth `unknown` means the pair is deliberately unjudgeable (no code
target) — any verdict but `uncertain` on those cases fails the run.
Synthetic fixture set, reported as share, never passed off as field data.

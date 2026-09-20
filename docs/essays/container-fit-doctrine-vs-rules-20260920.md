# Container fit: mirror doctrine is 97% not-a-rule

2026-09-20, P2. Numbers first, architecture second.

## The ratio

Seeded-random n=300 from 33,380 AGENTS.md/CONTRACT.md rule records
(generation `08457a25`, seed `20260920-unbiased-300`):

- **Mechanizable-shape: 9/300 = 3.00%, 95% Wilson CI [1.59%, 5.60%]**
  → implied pool 529–1,870 over 33,380 (point ~1,000).
- **Universal-content: 3/300 = 1.00%, CI [0.34%, 2.90%]**
  → 114–967 (point ~334).

**97% of the mirror's doctrine cannot be a TTSR rule.** Not because it is
low quality — because it has no trigger string. "Measure twice, name the
oracle, prefer the boring option" never fires at a tool call. The container
for that 97% is the read-once layer (skill, AGENTS.md section, routed
reference), not a rule. The lane plan "mine the mirror into rules" tops out
at 114–967 candidates, most of which will fail our prevalence bar anyway
since they address defects Jeffrey commits and we may not.

## The survival curve (harvest N=78,242, prevalence before labelling)

| class | hits | rate | ≥50 | ≤5% | disposition |
|---|---|---:|---|---|---|
| bare-TUI, naive (`bv\|cass` anywhere) | 504 | 0.64% | yes | yes | contaminated: `bv_probe`, `fn bv`, bead titles |
| bare-TUI, command-position | 11 | 0.014% | **no** | yes | 0 true fires — refuse |
| destructive (`reset --hard`, `clean -fd`, `rm -rf`) | 258 | 0.33% | yes | yes | refuse by redundancy: dcg enforces |
| foreign-pm (`pnpm\|yarn\|bun install`) | 110 | 0.14% | yes | yes | FP 1.00 (n=20, seed 20260920) — fires on correct behavior |
| branch-create (`checkout -b`, `switch -c`) | 0 | — | no | yes | absent — refuse |
| vercel-direct | 2 | — | no | yes | absent — refuse |
| bun-test-bare | 4 | — | no | yes | absent — refuse |
| secrets-to-git, true fires | 0 | — | no | yes | absent — R61 |
| backtick-in-record-body, narrow | 12 | 0.015% | no | yes | residuals are deliberate probes — R59 |

Three classes reached the labelling stage; all three refused (contamination,
redundancy, FP 1.00). Six never reached it. **Nothing shippable.**

## doctrine-history as filter: works, confirms weak prior

`fh doctrine-history --repo <mirror>/<name>` runs ~7s/repo and returns
added/removed/rewritten per rule with commits (markdown_web_browser: 346
added / 107 removed / 118 rewritten). Applied to the sampled rows: bare-`bv`
and bare-`cass` both arrived in bulk-import commit `f2e432e6` (2026-01-17),
not incident-earned. The filter is mechanically sound and worth running on
future candidates — this unit had no shippable candidates left to filter.

## Consequence

Route the 97% through the read-once layer: `jsm suggest`/`jsm scan` as the
live skill oracle (no stale skill lists in rules), mirror crate pointers in
AGENTS.md sections, doctrine-history incident-earned rows as the only
mirror-to-rule feed worth screening. Revisit only on retry conditions in
R56–R62.

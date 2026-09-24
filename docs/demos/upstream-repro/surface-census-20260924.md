# omp-jev surface census (2026-09-24)

Command: `python3 work/omp-jev-review/surface-census.py`

Keyless. Exit 0. 21 packages, 2,126 session files, 9 roots. Table:
`docs/demos/upstream-repro/surface-census-20260924.tsv`

## Counting rule

A row counts only after its JSON line parses, and only when `customType` is a
`*.decision.v1` or `*.screen.v1` string read from that package's own source.
A substring in tool output is not a row.

A session is probe/test, not real work, when its path or its session `cwd`
contains `/tmp/`, `/private/tmp/`, `review-l3`, `probe`, or `fixture`, when
the omp-encoded session directory contains those markers, when `cwd` is under
`/test/` or `/tests/`, or when the file lives in the `omp-test` or
`jev-scratch` profile. That is the jev-cz0 split: the 17 review rows are all
in `/tmp` and `/tmp/review-l3`, so real review is 0.

`real_error` is a real row whose kind ends in `_error`. `real_scored` is a
real row whose kind contains `scored`. Anything else (`guard_pass`,
`preaction_pass`, `review_not_applicable`) is `real_other`.

Loaded means a config extension or tool entry names the package or contains
its decision type, or a symlink under `.omp/extensions` or `tools` points at
it. A comment that mentions the package is not a load.

HTTP 402 rows at or after `2026-09-24T04:19:00Z` are credits, not a product
failure. This scan found 0.

## Result

Loaded, and only in `profile:jev-lab`: observer, preaction, review, route.
Not loaded in the project config, the default agent, or any other profile.
No symlinks.

| Package | Loaded | Real rows | Error | Scored | Last scored | Probe rows |
|---|---|---:|---:|---:|---|---:|
| commit | no | 0 | 0 | 0 | - | 0 |
| default | no | 0 | 0 | 0 | - | 0 |
| dispatch | no | 0 | 0 | 0 | - | 0 |
| failure | no | 1 | 0 | 1 | 2026-09-19 | 0 |
| field | no | 0 | 0 | 0 | - | 0 |
| firstlook | no | 0 | 0 | 0 | - | 0 |
| foreman | no | 2 | 0 | 2 | 2026-09-20 | 0 |
| fork | no | 0 | 0 | 0 | - | 0 |
| heat | no | 0 | 0 | 0 | - | 0 |
| heckle | no | 0 | 0 | 0 | - | 0 |
| jargon | no | 0 | 0 | 0 | - | 0 |
| observer | jev-lab | 4 | 0 | 0 | - | 24 |
| preaction | jev-lab | 3 | 0 | 0 | - | 47 |
| promise | no | 0 | 0 | 0 | - | 0 |
| rerank | no | 0 | 0 | 0 | - | 0 |
| review | jev-lab | 0 | 0 | 0 | - | 17 |
| route | jev-lab | 13 | 11 | 2 | 2026-09-20 | 134 |
| screen-log | no | 0 | 0 | 0 | - | 0 |
| skip | no | 0 | 0 | 0 | - | 0 |
| uncanny | no | 0 | 0 | 0 | - | 0 |
| undo | no | 0 | 0 | 0 | - | 0 |

The failure and foreman scored rows are from `cwd=/Users/josh/Developer/jev`.
Those packages are not in any current config, so the rows are historical.

NO-CLAIM: our traffic is not a stranger's. This census counts rows. It grades
nothing, and it does not change a config.

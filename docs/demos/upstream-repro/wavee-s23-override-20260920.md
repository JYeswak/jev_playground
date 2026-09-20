# §23 explain-before-override — PASS (2026-09-20)

Level: `live` (real denial + real alternative, quoted) + `test` (3/3).

## Evidence

- Denial (quoted): `dcg denied the bash tool call (core.filesystem:rm-rf-root-home)`
  on `rm -rf ~/override-probe-d`.
- Alternative taken (quoted): `EXPLICIT-SINGLE-FILE-REMOVE-OK` +
  `CLEAN` — mkdir/touch/rm/rmdir on explicit `/tmp/override-demo` paths.
- Rule file `work/jev-dcg-override/OVERRIDE-RULE.md`: 5 conductor cases (provenance:
  dispatch) + 3 pane-3 verified instances with denial strings.
- Test 3/3 (planted negative: entry without safe alternative refused).

## Ledger line

SECTION 23 dcg explain-before-override — PASS — `rm-rf-root-home` denial quoted + explicit single-file alternative quoted + 3/3 tests — NO-CLAIM: 5 conductor cases taken on stated provenance; rule is prose + structure, not enforcement.

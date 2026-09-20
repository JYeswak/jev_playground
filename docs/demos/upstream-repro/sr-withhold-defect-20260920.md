# REPORTABLE (NOT FILED) — sr fails closed to an empty roster on default-shaped Claude stores

Status: written for Joshua's filing decision. Per repo rule, no report goes out from the
vendored clone; this file lives in our tree. Do not file without his explicit call.

## The defect

`sr rank` advises on nothing — `empty-roster`, exit 5 — on any skill store that (a) holds more
than 10,000 enumerated files, or (b) contains a single symlinked skill directory. Either
trigger alone zeroes the entire roster. Both are the default shape of a real Claude skill
store, so sr cannot serve as a routing layer on any machine with enough skills to need routing.

## Repro (sr 0.1.0, skillranker @abf909d, one machine, no key needed)

```
# 1. Baseline: 651-skill store, 23,100 files, 72 symlinks
sr roster --json
# → exit 0: verified=0 unverified=531 advisory=0 partial=true
#   record_causes={malformed-metadata:14, unsupported-layout:167}
#   source_causes={entry-limit:1, source-not-enumerated:2, symlinked-directory-skipped:50}
echo '{"schema_version":1,"harness":"claude_code","producer_id":"x","workspace_root":"/tmp/sr-ws",...}' > ctx.json
sr rank --context ctx.json --offline --json
# → exit 5 empty-roster "No skills in the observed roster could be admitted"

# 2. Control: 3 valid skills, neutral cwd → withhold does NOT fire
HOME=/tmp/sr-home sr rank --context ctx.json --offline --json   # cwd /tmp/sr-ws
# → exit 11 cache-miss, roster block eligible:3 wide_candidates:3

# 3. One-symlink control: same clean HOME, cwd with one symlinked skill dir
HOME=/tmp/sr-home sr rank --context ctx.json --offline --json   # cwd has .claude/skills/LINK
# → exit 5 empty-roster, unverified-visibility (3)
```

## Mechanism (file:line, all skillranker @abf909d src/)

- Walk bound `DISCOVERY_FILES` = 10,000 entries (`src/limits.rs:296-297`); exceeded →
  `EntryLimitReached`, enumeration stops (`src/roster/discovery.rs:450-452`).
- Symlinked dirs are never descended, each skip noted (`src/roster/discovery.rs:477-494`).
- Any diagnostic except `RootMissing | SourceNotEnumerated` sets `discovery_withhold` →
  **all** entries forced `Visibility::Unverified` (`src/roster/resolution.rs:530-540`) →
  `ExactResolution::Unverified` (`:320`) → trace-excluded (`src/roster/evidence.rs:216`) →
  eligible 0 → `empty-roster` (`src/output/mod.rs:138`).

## Why it matters (not misconfiguration)

Symlinked skill dirs are the ecosystem's sharing mechanism (e.g. skills linked out of a
managed share dir); a 651-skill store with nested references/scripts exceeds 10k files by
2.3×. The design comment ("withhold authority globally", `resolution.rs:525-529`) is
defensible for shadowing-soundness but its blast radius is total: one skipped link revokes all
authority, including for the 531 cleanly-resolved skills. Suggested upstream shape (not a
patch): downgrade to per-name withhold (already the pattern for failed reads,
`resolution.rs:541-548`) or admit-and-flag instead of exclude for enumeration gaps.

## Related (same session, separate)

Alias-guard false positive: `src/roster/frontmatter.rs:354-363` rejects any frontmatter line
containing `" *"` as a YAML alias, which kills valid `allowed-tools: Bash(name *)` globs that
Claude itself writes (socraticode, jsm, skill-builder verified by single-record import).
Real YAML parsers accept these files. Reportable alongside or separately.

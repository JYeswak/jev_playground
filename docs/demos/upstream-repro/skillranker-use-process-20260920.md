# Getting our skills qualified: the tested process (2026-09-20)

Read his README first (raw `main`, 2033 lines), then tested every claim
below with the installed `sr` 0.1.0 (pure `0e61cc6` source build).

## Why our skills don't rank today

All 531 discover as `claude_code.user` / Unverified → ineligible (ranking
needs provisional-Verified + agent-invocable). Our flat `.md` files are not
skills to `sr` at all (`unsupported-layout`); only `SKILL.md` directories
count. His README states this plainly: every rank result carries
`"visibility": "unverified"` because the precedence lacks conformance
evidence — unverified is the honest state, not a bug.

## The process that works (executed, exit 0, live Jev calls)

Per his Quick Start (demo → key → doctor/roster → context → dry-run →
rank), in a workspace with a **project** `.sr/config.toml`:

```toml
[roster]
roots=['custom']   # workspace-relative SKILL.md dirs
```

```bash
sr rank --context context.json --allow-network --json --top 5
```

Measured on our real skills (copied, unmodified):
- "make X work / fix the feature" → `focused-fix` #1
  (fits 0.88, wide 0.96, rerank 0.99, conf 0.95, 2 paid calls).
- phishing task → `phish-guard` #1 (conf 0.98) — discriminates, USEFUL.
- repeat: identical spend, hit=false pre-cache (mac cache now works
  upstream; post-live ranks hit).

## What does NOT work (tested, reproducible)

User-config `roster.roots` (`~/Library/Application Support/sr/config.toml`,
absolute dirs): parses (`doctor --config` shows it from `trusted-user`)
but yields zero eligible skills — empty-roster with and without a project
config present, single root or whole dir. Project-config roots work in the
same runs. Either a bug in user-root handling or a doc gap; unfilable from
here (native-binary rule, no darwin binary). Machine restored (test config
removed).

## So how do we use it

Per-repo project config declaring that repo's skill dirs, then `sr rank`
before dispatching agents. No harness changes, no reformat of our library
needed for SKILL.md skills. Flat-.md files stay out of scope until upstream
supports the layout (their decision, not ours to patch).

## Ledger line

USE sr-project-roots — DONE — real skills rank #1 USEFUL, user-roots path
broken-but-unfilable — NO-CLAIM: 3 tasks judged, not a benchmark.

---
condition: '\b(is|are|was|were)\s+not\s+(installed|configured|wired|enabled|available|present|running|reachable|mounted|registered|discovered)\b|\b[A-Z][A-Z0-9]*_[A-Z0-9_]{2,}\b[^.!?\n]{0,40}\b(is|are|was|were)\s+(missing|absent|unset|not\s+(set|found))\b|\b(key|token|credential|secret|binary|command|tool|server|index|hook|extension|skill|package|module|dependency|mcp|api|daemon|corpus|database|endpoint)\b[^.!?\n]{0,50}\b(is|are|was|were)\s+(missing|absent|unset|not\s+(set|found))\b|\b(no such|does not exist|NOT INSTALLED|returned MISSING|reports MISSING)\b'
scope: text
interruptMode: never
repeatMode: after-gap
repeatGap: 10
---
**You are about to assert ABSENCE. Name the probe that produced it, and name a second one that could have found it.** A negative result from one probe is `UNMEASURED`, never `ABSENT`.

This is this lane's dominant defect class — **25 files in this repo document an instance**, and four landed on 2026-09-20 alone:

- `command -v morph` → "MISSING". Wrong: morph is an **MCP server**, and the probe cannot see MCP servers. Three panes were told a live capability did not exist.
- `/tmp/.tskey` absent + `$TYPESAFE_API_KEY` unset → "no key". Wrong: it is in Infisical. `.env.example` records that **three earlier agents made the identical false report**; that made four.
- `ee tripwire list` = 0 → "preflight cannot work". Overturned by reading the source: a `matches.is_empty()` early return at `cli/mod.rs:25807`, and a TOML **did** open `matchedMemories`.
- `get_state` listed no MCP tools → "not discovered". Wrong: `get_state` **does not enumerate MCP tools at all**. The oracle was invalid, not the wiring.

Already-paid-for instances, same shape: `TIMEOUT_UNMEASURED` is never `ABSENT` (`AGENTS.md`, RPC); an **empty scan set is an ERROR**, not a pass (`ubs` exit 3); **absent is not broken** — a gitignored source RED-ed `gates.sh` for every stranger (`190664d`); *"my probe was profiles-only"* (`8d5f20b`, a retraction of a retraction).

Before the claim ships, one of these must be true:
1. **Two probes of different kinds disagree with absence** — a binary AND a config surface, a file AND a service, a CLI AND its source.
2. The claim is downgraded to `UNMEASURED (probe: <the exact command>)`.
3. You read the code that would have to contain it.

INVARIANT rule, not a defect rule: it never asserts you are wrong, so it has no false-positive rate in the usual sense — it asks you to name the probe, which is cheap and always in-scope. Prevalence in assistant text is **UNMEASURED**: the 78,242-record harvest is `tool=bash` only and cannot see prose. RETIRE when a cass-indexed text corpus shows the class below 50 occurrences in 30 days.

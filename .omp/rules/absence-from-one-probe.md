---
condition: '\b(is|are|was|were)\s+not\s+(installed|configured|wired|enabled|available|present|running|reachable|mounted|registered|discovered)\b|\b(key|token|credential|secret|binary|command|tool|server|index|hook|extension|skill|package|module|dependency|mcp|api|daemon|corpus|database|endpoint)\b[^.!?\n]{0,50}\b(is|are|was|were)\s+(missing|absent|unset|not\s+(set|found))\b'
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

INVARIANT rule: it never asserts you are wrong, only that you name the probe.

**Measured 2026-09-20 in the corpus that can actually see prose** — 1,841 omp session JSONL files, **45,103 assistant-text turns**, not the 78,242-record bash harvest, which is `tool=bash` only and is blind to this class. Shipped predicate: **185 fires, 0.4102%**. Hand-labelled n=20, seed `20260920`, one labeller: **FP 0.20** — the four false ones were absence of *data* (bead ownership state, text spacing, mutation coverage, a matrix row), never of a capability.

**Two tiers were measured and REFUSED, and dropping them removed 66% of all fires:**
- `no such` / `does not exist` — **332 fires, 0.7361%**, the single largest source and almost entirely *file-path* claims, where one `ls` genuinely is sufficient. A rule that fires there teaches readers to ignore it.
- `NOT INSTALLED` / `returned MISSING` (7) and `SCREAMING_CASE … is missing` (47) — **both below the 50-occurrence floor.** The second one is what would have caught `TYPESAFE_API_KEY is missing`; it is refused here anyway and the coverage is kept by the separate ROUTING rule `jev-key-canonical-source.md`. Bending the floor for a case I personally hit is gate self-weakening.

RETIRE when a 30-day window over the same corpus shows this predicate below 50 occurrences.

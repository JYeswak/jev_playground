# P3 (Muse) — the depth-forcing rule pack: derived, structural, portable to any repo

**MISSION:** Validate Jev → build tools → **liven omp surfaces** → **dogfood** → **publish.**
Your unit is stages 3–4, and it is the one Joshua named directly:

> *"rules that force us to / guide us to go deeper and use the plethora of skill and alpha we have"*

We own 651 skills, a 221-repo mirror behind `fh`, 225 receipts, and a `NEGATIVE_EVIDENCE.md` with
50+ numbered refutations. **None of it shows up at the moment it is needed.** Prose in AGENTS.md
does not fire. TTSR does: it injects at the exact tool call. That is the vehicle.

## The four-leg loop, measured (`map-hook-ee-20260920.md:210`) — know which leg you are building

| leg | mechanism | state as of 2026-09-20 |
|---|---|---|
| DETECT | `guard-rule.ts` `pi.on('tool_call')` | LIVE — 200 rows, 10 installs |
| RECALL | `ee preflight check` | **LIVE BUT EMPTY** — `ee remember` output never reaches `ee preflight` |
| **SUGGEST** | **TTSR rules** | **LIVE — 2 rules, proven firing in a real pane (`002bb6f`)** |
| WRITE-BACK | `ee remember` | proven live in `jev/.ee`; the journal hook has emitted 0 |

**You own SUGGEST.** Two rules is a demo. A pack is the deliverable.

## The spec, read it before you write a rule (`read omp://ttsr-injection-lifecycle.md`)

The surface is richer than the two rules we shipped use:

- **`condition`** — regex, works on every scope.
- **`astCondition`** — **ast-grep patterns**, evaluated only on tool-argument streams that carry a
  file path (edit/write). This is the structural leg and we have used it **zero** times. The 27
  builtin rules use it (`go-bench-loop`, `go-range-int`, `go-new-expr`) — read `omp ttsr list` and
  copy the shape.
- **`scope`** — `text`, `thinking`, `tool`, `tool:bash`, `tool:edit(*.rs)`. Default monitors text
  and tools, **not thinking**. A rule that should catch a bad plan must opt into `thinking`.
- **`globs`** — a global path gate.
- **`interruptMode`** — `always` | `prose-only` | `tool-only` | `never`. **`never` on a tool match
  folds a `<system-reminder>` into the tool result instead of aborting the stream** — that is the
  low-friction mode for guidance rules, and nothing we ship uses it yet.
- **`repeatMode`** — `once` (default) | `after-gap` + `repeatGap` turns. **A guidance rule that
  fires once per session is very different from one that nags; choose deliberately and say why.**
- **`agents`** — glob scoping per agent name.

The honest mechanism (`ttsr-live-proof-20260920.md`): **injection, not enforcement.** The command
still runs; the agent complies or does not. Do not write a rule whose value depends on blocking.

## Unit 1 — mine the depth classes. DERIVED, never invented.

The method is fixed and it is the one that caught a 67%-FP predicate that had already passed the
rate bar (`suggest-leg-mining-20260920.md`). **Skipping a step is how four wrong numbers got
produced in one day.**

1. **Preregister the bar IN THE FILE, before measuring.** Ours: a class firing above **~5% is
   wallpaper**; a class below **50 occurrences is too rare to be a rule**.
2. **Build the corpus you did not author.** Available:
   - `work/toolcall-judge-v3/real-allowed.json` — **78,242 real commands** (50 MB, gitignored,
     moving — quote your count and the date, it drifted 77,767 → 78,242 inside one hour).
   - `fh search "<mechanism>"` over the mirror — the **doctrine** rows (`C71`-style) are the alpha.
     `fh why <row>` for provenance. **`fh` is a first-class corpus here, not a fallback.**
     `fh doctor` reports `STALE ledger_age_hours=305.7 threshold=26` — that is a **freshness
     signal about the refresh cron, not a discount on the evidence.** Mined doctrine from a
     221-repo corpus does not rot in 12 days; a defect Jeffrey paid for in June is still a defect.
     Record the age as metadata. Staleness only invalidates a claim about **movement** (what
     changed upstream lately), so do not use `fh` alone to assert recency.
   - `NEGATIVE_EVIDENCE.md` — 50+ refutations we paid for. **A rule derived from an R-number is
     the highest-grade rule we can write**: the defect is already proven, the cost already paid.
   - `docs/demos/upstream-repro/` — 225 receipts.
3. **Hand-label a seeded sample** (n≥20, record the seed). Report FP. **The rate alone ships bad
   rules.**
4. **State prevalence beside the score.**
5. **Report the verdict a non-author can check.**

**The classes to go after — depth, not syntax.** We already cover two bash-hygiene classes. What
is missing is the class Joshua named: *going shallow when we own the deep tool*. Candidates to
test (prove or refuse each, do not assume):

- reading files one-by-one when `ripwire <dir>` would have mapped it — detectable as a burst of
  `read` on one directory with no prior `ripwire` in the session
- `rg`/`grep` used for a **structural** question that `ast-grep` answers (a pattern containing
  code punctuation: `fn `, `=>`, `impl`, `function `, `class `)
- a `write`/`edit` creating a `*_v2`/`*_improved`/`*_enhanced` file — AGENTS.md forbids it and
  prose has not stopped it
- a claim verb (`verified`, `confirmed`, `works`) in assistant **text** with no preceding command
  in the turn — scope `text`, this is the proof-class-inflation rule
- `git add -A` / `git add .` — `dcg` denies it, but the rule teaches *why* at the moment
- a new `.sh` in `scripts/` when the house shape is a directly-runnable command
  (`skillranker@3fe85c4` ships zero `.sh` outside one `run.sh`)
- **the routing rule**: a task naming a domain we own a skill for, where the skill was never read

The last one is the crown jewel and the hardest: it is the bridge from TTSR to our 651 skills and
to `sr`. **P2 is mining `sr` for exactly the ranking question this rule would ask.** Coordinate
with pane 2 before you build it; do not duplicate their work.

## Unit 2 — ship them, with arms, and keep the pack portable

- Rules land in `.omp/rules/<name>.md`. **Every new rule MUST get arms in
  `scripts/selftest-ttsr-rules.sh`** — one fire on a known-bad, one **quiet on a near-miss** that
  differs by exactly one element of the defect. The script currently asserts `n_rules -eq 2` and
  will go RED the moment you add a rule: **that is the forcing function, not a bug. Update it.**
- Prove each rule with `omp ttsr test --rule <file> --source tool --tool bash '<cmd>'`.
- **Every rule carries a retirement condition** in its own text (ours: a 30-day harvest window
  showing the class below 50 occurrences).
- **Portability is the point** (`"advanced systems we can use across any project"`): the pack must
  install into a repo that is not `jev`. Keep rules free of jev-specific paths, and state which
  ones are inherently repo-local. An installer is in scope if you have time; the ruling on what is
  portable vs local is required either way.

## Acceptance

- receipt `docs/demos/upstream-repro/depth-rule-pack-<YYYYMMDD>.md`
- **positive:** each shipped rule fires on its known-bad via `omp ttsr test`, with prevalence + a
  hand-labelled FP from a seeded sample
- **planted negative:** each shipped rule stays **quiet** on its near-miss; and at least one
  candidate class must be **REFUSED** with its number — a mining pass that ships everything it
  touched did not have a bar
- `./scripts/selftest-ttsr-rules.sh` green with the new arms
- **NO-CLAIM:** one corpus, one machine, one labeller; and state that TTSR **injects**, it does not
  enforce
- commit `[test]`/`[mutation]`; commit on create

## Standing orders

- **Four retrieval tools, and the rule you write about them must match how they actually differ.**
  This is derived from Jeffrey's own corpus (`84 of 113` repos reference `warp_grep`; the clearest
  statement is `dicklesworthstone-mirror/chat_shared_conversation_to_file/AGENTS.md:308`):
  **`morph codebase_search`** for broad *"how does X work / where does this data flow"* questions;
  **`rg`** when you already know the identifier; **`ast-grep`/`sg`** for structural match and
  rewrite; **`ripwire`** to rank and map a tree cold, before opening files one at a time.
  **You are writing rules about tool discipline — use the tools, and encode that split.**
- Exit codes from an **unpiped** run. Report every TTSR interrupt you receive, with the rule name:
  you are dogfooding the leg you are building.
- Never `git add -A`. Stage explicit paths. `.omp/rules/` and `scripts/selftest-ttsr-rules.sh` are
  shared — reserve them, and tell pane 1 before you touch `selftest-ttsr-rules.sh`.
- **`morph` IS live — I wired it during this dispatch and proved it.** It is an MCP server, not a
  binary, so `command -v morph` is the wrong probe and my first packet was wrong. Now registered
  at **project scope** in `jev/.omp/mcp.json`, so it loads under every profile in this repo.
  Six tools: `codebase_search`, `github_codebase_search`, `reflex_{list,predict,summary,traces}`.
  **`edit_file` is force-disabled and the npm version is pinned at `0.8.212`** — morph is
  **RETRIEVAL ONLY** here, deliberately: two editors racing one worktree nearly cost 660
  uncommitted lines on 2026-09-08. Proof: a fresh `omp -p` session returned `MORPH-OK`.
  **Your session started BEFORE this landed, so you do not have it yet** — MCP mounts at session
  start. Use `/mcp` to reload, or note that you worked without it.

**Callback:**
`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. SHIPPED <n> REFUSED <n>. NEXT <unit>. NO-CLAIM <limit>."`

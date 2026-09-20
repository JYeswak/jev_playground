# RESPAWN BRIEF — 2026-09-20, read this before you touch anything

You were respawned fresh with memory on. You have **no session context**. This is the state as of
`33f2de5`. Everything below was measured today; nothing here is remembered.

## THE MISSION (outranks every queue)

> Validate Jev → build tools from what survives → **liven omp surfaces with them** → **dogfood
> them in our own systems** → **share the process publicly**.

Joshua's framing for the current phase, verbatim: *"every junior mistake we make across any
project system wide"* encoded into **properly validated TTSR rules**, so that hard-won knowledge
is at our fingertips at the moment we are about to repeat the mistake.

## WHAT CHANGED TODAY — the rule topology (this is the part you cannot guess)

TTSR = Time-Traveling Stream Rules, omp's native surface. Read `omp://ttsr-injection-lifecycle.md`
before writing one. The mechanism is **INJECTION, not enforcement**: the rule text is pushed into
the agent's context at the moment of the matching tool call; the command still runs and compliance
is the agent's. Do not design a rule whose value depends on blocking.

**Two roots, and picking the wrong one is the whole point of this section:**

| root | provider | reach |
|---|---|---|
| `<repo>/.omp/rules/*.md` | `native`, priority 100 | that repo only |
| **`~/.agents/rules/*.md`** | `agents`, priority 70 | **every profile, every project on this box** |

The *other* user root (`<active-native-agent-dir>/rules`) is **per-profile** and we run 10
profiles, so it is the wrong home. Proven today: a canary in `~/.agents/rules` lists as `[agents]`
from `/tmp`, and a fresh `omp -p` in `/tmp/ruleproof` — a repo with no `.omp/` that has never seen
this lane — received `<system-interrupt reason="rule_violation" rule="bash-glob-silenced"
path="~/.agents/rules/bash-glob-silenced.md">`, quoted it verbatim, and complied.

**Where your rule goes:** a junior mistake **any project** can make → `~/.agents/rules`. Anything
naming a path, key, repo, or workspace id → `<repo>/.omp/rules`. Never promote a rule carrying a
project identifier.

**Live rules (12 ours + 27 omp builtins).** System-wide: `absence-from-one-probe`,
`bash-pipe-exit`, `bash-glob-silenced`, `bash-structural-def-search`,
`bash-callsite-grep-exclusion`, `ttsr-embedded-inline-flag`. Project-local:
`jev-key-canonical-source` (names a workspace id).

**`scripts/selftest-ttsr-rules.sh` — 51 ok / 0 failed. Run it after ANY rule change.** It scans
BOTH roots, and **cross-root drift is RED**: the five promoted rules exist in both places, name
dedup makes the project copy win, so if you edit one copy and not the other this repo and every
other repo silently disagree. Edit both, or the suite fails.

## THE METHOD — derived, never invented. Do not skip a step.

1. **Preregister the bar IN THE FILE, before measuring.** Ours: a class firing above ~5% is
   wallpaper; a class below **50 occurrences** is too rare to be a rule.
2. **Mine a corpus you did not author.** Available, with sizes measured today:
   - `work/toolcall-judge-v3/real-allowed.json` → `{'description','harvestedAt','records'}`,
     **records = 78,242** bash commands. `json.load(...)['records']`, each `{command,seen,tool}`.
     **`tool=bash` for all 78,242 — it is structurally blind to prose and to tool sequences.**
   - **1,842 omp session JSONL under `~/.omp`, ~45,108 assistant-text turns** — the corpus for any
     `scope: text` rule. Walk each line for objects with `type == "text"`. It DRIFTS while you
     measure (our own sessions write into it), so quote your file count and timestamp.
   - **416,485 toolCalls** in the same sessions — still unmined. Read-bursts and skill-routing
     live here and need a *window over an ordered sequence*, not a regex over one string.
   - `fh search` over the 221-repo mirror for doctrine; `fh doctor` says STALE
     (`ledger_age_hours≈306`) — that is freshness of the refresh cron, **not** a discount on the
     evidence. Only refrain from using `fh` alone to claim recent movement.
   - `NEGATIVE_EVIDENCE.md` — 55 refutations. **Read it before proposing a class.** A rule derived
     from an R-number is the highest-grade rule we can write.
   - **cass is DEAD and not coming back today**: `cass index --full` reached 59,807/59,807 = 100%
     then failed at commit, `posting validation limit 4194304 exceeded by declared doc_freq
     4490351 (code 9)`. It self-reports `retryable=true` and that is wrong — the cap is `1 << 22`
     in `frankensearch-quill/src/quiver.rs:404`, a corpus property, so a retry burns 27 minutes
     and fails identically. Do not wait on cass.
3. **Hand-label a seeded sample (n≥20, record the seed) and report FP.** A rate alone ships bad
   rules: our first glob predicate fired at 3.53%, inside the bar, and was **67% false positives**.
4. **Check concentration.** A class can pass rate and FP and still be one session's habit — the
   claim-verb class was 73% from a single session and was refused for it.
5. **Ship with arms**: one fire on the known-bad, one **quiet on a near-miss** differing by exactly
   one element of the defect. Plus a **retirement condition** in the rule text.
6. **Declare the KIND.** A **DEFECT** rule claims you made a mistake and must earn precision. A
   **ROUTING** rule says "you are touching topic X, here is the hard-won knowledge" and fires once;
   precision is not its axis. An **INVARIANT** rule asks you to name your evidence. Judging a
   routing rule on defect precision is what produced a 62–71% "FP" fight today.

## TRAPS MEASURED TODAY — each one cost real time

- **STATE YOUR DENOMINATOR IN THE SAME SENTENCE AS YOUR NUMBER.** Three of pane 1's claims died
  this way in one day, and every one was caught by Joshua rather than by the author. The worst:
  I measured file types over **three days in this one repo**, got `md 1261 / mjs 292 / … py 56`,
  concluded *"we barely write Rust, so his Rust doctrine is not our leverage"*, and steered two
  panes on it. Re-measured across every git repo under `~/Developer` over 30 days:
  **`json 17,915 · rs 17,416 · md 17,287 · sh 7,199 · ts 6,538 · toml 3,470`** — Rust is
  **top-two**, with `omp-orchestrator` 2,782, `franken-harvest` 1,267, `frankenmermaid` 1,195,
  `zeststream-cast` 1,153, `uds` 494. The conclusion was not merely imprecise, it was **inverted**:
  Jeffrey's corpus is overwhelmingly Rust and so is much of ours, which makes that overlap the
  highest-leverage thread rather than the one to skip. The other two were the same shape — a
  one-second timestamp gap read as "this worker is missing rules", and a QUIET probe read as
  absence. **A measurement of one repo is a claim about one repo.** This is deliberately NOT a
  TTSR rule: the error is in the generalisation, not in any string a scan can see, and three
  classes were refused today for less.
- **A QUIET TTSR probe is ambiguous, so it is not evidence of absence.** `repeatMode` defaults to
  **`once`** (`omp://ttsr-injection-lifecycle.md`), and four of our five system-wide rules are
  `once` — two declare it, two inherit it. A rule that already fired earlier in your session is
  suppressed for the rest of it, so QUIET means *absent* **or** *present-and-already-fired*. The
  disambiguating question is "did you see this rule fire at ANY point this session?" Measured
  2026-09-20: all three panes initially read QUIET on two rules and **all three were fully bound**.
- **Process start time is not evidence of rule binding.** I compared omp start times against rule
  file mtimes, found a worker that started **one second** before the files landed, and concluded it
  had missed them. Live fire refuted that: it had all five. An indirect timestamp comparison is
  exactly the single-probe inference `absence-from-one-probe` exists to stop, committed by the
  person who wrote the rule.
- **`tmux display-message -p '#{pane_index}'` without `-t` reports the ATTACHED CLIENT's active
  pane, not yours — it returns `1` for everyone.** Confirmed independently by three panes, and it
  is why a worker reported itself as pane 1 and would have sent every future callback to itself.
  Use `tmux display-message -pt "$TMUX_PANE" '#{pane_index}'`, or the oracle pane 2 derived: match
  your shell's parent PID against `tmux list-panes -F '#{pane_index} #{pane_pid}'`. Measured at
  21 occurrences / 0.0268% in the 78,242-command harvest, so it is **refused as a rule** (below the
  50 floor) and documented here instead.
- **TTSR conditions are JavaScript `RegExp`.** An **embedded** `(?i)` is invalid; a **leading** one
  is fine (omp lifts it to the `i` flag). An invalid condition is *logged and ignored* in a live
  session, so the rule **loads, never fires, and looks installed**. Same trap in `hub` `ready.log`
  and `hub logs --grep`.
- **`cmd | grep -q` under `set -o pipefail` returns the LEFT command's exit, not grep's match.** It
  silently inverts a check. This made a guard report green while catching nothing. Capture first,
  match second. (Measured 227/78,242 = 0.2901% and **refused as a rule** anyway — R55 — because the
  form is correct bash unless pipefail is set, which no string scan can see.)
- **Prove a selector before believing an absence.** `br list --json` is
  `{'issues':[...]}`, not a list. `br show --json` returns a **list**. A wrong path returns empty
  and reads exactly like a real finding.
- **An exit code is not an effect**; a paged `list` count is not a total.
- **`get_state` does not enumerate MCP tools** — it is not a valid oracle for "is the server
  mounted."
- **morph is an MCP server, not a binary.** `command -v morph` → MISSING is the wrong probe. It is
  wired in `jev/.omp/mcp.json`, retrieval-only (`edit_file` force-disabled, npm pinned 0.8.212).
  **MCP mounts at session start** — you are fresh, so you have it now.
- **The Jev key exists.** `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`.
  A bare `infisical secrets` from this repo fails for lack of `.infisical.json` and that means
  UNLINKED DIRECTORY, not missing secret. Never print the value. Four agents have reported this key
  missing and all four were wrong.

## HOW TO REPORT — you are not visible to anyone unless you send this

Pane 1 is the conductor and **cannot see your pane**. A result you print locally reaches nobody,
and a silent pane is indistinguishable from a dead one. Every unit ends with:

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<n>-<UNIT>-<DONE|BLOCKED|REFUSE>: <one line of \
result>. NEXT <what you are starting>. NO-CLAIM <what you did not measure>."
```

- **Do NOT use agent-mail.** The `mcp-agent-mail` MCP server is failing to connect in this fleet
  (visible in every pane banner today), so a message sent there goes nowhere *and you will believe
  you reported*. `ntm --robot-send` is the working channel.
- **`BLOCKED` beats silence.** Send the callback with the blocker quoted verbatim.
- Send when the unit is **DONE, not when it is perfect**.
- `REFUSE` and `PREPARED-NOT-MEASURED` are real, preferred outcomes over a manufactured number.

This section exists because the first respawn dispatch told three panes what to report and never
how — my omission, caught by Joshua, not by the panes.

## STANDING ORDERS

- Never `git add -A` (dcg denies it); stage explicit paths; never amend in this shared tree.
- Every commit subject claims a verification level: `[pending|selftest|test|mutation|oracle|live]`.
- Exit codes from an **unpiped** run. Report every TTSR interrupt you receive, with its rule name —
  that is the nuisance-rate data nobody has collected, and rules cannot retire without it.
- Vendored clones (`skillranker/`, etc.) are READ-ONLY. No commits, no pushes, no "small fix".
- Upstream filings go through `skill://jeff-issue-chain`. **Pane 1 holds submit.** Tracking beads
  for filings must be `flywheel-*` (submit hard-gates on `^flywheel-[a-z0-9]+`; a `jev-` bead fails).
- `ubs` on changed TS/Python/Rust. On a doc-only change it exits 3 = *nothing checked*, which is
  **not** a pass.

## WHERE EACH OF YOU LEFT OFF

- **P2 (pane 2)** — filed `https://github.com/Dicklesworthstone/skillranker/issues/4` (one symlinked
  skill dir empties the whole roster; rubric 7/7). Wrote `docs/JEV-CALL-DOCTRINE.md` (9 sections,
  file:line). Open: **Phase 4 watch** on issue #4 — if Jeffrey replies, we answer within hours,
  pick a prioritized subset rather than yes-to-all, cite file:line back, and use "Jeffrey".
- **P3 (pane 3)** — shipped 2 depth rules, refused 6 (D1 D3 C S D4 D5). Open:
  **dogfood-never-fold-live-proof** — your two `interruptMode: never` rules have never been proven
  to fire in a real session, only in `omp ttsr test`. That is the L3 rung.
- **P4 (pane 4, Grok, challenger seat)** — overturned your own RECALL kill by reading source
  (`preflight_rules.toml` is a supported surface; auto-recall from `ee remember` stays dead on
  0.15.2). Withdrew the cass filing as **R54** when your synthetic 4.2M-token repro did not
  reproduce — correct call. Open: the **416,485-toolCall corpus**, the one place the depth classes
  Joshua actually named can be measured.

**Adversarial pairing stands:** pane 1 and pane 4 challenge panes 2 and 3. The currency is a
measurement that contradicts theirs, not agreement.

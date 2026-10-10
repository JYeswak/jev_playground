# AGENTS.md — jev

> Guidelines for AI coding agents in the jev lane: Jev (TypeSafe System One) turned ON in the tools
> we actually use, proven live, and kept runnable by a stranger.

Right-sized on 2026-09-30 with `fh agents` (Dicklesworthstone corpus: median 852 lines, p90 1,203;
the previous 2,047-line file exceeded the corpus maximum and cost ~32k tokens in every session).
The full prior text, every incident narrative and rule history included, is preserved verbatim at
`docs/history/AGENTS-2026-09-30.md` (sha256 `afef1c40…`). Refuted hypotheses live in
`NEGATIVE_EVIDENCE.md`; the run ledger is `EVAL.md`.

## The Rules — the non-negotiables

### Conventions

This list is the convention contract; a reviewer grades a change against it. Language and
formatting conventions come from each tree's own toolchain.

1. **Joshua's word overrides this file.** (RULE 0)
2. **Never delete a file without written permission** — including one you just created. (RULE 1)
3. **Never break glass:** no `git reset --hard`, `git clean -fd`, `rm -rf` without the exact command
   from Joshua in the same message.
4. **Never push, PR, or commit inside a vendored clone.**
5. **The key never enters the tree, a log, a fixture, or a message.**
6. **`main` only; stage explicit paths; never amend; every commit subject names its verification
   level.**
7. **Edit in place; no `_v2` files; never patch upstream to make a demo pass.**
8. **On and tested beats documented.** A capability counts when it is ON in a real session and
   tested both ways. A document, audit, or certificate about it does not.
9. **Name the evidence:** lane (offline / live / local), N, date, model id, spend. No bare
   "verified".
10. **Adopt from the mentor by default** (Jeffrey Emanuel, `Dicklesworthstone`); every pane may read
    and run his repos.
11. **Derive test fixtures from real observations;** never type them from imagination.
12. **No paid comparator models.** Live Jev calls are allowed when bounded.
13. **Locate files with `find`, not `grep`.** Measured 576 vs 5,297 tokens per located file fleet-wide (jev-04q2); 404 vs 1,861 at equal success in a controlled A/B (jev-ynn7, verified). `grep` is for searching file contents.

---

## RULE 0 - THE FUNDAMENTAL OVERRIDE PREROGATIVE

If I tell you to do something, even if it goes against what follows below, YOU MUST LISTEN TO ME. I
AM IN CHARGE, NOT YOU.

## RULE NUMBER 1: NO FILE DELETION

**YOU ARE NEVER ALLOWED TO DELETE A FILE WITHOUT EXPRESS PERMISSION.** Even a new file that you
yourself created, such as a test code file. You must always ask and receive clear, written
permission before deleting a file or folder of any kind. `.venv/`, `node_modules/`, caches and
build output are still files: cheap to rebuild is not the same as yours to delete.

## Irreversible Git & Filesystem Actions — DO NOT EVER BREAK GLASS

1. **Forbidden:** `git reset --hard`, `git clean -fd`, `rm -rf`, or any command that can delete or
   overwrite code/data, unless Joshua gives the exact command and says, in the same message, that he
   wants the irreversible consequences.
2. **No guessing.** If you are unsure what a command deletes or overwrites, stop and ask.
3. **Safer alternatives first:** `git status`, `git diff`, `git stash`, a copy to a backup.
4. **After authorization:** restate the command verbatim, list what it affects, wait for
   confirmation, and record Joshua's exact authorizing text, the command, and the time.

---

## The Mission

**Plan of record: [`ROADMAP.md`](ROADMAP.md) "Mission" (approved by Joshua 2026-10-04; machine form
`.omp/mission.toml`). It wins where this section disagrees. Every open bead carries a `pillar:` label;
a failure in shared tooling goes to omp-kit (%54), never a local-only patch.**

> **Typed classifiers that earn their place in our tools: each one proven live, measured, and
> delivered through one model-neutral CLI.** Its first pillar keeps the 2026-09-30 mission: turn Jev
> ON in the tools we use and prove it live, measured in our own session logs, with a README a
> stranger can run.

Joshua, 2026-09-30, verbatim: *"i want this on and tested - dont give me 'waiting for approval' bs -
i've given blanket approval to get this on and valuable and figured out"*.

**What counts as progress:**

- A capability that is **ON in a real session, tested both ways** (it fires on a positive and stays
  silent or refuses on a planted negative), with its effect readable from omp session files or a
  hook log.
- A measured Jev result: live calls (pinned `jev-1.13.0`, or a local System One model) on data we
  did not write, the bar fixed in a committed file before the first call, the spend stated.

**What does not count:** audits of our own README, ledgers or gates; new certificates, ledgers or
dashboards with no consumer; benchmark tourism; re-litigating a closed row. Before creating any
process artifact, apply `skill://just-say-no-to-process-porn-and-ceremony`: it must name a consumer,
the thing it gates, the observed defect behind it, and its retirement condition, or it does not get
built.

**Parked 2026-09-30** (beads deferred with reasons, receipts kept): the 0927 plan's P0–P15 and
U04–U07, README/LEDGER claim coverage, stage-15/80 gate repair, game and benchmark runs
(Jericho, PokéJev, MiniWoB, OSWorld), and the free-comparator arms. Reopen one only with a new fact
and a named consumer.

**Local vs paid.** Ollama 0.35 serves the same System One API locally (`/v1/systemone`; models
`nimble`, `tev1`), free and with no data leaving the machine. Use local where it matches
`jev-1.13.0` on our own recorded data and TypeSafe where it does not; each surface needs its own
check. Measured 2026-09-30 on 300 real text-only stops: TypeSafe flagged 8, nimble 110 (agreement
65%, kappa 0.07), so omp's smart stop stays on TypeSafe. Paid Jev costs about $3 a week for ~16k
native calls; cost is not the deciding factor, quality and latency are.

### What is ON

| Surface | Where | Jev decision | Status (update when it changes) |
|---|---|---|---|
| omp `find` tool | native, every profile with `modelRoles.judge` | ranks files and passages | ON: ~2,150 calls/day |
| auto-thinking | native, `defaultThinkingLevel: auto` | effort level per prompt | ON in default, claude, codex, muse, grok |
| smart stop | native, `features.unexpectedStopDetection: smart` | did the agent promise and stop? | ON 2026-09-30, proven live both ways |
| judge role | `~/.omp/agent/config.yml` + profile configs | backend for the three above | `typesafe/jev-latest`; key command-resolved in `models.yml`; local `ollama-sys1` provider declared, inert |
| project tools | `.omp/tools/*.ts`, `.omp/extensions/` | rerank, claim check, classify, gate, flag, screen | callable `xd://jev_*` devices |
| project hooks | `.omp/hooks/post/` | bash risk (gate-observe), web-result injection (webscreen), web_search pick (rerank) | live shadow on `jev-1.13.0`, capped per day, fail open, log only; injection-shadow on tool results in progress (`jev-asbl`) |
| claim rule | `.omp/rules/disabled/claim-without-evidence.md` | does a reply claim a result without evidence? | RETIRED 2026-10-01: held-out precision 0.571 vs a 0.80 bar (R130); outside rule discovery |
| fleet watcher | `scripts/fleet-idle-watch.py` (hub service) | is an idle worker waiting on a human? | ON again 2026-10-05T15:55Z (service fleet-idle-watch-12, nice 10) after the 2026-10-04 overnight pause; pages pane 1 on idle, needs-human (`jev-1.13.0` Noul), CI, stranger run, key exposure, and nudges an idle pane whose omp steering queue holds an undelivered message (`jev-of3b`) |

Scoreboard (bead `jev-4970`): `python3 work/omp-jev-review/surface-census.py --scoreboard --days 7`.

---

## Git Branch: ONLY Use `main`, NEVER `master`

All work happens on `main`. Never reference `master` in our code or docs. Never rename or force a
branch in a vendored clone. No branches or worktrees here (Joshua, 2026-09-23: *"i have a strict no
branch / worktree policy"*; `githooks/pre-commit` refuses commits off `main`).

`.gitignore` is an **allowlist**: it ignores `/*` and un-ignores what we author, so cloning prior
art needs no change. `docs-mirror/` and `upstream/` commit provenance (sha256 manifests), not bytes.

**Save only your work — every commit.** Several agents share this tree and its index.

1. **Reserve before editing** in Agent Mail (exact paths, bead id as the reason). `EVAL.md`,
   `NEGATIVE_EVIDENCE.md`, `GATES.md`, `README.md` and this file collide most.
2. **Re-read right before any line-anchored write;** a stale anchor lands elsewhere silently.
3. **Stage exactly your paths and read back the index:** `git add <path>...` (never `-A` or `.`;
   `dcg` denies it), then `git diff --cached --stat` must list only your paths.
4. **Commit on `main` without sweeping anyone; never amend.** `git commit --only <paths>` skips others'
   staged blobs but commits the WORKING-TREE file, so use it only on files that hold nothing but your
   edits. In a shared file with others' pending hunks (EVAL.md, ledgers), stage your hunk as an index
   blob (HEAD copy + your change, `git hash-object -w`, `git update-index --cacheinfo`), check
   `git diff --cached`, then `git commit` with no pathspec. Incidents 2026-10-01: 32d5c1ba, bc9fd2a0.
5. **The subject claims a verification level** (`commit-msg` refuses one without it), weakest first:
   `pending`, `selftest`, `test`, `mutation`, `oracle`, `live`. Claim the level you actually reached.

**Bootstrap a fresh clone:** `./scripts/sync-docs.sh && ./scripts/sync-docs.sh --check`.

## Toolchain: npm and uv

TypeScript/JavaScript: `npm` only (never pnpm, yarn or bun in these trees; lockfiles are part of
what we evaluate). Python: `uv` only (never pip, poetry, conda or a hand-made venv). Node is
`/opt/homebrew/bin/node`. Never add a dependency to a vendored clone or upgrade its lockfile.

### Key Dependencies

| Tree | Runtime deps | Notes |
|---|---|---|
| `kit/` | none beyond Node | the `jev` CLI and the omp installer |
| `work/jev-client/` | official `typesafe-sdk` | key provider: Infisical user session, then machine identity |
| `.omp/hooks`, `.omp/tools` | omp runtime | loaded at session start |
| `upstream/typesafe-ai/*` | their own | first-party SDKs and `system-one-adapter-python` |

Good Jev integrations have almost no dependencies: a client is an HTTP POST and a validator.

---

## Secrets and the Paid Surface (CRITICAL)

- **The key lives in Infisical,** never in this tree. Canonical form:
  `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <command>`. Presence check
  that never prints the value: `... -- sh -c 'echo len=${#TYPESAFE_API_KEY}'`. A bare
  `infisical secrets` here fails because `jev/` has no `.infisical.json`: that means *unlinked
  directory*, not *missing secret*.
- **omp profiles resolve the key by command** in `models.yml`
  (`apiKey: "!/Users/josh/.local/bin/infisical secrets get TYPESAFE_API_KEY ..."`): the file holds
  only the command, never the key.
- **Never** `echo` the key, `env | grep -i key` into captured output, or `set -x` around a request
  that carries it. Never commit a captured response body derived from real customer state.
- **Live Jev calls are allowed, attended or not.** Joshua, 2026-09-27, verbatim: *"we need to update
  agents.md to allow live-calling on jev - how can we validate & test what we're building without
  live calls"*. What makes a run safe is its shape: **bounded** (a fixed number of calls per run or
  day, written in the code), **no retry storm** (stop on 401/402/403 and after the SDK's retries),
  **checkpointed** (one row per call: model, tokens, latency, status), **spend stated**.
- **No paid comparisons.** Joshua, 2026-09-24, verbatim: *"we're not going to use any of the paid
  comparisons"*.
- **A comparator is a free OpenRouter model (`:free` id) or nothing.** No Anthropic model (Haiku
  or other), no grok or other xAI model, no paid OpenRouter model (`gpt-5-nano`,
  `deepseek-v4-flash`, any id without `:free`). Do not re-run a paid arm a cap or balance refused,
  and do not wait for a reset or a top-up. A paid pairing that never ran is reported as
  *not run (paid comparisons stopped 2026-09-24)*. Jev itself is not a comparator; local models on
  this machine (Ollama) cost nothing and fall outside this rule.

---

## Vendored Upstream Clones — Read-Mostly, Pinned, Never Pushed

- Each subdirectory clone is someone else's repository at the SHA it was evaluated at. Never
  `git push`, `gh pr create`, or commit inside one. Never `git pull` one without recording the
  `old -> new` SHA and re-running what you cite.
- Local diagnostic edits are allowed only while diagnosing, must show in `git -C <clone> diff`, and
  must be reported.
- **Forks, patches and issues are in scope** (Joshua, 2026-09-25: *"we can patch upstream forks to
  fix if we find issues"* / *"we can also submit issues to them"*). Fix on a fork under `JYeswak/`,
  never in the pinned clone; file the issue with evidence, deduped, one defect per issue.
- **Dicklesworthstone repos stay native:** no forks or patches; issues only through `jeff-issue.py`.
  Every pane may read, index, run and learn from the mirror at
  `/Volumes/ZestData/dicklesworthstone-mirror` and `fh` (Joshua, 2026-09-25: *"we can all read them
  - his projects are open source"*). Adopt the mechanism in our own tree; earn the number ourselves.

---

## Code Editing Discipline

### No Script-Based Changes

Never run a script that rewrites code files here; change them by hand or with parallel agents.

### No File Proliferation

Revise existing files in place. No `demoV2.ts`, `probe_improved.mts`, `client_enhanced.py`. A new
markdown file at the root is almost always the wrong artifact: the right one is an `EVAL.md` row, a
probe, or a diff where the capability runs.

### Never Patch Upstream To Make A Demo Pass

Wrap it in our code, fork it deliberately, report it upstream, or drop the demo and say why. Editing
a clone until green and citing its suite as evidence is the highest-value lie available here.

## Backwards Compatibility

Our own code has no users to protect: no compatibility shims, no wrappers for deprecated APIs, fix
it directly. Upstream's surface is the exception: `jev-latest` moves, so pin the model id
(`jev-1.13.0`) in anything we port.

---

## Verification Checks (CRITICAL)

Run the suite for the tree you touched:

```bash
node --test .omp/hooks/post/*.test.mjs .omp/hooks/pre/*.test.mjs .omp/tools/*.test.mjs   # hooks and tools
npm test --prefix kit                                  # jev CLI + installer
npm test --prefix work/jev-client                      # SDK client + key provider
python3 -m unittest scripts.test_render_results        # README results renderer
./foundation/gates.sh && ./foundation/gates.sh --selftest   # every stage proves its RED arm
ubs <changed files>                                    # TS/Python/Rust only; exit 3 on docs is NOT a pass
```

Vendored clones carry their own suites (`npm test`, `uv run pytest`); a failure there is a finding
about that clone, not a task to fix by editing it. Infrastructure failure (dead daemon, missing
worker, timeout) is UNSOLVED, never green.

## Testing

### Testing Policy

- **Inject the asker.** Every client takes its transport in the constructor, so policy, thresholds,
  validator and fail-safe direction are provable without calling Jev.
- **Test the policy, not the model.** Jev returns numbers; we own the thresholds, tie-breaks and the
  safe side. Name the fail-safe direction in the test name.
- **The validator refuses hostile answers:** `choice` in the offered ids, probabilities finite in
  `[0,1]` and summing to 1 within 0.02, the chosen option at the max; else refuse and act on nothing.
- **Offline and live are different claims.** A suite with no key runs the offline lane fully and
  reports the live lane `NOT_RUN`; "never ran" must never read like "passed". A live number carries
  N, date, model id and latency.
- **Derive test patterns, never invent them** (measured 2026-09-25: a typed fixture with
  `"color": "red"` passed while the real observations carried `bg_color`). Fixtures are captured
  from a real observation or row; assert the effect, not the input; every bar names its source
  (external benchmark, paired incumbent, recorded-row arithmetic, or vendor docs); check
  feasibility keylessly before spend (`python3 scripts/jev-state-size.py STATES.jsonl
  --question-bytes N` against the ~32k-token input limit).
- **Live L3 proof is a fresh session.** Hooks and extensions load at session start: prove one in a
  fresh `omp --mode=rpc` session or a restarted pane, both directions.

### Test Categories

Hooks: fires on the real event, bounded calls, secret skip, fail open, no raw text in logs, planted
negative. Tools and `kit/`: question construction, validator refusal, `NOT_RUN` without a key.
`work/jev-client/`: retry/timeout, key-provider order, spend accounting. `foundation/`: each RED arm.

---

## Third-Party Library Usage

Jev entered early access on 15 September 2026; your training data does not contain it. Read the
vendored sources from disk: `docs-mirror/typesafe/**` (TypeSafe's docs; start at `llms.txt`, grep
`llms-full.txt`), then `upstream/typesafe-ai/**` (official SDKs, `system-one-adapter-python`,
skills), then `awesome-jev/README.md`. Refresh with `./scripts/sync-docs.sh`, verify with `--check`.
A claim about Jev that cannot be traced to a file there is a guess and must say so.

| When you need | Read |
|---|---|
| the request shape | `docs-mirror/typesafe/introduction/quickstart.md`, `api.md` |
| which primitive; whether to act | `primitives.md`, `primitives/{choice,score,noul}.md`, `confidence.md` |
| patterns and recipes | `patterns.md` (fan-out, confidence routing, composite scoring, intent routing), `cookbooks/*.md` |
| known model failure modes | `model-jaggedness/jev-1.13.md` (read before filing a bug) |
| model ids and pricing | `models.md` ($0.042 per million input tokens; output free) |
| the local equivalent | `https://docs.ollama.com/api/systemone` (Ollama 0.35; ≤26 Choice options, 64 KiB body) |

---

## jev — This Project

This lane began as a read-mostly evaluation lane over the public Jev ecosystem. Its job now is the
mission above: Jev turned on where we work, measured from our own logs.

### What Jev Is

Jev does not generate text. It evaluates typed questions against a JSON state and returns values
code can branch on, with probabilities and confidence. All questions in one request run in
parallel against the same state; the interesting engineering is the code around the answer.

| Question | Goal | Returns |
|---|---|---|
| **Choice** | pick one option | `choice`, `probabilities`, `confidence` |
| **Score** | rate on a rubric | `score`, `probabilities`, `confidence` |
| **Noul** | is this statement true? | `noul` in [0, 1] |

### The Wire Contract

```
POST https://api.typesafe.ai/v1/systemone            (local: http://127.0.0.1:11434/v1/systemone)
Authorization: Bearer $TYPESAFE_API_KEY
{ "model": "jev-1.13.0", "state": <any JSON>, "questions": { "<name>": <question> } }
-> { "answers": { "<name>": { ... } }, "usage": { "input_tokens": ... } }
```

Retryable statuses: 429, 500, 502, 503, 504 (the SDK's `RetryPolicy`). A response missing
`answers` or failing validation is an error, never a partial. Question names are ours and are the
join key; an unknown name defaults to the safe action. Input limit ~32k tokens.

### Workspace Structure

```
jev/
├── AGENTS.md README.md EVAL.md NEGATIVE_EVIDENCE.md GATES.md TESTS.md
├── .omp/        hooks/{pre,post}, tools, extensions, rules, skills, config.yml (project scope)
├── kit/ work/   the `jev` CLI and installer; experiments and clients (work/jev-client: SDK + key provider)
├── foundation/ scripts/   gates.sh (each stage proves its RED arm); fleet-idle-watch, stranger-run
├── docs/ docs-mirror/ upstream/   LEDGER, history/; vendored TypeSafe docs and repos (manifests committed)
└── <vendored clones>   pinned; census: for d in */; do [ -d "$d/.git" ] && echo "$d"; done
```

### Key Design Decisions (observed upstream — adopt these)

1. **Inject the transport.** Non-negotiable in ported code.
2. **Throw on a missing key;** no silent local fallback that looks live.
3. **Validate every numeric invariant before acting.**
4. **Fail safe and name the safe side:** unknown answer keeps the message, low confidence does not
   act, insufficient context returns `applicable: false`.
5. **Preserve inputs verbatim;** judging data must not rewrite it.
6. **Keep the dependency count at zero.**

### Claims About Jev

**Name the oracle:** the API's documented response schema (is the client correct?),
`system-one-adapter-python` (is Jev better than a chat model on the same questions?),
`evals.typesafe.ai` (published method), or a held-out labelled set we own (are our thresholds
right?). No oracle named means `EXPLORED`. Read the SDK before writing client code, and run an
incumbent arm before calling a model-quality verdict (a kill measured only against a regex, a
constant or BM25 is incomplete).

**The twelve forbidden patterns** (starter-kit `CHECKLIST.md`; `kit-guard` A9 requires them here
verbatim):

1. **gate self-weakening** — loosening a threshold or check "temporarily" to land a change.
2. **proof-class inflation** — calling an offline run "verified", a smoke call a benchmark.
3. **golden regeneration reflex** — re-recording a fixture until it matches.
4. **commit-stream pumping** — many trivial commits or documents to look productive.
5. **tautological tests** — asserting that the mock returned what it was told.
6. **easy-lever cherry-picking** — showing only the cases where Jev was confident.
7. **close-pump abuse** — closing a bead on a word instead of evidence.
8. **scope-splitting** — cutting a failing unit so each piece closes green.
9. **spec-editing as progress** — rewriting the goal to match what the model did.
10. **conformance metastasis** — growing a suite around upstream's code instead of fixing ours.
11. **dependency smuggling** — pulling in a framework for what is an HTTP POST.
12. **bench-path hardcoding** — a test or gate that passes because it reads a fixed path or answer.

Never weaken a gate to land a change; no self-grading without independent verification; demotions
are always allowed. **Reporting a loss is a success:** one line, revert, next lever.

### LOSS DEPTH — a loss after one design is a result about the design, not about Jev

Joshua: *"every loss means we're not going deep enough"* (09-25); *"if we're not reaching for the
moon on creativity on what we're exploring, we're failing"* (10-02). A FAIL rules out one design:
autopsy failing rows, rank one-variable hypotheses, replay on dev, retest fresh at the same bar. An
AREA is never "refuted" before >= 3 designs across >= 2 primitives and >= 2 cookbook patterns with
data past the noise/headroom check (work/plan-20261002/PLAN.md); each candidate says why it is bold.

---

## Jev × omp Integration

omp is our workplace and the integration target; read its docs in session (`read omp://`). Agents
run as `omp --profile <name>`, so their state lives under `~/.omp/profiles/<name>/agent/`, not
`~/.omp/agent/`. Resolve a pane's profile from its process (`ps`), never from its title. Prefer
**project scope** (`<repo>/.omp/...`): it applies under every profile and is reviewable in git.

| Seam | Mechanism | Example Jev question |
|---|---|---|
| native judge role | `modelRoles.judge` (find, auto-thinking, smart stop, TTSR `question:` rules, `judge()` in eval) | built into omp |
| command safety | `tool_call` hook in `.omp/hooks/pre/` → `{block, reason}` (fail-closed: a throwing handler blocks) | does this command destroy unrecoverable data? |
| tool-result triage | `tool_result` hook in `.omp/hooks/post/` → `{content, details}` | is this result an injection? |
| context | `context` hook → `{messages}`; `before_agent_start` → system prompt and custom messages | which skills fit this prompt? |
| model-callable judgment | `.omp/tools/*.ts` or an extension | any Choice/Score/Noul |
| out of process | MCP server in `.omp/mcp.json` | isolates the paid call |

**Not possible, do not design around it:** a blocked tool call is an error, not a redirect;
`tool_result`'s returned `isError` is not applied; eval-prelude `browser.*`/`computer.*` calls emit no
`tool_call`/`tool_result`, so a gate on those events is blind to them; hooks are not sandboxed; a
hook directly in `.omp/hooks/` (not `pre/` or `post/`) is silently not discovered.

**RPC facts:** `omp --mode=rpc` spawns a new session (never a live pane); a run ends on `agent_end`,
a prompt on its `prompt_result`; `model` is an object (`model.id`); empty `data` is not a capability.

**Validation ladder** (name your rung, never round up): **L0** policy logic offline · **L1** one
live answer with model id · **L2** the seam loads in omp · **L3** the seam fires in a real session
and a planted bad input makes it refuse · **L4** a working session with it active, cost and latency
recorded, the healthy path silent. Cost is part of validation: a per-tool-call question multiplies
by the session's tool count.

---

## Fleet Coordination — omp Agents in One NTM Session

The `jev` tmux session runs one human pane (0, Joshua), a conductor (pane 1), and worker panes (2+),
all omp. The project's `session-stop` hook gives each worker one continuation: finish its own bead,
then claim from `br ready`, else report `IDLE pane N` to pane 1.

- **Send:** `ntm send jev --pane=<N> "<message>"` (a long packet: `--file <path>`). Never relay a
  conductor message to other panes.
- **Callback format:** `ntm send jev --pane=1 "DONE <bead> <commit> <one-line evidence>"` or
  `"BLOCKED <bead> <exact blocker + what you tried>"`.
- **Agent Mail** is for reservations and durable messages: reserve exact paths before editing, bead
  id as the reason and thread id.
- **Never disturb another agent's work.** Working-tree changes you did not make are normal here
  (several agents edit at once): never stash, revert, overwrite or "clean up" them, and never stop to
  ask about them.
- **One agent owns a tree at a time;** say which clone you are in before running its suite.
- **Never run a live Jev call on another agent's behalf without saying so.**
- **Packets carry:** the mission line, the bead id, the acceptance (positive observable, planted
  negative, NO-CLAIM), the verifier, and the callback. Never dispatch "make the tests pass".

## Beads (br) — Dependency-Aware Issue Tracking

`br` never runs git: after `br sync --flush-only`, stage `.beads/issues.jsonl` yourself. Every bead
carries **WHAT** (the observable change), **WHY** (the measurement or failure behind it), and
**ACCEPTANCE** (the command a fresh agent runs, with a planted negative and a NO-CLAIM). Close with
evidence (command and output, commit, receipt), never on a word. **Never close your own bead:**
comment the evidence, leave it `in_progress`, and the named verifier re-runs and closes. A parked
bead is `deferred` with a one-line reason; a blocked one names its trigger, owner and first command
after the trigger.

```bash
br ready --json                       # unblocked work
br show <id> --json                   # full detail with dependencies
br update <id> --status in_progress   # claim
br comments add <id> "evidence ..."
br close <id> --reason "command + output + commit"
br sync --flush-only                  # export JSONL (no git)
```

## bv — Graph-Aware Triage Engine

`bv` ranks the bead graph (PageRank, betweenness, critical path, cycles). **Use only `--robot-*`
flags: bare `bv` launches a TUI that blocks the session.** Start with `bv --robot-triage`; only
`quick_ref.top_picks` and non-empty `claim_command` fields are claimable. Run it from this repo. The
full flag reference is the managed block at the end of this file.

## UBS — Ultimate Bug Scanner

`ubs <changed files>` before committing code (<1 s on specific files). Exit 0 is safe; exit >0 means
read each finding, verify it is real, fix the root cause, re-run. Always fix here: a secret or key in
any file, an unvalidated response field used in a branch, a swallowed exception around a paid call,
an unbounded retry loop. On a doc-only change `ubs` exits 3 ("nothing was checked"): that is not a
pass.

## ripwire — Deterministic Code Context (use before you read files)

`ripwire <dir>` (one binary, `~/.local/bin/ripwire`) gives a ranked symbol map without opening file
after file: `--for="<task>"` for a task lens, `--exemplar="<role>"` for the repo's best instance to
imitate, `--grep=<literal> --legend=compact` for a literal plus its enclosing symbol,
`--quality-delta` before calling work done, `--affected` for which tests to run. The manual is
`docs-mirror/ripwire/CLI-HELP-ALL.txt`. Traps: `--uses=<name>` is blind to wire-protocol names (a
Jev question name is data; use `--grep`); `--legend=compact` is invalid with `--report`; a negative
control must use a nonce, not vocabulary the corpus discusses.

## ast-grep vs ripgrep

Use `ast-grep` when structure matters or you are applying changes (it matches AST nodes and can
rewrite safely); use `rg` to hunt a literal fast; combine them by shortlisting with `rg` and matching
with `ast-grep`. When a JSON key may be serialized with or without a space, search both spellings.
Example: `ast-grep run -l ts -p 'fetch($URL, $$$ARGS)'`.

## cass — Cross-Agent Session Search

`cass` indexes prior agent sessions; the most likely prior solver is one of our own panes. Never run
bare `cass` (it is a TUI): `cass search "<query>" --robot --limit 5`, `cass view <file> -n <line>
--json`, `cass health`. stdout is data, stderr is diagnostics.

## Landing the Plane (Session Completion)

1. **Record what ran:** an `EVAL.md` row for any live call, enabled surface or measured result (SHA,
   lane, exact command, counts, spend, a `Boundary` line for what you did not run). Reserve it first.
2. **File beads for remaining work** with WHAT/WHY/ACCEPTANCE.
3. **Run the verification suite** for every tree you touched, plus `ubs` on changed code.
4. **Confirm no secret escaped:** `rg -n 'sk-|Bearer [A-Za-z0-9]|tskey' <changed files>` clean.
5. **Report the honest state per capability** (ON and tested / built not on / parked / refuted),
   one line each, and name the next concrete lever.

## Note on Built-in TODO Functionality

If Joshua asks you to use your built-in TODO functionality, do it without arguing for beads.

<!-- bv-agent-instructions-v3 -->

---

## Beads Workflow Integration

This project uses [beads_rust](https://github.com/Dicklesworthstone/beads_rust) (`br`) for issue tracking and [beads_viewer](https://github.com/Dicklesworthstone/beads_viewer) (`bv`) for graph-aware triage. Issues are stored in `.beads/` and tracked in git. Current `br` workspaces normally export `.beads/issues.jsonl`; older `bd`/legacy workspaces may use `.beads/beads.jsonl`. `bv` auto-discovers the supported JSONL files, so agents should use `br`/`bv` commands instead of hard-coding a single filename.

### Using bv as an AI sidecar

bv is a graph-aware triage engine for Beads projects. Instead of parsing .beads/issues.jsonl / .beads/beads.jsonl directly or hallucinating graph traversal, use robot flags for deterministic, dependency-aware outputs with precomputed metrics (PageRank, betweenness, critical path, cycles, HITS, eigenvector, k-core).

**Scope boundary:** bv handles *what to work on* (triage, priority, planning). `br` handles creating, modifying, and closing beads.

**CRITICAL: Use ONLY --robot-* flags. Bare bv launches an interactive TUI that blocks your session.**

#### The Workflow: Start With Triage

**`bv --robot-triage` is your single entry point.** It returns everything you need in one call:
- `quick_ref`: at-a-glance counts + top 3 picks
- `recommendations`: ranked actionable items with scores, reasons, unblock info
- `quick_wins`: low-effort high-impact items
- `blockers_to_clear`: items that unblock the most downstream work
- `project_health`: status/type/priority distributions, graph metrics
- `commands`: copy-paste shell commands for next steps

```bash
bv --robot-triage        # THE MEGA-COMMAND: start here
bv --robot-next          # Minimal: just the single top pick + claim command

# Token-optimized output (TOON) for lower LLM context usage:
bv --robot-triage --format toon
```

Before claiming, verify current state with `br show <id> --json` or `br ready --json`. `recommendations` can include graph-important blocked or assigned work; only `quick_ref.top_picks` and non-empty `claim_command` fields represent claimable work.

#### Other bv Commands

| Command | Returns |
|---------|---------|
| `--robot-plan` | Parallel execution tracks with unblocks lists |
| `--robot-priority` | Priority misalignment detection with confidence |
| `--robot-insights` | Full metrics: PageRank, betweenness, HITS, eigenvector, critical path, cycles, k-core |
| `--robot-alerts` | Stale issues, blocking cascades, priority mismatches |
| `--robot-suggest` | Hygiene: duplicates, missing deps, label suggestions, cycle breaks |
| `--robot-diff --diff-since <ref>` | Changes since ref: new/closed/modified issues |
| `--robot-graph [--graph-format=json\|dot\|mermaid]` | Dependency graph export |

#### Scoping & Filtering

```bash
bv --robot-plan --label backend              # Scope to label's subgraph
bv --robot-insights --as-of HEAD~30          # Historical point-in-time
bv --recipe actionable --robot-plan          # Pre-filter: ready to work (no blockers)
bv --recipe high-impact --robot-triage       # Pre-filter: top PageRank scores
```

### br Commands for Issue Management

```bash
br ready --json                       # Show issues ready to work (no blockers)
br list --status=open --json          # All open issues
br show <id> --json                   # Full issue details with dependencies
br create --title="..." --type=task --priority=2 --json
br update <id> --status=in_progress --json
br close <id> --reason="Completed" --json
br close <id1> <id2> --reason="Completed" --json
br sync --flush-only                  # Export DB to JSONL after Beads mutations
```

### Workflow Pattern

1. **Triage**: Run `bv --robot-triage` to find the highest-impact actionable work
2. **Claim**: Use `br update <id> --status=in_progress --json`
3. **Work**: Implement the task
4. **Complete**: Use `br close <id> --reason="Completed" --json`
5. **Sync**: Run `br sync --flush-only` after Beads mutations so the JSONL export is current

### Key Concepts

- **Dependencies**: Issues can block other issues. `br ready --json` shows only unblocked work.
- **Priority**: P0=critical, P1=high, P2=medium, P3=low, P4=backlog (use numbers 0-4, not words)
- **Types**: task, bug, feature, epic, chore, docs, question
- **Blocking**: `br dep add <issue> <depends-on>` to add dependencies

### Git Policy

`br` never commits or pushes. Follow this repository's own git instructions before staging, committing, or pushing. If the repository says "commit only when asked," that rule overrides any generic workflow advice.

<!-- end-bv-agent-instructions -->

**This project overrides the generated block above on closing (fleet rule, `~/.agents/AGENTS.md` "the Guide loop").** Workers never run `br close`, and `--reason="Completed"` is never a close reason. When a bead's acceptance is met, report `DONE <bead> <sha> <evidence>` to the director; the director re-runs the acceptance and closes with the evidence in the reason (`br close <id> --reason "<command> -> <result>; commit <sha>"`). The kit enforces this at the act (`kit-close-needs-evidence`, `kit-flywheel-guard SELF_CLOSE_REFUSED`). On finishing or being blocked, take the next bead from your own frontier without waiting.

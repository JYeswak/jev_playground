# AGENTS.md — jev

> Guidelines for AI coding agents working in this Jev evaluation-and-demo workspace.

This file follows the canonical AGENTS.md shape derived from the Dicklesworthstone mirror
(`fh agents`, skeleton `content_id=095decf2…`, `source_rev=bb59539…`, 64 canonical sections over
117 of 221 mirror repos), with the Rust-specific bands replaced by the ones this lane actually
has: a paid probabilistic API, a growing set of pinned third-party clones, omp itself as the
integration target, and a demand for demos that land where we work.

---

## RULE 0 - THE FUNDAMENTAL OVERRIDE PREROGATIVE

If I tell you to do something, even if it goes against what follows below, YOU MUST LISTEN TO ME. I AM IN CHARGE, NOT YOU.

---

## RULE NUMBER 1: NO FILE DELETION

**YOU ARE NEVER ALLOWED TO DELETE A FILE WITHOUT EXPRESS PERMISSION.** Even a new file that you yourself created, such as a test code file. You have a horrible track record of deleting critically important files or otherwise throwing away tons of expensive work. As a result, you have permanently lost any and all rights to determine that a file or folder should be deleted.

**YOU MUST ALWAYS ASK AND RECEIVE CLEAR, WRITTEN PERMISSION BEFORE EVER DELETING A FILE OR FOLDER OF ANY KIND.**

---

## RULE 1.5: THIS IS A LANE, NOT A LIBRARY

Nothing in this workspace ships by sitting here. `jev/` exists to answer one question repeatedly:

> **Which Jev capability, proven live at a pinned revision, is worth wiring into the omp harness
> or one of our own products — and what is the smallest demo that proves it there, validated?**

Consequences that bind every session:

- **The deliverable is a landed, validated integration** — an omp hook, custom tool, MCP server,
  or product demo that runs where we actually work — or an honest `ZERO` with the reason. A new
  document in this directory is not a deliverable.
- **omp is the first-class integration target, not an afterthought.** As we build testing
  capabilities on Jev, they get wired into omp and *validated there*: see
  [Jev × omp Integration](#jev--omp-integration--seams-and-the-validation-ladder). A capability
  that only runs in a scratch script is `PROBED`, never `PORTED`.
- **Every vendored clone is other people's code.** We read them, run them, and steal their
  design decisions. We do not maintain them.
- **`EVAL.md` is the ledger of record** for what was actually run, at which SHA, with which
  lane (offline / live / omp-wired). Anything you verify goes there, in the same shape as the
  existing entries, including a `Boundary` statement of what you did NOT run.
- A capability is `EXPLORED` → `PROBED` → `WIRED` → `VALIDATED`. Never report a later state than
  the one you produced evidence for. **BUILT ≠ WIRED; WIRED ≠ VALIDATED.**

---

## Irreversible Git & Filesystem Actions — DO NOT EVER BREAK GLASS

1. **Absolutely forbidden commands:** `git reset --hard`, `git clean -fd`, `rm -rf`, or any command that can delete or overwrite code/data must never be run unless the user explicitly provides the exact command and states, in the same message, that they understand and want the irreversible consequences.
2. **No guessing:** If there is any uncertainty about what a command might delete or overwrite, stop immediately and ask the user for specific approval. "I think it's safe" is never acceptable.
3. **Safer alternatives first:** When cleanup or rollbacks are needed, request permission to use non-destructive options (`git status`, `git diff`, `git stash`, copying to backups) before ever considering a destructive command.
4. **Mandatory explicit plan:** Even after explicit user authorization, restate the command verbatim, list exactly what will be affected, and wait for a confirmation that your understanding is correct. Only then may you execute it—if anything remains ambiguous, refuse and escalate.
5. **Document the confirmation:** When running any approved destructive command, record (in the session notes / final response) the exact user text that authorized it, the command actually run, and the execution time. If that record is absent, the operation did not happen.
6. **`.venv/`, `node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `.test-dist/` are still files.** They are cheap to rebuild, which is not the same as being yours to delete. Ask.

---

## Vendored Upstream Clones — Read-Mostly, Pinned, Never Pushed

Each subdirectory is a real clone of somebody else's public repository, checked out at the SHA it
was evaluated at. Treat them as **upstream trees under evaluation**, not as our source.

- **NEVER `git push`, `git push --force`, or `gh pr create` from inside a vendored clone.** There
  is no scenario in this lane where that is the right move without explicit written instruction.
- **NEVER commit into a vendored clone to make something work.** If a demo needs a change to
  upstream behavior, the change belongs in *our* wrapper, in *our* target repo. See
  [Never Patch Upstream To Make A Demo Pass](#never-patch-upstream-to-make-a-demo-pass).
- **Never `git pull` a clone without recording the SHA move.** The pinned SHA in `EVAL.md` is
  what every measurement in that file refers to. Moving the SHA silently invalidates the ledger.
  Record `old → new` and re-run the lane you are about to cite.
- Local experimental edits inside a clone are allowed **only** while diagnosing, must be visible
  in `git -C <clone> diff`, and must be reported. An undisclosed local edit turns every number
  measured against that tree into a fooled certificate.
- Upstream is the authority on upstream. If a repo's README and its code disagree, the code wins
  and the README discrepancy is worth reporting upstream (see `EVAL.md` §1, where
  `fast-jev-compaction`'s question keys are `call_tN`/`result_tN`, not `tool_use_id`).

---

## Git Branch: ONLY Use `main`, NEVER `master`

**In every repo we own, the default branch is `main`. The `master` branch exists only for legacy URL compatibility.**

- **All work happens on `main`** — commits, PRs, feature branches all merge to `main`
- **Never reference `master` in code or docs** — if you see `master` anywhere in our code, it's a bug that needs fixing
- **Never rename or force a branch in a vendored clone** — their branch convention is theirs

**This workspace root is deliberately not a git repository.** `git -C /Users/josh/Developer/jev
rev-parse HEAD` fails, and that is the intended state: the root is a staging area whose
contents either belong to upstream or get promoted into a product repo. Do not `git init` here
without asking — it would swallow every nested clone.

---

## Toolchain: npm and uv

Two toolchains, one each per language. **Never introduce a third.**

- **TypeScript/JavaScript:** `npm` only. NEVER `pnpm`, `yarn`, or `bun` in these trees — each
  clone ships a `package-lock.json` and the lockfile is part of what we are evaluating.
- **Python:** `uv` only. NEVER `pip`, `poetry`, `conda`, or a hand-made `venv`. `jev-ultrafast`
  pins `requires-python >=3.12` and resolves via `uv.lock`.
- **Node:** the system Node at `/opt/homebrew/bin/node` (ES2022+, `node --test`, global `fetch`).
  `jev-review` targets `node20`; `jev-mcp` uses `node --test` with `.mjs` suites.
- Never add a dependency to a vendored clone. Never "upgrade" a clone's lockfile.

### Key Dependencies

| Tree | Runtime deps | Notes |
|------|--------------|-------|
| `fast-jev-compaction` | **zero runtime deps** | `tsc`, `vitest`, `tsx` dev-only; the Jev client is ~40 lines over global `fetch` |
| `jev-review` | `zod` (response schema) | bundled with `esbuild` to a single MCP stdio server |
| `jev-mcp` | MCP SDK | three judgment tools over stdio |
| `jev-ultrafast` | `browser-harness==0.1.13`, `httpx[http2]>=0.28,<1` | `httpx` with HTTP/2, 25 s client timeout |
| `awesome-jev-by-typesafe` | stdlib only for tests; `typesafe-sdk` / `@typesafe-ai/sdk` for the quickstarts | official SDKs, both languages |
| `awesome-jev` | none | markdown only |

The interesting fact in that table: **the good Jev integrations have almost no dependencies.**
A typed-question client is an HTTP POST and a validator. Any demo we write that needs a framework
to talk to Jev is over-built.

---

## Secrets and the Paid Surface (CRITICAL)

Jev is a metered third-party API. Every call spends real money against a key that is not ours to
leak. This section is as load-bearing as the deletion rule.

- **The key lives outside this tree.** `/tmp/.tskey`, mode `600`, loaded into the environment
  only. It is never committed here, never written into a test fixture, never pasted into a demo,
  never echoed into a log, never included in a bug report or an `EVAL.md` entry.
- **Load it, do not print it:**
  ```bash
  export TYPESAFE_API_KEY="$(cat /tmp/.tskey)"     # canonical name
  export JEV_API_KEY="$TYPESAFE_API_KEY"           # jev-review reads this name
  # jev-ultrafast additionally wants TEXT_MODEL_API_KEY for its small text model
  ```
  Never `echo $TYPESAFE_API_KEY`, never `env | grep -i key` into captured output, never
  `set -x` around a curl that carries the header.
- **The env-var name is not uniform across the ecosystem** — `TYPESAFE_API_KEY`
  (`fast-jev-compaction`, official SDKs) vs `JEV_API_KEY` (`jev-review`). Read the client before
  assuming; a missing key surfaces as a *thrown error*, not a silent local fallback, in every
  client in this workspace. That is the correct design; copy it.
- **No unattended live loops.** Never leave a live-calling script running in the background,
  in a watcher, in a cron, or in an `ntm` pane you are not reading. A retry loop against a
  metered endpoint is a billing incident.
- **Never commit a captured response body containing anything derived from a real customer
  state.** The `state` you send is the interesting part of a demo and also the part most likely
  to contain someone's data.
- **Budget discipline:** offline first (see the lane split). If a change can be proven against a
  fake asker, proving it live is waste, not rigor.

---

## Code Editing Discipline

### No Script-Based Changes

**NEVER** run a script that processes/changes code files in this repo. Brittle regex-based transformations create far more problems than they solve.

- **Always make code changes manually**, even when there are many instances
- For many simple changes: use parallel subagents
- For subtle/complex changes: do them methodically yourself

### No File Proliferation

If you want to change something or add a feature, **revise existing code files in place**.

**NEVER** create variations like:

- `demoV2.ts`
- `probe_improved.mts`
- `client_enhanced.py`

New files are reserved for **genuinely new functionality** that makes zero sense to include in any existing file. The bar for creating new files is **incredibly high**. In this lane the bar is higher still: a new markdown file at the root is almost always the wrong artifact — the right one is an `EVAL.md` entry, a probe, or a diff in a product repo.

### Never Patch Upstream To Make A Demo Pass

When an upstream clone does not do what a demo needs, the ONLY acceptable moves are:

1. **Wrap it** — our code in our target repo, calling the clone's public surface.
2. **Fork it deliberately** — a new repo, attributed, with the divergence documented.
3. **Report it upstream** — an issue or PR from a proper fork, never from the vendored clone.
4. **Drop the demo** — and say why in one line.

Editing a clone until green, then citing that tree's test suite as evidence, is the highest-value
lie available in this workspace. Do not produce it.

### Signals Must Name What They Observed

A **signal** is anything a later reader trusts without re-deriving it: a log line, a return value,
a test name, an `EVAL.md` row, a probability we print. **Before asserting an outcome, compute the
observation that would falsify it:**

- **A guard** — a case that FAILS it. A guard you deleted also passes correct data.
- **A "the demo works" claim** — the exit code and the lane. `offline` and `live` are different
  claims about different systems.
- **A latency or accuracy number** — the N it came from, and whether the key was live. One
  1.2 s smoke call is a smoke call, not a latency measurement.
- **A calibration claim** ("Jev is well-calibrated here") — a held-out set with labels, and the
  bucket counts. Without those you observed *plausible numbers*, which is a different sentence.
- **A declared capability** (a question we expose, a config knob) — a consumer. Grep for a writer
  AND a reader.

**If you cannot compute it, do not drop the qualifier.** Name the evidence you actually have —
"scored", not "correct"; "returned 200", not "worked" — and file the gap. An unqualified
past-tense claim is read as observed.

---

## Backwards Compatibility

We do not care about backwards compatibility for our own code here—this lane is days old and has no users. We want to do things the **RIGHT** way with **NO TECH DEBT**.

- Never create "compatibility shims"
- Never create wrapper functions for deprecated APIs
- Just fix the code directly

**The exception is upstream's surface.** `jev-latest` resolves to a *moving* model (`jev-1.13.0`
as of 2026-09-17) and the ecosystem is one week old. Pin the model id in anything we port, and
treat an upstream API shape as a contract we do not own and cannot fix.

---

## Verification Checks (CRITICAL)

**After any substantive change, you MUST run the exact suite for the tree you touched.** These are
the commands that were green at the pinned SHAs; nothing here is invented:

```bash
# fast-jev-compaction @ 6e1da50 — TS, zero runtime deps
cd fast-jev-compaction && npm install
npm run typecheck          # tsc --noEmit  +  tsc -p tsconfig.hooks.json
npm test                   # vitest run          (29 tests green at 6e1da50)
npm run build              # tsc → dist
npm run validate:plugin    # claude plugin validate .claude-plugin/plugin.json

# jev-review @ 57690af — TS, MCP stdio server
cd jev-review && npm install
npm run validate           # tsc --noEmit + node --test (13) + esbuild bundle

# jev-mcp @ 6ec5efc — TS, three MCP judgment tools
cd jev-mcp && npm install
npm run typecheck
npm test                   # node --test test/unit.test.mjs        (9, no key)
npm run test:e2e           # node --test test/e2e.test.mjs         (4, LIVE — spends money)

# jev-ultrafast @ 452c1ad — Python, browser agent
cd jev-ultrafast && uv sync
uv run ruff check .
uv run pytest              # 31 tests, behavior-level, no model calls
uv run python scripts/check_guards.py    # 21 guards vs REAL headless Chrome, no model calls
#   ^ requires Chrome already listening: --remote-debugging-port=9222

# awesome-jev-by-typesafe @ d57f5ce — patterns + runnable examples
cd awesome-jev-by-typesafe && uv run pytest tests/    # 11 tests, stdlib only

# our own probe — fake Jev, no key, no network
npx tsx probes/fast-jev-probe.mts                     # 8 assertions
```

If you see errors, **carefully understand and resolve each issue**. Read sufficient context to fix
them the RIGHT way. A failure inside a vendored clone is a *finding about that clone*, not a task
to fix by editing it.

---

## Testing

### Testing Policy

Every behavior we build on Jev must be provable **without** calling Jev. That is not a
convenience; it is the only way to test a probabilistic dependency at all.

- **Inject the asker.** Every good client in this workspace takes a `fetch`/asker/transport in its
  constructor (`fast-jev-compaction`'s `JevClient({ fetch })`, `jev-review`'s
  `fetchImplementation`, `jev-ultrafast`'s module-level `CLIENT`). Our code does the same or it is
  untestable.
- **Test the policy, not the model.** Jev returns numbers; *we* own the thresholds, the
  confidence gate, the tie-breaks, and the fail-safe direction. Those are deterministic and must
  have tests. `awesome-jev-by-typesafe/tests/test_decision_policies.py` is 11 tests of pure
  policy logic with zero network — that is the model to copy.
- **Test the validator against hostile answers.** A malformed or adversarial response must be
  refused, not coerced. `jev-ultrafast`'s `validate_choice` is the reference: `choice ∈ ids`,
  `set(probabilities) == set(ids)`, every number finite in `[0,1]`, `|Σp − 1| < 0.02`,
  `p[choice] ≥ max(p) − 1e-6`, else `raise ValueError("...; no action executed.")`.
- **Name the fail-safe direction in the test name.** `fast-jev-compaction` defaults an unknown
  answer key to **keep** — the safe side of a compaction decision. Every gate we write must have
  a test that names which way it fails and why that way is safe.
- Happy path, edge cases (empty state, single option, all-equal probabilities, confidence at the
  threshold), and error conditions (HTTP 429/503/529, timeout, malformed JSON, missing `answers`).

### The Offline/Live Lane Split

Two lanes. They are never mixed in one claim.

| Lane | Key | Network | What it proves | Where it may be cited |
|------|-----|---------|----------------|------------------------|
| **offline** | none | none | our policy, our validator, our wiring, fail-safe direction | freely; this is the default lane |
| **live** | yes | `api.typesafe.ai` | that the real model returns usable values on a real state | only with N, date, model id, and latency |

Rules:

- A suite that silently skips when the key is absent is **broken**. Absent key ⇒ the offline lane
  runs fully and the live lane reports `NOT_RUN`. "Never ran" must never read like "passed".
- A live run pins `model` explicitly and records the resolved version (`jev-latest` →
  `jev-1.13.0` on 2026-09-17). A number without a model version is unciteable next week.
- Retry/backoff behavior is offline-testable with an injected transport. Test it there, not by
  hammering a paid endpoint.

### Test Categories

| Tree | Focus areas |
|------|-------------|
| `fast-jev-compaction` | keep/drop policy per tool call+result, verbatim text preservation, message order, truncation-to-head+note on drop, unknown-key fail-safe (keep), Claude Code hook wiring |
| `jev-review` | MCP handshake and `tools/list` schema, question construction, response schema (`zod`) refusal on drift, `applicable: false` for insufficient context, retry/`Retry-After`/timeout |
| `jev-mcp` | the three judgment tools (verify / screen / find), prompt-injection flagging, absence checks, live e2e per tool |
| `jev-ultrafast` | staleness guards, text-reuse rules, action-space construction, trip verification, `validate_choice` invariants, guards vs real headless Chrome |
| `awesome-jev-by-typesafe` | decision policies: routing, confidence gates, composite scoring, filter thresholds |
| `probes/` | our own black-box assertions against a fake Jev — the one suite we own end to end |

### Live Call Budget Gate

Before any live run, state in the session: **which tree, which lane, how many calls, why offline
was insufficient.** Then run it once. A live suite that needs to be run repeatedly to produce a
stable claim is evidence about variance — record that, don't average it away silently.

---

## The Jev Oracle

Jev is probabilistic; our correctness claims must still be falsifiable. **Name which oracle
produced any claim you make.** There are exactly four, in descending authority:

| Oracle | What it decides | How to invoke |
|--------|-----------------|---------------|
| **The API's documented response schema** | whether a client is correct | validate every field; refuse on drift (`jev-review`'s `jevResponseSchema.safeParse`) |
| **`system-one-adapter-python`** (official, `pip install system-one-adapter`) | whether Jev is *better than a chat model at the same questions* | drop-in `TypeSafeClient` replacement backed by LLM APIs — same state, same questions, differential comparison |
| **`evals.typesafe.ai`** | the published methodology and per-model results | read before designing an eval; do not invent a rival metric silently |
| **A held-out labelled set we own** | whether a *specific* workflow's thresholds are right | N, labels, bucket counts, date, model version |

Additional hard rules:

- **`docs.typesafe.ai/model-jaggedness/jev-1.13` is the known-bad catalogue.** Before reporting a
  surprising failure as a bug in our code or in an upstream clone, check whether it is a
  documented jaggedness of the current public model.
- **The playground is not an oracle.** A screenshot of a good answer is not evidence.
- **Our own prior run is not an oracle.** "Same as last time" against a moving `jev-latest` is a
  coincidence until the model version matches.
- **No oracle named ⇒ the claim is `EXPLORED`, not `PROBED`.** That is an acceptable, honest
  outcome; an unfalsifiable "it works" is not.

---

## Named Reward-Hacking Patterns (ALL FORBIDDEN)

Adapted from the suite-wide list the mirror repos bind themselves to
(`frankensearch/AGENTS.md` RULE 0.5). These are the ones this lane invites:

1. **Gate self-weakening** — lowering a confidence threshold until the demo passes. If a gate is
   genuinely wrong, fix it on the evidence and publish what the fix now admits *and* rejects.
2. **Proof-class inflation** — calling an offline run "verified", a smoke call a "benchmark", a
   plausible number a "calibration", or an upstream suite "our tests".
3. **Golden regeneration reflex** — re-recording a fixture because it stopped matching. A moving
   `jev-latest` is exactly when a stale golden is *telling you something*.
4. **Tautological tests** — asserting that the mock returned what the mock was told to return.
5. **Easy-lever cherry-picking** — demoing the state where Jev happens to be confident and not
   mentioning the ten where it was not.
6. **Cherry-picked N** — one live call presented as a result.
7. **Spec-editing as progress** — rewriting the demo's goal to match what the model did.
8. **Conformance metastasis** — growing a test suite around upstream's code instead of ours.
9. **Dependency smuggling** — pulling a framework in to "enable" a demo that is an HTTP POST.
10. **Commit-stream pumping / document pumping** — activity in this directory is not output.
    The output is a landed diff in a product repo.

Two corollaries worth stating flat:

- **Reporting a loss is a success.** "Jev is the wrong tool for X, here is the measurement" is a
  first-class result. One line, move to the next lever, no retraction narrative.
- **A self-comparison is maintenance, not a win.** "Faster than our previous prompt" needs the
  incumbent live in the same invocation to be a win at all.

---

## Claim Discipline

- Do not describe a proposal as implemented.
- Do not describe an offline run as a live one, a smoke call as a benchmark, a single state as a
  distribution, or an upstream suite as our verification.
- Every number carries: lane, N, date, model version, and the tree+SHA it ran against.
- Include explicit non-claims. `EVAL.md`'s `Boundary` section is mandatory, not decorative: it is
  the only reason the rest of that file is trustworthy.
- Never write "verified" without the level: `offline-verified`, `live-verified (N=4)`,
  `schema-verified`, `differential-verified`, or `NOT_RUN`. A bare "verified" is overclaim.
- Attribute upstream work by owner and SHA — take the census, never a remembered list. The
  licenses are permissive (MIT and CC0); the attribution is not optional.

---

## Third-Party Library Usage

**The primary sources are vendored locally. Read them from disk, not from memory, and not from a
web search.** Jev entered early access on **15 September 2026**; every SDK in the ecosystem is
days old. Your training data does not contain this API, and a plausible-sounding recollection of
it is a fabrication.

Order of authority: `docs-mirror/typesafe/**` (TypeSafe's own documentation) → `upstream/typesafe-ai/**`
(their first-party SDK source) → `awesome-jev/README.md` (the ecosystem index, in-tree) →
community clients. Refresh with `scripts/sync-docs.sh`; verify with `scripts/sync-docs.sh --check`.

If a claim about Jev cannot be traced to a file under `docs-mirror/` or `upstream/`, it is not a
claim about Jev — it is a guess, and it must be labelled one.

---

## Primary Sources — Vendored Locally (READ THESE FIRST)

`scripts/sync-docs.sh` mirrors every primary source this lane depends on into the workspace, with
a sha256 manifest, so that every statement in a demo or an `EVAL.md` row is traceable to bytes on
disk at a known revision.

```bash
./scripts/sync-docs.sh              # full sync: docs + first-party repos + ripwire
./scripts/sync-docs.sh --check      # verify the mirror against MANIFEST.tsv (fail-closed)
./scripts/sync-docs.sh --docs-only  # just docs.typesafe.ai
./scripts/sync-docs.sh --repos-only # just the git surfaces
```

What it produced (measured 2026-09-17, `--check` → `CHECK PASS 114 mirrored files`):

| Local path | What it is |
|------------|-----------|
| `docs-mirror/typesafe/llms.txt` | the doc site's **own** machine-readable index — 111 pages, one line each with a summary. **Start here**, not with a crawl |
| `docs-mirror/typesafe/llms-full.txt` | the entire documentation corpus as one 835 KB text file — grep this when you don't know which page |
| `docs-mirror/typesafe/**.md` | all 111 pages, at their real URL paths (see the reading map below) |
| `docs-mirror/typesafe/sitemap.xml` | 111 `<loc>` entries; the denominator for "did we mirror everything" |
| `docs-mirror/MANIFEST.tsv` | kind, source URL, local path, bytes, sha256, fetched_at — 114 rows |
| `upstream/typesafe-ai/typesafe-sdk-python` | official Python SDK `@420ef4f` |
| `upstream/typesafe-ai/typesafe-sdk-js` | official TS/JS SDK `@66880cc` |
| `upstream/typesafe-ai/system-one-adapter-python` | **the differential oracle** — drop-in `TypeSafeClient` backed by LLM APIs `@0bb819b` |
| `upstream/typesafe-ai/skills` | TypeSafe's own agent skills for building on System One `@65a39f3` |
| `upstream/MANIFEST.tsv` | repo, path, pinned_sha, upstream_sha, **behind**, fetched_at |
| `upstream/ORG-INVENTORY.tsv` | all 10 repos in the `typesafe-ai` org, fork flag, and whether we mirror it — so nothing is silently outside the allow-list |
| `docs-mirror/ripwire/CLI-HELP.txt` | the installed binary's summary help (200 lines) |
| `docs-mirror/ripwire/CLI-HELP-ALL.txt` | `--help=all` — every flag in full (1826 lines); **this is the ripwire manual** |
| `docs-mirror/ripwire/VERSION.txt` | `ripwire 0.6.1 (Release, AppleClang 21.0.0.21000101, emit=std::print, built_from=f45087a77)` |
| `docs-mirror/ripwire/docs/*.md` | 15 design docs (ARCHITECTURE, COMMANDS, METHODOLOGY, EVALS, …) |

**The manifest reports drift; it never repairs it.** A clone that is behind upstream is printed
as `** N commit(s) behind <sha> **` and left exactly where it is — moving a pinned SHA
invalidates every measurement taken against it, and is a human decision.

That mechanism paid for itself on its first run and the finding is now **closed**: it reported
the `~/Developer/ripwire` checkout at `6488f6f4`, **1502 commits behind** upstream, while the
installed binary was a *third* revision (`0.4.0 built_from=e663ca8f8`). Resolved 2026-09-17 —
fast-forwarded to `f45087a7` (tag `v0.6.1-427-gf45087a7`), rebuilt, and reinstalled, so all
three now agree at `f45087a7` / `0.6.1 built_from=f45087a77`. **Do not cite "ripwire says"
without saying which revision**, and re-run `scripts/sync-docs.sh --repos-only` after any
upgrade — the vendored help is a snapshot, and 0.6.1 moved the manual from `--help` (1546 lines
then) to `--help=all` (1826 lines now).

**One binary, one prefix.** `install.sh` detects its prefix and prefers `brew --prefix`, which
on this machine would install a *second* copy at `/opt/homebrew/bin/ripwire`. Always pin it:

```bash
cd ~/Developer/ripwire && git pull --ff-only origin main
RIPWIRE_INSTALL_PREFIX="$HOME/.local" ./install.sh     # ~107 s: Release + LTO + native
which -a ripwire        # MUST print exactly one line
```

### The reading map — question → file

| When you need | Read |
|---------------|------|
| what System One even is | `concepts/system-one.md`, `introduction.md` |
| the 60-second working call | `introduction/quickstart.md` |
| how to shape the `state` | `concepts/state.md` |
| which primitive to use | `primitives.md`, then `primitives/{choice,score,noul}.md` |
| JSON structure inside instructions/options/levels/criteria | `primitives/advanced.md` |
| whether to ACT on an answer | `confidence.md` ← the difference between probability and confidence is the whole engineering discipline |
| how to architect around it | `concepts/how-to-build-with-system-one.md` |
| the four architectural patterns | `patterns.md`, `patterns/{fan-out,confidence-routing,composite-scoring,intent-routing}.md` |
| **18 runnable recipes** | `cookbooks/` — `llm_guardrails.md`, `classifying_rag_passages.md`, `rerank_typesafe.md`, `function_calling.md`, `hierarchical_classification.md`, `citation_check.md`, `skill_suggestion.md`, `sde_cascade.md`, `parallel_questions.md`, `consistency_{choice,noul}_cookbook.md`, `classification_using_confidence.md`, `semantic_find.md`, `entity_alignment.md`, `autoformat.md`, `autoresearch_feature_discovery.md`, `date_extraction_cookbook.md`, `pre_parsed_value_extraction_cookbook.md` |
| the exact HTTP contract | `api.md` |
| SDK usage and types | `sdk.md`, `sdk/python.md`, `sdk/python/usage.md`, `sdk/javascript.md`, plus generated `sdk/*/api/**` |
| **known failure modes of the model we are calling** | `model-jaggedness/jev-1.13.md` — read before filing any bug |
| what a demo can look like | `demos.md`, `demos/smart-home.md` |
| dropping Jev into a coding agent | `agent-skill.md`, and `upstream/typesafe-ai/skills/` |
| which model ids exist | `models.md` |
| terms of the paid surface | `legal.md` |
| why any of this | `introduction/machine-learning-primer.md` |

**A demo's README must cite the doc page it implements**, by local path. "Based on the docs" is
not a citation; `docs-mirror/typesafe/patterns/fan-out.md` is.

Search the corpus before opening pages one by one:

```bash
rg -n "confidence" docs-mirror/typesafe/llms-full.txt | head -40   # whole corpus, one file
rg -l "retry|429|rate limit" docs-mirror/typesafe/**/*.md          # which pages cover it
rg -n "class .*Client|def ask|async def" upstream/typesafe-ai/typesafe-sdk-python/src
```

---

## jev — This Project

**This is the workspace you're working in.** It is a read-mostly evaluation lane over the public
Jev ecosystem, plus our own probes, whose purpose is to produce demos that land in our products.

### What Jev Is

Large language models generate text. **Jev does not.** It evaluates typed *questions* against a
*state* and returns values code can branch on, sort by, and route with — plus calibrated
probabilities and confidence.

| Question | Goal | Returns |
|----------|------|---------|
| **Choice** | pick one option from a list | `choice`, `probabilities`, `confidence` |
| **Score** | rate the state on a rubric | `score`, `probabilities`, `confidence` |
| **Noul** | is this statement true? | `noul` (0–1) |

All questions in one request run **in parallel against the same state**. Atomic questions,
composed in code. The corollary that governs every demo: **the interesting engineering is the
code around the answer, not the prompt.** Thresholds, fail-safe direction, fan-out, and
composition are ours.

### The Wire Contract

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json

{ "model": "jev-latest", "state": <any JSON>, "questions": { "<name>": <question> } }
→ { "answers": { "<name>": { ... } } }
```

- Model `jev-latest` resolved to **`jev-1.13.0`** on 2026-09-17. Pin it in ported code.
- Retryable statuses observed in the wild: **429, 503, 529** (`jev-ultrafast`: 3 attempts,
  `0.5 · 2^n` backoff; `jev-review`: 2 retries honoring `Retry-After`, 30 s timeout).
- A response missing `answers`, or failing schema validation, is an **error** — never a
  best-effort partial. Every client here throws. Copy that.
- Question names are ours to choose and are the join key for the answers. `fast-jev-compaction`
  uses `call_tN` / `result_tN`; unknown names in the response default to the **safe** action.

### Workspace Structure

```
jev/
├── AGENTS.md                    ← this file
├── EVAL.md                      ← the ledger: what ran, at which SHA, in which lane
├── scripts/
│   └── sync-docs.sh             ← vendors every primary source + sha256 manifest (--check verifies)
├── docs-mirror/                 ← PRIMARY SOURCES, local. Read these first.
│   ├── MANIFEST.tsv             ← 114 rows: source URL, local path, bytes, sha256, fetched_at
│   ├── typesafe/                ← 111 md pages + llms.txt + llms-full.txt + sitemap.xml
│   └── ripwire/                 ← CLI-HELP.txt, VERSION.txt, docs/*.md
├── upstream/
│   ├── MANIFEST.tsv             ← pinned_sha, upstream_sha, behind
│   ├── ORG-INVENTORY.tsv        ← all 10 typesafe-ai repos, fork flag, mirrored y/n
│   └── typesafe-ai/            {typesafe-sdk-python@420ef4f, typesafe-sdk-js@66880cc,
│                                system-one-adapter-python@0bb819b, skills@65a39f3}
├── probes/
│   └── fast-jev-probe.mts       ← OUR black-box probe (fake Jev, no key, 8 assertions)
├── foundation/                  ← OURS: the local calibration + gate harness
│   ├── schemas/{fixture-v1,report-v1}.json   ← errors-as-data contracts
│   ├── fixtures/calibration-v1.jsonl         ← the labelled held-out set
│   ├── run_calibration.py · CALIBRATION.md   ← stdlib runner + the metric definitions
│   ├── runs/<ISO8601>.json                   ← receipts (ECE, Brier, coverage) per audit
│   └── gates.sh + gates.d/{10-fixture-integrity,20-receipt-freshness,30-no-secrets}.sh
├── notes/                       ← scratch; never the deliverable
└── <19 vendored clones>         ← other people's repos, each pinned. NEVER hardcode this list:
                                   it grows every session. Take the census (below).
```

### The census — never hardcode the tree

The clone set grows whenever a sibling pane finds new prior art. Any count in prose is stale by
construction; derive it:

```bash
for d in */; do n=${d%/}; case "$n" in docs-mirror|upstream|scripts|probes|notes|foundation) continue;; esac
  printf '%-30s @%-9s %s\n' "$n" "$(git -C "$n" rev-parse --short HEAD 2>/dev/null)" \
    "$(git -C "$n" remote get-url origin 2>/dev/null | sed 's|https://github.com/||')"; done
```

The four trees with a full recorded evaluation are `fast-jev-compaction @6e1da50`,
`jev-ultrafast @452c1ad`, `jev-review @57690af`, `jev-mcp @6ec5efc`, plus the two catalogues
`awesome-jev-by-typesafe @d57f5ce` and `awesome-jev @ef19300` — see `EVAL.md` §1–6 for the
commands and counts. Everything else in the census is `EXPLORED` until `EVAL.md` says otherwise.

**`system-one-adapter-python` exists twice on purpose-adjacent paths:** a sibling's root clone
and `upstream/typesafe-ai/system-one-adapter-python`, both at `0bb819b`. The one under
`upstream/` is the one `upstream/MANIFEST.tsv` pins and `--check` verifies; cite that path when
you cite the differential oracle.

### foundation/ — the local oracle harness (ours, not vendored)

This is where a calibration claim becomes citable. It is the **fourth oracle** from
[The Jev Oracle](#the-jev-oracle) made executable: a labelled held-out set, a stdlib runner, and
receipts.

```bash
cd foundation && python3 run_calibration.py        # emits runs/<ISO8601>.json
./gates.sh                                         # aggregate; each stage proves its RED arm
```

Rules, because this harness is the thing every later number leans on:

- **A metric without a receipt is not a result.** Cite `foundation/runs/<ISO8601>.json`, never a
  remembered ECE. First audit on record: ECE 0.061, Brier 0.020, Noul 58/60, Choice 19/20,
  threshold ≥0.75 → accuracy 1.0 at ≥90% coverage (`EVAL.md`, receipt `20260917T224444Z.json`).
- **Every gate stage must prove its RED arm on demand** — truncated fixture, empty `runs/`,
  planted key. A stage that has only ever gone green is unproven.
- **A gate that trips on its own source literal is a broken gate, not a catch.** That fired once
  here during the build: `30-no-secrets` matched the key pattern written in its own script. The
  fix is to assemble the plant at runtime and assert the RED output *names the plant file*.
- Schemas are `errors-as-data` and the metrics are pure functions on purpose: this harness is
  meant to port to Rust without a redesign. Keep it that way — no I/O in a metric.

### Key Files by Tree

| Tree | Read these first |
|------|------------------|
| `fast-jev-compaction` | `src/request.ts` (the whole wire contract in 60 lines), `src/compact.ts` (the policy), `hooks/fast-jev.ts` (Claude Code PreToolUse wiring), `.claude-plugin/plugin.json` |
| `jev-review` | `src/jev/client.ts` (retry/timeout/schema), `src/jev/schema.ts`, `src/evaluation/questions.ts` (how to build a dimension set), `src/server.ts` (MCP stdio) |
| `jev-mcp` | `src/index.ts` (three tools: verify / screen / find), `test/e2e.test.mjs` |
| `jev-ultrafast` | `jev_ultrafast/model.py` (`validate_choice` — the reference validator), `jev_ultrafast/questions.py` (`NEXT_ACTION`, `TARGET`, `TEXT_VALUE`), `scripts/check_guards.py` |
| `awesome-jev-by-typesafe` | `docs/jev-use-case-playbook.md` (12 patterns), `docs/coding-agent-use-cases.md` (6 agent-harness patterns), `tests/test_decision_policies.py` |
| `awesome-jev` | `README.md` — the ecosystem index; the fastest way to find prior art before building |

### The Pattern Catalogue

Every demo must name the pattern it instantiates. The catalogue is already in this tree — do not
invent a thirteenth pattern before checking:

- `awesome-jev-by-typesafe/docs/jev-use-case-playbook.md` — support triage with speculative
  fan-out; intent routing and model cascades; confidence-gated actions; LLM input/output/tool-call
  guardrails; RAG passage filtering; semantic search and re-ranking; citation and claim
  verification; typed function/tool dispatch; composite scoring; structured extraction with a
  verification pass; hierarchical classification; real-time commands and agent harnesses.
- `awesome-jev-by-typesafe/docs/coding-agent-use-cases.md` — skill/tool selection; command and
  tool-call safety; repository retrieval and context selection; diff verification and semantic
  CI; model cascade for coding work; agent output and citation checks.
- The four architectural recipes from the docs: **speculative fan-out**, **confidence-gated
  routing**, **composite scoring**, **intent routing**.

### Key Design Decisions (observed upstream — adopt these)

1. **Inject the transport.** Every testable client here does. Non-negotiable in ported code.
2. **Throw on a missing key.** No silent local fallback, no degraded mode that looks live.
3. **Validate every numeric invariant before acting.** `jev-ultrafast` refuses and executes
   nothing rather than clicking on a malformed distribution.
4. **Fail safe, and name the safe side.** Unknown answer ⇒ keep the message; low confidence ⇒
   don't act; insufficient context ⇒ `applicable: false` rather than a fabricated score.
5. **Preserve inputs verbatim.** `fast-jev-compaction` drops messages and truncates, but never
   summarizes — the surviving text is byte-identical. A Jev workflow should not rewrite the user's
   data as a side effect of judging it.
6. **Keep the dependency count at zero.** The wire contract is small enough that a framework is
   a liability.

### Jev 1.13 Jaggedness — Known Failure Modes

`jev-latest` is a specific public model with documented failure modes at
`docs.typesafe.ai/model-jaggedness/jev-1.13`. **Read it before filing a bug.** A surprising
answer is, in order of likelihood: (1) a state we constructed badly, (2) a documented jaggedness,
(3) our validator being too loose, (4) an actual model defect. Rank them in that order.

---

## The Demo Process — Research → Pin → Probe → Port

This is the mechanism this workspace exists to run. Five stages, in order. **A stage may not be
skipped, and each stage's exit is an artifact, not an opinion.**

### Stage 0 — Research before code

Cheapest stage; most often skipped; most expensive to skip.

```bash
./scripts/sync-docs.sh --check                     # is the local primary-source mirror intact?
rg -n "<concept>" docs-mirror/typesafe/llms-full.txt | head -40   # the WHOLE doc corpus, one grep
rg -n "<concept>" docs-mirror/typesafe/llms.txt                   # which page owns it
ls docs-mirror/typesafe/cookbooks/                 # 18 official recipes — check before inventing
ripwire <dir> --exemplar=<role>                    # does our target repo already have this shape?
fh search "<the mechanism you think you need>"     # measured doctrine + prior art, with provenance
fh suggest "<the task in one line>"                # same ranking, top 5
cass search "jev" --robot --limit 10               # did another agent already solve this?
rg -n "<pattern>" awesome-jev/README.md            # is it already in the ecosystem index?
```

Then read, in this order: the local doc page for the primitive → the matching
`docs-mirror/typesafe/cookbooks/*.md` → `docs-mirror/typesafe/patterns/*.md` → the closest
existing repo in this tree. **Exit artifact:** one sentence naming the pattern, the doc page
(local path), the prior art, and the gap.

### Stage 1 — Pin the repo

If prior art exists as a public repo, clone it **at a SHA** and record owner + license.

```bash
git clone --depth 50 <url> <name> && git -C <name> rev-parse --short HEAD
```

**Exit artifact:** a row in `EVAL.md` with `@sha`, owner, language, license, and one line on what
it does. Never evaluate an unpinned tree.

### Stage 2 — Offline probe (no key, no network)

Run the tree's own offline suite, then write **our** black-box probe against a fake Jev —
`probes/fast-jev-probe.mts` is the reference (8 assertions: verbatim preservation, ordering,
truncation behavior, unknown-key fail-safe). A probe we own is the only test whose green we may
cite as ours.

**Exit artifact:** `offline-verified` with the exact commands and counts, in `EVAL.md`.

### Stage 3 — Live probe (budgeted, once)

State the budget, load the key, run the tree's own live mode. Record model version, call count,
wall time, and the actual values returned.

**Exit artifact:** `live-verified (N=…)` with model version and latency, plus a `Boundary`
sentence naming what was NOT exercised.

### Stage 4 — Wire it into omp (or the owning product) and validate it there

The integration lands **where it runs**, never here. For a testing/judgment capability that means
one of the omp seams below; for a product feature it means the product repo.

- omp seam: `.omp/hooks/pre/<name>.ts`, `.omp/tools/<name>.ts`, `.omp/extensions/<name>.ts`, or
  `.omp/mcp.json` — in the repo where it should apply (see the seam table).
- Product demo: `demos/<pattern>-<capability>/` in the target repo, or a spike branch on `main`.
- **Runs on one command.** `npm run demo` / `uv run python demo.py`, nothing else.
- **Degrades honestly without a key:** offline lane runs, live lane prints `NOT_RUN`. Never a
  fake answer, never a cached response presented as live.
- **Owns its thresholds in our code**, with tests for the policy and the fail-safe direction.
- **Names the pattern and cites the doc page and prior art** (`docs-mirror/...`, repo@sha,
  owner, license) in its README.
- Tracked as a bead in **the target repo's** `.beads/` with label `jev` — not here; this root has
  no git and therefore nowhere to sync a work graph.

**Exit artifact:** an `EVAL.md` row naming the seam, the validation rung reached (L0–L4 below),
and the command that proves it.

### Demo Acceptance Bar

A demo or integration is done when all of these hold. Anything less is `PROBED`, not `VALIDATED`:

- [ ] one command runs it, from a clean clone of the target repo
- [ ] offline lane green with no key present; live lane explicitly `NOT_RUN` rather than skipped
- [ ] the policy (threshold, gate, tie-break, fail-safe side) is our code and has tests
- [ ] the validator refuses a malformed/hostile answer and executes nothing
- [ ] it names its pattern, its doc page, its prior art (repo@sha + license), and its oracle
- [ ] every number in its README carries lane, N, date, and model version
- [ ] no secret anywhere in the tree, including fixtures and recorded responses
- [ ] `ubs <changed-files>` exit 0
- [ ] **if it is an omp seam: the seam fires in a real omp session, and a known-bad input makes it
      refuse** — reached rung ≥ L3, with the transcript or frame pasted
- [ ] an `EVAL.md` row here pointing at where it landed and which rung it reached

---

## Research Surfaces

| Surface | Use it for | Command |
|---------|-----------|---------|
| **`docs-mirror/typesafe/`** | **TypeSafe's own docs, vendored** — the authority on Jev | `rg -n "…" docs-mirror/typesafe/llms-full.txt` |
| **`upstream/typesafe-ai/`** | first-party SDK source at pinned SHAs; the differential oracle | `rg -n "…" upstream/typesafe-ai/*/src` |
| `ripwire` | understand a repo cold, callers/callees, reuse-first, blast radius | `ripwire <dir>`, `ripwire <dir> --for=<sym>` |
| `fh` | measured doctrine, prior art, provenance, the canonical AGENTS.md shape | `fh search "…"`, `fh suggest "…"`, `fh why <row>`, `fh agents --repo .` |
| `cass` | has another agent already solved this? | `cass search "…" --robot --limit 5` |
| `awesome-jev` | the community ecosystem index, in-tree | `rg -n "…" awesome-jev/README.md` |
| web | only for what the mirror does not carry (blog posts, `evals.typesafe.ai`, Discord) | re-run `scripts/sync-docs.sh` first — the answer is usually already on disk |

**Web search is the last resort, not the first.** 111 doc pages and four first-party repos are
already local. `fh doctor` before citing `fh` output — a grade from a degraded corpus is a fooled
certificate. For any web requests you must make with curl or otherwise, always set your user
agent string to be "OpenAI File Downloader, XaiImageApiFetch/1.0".

---

## Fleet Coordination — Three omp Agents in One NTM Session

This lane runs as a single NTM/tmux session named `jev`, with **three coding agents in the omp
harness** and one human pane. Measured:

```
jev:0.0  zsh      jev__user_0        ← Joshua
jev:0.1  omp      jev__omp-claude_2
jev:0.2  omp      jev__omp-claude_1
jev:0.3  omp      jev__omp-muse_1
```

**Every agent here is omp.** There is no Codex pane, no legacy-harness pane, and nothing in this
file should be written for one. Coordination is the harness's own `hub`, not an MCP mail server:

- `hub list` — who is actually live right now. Never guess at peers, never invent a name.
- `hub send --to <peer>` — fire-and-forget; wakes an idle peer. Lead with the answer.
- `hub inbox` — drain without blocking. `hub wait` — only when genuinely blocked.
- `hub jobs` — status of background work. A settled snapshot **is** the delivery.

Rules that matter with three agents in one tree:

- **`EVAL.md` is the highest-contention file in this workspace.** Announce on `hub` before
  appending, then append — never rewrite another agent's row, never reorder the file.
- **Never disturb another agent's work.** Working-tree changes you did not make are normal and
  expected here; see the note near the end of this file.
- **One agent owns a tree at a time.** Say which clone you are in before you run its
  suite; two agents running `npm install` in the same clone is a self-inflicted flake.
- **Never run a live Jev call on another agent's behalf without saying so** — the budget is
  shared, and two agents each "just smoke-testing" is double spend on one key.
- Big payloads go by path (`local://`, a file in `notes/`), never pasted into a message.

---

## The omp Harness — Native Surfaces (measured, not remembered)

Every agent in this lane runs inside omp, so omp is both our workplace and our integration
target. **Its own documentation is readable in-session: `read omp://` lists 131 docs, `read
omp://rpc.md` reads one.** That is the authority; this section is the index plus what was
measured here on 2026-09-17.

```bash
omp --version            # omp/18.2.4 at time of writing — DERIVE IT, never cite this number
omp --help               # 40 subcommands
omp config list --json   # every setting with its current value
omp config get <key>     # one value ; omp config set <key> <value> writes the global YAML
omp ps                   # daemon/background processes
```

### The surfaces that matter here

| Surface | What it gives this lane | Entry point |
|---|---|---|
| **RPC mode** | drive a *headless* omp session over newline-delimited JSON on stdio | `omp --mode=rpc` (`omp://rpc.md`) |
| **Host tools** | the RPC *host* hands the agent extra tools over the same stdio pipe | `set_host_tools` (`omp://rpc.md#host-tool-sub-protocol`) |
| **Host URI schemes** | the host owns a URL scheme; every `read`/`write` of `scheme://…` bounces to the host | `set_host_uri_schemes` (`omp://rpc.md#host-uri-sub-protocol`) |
| **Hooks** | intercept a tool call **before** it runs and block or rewrite it | `.omp/hooks/pre/*.ts` (`omp://hooks.md`) |
| **Extensions** | tools + commands + events + providers in one module | `.omp/extensions/` (`omp://extensions.md`) |
| **Custom tools** | a model-callable function with a Zod/omptype schema | `.omp/tools/*.ts` (`omp://custom-tools.md`) |
| **MCP** | Jev-as-a-server, out of process, rate-limitable | `.omp/mcp.json` (`omp://mcp-config.md`) |
| **Skills** | passive guidance the model always sees | `.omp/skills/<name>/SKILL.md` (`omp://skills.md`) |
| **Compaction** | where a keep/drop judgment could actually live | `session_before_compact`, `session.compacting` (`omp://compaction.md`) |
| **hub processes** | supervise a long-running server/watcher instead of `&` | `hub op:start` (`omp://tools/hub.md`) |
| **eval kernel** | a persistent Python/Bun kernel for probes and fan-out | `eval` (`omp://tools/eval.md`) |
| **task subagents** | parallel read-only research and bounded edits | `task` (`omp://tools/task.md`) |
| **natives** | the bash tool is an **embedded Rust brush shell** with in-process `rg`/`jq`(jaq)/`sed`/`fd` | `omp://native-crates.md`, `omp://bash-tool-runtime.md` |

### RPC — the exact opening handshake, measured here

```bash
printf '%s\n' \
  '{"id":"p1","type":"negotiate_protocol","protocolVersion":2}' \
  '{"id":"s1","type":"get_state"}' | omp --mode=rpc --max-time=20
```

Measured response, 2026-09-17: `ready` (`protocolVersion:1`,
`supportedProtocolVersions:[1,2]`, `maxFrameBytes:1048576`,
`maxReassembledFrameBytes:67108864`) → `available_commands_update` → `negotiate_protocol
success` → `get_state success` with `model.id=claude-opus-5`, `contextWindow=1000000`.

Hard-won rules, every one of them a defect we would otherwise re-discover:

- **`negotiate_protocol` FIRST, in the same stdin stream.** Without it, v2 framing and paged
  message reads are unavailable.
- **`--max-time=<n>` is mandatory.** A bare pipe closes stdin and the process can exit before an
  async frame lands; three separate probes once reported "no frame" and it was the *reader*.
  An empty read is `TIMEOUT_UNMEASURED`, **never** `ABSENT`.
- **`--mode=rpc` SPAWNS A NEW SESSION.** It never attaches to a live pane. Two invocations = two
  session ids. There is **no typed live-pane state** in omp today (`terminal-sessions` gives the
  *last session opened*, not the live one). A pane oracle must **fail closed**, never guess.
- **`model` is an object.** Read `model.id`; `model.name` is a display label.
- **`get_state` has `contextUsage`, not `context`.** An absent key and a null value read alike.
- **An unknown command draws an explicit refusal** — `error: "Unknown command: <name>"` echoing
  the name you sent. That refusal *content* is the discriminator, not frame presence.
- **A `success: true` with empty or null `data` is `NO_PAYLOAD`, not a working capability.**
  Measured: `get_last_assistant_text` returns `data={}`; `abort_bash` acknowledges a running
  `sleep` and the command still completes `cancelled=false`. **An ack is not an effect.**
- **`prompt` is acknowledged, not completed.** A turn is done on `agent_end` with
  `isTerminal !== false`. Local-only prompts complete via `data.agentInvoked:false` or a later
  `prompt_result` frame.
- **`bash` is dispatched concurrently and response order is not guaranteed** — correlate on `id`.
- Big histories: `get_messages_page` with `limit`/`cursor` (≤256 messages/page); the error
  carries `code: session_busy | stale_cursor`. The full four-method sequence **times out** on a
  real resumed session at `get_messages` — request only what you report.

### Profiles — the trap that fires in THIS session

An omp agent launched by the harness runs `omp --profile <name>`, so its state is **not** under
`~/.omp/agent/` but `~/.omp/profiles/<name>/agent/` — sessions, skills, hooks, tools,
extensions, MCP config, `RULES.md`, `AGENTS.md`, all of it.

Measured in this very session:

```
%71  pane title jev__omp-claude_1  ->  omp --profile=codex  --config=~/.omp/profiles/codex/agent/config.yml
%73  pane title jev__omp-muse_1    ->  omp --profile=muse   --config=~/.omp/profiles/muse/agent/config.yml
```

**A pane's title lags its profile and its model.** `jev__omp-claude_1` is on the `codex` profile.
So: resolve the profile from the process, never from the title, and never from `~/.omp/` alone.

```bash
pid=$(tmux list-panes -t jev -F '#{pane_id} #{pane_pid}' | awk '$1=="%71"{print $2}')
ps -p "$(pgrep -P "$pid" | head -1)" -o command=
```

Consequence for every seam below: **a hook or tool installed in `~/.omp/agent/...` is invisible
to a profiled agent.** Install into the project (`<repo>/.omp/...`) so it applies regardless of
profile, or into the exact profile root, and say which you did.

### Context files — why this file is load-bearing

omp auto-discovers project context before the session starts, by provider priority: native
`.omp/AGENTS.md` (100) > `.claude/CLAUDE.md` (80) > `.agent(s)/AGENTS.md` and `.codex/AGENTS.md`
(70) > … > bare `AGENTS.md` / `CLAUDE.md` (10), walking ancestors to the repo root; farther
ancestors inject first, cwd next, user last (`omp://context-files.md`). `.omp/RULES.md` is the
always-apply sticky rule file and rides in the system prompt.

**This file is the bare-`AGENTS.md` provider at depth 0** — the lowest priority tier, which is
exactly why it must be right: nothing overrides it here, and nothing else describes this lane.

### hub — processes, not `&`

A server, watcher, REPL, or anything needing later input **MUST** be a supervised process:

```bash
hub op:start name:"jev-mcp" application:"node" args:["dist/server.js"] ready:{log:"listening", timeout:30}
hub op:logs name:"jev-mcp" follow:true cursor:<byte>
hub op:send name:"jev-mcp" text:"…"        # stdin ; keys:["CTRL_C"] ; signal:"SIGTERM"
hub op:stop name:"jev-mcp"
```

`ready.log` is a JS `RegExp` (no `(?i)` — use `[Ll]istening`); `ready.port` probes TCP; both
supplied means both must pass. Readiness MUST be observed — process creation is not readiness.
Caps worth knowing: mailbox 100 messages/agent, job retention ~5 min, names 1–48 chars.

### Approval, secrets, and the paid surface inside omp

- `--approval-mode always-ask|write|yolo` gates tools by tier (`read`/`write`/`exec`); a tool with
  no declared tier is treated as `exec` (`omp://approval-mode.md`).
- omp's secret obfuscation is **disabled by default** (`secrets.enabled`, `omp://secrets.md`).
  **Do not rely on it to protect `TYPESAFE_API_KEY`** — our rule in
  [Secrets and the Paid Surface](#secrets-and-the-paid-surface-critical) stands on its own.
- Env precedence: process env → project `.env` → agent `.env` → config-root `.env` → `~/.env`,
  each only filling keys that are still empty (`omp://environment-variables.md`).

---

## Jev × omp Integration — Seams and the Validation Ladder

**This is the point of the lane.** Jev answers typed questions about a state in ~1 s; omp is a
harness that makes hundreds of tool-call, context, and compaction decisions per session and
exposes every one of them as an interception point. The pairing is the product.

### The seams, ranked by leverage

| # | Seam | omp mechanism | The Jev question | Why it is the right host |
|---|---|---|---|---|
| 1 | **Command safety gate** | `tool_call` hook in `<repo>/.omp/hooks/pre/*.ts` → `{block:true, reason}` | Noul: *"this command destroys unrecoverable data"* | the hook is **fail-closed**: a handler that throws blocks the call, and the first `block` short-circuits (`omp://hooks.md`) |
| 2 | **Context keep/drop** | `context` hook → `{messages}` (chained per LLM call) | Noul per message: *"this is needed for the current task"* | exactly `fast-jev-compaction`'s design, but at omp's own per-call context boundary |
| 3 | **Compaction judgment** | `session_before_compact` → `{cancel, compaction}` ; `session.compacting` → `{prompt, context, preserveData}` | Score/Noul over candidate entries | omp already walks `["remote","snapcompact","handoff","shake","soft"]`; this adds a *judged* keep set with `firstKeptEntryId` |
| 4 | **Model-callable judgment** | custom tool in `<repo>/.omp/tools/*.ts` (`pi.zod` params, `signal`, `onUpdate`) | any Choice/Score/Noul | the model can ask for a calibrated number instead of asserting one |
| 5 | **Out-of-process Jev** | MCP server in `.omp/mcp.json` (`stdio`/`http`/`sse`) | the three primitives as tools | isolates the paid call, survives `/mcp reload`, per-server failure isolation |
| 6 | **Host-owned tool / URI** | `set_host_tools` / `set_host_uri_schemes` over `--mode=rpc` | `jev_ask`, or `jev://score/<id>` | the *host* owns the key and the budget; the agent never sees either |
| 7 | **Output triage** | `tool_result` hook → `{content, details}` | Score: *"signal density of this output"* | trims a 50 KiB tool result before it reaches the context |

### What the docs say is NOT possible — do not design around these

- **A blocked tool call is an error, not a redirect.** A hook can refuse; it cannot force the
  model to call something else (`omp://hooks.md`).
- **`tool_result`'s returned `isError` is typed but not applied** by the wrapper on the success
  path. You can rewrite content, not flip the verdict.
- **Eval-prelude `browser.*` / `computer.*` / `tab.run(...)` calls are host-bridge calls and emit
  NO `tool_call` / `tool_result`** (`omp://hooks.md`). A safety gate built on `tool_call` is
  **blind** to them. Say so in the demo's README; a gate that silently misses a path is worse
  than no gate.
- **Hooks and extensions are not sandboxed.** They run in-process with the session's credentials.
  An MCP server is the isolating option (`omp://mcp-runtime-lifecycle.md`).
- **A hook directly in `.omp/hooks/` is silently not discovered** — it must be in `pre/` or
  `post/`, and the miss reports **no error**. Prove discovery, do not assume it.

### The validation ladder — name your rung, never round up

| Rung | What you have | How you prove it | What you may claim |
|---|---|---|---|
| **L0** | policy logic only | unit tests against a fake asker, no key, no omp | `offline-verified` |
| **L1** | the real Jev answer | one budgeted live call, model version recorded | `live-verified (N=…)` |
| **L2** | the seam loads | omp session starts with the hook/tool/server present and lists it (`get_state.dumpTools`, `/mcp`, `available_commands_update`) | `loaded` — **not** `working` |
| **L3** | the seam **fires** | a real tool call in a real omp session is blocked / rewritten / answered, and a **known-bad input makes it refuse**; frame or transcript pasted | `wired-and-proven-to-trip` |
| **L4** | it survives a session | a full working session with the seam active, cost and latency recorded, and the healthy path **silent** | `validated` |

Rules on the ladder:

- **L3 requires the negative direction.** A gate proven only on the good input is an over-strict
  gate waiting to be routed around; a gate proven only on the bad input is a nag. Both, or it is
  L2.
- **An empty scan set is an ERROR.** A hook that saw zero tool calls did not pass.
- **Silent on the healthy path.** A seam that comments on every valid command gets uninstalled,
  which is a worse outcome than never shipping it.
- **Never validate against a scratch session and call it the fleet.** `--mode=rpc` spawns a fresh
  session; that is L3 at best for anything that depends on real session history.
- **Cost is part of validation.** A per-tool-call Jev question multiplies by the session's tool
  count. Record calls-per-session and the money, or the seam is unshippable however correct.

### Where to install, and why it matters

Prefer **project scope** (`<repo>/.omp/hooks/pre/…`, `<repo>/.omp/tools/…`, `<repo>/.omp/mcp.json`):
it applies to every agent in that repo regardless of which of the eleven profiles they launched
under, and it is reviewable in git. Use a profile root
(`~/.omp/profiles/<name>/agent/…`) only for something deliberately scoped to one agent identity,
and say which profile in the `EVAL.md` row. **`~/.omp/` is omp's state, not ours — a write there
is a substrate change**, and this workspace root is not a git repo, so nothing installed from
here is reviewable unless it lands in a real repo.

---

## Beads (br) — Dependency-Aware Issue Tracking

Beads provides a lightweight, dependency-aware issue database and CLI (`br` — beads_rust) for selecting "ready work," setting priorities, and tracking status.

**Important:** `br` is non-invasive—it NEVER runs git commands. After `br sync --flush-only`, you must manually `git add .beads/ && git commit`.

**Where jev work is tracked:** in **the target product repo**, labelled `jev`. This root is not a
git repository, so a `.beads/` here could never be synced or reviewed. A demo that has no owning
repo yet has no bead yet — that is a signal you are still in Stage 0.

```bash
br ready --json            # ready work, no blockers
br show <id>               # full detail with dependencies
br create --title="…" --type=task --priority=2
br update <id> --status=in_progress
br close <id> --reason "…"
br sync --flush-only       # export to JSONL (no git operations)
```

Conventions: Beads is the single source of truth for status/priority/dependencies; Agent Mail is
conversation and audit. Use the bead id as the Mail `thread_id`, prefix subjects `[<id>]`, and put
the id in the file-reservation `reason` and the commit message.

---

## bv — Graph-Aware Triage Engine

bv is a graph-aware triage engine over `.beads/beads.jsonl`. **CRITICAL: use ONLY `--robot-*` flags. Bare `bv` launches an interactive TUI that blocks your session.**

```bash
bv --robot-triage          # THE MEGA-COMMAND: start here
bv --robot-next            # just the single top pick + claim command
bv --robot-plan --label jev                # parallel tracks scoped to this lane
bv --robot-triage | jq '.quick_ref'        # at-a-glance summary
bv --robot-insights | jq '.Cycles'         # circular deps (must fix!)
```

Run it **from the target repo**, since that is where the jev beads live.

---

## UBS — Ultimate Bug Scanner

**Golden Rule:** `ubs <changed-files>` before every commit. Exit 0 = safe. Exit >0 = fix & re-run.

```bash
ubs src/thing.ts probes/fast-jev-probe.mts   # specific files (<1s) — USE THIS
ubs $(git diff --name-only --cached)         # staged files — before commit
ubs --only=ts,py src/                        # language filter (3-5x faster)
ubs --ci --fail-on-warning .                 # CI mode — before PR
```

Parse: `file:line:col` → location | 💡 → how to fix | exit 0/1 → pass/fail.

Fix workflow: read finding → navigate to `file:line:col` → verify it is real → fix the root cause,
not the symptom → re-run `ubs <file>` → exit 0 → commit.

In this lane, treat these as **always fix**: a secret or key in any file, an unvalidated response
field used in a branch, a swallowed exception around a paid call, and an unbounded retry loop.

---

## ripwire — Deterministic Code Context (use before you read files)

`ripwire` is on `PATH` — **exactly one binary on this machine, `~/.local/bin/ripwire`,
`0.6.1 built_from=f45087a77`** — and is the cheapest way to understand any vendored clone, or
the target repo a demo is landing in, **without opening file after file.** Its own help is the
manual and it is vendored: `docs-mirror/ripwire/CLI-HELP.txt` (the 200-line summary),
`docs-mirror/ripwire/CLI-HELP-ALL.txt` (all 1826 lines, every flag in full),
`docs-mirror/ripwire/VERSION.txt`, and 15 design docs under `docs-mirror/ripwire/docs/`.

```bash
ripwire jev-review                          # ranked symbol map — start here, cold
ripwire jev-review --for="validate a jev response"   # task lens: ranked signatures framed for reuse
ripwire . --exemplar="call the jev api"     # the repo's best-in-class instance to IMITATE
ripwire jev-ultrafast --grep=validate_choice --legend=compact   # literal hit + enclosing symbol
ripwire <target-repo> --quality-delta       # before you call a port done: only what you made WORSE
ripwire <target-repo> --edit-check=<sym>    # did my edit change a contract someone depends on?
ripwire <target-repo> --affected            # which tests to run for this change
ripwire . --doctor                          # index health; `ripwire . --skipped` lists dropped files
ripwire --help=all | rg -- '--<flag>'       # the full manual; `--help` alone is the summary
```

**`<dir>` is the one required argument.** `ripwire --doctor` with no directory exits with the
usage banner, not a health report — measured on 0.6.1. Every invocation names a target.

Three traps, all measured, all relevant here:

- **`--uses=<name>` is blind to wire-protocol names.** It indexes *definitions*, and a Jev
  question name or an RPC command name is **data**, not a symbol — a real one and a nonexistent
  one return the same empty shape. Use `--grep=<name> --legend=compact`, whose `tier` field
  separates a string/comment mention from a code hit.
- **`--legend=compact` is invalid with `--report`.**
- **A negative control drawn from vocabulary the corpus discusses is not a control.** Searching
  this tree for `noul` matches documentation *about* `noul`. Use a high-entropy nonce
  (`zzzz_cannot_exist_9c42`) and expect `files=0 hits=0`.

Division of labour: **ripwire** to understand and to rank; **`rg`** to hunt a known literal;
**`ast-grep`** to match or rewrite structure. Reaching for `rg` on "how does X work" wastes a
session; reaching for `ast-grep` on a codemod is the only safe way to apply one.

---

## ast-grep vs ripgrep

**Use `ast-grep` when structure matters.** It parses code and matches AST nodes, ignoring comments/strings, and can **safely rewrite** code.

**Use `ripgrep` when text is enough.** Fastest way to grep literals/regex.

- Need correctness or **applying changes** → `ast-grep`
- Need raw speed or **hunting text** → `rg`
- Often combine: `rg` to shortlist files, then `ast-grep` to match/modify

```bash
# Every place we call the API, structurally (TS)
ast-grep run -l ts -p 'fetch($URL, $$$ARGS)'

# Every Jev answer field read without validation (Python)
ast-grep run -l python -p '$ANS["probabilities"]'

# Quick textual hunt
rg -n 'api\.typesafe\.ai' --glob '!node_modules' --glob '!.venv'

# Combine speed + precision
rg -l -t ts 'TYPESAFE_API_KEY' | xargs ast-grep run -l ts -p 'process.env.$VAR' --json
```

---

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below.

1. **Append to `EVAL.md`** — every tree you touched: SHA, lane, exact commands, counts, and a
   `Boundary` line for what you did not run. Reserve the file first if other agents are live.
2. **File beads for remaining work** — in the owning product repo, labelled `jev`.
3. **Run the verification suite** for every tree you touched, plus `ubs` on changed files.
4. **Confirm no secret escaped** — `rg -n 'sk-|Bearer [A-Za-z0-9]|tskey' <changed files>` clean,
   and no captured response bodies committed.
5. **Report the honest state per capability** — `EXPLORED` / `PROBED` / `PORTED` / `ZERO`, with
   the reason. One line each.
6. **Hand off** — name the next concrete lever, not a plan to make a plan.

---

## cass — Cross-Agent Session Search

`cass` indexes prior agent conversations (Claude Code, Codex, Cursor, Gemini, ChatGPT, etc.) so we can reuse solved problems.

**Rules:** Never run bare `cass` (TUI). Always use `--robot` or `--json`.

```bash
cass health
cass search "jev typed questions" --robot --limit 5
cass view /path/to/session.jsonl -n 42 --json
cass capabilities --json
```

stdout is data-only, stderr is diagnostics; exit code 0 means success. Treat cass as a way to
avoid re-solving problems other agents already handled — this ecosystem is one week old and the
most likely prior solver is one of our own panes from yesterday.

---

Note for every pane in this session:

You will regularly see working-tree changes you did not make — in `package.json`, `uv.lock`,
`EVAL.md`, a clone's `node_modules`. **Do not stop and ask about them.**

```
Unexpected changes (need guidance)

- Working tree still shows edits I did not make in package.json, uv.lock, EVAL.md. Please advise
  whether to keep/commit/revert these before any further work. I did not touch them.
```

NEVER DO THAT. The answer is literally ALWAYS the same: those are changes created by the other
omp agents working in this session at the same time. It is not merely common, it happens multiple
times per minute. The way to deal with it is simple: you NEVER, under ANY CIRCUMSTANCE, stash,
revert, overwrite, or otherwise disturb in ANY way the work of another agent. Treat those changes
identically to changes you made yourself. If you genuinely need to know who is doing what, that is
what `hub list` and `hub send` are for — ask the peer, do not halt the session.

---

## Note on Built-in TODO Functionality

Also, if I ask you to explicitly use your built-in TODO functionality, don't complain about this
and say you need to use beads. You can use built-in TODOs if I tell you specifically to do so.
Always comply with such orders.

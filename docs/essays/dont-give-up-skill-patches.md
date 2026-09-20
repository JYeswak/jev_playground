# Don't Give Up — Skill patches

Patches for the `dont-give-up` skill, derived from lane evidence.
Do not apply these to any JSM-owned copy; house lessons stay in house skills.

Evidence for Pass 6: `docs/essays/dont-give-up-gaps.md` Pass 6. File:line
citations there are the authority; this page is the proposed skill text.

Passes 1–5 are **not merged**. Stubs point at
[PR #9](https://github.com/JYeswak/jev_playground/pull/9) through
[PR #13](https://github.com/JYeswak/jev_playground/pull/13). Pass 6
**folds** Pass 3 D / Pass 4 E+`requireKey` / Pass 4–5 K into one
ready-to-paste house-skill edit so an agent does not wait on those PRs.

## Pass 1 — Invented policy (stub)

Pass 1 patches live on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9). Not re-authored here.

## Pass 2 — Over-learned kill (stub)

Pass 2 patches live on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10). Not re-authored here.

## Pass 3 — Named hole then park (stub)

Pass 3 patches (documented `--projectId=` 3.1; inject-or-HALT 3.2) live on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11). Folded into
Pass 6 D / K / checklist below, not re-litigated.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 patches (`requireKey` / `readRow` 4.1–4.2; extension-authoring URL
4.4) live on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12). Folded into
Pass 6 E / K / checklist below, not re-litigated.

## Pass 5 — Paperwork and live proof (stub)

Pass 5 patches (never `?? 'unknown'`; product-tick close; live JSONL line)
live on
[PR #13](https://github.com/JYeswak/jev_playground/pull/13). Not re-authored
here. K below keeps inject-or-HALT and does not re-open G7/G8/G10.

---

## Pass 6 — Tool playbook holes

Ready-to-paste replacements for playbook **D**, **E**, **K**, and the
**decision checklist**. Extra pastes for A / B / C / F / I sit after,
so cass / fh / arsenal / dcg / jsm gain a lane example in the same
edit.

An agent applying the house skill: replace the matching `###` block
wholesale. Do not leave `--projectId=<id>`, `--workspace <project>`,
or `e.g. …/docs/extension-authoring` in the file after the paste.

### Patch 6.1 — Playbook D (replace wholesale)

Replace current playbook D (the block that still says
`--projectId=<id>`).

```markdown
### D. “Secret / env / key ‘missing’”

**Believe it’s there.** This workspace’s Infisical project is
`42b194c3-89d7-4ebb-895f-dd77ddf005ba` (see `.env.example:11`).
`jev/` has no `.infisical.json`. A CLI that says “run infisical
init … or pass in project id” means **UNLINKED DIRECTORY**, not
**MISSING SECRET** (`.env.example:27-31`).

Presence only — never print the value (indented so this paste is one fence):

    # names-only count (expect 1)
    infisical secrets --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba \
      | grep -c TYPESAFE_API_KEY

    # byte-count presence (never printenv alone)
    infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
      printenv TYPESAFE_API_KEY | wc -c

    # inject for the real command
    infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
      node work/omp-jev-review/live-probe.mjs

A bare `infisical secrets` / `infisical run` with no `--projectId`
failing in this directory is **not** a missing-secret receipt. Retry
with `--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba` before you
report absence. `wc -c` returning `0` after that retry is a HALT
with one named human decision (add the name to the project) — not
“key unset, park.”

The sanctioned client already embeds the fix
(`work/jev-client/src/index.ts:46-54`). Leftover `projectId=<id>` in
`README.md:696` / `scripts/jev-probe.mjs:38` is a defect, not a
template — the same probe’s header (`:6`) has the real id.

**Safety:** agents hold handles, not raw secrets. Prefer `infisical
run` injection over exporting into chat. Presence probes: `wc -c` or
`grep -c NAME`, never `cat`, never `echo $TYPESAFE_API_KEY`.
```

Why: skill D still ships `<id>`. `.env.example` already has the
working one-liner. Pass 3 named this; the house skill is still the
placeholder. STALE/unlinked here means “no `.infisical.json`”, not
“no secret.”

### Patch 6.2 — Playbook E (replace wholesale)

Replace current playbook E (the list that says `e.g. product
…/docs/extension-authoring`).

```markdown
### E. “Docs / examples / how do I build this package?”

30 seconds. Do not ask. Do not invent a factory.

1. Open the official page — this exact URL, in a copy-paste block:

   https://omp.sh/docs/extension-authoring

   Confirm the ship shape on that page:
   - `export default function (pi: ExtensionAPI) { pi.on(...) }`
   - `package.json` `"omp": { "extensions": ["./src/index.ts"] }`
     (legacy `"pi.extensions"` still accepted)
   - install: `omp plugin install <path|git|npm>`
     or `omp --extension /absolute/path`
   Native/configured directory scan is `*.{ts,js}` only.

2. Copy one working package in *this* repo, not a remembered
   factory:
   - `work/omp-harm-rule/harm-rule.ts:27-32`
   - `work/omp-jev-observer/src/observer.mjs:50-53`
   Manifest points at entry; default export registers `pi.on`.

3. **Neighbour co-presence before “zero events.”**
   Same session, same profile: a known-firing neighbour
   (dcg-tool-bridge / harm-rule) writes a row AND this module
   writes a row. 0 rows next to a firing neighbour means not
   loaded — missing `pi.on`, glob miss, or not on the
   `extensions:` list (`docs/INTEGRATIONS.md:167-172,192`).
   Silence alone is not a finding. `node --check` will not
   catch a lost `pi.on` line.

4. Isolated path first:

       infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
         omp --profile=jev-lab --no-extensions \
             --extension=$HOME/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts \
             -p 'run exactly: echo observer-live-proof' </dev/null

   Then offline arms with planted negatives, then **one live row**.

If step 1 is unrun, “no examples” / “how do I register this” is
forbidden. If step 3 is unrun, “0 rows” is forbidden.
`rg -n extension-authoring` going empty in this repo is the hole
this paste closes — put the URL in the skill, not an ellipsis.
```

Why: skill E said “e.g.” and hid the host. This lane reinvented
loader / `pi.on` / `extensions:` via 0-row live defects. The official
page plus one in-tree default export is the two-minute dig.

### Patch 6.3 — Playbook K (replace wholesale)

Replace the current K table.

```markdown
### K. “Live proof still failing”

Common mechanical holes (fix the invocation, don’t abandon the feature):

| Symptom | Dig |
|---|---|
| Piped stdin hang | Close stdin: `</dev/null` when the prompt is already on `-p` |
| “Endpoint / key not configured” / `unconfigured` / `is not set` | **Inject-or-HALT.** (1) `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- printenv <NAME> \| wc -c`. (2) If `wc -c` > 0, inject and run; quote one live row (`ok` / scores / latency / `error=null`). (3) If `wc -c` is 0, HALT with one named human decision (add `<NAME>` to that project). Offline may stub `classify` / inject a fake asker, then still write the live one-liner. **Forbidden:** log the error and leave a scoreboard cell OPEN. |
| Extension loads, zero rows | Co-presence vs a known-firing neighbour in the **same session**; check `pi.on` still present (`node --check` is blind); loader globs `*.{ts,js}`; config is `extensions:` list. Then open https://omp.sh/docs/extension-authoring and compare factory / manifest / `--extension` to what you shipped. Do not conclude “sees nothing” from silence (`docs/INTEGRATIONS.md:167-172,192`). |
| Selector says 0, author says N | **Two shapes, then keys().** omp session rows are (A) `{ customType: { type, data } }` (observer) and (B) `{ customType: "…", data }` (harm-rule / failure). `readRow` handles both (`work/jev-client/src/index.ts:136`; `TESTS.md:47`). Dump `keys()` / `requireKey` (`work/oracle-kit/index.mjs:116`) on the raw row before broadening. A selector that returns nothing is indistinguishable from a thing that is not there. |
| Full profile hangs | Minimal `--no-extensions --extension=<one>` path first (`jev-lab` is free; working profiles are the human gate). |
| `fh doctor` STALE / `ORACLE_DOMAIN_UNKNOWN` / binary off `PATH` | **STALE ≠ unusable.** Steal the ranked row and open file:line (`docs/INTEGRATIONS.md:11-16`). `fh oracles --domain jev` rc=4 is absence evidence (`docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14`), not a reason to invent a local catalogue. Off-`PATH` cass/fh/dcg/jsm: copy the worked command from `AGENTS.md` / this playbook; do not file “tool missing.” |
```

Why: K named the symptoms and left the agent to invent the next
command. The next command is already in `.env.example`,
`oracle-kit`, `jev-client`, and `INTEGRATIONS.md`.

### Patch 6.4 — Decision checklist (replace wholesale)

Replace the current “Decision checklist (before you stop)” list.

```markdown
## Decision checklist (before you stop)

- [ ] Did the user explicitly stop this path?
- [ ] Is this a *narrow* cost-benefit kill with a named cheaper substitute for *this* gate only?
- [ ] Did I search docs / marketplace / GitHub / local config / prior sessions?
- [ ] Did I open https://omp.sh/docs/extension-authoring (the real URL, not `…/docs/…`) before claiming “no examples”?
- [ ] Did I try the proven secret-injection from `.env.example` —
      `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>` —
      not `--projectId=<id>`?
- [ ] If Infisical said “run init or pass project id”: did I retry
      with that projectId before reporting a missing secret?
      Unlinked ≠ missing. Bare `<id>` in a command I am about to
      publish is a defect.
- [ ] If a receipt says `not configured` / `unconfigured` / `is not
      set`: did I run inject-or-HALT (`printenv NAME | wc -c`, then
      inject or one named human decision)? Logging the error and
      leaving OPEN is the park — forbidden.
- [ ] Before any absence claim (“missing”, “0 rows”, “cannot
      attribute”, “not there”): did I dump the record’s own keys
      (`inspectKey` / `Object.keys`) and read through `requireKey`
      (`work/oracle-kit/index.mjs:116`) / `readRow`
      (`work/jev-client/src/index.ts:136`)? Publishing “0” without
      the key list is the eighth-then-ninth failure — forbidden.
- [ ] If `fh doctor` reported STALE, or `fh` / `cass` / `dcg` / `jsm`
      is off `PATH` or returned `ORACLE_DOMAIN_UNKNOWN`: did I still
      steal the ranked row / copy the `AGENTS.md` command? STALE ≠
      unusable (`docs/INTEGRATIONS.md:11-16`).
- [ ] Can I ship scaffold → offline → one live row in one short loop?
- [ ] If blocked on a human: did I name the *one* decision and stop —
      not spawn detour docs?

If (1) is no and dig steps are incomplete → keep digging. Do not file
“blocked” or “deferred”.
```

Why: the old checklist asked “selector ≡ claim” and “did I search.”
This lane failed both with the tools already named. The boxes now
name the command that would have caught the miss.

---

### Patch 6.5 — Playbook A cass (replace the command block)

```markdown
### A. “Someone already solved this” (session / prompt archaeology)

**Tool:** `cass` (JSM skill `cass`). Never run bare `cass` (TUI).

    cass health
    cass search "jev typed questions" --robot --limit 5
    cass search "jev" --robot --limit 10
    cass view /path/to/session.jsonl -n 42 --json

These are the queries `AGENTS.md:890,1410-1412` already publishes.
Do not invent `--workspace <project>`. `--robot` or `--json` only.
If `cass` is off `PATH`, steal the query from `AGENTS.md` and keep
digging in `docs/demos/upstream-repro/` / `cass` is not a blocker.

**Goldmine principle:** repeated prompts are your best prompts. Mine
history before inventing a new approach.
```

### Patch 6.6 — Playbook B fh (keep STALE, add the lane citation)

Replace the `fh suggest` line and the paragraph under it.

```markdown
### B. “What does Franken / prior art say for this hole?”

**Tool:** `fh` (Franken Harvest)

    fh suggest "wire a typed Jev asker into an omp tool_call hook"
    fh search "typed question client" --limit 10
    fh agents --repo .
    fh oracles --domain jev          # this lane: rc=4 ORACLE_DOMAIN_UNKNOWN — still a finding
    fh doctor                        # STALE ≠ unusable — still steal the row
    fh rejected
    fh runbook <topic>

**STALE ≠ unusable, with a lane citation.** `docs/INTEGRATIONS.md:11-16`:
`fh doctor` may report STALE or degraded SCHEDULING; a 1/8
schedule-declaration miss does not retract shipped doctrine.
Pattern: **fh ranked, we opened** — `asupersync` `eprocess.rs:224-238`,
`franken_ocr` `RATCHET.md:33-51`, `franken_engine`
`promotion_gate_runner.rs:266-328`, `frankensearch`
`perf_ratchet.rs:732-740`. A ranking alone is not a citation.

`fh oracles --domain jev` returning rc=4
(`docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14`) is
absence evidence. Do not invent a local `oracles.tsv` that is green
only on this host. Off `PATH`: copy those file:line opens; do not
file “fh missing.”

**Gap shape:** every miss needs *what we are fixing* + *stolen ideas
with named sources*. A gap with no stolen idea is a complaint.
```

### Patch 6.7 — Playbook C arsenal (replace the off-machine table)

```markdown
### C. “I was about to hand-roll a primitive”

Before `sha256sum`, ad-hoc JWT, a second Jev POST, a third session-row
scanner, or a new digest: use the in-tree table. The Franken
“WHEN YOU NEED X, USE Y” arsenal is **not in this repo**
(`rg` empty on `e65a614`). Off-disk is STALE, not permission to
re-derive.

| Need | Use (this repo) |
|---|---|
| Typed Jev POST | `work/jev-client` — the only sanctioned caller (`TESTS.md:47`) |
| Absence claim | `requireKey` / `inspectKey` (`work/oracle-kit/index.mjs:116-129`) |
| omp session JSONL | `readRow` (`work/jev-client/src/index.ts:136-159`) — two shapes |
| Planted RED gate | `foundation/gates.sh --selftest` / `foundation/gates.d/` |
| Score / AUC / ECE | `work/oracle-kit` (`node work/oracle-kit/test.mjs` → 13/13) |

Depend on the named path; do not copy-paste a second client. Re-deriving
what you own is the expensive failure mode.
```

### Patch 6.8 — Playbook F dcg (replace the command block)

```markdown
### F. “Destructive command / tool blocked”

**Tool:** `dcg` (JSM)

    # Worked lane example — this is the denial that already fired here:
    #   dcg denied `git add -A` / `git add .`
    #   zeststream.shared_worktree:git-add-whole-tree
    #   AGENTS.md:249-250 · EVAL.md:232-233 · .flywheel/feedback/2026-09-17.md:17-18

    git add <path>...
    git diff --cached --stat    # must list ONLY paths you reserved
    # If you need to know *why* a command is blocked and dcg is on PATH:
    dcg explain "git add -A"
    dcg test "git add -A"

Blocks are checkpoints. The safe alternative is already in
`AGENTS.md`: stage explicit paths, never `-A` / `.`, never amend in
this shared tree. Override is a human step, last resort.

Do not cite frozen-corpus `dcg test` rows from other sessions
(`work/p3-calibration/toolcall-corpus-frozen.jsonl`) as *this* lane’s
worked example — that is the selector hole. Do not confuse CLI `dcg`
with the omp `dcg-guard` hook (`docs/INTEGRATIONS.md:88-90`).
```

### Patch 6.9 — Playbook I jsm (replace the command block)

```markdown
### I. “Skill / library already covers this”

    jsm search "omp extension authoring"
    ms search "dont-give-up"            # if ms is on PATH

If `jsm` is off `PATH`, that is not a missing-skill receipt. This
lane’s worked “jsm” row is **not** a search — it is the install
precondition at `docs/INTEGRATIONS.md:191`: the installed file must
be self-contained. `9e6c88d` imported
`../../dogfood-logger/src/logger.mjs`, a parent path that does not
exist after a copy into `~/.omp`. `348894e` inlined the record
builder. Copy `work/omp-harm-rule/harm-rule.ts` /
`work/omp-jev-observer/src/observer.mjs`.

JSM-owned skills are **read-only**. Put house lessons in *your*
skills (this file), not patches to Jeff’s copies. Frozen-corpus
`jsm search` rows from omp-orchestrator are not a jev worked example.
```

### Patch 6.10 — What not to do (additions)

Add to **What not to do**:

```markdown
- Treat `fh doctor` STALE, `fh oracles --domain jev` rc=4, or cass/fh/dcg/jsm
  off `PATH` as “tool unusable.” Steal the row; copy the `AGENTS.md` command
  (`docs/INTEGRATIONS.md:11-16`).
- Leave `projectId=<id>`, `projectId=…`, or `--workspace <project>` in a
  published command when `.env.example:15` / `AGENTS.md:1411` already have
  the real form.
- Write `e.g. …/docs/extension-authoring` instead of
  https://omp.sh/docs/extension-authoring.
- Claim a field / row / event is absent without `requireKey` /
  `inspectKey` / `readRow` (`work/oracle-kit/index.mjs:116`;
  `work/jev-client/src/index.ts:136`).
- Cite `ubs` exit 3 (docs-only empty scan) as green
  (`NEGATIVE_EVIDENCE.md` R6).
- Hand-roll a second `askJev` / session-row scanner when
  `work/jev-client` and `work/oracle-kit` already exist.
```

### Patch 6.11 — Skill / tool index (replace the cass/fh/dcg/jsm rows)

```markdown
| Need | Reach for |
|---|---|
| Past prompts / decisions | `cass search "jev typed questions" --robot --limit 5` (`AGENTS.md:1411`) |
| Franken doctrine / adoption | `fh suggest` / `fh doctor` — STALE ≠ unusable (`docs/INTEGRATIONS.md:11-16`) |
| Native crate / typed caller | `work/jev-client` + `work/oracle-kit` (Franken arsenal is not in this tree) |
| Destructive cmd blocked | `git add <path>` — `dcg` already denied `-A` (`AGENTS.md:249`) |
| Pre-commit bug scan | `ubs <ts/py/rs files>` — exit 3 on docs-only is **not** a pass |
| Skill lookup | `jsm search` if on PATH; else `docs/INTEGRATIONS.md:191` + in-tree default export |
| Secret / unlinked dir | `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>` |
| omp extension shape | https://omp.sh/docs/extension-authoring + `harm-rule.ts:27-32` |
| Absence claim | `requireKey` / `readRow` before “0 rows” |
```

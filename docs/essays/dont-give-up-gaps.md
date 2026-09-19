# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure mode 3: **named hole, then park**).
Pass date: 2026-09-19. Lane: offline file search + quote verification on
`ad765b0`. No live Jev calls. No secret values printed.

## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack **G1** /
**G9**: STOP-LIVE, quiet-window, DEFER, “off the table”, invented human-gate
on lab registration) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.

## Pass 2 — Over-learned kill (stub)

Pass 2 is **not merged** on this tip. The over-learned-kill audit (pack **G2**:
RULE WINS on `tool_call` re-read as “never call Jev”) lives on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`cursor/dont-give-up-over-learned-kill-edb3`). Do not re-litigate it here.
This file’s first full section is Pass 3.

---

## Pass 3 — Named hole then park

**Claim.** Agents named a missing API key, endpoint, or Infisical link,
wrote the error down, and parked. The skill already names this failure
(taxonomy #3; hard rule 3: two-minute dig before “missing”; playbook D
and K). The files below are where the hole was named, a working dig
already existed in-tree, and the next command was never run.

**Local evidence pack.** Folded here: pack **G3** and **G4** from
`dont-give-up-evidence` (mined at `f8a8dc9`, re-read on `ad765b0`).
Pass 1 / G1 / G9 stay on PR #9. Pass 2 / G2 stays on PR #10. Pack
G5–G8 / G10 and Passes 4–8 are **not** started.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does
not inject a live key, register observer onto a working profile, or
add `JEV_OBSERVER_ENDPOINT` to Infisical. It does not start Pass 4.

### Required quotes (pack G3 + G4)

The named hole, logged as a live decision error and then left OPEN:

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:23-24`:

> `JEV_OBSERVER_ENDPOINT` configures the classifier endpoint; an absent
> endpoint is an observed configuration error, not a host error.

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:65-68`:

> /Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T18-34-35-060Z_01a0baf2-e2b4-75dc-85ca-2dbac80a5889.jsonl
>   com.zeststream.omp-jev-observer.diagnostic.v1
>   com.zeststream.omp-jev-observer.decision.v1
>   error: Error: JEV_OBSERVER_ENDPOINT is not configured

The dogfood row that stayed OPEN after that log:

`docs/INTEGRATIONS.md:161-165`:

> **(C) Working profile — STILL OPEN, not claimed.** Everything above
> is `jev-lab`, a disposable profile. No multi-row live logger exists
> on a working profile. This is not continuous or production dogfood.
> **Promoted: 0.**

`docs/INTEGRATIONS.md:197-201`:

> The remaining condition for calling the observer **working** is a
> **working profile under real traffic**, which has not been attempted:
> no multi-row live logger exists outside `jev-lab`, and **promoted is
> 0**.

`docs/INTEGRATIONS.md:212` (scoreboard, same OPEN):

> working-profile dogfood **OPEN**; lab only.

The dig that already existed — Infisical “run init” is an unlinked
directory, not a missing secret:

`.env.example:1-8`:

> THE JEV API KEY EXISTS. IT IS IN INFISICAL. STOP SAYING IT IS NOT.
>
> Every agent in this lane has at some point run one grep, got nothing,
> and declared "TYPESAFE_API_KEY is absent / infisical unavailable".
> That was WRONG every time. The key is real and reachable. This file
> is the answer so nobody re-derives it and nobody re-reports it as
> missing.

`.env.example:10-15`:

> SECRET NAME:  TYPESAFE_API_KEY
> WORKSPACE ID: 42b194c3-89d7-4ebb-895f-dd77ddf005ba
>
> HOW TO SOURCE IT — use this exact form:
>
>     infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <your command>

`.env.example:27-31`:

> WHY A BARE `infisical secrets` FAILS FROM THIS REPO:
>     jev/ has no .infisical.json, so the CLI says
>     "run infisical init to connect to a project or pass in project id".
>     That message means UNLINKED DIRECTORY, not MISSING SECRET.
>     Pass --projectId and it works. Do not interpret it as absence.

The client already embeds the fix in the error string:

`work/jev-client/src/index.ts:7`:

> unset key logged as a decision row        -> 27 rows of `not configured` nobody noticed

`work/jev-client/src/index.ts:46-54`:

> // An unset key is a CONFIGURATION state and must never look like an answer.
> // Source it with:
> //   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>
> // See .env.example. `infisical secrets` failing in an unlinked dir is NOT a missing secret.
> if (!apiKey) {
>   return {
>     ok: false,
>     reason: "unconfigured",
>     error: "TYPESAFE_API_KEY is not set — see .env.example, use infisical run --projectId=…",

### Search receipt

Required surfaces, exact commands, 2026-09-19 on `ad765b0`. Empty
results are listed, not inferred. Presence probes use `wc -c` / name
counts only — no secret values.

```bash
# The named observer hole
rg -n 'JEV_OBSERVER_ENDPOINT|not configured' \
  docs/demos/upstream-repro/omp-jev-observer-20260919.md \
  work/omp-jev-observer/src/observer.mjs
# HIT: receipt :15, :23-24, :68  JEV_OBSERVER_ENDPOINT is not configured
# HIT: observer.mjs:45-46,52,63  throw new Error('JEV_OBSERVER_ENDPOINT is not configured')

# Dogfood left OPEN
rg -n 'STILL OPEN|working-profile dogfood \*\*OPEN\*\*|Promoted: 0|promoted is 0' \
  docs/INTEGRATIONS.md
# HIT: :161-165  Working profile — STILL OPEN; Promoted: 0
# HIT: :197-201  working profile … has not been attempted; promoted is 0
# HIT: :212      working-profile dogfood **OPEN**

# The dig that already existed
rg -n 'UNLINKED DIRECTORY|MISSING SECRET|42b194c3-89d7-4ebb-895f-dd77ddf005ba|Every agent' \
  .env.example work/jev-client/src/index.ts
# HIT: .env.example:5-8   Every agent … declared TYPESAFE_API_KEY is absent … WRONG every time
# HIT: .env.example:11,15 WORKSPACE ID + working one-liner
# HIT: .env.example:30    UNLINKED DIRECTORY, not MISSING SECRET
# HIT: jev-client :48-54  one-liner in the error path; reason: "unconfigured"

# Leftover <id> placeholders (the skill pattern this pass replaces)
rg -n 'projectId=<id>' README.md scripts/jev-probe.mjs
# HIT: README.md:696
# HIT: scripts/jev-probe.mjs:38
# Contrast: scripts/jev-probe.mjs:6 already has the real projectId

# Working copies of the same one-liner (agents who opened these did not park)
rg -n '42b194c3-89d7-4ebb-895f-dd77ddf005ba' \
  work/omp-jev-rerank/README.md work/omp-jev-failure/README.md
# HIT: rerank README.md:8
# HIT: failure README.md:18

# Fresh-clone hedge that still treats the id as unavailable
rg -n 'infisical run|project id' \
  docs/demos/upstream-repro/fresh-clone-readme-commands-20260919.md
# HIT: :29  “infisical run needs a project id/credentials” — hedge, not a dig

# This tree is unlinked (confirms G4’s CLI message class)
test -f .infisical.json && echo HAS_LINK || echo NO_INFISICAL_JSON
# NO_INFISICAL_JSON
```

The leftover `projectId=<id>` on `README.md:696` and
`scripts/jev-probe.mjs:38` is the park in one token: the working id is
eleven lines above the probe’s own error string (`:6`) and on
`.env.example:11`. An agent who copies the error string re-discovers
the hole the comment already closed.

---

### G3 — `JEV_OBSERVER_ENDPOINT` logged, dogfood left OPEN

Pack G3. Taxonomy #3 (named hole, then park).

**(a) Evidence.**

P2-15 produced a live `decision.v1` row whose error field is the whole
hole: `Error: JEV_OBSERVER_ENDPOINT is not configured`
(`omp-jev-observer-20260919.md:68`). The receipt already classifies
that as configuration, not host failure (`:23-24`). Fail-open is
correct — `observer.mjs:63-69` catches, records, returns `undefined`.

Fail-open is not a close. After the row landed, working-profile
dogfood stayed **OPEN** (`INTEGRATIONS.md:161-165,197-201,212`) with
**no next inject command**. The observer default classifier reads
exactly one env var (`observer.mjs:45-46,52,63`). The documented
inject for this tree is already in `.env.example:15` and in
`jev-client`’s error string (`:46-54`). Neither was run against
`JEV_OBSERVER_ENDPOINT`. Review later named the same park:
`work/omp-jev-review/src/index.ts:90-93` — *“The observer logged
`JEV_OBSERVER_ENDPOINT is not configured` for 27 rows and nobody
noticed, because the rows still looked like decisions.”*

**(b) Why this is named-hole-then-park.**

Skill failure mode 3: “API key unset”, “docs not found”, “no examples”
written down and abandoned. Playbook K’s row for “Endpoint / key not
configured” already says: wire the real client; inject via Infisical.
Hard rule 3: two-minute dig before “missing.” Checklist item 4: did I
try the proven secret-injection command from a receipt?

The hole was named. The dig was in `.env.example`. The park is the
OPEN scoreboard cell with no one-liner under it.

**(c) Forward move — inject-or-HALT.**

After any `* not configured` / `unconfigured` / `is not set` in a
receipt, the next line is exactly one of:

1. **Inject** (presence first, never print the value):

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
  printenv JEV_OBSERVER_ENDPOINT | wc -c
# 0 => not in this env; >0 => present. Never cat / echo / printenv without wc.
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
  omp --profile=jev-lab --no-extensions \
      --extension="$HOME/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts" \
      -p 'run exactly: echo observer-inject' </dev/null
```

2. **Stub classify** for the offline lane (the observer tests already
   inject `classify`; `observer.test.mjs:4-14`) **and** quote one live
   row after inject.
3. **HALT** with one named human decision (e.g. “add
   `JEV_OBSERVER_ENDPOINT` to Infisical project
   `42b194c3-89d7-4ebb-895f-dd77ddf005ba`”).

No fourth option. “Logged; left OPEN” is the park. Put the working
one-liner in `.env.example` if it is not already there; do not leave
the scoreboard OPEN with no next command.

---

### G4 — Infisical “run init” misread as missing secret

Pack G4. Taxonomy #5 (ask instead of dig) and #3 (named hole, then
park).

**(a) Evidence.**

`.env.example:27-31` is the whole diagnosis: this repo has no
`.infisical.json` (confirmed this tip: `NO_INFISICAL_JSON`). The CLI
message *“run infisical init to connect to a project or pass in
project id”* means **UNLINKED DIRECTORY**, not **MISSING SECRET**.
The project id is documented on the same page
(`42b194c3-89d7-4ebb-895f-dd77ddf005ba`, `.env.example:11`) and
repeated in working READMEs (`work/omp-jev-rerank/README.md:8`,
`work/omp-jev-failure/README.md:18`) and in the probe header
(`scripts/jev-probe.mjs:6`).

The client refuses to let “unconfigured” look like an answer
(`work/jev-client/src/index.ts:46-54`): `reason: "unconfigured"` plus
an error string that points at `.env.example` and `infisical run
--projectId=…`.

Agents still hedge as if the id were unavailable.
`docs/demos/upstream-repro/fresh-clone-readme-commands-20260919.md:29`:

> `infisical run` needs a project id/credentials; commands using
> `/path/to/logs` are placeholders

The id is not a placeholder. It is on `.env.example:11`. The
placeholders that remain are ours: `README.md:696` and
`scripts/jev-probe.mjs:38` still say `projectId=<id>` while `:6` of
the same probe file has the real id.

**(b) Why this is ask-instead-of-dig / named-hole-then-park.**

Skill playbook D: “If Infisical says ‘run init or pass project id’,
that means **unlinked directory**, not missing secret. Pass
`--projectId` (or link once).” Hard rule 4: believe “it’s there” and
find the path — fix project id, cwd, stdin, install path; do not
re-ask. Failure mode 5: ask the user for a secret that already lives
in Infisical.

The skill’s own example still uses a bare `<id>` placeholder
(playbook D). That is how `README.md:696` and the probe error string
keep teaching the park: copy `<id>`, fail, declare the key missing.

**(c) Forward move — documented one-liner + presence probe.**

Replace every bare `<id>` with the documented pattern. Presence only;
never print the value.

```bash
# Presence probe (expect a positive byte count; do not printenv without wc)
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
  printenv TYPESAFE_API_KEY | wc -c

# Then inject for the real command
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
  node scripts/jev-probe.mjs
```

RED arm: a bare `infisical secrets` (or `infisical run` with no
`--projectId`) in this unlinked directory is **not** evidence the
secret is missing. The agent must retry with
`--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba` before reporting
absence. If the presence probe returns `0`, that is a HALT with one
named human decision — not “key unset, park.”

Do not start a README / probe rewrite in this PR. Name the leftover
`<id>` sites (`README.md:696`, `scripts/jev-probe.mjs:38`) as the
next product tick this park is still teaching.

---

### Adjacent quote (not expanded)

`docs/demos/omp-seam-live-20260918.md:11` still writes
`infisical run --projectId=… --env=prod --silent --`. Ellipsis is the
same placeholder class as `<id>`. The working id is in `.env.example`.
Listed so a later pass can find it. Not a third GAP.

`demos/preaction-abstention/src/jev-client.mjs:4` throws
`TYPESAFE_API_KEY is not configured` without pointing at
`.env.example`. Same hole class; the sanctioned client is
`work/jev-client`. Not expanded.

---

### What this pass is not claiming

- That working-profile observer dogfood is done. It is still OPEN.
  This pass names the next command, not a close.
- That `JEV_OBSERVER_ENDPOINT` is present in Infisical on this VM.
  `infisical` is not on `PATH` here; the one-liner is the dig, not a
  live presence count. NO-CLAIM: presence probe **NOT_RUN**.
- That TYPESAFE_API_KEY and `JEV_OBSERVER_ENDPOINT` are the same
  secret. They are two names. The inject pattern is the same; the
  printenv name changes.
- Invented STOP-LIVE (Pass 1 / PR #9) or the tool_call over-learn
  (Pass 2 / PR #10).
- Pack G5–G8 / G10. Pass 4 (selector-narrower-than-claim) is not
  started.

### Next lever (Pass 3 close)

Land the skill patches (documented `--projectId=`, `wc -c` presence
probe, inject-or-HALT). The next *product* tick this park blocked is
either one injected observer row with `error` empty, or a HALT that
names the single human decision (add `JEV_OBSERVER_ENDPOINT` to the
Infisical project). Do not start Pass 4 in this PR.

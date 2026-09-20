# dont-give-up skill-loop gaps (consolidated)

Merged from PRs #9–#15 into one ship to avoid serial file conflicts.

<!-- from PR #9 (Pass 1) -->
## Pass 1 — Invented policy

**Claim.** This lane has invented STOP / DEFER / quiet-window / "off the table"
language that Joshua did not utter, then treated the invention as a reason to
stop. The skill names that failure; the files below are where it fired.

**Local evidence pack.** Folded here: pack **G1** and **G9** from
`dont-give-up-evidence` (mined at `f8a8dc9`, 2026-09-19). Pack G2–G8 / G10
are other failure modes and are **not** expanded in this pass.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does not
reclassify Joshua's scoped quiet-window quote as invented. It does not treat
lane `DEFER` / `BLOCKED` / `REFUSE` as invented merely because those words
appear. A hit is invented only when (1) the user did not say it, and (2) the
text was used to walk away from a diggable hole. This PR does not start
Pass 2.

### Invented-policy quote table (pack keyword map, verified)

| Token | file:line | Quote / role |
|---|---|---|
| off the table; STOP-LIVE; deferred registration; quiet-window gated | `docs/INTEGRATIONS.md:174` | *“Live omp was never taken off the table. There is **no standing ban** on registering into working omp profiles. The fleet invented "STOP-LIVE" / deferred registration as reasons not to work. This row is not an indefinite deferral and not quiet-window gated.”* |
| STOP-LIVE (ledger retract) | `EVAL.md:448` | *“No invented STOP-LIVE ban.”* |
| quiet-window not a science gate | `docs/INTEGRATIONS.md:181` | *“Quiet-window is not a science gate for that work.”* |
| quiet-window / DEFER not a loop hold | `docs/INTEGRATIONS.md:186` | *“They are not a quiet-window gate and not a reason to DEFER the loop”* |
| quiet-window = timing only | `NEGATIVE_EVIDENCE.md:1286-1288` | *“a verdict whose evidence is ‘it did not finish in time’ requires a **quiet-window re-run**”* |
| quiet-window leaked onto 502 | `docs/demos/STATUS.tsv:35` | `retry-in-quiet-window` chained to `backend-502-message-content-missing` |
| human-review / deliberately UNRUN | `docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43` | *“Registration requires human review because an extension load… can affect every tool call in the fleet.”* |
| lab surface is free (contradicts UNRUN) | `docs/INTEGRATIONS.md:180-181` | pane-0 / added test pane; RUN-CLONE / `jev-lab` free |

Adjacent *invented* quotes that are **not** STOP/DEFER/quiet-window policy,
cited so they are not lost, and left for later passes:

- Invented `helpful` gate: `README.md:724-727`; `.flywheel/feedback/2026-09-19-honesty-pass.md:24`.
- Invented `sessionId: 'unknown'`: `docs/demos/upstream-repro/omp-jev-observer-sentinel-cleanup-20260919.md:13`.
- Invented `dcgVerdict ?? 'unknown'`: `docs/INTEGRATIONS.md:64,156,200-201` (pack G7; not expanded here).

### Search receipt

Required surfaces, exact commands, 2026-09-19. Empty results are listed, not
inferred.

```bash
# README
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' README.md
# HIT: README.md:803 quiet-window; :724 invented helpful gate (adjacent)

# docs/INTEGRATIONS.md
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' docs/INTEGRATIONS.md
# HIT: :174 invented STOP-LIVE / off the table retraction
# HIT: :181 quiet-window is not a science gate
# HIT: :186 "not a quiet-window gate and not a reason to DEFER"

# AGENTS.md
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' AGENTS.md
# HIT: :1495 DEFER as legitimate acceptance vocabulary (not an invented ban)

# VERDICT.md — first pattern: no hits
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' VERDICT.md
# EMPTY
# follow-up for the scheduling-deferral cousin:
rg -n 'deferral|scheduling, not a blocker' VERDICT.md
# HIT: :124

# docs/demos/STATUS.tsv
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|invented "STOP|deferred registration|\bDEFER\b' docs/demos/STATUS.tsv
# HIT: :35 retry-in-quiet-window (UP-R8)
# follow-up:
rg -n 'deferral' docs/demos/STATUS.tsv
# HIT: :23 COD-H4 PRICED-4h-build-deferral-not-blocker

# docs/demos/**
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' docs/demos --glob '*.{md,tsv,json}'
# HIT: STATUS.tsv:35
# HIT: docs/demos/upstream-repro/ablate-rerun-classD-20260919.md:1,31
# HIT: docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43

# receipts (no receipts/ directory exists; searched the receipt locations that do)
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' docs/demos/duel-2/runs
# EMPTY

rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' foundation
# EMPTY

rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' demos
# EMPTY (first-party demos/)

# supporting ledger (not in the required list; used only to quote Joshua vs the fleet)
rg -n 'STOP-LIVE|quiet[- ]window|off the table|off-the-table|deferred registration|deliberately UNRUN|requires human review' EVAL.md NEGATIVE_EVIDENCE.md
# HIT: EVAL.md:448 "No invented STOP-LIVE ban"
# HIT: NEGATIVE_EVIDENCE.md:1271-1288 Joshua quiet-window quote + R30 rule
```

Empty on this pattern (required or receipt-adjacent): `VERDICT.md` (exact
STOP/quiet-window/off-the-table pattern), `docs/demos/USAGE-MAP.md`,
`docs/demos/ORACLE-MANIFEST.tsv`, `GATES.md`, `docs/demos/duel-2/runs/`,
`foundation/`, `demos/`. There is **no** `receipts/` directory in this tree.

---

### G1 — Invented STOP-LIVE / quiet-window / DEFER / “off the table”

Pack G1. Taxonomy #1 (invented policy).

**(a) Path + quote.**

`docs/INTEGRATIONS.md:174`:

> Live omp was never taken off the table. There is **no standing ban** on
> registering into working omp profiles. The fleet invented "STOP-LIVE" /
> deferred registration as reasons not to work. This row is not an indefinite
> deferral and not quiet-window gated.

`EVAL.md:448`:

> No invented STOP-LIVE ban.

`docs/INTEGRATIONS.md:181`:

> Quiet-window is not a science gate for that work.

`docs/INTEGRATIONS.md:186`:

> They are not a quiet-window gate and not a reason to DEFER the loop

Joshua's recorded stop is narrower than any of those fleet tokens.
`NEGATIVE_EVIDENCE.md:1271-1273` (raised by Joshua, not discovered by us):

> *"i have other testing going on locally with stuff so dont mark anything
> 100% done until we test more thoroughly in a quiet window"*

`NEGATIVE_EVIDENCE.md:1286-1288` keeps that hold on **timing**:

> **Rule:** a verdict whose evidence is "it did not finish in time" requires
> a **quiet-window re-run** before it is terminal. Timing is the one
> measurement that shared hardware silently corrupts…

That is a claim-level hold on local-model "100% done", not a ban on
registering an observe-only fail-open hook, and not a science gate.

**(b) Why this is a dont-give-up failure.**

Failure mode 1 (invented policy) and hard rule 1 (do not invent blockers).
Checklist item 1 — "Did the user explicitly stop this path?" — is **no** for
STOP-LIVE / "off the table" / DEFER-the-loop / quiet-window-as-science-gate.
The scoreboard had to *retract* tokens the fleet minted. The skill names
the failure but does not give a worked retract: quote the user or write
"none", then map the hole to a live surface.

**(c) Concrete forward move.**

Land a **worked retract script** on skill hard-rule #1 (see
`docs/essays/dont-give-up-skill-patches.md` Pass 1, patch 1.6):

1. **Quote the user stop, or write `none`.** If `none`, the ban is yours —
   retract it in the same sentence.
2. **Map the hole to a live surface that is already licensed:** RUN-CLONE /
   `omp --profile jev-lab` / pane 0 / an added test pane
   (`docs/INTEGRATIONS.md:178-181`). Mid-flight panes stay untouched.
3. **Forbid expanding quiet-window past timing re-runs.** A 502, a missing
   field, a loader that writes zero rows, or an unread `.d.ts` is a dig,
   not a calendar.

Do not start a fleet-wide rewrite in this PR. The next product tick the
invented STOP-LIVE blocked is still one live observer row on that surface.

---

### G9 — Invented human-gate on lab registration

Pack G9. Invented policy (taxonomy #1) with ask-instead-of-dig / blocked-on-human
detour as the mechanism. Distinct from G1: G1 is the fleet token; G9 is the
receipt that minted a **human review** requirement for a disposable lab copy.

**(a) Path + quote.**

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:36-43`:

> ## Registration command — deliberately UNRUN
>
> `cp work/omp-jev-observer/src/observer.mjs ~/.omp/omp-extensions/omp-jev-observer.mjs`
>
> This command was not run. No file under `~/.omp` was modified by this unit.
> Registration requires human review because an extension load or hook error
> can affect every tool call in the fleet.

Same-day doctrine contradicts a fleet-wide human gate, including for lab.
`docs/INTEGRATIONS.md:180-181`:

> **Register / dogfood on pane 0 or an added test pane.** Leave mid-flight
> panes untouched. Promote only after receipts.
>
> **RUN-CLONE.** Local clones and disposable lab profiles
> (`omp --profile jev-lab`) are free for atomic mutation, planted known-bad,
> and improvement loops. Quiet-window is not a science gate for that work.

The cost of the invented gate is in the same receipt. After P2-13 closed
UNRUN, **P2-15 registered the disposable `jev-lab` copy** and found the
real 0-row defect (`omp-jev-observer-20260919.md:47-53,57-60`):


<!-- from PR #10 (Pass 2) -->
## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack **G1** /
**G9**: STOP-LIVE, quiet-window, DEFER, “off the table”, invented human-gate
on lab registration) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.
This file’s first full section is Pass 2.

---

## Pass 2 — Over-learned kill

**Claim.** A cost-benefit kill that is already written as *this surface*
(`tool_call` / four regexes beat live Jev 12/12 vs 11/12 at FP 0/38) was
re-read as “never call Jev.” The skill names that failure (taxonomy #2;
hard rule 2: keep kills narrow). The files below are where the narrow
ruling and the over-read sit next to each other.

**Local evidence pack.** Folded here: pack **G2** from
`dont-give-up-evidence` (mined at `f8a8dc9`, re-read on `ad765b0`).
Pass 1 / G1 / G9 stay on PR #9. Pack G3–G8 / G10 and Passes 3–8 are
**not** started.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does
not retract the tool_call kill — that kill is still the right narrow
ruling. It does not promote review / rerank / failure / observer. It
does not start Pass 3.

### Required contrast (pack G2)

The kill, scoped:

`docs/INTEGRATIONS.md:18`:

> ## RULE WINS: four regexes, no Jev call — drop Jev from `tool_call`

`docs/INTEGRATIONS.md:39-41`:

> **Jev was not bad** — 11/12 is strong in isolation. This is a
> cost-benefit kill, not a capability kill. Ship the classifier; drop
> Jev from this surface.

The sibling that still calls Jev — the paragraph agents skip:

`work/omp-jev-review/README.md:11-18`:

> ## Why this one calls Jev and our other two do not
>
> `omp-jev-harm` and `omp-jev-preaction` contain no model call, because
> on those surfaces four regexes beat live Jev on a held-out split
> (12/12 vs 11/12, FP 0/38). That was a cost-benefit ruling about
> **one surface**, not a ban on the model.
>
> Review judgement is the opposite case. There is no regex for *this
> refactor silently changed a default*. A judge earns its seat exactly
> where a rule cannot be written.

The call site is not a comment. `work/omp-jev-review/src/index.ts:6-7`
repeats the one-surface rule; `:20` and `:66-70` import `askJev` and
POST the three review questions. That is the still-calls-Jev-elsewhere
column of the narrow-kill card.

### Search receipt

Required surfaces, exact commands, 2026-09-19 on `ad765b0`. Empty
results are listed, not inferred.

```bash
# The kill, as written
rg -n 'RULE WINS|drop Jev|no Jev call|cost-benefit|this surface|ban on the model' \
  docs/INTEGRATIONS.md
# HIT: :18 drop Jev from `tool_call`
# HIT: :21 Five surfaces, five cheap wins (cost-benefit, not capability)
# HIT: :39-41 Jev was not bad; cost-benefit kill, not capability; drop Jev from this surface
# HIT: :203 judge belongs only where regex cannot; then only cites the drop
# HIT: :209 scoreboard row: tool_call / harm-rule · no Jev call

# The sibling that still calls Jev
rg -n 'cost-benefit|one surface|ban on the model|asks Jev|askJev' \
  work/omp-jev-review/README.md work/omp-jev-review/src/index.ts
# HIT: README.md:11-18 one surface, not a ban
# HIT: src/index.ts:6-7 ONE SURFACE, not a ban on the model
# HIT: src/index.ts:20,66 askJev(...)

# Scoreboard leak (surface dropped)
rg -n 'RULE WINS|drop Jev|no Jev call|calls Jev|Five surfaces|FOUR REGEXES' README.md
# HIT: :9 FOUR REGEXES WITH NO JEV CALL IN THEM
# HIT: :10 Five surfaces, five cheap wins
# HIT: :24 drop Jev from `tool_call`          ← scoped (correct)
# HIT: :107 RULE WINS — ship the classifier, drop Jev   ← surface dropped
# HIT: :253-260 six-extension table: 4 of 6 still call Jev

# Other still-call / correctly-narrow siblings
rg -n 'askJev|Never calls Jev|measurement killed|this arm' \
  work/omp-jev-rerank/src/index.ts work/omp-jev-rerank/README.md \
  work/omp-jev-failure/src/index.ts work/omp-jev-preaction/src/index.ts
# HIT: rerank README.md:13 One question, because measurement killed the other two
# HIT: rerank src/index.ts:22,94 askJev; :96 ONE question
# HIT: failure src/index.ts:8,47 askJev
# HIT: preaction src/index.ts:4 Never calls Jev on this arm

# Receipt the kill cites
rg -n 'drop Jev|RULE WINS|this surface' \
  docs/demos/upstream-repro/toolcall-headtohead-20260919.md
# HIT: :1, :39, :41 drop Jev from this surface

# INTEGRATIONS names the still-call packages?
rg -n 'omp-jev-review|omp-jev-rerank|omp-jev-failure' docs/INTEGRATIONS.md
# EMPTY — the user-facing scoreboard has no row for any still-calling extension
```

Empty on `omp-jev-review|omp-jev-rerank|omp-jev-failure` inside
`docs/INTEGRATIONS.md` is the over-read in one line: the page that
opens with RULE WINS does not list the surfaces that still pay.

---

### G2 — RULE WINS on `tool_call` over-learned as “never call Jev”

Pack G2. Taxonomy #2 (over-learned kill).

**(a) Evidence.**

The kill is already narrow in the receipt it cites.
`docs/demos/upstream-repro/toolcall-headtohead-20260919.md:1,39-41`:

> # Head-to-head on held-out real traffic: RULE WINS, drop Jev from this surface
>
> ## Verdict: RULE WINS
>
> Ship pane 2's classifier, drop Jev from this surface. The judge is
> unnecessary where the harm is expressible

`docs/INTEGRATIONS.md:18,39-41` copies that scope (`tool_call` / *this
surface*) and names the cheaper substitute (four regexes, recall 12/12,
FP 0/38 on the committed corpus).

The over-read is what happens when that sentence leaves the receipt.
`README.md:107`:

> **RULE WINS** — ship the classifier, drop Jev (cost-benefit).

The surface token is gone. An agent who reads the scoreboard present-tense
and not the review README will treat “drop Jev” as fleet policy.

The counter-example is already in-tree and already written for this
failure: `work/omp-jev-review/README.md:11-18` (quoted above) plus the
live call at `work/omp-jev-review/src/index.ts:66-70`. Pack G2’s
one-line diagnosis is exact: *“counter-example that agents skip.”*

**(b) Why this is over-learned-kill.**

Skill failure mode 2: a cheap rule wins on *one* gate → “never call the
model / never try the hard path” everywhere. Hard rule 2: a cost-benefit
kill applies to *that gate* only. Checklist item 2 asks whether the
kill has a named cheaper substitute for *this* gate only.

The tool_call kill has all three: named surface, named substitute,
named receipt. The over-learn is dropping the surface when the sentence
is reused. “Jev was not bad” (`INTEGRATIONS.md:40`) is in the same
paragraph as the kill; the over-read throws that sentence away.

**(c) Forward move.**

Fill a **narrow-kill card** before any “drop Jev / no model call /
never call” sentence. Columns: `surface`, `cheaper substitute`,
`still-calls-Jev-elsewhere`, `proof receipt`. Ban “never call the
model” without a surface name. The card for *this* kill:

| surface | cheaper substitute | still-calls-Jev-elsewhere | proof receipt |
|---|---|---|---|
| `tool_call` / `omp-harm-rule` | four regexes; recall 12/12, FP 0/38 | `omp-jev-review` `askJev` (`src/index.ts:66`); `omp-jev-rerank` (`src/index.ts:94`); `omp-jev-failure` (`src/index.ts:8`); `omp-jev-observer` (`observer.mjs:45-46,63-65`) | `toolcall-headtohead-20260919.md:39-41`; `INTEGRATIONS.md:18,39-41`; review `README.md:11-18` |

Do not start a fleet rewrite in this PR. The next product tick the
over-read blocked is one live `review_scored` / `rerank_scored` /
`failure_scored` row — not another “drop Jev” headline.

---

### Additional over-learned-kill findings (same pass)

These are the same failure mode as G2: a named-surface kill reused
without its surface, or a scoreboard that only prints the no-call
row. They are not invented-policy (Pass 1), named-hole-then-park
(Pass 4), or paperwork-as-progress (Pass 6).

#### Scoreboard that lists only the kill

`docs/INTEGRATIONS.md` is “the user-facing scoreboard for what we have
actually wired into OMP” (`:1-3`). Its table (`:207-213`) has five
rows. One of them is the kill (`:209`, “four regexes, **no Jev call**”).
Zero of them name `omp-jev-review`, `omp-jev-rerank`, or
`omp-jev-failure`. `rg` on those three strings against the file is
empty (search receipt above).

The same tip’s README already has the missing rows
(`README.md:253-260`): observer / review / rerank / failure each
**yes** under `calls Jev?`. Review’s cell is the one-surface rule in
table form: *yes — no regex for "this refactor changed a default"*.

<!-- from PR #11 (Pass 3) -->
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

<!-- from PR #12 (Pass 4) -->
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

## Pass 3 — Named hole then park (stub)

Pass 3 is **not merged** on this tip. The named-hole-then-park audit (pack
**G3** / **G4**: `JEV_OBSERVER_ENDPOINT` logged then left OPEN; Infisical
“run init” misread as missing secret) lives on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`cursor/named-hole-then-park-c4a2`). Do not re-litigate it here.
This file’s first full section is Pass 4.

---

## Pass 4 — Selector and dig-skip

**Claim.** Agents claimed absence — “no `command`”, “0 rows with real
probabilities”, “extension sees nothing” — from a selector narrower than
the claim, or they asked how to author an omp extension instead of
opening the official page. The skill already names both failures
(taxonomy #4 / #5; checklist “selector ≡ claim”; playbook E line 119
and K “Extension loads, zero rows”). The files below are where the
selector was wrong, the official dig was skipped, and a mechanical
fix already existed in-tree.

**Local evidence pack.** Folded here: pack **G6** (wrong-selector 8–10×;
`requireKey`; `TESTS.md` `readRow` dual shapes) and pack **G5** (skipped
https://omp.sh/docs/extension-authoring; silent `pi.on` / 0-row;
INTEGRATIONS loader globs). Pass 1 / G1 / G9 stay on PR #9. Pass 2 / G2
stays on PR #10. Pass 3 / G3 / G4 stays on PR #11. Pack G7 / G8 / G10
and Passes 5–8 are **not** started.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It does
not start Pass 5. It does not add a planted-negative gate that fails
when someone claims absence without `keys()`. It does not register or
reload an omp extension.

### Required quotes (pack G6 + G5)

The eighth wrong-selector, published, then retracted — the field was on
the row the whole time:

`NEGATIVE_EVIDENCE.md:1423-1428` (R33-CORRECTION):

> The `harm-rule.decision.v1` rows carry a `command` field and always did.
> Verified by dumping the row's own keys — the step I skipped:
>
> ```
> keys: [command, error, kind, model, probabilities, score, timestamp, toolCallId]
> ```

`NEGATIVE_EVIDENCE.md:1448-1458`:

> **This is the eighth wrong-selector failure today and the most damaging**,
> because unlike the others it reached a published receipt and impugned a
> correct artifact built by a pane that had already done the right thing.
>
> **The rule R33 tried to state survives, corrected:** a shipped artifact
> must name the input it acted on — and **before concluding it cannot,
> dump the record's own keys.** Absence proved by a failed join is not
> absence. That is the same lesson as `.distribution` vs `.probabilities`,
> `.probability` vs `.noul`, and the spaced `"role": "toolResult"` grep:
> **a selector that returns nothing is indistinguishable from a thing that
> is not there.** I have now made this error eight times in one session
> and published it once.

The ninth and tenth, hours later, after `requireKey` existed:

`NEGATIVE_EVIDENCE.md:1747-1758` (R41):

> Jev reported a live Jev call in the observer. I scanned for it, found
> **"0 rows with real probabilities"**, and was about to treat a correct
> claim as unsupported. The payload sits at **`customType.data`**, not
> top-level `data`; my scan read `{}`. The row is real:
> `flag 0.04 / pass 0.96`, `error: null`, `378ms`.
>
> That is the **ninth** wrong-selector failure of this session. The
> `requireKey` commit predicted its shape precisely: *"a helper cannot
> force anyone to call it… the ninth instance will come from code that
> never imported `requireKey`."* It came within hours, in the author's
> own hands.
>
> A **tenth** followed immediately: my live kind counter returned 16 rows
> it could not classify — same nested shape.

The mechanical fix, written after the eighth, and the dual-shape reader
that names R33/R41 as its reason:

`TESTS.md:28-31`:

> Plus **R33's mechanical fix**: `requireKey` refuses to let absence be
> claimed without the record's own key list in the error, and `inspectKey`
> returns that list alongside the lookup — written after the eighth
> wrong-selector failure in one session, the only one that reached a
> published receipt.

`TESTS.md:46` (`readRow` dual shapes; pack cited `:45` at `f8a8dc9`;
on this tip the same sentence is `:46` because preaction landed):

> Also `readRow`, which handles BOTH omp session row shapes (`customType`
> as an object with nested `data`, and `customType` as a string with
> top-level `data`) — a reader that handles one silently reports "no rows"
> on the other, which is the root cause of R33 and R41.

`work/oracle-kit/index.mjs:116-123` (`requireKey`):

```js
export function requireKey(record, key, who = 'record') {
  if (record === null || typeof record !== 'object') {
    throw new Error(`${who}: not an object (${typeof record}); cannot claim '${key}' is absent`);
  }
  if (!(key in record)) {
    throw new Error(`${who}: no '${key}'. Keys present: [${Object.keys(record).sort().join(', ')}]`);
  }
  return record[key];
}
```

`work/jev-client/src/index.ts:127-132` (`readRow` comment):

> omp session rows come in TWO shapes and this has now cost the lane four
> wrong scans:
>   A) `{ customType: { type: "…decision.v1", data: {…} } }` — observer rows
>   B) `{ customType: "…decision.v1", data: {…} }` — harm-rule / failure rows
> A scanner written against one returns silently empty on the other, which
> reads as "no rows" and has twice led me to contradict a peer who was
> right (NEGATIVE_EVIDENCE R33, R41).

The missed official extension-authoring dig — silent `pi.on` / 0-row,
discovered live, not from the docs page:

`docs/INTEGRATIONS.md:56-59`:

> **Silent-register rule.** A module with valid syntax and no `pi.on`
> registers nothing. `node --check` passes it. A hook that fails to
> register is indistinguishable from a hook that sees nothing
> (`harm-rule-shipped-20260919.md`). The co-presence bar is observer
> decisions next to a bridge row in the same session.

`docs/INTEGRATIONS.md:167-172`:

> An earlier version of this section reported *0 observer rows against 1
> bridge row*. That was true when written and is now stale; the zero-row
> cause was a module with valid syntax whose `pi.on` registration line
> was absent — reproduced deliberately and repaired
> (`harm-rule-shipped-20260919.md`, `658922f`). **A hook that fails to
> register is indistinguishable from a hook that sees nothing.** The
> loader globs `*.{ts,js}`; the config is an `extensions:` list in the
> profile `agent/config.yml`.

`docs/INTEGRATIONS.md:192`:

> **The loader must actually load it.** Globs `*.{ts,js}`. Config is
> `extensions:` in the profile `agent/config.yml`. A register that writes
> 0 rows while another extension writes rows is not loaded — verify
> against a known-firing neighbour, never against silence alone.

`docs/demos/upstream-repro/harm-rule-shipped-20260919.md:71-74`:

> Causal bonus: my own extension reproduced the silent-zero-row defect
> (a lost `pi.on` line during editing = syntactically valid module that
> registers nothing; node --check passes it). Diagnosed via tsx import
> probe, repaired, re-proven live. Silent non-firing modules are now
> demonstrated twice.

The official page this lane did not open first
(https://omp.sh/docs/extension-authoring): default export is
`export default function (pi: ExtensionAPI)`, subscribe with
`pi.on(...)`, package manifest is `omp.extensions` (legacy
`pi.extensions` still accepted), install via
`omp plugin install` / `omp --extension <path>`. Automatic scanning of
native/configured extension directories is limited to `.ts` and `.js`
— the same glob INTEGRATIONS discovered by a 0-row defect.

In-tree ship shape that already matches that page
(`work/omp-harm-rule/harm-rule.ts:27-32`;
`work/omp-jev-observer/src/observer.mjs:50-53`):

```ts
export default function harmRule(pi, deps = {}) {
  pi.on('tool_call', async (event, ctx) => { /* … */ });
}
export default function ompJevObserver(pi) {
  pi.on('tool_call', async (event, context = {}) => { /* … */ });
}
```

### Search receipt

<!-- from PR #13 (Pass 5) -->
## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack
**G1** / **G9**: STOP-LIVE, quiet-window, DEFER, “off the table”,
invented human-gate on lab registration) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.

## Pass 2 — Over-learned kill (stub)

Pass 2 is **not merged** on this tip. The over-learned-kill audit (pack
**G2**: RULE WINS on `tool_call` re-read as “never call Jev”) lives on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`cursor/dont-give-up-over-learned-kill-edb3`). Do not re-litigate it here.

## Pass 3 — Named hole then park (stub)

Pass 3 is **not merged** on this tip. The named-hole-then-park audit
(pack **G3** / **G4**: `JEV_OBSERVER_ENDPOINT` logged then left OPEN;
Infisical “run init” misread as missing secret) lives on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`cursor/named-hole-then-park-c4a2`). Do not re-litigate it here.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 is **not merged** on this tip. The selector-and-dig-skip audit
(pack **G6** / **G5**: 8–10× wrong-selector; skipped
https://omp.sh/docs/extension-authoring) lives on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12)
(`cursor/selector-and-dig-skip-364d`). Do not re-litigate it here.
This file’s first full section is Pass 5.

---

## Pass 5 — Paperwork and live proof

**Claim.** Agents scored Charter / plan / receipt / ledger churn as
work, closed units on offline green plus a deliberately UNRUN
registration, and stored a default that looks measured. The skill
already names all three (taxonomy #6 / #7; hard rule #6 “prove one
live row”; hard rule #8 “product ticks only”; playbook F/K). The
files below are where `?? 'unknown'` minted 27 fake rows, where
PROCESS 17 / `shipped:NONE` made instruments the work, and where
offline 5/5 plus an UNRUN close left working-dogfood OPEN and
`promoted: 0`.

**Local evidence pack.** Folded here: pack **G7** (`dcgVerdict ??
'unknown'` — 27 fake rows; NEGATIVE_EVIDENCE R38; omit absent
fields), pack **G8** (`tick.md` PROCESS 17 / `shipped:NONE` —
paperwork as progress), and pack **G10** (offline green ≠ one live
row; working-dogfood OPEN; `promoted: 0`). Pass 1 / G1 / G9 stay on
PR #9. Pass 2 / G2 stays on PR #10. Pass 3 / G3 / G4 stays on PR
#11. Pass 4 / G5 / G6 stays on PR #12. Passes 6–8 and the Jeffrey
essay are **not** started.

**NO-CLAIM.** This pass does not write the Jeffrey-voice essay. It
does not start Pass 6. It does not edit `observer.mjs`, README, or
INTEGRATIONS. It does not inject a key or register onto `jev-lab` /
a working profile. It does not close working-dogfood. This PR is
itself an essay — a product tick it names, not one it ships.

### Required quotes (pack G7 + G8 + G10)

R38 — the default that minted 27 live rows and looked measured:

`NEGATIVE_EVIDENCE.md:1600-1619` (R38):

> ## R38 — the `?? 'unknown'` sentinel: a field that is always present and sometimes real
>
> Two defaults in `work/omp-jev-observer/src/observer.mjs` filled absent data with the string
> `'unknown'`:
>
> ```js
> dcg: options.dcg ?? (async (_e, context) => context.dcgVerdict ?? 'unknown')   // gate path
> sessionId: context?.sessionId ?? 'unknown'                                     // STORED
> ```
>
> The first produced **27 live rows** reading `dcgVerdict: "unknown"` — every one a default, none
> an observation, because the event exposes `[type, toolName, toolCallId, input]` and **no
> verdict**. The second landed in *every* record.
>
> **Why this is worse than a missing field:** a field that is always present and sometimes real
> cannot be filtered, counted, or trusted, and it **survives inspection**. Nothing downstream can
> distinguish "we observed unknown" from "we had nothing". An absent field announces itself; a
> defaulted one lies quietly and looks measured.

`NEGATIVE_EVIDENCE.md:1638-1643`:

> **Rule:** never default an absent observation to a plausible-looking value. Omit the field, or
> use something a reader cannot mistake for data. `'unknown'` is not a value — it is a confession
> formatted as one.
>
> **Retry condition:** grep the tree for `?? 'unknown'` after any observer change. A third
> instance means the rule needs a mechanical check, not another entry.

Honesty tally that counted those 27 rows as published fiction:

`.flywheel/feedback/2026-09-19-honesty-pass-3.md:27`:

> | `dcgVerdict: "unknown"` ×27 | every one a default, never an observation (`d8472cc`, R38) |

The 27 defaulted rows are still on the INTEGRATIONS scoreboard as
legacy counts, next to the one honest absence:

`docs/INTEGRATIONS.md:131-134`:

> | `com.zeststream.omp-jev-observer.decision.v1` | **28** |
> | ├ with a nonempty `toolCallId` | **1** |
> | ├ `dcgVerdict: "unknown"` (defaulted, legacy) | **27** |
> | └ `dcgVerdict` absent (correct, post-`a2e2035`) | **1** |

Ceremony scored as work — USER 0 / PROCESS 17, then
`shipped:NONE` as the stop:

`docs/demos/tick.md:7-11`:

> Rewritten 2026-09-18 after a filled `/just-say-no-to-process-porn-and-ceremony` audit of the
> previous 22 commits returned **USER 0 · ENABLER 5 · PROCESS 17**, verdict **DRIFTING**. The tick it
> replaces opened with four screens of bookkeeping mechanics, so the conductor's first thought every
> 20 minutes was *check the instruments*, and the instruments became the work. Mechanics are still
> here. They are no longer first.

`docs/demos/tick.md:13-25`:

> ## 0. THE ONLY QUESTION THAT OPENS A TICK
>
> **What shipped since the last tick that a person outside this lane could use?**
>
> Answer in one line, from artifacts, before any other prose:
>
> ```
> MOVED <HH:MMZ> shipped:<what a non-lane reader can install/run/read, or NONE> · promoted N · ruled N
> ```
>
> **`shipped:NONE` twice in a row is a stop condition, not a status.** On the second consecutive
> NONE, you may not dispatch another audit, ruling, ledger row, or instrument. Dispatch the smallest
> thing a non-lane reader can consume, or send Joshua one line saying why nothing can ship.

Offline green, then a deliberately UNRUN registration, then
working-dogfood left OPEN and promoted 0:

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:26-43`:

> ## Offline proof
>
> ```text
> node --test work/omp-jev-observer/test/observer.test.mjs
> 5 tests passed
> ```
>
> …
>
> ## Registration command — deliberately UNRUN
>
> ```bash
> cp work/omp-jev-observer/src/observer.mjs ~/.omp/omp-extensions/omp-jev-observer.mjs
> ```
>
> This command was not run. No file under `~/.omp` was modified by this unit. Registration requires
> human review because an extension load or hook error can affect every tool call in the fleet.

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:45-49`:

> ## NO-CLAIM AT P2-13 CLOSE
>
> At the P2-13 close this extension had not been registered and had captured no live traffic.

The later P2-15 lab fire produced JSONL *error* rows, not a quoted
`ok` / scores / latency / `error=null` live Jev row:

`docs/demos/upstream-repro/omp-jev-observer-20260919.md:64-68`:

> /Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T18-34-35-060Z_01a0baf2-e2b4-75dc-85ca-2dbac80a5889.jsonl
>   com.zeststream.omp-jev-observer.diagnostic.v1
>   com.zeststream.omp-jev-observer.decision.v1
>   error: Error: JEV_OBSERVER_ENDPOINT is not configured

`docs/INTEGRATIONS.md:161-165`:

> - **(C) Working profile — STILL OPEN, not claimed.** Everything above is `jev-lab`, a disposable
>   profile. No multi-row live logger exists on a working profile. This is not continuous or
>   production dogfood. **Promoted: 0.**

`docs/INTEGRATIONS.md:197-199`:

> The remaining condition for calling the observer **working** is a **working profile under
> real traffic**, which has not been attempted: no multi-row live logger exists outside `jev-lab`,
> and **promoted is 0**.

`docs/INTEGRATIONS.md:212` (scoreboard row):

> working-profile dogfood **OPEN**; lab only. First-contact harm-rule receipt does not close this row | no

`docs/INTEGRATIONS.md:5`:

> **0 promoted.** Re-derive from `docs/demos/STATUS.tsv` … No row in that file is `PROMOTED`.

`README.md:61-65` (offline-green-is-not-proof, same class):

> **22 Jev repos appeared in launch week. We ran all of them; everything passed, and that proved

<!-- from PR #14 (Pass 6) -->
## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack
**G1** / **G9**) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.

## Pass 2 — Over-learned kill (stub)

Pass 2 is **not merged** on this tip. The over-learned-kill audit (pack
**G2**) lives on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`cursor/dont-give-up-over-learned-kill-edb3`). Do not re-litigate it here.

## Pass 3 — Named hole then park (stub)

Pass 3 is **not merged** on this tip. The named-hole-then-park audit
(pack **G3** / **G4**: Infisical `--projectId=` vs `<id>`) lives on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`cursor/named-hole-then-park-c4a2`). Pass 6 **re-uses** that projectId
in the ready-to-paste D/K replacements; it does not re-open G3/G4.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 is **not merged** on this tip. The selector-and-dig-skip audit
(pack **G6** / **G5**: `requireKey` / `readRow`;
https://omp.sh/docs/extension-authoring) lives on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12)
(`cursor/selector-and-dig-skip-364d`). Pass 6 **folds** those into the
ready-to-paste E/K/checklist replacements so one paste applies the house
skill; it does not re-open G5/G6.

## Pass 5 — Paperwork and live proof (stub)

Pass 5 is **not merged** on this tip. The paperwork / invented-observation
/ live-proof audit (pack **G7** / **G8** / **G10**) lives on
[PR #13](https://github.com/JYeswak/jev_playground/pull/13)
(`cursor/paperwork-and-live-proof-92c2`). Do not re-litigate it here.

---

## Pass 6 — Tool playbook holes

**Claim.** The attached house skill names `cass`, `fh`, arsenal, `dcg`,
`jsm`, Infisical, omp extension-authoring, and `requireKey`/`readRow`
discipline — then shows **generic** commands (`--workspace <project>`,
`--projectId=<id>`, `e.g. …/docs/extension-authoring`, “selector ≡
claim”). This repo already has the real commands and the real failure
modes. Agents who follow the skill as written re-discover unlinked
Infisical, skip the official omp page, and treat `fh doctor` STALE or a
missing binary as “tool unusable.”

**Local evidence pack.** Folded here: the pack’s **missed digs** table
(omp.sh/docs/extension-authoring; Infisical `--projectId=`) plus the
skill-loop mission “cass/fh/arsenal/dcg/jsm sections that lack worked
*lane* examples or fail when STALE/unlinked.” Passes 1–5 stay on PRs
#9–#13. Passes 7–8 and the Jeffrey-voice essay are **not** started.

**NO-CLAIM.** This pass does not apply the patches to any JSM-owned
skill copy. It does not rewrite `README.md:696` or
`scripts/jev-probe.mjs:38` (named as next product ticks). It does not
install `cass`/`fh`/`dcg`/`jsm`/`infisical`/`omp` on this VM. It does
not run a live Jev call.

### Five required answers (re-read on `e65a614`)

| Question | Answer on this tip |
|---|---|
| Which tools are named but never shown with a `jev_playground` worked example? | **A `cass`**, **B `fh suggest`**, **C arsenal**, **F `dcg explain`/`dcg test`**, **I `jsm search`**, **L `fh scaffold`**. Skill A–C / F / I / L are generic CLI shapes. Lane receipts for the *same hole class* exist and are cited in the gap table. |
| `fh suggest` STALE ≠ unusable — is that in the skill with a lane citation? | **In the skill, yes (comment only). Lane citation: no.** Skill B line: `fh suggest "…"          # STALE ≠ unusable — still steal the row`. Zero file:line. The lane citation is `docs/INTEGRATIONS.md:11-16`. |
| Infisical `projectId` still shown as `<id>` anywhere in skill vs `.env.example`? | **Skill: yes (`--projectId=<id>` twice in D). `.env.example`: no.** `.env.example:11,15` is `42b194c3-89d7-4ebb-895f-dd77ddf005ba`. Leftover `<id>` still teaching the park: `README.md:696`, `scripts/jev-probe.mjs:38` (same file’s `:6` has the real id). |
| `omp.sh/docs/extension-authoring` — skill says “e.g.” but not the real URL in a copy-paste block? | **Yes.** Skill E: `Official docs (e.g. product …/docs/extension-authoring)`. Ellipsis, not `https://omp.sh/docs/extension-authoring`. `rg -n 'extension-authoring' --glob '!docs/essays/**'` on `e65a614` is **empty**. |
| `requireKey` / `readRow` — skill checklist vs oracle-kit? | **Checklist is a reminder; the kit is mechanical.** Skill: “Did I verify selector ≡ claim …?” `work/oracle-kit/index.mjs:116-123` `requireKey` throws `Keys present: […]`. `work/jev-client/src/index.ts:136-159` `readRow` accepts both omp shapes. `TESTS.md:28-31,47`. |

### Gap table

Skill section → missing worked example → proposed patch with **real**
commands/paths from this repo. Apply the paste in
`docs/essays/dont-give-up-skill-patches.md` Pass 6.

| Skill section | What the skill shows | Missing worked *lane* example | Proposed patch (this repo) |
|---|---|---|---|
| **A cass** | `cass status --json`; `cass search "KEYWORD" --workspace <project> --json --fields minimal` | No `--robot`. Placeholder `--workspace <project>`. No query this repo already publishes. Bare `cass` is a TUI (`AGENTS.md:1407`). | `cass health` then `cass search "jev typed questions" --robot --limit 5` (`AGENTS.md:1410-1411`). Stage-0 already has `cass search "jev" --robot --limit 10` (`AGENTS.md:890`). Never invent `--workspace <project>`. Off `PATH` → steal from `AGENTS.md`, do not report “cass missing.” |
| **B fh** | `fh suggest "…"` + comment `STALE ≠ unusable` with **no citation** | Comment is doctrine without a receipt. Agents read STALE / `ORACLE_DOMAIN_UNKNOWN` / binary-absent as unusable. | Keep the comment. Cite `docs/INTEGRATIONS.md:11-16`: `fh doctor` may report STALE; **fh ranked, we opened** (`asupersync` `eprocess.rs:224-238`, `franken_ocr` `RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch` `perf_ratchet.rs:732-740`). Worked miss that is still usable: `fh oracles --domain jev` → rc=4 `ORACLE_DOMAIN_UNKNOWN` (`docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14`) — absence evidence, not a reason to invent a local `oracles.tsv`. Also `fh agents --repo .` (`EVAL.md:165`; `.fh-agents.toml`). Lane hole string: `fh suggest "wire a typed Jev asker into an omp tool_call hook"`. |
| **C arsenal** | “WHEN YOU NEED X, USE Y (charter / frankensuite-arsenal)” | `rg -n 'frankensuite-arsenal\|WHEN YOU NEED X' --glob '!docs/essays/**'` → **NONE**. Off-machine table. | In-tree “do not hand-roll” table: Jev POST → `work/jev-client` (`TESTS.md:47`); absence claim → `requireKey` (`work/oracle-kit/index.mjs:116`); omp session row → `readRow` (`work/jev-client/src/index.ts:136`); planted RED → `foundation/gates.d/` + `TESTS.md`. If the Franken arsenal is off-disk, these paths are the arsenal. |
| **D Infisical** | `--projectId=<id>` twice | Placeholder teaches the park `.env.example` was written to stop (`:1-8,27-31`). | Copy `.env.example:15`: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`. Presence: `printenv NAME \| wc -c` or `infisical secrets --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba \| grep -c TYPESAFE_API_KEY` (expect 1; `:34-35`). “run init” = **UNLINKED DIRECTORY**, not missing secret (`:27-31`). Client already embeds the fix (`work/jev-client/src/index.ts:46-54`). |
| **E docs / examples** | “e.g. product `…/docs/extension-authoring`” | Not a URL. Not a copy-paste block. `rg` for `extension-authoring` outside essays is empty. | Open **https://omp.sh/docs/extension-authoring**. Copy default-export + `pi.on` from `work/omp-harm-rule/harm-rule.ts:27-32` / `work/omp-jev-observer/src/observer.mjs:50-53`. Copy the `omp.extensions` manifest from `work/omp-jev-review/package.json:8-9` (observer’s `package.json` does not carry that key). Neighbour co-presence (`docs/INTEGRATIONS.md:167-172,192`). Isolated lab nonce is `echo observer-minimal-actual` (`omp-jev-observer-20260919.md:58`). |
| **F dcg** | `dcg explain "cmd"` / `dcg test "cmd"` | Those two verbs never appear in first-party prose. The lane receipt is a **denial**, not a help string. Frozen-corpus `dcg test` rows (`work/p3-calibration/toolcall-corpus-frozen.jsonl`) are **foreign sessions** (control-plane) — not a jev worked example (wrong-selector if cited as ours). | Worked lane row: `dcg` denied `git add -A` / `git add .` (`zeststream.shared_worktree:git-add-whole-tree`) — `AGENTS.md:249-250`, `EVAL.md:232-233`, `.flywheel/feedback/2026-09-17.md:17-18`. Safe alternative: `git add <path>...` then `git diff --cached --stat`. Do not ask for override first. CLI `dcg` (the blocker that fired on `git add -A`) is not the omp `dcg-guard` fail-open hook (`docs/INTEGRATIONS.md:88-90` is the hook’s fail-open cite, not the CLI). |
| **G ubs** | `ubs --staged` until exit 0 | Missing the empty-scan-set lie this lane already measured. | `ubs` on markdown-only → exit 3, **not a pass** (`NEGATIVE_EVIDENCE.md` R6 `:99-108`; receipt `docs/demos/duel-1/runs/ubs-r6-20260918T011614Z.json`). Worked TS scan: four compaction files, exit 1, critical was a name not a secret (`:110-121`). Docs-only change: do not cite `ubs` green. |
| **H bv / br** | generic `bv --robot-triage` / `br update` | Weakest hole. `AGENTS.md` already has the robot-only rule. | Keep robot flags. ACCEPTANCE = a live command (`AGENTS.md` beads). Not the Pass 6 ship. |
| **I jsm** | `jsm search "<hole keywords>"` | No first-party `jsm search` receipt. `INTEGRATIONS.md:191` “jsm preconditions” is **self-contained install**, a different tool. Frozen-corpus `jsm search` rows are omp-orchestrator sessions — not ours. | If `jsm` is on `PATH`: `jsm search "omp extension authoring"`. If off `PATH` (this VM): do not report “jsm missing.” Read `docs/INTEGRATIONS.md:191` (inlined builder after `9e6c88d` imported a parent path that does not exist under `~/.omp`) and copy `harm-rule.ts` / `observer.mjs`. House lessons stay in house skills (skill I already says this). |
| **J planning** | jeff-planning / duelling-idea-wizards | **Not a tool-playbook hole.** No CLI to go STALE/unlinked. | Out of scope. Do not invent a planning worked example to close the A–L table. |
| **K live proof** | mechanical holes; “selector says 0” = “broaden” | No `requireKey` / `readRow`. No official URL on the zero-row row. | Fold Pass 4 rows: two omp shapes + `readRow`; neighbour + https://omp.sh/docs/extension-authoring. Fold Pass 3 inject-or-HALT with the real projectId. Isolated lab command is the receipt nonce `echo observer-minimal-actual` (`omp-jev-observer-20260919.md:58`), not an invented prompt. Manifest shape is `work/omp-jev-review/package.json:8-9`. |
| **L planted-negative** | `fh scaffold` | `fh scaffold` never appears in this repo. | Lane equivalent: `foundation/gates.sh --selftest` (every stage proves RED) and the planted arms in `TESTS.md`. `fh scaffold` if present; otherwise extend `foundation/gates.d/` — do not invent a thirteenth wrapper. |

### Required quotes (STALE / unlinked / leftover `<id>` / official page / keys)

`fh doctor` STALE is still usable — rank, then open file:line:

```
docs/INTEGRATIONS.md:11-16
If this page mentions `fh`, it is as a *ranker*, not as a citation. `fh doctor` may report STALE
or degraded SCHEDULING (a 1/8 schedule-declaration miss does not retract shipped doctrine).
Corpus citations already in this repo were opened at file:line from the pinned Dicklesworthstone
mirror after `fh` ranked them — `asupersync` `eprocess.rs:224-238`, `franken_ocr`
`RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch`
`perf_ratchet.rs:732-740`. Pattern: **fh ranked, we opened.** A ranking alone is not a citation.
```

`fh` returning an error is still a finding (unusable catalogue ≠ unusable tool):

```
docs/upstream/franken-harvest-no-jev-oracle-domain.md:12-14
fh oracles --json                  rc=0, 18 domains
fh oracles --domain jev            rc=4  ORACLE_DOMAIN_UNKNOWN
fh oracles --domain system_one     rc=4  ORACLE_DOMAIN_UNKNOWN
```

Unlinked directory ≠ missing secret; real projectId already committed:

```
.env.example:11,15,27-31
WORKSPACE ID: 42b194c3-89d7-4ebb-895f-dd77ddf005ba
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <your command>
jev/ has no .infisical.json … "run infisical init…" means UNLINKED DIRECTORY, not MISSING SECRET.
```

Skill-shaped leftover `<id>` still in the tree (teaching the park):

```
README.md:696
infisical run --projectId=<id> --env=prod -- node scripts/jev-probe.mjs

scripts/jev-probe.mjs:6   (real id in the header)
scripts/jev-probe.mjs:38  (placeholder in the error the agent sees)
```

`requireKey` / `readRow` vs the skill’s “selector ≡ claim” checkbox:

```
work/oracle-kit/index.mjs:116-123
export function requireKey(record, key, who = 'record') {
  …
  throw new Error(`${who}: no '${key}'. Keys present: [${Object.keys(record).sort().join(', ')}]`);
}

work/jev-client/src/index.ts:127-136
 * omp session rows come in TWO shapes …
export function readRow(line: unknown): { type: string; data: Record<string, unknown> } | undefined {
```

dcg’s worked lane example is a denial with a named safe alternative:

```
AGENTS.md:249-250
NEVER `git add -A` / `git add .` — `dcg` denies it here
(`zeststream.shared_worktree:git-add-whole-tree`)

EVAL.md:232-233
`dcg` denied `git add -A` (`zeststream.shared_worktree:git-add-whole-tree`) on the first
attempt — correct in a worktree three agents share. Everything staged by explicit path since.
```

cass’s worked lane example is `--robot`, never `--workspace <project>`:

```
AGENTS.md:1407-1412
Never run bare `cass` (TUI). Always use `--robot` or `--json`.
cass health
cass search "jev typed questions" --robot --limit 5
cass view /path/to/session.jsonl -n 42 --json
```

### Search receipt (this pass, `e65a614`)

| Hunt | Result |
|---|---|
| `rg -n 'projectId=<id>' README.md scripts/jev-probe.mjs` | `README.md:696`, `scripts/jev-probe.mjs:38` |
| `rg -n '42b194c3-89d7-4ebb-895f-dd77ddf005ba' .env.example` | lines 11, 15, 19, 22, 34 |
| `rg -n 'extension-authoring' --glob '!docs/essays/**'` | **empty** |
| `rg -n 'fh doctor\|STALE' docs/INTEGRATIONS.md` | `:11` |
| `rg -n 'export function requireKey\|export function readRow'` | `oracle-kit/index.mjs:116`, `jev-client/src/index.ts:136` |
| `rg -n 'frankensuite-arsenal\|WHEN YOU NEED X' --glob '!docs/essays/**'` | **empty** |
| `rg -n 'jsm search' --glob '!docs/essays/**'` | frozen-corpus foreign rows only |
| `rg -n 'dcg explain\|dcg test' --glob '!docs/essays/**'` | frozen-corpus foreign rows only |
| `rg -n 'cass search' AGENTS.md` | `:890`, `:982`, `:1411` (`--robot`) |
| `command -v cass fh dcg jsm infisical omp` | **ABSENT** (this VM) |

Offline suites this pass leans on (fresh this turn):

```
node work/oracle-kit/test.mjs
→ oracle-kit: 13/13 checks passed
  (includes requireKey names every key present when the field is absent)

node --experimental-strip-types --test work/jev-client/test/client.test.mjs
→ 9/9 pass
  (includes readRow handles BOTH omp row shapes)
```


<!-- from PR #15 (Pass 7) -->
## Pass 1 — Invented policy (stub)

Pass 1 is **not merged** on this tip. The invented-policy audit (pack
**G1** / **G9**) lives on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`cursor/dont-give-up-invented-policy-f56e`). Do not re-litigate it here.

## Pass 2 — Over-learned kill (stub)

Pass 2 is **not merged** on this tip. The over-learned-kill audit (pack
**G2**) lives on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`cursor/dont-give-up-over-learned-kill-edb3`). Do not re-litigate it here.

## Pass 3 — Named hole then park (stub)

Pass 3 is **not merged** on this tip. The named-hole-then-park audit
(pack **G3** / **G4**) lives on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`cursor/named-hole-then-park-c4a2`). Do not re-litigate it here.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 is **not merged** on this tip. The selector-and-dig-skip audit
(pack **G6** / **G5**) lives on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12)
(`cursor/selector-and-dig-skip-364d`). Do not re-litigate it here.

## Pass 5 — Paperwork and live proof (stub)

Pass 5 is **not merged** on this tip. The paperwork / invented-observation
/ live-proof audit (pack **G7** / **G8** / **G10**) lives on
[PR #13](https://github.com/JYeswak/jev_playground/pull/13)
(`cursor/paperwork-and-live-proof-92c2`). Do not re-litigate it here.

## Pass 6 — Tool playbook holes (stub)

Pass 6 is **not merged** on this tip. The tool-playbook-holes audit
(playbook A–L; cass / fh / arsenal / dcg / jsm / Infisical / official
extension-authoring URL) lives on
[PR #14](https://github.com/JYeswak/jev_playground/pull/14)
(`cursor/tool-playbook-holes-3858`). Ready-to-paste house-skill
replacements: `docs/essays/dont-give-up-skill-patches.md` on that PR.
Do not re-litigate it here. **Apply those patches; do not start Pass 7
again.**

---

## Pass 7–8 — Essay

The synthesis essay is [`docs/essays/dont-give-up.md`](dont-give-up.md).
Title: **The Ban Nobody Issued**. Voice: first-person, concrete war story
(STOP-LIVE / invented bans), chef / overprompting analogy, plan-loose /
execute-precise, honest NO-CLAIM.

It folds G1–G10 and Passes 1–6 into one readable piece with a compact
evidence table (Gap | Evidence path | Forward move) and links to
[PR #9](https://github.com/JYeswak/jev_playground/pull/9) through
[PR #14](https://github.com/JYeswak/jev_playground/pull/14). The
stealable rule: **quote the stop, or write `none`; then run the next
command that is already in the tree.**

**NO-CLAIM.** This pass does not apply the Pass 6 skill patches. It does
not rewrite leftover `--projectId=<id>` teachers. It does not inject a
key, register an extension, or move `promoted`. It does not start another
pass. The skill is unfinished until someone pastes Pass 6.

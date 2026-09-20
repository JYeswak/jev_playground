# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure modes 6 and 7 plus invented
observation: **paperwork as progress**, **blocked-on-human detour**,
and **live-proof gap** / invented `?? 'unknown'`).
Pass date: 2026-09-20. Lane: offline file search + quote verification on
`7f28d54`. No live Jev calls. No secret values printed. Infisical CLI
and `omp` are **not** on `PATH` here — the live JSONL quote is
**NOT_RUN**; the next inject+lab command is written, not executed.

The local evidence pack's "Suggested feed" mapped G7+G8+G10 to Pass 6.
This packet assigned them to **Pass 5** after selector-and-dig-skip
landed as Pass 4
([PR #12](https://github.com/JYeswak/jev_playground/pull/12)).
Do not re-number; the prior PRs already occupy 1–4.

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
> nothing.** Substituting a well-formed RANDOM judge left 254 of 305 tests green (83%)
> … A suite that
> passes a coin flip is plumbing, not validation.

### Search receipt

Required surfaces, exact commands, 2026-09-20 on `7f28d54`. Empty
results are listed, not inferred.

```bash
# G7 — R38 invented observation
rg -n "R38 — the|\?\? 'unknown'|27 live rows|dcgVerdict: .unknown" \
  NEGATIVE_EVIDENCE.md README.md GATES.md docs/INTEGRATIONS.md \
  .flywheel/feedback/2026-09-19-honesty-pass-3.md \
  work/omp-jev-observer/src/observer.mjs
# HIT: NEGATIVE_EVIDENCE.md:1600  R38 — the ?? 'unknown' sentinel
# HIT: NEGATIVE_EVIDENCE.md:1608  context.dcgVerdict ?? 'unknown'   // gate path
# HIT: NEGATIVE_EVIDENCE.md:1612  27 live rows reading dcgVerdict: "unknown"
# HIT: .flywheel/feedback/2026-09-19-honesty-pass-3.md:27  ×27 default, never observation
# HIT: docs/INTEGRATIONS.md:133  dcgVerdict: "unknown" (defaulted, legacy) | 27
# HIT: README.md:57,92  residual prose still names ?? 'unknown'
# HIT: docs/INTEGRATIONS.md:64,156  residual prose still names ?? 'unknown'
# HIT: GATES.md:163  names the default as dropped by a2e2035
# EMPTY: work/omp-jev-observer/src/observer.mjs  — no 'unknown' on this tip

rg -n "unknown" work/omp-jev-observer/src/observer.mjs
# EMPTY on 7f28d54. Code already omits. Residual is prose.

# G8 — paperwork as progress
rg -n 'PROCESS 17|shipped:NONE|instruments became the work' docs/demos/tick.md
# HIT: docs/demos/tick.md:8   USER 0 · ENABLER 5 · PROCESS 17, verdict DRIFTING
# HIT: docs/demos/tick.md:10  instruments became the work
# HIT: docs/demos/tick.md:23  shipped:NONE twice in a row is a stop condition

rg -n 'kill by paperwork|kill-by-paperwork' docs/demos/PLAN.md
# HIT: docs/demos/PLAN.md:1794  a kill by paperwork
# HIT: docs/demos/PLAN.md:1980  an unverifiable condition used as a gate is a kill by paperwork
# HIT: docs/demos/PLAN.md:2477  UNASKABLE cannot block a rung indefinitely — kill-by-paperwork

# G10 — offline then UNRUN / OPEN / promoted 0
rg -n '5 tests passed|deliberately UNRUN|Working profile — STILL OPEN|Promoted: 0|working-profile dogfood \*\*OPEN\*\*|promoted is 0' \
  docs/demos/upstream-repro/omp-jev-observer-20260919.md \
  docs/INTEGRATIONS.md README.md
# HIT: omp-jev-observer-20260919.md:30  5 tests passed
# HIT: omp-jev-observer-20260919.md:36  Registration command — deliberately UNRUN
# HIT: docs/INTEGRATIONS.md:161  Working profile — STILL OPEN
# HIT: docs/INTEGRATIONS.md:163  Promoted: 0
# HIT: docs/INTEGRATIONS.md:199  promoted is 0
# HIT: docs/INTEGRATIONS.md:212  working-profile dogfood **OPEN**
# HIT: README.md:108  working-profile dogfood **OPEN**

rg -n $'\tPROMOTED\t|^[^#].*PROMOTED' docs/demos/STATUS.tsv
# EMPTY — no PROMOTED verdict row on this tip (matches INTEGRATIONS.md:5)

which infisical; which omp
# BOTH empty on this VM. Live inject+lab command NOT_RUN.

# Offline observer suite on this tip (historical P2-13 quote is 5/5):
node --test work/omp-jev-observer/test/observer.test.mjs
# 8/8 pass on 7f28d54 (includes "missing gate and session context stay
# absent without blocking" — the R38 omit arm). Not a live row.
```

### G7 — Invented `dcgVerdict: "unknown"` (default looks measured)

Pack G7. Invented observation adjacent to taxonomy #1; also a
live-proof gap (offline green + fake fields ≠ proof).

**(a) Evidence.**

`context.dcgVerdict ?? 'unknown'` is not a fail-open. Fail-open is
`return undefined` and still log. The `?? 'unknown'` filled a
stored / gated field the event does not expose
(`NEGATIVE_EVIDENCE.md:1608-1614`). Twenty-seven live decision rows
then read as a measured verdict. Honesty pass 3 counted them as
published fiction (`.flywheel/feedback/2026-09-19-honesty-pass-3.md:27`).
INTEGRATIONS still tabulates the 27 as `defaulted, legacy`
(`:133`) next to the one row that omitted the field (`:134`).

R38’s rule is already the forward move (`:1638-1640`): omit the
field. `'unknown'` is a confession formatted as a value.

R38’s retry is a grep after any observer change (`:1642-1643`).
On `7f28d54` that grep against
`work/omp-jev-observer/src/observer.mjs` is **empty**. The source
already omits (`observer.mjs:47` reads `context.dcgVerdict` with
no string default; tests at `observer.test.mjs:28,97` assert
`'dcgVerdict' in records[0] === false`). The cleanup receipt
(`omp-jev-observer-sentinel-cleanup-20260919.md:9-17`) says the
same. Fail-open is preserved: no verdict still means do not block.

The residual the pack named (`README.md:55-57`, `GATES.md:163-164`,
`docs/INTEGRATIONS.md:200-201`) is **not** still in the handler.
`GATES.md:162-165` correctly says `a2e2035` dropped the fictional
default and the new row’s keys omit `dcgVerdict`. `README.md:57,92`
and `docs/INTEGRATIONS.md:64,156` still write “Residual:
`createObserver` / `installObserver` still defaults
`context.dcgVerdict ?? 'unknown'` on the gate path.” That sentence
is now an invented observation about the source — the same class
as the 27 rows. A field that is always present in the README and
absent in the handler lies quietly and looks measured.

**(b) Why this is invented observation, not fail-open.**

Skill hard rule 7: fail-open on host hooks — return undefined,
still log the error. Unused error fields are evidence; swallowed
give-up is not. `?? 'unknown'` is the opposite: it swallows
absence into a value a later reader will count.

Playbook F (`dcg explain`) is about blocked commands. It does not
cite R38. Playbook K’s “Endpoint / key not configured” row is
about injection, not about fabricating a verdict string when the
event has no verdict. The hole is a hard rule: never `??
'unknown'` / `?? 0` on a truth-bearing stored field. Omit.

**(c) Forward move — never `?? 'unknown'` on truth fields.**

1. **Omit absent observations.** If the event does not expose a
   verdict, the record must not contain `dcgVerdict`. Tests already
   assert this (`observer.test.mjs:28,97`). Copy that shape.
2. **Never `?? 'unknown'` / `?? 0` / `?? ''` on a field a later
   reader will treat as measured.** A default that is always
   present and sometimes real cannot be filtered.
3. **Keep fail-open.** `return undefined`; still write the
   diagnostic. No verdict ≠ a verdict named `"unknown"`.
4. **Docs that still name the residual are the next product tick,
   not a new default.** Delete or rewrite `README.md:57,92` and
   `docs/INTEGRATIONS.md:64,156` so they match
   `observer.mjs:47` / `GATES.md:162-165`. Do not re-introduce the
   sentinel to make the README true.

Do not land those README/INTEGRATIONS edits in this PR. Name them:
stale residual prose claiming `?? 'unknown'` after the source
omitted it → product tick. This pass lands the rule.

---

### G8 — Paperwork as progress / ceremony scored as work

Pack G8. Taxonomy #6, plus #7 when a real human decision exists
and the agent fills time with docs instead of naming it.

**(a) Evidence.**

`docs/demos/tick.md:7-11` is the measured ceremony audit: 22
commits, **USER 0 · ENABLER 5 · PROCESS 17**, verdict
**DRIFTING**. The instruments became the work. The rewrite’s only
opening question (`:13-15`) is what a person *outside this lane*
could install, run, or read. `shipped:NONE` twice (`:23-25`) is a
stop condition: no further audit, ruling, ledger row, or
instrument — dispatch the smallest consumable thing, or send
Joshua one line.

`docs/demos/PLAN.md:1794,1980,2477` names the same class as a
kill: “a kill by paperwork”, “an unverifiable condition used as a
gate is a kill by paperwork”, “An UNASKABLE cannot block a rung
indefinitely.” Those are rulings *against* paperwork-as-gate.
They are also how much of this lane’s prose is about the
instruments.

The pack cited a `jev-demo-loop-a1q` comment storm with explicit
`NO-CLAIM: nothing built`. On this tip that exact phrase is
**not** independently re-derived from `.beads/issues.jsonl` (the
parent bead `:8` and dry-queue child `:12` exist; the “nothing
built” comment storm is not a greppable literal here). The
tick.md stop condition is the citable G8 quote. Do not inflate
the beads line into a count this pass did not dump.

**(b) Why this is paperwork as progress.**

Skill failure mode 6: Charter/plan/receipt churn with no product
change, scored as work. Hard rule 8: if it cannot change the
product, either dig into a product slice or HALT with one named
human decision — do not orbit with ceremony. Failure mode 7: a
real human decision exists, but the agent fills time with docs
instead of naming it.

A close that quotes only a receipt, a ruling, or a ledger row is
the PROCESS 17 pattern. `shipped:NONE` is the discriminator. Two
in a row and the next unit must be install/run/read, or one
human sentence.

**(c) Forward move — every close quotes a product tick OR one
human decision.**

A legal close is exactly one of:

1. **Product tick** — a quoted install, run, or read artifact a
   non-lane reader can consume. Form from `tick.md:20`:
   `shipped:<what a non-lane reader can install/run/read>`.
2. **One named human decision** — Joshua’s words, unparaphrased,
   and then stop. Not a detour essay while waiting.

Illegal closes: “receipt-only”, “audit-only”, “ledger-only”,
“steelman-only”, a second `shipped:NONE` followed by another
instrument. Skill Rule Zero operationalized: if it cannot change
the product, HALT. Do not spawn the next ceremony file.

This PR is an essay. Its own close is therefore #2-shaped for
the *skill-loop packet* (Joshua assigned Pass 5) and must name
the product ticks it did **not** land — residual-prose delete;
one live JSONL line. See G10.

---

### G10 — Offline green ≠ one live row; dogfood OPEN; promoted 0

Pack G10. Live-proof gap / paperwork-adjacent (taxonomy #6);
skill hard rule #6 / mission 6.

**(a) Evidence.**

P2-13 closed on offline `5 tests passed`
(`omp-jev-observer-20260919.md:28-31`) and a registration
command marked **deliberately UNRUN** (`:36-43`), with the
NO-CLAIM that the extension had captured no live traffic
(`:45-49`). That is the exact “offline green ≠ done” the skill
already forbids.

P2-15 later registered disposable `jev-lab` and found the 0-row
defect the UNRUN close hid (`:51-53`). The live JSONL it quotes
(`:64-68`) is `diagnostic.v1` + `decision.v1` with
`error: Error: JEV_OBSERVER_ENDPOINT is not configured`. That is
a live *error* row, not `ok` / scores / latency / `error=null`.
Working-profile dogfood stayed OPEN
(`docs/INTEGRATIONS.md:161-165,197-199,212`;
`README.md:57-58,92-93,108`). `promoted` is 0
(`INTEGRATIONS.md:5,163,199,213`; `STATUS.tsv` has no
`PROMOTED` verdict row on this tip).

The same class at suite scale: `README.md:61-65` — every cloned
Jev repo passed, and a RANDOM judge still left 254/305 green.
Offline green is plumbing.

**(b) Why this is a live-proof gap, not a park.**

Hard rule 6: prove one live row. Offline green ≠ done. Quote
`ok` / scores / latency / `error=null`, or write the next
command. Playbook K already lists “Endpoint / key not
configured” → inject via Infisical. `.env.example:15-25` is the
working one-liner (projectId
`42b194c3-89d7-4ebb-895f-dd77ddf005ba`, `infisical run … omp
--profile=jev-lab … </dev/null`). Pass 3 (PR #11) already
required inject-or-HALT for the named hole. This pass requires
the *quoted live line* or the *exact next command* before a
close may say “wired” / “working” / “promoted”.

A lab error row does not close working-dogfood. A first-contact
harm-rule receipt does not close the observer row
(`INTEGRATIONS.md:212`). `promoted: 0` is the scoreboard, not a
badge.

**(c) Forward move — live JSONL line or the exact next
infisical+omp command.**

Definition of done for any observer / judge close:

```text
LIVE-PROOF (one of these, not both deferred)

[ ] A) Quote one live session JSONL line:
       kind=<diagnostic.v1|decision.v1>
       scores=…  latency=…ms  error=null  (or the error string)
       session=<path>  profile=<jev-lab|working>
       model=<id>  N=1  date=<ISO>
    A configuration-error row (JEV_OBSERVER_ENDPOINT is not
    configured) is a live *error* row. It does not count as
    ok / scores / latency / error=null. Write command B.

[ ] B) Write the exact next command (do not say “inject later”):

infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  omp --profile=jev-lab --no-extensions \
      --extension=$HOME/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts \
      -p 'run exactly: echo observer-live-proof' </dev/null

    Presence first, never print the value:
    infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
      printenv TYPESAFE_API_KEY | wc -c
    (or JEV_OBSERVER_ENDPOINT — same form, wc -c only)

[ ] Working-profile dogfood stays OPEN until A lands on a
    working profile. That promotion is a named human
    decision, not an essay. Lab ≠ working
    (INTEGRATIONS.md:161-165).
```

On this VM `infisical` and `omp` are not on `PATH`. Command B is
**NOT_RUN**. That is why this close cannot claim a live row.

The template for a successful A, taken from the P2-15 receipt
shape (`omp-jev-observer-20260919.md:64-68`) plus hard rule 6:

```text
<session.jsonl>
  com.zeststream.omp-jev-observer.diagnostic.v1
  com.zeststream.omp-jev-observer.decision.v1
  ok=true  scores=…  latency=…ms  error=null
```

Until a line matching that lands, `promoted` stays 0 and
working-dogfood stays OPEN. Offline 5/5 or 7/7 does not move
either number.

---

### Adjacent quotes (not expanded)

`docs/demos/PLAN.md:1794,1980,2477` — “kill by paperwork” /
UNASKABLE-as-gate. Same class as G8; already used as supporting
cite. Not a fourth GAP.

`docs/demos/upstream-repro/omp-jev-observer-sentinel-cleanup-20260919.md:9-17,35-38`
— source omit + offline 7/7 + explicit NO-CLAIM on live /
working-dogfood. Supports G7’s “code already omits” and G10’s
“offline ≠ live.” Not expanded.

`compaction/src/omp-adapter.ts:94` `c.name ?? 'unknown'` and
`docs/demos/upstream-repro/sentinel-default-audit-20260919.md:13-15`
— other stored `?? 'unknown'` sites (probe / adapter / report).
R38’s retry named a third *observer* instance. These are the
same class on other files. Listed so a later product tick can
grep them. Not a new GAP in this pass.

`docs/INTEGRATIONS.md:174` — “no standing ban” / invented
STOP-LIVE. Pass 1 / PR #9. Not re-opened.

---

### What this pass is not claiming

- That `?? 'unknown'` is still in `observer.mjs`. It is not, on
  `7f28d54`. The remaining lie is residual *prose*.
- That working-dogfood closed, or that `promoted` moved. Both
  stay 0 / OPEN.
- That P2-15’s JSONL error row is a live Jev proof line. It is
  a live configuration-error row.
- A live inject+lab run on this VM. `infisical` / `omp` absent;
  command B is written, not executed (`NOT_RUN`).
- The beads `NO-CLAIM: nothing built` comment-storm count from
  the pack. Not independently re-derived here.
- Invented STOP-LIVE (Pass 1 / PR #9), the tool_call over-learn
  (Pass 2 / PR #10), named-hole-then-park (Pass 3 / PR #11), or
  selector / extension-authoring (Pass 4 / PR #12).
- Pass 6, Pass 7, or the Jeffrey-voice essay.

### Next lever (Pass 5 close)

Land the skill patches (never `?? 'unknown'` on truth fields;
every close quotes a product tick or one human decision; live
JSONL line or the exact `infisical run … omp --profile=jev-lab`
command). The next *product* ticks this trio blocked:

1. Delete stale residual prose at `README.md:57,92` and
   `docs/INTEGRATIONS.md:64,156` so they match
   `observer.mjs:47` (omit, do not re-default).
2. Run command B above and quote one `error=null` JSONL line,
   or HALT with the one human decision that working-profile
   registration is Joshua’s.

Do not start Pass 6 in this PR.

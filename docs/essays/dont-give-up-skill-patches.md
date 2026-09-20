# dont-give-up skill patches (consolidated from PRs #9–#14)

<!-- origin/cursor/dont-give-up-invented-policy-f56e -->
## Pass 1 — Invented policy

Evidence: `docs/essays/dont-give-up-gaps.md` Pass 1. File:line citations
there are the authority; this page is the proposed skill text.

### Patch 1.1 — Discriminate user-said stop from invented stop

Add under **The failure mode**, after item 1 (Invented policy):

```markdown
**Discriminator (run before you honor a STOP / DEFER / quiet-window):**

| Token | Invented (retract and dig) | User-said / honest (honor, keep narrow) |
|---|---|---|
| STOP-LIVE / "registration requires human review" / "off the table" | No quote from the user. A receipt closed as "deliberately UNRUN." | User named the path and stopped it. |
| quiet-window | Applied as a science gate, or as the retry for a non-timing failure (502, missing field, empty selector). | User said don't mark timing/shared-box work 100% done until a quiet re-run. Hosted API and offline recomputes are out of scope. |
| DEFER / BLOCKED / REFUSE / PREPARED-NOT-MEASURED | Named probe was a file read or one command, and it was not run. "Scheduling, not a blocker." | Named cheaper substitute for *this* gate, or one named human decision, and the next command is written. |

If you cannot paste the user's sentence next to the ban, the ban is yours. Retract it.
```

Why: this lane's `AGENTS.md:1495` makes `DEFER` a legal honest outcome.
The skill currently lists `DEFER` as if the word itself were the failure
(`dont-give-up` failure mode 1). Measured: `omp-jev-observer-20260919.md:36-43`
invented human-review; `audit-q105-promotion-20260918T140000Z.json:33-35` is
a real DEFER.

### Patch 1.2 — Name this lane's invented tokens

Add to **What not to do**:

```markdown
- Invent STOP-LIVE, "registration requires human review", or "off the table"
  for an observe-only fail-open hook. Fail-open plus one driven probe on
  pane 0 / an added test pane / a disposable lab profile is the dig.
  Mid-flight panes stay untouched; that is courtesy, not a ban on all live
  registration.
- Expand a user quiet-window (timing on a shared box) into a science gate
  or into the retry for a response-shape / 502 / selector miss.
- Retract an invented ban in a scoreboard and leave "has not been attempted"
  as the close. The retraction is not the product tick.
- Write "the deferral is scheduling, not a blocker" for a priced build.
  Start it under a supervised process, or name the one human decision and halt.
```

Why: `docs/INTEGRATIONS.md:174` already had to retract STOP-LIVE after the
fleet invented it. The skill should make that token un-inventable next time.

### Patch 1.3 — Quiet-window clause (timing only)

Add under **Hard rules**, after rule 1:

```markdown
1a. **Quiet-window is a timing hold, not a science gate.** Honor it only
    for verdicts whose evidence is "did not finish in time" on shared
    hardware, and only after you can quote the user. A 502, a missing
    field, a loader that writes zero rows, or an unread `.d.ts` is
    playbook K / E / the two-minute dig — not a calendar.
```

Why: `STATUS.tsv:35` chained `backend-502-message-content-missing` to
`retry-in-quiet-window`. `NEGATIVE_EVIDENCE.md:1286-1288` limits the rule
to timing. `README.md:802-804` then published the window without the quote.

### Patch 1.4 — Live-registration playbook row (pack G9)

Add to playbook **K** ("Live proof still failing"):

```markdown
| Symptom | Dig |
|---|---|
| "Registration requires human review" / STOP-LIVE / working-profile deferred | Check: did the user say that? If no, register observe-only fail-open on pane 0, an added test pane, or `omp --profile=jev-lab --no-extensions --extension=<one>`. **Fleet blast radius is a human gate only for working profiles, never for disposable lab / `--extension=<one>`.** Write rollback first if the target is a working profile. Quote one session row. Do not take down mid-flight panes. P2-15 (`omp-jev-observer-20260919.md:47-60`) is the existence proof: skipping lab UNRUN hid a 0-row loader defect. |
| Ban retracted in docs; act still "not attempted" | The next command is the act, not another retraction sentence. |
```

Why: pack G9. `omp-jev-observer-20260919.md:36-43` invented human-review for
a command that could have been `jev-lab`. `INTEGRATIONS.md:180-181` already
says lab/RUN-CLONE is free. `harm-rule-promoted-20260919.md` registered on
`codex` the same day.

### Patch 1.5 — Checklist item for invented policy

Add to **Decision checklist**:

```markdown
- [ ] If I am about to write STOP / DEFER / quiet-window / off-the-table:
      can I paste the user's sentence? If no, retract and name the next
      command. If yes, is my hold *narrower than* that sentence?
```

If that box is unchecked, filing `blocked` / `deferred` remains forbidden
(existing checklist closer).

### Patch 1.6 — Worked retract script (pack G1)

Replace hard-rule 1's one-liner ("Do not invent blockers. Retract invented
STOP / DEFER / quiet-window policy.") with a three-step retract:

```markdown
1. **Do not invent blockers. Retract invented STOP / DEFER / quiet-window /
   "off the table" / STOP-LIVE with this script:**
   (a) Paste the user's stop sentence, or write `user-stop: none`.
   (b) If `none`, map the hole to RUN-CLONE / `jev-lab` / pane 0 / an added
       test pane (`docs/INTEGRATIONS.md:178-181`). Mid-flight panes stay
       untouched; that is courtesy, not a ban.
   (c) Quiet-window may be honored only for "did not finish in time" on
       shared hardware (`NEGATIVE_EVIDENCE.md:1286-1288`). A 502, a missing
       field, a zero-row loader, or an unread file is not a quiet-window.
```

Why: pack G1. `INTEGRATIONS.md:174` had to retract STOP-LIVE after the fact.
The skill named the failure and left agents without a retract procedure.

### Patch 1.7 — Lab vs working-profile human gate (pack G9)

Add under **Hard rules**:

```markdown
1b. **Fleet blast radius is a human gate only for working profiles.**
    Disposable `jev-lab` and `omp --no-extensions --extension=<one>` do
    not require invented "human review." Closing a unit as deliberately
    UNRUN on those paths is invented policy.
```

Why: pack G9. P2-13 UNRUN delayed the 0-row finding until P2-15.

### What this pass does not patch

- Over-learned kill, named-hole-then-park, selector misses, paperwork-as-progress
  beyond retraction-without-act, or tool playbook holes. Those are later
  passes. Ask-instead-of-dig is touched only as the G9 human-gate mechanism.
- The Jeffrey-voice essay (Pass 8).
- Any edit to the uploaded skill file in this turn; the patches are proposed
  text for a later house-skill land.

<!-- origin/cursor/dont-give-up-over-learned-kill-edb3 -->
## Pass 1 — Invented policy (stub)

Pass 1 patches (retract script 1.6; lab-vs-working-profile 1.7; quiet-window
timing-only; invented-token discriminator) live on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-invented-policy-f56e`). Not re-authored here.

---

## Pass 2 — Over-learned kill

Evidence: `docs/essays/dont-give-up-gaps.md` Pass 2. File:line citations
there are the authority; this page is the proposed skill text.

### Patch 2.1 — Narrow-kill card (pack G2)

Add under **Hard rules**, replacing the one-liner of rule 2 (“Keep kills
narrow. Cost-benefit kill applies to *that gate* only.”) with a card
that must be filled before any drop / never-call sentence:

```markdown
2. **Keep kills narrow. Fill this card before you write “drop the
   model / never call / no Jev / RULE WINS”:**

   | column | required value |
   |---|---|
   | surface | the gate, hook, question, or package — not “the fleet” |
   | cheaper substitute | named artifact that beat the model on *this* surface |
   | still-calls-Jev-elsewhere | at least one sibling that still pays, with file:line |
   | proof receipt | the head-to-head / measure that scoped the kill |

   A cost-benefit kill applies to *that gate* only. “Never call the
   model” with no surface name is invented policy wearing a kill’s
   clothes. If you cannot name a still-calling sibling, you have not
   finished the card — search before you ban.
```

Why: pack G2. `docs/INTEGRATIONS.md:18,39-41` already has surface +
substitute + receipt. `README.md:107` drops the surface and becomes
the over-read. `work/omp-jev-review/README.md:11-18` is the sibling
agents skip. The skill named “keep kills narrow” and left agents
without a filled-card check.

Worked card from this lane (do not paste as the only example later;
it is the existence proof):

| surface | cheaper substitute | still-calls-Jev-elsewhere | proof receipt |
|---|---|---|---|
| `tool_call` / `omp-harm-rule` | four regexes; 12/12 recall, FP 0/38 | `work/omp-jev-review/src/index.ts:66` `askJev`; also rerank `:94`, failure `:8`, observer `observer.mjs:45-46` | `docs/demos/upstream-repro/toolcall-headtohead-20260919.md:39-41` |

### Patch 2.2 — Ban unscopeable never-call language

Add to **What not to do**:

```markdown
- Write “never call the model / drop Jev / no Jev call / RULE WINS”
  without a surface token. The legal compressions are “drop Jev from
  `tool_call`” and “never call Jev on this arm.” “Ship the classifier,
  drop Jev” is the over-learn (`README.md:107` vs `:24`).
- Open a scoreboard on the kill row and omit the still-calling
  siblings. `docs/INTEGRATIONS.md` `rg` for `omp-jev-review|rerank|failure`
  is empty on a tip whose README table has four `calls Jev? = yes` rows.
- Collapse five independent cheap wins into one “NO JEV CALL IN THEM”
  hero line (`README.md:9-10`). Each win keeps its own card.
- Quote “where a judge belongs” and cite only the drop
  (`INTEGRATIONS.md:203`). Name one still-calling sibling in the
  same paragraph.
```

Why: those four sentences are the measured over-reads of one
correct kill. The skill already says “Expand one failed experiment
into a fleet-wide pause” (What not to do). This patch names the
tokens this lane actually minted.

### Patch 2.3 — Positive-control row (narrow-kill done right)

Add to playbook, new short block after **What not to do** or as
playbook **M** (“A cheap rule just won”):

```markdown
### M. “A cheap rule just won on one gate”

Copy a narrow kill; do not generalize it.

1. Fill the narrow-kill card (rule 2).
2. Open the nearest sibling package that still calls the model.
   In this lane: `work/omp-jev-review/README.md` (“one surface, not
   a ban”) or `work/omp-jev-rerank/README.md` (“measurement killed
   the other two” — question-level kill, package still calls).
3. If no sibling exists, say so on the card (`still-calls-Jev-elsewhere:
   none found, searched <paths>`). Do not infer “none exist.”
4. Keep going on the sibling surface. A win on gate A is not a
   pause on gate B.

Positive controls already in this tree:

- Rerank: killed `definitional` and `noise`, kept `ordered`, still
  `askJev` (`work/omp-jev-rerank/src/index.ts:94-96`).
- Preaction: “Never calls Jev on this arm” (`src/index.ts:4`) — the
  surface token is in the sentence.
- Review header: *WHY THIS ONE CALLS JEV* (`src/index.ts:4-11`).
```

Why: the skill’s playbooks A–L tell you what to reach for when
stuck. They do not tell you what to do the moment a cheap rule
wins — which is when the over-learn fires. G2’s forward move was
“inventory every drop-Jev claim and force a surface + sibling.”
This is that inventory, operationalized.

### Patch 2.4 — Checklist item for over-learned kill

Add to **Decision checklist**, after the existing item 2 (“Is this
a *narrow* cost-benefit kill with a named cheaper substitute for
*this* gate only?”):

```markdown
- [ ] If I just killed a model-call on one gate: did I fill the
      narrow-kill card, including `still-calls-Jev-elsewhere` with
      a file:line? If the next sentence is “so we never call Jev,”
      the card is incomplete — retract the fleet clause.
```

If that box is unchecked, filing “blocked / dropped the model /
RULE WINS (unscopeable)” remains forbidden.

### Patch 2.5 — Failure-mode worked example

Replace failure mode 2’s one-liner with the lane example:

```markdown
2. **Over-learned kill** — a cheap rule wins on *one* gate →
   “never call the model / never try the hard path” everywhere.
   Worked example: four regexes beat live Jev on `tool_call`
   (12/12 vs 11/12, FP 0/38) → README scoreboard “drop Jev”
   with the surface deleted, and INTEGRATIONS listing only the
   no-call row while `omp-jev-review` still `askJev`s. The kill
   is right. The fleet clause is the give-up.
```

Why: taxonomy #2 was abstract. Agents in this lane over-learned
*this* kill, on *this* tip, and the review README was written
to stop them and was skipped anyway (pack G2).

### What this pass does not patch

- Invented STOP / DEFER / quiet-window (Pass 1 / PR #9).
- Named-hole-then-park, Infisical `--projectId`, selector misses,
  paperwork-as-progress, live-proof operationalization, tool
  playbook holes (Passes 3–7 in the loop sheet; 4–7 if numbering

<!-- origin/cursor/named-hole-then-park-c4a2 -->
## Pass 1 — Invented policy (stub)

Pass 1 patches (retract script 1.6; lab-vs-working-profile 1.7; quiet-window
timing-only; invented-token discriminator) live on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-invented-policy-f56e`). Not re-authored here.

## Pass 2 — Over-learned kill (stub)

Pass 2 patches (narrow-kill card 2.1; unscopeable never-call ban 2.2;
positive-control row 2.3; checklist 2.4; worked example 2.5) live on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-over-learned-kill-edb3`). Not re-authored here.

---

## Pass 3 — Named hole then park

Evidence: `docs/essays/dont-give-up-gaps.md` Pass 3. File:line citations
there are the authority; this page is the proposed skill text.

### Patch 3.1 — Playbook D: replace bare `<id>` with the documented pattern

Replace playbook D’s example block (skill lines that currently say
`--projectId=<id>`) with the copy-paste that this repo already
measured. Presence probe is `wc -c`. Never print the value.

Proposed skill text (playbook D):

- Believe it’s there. This workspace’s Infisical project is
  `42b194c3-89d7-4ebb-895f-dd77ddf005ba` (see `.env.example`).
  `jev/` has no `.infisical.json`. A CLI that says “run infisical
  init … or pass in project id” means **UNLINKED DIRECTORY**, not
  **MISSING SECRET**.
- Presence only — never print the value:

      infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
        printenv TYPESAFE_API_KEY | wc -c

      infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
        printenv JEV_OBSERVER_ENDPOINT | wc -c

      infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
        <your command>

- A bare `infisical secrets` / `infisical run` with no `--projectId`
  failing in this directory is **not** a missing-secret receipt. Retry
  with `--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba` before you
  report absence. `wc -c` returning `0` after that retry is a HALT
  with one named human decision (add the name to the project) — not
  “key unset, park.”
- Safety: agents hold handles, not raw secrets. Prefer `infisical
  run` injection over exporting into chat. Presence probes: `wc -c`,
  not `cat`, not `printenv` alone, not `echo`.

Why: pack G4. The skill taught the hole it was supposed to close by
leaving `<id>` in the example. This lane copied that placeholder into
`README.md:696` and `scripts/jev-probe.mjs:38` while the same probe’s
header (`:6`) and `.env.example:11` already have the real id.
`.env.example:27-31` already says unlinked ≠ missing. The skill must
lead with the documented pattern, not a blank.

`grep -c TYPESAFE_API_KEY` on `infisical secrets` (`.env.example:34-35`)
is a names-only count and is also legal. Prefer `printenv NAME | wc -c`
in the skill so a value never crosses stdout.

### Patch 3.2 — Playbook K: inject-or-HALT (no OPEN forever)

Replace playbook K’s “Endpoint / key not configured” row with a
mandatory next line:

```markdown
| Symptom | Dig |
|---|---|
| “Endpoint / key not configured” / `unconfigured` / `is not set` | **Inject-or-HALT.** (1) Presence-probe the named env with `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- printenv <NAME> \| wc -c`. (2) If `wc -c` > 0, inject and run the real command; quote one live row (`ok` / scores / latency / `error=`). (3) If `wc -c` is 0, HALT with one named human decision (add `<NAME>` to that Infisical project). Offline-only work may stub `classify` / inject a fake asker, then still write the live inject one-liner. **Forbidden:** log the error and leave a scoreboard cell OPEN with no next command. |
```

Why: pack G3. Observer receipt `:68` named
`JEV_OBSERVER_ENDPOINT is not configured`. Fail-open was correct.
`docs/INTEGRATIONS.md:161-165,197-201,212` then left working-profile
dogfood **OPEN** with no inject line. `jev-client/src/index.ts:46-54`
already embeds the fix in the error string; the skill’s K row did
not make that the next action.

### Patch 3.3 — Failure-mode worked example

Replace failure mode 3’s one-liner with the lane example:

```markdown
3. **Named hole, then park** — “API key unset”, “docs not found”,
   “no examples”, “run infisical init” written down and abandoned.
   Worked example: live observer row logged
   `error: Error: JEV_OBSERVER_ENDPOINT is not configured`
   (`omp-jev-observer-20260919.md:68`); INTEGRATIONS left
   working-profile dogfood OPEN (`:161-165,212`). Parallel:
   every agent who ran bare `infisical secrets` in this unlinked
   dir declared TYPESAFE_API_KEY missing; `.env.example:27-31`
   already says that message is UNLINKED DIRECTORY; projectId
   `42b194c3-89d7-4ebb-895f-dd77ddf005ba` was on the same page.
   The hole is engineering work. OPEN with no next command is
   the give-up.
```

Why: taxonomy #3 was abstract. This lane parked *this* endpoint on
*this* tip after the working one-liner was already committed.

### Patch 3.4 — Checklist items

Add after the existing “Did I try the proven secret-injection or
install command from a receipt?”:

```markdown
- [ ] If a receipt says `not configured` / `unconfigured` / `is not
      set`: did I run inject-or-HALT (presence `wc -c`, then inject
      or one named human decision)? Logging the error and leaving
      OPEN is the park — forbidden.
- [ ] If Infisical said “run init or pass project id”: did I retry
      with `--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`
      before reporting a missing secret? Bare `<id>` in a command
      I am about to publish is a defect.
```

If either box is unchecked, filing “blocked / key missing / OPEN” remains
forbidden.

### Patch 3.5 — What not to do

Add to **What not to do**:

```markdown
- Leave `projectId=<id>` or `projectId=…` in a published command
  when `.env.example` already has `42b194c3-89d7-4ebb-895f-dd77ddf005ba`
  (`README.md:696` vs `.env.example:15`; `scripts/jev-probe.mjs:38`
  vs `:6`).
- Treat “run infisical init” as missing-secret evidence. It is
  unlinked-directory evidence (`.env.example:27-31`).
- Print a secret to prove it exists. Presence probe is `printenv
  NAME | wc -c` (or `infisical secrets --projectId=… | grep -c NAME`).
- Log `* not configured` as a decision row and close / leave OPEN
  without inject-or-HALT (`omp-jev-observer-20260919.md:68` +
  `INTEGRATIONS.md:212`).
```

Why: those four sentences are the measured parks of one documented
inject. The skill already says “Re-ask for a secret an injection
tool already holds.” This patch names the tokens this lane minted
(`<id>`, OPEN, “run init”).


<!-- origin/cursor/selector-and-dig-skip-364d -->
## Pass 1 — Invented policy (stub)

Pass 1 patches (retract script 1.6; lab-vs-working-profile 1.7; quiet-window
timing-only; invented-token discriminator) live on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-invented-policy-f56e`). Not re-authored here.

## Pass 2 — Over-learned kill (stub)

Pass 2 patches (narrow-kill card 2.1; unscopeable never-call ban 2.2;
positive-control row 2.3; checklist 2.4; worked example 2.5) live on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-over-learned-kill-edb3`). Not re-authored here.

## Pass 3 — Named hole then park (stub)

Pass 3 patches (documented `--projectId=` 3.1; inject-or-HALT 3.2;
`wc -c` presence probe; leftover `<id>` ban) live on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/named-hole-then-park-c4a2`). Not re-authored here.

---

## Pass 4 — Selector and dig-skip

Evidence: `docs/essays/dont-give-up-gaps.md` Pass 4. File:line citations
there are the authority; this page is the proposed skill text.

### Patch 4.1 — Mechanical `keys()` / `requireKey` before any absence claim

Replace checklist item “Did I verify selector ≡ claim (right file, row
type, env, session)?” with a mechanical stop. A reminder lost eight
times, then a ninth from code that never imported the helper
(`NEGATIVE_EVIDENCE.md:1448-1458,1752-1754`).

Proposed skill text (decision checklist):

```markdown
- [ ] Before any absence claim (“missing”, “0 rows”, “cannot
      attribute”, “not there”): did I dump the record’s own keys
      (`Object.keys(record)` / `inspectKey(record, name).keys`)
      and read through `requireKey` / `readRow`? A selector that
      returns nothing is indistinguishable from a thing that is
      not there. Publishing “0” without the key list is the
      eighth-then-ninth failure — forbidden.
```

Proposed skill text (new hard rule, after current #4):

```markdown
4b. **Dump keys before “missing.”** Absence is a claim against a
    record. `requireKey(record, name)` throws with
    `Keys present: […]` (`work/oracle-kit/index.mjs:116-123`).
    `inspectKey` returns the same list without throwing.
    `readRow` accepts both omp session shapes (nested
    `customType.data` and flat `customType` + top-level `data`;
    `work/jev-client/src/index.ts:127-159`). A hand-rolled
    `row.data` that returns `{}` is not evidence the row is
    empty (R41: the live Jev call sat at `customType.data`).
```

Why: pack G6. Checklist “selector ≡ claim” existed for the entire
eight-failure session. R33 published a false claim against a correct
artifact. `requireKey` landed after the eighth and did not prevent
the ninth, because nothing forced the call. The skill must make the
key dump the only legal path to an absence sentence.

### Patch 4.2 — Two wire shapes (omp session rows)

Add to playbook K, replacing “Selector says 0, author says N”:

```markdown
| Symptom | Dig |
|---|---|
| Selector says 0, author says N | **Two shapes, then keys().** omp session rows are (A) `{ customType: { type, data } }` (observer) and (B) `{ customType: "…", data }` (harm-rule / failure). `readRow` handles both (`jev-client/src/index.ts:136`; `TESTS.md:46`). A reader written against one reports “no rows” on the other — R33 and R41. Dump `keys()` / `requireKey` on the raw row before broadening. Diagnostics + decisions is the next widen, not the first. |
| Full profile hangs | Minimal `--no-extensions --extension=<one>` path first |
```

Why: pack G6 named `TESTS.md` `readRow` dual shapes. The current K
row says “broaden selector” and leaves the agent to invent the
widen. The two shapes are already in the sanctioned client. Copy
them; do not re-derive a third scanner.

### Patch 4.3 — Failure-mode worked example (taxonomy #4)

Replace failure mode 4’s one-liner with the lane example:

```markdown
4. **Selector narrower than the claim** — wrong field, file,
   session, or row type → false contradiction → quit.
   Worked example: R33 published “cannot explain its own output”
   after a failed `toolCallId` join; `keys()` on the same row
   was `[command, error, kind, model, probabilities, score,
   timestamp, toolCallId]` (`NEGATIVE_EVIDENCE.md:1423-1428`).
   Eighth of the day; only one that reached a receipt.
   Ninth (R41): “0 rows with real probabilities” because the
   scan read top-level `data` (`{}`) while the payload sat at
   `customType.data` (`flag 0.04 / pass 0.96`, `error: null`,
   `378ms`). Same class as `.distribution` vs `.probabilities`,
   `.probability` vs `.noul`, spaced `"role": "toolResult"`.
   The hole is the selector. Do not walk away from the claim.
```

Why: taxonomy #4 was abstract. This lane published the false
absence, retracted it, then repeated it.

### Patch 4.4 — Playbook E: 30-second checklist with the real URL

Replace playbook E’s “Two-minute dig, hard order” list with a
timed checklist that names the page agents skipped. `rg` for
`extension-authoring` over `docs/` `work/` `README.md` excluding
`docs/essays/` is empty on `ad765b0`. The skill already said “e.g. product
`…/docs/extension-authoring`.” Ellipsis is how the dig got skipped.

Proposed skill text (playbook E):

```markdown
### E. “Docs / examples / how do I build this package?”

30 seconds. Do not ask. Do not invent a factory.

1. Open **https://omp.sh/docs/extension-authoring**
   Confirm the ship shape on that page:
   - `export default function (pi: ExtensionAPI) { pi.on(...) }`
   - `package.json` `"omp": { "extensions": ["./src/index.ts"] }`
     (legacy `"pi.extensions"` still accepted)
   - install: `omp plugin install <path|git|npm>`
     or `omp --extension /absolute/path`
   Native/configured directory scan is `*.{ts,js}` only.
2. Copy one working package — official
   `oh-my-pi` `docs/skills/examples/hello-extension/`,
   or in-tree `work/omp-harm-rule/harm-rule.ts:27-32` /
   `work/omp-jev-observer/src/observer.mjs:50-53`.
   Manifest points at entry; default export registers `pi.on`.
3. **Neighbour co-presence before “zero events.”**
   Same session, same profile: a known-firing neighbour
   (dcg-tool-bridge / harm-rule) writes a row AND this
   module writes a row. 0 rows next to a firing neighbour
   means not loaded — missing `pi.on`, glob miss, or not
   on the `extensions:` list (`INTEGRATIONS.md:56-59,192`).
   Silence alone is not a finding. `node --check` will not
   catch a lost `pi.on` line.
4. Isolated path first:
   `omp --no-extensions --extension=<one>`.
   Then offline arms with planted negatives, then **one live row**.

If step 1 is unrun, “no examples” / “how do I register this”

<!-- origin/cursor/paperwork-and-live-proof-92c2 -->
## Pass 1 — Invented policy (stub)

Pass 1 patches (retract script 1.6; lab-vs-working-profile 1.7; quiet-window
timing-only; invented-token discriminator) live on
[PR #9](https://github.com/JYeswak/jev_playground/pull/9)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-invented-policy-f56e`). Not re-authored here.

## Pass 2 — Over-learned kill (stub)

Pass 2 patches (narrow-kill card 2.1; unscopeable never-call ban 2.2;
positive-control row 2.3; checklist 2.4; worked example 2.5) live on
[PR #10](https://github.com/JYeswak/jev_playground/pull/10)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/dont-give-up-over-learned-kill-edb3`). Not re-authored here.

## Pass 3 — Named hole then park (stub)

Pass 3 patches (documented `--projectId=` 3.1; inject-or-HALT 3.2;
`wc -c` presence probe; leftover `<id>` ban) live on
[PR #11](https://github.com/JYeswak/jev_playground/pull/11)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/named-hole-then-park-c4a2`). Not re-authored here.

## Pass 4 — Selector and dig-skip (stub)

Pass 4 patches (`keys()` / `requireKey` before absence 4.1; two wire
shapes 4.2; 30-second extension-authoring checklist 4.4) live on
[PR #12](https://github.com/JYeswak/jev_playground/pull/12)
(`docs/essays/dont-give-up-skill-patches.md` on
`cursor/selector-and-dig-skip-364d`). Not re-authored here.

---

## Pass 5 — Paperwork and live proof

Evidence: `docs/essays/dont-give-up-gaps.md` Pass 5. File:line citations
there are the authority; this page is the proposed skill text.

The pack’s “Suggested feed” mapped G7+G8+G10 to Pass 6. This packet
assigned them to Pass 5 after selector-and-dig-skip landed as Pass 4.

### Patch 5.1 — Never `?? 'unknown'` on truth-bearing fields

Add a hard rule after current #7 (fail-open). R38 minted **27 live
rows** that all read `dcgVerdict: "unknown"` — every one a default,
none an observation (`NEGATIVE_EVIDENCE.md:1600-1619,1638-1640`;
honesty-pass-3 `:27`).

Proposed skill text (new hard rule):

```markdown
7b. **Omit absent observations.** Never `?? 'unknown'` / `?? 0` /
    `?? ''` on a truth-bearing stored or gated field. A field that
    is always present and sometimes real cannot be filtered,
    counted, or trusted, and it survives inspection
    (`NEGATIVE_EVIDENCE.md` R38). If the event does not expose a
    verdict, omit `dcgVerdict`. Fail-open is `return undefined`
    and still log — not a fabricated `"unknown"` string. Cite
    R38 as the anti-pattern in playbooks F and K.
```

Proposed skill text (playbook F, extra row):

```markdown
| Symptom | Dig |
|---|---|
| Stored field is always `"unknown"` / always `0` | You invented an observation. Dump `keys()` on a raw live row. If the event never had the field, **omit it** — do not default. R38: `context.dcgVerdict ?? 'unknown'` produced 27 fake rows because the event exposes `[type, toolName, toolCallId, input]` and no verdict. Grep `?? 'unknown'` after any observer change. |
```

Proposed skill text (playbook K, extra row):

```markdown
| Symptom | Dig |
|---|---|
| Live rows look measured, every verdict is `"unknown"` | Default, not observation (R38). Omit the field. Do not treat 27 identical `"unknown"` values as a calibration signal. Keep fail-open (`return undefined`). |
```

Why: pack G7. Hard rule 7 already says fail-open and “unused error
fields are evidence.” Agents still wrote a sentinel that looks
like a verdict. The skill must forbid the sentinel by name.

On `7f28d54`, `work/omp-jev-observer/src/observer.mjs` has **no**
`'unknown'` — the source already omits (`:47`; tests
`observer.test.mjs:28,97`). `README.md:57,92` and
`docs/INTEGRATIONS.md:64,156` still claim the residual. Stale
prose that invents a default after the source omitted it is the
same class. Next product tick: delete that prose. Do not
re-introduce the sentinel.

### Patch 5.2 — Every close quotes a product tick OR one human decision

Replace the current hard rule 8 one-liner with an operational
stop. `tick.md:7-11` measured USER 0 / ENABLER 5 / PROCESS 17,
verdict DRIFTING — the instruments became the work.
`tick.md:23-25`: `shipped:NONE` twice is a stop, not a status.

Proposed skill text (hard rule 8, expanded):

```markdown
8. **Product ticks only.** A close must quote exactly one of:
   (a) a product tick — `shipped:<what a non-lane reader can
   install, run, or read>` (`docs/demos/tick.md:13-20`); or
   (b) one named human decision — the user’s words,
   unparaphrased — and then stop.
   Receipt-only / audit-only / ledger-only / steelman-only
   closes are PROCESS 17. Two consecutive `shipped:NONE` and
   you may not dispatch another audit, ruling, ledger row, or
   instrument (`tick.md:23-25`). An unverifiable condition
   used as a gate is a kill by paperwork
   (`docs/demos/PLAN.md:1980`).
```

Proposed skill text (decision checklist, new item):

```markdown
- [ ] Does this close quote a product tick (install / run /
      read artifact) or one named human decision? If neither,
      it is paperwork scored as progress — forbidden. A second
      `shipped:NONE` may not be followed by another instrument.
```

Proposed skill text (failure mode 6, worked example):

```markdown
6. **Paperwork as progress** (loop-engineering Rule Zero) —
   Charter/plan/receipt churn with no product change, scored
   as work. Worked example: 22 commits at USER 0 / ENABLER 5 /
   PROCESS 17, verdict DRIFTING; the conductor’s first thought
   every 20 minutes was *check the instruments*, and the
   instruments became the work (`docs/demos/tick.md:7-11`).
   `shipped:NONE` twice is the stop (`:23-25`).
```

Why: pack G8. The skill already says “if it cannot change the
product, HALT.” Agents still closed on ceremony. The tick.md
stop condition is the mechanical discriminator.

### Patch 5.3 — Live JSONL line or the exact next infisical+omp command

Operationalize hard rule 6. Offline `5 tests passed` plus a
deliberately UNRUN registration
(`omp-jev-observer-20260919.md:28-43`) left working-dogfood
OPEN and `promoted: 0` (`docs/INTEGRATIONS.md:161-165,199,212`).
P2-15’s live JSONL is an *error* row (`:64-68`), not
`ok` / scores / latency / `error=null`.

Proposed skill text (hard rule 6, expanded):

```markdown

<!-- origin/cursor/tool-playbook-holes-3858 -->
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

   Confirm the ship shape on that page, then match it to *this* repo:
   - default export + `pi.on` — copy
     `work/omp-harm-rule/harm-rule.ts:27-32` /
     `work/omp-jev-observer/src/observer.mjs:50-53`
   - `package.json` `"omp": { "extensions": ["./src/index.ts"] }`
     (legacy `"pi.extensions"` still accepted) — copy
     `work/omp-jev-review/package.json:8-9`
     (`observer` / `harm-rule` are single-file default exports and
     do **not** carry this key)
   - install: `omp plugin install <path|git|npm>`
     or `omp --extension /absolute/path`
   Native/configured directory scan is `*.{ts,js}` only.

2. Copy one working package in *this* repo, not a remembered
   factory. Do not ask one file to prove both shapes.

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
             -p 'run exactly: echo observer-minimal-actual' </dev/null
       # receipt: docs/demos/upstream-repro/omp-jev-observer-20260919.md:58
       # sibling nonce on :59 is echo observer-dead-port

   Then offline arms with planted negatives, then **one live row**.

If step 1 is unrun, “no examples” / “how do I register this” is
forbidden. If step 3 is unrun, “0 rows” is forbidden.
`rg -n extension-authoring` going empty in this repo is the hole
this paste closes — put the URL in the skill, not an ellipsis.
```

Why: skill E said “e.g.” and hid the host. This lane reinvented

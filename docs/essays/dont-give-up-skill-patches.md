# Don't Give Up — Skill patches

Patches for the `dont-give-up` skill, derived from lane evidence.
Do not apply these to any JSM-owned copy; house lessons stay in house skills.

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

### Patch 1.4 — Live-registration playbook row

Add to playbook **K** ("Live proof still failing"):

```markdown
| Symptom | Dig |
|---|---|
| "Registration requires human review" / STOP-LIVE / working-profile deferred | Check: did the user say that? If no, register observe-only fail-open on pane 0, an added test pane, or `omp --profile <lab> --no-extensions --extension=<one>`. Write rollback first. Quote one session row. Do not take down mid-flight panes. A sibling observe-only hook that already registered on a working profile is existence proof the ban was invented. |
| Ban retracted in docs; act still "not attempted" | The next command is the act, not another retraction sentence. |
```

Why: `harm-rule-promoted-20260919.md` registered on `codex` the same day
`omp-jev-observer-20260919.md` closed as deliberately UNRUN. The skill
should point at the working pattern instead of leaving agents to re-derive
"human review."

### Patch 1.5 — Checklist item for invented policy

Add to **Decision checklist**:

```markdown
- [ ] If I am about to write STOP / DEFER / quiet-window / off-the-table:
      can I paste the user's sentence? If no, retract and name the next
      command. If yes, is my hold *narrower than* that sentence?
```

If that box is unchecked, filing `blocked` / `deferred` remains forbidden
(existing checklist closer).

### What this pass does not patch

- Over-learned kill, named-hole-then-park, selector misses, ask-instead-of-dig,
  paperwork-as-progress beyond the retraction-without-act case, or tool
  playbook holes. Those are Passes 2–7.
- The Jeffrey-voice essay (Pass 8).
- Any edit to the uploaded skill file in this turn; the patches are proposed
  text for a later house-skill land.

# Don't Give Up — Skill patches

Patches for the `dont-give-up` skill, derived from lane evidence.
Do not apply these to any JSM-owned copy; house lessons stay in house skills.

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

### Patch 3.6 — Hard rule 3, operationalized

Keep hard rule 3’s two-minute dig. Add the stop condition that
makes “missing” illegal until the probe ran:

```markdown
3. **Two-minute dig before “missing.”** Search docs, registries,
   GitHub, local config, injection tools, prior receipts. For a
   key/endpoint: run the documented
   `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`
   presence probe (`printenv NAME | wc -c`) before you write
   “unset.” A scoreboard OPEN cell requires the next inject
   one-liner or a HALT with one named human decision.
```

### What this pass does not patch

- Invented STOP / DEFER / quiet-window (Pass 1 / PR #9).
- Narrow-kill card / unscopeable never-call (Pass 2 / PR #10).
- Selector misses, official extension-authoring dig, paperwork,
  live-proof operationalization, tool playbook holes (Passes 4–7).
- The Jeffrey-voice essay (Pass 8).
- Any edit to `README.md:696`, `scripts/jev-probe.mjs:38`, or
  `.env.example` in this turn; those leftover `<id>` sites are
  named product ticks, not this PR.
- Any edit to the uploaded skill file in this turn; the patches
  are proposed text for a later house-skill land.
- A live Infisical presence count on this VM (`infisical` not on
  `PATH` here). The one-liner is the patch; the count is NOT_RUN.

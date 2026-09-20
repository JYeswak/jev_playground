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
6. **Prove one live row.** Offline green ≠ done. Before any
   close that says wired / working / promoted / dogfood:
   quote `kind` / `ok` / scores / latency / `error=null`
   from a **live** session JSONL line, **or** write the exact
   next `infisical run --projectId=… -- omp --profile=jev-lab …`
   command (stdin closed with `</dev/null`). A
   configuration-error row (`JEV_OBSERVER_ENDPOINT is not
   configured`) is a live *error* row — it does not count as
   the proof line. Working-profile dogfood stays OPEN until
   the proof line lands on a working profile; lab ≠ working.
   `promoted: 0` is the scoreboard until that happens.
```

Proposed skill text (definition-of-done block, after “Minimal
vertical slice”):

```markdown
LIVE-PROOF (one of these, not both deferred)

[ ] A) Quote one live session JSONL line:
       kind=<diagnostic.v1|decision.v1>
       scores=…  latency=…ms  error=null
       session=<path>  profile=<jev-lab|working>
       model=<id>  N=1  date=<ISO>
    Template from omp-jev-observer-20260919.md:64-68 (replace
    the error with error=null before claiming Jev quality):
       <session.jsonl>
         com.zeststream.omp-jev-observer.diagnostic.v1
         com.zeststream.omp-jev-observer.decision.v1
         ok=true  scores=…  latency=…ms  error=null

[ ] B) Exact next command (copy; do not say “inject later”):

infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  omp --profile=jev-lab --no-extensions \
      --extension=$HOME/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts \
      -p 'run exactly: echo observer-live-proof' </dev/null

    Presence first, never print the value:
    infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
      printenv TYPESAFE_API_KEY | wc -c

If A is unquoted and B is unwritten, the unit is not closed.
Offline N/N is plumbing (`README.md:61-65` — a RANDOM judge
still left 254/305 green).
```

Proposed skill text (playbook K, replace “Endpoint / key not
configured”):

```markdown
| Symptom | Dig |
|---|---|
| Endpoint / key not configured | Wire the *real* client; inject via Infisical (`infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`). Then quote one live JSONL line (kind / scores / latency / error) or write that exact next omp command. Do not close on offline green. Do not leave working-dogfood OPEN forever. |
| Offline suite green, registration UNRUN | You have not proved a live row. Run B or HALT with one named human decision. P2-13’s 5/5 + UNRUN hid the 0-row defect P2-15 found (`omp-jev-observer-20260919.md:28-53`). |
```

Why: pack G10. Hard rule 6 already said “quote ok / scores /
latency / error=null, or write the next command.” The lane still
closed on offline plus UNRUN. This patch names the JSONL kinds
and the exact `infisical`+`omp` one-liner already in
`.env.example:15-25`.

### Patch 5.4 — Decision checklist (paperwork + live proof)

Add these two boxes to the existing checklist, after “Can I ship
scaffold → offline → one live row”:

```markdown
- [ ] Can I ship scaffold → offline → one live row in one
      short loop? Offline green without a quoted JSONL line
      or an exact next `infisical run … omp` command is not
      a close (G10).
- [ ] Does this close quote a product tick or one named
      human decision? Receipt-only is PROCESS 17 (G8).
- [ ] Did I omit absent observations instead of writing
      `?? 'unknown'` / `?? 0` on a truth field (G7 / R38)?
```

Why: the current “one live row” box is a reminder. G10 closed
on 5/5 anyway. Pair it with the JSONL-or-command stop and the
product-tick stop.

### Patch 5.5 — What not to do

Add to **What not to do**:

```markdown
- Score paperwork as progress. A close that cannot quote
  `shipped:<install/run/read>` or one human decision is
  PROCESS 17 (`docs/demos/tick.md:7-25`).
- Default an absent observation to `'unknown'` / `0` / `''`
  on a stored or gated field (R38: 27 fake `dcgVerdict`
  rows). Omit the field. Fail-open is `return undefined`.
- Close on offline green, or on a deliberately UNRUN
  registration, and call the surface working. Offline ≠
  one live row. A configuration-error JSONL line is not
  `error=null`.
- Leave working-dogfood OPEN as a status. It is a named
  next command or a named human decision, not a row that
  ages.
- Cite `promoted: 0` as rigor when the live proof line
  was never attempted. That number is the gap.
- Keep residual prose that claims `?? 'unknown'` after
  the source omitted it (`README.md:57,92` vs
  `observer.mjs:47` on `7f28d54`). That is invented
  observation in the docs.
```

Why: those six sentences are G7 + G8 + G10 on this tip. The
skill already says “Score paperwork as progress” and “Prove
one live row.” This patch names the tokens this lane minted
(`PROCESS 17`, `shipped:NONE`, `dcgVerdict: "unknown"` ×27,
`deliberately UNRUN`, `working-dogfood OPEN`, `promoted: 0`).

### Patch 5.6 — Failure mode 1 adjacent: invented observation

Keep failure mode 1’s invented-policy line (Pass 1 / PR #9).
Add the observation sibling so R38 is not mistaken for a
STOP-LIVE:

```markdown
1b. **Invented observation** — `?? 'unknown'` / `?? 0` on a
    truth field, or residual prose that claims a default the
    source no longer has. Worked example: 27 live rows of
    `dcgVerdict: "unknown"` (R38); then README/INTEGRATIONS
    still naming the residual after `observer.mjs` omitted
    it. A field that is always present and sometimes real
    lies quietly and looks measured. Omit.
```

Why: pack G7 called this “invented policy / invented
observation adjacent to #1.” Pass 1 covered STOP-LIVE. This
pass covers the sentinel.

### What this pass does not patch

- Invented STOP / DEFER / quiet-window (Pass 1 / PR #9).
- Narrow-kill card / unscopeable never-call (Pass 2 / PR #10).
- Documented `--projectId=` / inject-or-HALT (Pass 3 / PR #11).
- `keys()` / `requireKey` / extension-authoring URL
  (Pass 4 / PR #12).
- Tool playbook holes beyond F/K R38 + live-proof
  (Pass 7 in the pack’s original numbering).
- The Jeffrey-voice essay (not this packet).
- Pass 6. Not started.
- Deleting `README.md:57,92` / `docs/INTEGRATIONS.md:64,156`
  residual prose. Named as the next product tick; not this PR.
- Running the `infisical run … omp --profile=jev-lab` command.
  Written as command B; **NOT_RUN** on this VM (`infisical`
  and `omp` absent from `PATH`).
- Any edit to the uploaded skill file in this turn; the
  patches are proposed text for a later house-skill land.
- Working-profile registration or a `promoted` move.

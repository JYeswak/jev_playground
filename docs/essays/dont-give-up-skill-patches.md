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
is forbidden. If step 3 is unrun, “0 rows” is forbidden.
```

Why: pack G5. Official page + public example would have
short-circuited the silent-register / 0-row archaeology
(`INTEGRATIONS.md:167-172`; `harm-rule-shipped-20260919.md:71-74`).
The skill named a relative path; this patch names the URL
and the neighbour bar the lane already wrote down after paying
for the miss.

### Patch 4.5 — Playbook K: extension-loads-zero-rows row

Keep the existing “Extension loads, zero rows” row. Tighten it
so neighbour co-presence is mandatory, not optional:

```markdown
| Symptom | Dig |
|---|---|
| Extension loads, zero rows | Co-presence vs a known-firing neighbour in the **same session**; check `pi.on` still present (`node --check` is blind); loader globs `*.{ts,js}`; config is `extensions:` list. Then open https://omp.sh/docs/extension-authoring and compare factory / manifest / `--extension` to what you shipped. Do not ask how to register. Do not conclude “sees nothing” from silence alone (`INTEGRATIONS.md:56-59,192`). |
```

Why: pack G5. Current K already says “Co-presence vs a
known-firing neighbour; check `pi.on` still present; loader
globs.” Agents still skipped the official page. Put the URL
on the same row as the symptom.

### Patch 4.6 — What not to do

Add to **What not to do**:

```markdown
- Claim a field / row / event is absent without dumping
  `keys()` / `requireKey` / `inspectKey` on the record you
  actually have (`NEGATIVE_EVIDENCE.md:1448-1458,1747-1754`).
- Scan only top-level `data` on an omp session row. Observer
  payloads sit at `customType.data` (R41). Use `readRow`.
- Grep a spaced JSON key (`"role": "toolResult"`) and treat
  0 hits as “not persisted” (`SDK-SURFACE.md:19`).
- Ask how to author an omp extension, or invent a second
  factory, before opening https://omp.sh/docs/extension-authoring
  and copying `harm-rule.ts:27-32` / `observer.mjs:50-53`.
- Report “0 rows” / “sees nothing” without a known-firing
  neighbour in the same session (`INTEGRATIONS.md:192`).
```

Why: those five sentences are the measured selector misses and
the measured dig-skip of one day. The skill already says
“Believe it’s there and find the path” and “Copy a working
pattern.” This patch names the tokens this lane minted
(`keys: […]`, `customType.data`, `extension-authoring`,
neighbour).

### Patch 4.7 — Hard rule 5, operationalized

Keep hard rule 5’s “official authoring page + one public
example package.” Name the page:

```markdown
5. **Copy a working pattern before inventing.** Official
   authoring page first — for omp that is
   https://omp.sh/docs/extension-authoring — plus one public
   example package (`hello-extension` or in-tree
   `omp-harm-rule` / `omp-jev-observer`). A 0-row live defect
   is not how you learn `pi.on` / `omp.extensions` /
   `--extension`.
```

### What this pass does not patch

- Invented STOP / DEFER / quiet-window (Pass 1 / PR #9).
- Narrow-kill card / unscopeable never-call (Pass 2 / PR #10).
- Documented `--projectId=` / inject-or-HALT (Pass 3 / PR #11).
- Paperwork, live-proof operationalization, invented
  `?? 'unknown'`, tool playbook holes beyond E/K
  (Passes 5–7).
- The Jeffrey-voice essay (Pass 8).
- A planted-negative gate that fails when someone claims
  absence without `keys()`. Named as the next product tick;
  not this PR.
- Worked install transcripts for `omp-jev-observer` /
  `omp-harm-rule` (pack G5 reserved those for a later pass).
- Any edit to the uploaded skill file in this turn; the
  patches are proposed text for a later house-skill land.
- A live dual-shape omp session read on this VM. `readRow`’s
  offline test exists; live proof is NOT_RUN.

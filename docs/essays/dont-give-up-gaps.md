# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure modes 4 and 5: **selector
narrower than the claim** and **ask instead of dig**).
Pass date: 2026-09-19. Lane: offline file search + quote verification on
`ad765b0`. No live Jev calls. No secret values printed.

The local evidence pack's "Suggested feed" mapped G5+G6 to a later pass.
This packet assigned them to **Pass 4** after named-hole-then-park landed
as Pass 3 ([PR #11](https://github.com/JYeswak/jev_playground/pull/11)).
Do not re-number; the prior PRs already occupy 1–3.

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

Required surfaces, exact commands, 2026-09-19 on `ad765b0`. Empty
results are listed, not inferred.

```bash
# G6 — eighth / ninth / tenth wrong-selector
# (R41 wraps ninth in **ninth**; do not require the bare adjacency)
rg -n 'eighth wrong-selector|\*\*ninth\*\* wrong-selector|A \*\*tenth\*\*|customType.data|Keys present' \
  NEGATIVE_EVIDENCE.md work/oracle-kit/index.mjs
# HIT: NEGATIVE_EVIDENCE.md:1448  eighth wrong-selector failure today
# HIT: NEGATIVE_EVIDENCE.md:1749  customType.data, not top-level data
# HIT: NEGATIVE_EVIDENCE.md:1752  **ninth** wrong-selector failure
# HIT: NEGATIVE_EVIDENCE.md:1756  **tenth** followed immediately
# HIT: work/oracle-kit/index.mjs:121  Keys present: [${Object.keys...}]
# ALSO: NEGATIVE_EVIDENCE.md:1457  eight times in one session (prose, not this pattern)

# requireKey / inspectKey / readRow
rg -n 'export function requireKey|export function inspectKey|export function readRow|BOTH omp' \
  work/oracle-kit/index.mjs work/jev-client/src/index.ts TESTS.md \
  work/jev-client/test/client.test.mjs
# HIT: oracle-kit/index.mjs:116,127
# HIT: jev-client/src/index.ts:136  readRow
# HIT: TESTS.md:28-31 requireKey after the eighth
# HIT: TESTS.md:46 readRow BOTH omp session row shapes (pack :45 @ f8a8dc9)
# HIT: jev-client/test/client.test.mjs:109  both shapes + neither-shaped RED

# Same class, earlier: guessed SDK fields
rg -n 'distribution|probability vs|\.noul|role.: .toolResult' \
  docs/demos/SDK-SURFACE.md NEGATIVE_EVIDENCE.md
# HIT: SDK-SURFACE.md:17-19  .distribution vs .probabilities; spaced toolResult
# HIT: NEGATIVE_EVIDENCE.md:1455-1456  same three named in R33-CORRECTION

# G5 — silent pi.on / 0-row / loader globs / neighbour
rg -n 'Silent-register|pi.on|loader globs|known-firing neighbour|0-row defect' \
  docs/INTEGRATIONS.md docs/demos/upstream-repro/harm-rule-shipped-20260919.md
# HIT: INTEGRATIONS.md:56-59  Silent-register; no pi.on; co-presence bar
# HIT: INTEGRATIONS.md:48     loader globs *.{ts,js}
# HIT: INTEGRATIONS.md:167-172 zero-row cause = missing pi.on
# HIT: INTEGRATIONS.md:181    0-row defect was seen on jev-lab
# HIT: INTEGRATIONS.md:192    known-firing neighbour, never silence alone
# HIT: harm-rule-shipped-20260919.md:71-74  lost pi.on; node --check passes

# Official URL is NOT cited outside this pass's essays (the missed dig)
rg -n 'omp.sh/docs/extension-authoring|extension-authoring' \
  docs/ work/ README.md --glob '!docs/essays/**'
# EMPTY on ad765b0 excluding these two essay files — the official
# page was never opened from the rest of the tree
```

`rg` empty for `extension-authoring` outside `docs/essays/` is the
G5 finding, not a search failure. Playbook E already names
`…/docs/extension-authoring`. The lane reinvented loader / `pi.on`
/ `extensions:` via live 0-row defects instead.

---

### G6 — Selector narrower than the claim (8–10×)

Pack G6. Taxonomy #4 (selector narrower than the claim).

**(a) Evidence.**

R33 published “the extension cannot explain its own output” after a
failed `toolCallId` join (`js-bash-*` vs `call_…|fc_…`). The
`harm-rule.decision.v1` rows already carried `command`. Dumping
`keys()` would have shown it
(`NEGATIVE_EVIDENCE.md:1423-1428,1448-1458`). That was the **eighth**
wrong-selector of the session and the only one that reached a published
receipt.

`requireKey` / `inspectKey` landed after that eighth
(`work/oracle-kit/index.mjs:116-129`; `TESTS.md:28-31`; commit
`63f052c`). The helper throws with the record’s own key list, so
absence cannot be claimed without having been shown what *is* present.

R41 is the **ninth**, in the author’s own hands, hours later, from
code that never imported `requireKey` (`NEGATIVE_EVIDENCE.md:1752-1754`).
A live Jev call sat at `customType.data`; a top-level `data` scan
returned `{}` and read as “0 rows with real probabilities.” The row
was `flag 0.04 / pass 0.96`, `error: null`, `378ms`. A **tenth**
followed on the same nested shape; the author refused to publish the
tally rather than print a number the selector could not classify.

The same class, earlier the same day (`docs/demos/SDK-SURFACE.md:17-19`;
named again at `NEGATIVE_EVIDENCE.md:1455-1456`):

| selector used | field that was there | what “0 hits” fabricated |
|---|---|---|
| `.distribution` | `.probabilities` | AUC exactly 0.500 on three router runs |
| `.probability` | `.noul` | Python probe crash |
| `"role": "toolResult"` (spaced) | `"role":"toolResult"` | “omp does not persist tool results” |

`readRow` exists because one-shape scanners are this defect
(`work/jev-client/src/index.ts:127-159`; `TESTS.md:46`;
`work/jev-client/test/client.test.mjs:109-120`). Shape A
(`customType` object, nested `data` — observer rows) and shape B
(`customType` string, top-level `data` — harm-rule / failure rows)
are both live. A reader that handles one reports “no rows” on the
other. That silent empty is indistinguishable from absence — R33 and
R41’s root cause, named in the function comment.

**(b) Why this is selector-narrower-than-claim.**

Skill failure mode 4: “wrong field, file, session, or row type → false
contradiction → quit.” Checklist item “Did I verify selector ≡ claim?”
is a reminder. Eight repetitions, then a ninth from code that never
imported the helper, means the reminder is not the fix.

Playbook K already says “Selector says 0, author says N → broaden
selector (diagnostics + decisions).” It does not require `keys()` /
`requireKey` before the absence sentence. That is the hole.

**(c) Forward move — `keys()` / `requireKey` before any absence claim.**

Before writing “missing”, “0 rows”, “cannot attribute”, or “not there”:

1. **Dump the record’s own keys.** `Object.keys(record)` or
   `inspectKey(record, name).keys`. If you have not printed the key
   list, you have not claimed absence.
2. **Read through `requireKey` / `readRow`.** `requireKey` throws with
   the key list (`oracle-kit/index.mjs:116-123`). `readRow` accepts
   both omp session shapes (`jev-client/src/index.ts:136-159`). A
   hand-rolled `row.data` or `row.customType.data` is the ninth
   instance waiting to happen.
3. **Name both wire shapes** when the claim is about omp session
   rows. Shape A (nested) and shape B (flat) are both current.
   One-shape green is not a zero-row finding.
4. **Refuse to publish** a count your selector cannot classify
   (R41’s tenth — the one honest move in that pair).

A selector that returns nothing is indistinguishable from a thing that
is not there. That sentence is already in R33-CORRECTION. The skill
must make the key dump mandatory, not advisory.

Do not land a new planted-negative gate in this PR. Name it: claim
absence without `keys()` / `requireKey` → RED. That is a later
product tick, not this pass.

---

### G5 — Missed official extension-authoring dig → 0-row / silent-register

Pack G5. Taxonomy #5 (ask instead of dig) plus the skill’s own tool
playbook hole (playbook E names the page; agents still hand-rolled).

**(a) Evidence.**

Playbook E already says: official docs first
(`…/docs/extension-authoring`), then registry, then one public GitHub
example, then local copies. The real URL is
https://omp.sh/docs/extension-authoring. On `ad765b0`,
`rg -n 'extension-authoring'` over `docs/` `work/` `README.md`
excluding `docs/essays/` is **empty**. The page was not opened
from the rest of this tree.

What the lane did instead: reinvent loader / `pi.on` / `extensions:`
via live 0-row defects.

- `docs/INTEGRATIONS.md:56-59` — silent-register rule, written after
  the fact: valid syntax + no `pi.on` registers nothing;
  `node --check` passes; indistinguishable from “sees nothing.”
- `docs/INTEGRATIONS.md:167-172` — the zero-row vs 1 bridge-row
  report was a missing `pi.on` line, reproduced and repaired
  (`harm-rule-shipped-20260919.md`, `658922f`). Loader globs
  `*.{ts,js}`; config is `extensions:` in
  `agent/config.yml`.
- `docs/INTEGRATIONS.md:192` — neighbour co-presence is the bar:
  0 rows while another extension writes rows means *not loaded*,
  not “the hook is quiet.”
- `harm-rule-shipped-20260919.md:71-74` — the same silent-zero-row
  defect reproduced by losing `pi.on` during editing. Diagnosed via
  a tsx import probe, not the official page.

The official page already states the ship shape the lane excavated:
default export `(pi) => …`, `omp.extensions` / `pi.extensions`,
`omp plugin install`, `omp --extension <path>`, directory scan
limited to `.ts`/`.js`. In-tree copies already match
(`harm-rule.ts:27-32`, `observer.mjs:50-53`). Asking “how do I
register an extension?” after those bytes exist is ask-instead-of-dig.

**(b) Why this is ask-instead-of-dig.**

Skill failure mode 5: ask the user for an example that already lives
in official docs, a marketplace, GitHub, or prior sessions. Hard rule
3: two-minute dig before “missing.” Hard rule 5: copy a working
pattern before inventing — official authoring page + one public
example package.

Playbook E names the path. Agents still skipped it and paid in
0-row archaeology. The skill’s E block needs a 30-second checklist
with the **real URL** and a neighbour-co-presence stop, or the next
agent will hand-roll again.

**(c) Forward move — 30-second checklist.**

Before writing a new omp extension, or claiming “zero events” /
“not loaded” / “how do I register this”:

```text
30s — extension-authoring (do not skip)

[ ] 1. Open https://omp.sh/docs/extension-authoring
       Confirm: export default function (pi) { pi.on(...) }
                package.json  "omp": { "extensions": ["./src/index.ts"] }
                (legacy "pi.extensions" still accepted)
                install: omp plugin install <path|git|npm>
                         or omp --extension /absolute/path
[ ] 2. Copy one working package — official hello-extension
       (oh-my-pi docs/skills/examples/hello-extension/)
       or in-tree work/omp-harm-rule/harm-rule.ts:27-32
       / work/omp-jev-observer/src/observer.mjs:50-53.
       Do not invent a second factory shape.
[ ] 3. Prove load against a known-firing neighbour before
       claiming zero events. Same session, same profile:
       neighbour writes a row (dcg-tool-bridge / harm-rule)
       AND this module writes a row. Silence next to a firing
       neighbour = not loaded (missing pi.on, glob miss,
       not on the extensions: list). Silence alone is not a
       finding (INTEGRATIONS.md:192).
[ ] 4. Mechanical checks, 10 seconds:
       - default export is a function, not an object
       - pi.on(...) still present (node --check will not catch a
         lost line; INTEGRATIONS.md:56-59)
       - filename matches loader glob *.{ts,js}
       - profile agent/config.yml lists it under extensions:
       - isolated path first: omp --no-extensions --extension=<one>
```

If box 1 is unchecked, “no examples” / “how do I build this” is
forbidden. If box 3 is unchecked, “0 rows” is forbidden.

Do not add the worked `omp-jev-observer` / `omp-harm-rule` install
transcript in this PR. Pack G5’s own forward said that is Pass 5.
This pass lands the checklist and the URL.

---

### Adjacent quotes (not expanded)

`compaction/src/omp-adapter.ts:59-68` — two live *envelopes*
(`message_end` stream vs `message` SessionEntry), same payload.
Before the second envelope was accepted, a real session adapted to
**zero messages** (R23). Same failure class as `readRow`’s two
*row* shapes; different layer. Listed so a later pass can join
them. Not a third GAP.

`docs/demos/SDK-SURFACE.md:17-19` — the three guessed-field
selectors named in R33-CORRECTION. Evidence for G6, already quoted
in the table above. Not expanded into a separate section.

`NEGATIVE_EVIDENCE.md:1767-1769` — if an eleventh wrong-selector
occurs, `requireKey` cannot be adopted voluntarily and the
inspection path itself must be the only way to read these files.
Retry condition, not a new gap.

---

### What this pass is not claiming

- That `requireKey` is used at every read site. R41 proved it is
  not. This pass makes the dump mandatory in the skill, not in
  every caller.
- That both omp row shapes have been re-proven live on this VM.
  `readRow`’s test is offline (`client.test.mjs:109-120`).
  Live dual-shape proof is NOT_RUN here.
- That https://omp.sh/docs/extension-authoring was fetched as
  rendered HTML on this VM. The URL is the official page; the
  factory / `omp.extensions` / `--extension` contract is also in
  the oh-my-pi authoring skill. This pass cites the URL the
  lane skipped; it does not re-host the page.
- Invented STOP-LIVE (Pass 1 / PR #9), the tool_call over-learn
  (Pass 2 / PR #10), or named-hole-then-park (Pass 3 / PR #11).
- Pack G7 / G8 / G10. Pass 5 is not started.

### Next lever (Pass 4 close)

Land the skill patches (`keys()` / `requireKey` before absence;
30-second extension-authoring checklist with the real URL and
neighbour co-presence). The next *product* tick this pair blocked
is a planted-negative: claim absence without a key dump → RED.
Do not start Pass 5 in this PR.

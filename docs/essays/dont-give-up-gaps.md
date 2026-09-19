# Don't Give Up — Gaps

Skill under audit: `dont-give-up` (failure mode 2: **over-learned kill**).
Pass date: 2026-09-19. Lane: offline file search + quote verification on
`ad765b0`. No live Jev calls.

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
Rerank’s cell is the narrow-kill done right: *yes, **one** question —
measurement killed the other two*.

An agent who opens INTEGRATIONS first — the page AGENTS.md and the
README both point at — sees only RULE WINS. That is the over-learn
as a missing column, not as a sentence.

**Forward.** Add the still-call rows (or a `calls Jev?` column) to the
INTEGRATIONS scoreboard, each with its own narrow-kill card. Do not
do that rewrite in this pass; name it.

#### Hero line collapses five independent kills into “no Jev”

`README.md:9-10`:

> **We set out to wire Jev into omp and shipped FOUR REGEXES WITH NO
> JEV CALL IN THEM.** Five surfaces, five cheap wins (cost-benefit,
> not capability)

`docs/INTEGRATIONS.md:21` repeats the five-surfaces line immediately
under a heading that is about `tool_call` only (`:18`).

The five wins are five *different* surfaces with five *different*
substitutes (`README.md:11-14`): (1) phishing domain regex, (2) flat
mid-tier pricing, (3) prompt length on tier choice, (4)
keep-everything on compaction, (5) four regexes on tool-call harm.
Each is a valid narrow kill. The hero line makes them one “no Jev
call” story. An agent who stops at the bold sentence never reaches
the six-extension table 240 lines later that still calls the model
on four packages.

**Forward.** Hero / TL;DR sentences that mention a kill must carry
the surface token. “Four regexes, no Jev call on `tool_call`” is the
honest compression. “No Jev call in them” plus “five surfaces” is
the over-learn.

#### “Where a judge belongs” cites only the drop

`docs/INTEGRATIONS.md:203`:

> **Where a probabilistic judge belongs.** Only on what regex cannot
> express. Measured on this surface: the classifier wins and Jev is
> dropped

The first sentence is the rule. The second sentence is only the
negative example. The positive examples are already shipped
(`omp-jev-review`, `omp-jev-rerank`’s surviving `ordered` question,
`omp-jev-failure`) and uncited on that page.

**Forward.** The same paragraph must name one still-calling sibling
or it will be read as “belongs nowhere.”

---

### Narrow-kill done right (positive controls — not defects)

These are in-repo proofs that a kill *can* stay narrow. They are the
shape the skill should copy, not further GAPs.

**Rerank killed two questions and kept the third.**
`work/omp-jev-rerank/README.md:13-27` — `definitional` constant-no,
`noise` constant-yes, `ordered` 4/4 and moving. The package still
imports `askJev` (`src/index.ts:22,94-96`). A question-level kill
did not become a package-level ban and did not become a fleet ban.

**Preaction names the arm.**
`work/omp-jev-preaction/src/index.ts:4`:

> Never calls Jev on this arm (cost-benefit: regexes beat the model here).

“This arm” is the surface token. The cheaper substitute is the seven
`policy.json` regexes (`README.md:3-5,17`). It is not the harm-rule
kill leaking; it is a second measured gate with its own substitute.

**Review’s header exists because the over-learn was predicted.**
`work/omp-jev-review/src/index.ts:4-11` is titled *WHY THIS ONE CALLS
JEV, WHEN omp-jev-harm AND omp-jev-preaction DO NOT.* The skill
failed if an agent can quote RULE WINS and not this header.

---

### Adjacent quote (not expanded)

`docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md:60-62,100-102` — “this
lane does not ship Jev-free tools” / demo-1 “no Jev-free demos.” That
is the *inverse* over-learn (a no-Jev demo-shape kill reused as “must
call Jev or it is not lane work”). Different direction from G2.
Listed so Pass 3+ can find it. Not this mission.

---

### What this pass is not claiming

- That the tool_call / harm-rule kill is wrong. 12/12 vs 11/12 at
  FP 0/38 on a held-out split neither scoring pane authored is still
  the receipt. Narrow it; do not reopen it.
- That review / rerank / failure / observer are promoted. README
  `calls Jev? = yes` is a wiring fact, not a rung-5.
- That “five cheap wins” are false. Each win is a named surface with
  a named substitute. The defect is collapsing them into one “no Jev”
  hero line.
- That INTEGRATIONS invented STOP-LIVE (Pass 1 / PR #9).
- Pack G3–G8 / G10.

### Next lever (Pass 2 close)

Land the narrow-kill card on the skill (see
`docs/essays/dont-give-up-skill-patches.md` Pass 2). The next
*product* tick this over-read blocked is one quoted live row from a
surface the card marks `still-calls-Jev-elsewhere` — review,
rerank, or failure — not another RULE WINS sentence. Do not start
Pass 3 in this PR.

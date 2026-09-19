# Don't Give Up — Skill patches

Patches for the `dont-give-up` skill, derived from lane evidence.
Do not apply these to any JSM-owned copy; house lessons stay in house skills.

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

Why: pack G2. `docs/INTEGRATIONS.md:18,40-41` already has surface +
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
  follows missions).
- The inverse over-learn (“this lane does not ship Jev-free
  tools”, `RUNG2_COD-H3_resolved_MU.md:60-62`). Different
  direction; listed in the Pass 2 gaps essay, not patched here.
- The Jeffrey-voice essay (Pass 8).
- Any edit to INTEGRATIONS / README scoreboards in this turn;
  those are named product ticks, not this PR.
- Any edit to the uploaded skill file in this turn; the patches
  are proposed text for a later house-skill land.

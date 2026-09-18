# Duel 1 — duelist A (Claude): 15 ideas, winnowed to 5

Ground rules I held myself to: every idea cites a `USAGE-MAP.md` section; no source outside this
tree; nothing that re-proposes shipped work (the compaction hook, `replay.ts`, and the resume-quality
A/B exist — §14 work is **extended**, never re-listed); each survivor states how it installs, how it
is tested including RED arms, who uses it, why it beats the obvious alternative, and its ship
criteria.

**What I read first, and the two numbers that shaped the ranking:**

- `compaction/runs/replay-big-20260917.json` — 179 events → 24 messages; the library took 13 → 8
  messages and 2333 → 1292 chars (**45% reduction**), `kept: 0`, `resultsTrailing: 0`,
  `failures: []`. Pruning works mechanically and loses no text it keeps.
- `compaction/runs/ab-20260917.json` — schema `jev.resume-quality-ab.v1`, `liveCalls: 4`,
  `jevRequests: 1`, **3** recall questions (`q1`,`q2`,`q3`), **`armA.score: 1` vs `armB.score: 3`**,
  `verdict: "B wins"`, at `armA.contextBytes: 4188` vs `armB.contextBytes: 1241`. **The
  preserve-instructed summary scored 3/3 and Jev pruning scored 1/3, on a third of the bytes.**
  > CORRECTED after pane 3's cross-score (`WIZARD_SCORES_MU_ON_CC.md`, `ad99a27`): I first wrote
  > "4 recall questions" and "3–1", conflating `liveCalls: 4` with the question count. The receipt
  > has three questions. The corrected reading is **worse for my own argument** — arm B was
  > perfect, not merely ahead.

That second receipt is the most valuable thing this lane owns, because it is the one place the
evidence went *against* the capability we are mid-way through wiring. Every ranking below is driven
by one question: **does this demo change a decision we are actually about to make?**

---

## The 15 (one line each, with the section they stand on)

| # | Idea | Map § | Why it made the long list |
|---|---|---|---|
| 1 | Fact-ledger companion for pruned context, re-scored on the existing A/B | §14 | turns our one negative result into a decidable question, on a harness + fixture we own |
| 2 | Claim-check pre-commit lane (numbers in a message vs the receipt they cite) | §2 | this lane asserts numbers constantly and verifies none of them mechanically |
| 3 | Routing backtest over **our own** omp session logs | §4 | upstream measured −60% on 237 turns of *their* traffic; our logs already exist |
| 4 | Signals-not-verdicts classifier starter (+ calibration report) | §9, §13 | 62.6% verdict vs 95.1% from 5 signal questions — the most transferable measured lesson in the map |
| 5 | Context-admission screen hook (files, fetches, pastes) | §1, §12 | injection caught at 0.99 *while still reading the page as a real page* |
| 6 | Foreman-lite completion judge wired to our bead close path | §6 | our `close-evidence-gate` checks a close_reason's form; nothing judges its substance |
| 7 | Portable calibration micro-harness, packaged out of `foundation/` | §13 | everyone shipping a Jev threshold needs it; nobody has it |
| 8 | Policy-gate template: Score/Noul → allow/confirm/block/warn/steer in code | §11 | the single most reusable shape; thresholds and fail-safe side named |
| 9 | BM25 → Jev-rubric rerank recipe with a measured slice | §3 | nDCG 0.692 vs 0.691 at $0.45 vs $2.51/1k, better on negation |
| 10 | commit-miner sweep over the ~20 vendored clones before we depend on them | §8 | we read other people's code daily and never triage its history |
| 11 | Blind injection/vuln corpus as an L3 proof surface for our hooks | §12 | 662 deepset msgs + 200 vuln pairs, blind — the honest L3 arm |
| 12 | Failure-attribution probe for our own failed runs | §7 | Who 73.4 / When 76.4, $1.28 total, input-billed only |
| 13 | Zero-label triage for inbound issues/support text | §9 | TF-IDF needed 100–10k labels; 20+ points behind under shift |
| 14 | Structured extraction + verification pass over receipt JSON | §2, §9 | receipts are the lane's currency and nothing parses them |
| 15 | Skill-router advisory surface for omp sessions | §3 | skillranker is the pattern wired to live session context |

**Cut, with the reason** (a duel should see what I discarded): **#11** is infrastructure for #5, not a
demo — folded in as its L3 arm. **#13** and **#14** are weaker framings of #4 and #2 respectively.
**#15** is blocked, not unpromising: `EVAL.md` §7 records that we mined only skillranker's AGENTS.md,
read no source, made no live call, and pinned a moving repo — promoting it would be shipping on an
unread source. **#9** needs a first-party retrieval surface with gold labels, which we do not have.
**#12** has an honest ceiling (All = 31.3) that makes it a triage *hint*, not a verdict — worth
building, not worth building first. **#6**, **#7**, **#8**, **#10** are all real and all survive to
the next duel round; they lost only on "does it change a decision this week".

---

## The 5, best → worst

### 1. Fact-ledger companion — make pruning win the A/B, or kill it with a number

**Stands on:** §14 (standing lesson: "relevance-pruning loses verbatim recall; pair with fact ledger
or yield to summarization for fact-dense transcripts") and our two receipts above.

**The claim under test:** Jev pruning scored 1/3 on fact recall *because it drops the bytes that
carried the facts*, not because pruning is wrong. So: build a **byte-exact fact ledger** (the
quoted lines that answer "what is the value of X" — ports, paths, ids, versions), append it to the
pruned context, and re-score **the same three questions on the same fixture**. Either
`armA+ledger` beats `armB` at comparable bytes, or pruning is the wrong tool for fact-dense
transcripts and demo-1 ships summary-first.

**MECHANISM, named after pane 3's hit — this was the file's real defect.** I wrote "with a
Noul/Choice pass", which is not a mechanism: **a Noul judges, it does not extract.** The extraction
step is deterministic and Jev only verifies it:
1. A deterministic extractor proposes candidate lines (regex/structural: `key: value`, port/path/id
   shapes) from the *dropped* messages — no model involved, so the quote is byte-exact by
   construction rather than by promise.
2. **Choice** over those candidates answers "which of these lines states the value of X", one
   question per fact slot. Choice returns a member of a supplied set, so it cannot paraphrase.
3. **Noul** verifies each survivor: "this quoted line appears verbatim in the source message."

**The installable thing:** `jev-fact-ledger` — a module plus a CLI emitting
`{quote, sourceMessageId, byteRange}[]`. Extends `compaction/src/`.

**Second concession:** I wrote that it "reuses `compaction/ab/run-ab.ts` **unchanged** as the
scorer, and emits a third arm into the existing schema." Pane 3 is right that those cannot both
hold — an unchanged scorer cannot emit a new arm. Resolution: the scorer takes the third arm as
*data* (an `armC` config entry, a small change to it, honestly declared) **or** it stays unchanged
and the ledger arm runs as a second invocation whose receipt is merged after. Pick one in the plan;
do not claim both.

**Who uses it:** our systems, immediately — it is the blocker on whether the compaction hook ships
fleet-wide. Then the AI space, because §14's lesson is upstream's too and nobody has published the
fix.

**Why it beats the obvious alternative:** the obvious alternative is "just summarize" (arm B, which
already won). But a summary is *generated text* — the one thing Jev deliberately does not do, and
the thing that can silently invent a port number. A ledger of byte-exact quotes cannot paraphrase.
The demo's value is that it makes "prune + quote" vs "summarize" a measured choice rather than a
taste one.

**Tests, with RED arms:**
- *Trigger:* a fixture where the answer-bearing line is present but the ledger omits it ⇒ recall
  question fails and the harness reports the miss (proves the scorer is actually reading the ledger).
- *Trigger:* a ledger entry whose `quote` is not byte-identical to its `sourceMessageId` span ⇒
  **refuse** (a paraphrase in a fact ledger is the failure mode; it must be structurally impossible
  to ship one).
- *Satisfying:* the four existing questions, with the ledger, score ≥ arm B's 3 — and if they do not,
  that is a publishable result, not a failure of the demo.
- Offline throughout with an injected asker; exactly one budgeted live run for the scored arm.

**Ship criteria:** install script (`npm run fact-ledger` + the CLI bin); deterministic tests incl.
both RED arms; receipt `compaction/runs/ab-<ISO>.json` with the third arm and the transcript sha;
`EVAL.md` row naming the rung and the verdict either way.

---

### 2. Claim-check pre-commit lane — verify the number, not the format

**Stands on:** §2 (`jev_verify` caught a contradicted claim at **confidence 1.0** against a city
ordinance).

**The gap it closes:** this lane already refuses a commit subject with no verification level, and
`close-evidence-gate` already requires a close_reason to *carry* proof. Both check **form**. Nothing
checks whether "8/8 witnesses", "45% reduction", or "ECE 0.061" in a message actually matches the
receipt it cites. Measured this session: four of my own findings were instrument errors that read as
confident claims. This is the mechanism for that class.

**The installable thing:** a third `githooks/pre-commit` lane. It extracts `(number, unit, cited
artifact)` triples from the staged commit message, loads each cited artifact (a `runs/*.json`, a gate
output, a test count), and asks Jev to verify the claim against that evidence. Refuses on a
contradiction; silent when every claim checks out or when no claim cites an artifact.

**Who uses it:** us, on every commit — and it is the most exportable piece of lane discipline we
have, because "the commit message says a number the artifact does not" is universal.

**Why it beats the obvious alternative:** the obvious alternative is a regex that greps the number
out of the JSON. That works only when the message and the receipt use the same words — it cannot tell
that "8/8 witnesses" corresponds to `"witnesses": {"passed": 7, "total": 8}`, and it silently passes
when it finds nothing. Jev checks a *claim against evidence*, which is exactly §2's measured shape,
and the fail-safe side is ours to set.

**Tests, with RED arms:**
- *Trigger:* a message claiming `8/8` against a receipt showing 7 ⇒ refuse, naming both numbers.
- *Trigger:* a message citing an artifact that does not exist ⇒ refuse (never "no claims found").
- *Satisfying:* a truthful message ⇒ exit 0, no output. Five healthy commit shapes, as the
  staged-deletion lane already does.
- *Fail-safe:* no key or API unreachable ⇒ `CLAIM_CHECK_SKIPPED` with a named reason, exit 0. A
  pre-commit lane that blocks the fleet when a paid API is down is not shippable.
- Offline: an injected asker with recorded verdicts; the live arm is opt-in.

**Ship criteria:** install via the existing `githooks/` + `core.hooksPath` path (no new mechanism);
tests incl. both RED arms and the skip path; receipt `runs/claim-check-<ISO>.json` of a real pass
over the last N commits; `EVAL.md` row with the false-positive rate over that window.

---

### 3. Routing backtest over our own omp logs — the money one

**Stands on:** §4 — `jev-codex-router@8292b51` measured **−60% vs full-frontier on a 7-day replay of
237 real turns**, at `$0.00003` and `0.6s` per decision, fail-open with a kill switch and a local
decision log.

**The installable thing:** `jev-route-backtest` — point it at `~/.omp/profiles/<p>/agent/sessions/*.jsonl`,
replay each turn through the tier Choice, and emit what routing *would* have spent versus what we
actually spent, plus a per-turn decision log for calibration. Read-only; it never routes anything.

**Who uses it:** us. Three panes per session, all on a frontier model. This is the only demo on the
list that pays for itself in dollars we can name, and the input already exists on disk.

**Why it beats the obvious alternative:** the obvious alternative is "put the cheap model on the
cheap panes", decided by vibe. The backtest answers it per turn on our actual traffic, and it is
strictly safer than upstream's live router because it starts read-only: we learn the saving before
anything is rerouted. Upstream backtested *their* 237 turns; the question "what would it save **us**"
is unanswered and is one harness away.

**Tests, with RED arms:**
- *Trigger:* a synthetic log where every turn is hard ⇒ savings ≈ 0 and the report says so (no free
  lunch); if it reports a saving there, the estimator is broken.
- *Trigger:* a log of all-trivial turns ⇒ savings near the theoretical max.
- *Trigger:* a malformed session line ⇒ counted as `UNPARSED` in the denominator, never dropped
  silently (an empty scan set is an ERROR).
- *Satisfying:* a real 200+ turn window replays with a stable total across two runs (determinism),
  and the per-turn log lets a human spot-check ten decisions.
- Offline by construction: decisions come from recorded Jev answers in the fixture; the live arm
  is one budgeted pass to confirm the recorded answers still hold.

**Ship criteria:** install script (`uvx`/`npx` single bin); tests incl. the three RED arms and the
determinism check; receipt `runs/route-backtest-<ISO>.json` with turn count, saved $, and model
versions; `EVAL.md` row with the window and the boundary (what traffic was *not* replayed).

---

### 4. Signals-not-verdicts classifier starter

**Stands on:** §9 — `jev-phishing-bench@1d56e8c`: Jev's **verdict alone loses** (62.6 vs 81.3), but
**5 signal questions → logistic regression hits 95.1%**, AUROC 0.988, ECE 0.027; and a *fixed rule on
one strong signal* (free hosting) alone gets 89.5%. Plus §13 for the calibration report.

**The installable thing:** a template repo/scaffold: bring a labelled CSV, declare 3–7 **signal**
Nouls (not a verdict), and get (a) a fitted tiny model *and* (b) a no-fit fixed-rule baseline, with a
calibration report (ECE, bins, flip rate between passes) and a held-out score.

**Who uses it:** the AI space first — this is the question every team asks in week one ("can Jev do
my classification?") and the measured answer is "not the way you are about to ask it". Us second, for
any triage surface we build later.

**Why it beats the obvious alternative:** the obvious alternative — ask Jev "is this X?" and threshold
the answer — is *measurably 33 points worse* on the in-tree corpus. The template's whole thesis is
that the obvious thing loses, and it ships the comparison so the user sees it on their own data.

**Tests, with RED arms:**
- *Trigger:* run the template's own verdict-only baseline; if it does **not** lose to the signal
  model on the shipped fixture, the template refuses to report (its thesis is falsifiable and it
  checks itself).
- *Trigger:* a deliberately miscalibrated probability column ⇒ the ECE gate fails.
- *Trigger:* fewer than the declared minimum labelled rows ⇒ ERROR, never a confident score on 12
  examples.
- *Satisfying:* the shipped fixture reproduces a published-shape result (signal model > verdict,
  ECE under threshold) offline from recorded answers.

**Ship criteria:** install script (`uvx jev-signals init`); tests incl. all three RED arms; receipt
per run with fixture sha + model version; `EVAL.md` row; README citing
`jev-phishing-bench@1d56e8c` and `jev-spam-eval@76ef183` with their licenses.

---

### 5. Context-admission screen hook

**Stands on:** §1 — `jev_screen` blocked a pricing page carrying a hidden "ignore your instructions"
note at **injection probability 0.99 while still reading it as a real page**; and §12 for the blind
corpus (`jev-sec-bench@fdb16b9`: 662 deepset injection messages + 200 vuln-code pairs).

**The installable thing:** an omp hook on the read/fetch path plus a `jev-screen` CLI, judging bytes
**before** they enter context. Shadow first: it logs a verdict and never blocks until the
false-positive rate is measured on our own traffic.

**Who uses it:** our systems. Every pane reads URLs, docs, and pasted output all day; this is the one
attack surface where a wrong answer is not merely expensive.

**Why it beats the obvious alternative:** a denylist or regex faces the exact case §1 measured — the
malicious instruction was *inside a legitimately useful page*. A pattern guard must either block the
page (losing the content) or miss the note. A screen that returns "real page, injection 0.99" lets
code make a graded decision, which is the whole §11 shape.

**Tests, with RED arms:**
- *Trigger:* a held-out slice of the 662 deepset messages ⇒ flagged above threshold. This is a
  **blind** arm: the slice is not the slice used to pick the threshold.
- *Trigger:* the §1 shape specifically — a benign page with an embedded instruction ⇒ flagged as
  injection **and** classified as a real page (both, or the demo is a page-blocker, not a screen).
- *Satisfying:* a corpus of ordinary docs ⇒ silent, with the false-positive rate reported as a
  number.
- *Fail-safe:* declared **advisory/fail-open** in shadow, and the enforce flip is a separate,
  human-approved change with its own receipt.

**Ship criteria:** install script; tests incl. the blind arm and the FP-rate report; receipt with the
corpus slice sha, threshold, and per-class counts; `EVAL.md` row naming the rung (shadow = L3 at
best) and the cost per screened read — because this one runs on *every* read and cost is part of
whether it can ship at all.

---

## Why this order

1. **#1** is the only idea that changes a decision already in flight (does demo-1 ship?), and it
   reuses a fixture, a scorer, and a schema we already own. Highest information per unit of work.
2. **#2** attacks this lane's own demonstrated failure mode with a capability measured at confidence
   1.0, on a mechanism (a pre-commit lane) we have already installed twice and proven in both
   directions.
3. **#3** is the largest measurable saving with the smallest risk (read-only) and inputs already on
   disk. It ranks below #2 only because it optimizes cost rather than correctness.
4. **#4** is the strongest *outward* artifact: it encodes the most counterintuitive measured lesson
   in the corpus and its RED arm is its thesis.
5. **#5** has the highest ceiling and the highest blast radius — it runs on every read and can block
   context admission. It ranks last of the five deliberately: it should ship after #2 has taught us
   what a live per-event Jev lane costs in practice.

**Standing bias I am declaring, since another model is about to attack this:** I have weighted
*decisions we are about to make* over *artifacts the AI space would applaud*. A duelist could
reasonably invert #4 and #1 — #4 has a larger audience and a cleaner story, and #1's payoff might be
"pruning loses, ship summary-first", which is a smaller headline even though it is the more useful
answer. If the attack lands, take #4 first.

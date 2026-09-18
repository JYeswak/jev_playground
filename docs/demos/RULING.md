# RULING — which ideas deserve their own deeply-planned project, and the evidence for the rest

**Derived 2026-09-18 from `docs/demos/STATUS.tsv`, not from prose.** Every candidate below cites a
receipt that `scripts/lane-status.sh` verifies exists on disk; the script exits 3 if any does not.
Reasoning lives in `docs/demos/PLAN.md`; refutations live in `NEGATIVE_EVIDENCE.md`.

**State at ruling: 17 candidates · RULED_OUT 4 · CLEARED 5 · HELD 8 · PROMOTED 0.**

---

## THE RULING

**Two candidates earn their own deeply-planned project. Neither earns a build first.**

### 1. COD-H2 pre-action abstention — **first phase: SPECIFICATION**

**It cleared more of this gauntlet than anything else and every clearance was signed by a
non-author.** Blind demand **905** (top of 17). Rung-2 structure against a **shipped** incumbent
proven **binary** by source-read — `AutoModeMiddleware`'s own docstring: *"it does not request human
approval"* (§3u). Rung 3 **in full**: real client that exits **`rc2` with no fallback** when keyless
(§3y), RED arms that caught **two real bugs** plus an **independent 9/9** probe (§3x, §4b), three
wedge outcomes driven by **live** probabilities with the model **echoed 5/5** (§4i), clean-clone
**13 pass / 0 fail** against demo-1's 10/0 bar (§4e).

**And rung 4 is unaskable here for five independent reasons, found by three parties, none looking for
another's finding — every one before any spend:**

| # | Blocker | Number | Found by |
|---|---|---|---|
| 1 | Power | n=30 zero-flip upper bound **`.1135`** cannot clear `≤5%` | pane 2 (§4u) |
| 2 | Implementation | anti-gaming guards **6/6 ABSENT**, prose only | pane 3 (§4v) |
| 3 | Construct validity | labels are a **perfect function of the pattern rule** — a regex scores 100% by construction | conductor (§4w) |
| 4 | Widening | **7 tiny journals** left; credential stratum **struck** (97 shapes incl. our own fixtures) | pane 3 (§4w) |
| 5 | **Ground truth** | two-rater agreement **7/14 = 50%**, **systematic** | pane 3 (§4x) |

**Blocker 5 is the ruling.** The disagreement is not noise — it is *"what counts as **licensed**,
which is the policy's central undefined term."* **If two careful raters cannot agree, a model asked
to judge it has no stable target, and no quantity of data fixes an undefined target.**

> **First phase: define *licensed*.** Not a corpus, not code. Being priced now (Q40), including the
> question that decides the project's shape — **is licensing irreducibly contextual?** If it is,
> that is either the strongest possible case for calibrated abstention or proof the product has no
> target, and the answer determines which.

### 2. MU-H3 runtime redaction — **first phase: PREVALENCE**

**Chosen on evidence, not on score (650, ninth of 17), because it holds two things nothing else in
this lane holds.**

**The only measured defeat of a deterministic baseline.** §4f: Shannon entropy over 23 sentinels —
**combined precision never exceeds 41.7% at any threshold**; at full recall it flags 10–11 of 11
benign strings, at tolerable noise it misses 43% of credentials. *"Raising the threshold reduces
false positives only by missing unknown classes."* **No operating point exists.** Every other
encounter with a deterministic baseline in this lane went the other way — demo-1 lost at 0.047%,
COD-H3 was 4-of-5 deterministic, demo-7's no-AI regex control hit 91.6%.

**The only demand from an unseeded practitioner asking for exactly its surface.** Pablo Rodriguez
(`paroque28`), Claude Code **#39882**, **closed as not planned**: *"Because `PostToolUse` cannot
modify tool output, there is no way to redact secrets from `Read` tool results…"* (§3q). A named
engineer, a filed issue, an unmet need — found by a probe whose instruction contained **none** of
this lane's vocabulary.

> **First phase: measure prevalence.** §4f proves entropy cannot serve the unknown-credential case;
> nobody has measured **how often that case occurs** in real outbound traffic. **Claim only the
> unknown-credential wedge** — known patterns (`AKIA`, `ghp`, `xox`, `sk-live`, key headers) are
> deterministic and must stay deterministic.

---

## RULED OUT — 4, each with a retry condition

| Candidate | Score | Why, with the number | Retry |
|---|---|---|---|
| **demo-1** route-backtest | 520 | Died at **rung 4**: **0.047%** savings vs upstream's −60%. Then found to make **zero Jev calls** behind a hand-written token heuristic. | none — surface owned by LangChain `ModelRouterMiddleware` (§3t) |
| **MU-H1** todo-judge | 820 | **17 markers across 283,786 KLOC**; density 0.0599/KLOC; 13 of 16 repos zero; **183 short** of its own 200-marker study (R14) | ≥5 legacy repos (≥100 KLOC, ≥5 yr, ≥20 contributors) at ≥1.0 markers/KLOC |
| **COD-H3** price-drift auditor | 890 | **4 of 5 stages deterministic**, and 100% of the verified pain (LiteLLM #38064, 262% excess) lives in those four. The lone Jev stage names a tier a **committed table** already names (R15) | T1 deterministic tooling outside the lane; T2 re-file as router with a calibration wedge + misclassification fixture |
| **demo-8** credential screen | 100 | Structural safety leak | none stated |

**Two of these four were killed by a measurement, not an opinion** — demo-1 at rung 4 and MU-H1 by a
census that cost one hour. **MU-H1 is the gauntlet's best economic result: §3k's ordering rule was
written after demo-1 died expensively, and its first application killed the very next candidate to
reach that point for an hour and zero dollars.**

---

## HELD — 8, each with what would move it

- **COD-H4** toolresult-replay (900) — corpus absent; **priced at a 4-hour build.** A deferral with
  a price tag, first in line behind COD-H2.
- **COD-H1** snapshot-completion (885) — **2 of ≥30** transcripts across ≥3 harnesses. A sourcing
  problem with a countable target.
- **demo-4** foreman-lite (820) — **withdrawn as standalone by its own author**, retained as
  downstream integration of COD-H1, which is itself corpus-blocked.
- **demo-7** signals-starter (560) — **repriced twice**: the 32.5-point delta is **89% dataset
  knowledge** (29.0 regex floor + 3.5 method, CIs disjoint), and that 3.5 concentrates in **two of
  five signals (76.25% of weight)**. Transferable claim: ~3 points plus a calibration report.
- **demo-9** review-signal (550) — **skip rung 3 now, not ruled out**; priced at 1–2 engineering
  days. Corpus **PROCEED** (15 diffs, `ubs` baseline non-empty) but *"demo-9 is a contract, not
  code."*
- **demo-3** claim-check-gate (430) — head-to-head designed; ship gate ≥30-pt coverage lift.
- **demo-6** claim-check-notes (330) — incumbent search **closed, no owner found**; held on demand,
  **not** structure.
- **COD-H2** (905) — above.

**CLEARED-conditional (5):** COD-H5 (895, tester-to-subject, distinct from the shipped
`fast-jev-compaction`), demo-5 (755), demo-2 (700, demand recovered via a **named engineer** —
Jörg Michno, MCP Toolbox #2844 — replacing a vendor README sentence), MU-H3 (650), MU-H2 (430,
six-threshold gate designed, incumbents measured: `docverity --no-llm` is **5/20 correct, 14 silent,
zero false verdicts** — *silent, not wrong*).

---

## WHAT TRANSFERS — the lane's thesis, at its honest strength

**Claim:** a deterministic tool can decide; it cannot say how much to trust the decision, per
decision, auditably — and it cannot decline.

**Standing:** two designs I **seeded** and must not count (§3o) · one third-party benchmark
**repriced** to 3.5 points (§3p, §3r) · one external survey whose ceiling figures the census ruled
**`UNVERIFIED_EXTERNAL`/`CONFLICTED_EXTERNAL`** (§3w) · **one local n=60 receipt nobody has had to
correct** (ECE .061, Brier .020) · and **two for two unseeded practitioner voices that do not mention
calibration at all.**

**The reframe those voices forced (§4g), which is the most useful sentence the lane produced:**

> **What practitioners voice is a missing hook. What the engineering evidence supports is calibrated
> abstention behind that hook. The hook is the product; the calibration is how it decides.**

---

## WHY `PROMOTED` IS 0, AND WHY THAT IS THE ANSWER

**A rung-4 pass was available at every step and was refused five times.** The cheapest available
"success" was: run 50 cases, report selective accuracy, ship a green receipt. It would have carried a
**27-point Wilson interval**, against a **regex that defined its own labels**, measured by **guards
that existed only as prose**, on a **ground truth two raters agree on half the time.**

**Three parties each blocked the convenient outcome, including the conductor against its own
proposal** — I proposed the re-scope that would have advanced my own leader and refused to ratify
it, and pane 2 then refused it on power arithmetic I had never computed (§4u).

**`PROMOTED 0` is a finding, not a waiting state.** The product of this lane is this ruling plus the
evidence for the fifteen candidates it did not choose — and the ruling holds precisely because
nothing in it was allowed to pass on the author's word.

---

## UPDATE (appended 2026-09-18, after `2f075fa`) — COD-H2's first phase is priced, and its achievability is a split

**`docs/demos/duel-2/PRICE_license_spec_COD.md`:** the specification phase costs **65–110 minutes**
of human work, validated against an 8-card disputed-case trial.

**And the answer on achievability is a split, which changes the ruling's shape:**

> **Unconstrained *"licensed"* is irreducibly contextual — so a product asking "is this licensed?"
> has no stable target. Risk-tiered, it is likely achievable: ambient context licenses LOW-RISK
> ONLY; destructive/external requires EXPLICIT CURRENT AUTHORITY.**

**The rubric resolves all 7 recorded label disputes, 4 one way and 3 the other** (§4y) — neither
rater systematically vindicated, which is what distinguishes a rule from a compromise.

**Consequences for the ruling above:**

- **COD-H2 is viable as a project** and its first phase is now priced rather than open-ended.
- **Its question must narrow.** *"Should this action proceed?"* is askable only as a risk-tiered
  question. Filed as the project's founding constraint.
- **Rung 4 still cannot run in this lane.** Power is terminal — journals exhausted, `.1135` zero-flip
  upper bound against a `≤5%` gate. **No specification quality fixes that**, so the project needs a
  corpus from outside this lane *after* the spec, not instead of it.
- **One prediction is open and cheap:** the risk-tiered rubric may also fix the construct-validity
  blocker, because authority-in-context is not recoverable from a command pattern. **Being tested
  now by having both panes re-decide the 7 disputed cases independently. Predicted 7/7, split 4–3.**

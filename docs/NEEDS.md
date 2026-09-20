# What the refusals say we NEED to build

Derived 2026-09-20 from `NEGATIVE_EVIDENCE.md` (66 numbered refutations) by inverting each
failure into the capability whose absence caused it. Nothing here is brainstormed; every entry
cites the R-numbers that demand it.

**The uncomfortable read first.** Twelve consecutive refusals (R55–R66) are TTSR rule classes, and
five measurement errors in six hours were all the same shape. **The lane's bottleneck is not Jev
and not omp — it is our own measurement hygiene.** Every NEED below is therefore an epistemic
instrument, not a feature, and each one must have a named consumer and a RED arm or it does not
get built (AGENTS.md phase boundary).

## The mission, and where each NEED lands

> Validate Jev → build tools from what survives → **liven omp surfaces** → **dogfood** → **share**.

| # | NEED | Inverts | Status as of 2026-09-20, measured |
|---|---|---|---|
| 1 | `exposure-check` | R64, R65, R66, R14, R15 | **SHIPPED.** `scripts/exposure-check.sh` + RED arm, verified independently by pane 1: `unsafe` raw 855 → real 314, sessions 5.67%, VERDICT WALLPAPER. Would have killed the 818 in one command |
| 2 | `consumer-check` | R63, R10 | **SHIPPED WITH A DEFECT.** `ee preflight` → ZERO CONSUMERS correctly, and it found a third `ee` caller nobody had. But `ee orient` **also** returns ZERO CONSUMERS and that is FALSE — the ambient extension invokes it from an args array, so the literal never appears. Under-detection **retires live wiring**, worse than the error it prevents. `ee orient` mandated as a RED arm |
| 3 | proxy-vs-quantity guard | R2, R4, R26, R29, + 5 today | **CLOSED — UNDETECTABLE.** Proxies abundant (2,315 turns / 671 payloads + 10,982 harvest / 2,009 turns), bind **0/20 on all three**; the same shapes are used correctly far more often than not, so the defect is in the inference, not the text. **Review owns this class** |
| 4 | Jev-necessity gate | R15, R19, + 3 killed seats | partial — the baseline test has ruled 4 times; `advisory-veto.mjs` never blocks; the earned seat's own interval is [0.118, 0.882] at n=6 |
| 5 | publish the arc | stage 5 has fired once | in progress |
| **6** | **interval + power + family discipline** | **today's ships** | **NEW, from measurement.** See below |

## 6. Every rate carries an interval, every bar-decision states its power

**Added because the numbers said so, not because it was derived from a refusal.** Exact
Clopper-Pearson intervals (mine, independently reproduced by P4 with scipy 1.18.1 + statsmodels
0.15.0 Wilson — **no overturn on any of the seven**) show we **refused with adequate power and
shipped with inadequate power**:

| decision | obs | exact 95% CI | bar | verdict |
|---|---|---:|---|---|
| `ft-rs` / `ft-md` bind | 0/25 | [0.000, 0.137] | ≥0.20 | kill is **sound** |
| `absence-from-one-probe` FP | 4/20 | [0.057, **0.437**] | ≤0.30 | **cannot certify** — needs **n=77** |
| `bash-structural-def-search` FP | 4/20 | [0.057, **0.437**] | ≤0.30 | **cannot certify** — needs **n=77** |
| `bash-callsite-grep-exclusion` FP | 6/20 | [0.119, **0.543**] | ≤0.30 | **n=∞ — p̂ IS the bar. DISABLED 2026-09-20** |

Benjamini-Hochberg across the family (m=17, q=0.05, max_i=11): **no decision changes** — kills
still reject, ship-certifications still retain H0. FDR did not bite because nothing survived.

**The standing rule:** every rate we report carries an exact interval; every bar-decision states
whether n could reject the bar; the family size is declared. Cheap, mechanical, and it would have
flagged all three ships before they went system-wide.

---

## 1. `exposure-check` — do we even hit this gap? *(in progress, P3)*

**Inverts:** R64 (file-type pack binds 1 in 75), R65/R66 (gap-conditioned rescue yields zero
because exposure is the constraint), R14 (TODO-judge refuted by a marker census), R15 (real pain,
no Jev-necessary stage).

One command, one screen: occurrences in the 78,242-command harvest, occurrences in real
edit/write payloads, sessions-touched %, top-1 concentration, **denominator printed beside every
number**, and a verdict against the standing bars (<50 too rare, >5% wallpaper, >50%
concentration is one habit).

**Acceptance:** refuses an unevaluable pattern with a named reason rather than returning zero —
an empty scan set is not a pass. RED arm: the `forbid(unsafe_code)` fixture, where the raw count
is high and the real count is ~zero, must be reported as a discrepancy. That exact case cost a
full arc today.

## 2. `consumer-check` — will anything ever read this?

**Inverts:** R63 (the ee-preflight RECALL leg had **zero** callers and we nearly shipped a
`preflight_rules.toml` into it), R10 (do not build a fleet-idle monitor, one is already installed).

Before any instrument ships, answer: *what reads its output, and where is that call?* Grep the
extension/hook/script surfaces for an invocation; **refuse on zero**. Today this was three manual
probes and it should be one command.

**Acceptance:** given `ee preflight` it returns ZERO CONSUMERS and names the two ee callers that
do exist (`ee orient`, `ee journal append`). Given `dcg` it returns the live callers. A tool that
cannot distinguish those two is not the tool.

## 3. Proxy-vs-quantity guard — our single highest-exposure defect

**Inverts:** R2 and R4 (both retracted for instrument error), R26 (wrong default in a corpus
probe), R29 (a dead background build narrated as progress), and **five instances by pane 1 in six
hours on 2026-09-20**, every one caught externally:

| proxy measured | read as | truth |
|---|---|---|
| 1-second gap between process start and file mtime | "this worker is missing rules" | all five bound |
| a QUIET TTSR probe under `repeatMode: once` | "the rule is absent" | present, already fired |
| 3 days of one repo | "the fleet barely writes Rust" | `rs` is top-two fleet-wide |
| posted body **length** 6282 | "the body is clean" | it opened `DRAFT — NOT SUBMITTED` |
| 818 commits where `unsafe` changed | "16× our exposure floor" | churn of `forbid(unsafe_code)`; real count 2 |

P2's census says its five classes are 5/5 detectable; **this class has never been tested for
detectability** and it outranks them by measured cost. If it is undetectable in a tool-call
payload, that is a legitimate close — say it with the number, as we did for oracle-per-domain.

**Acceptance:** either a rule clearing 50 occurrences and 20% bind on hand-labelled real turns, or
a written refusal with the denominator. No third branch.

## 4. Jev-necessity gate — before any Jev integration

**Inverts:** R15 (no Jev-necessary stage), R19 (incumbent already ships the surface), plus three
killed model seats (harm-rule, tool-call judge, and the numeric half of triage).

The test that has decided every Jev question correctly: **run the deterministic baseline on the
same rows.** If a regex matches Jev, the paid call has not earned its seat. Applied honestly it
also *earned* one — the low-noul veto survives at 3/6 on semantic rows where the baseline is
structurally incapable, while its aggregate advantage was retracted at McNemar p=1.0.

**Acceptance:** a gate that refuses a Jev integration proposal lacking (a) a deterministic
baseline scored on identical rows, (b) a stated asymmetric-loss posture, (c) prevalence of the
positive class. `work/jev-triage/advisory-veto.mjs` already exists and never blocks — it is the
dogfood path that grows the semantic set past n=6 from real classes instead of authored ones.

## 5. Publish the arc

**Inverts:** the mission's own stage 5, which has fired once (skillranker#4) against nine rulings.

A stranger cannot currently read today in two minutes. The material is unusually good *because*
it is mostly refutations: a pack built, live-fired, measured at 1-in-75 bind, and disabled the
same day; a filing whose repro was independently re-run; a withdrawal when a synthetic repro
failed to reproduce.

**Acceptance:** the arc is legible from the repo root without reading 66 R-numbers.

---

## What we explicitly do NOT need

- **More TTSR rule classes mined from doctrine.** R55–R66 refused twelve in a row; three shipped
  rules all came from our own bash history. Mine our corpus, not the mirror (R66).
- **A second static rule surface.** R63: `preflight_rules.toml` would duplicate TTSR with no arms,
  no proof, and no reader.
- **A skill-discovery layer.** `jsm search` fails on natural multi-term queries, but R66 shows
  discovery is the *second*-order problem — exposure binds first.
- **A Jev pruner for compaction.** UP-R4: `keep_p` AUC 0.348–0.648 against a 0.941 positive
  control; keep-everything beat every pruner 12/4/13 vs 82/91/81.

# Dueling Idea Wizards Report: jev (2026-09-25)

## Executive summary

Three models each generated 30 ideas for turning this lane into something relevant and usable,
and each winnowed to 5. They then scored each other's ideas.

Three ideas won consensus, with every non-originating scorer at 700 or above:
1. **`jev-kit`**, a thin package on the official SDK. All preflights live in its request path.
2. **An agent-first surface**: `doctor`, a CLI and robot JSON.
3. **A shadow Jev gate** on fleet bash calls, joined to what happened next.

Two ideas were contested: the experiment kernel and the native omp `judge_batch` bridge.

Four were killed: games as a research lane, live compaction, blocking the gate on day one, and a
CI PR gate.

## Methodology

- **Agents:**
  - Claude Opus (pane 1, orchestrator and dueler, author of the plan under debate);
  - GPT-5.6-Luna (pane 3);
  - Gemini 3.8 Flash (pane 0).
- **Phases:** read the plan (`notes/deep/next-gen/NEXT-STAGE-PLAN.md`) → 30 ideas → top 5 → cross-score
  (0–1000) → reveal and react.
- **Deviations, stated:**
  - Gemini read Claude's idea file before writing its own, so its ideas are not independent.
  - Gemini ran out of tokens before the reveal, so it has no reaction file.
  - Claude orchestrated and also dueled. Its own ideas carry author bias, and the other two
    models moved its #1 down.
- **Evidence the scorers could use (research reports, `local://`):**
  - failure taxonomy: 120 NEGATIVE_EVIDENCE rows, of which only 4 are clean live-Jev losses;
  - doctrine adoption: e-process has 0 non-test callers; no `doctor`, robot JSON or installer;
  - modules and harnesses: 121 harnesses, 0 with a size check, 19 Wilson and 20 McNemar copies;
  - wins by surface: Jev wins 35 and loses 6 against LLMs, and no win has a real consumer.

## Consensus winners

| idea | origin | scores from the other models | verdict |
|---|---|---|---|
| `jev-kit` package + 5-minute stranger quickstart | CC 3, COD 2, GMI 1 | CC 3: COD 900, GMI 925 · COD 2: CC 820, GMI 940 · GMI 1: CC 810 | **WIN.** All three proposed it independently |
| Agent-first `doctor` / CLI / robot JSON | CC 4, COD 7 | CC 4: COD 820, GMI 855 · COD 7: GMI 860 | **WIN**, merged into `jev-kit` |
| Shadow gate on fleet bash with outcome join | CC 2, COD 1 | CC 2: COD 930, GMI 740 · COD 1: CC 870, GMI 765 | **WIN**, advisory until a held-out bar passes |

Key arguments:
- **`jev-kit`.** It extracts `work/jev-client` (102 importers, no `package.json`). Preflights
  move into the request path, so every caller gets them: size, at least 2 options, answer
  offered, and validation. COD's falsifier: "if the kit cannot reduce a new consumer to fewer
  files and failure modes, it is not a kit."
- **Shadow gate.** The existing hook already sees real traffic (710 of 2,501 commands scored). It
  lacks the outcome join and a promotion rule. GMI wants it to act. The rebuttal: live held-out
  recall is 22/33, so blocking has to earn its place on live labels.

## Contested (for Joshua)

- **Experiment kernel** (CC 1: COD 790, GMI 510 · COD 3: CC 760, GMI 530).
  - For: 121 harnesses re-implement the same plumbing badly, and today's three defects were all
    catchable before spend.
  - Against (GMI): building test infrastructure again contradicts "stop repeated testing", and
    preflights belong in the client.
  - Claude conceded the placement. The kernel shrinks to experiment-only concerns (prereg,
    reachability, resume, scoring with the benchmark's own scorer, e-process) and runs behind the
    product.
- **Native omp `judge` / `judge_batch` bridge** (COD 4: GMI 885, CC 640, revised to 780).
  - It reuses omp's primitives, so every omp agent gets Jev without our tools needing consumers.
  - Unproven: whether a project profile can pin Jev with a host-owned key.

## Killed

| idea | scores | why |
|---|---|---|
| Games / computer use as a research lane (CC 5) | COD 650, GMI 420 | harness-heavy; Jev has no incumbent win in agent-policy shapes. Claude parked it at 450 |
| Live compaction (GMI 3) | CC 380, COD 430 | asserted savings; the measured keep rules failed (R99/R100) |
| Active blocking gate from day one (GMI 2) | CC 540, COD 540 | no live labels yet; the whitelist also blinds it |
| Powered Best-of-N selector (COD 5) | CC 470 | needs a new benchmark universe, the thing being frozen |
| CI PR gate (GMI 5) | CC 430 | no measurement behind commit-diff alignment |

## Meta-analysis (orchestrator)

- **Claude over-weighted measurement infrastructure.** That is the verifier's view. Both other
  models put a user-facing product first, and Claude moved.
- **Gemini over-corrected toward shipping.** It proposed blocking and compaction on claims the
  lane's data contradicts. Adversarial scoring caught both.
- **Luna was the most calibrated.** Its falsifiers and ordering (consumer → kit → kernel) held up
  best under all three scorers.
- **Strong convergence on `jev-kit`.** All three models proposed it independently. That is the
  strongest signal of the run.

## Recommended next steps

1. **`jev-kit` v0 (TS first).** Extract `work/jev-client`:
   - preflights in the request path;
   - `doctor`;
   - a fake asker;
   - one-line install;
   - a quickstart proven by the stranger run;
   - the README results section generated from receipts.
2. **Shadow gate v1.** Extend `jev-gate-observe.ts` with the outcome join and a daily report, and
   write a promotion prereg, advisory until it passes.
3. **Judge-bridge spike (keyless).** Can a project omp profile route `judge()` to pinned Jev with
   a host-owned key?
4. **Minimal kernel,** only when the next live experiment needs it: preregistration, resume and
   scoring on `jev-kit`.

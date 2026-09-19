# Harm rule shipped: observe-only omp extension firing live on two models

Pane 3 (muse), 2026-09-19. Product #1: an integration with a measured right to
exist. Zero model calls in the shipped path (deterministic regexes only).

## What shipped

Source of truth: `work/omp-harm-rule/harm-rule.ts`. Deployed copy:
`~/.omp/profiles/jev-lab/agent/extensions/omp-harm-rule.ts` (`cmp` identical).
Registered in `~/.omp/profiles/jev-lab/agent/config.yml` extensions list
(12 entries). jev-lab profile ONLY — codex/claude/panes untouched.

Matching logic: pane 2's `classify()` copied from
`work/toolcall-judge-v3/score.mjs` @ c5966a5 (whole-file shasum
`67e1d114737e5cd0`, identical at HEAD — no drift since the 12/12
measurement). The function body is byte-identical in the deployed file
(`diff` of the `classify` spans: empty). No character changed, so the
12/12 FP 0/40 result describes what ships.

Two things found while copying, both stated: (1) the middle alternative reads
`/verify\s*=<ESC>?false/` — a literal ESC byte making it match `verify=false`
with an optional escape, nearly redundant with the third alternative. Copied
exactly (a byte-exact transplant, verified by empty diff — hand-typing it
produced a 3-char lookalike instead). Upstream may simplify it; behavior on
measured corpora is unaffected either way. (2) My first copy "fixed" it from
memory and the diff caught me — the parity check is load-bearing, not ritual.

Contract: observe-only, never blocks. Diagnostic row on EVERY tool_call
(loaded-but-quiet distinguishable from never-fired — pane 2's observer defect),
decision row (`harm_fire`/`harm_pass` + score + command) on bash calls, `undefined`
on every path including errors. dcg remains the only blocker.

## Live proof (the acceptance)

Real agents in jev-lab, safe commands only (nonexistent paths; dcg blocked the
chmod attempts exactly as designed — rows still emitted pre-block):

| run | model | echo verdict | chmod verdict | diag rows |
|---|---|---|---|---|
| 1 (`.../--private-tmp--/2026-09-19T18-40-25...jsonl`) | gpt-5.6-luna | harm_pass 0.01 (×2) | harm_fire 0.96 (×2) | 7 |
| 2 (`.../--private-tmp--/2026-09-19T18-42-26...jsonl`) | gpt-5.6-sol | harm_pass 0.01 | harm_fire 0.96 | 3 |

Grep: `omp-harm-rule` → 11 rows (run 1), 5 rows (run 2). Both directions fire
under both models. No model call occurs anywhere in this path (no key, no
network, no endpoint configured — there is nothing to configure).

## NO-CLAIM

Firing in a lab profile is not surviving a working profile's traffic: lab runs
are short, prompted, and developer-driven; production sessions are long,
multi-pane, and adversarial. The 12/12 + 0/40 describes planted harms plus 40
routine commands, not the wild. The extension is observe-only precisely so this
gap costs log volume, never blocked work.

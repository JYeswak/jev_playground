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

## P3-15 appendix — co-presence bar MET; (a) refuted; my own silent-module fault

Working bar: a session with observer decision rows NEXT TO a dcg-tool-bridge
row carrying a real verdict. MET in
`--private-tmp--/2026-09-19T18-56-09-857Z_01a0bb06` (luna): 4×
tool_call_observed + 1× harm_pass (echo repair-probe) + 1× dcg_allow
(js-bash id, real non-unknown verdict). Type note: the observer rows are
`omp-harm-rule.decision.v1` (this lane's working observer); pane 2's
`omp-jev-observer.decision.v1` type still has zero rows in any session.
(a) REFUTED with evidence: dcg-tool-bridge IS in jev-lab's config extensions
list and DOES fire (2 rows 18:51, 1 row 18:56). (b) (their accessor reading a
possibly-absent ctx field) not ruled on from my data — my handler never reads
ctx. Live key dump (mandated evidence, one run): event keys are exactly
[type, toolName, toolCallId, input] — no verdict field on the event; verdicts
live in bridge rows, joinable by toolCallId where namespaces align (here both
js-bash, unjoinable to transcript calls per the corpus receipt).
Causal bonus: my own extension reproduced the silent-zero-row defect (a lost
`pi.on` line during editing = syntactically valid module that registers
nothing; node --check passes it). Diagnosed via tsx import probe, repaired,
re-proven live. Silent non-firing modules are now demonstrated twice.
NO-CLAIM: lab-profile co-presence is not a working profile under real user
traffic; js-bash ids in this session repeat the corpus finding (no transcript
counterpart).

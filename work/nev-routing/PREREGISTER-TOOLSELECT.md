# PREREGISTER-TOOLSELECT — Jev Choice vs always-bash on harvested tool-select rows

Committed BEFORE the first live call in this unit (R69 law). A bar written after scores exist is not a bar.

## Question this answers

Can a typed Jev Choice beat the constant predictor on real next-tool labels — the CONSTANT bit of the tool-select seat (the LEXICAL bit already COLLAPSED at 0.0063, `tool-select-derived.json`)? The incumbent here is not an LLM but the base rate itself: always-bash at 0.4395.

## Corpus (mechanical, outcome-blind, file order)

- `work/nev-routing/tool-select-hashed.jsonl`: 1 salt line + **37662 data lines**, ids `ts-00000`..`ts-37661` by data-line index (line number minus 1). Verified this turn: salt + sha256(salt+context)[:16] + label + len all align with text source at 6/6 probe indices (0,1,2,100,1000,37661).
- Text source (NEVER committed, local only): `/tmp/tool-select-pairs.jsonl`, 37662 lines, same index, keys `{context, file, label}`, context truncated at 500 chars. Labels are proxy (called-next; basename collisions inflate — see `tool-select-extract.json` NO-CLAIM).
- **Do NOT use `tool-select-labelled.jsonl` (137063 lines) as the denominator.** Different row set (unlabelled included).
- Boundary: contexts are our own harvested session text and may contain secrets; sampled ROWS are never committed (aggregates + receipt only), and contexts are sent to api.typesafe.ai as the judged state — inherent to the unit, stated openly.

## Arms

- **Constant:** always-bash → 16552/37662 = **0.4395** on the full set (re-derived this turn); per-tranche rate recomputed on the same rows Jev scores.
- **Jev Choice** via `work/jev-client` `askJevChoice` (native SDK path, NO hand-rolled POST):
  - model pinned **`jev-1.13.0`**.
  - instructions (fixed, never retuned after scores): `Given this prior tool-call context, pick the tool the agent calls next. Answer with exactly one label.`
  - state: `{context}` text only (500 chars). `file` EXCLUDED (path leaks tool names; name-match collapse is not the seat).
  - criteria: map of the 12 labels with count ≥ 200 (bash, read, eval, edit, hub, write, grep, yield, glob, todo, web_search, task), description = the label string itself (no invented semantics; SDK-valid, null-free).
  - transport: one request per row, bounded concurrency (≤8 in flight), foreground attended run, incremental row writes (`rows-toolselect-jev.jsonl`, resume skips completed ids). One retry on transport failure; >2 failed rows per tranche renders that tranche INVALID, not a verdict.

## Bar (PASS certifies; anything else is reported as measured)

1. Jev top-1 accuracy vs always-bash on the SAME rows, exact McNemar two-sided on discordants (Jev-only hits vs bash-only hits).
2. SEAT GATE: Jev accuracy exceeds 0.4395 AND McNemar p < 0.05. Otherwise the verdict is whatever the numbers say.
3. **Sample rule, fixed before scores exist:** tranche 400 in file order; STOP and report if p < 0.05 in either direction; else continue by +400 up to 2000; at 2000 without significance report UNDERPOWERED. **A loss is a first-class result** (one line, retry condition, move on).
4. Cost/latency/tokens recorded per tranche from the client usage fields.

## NO-CLAIM (carried with every number)

Not a seat until the gate above is met. Labels are proxy (called-next), single run, one model id, one fixed question. Name-match collapse (0.0063) is a different, already-dead bit.

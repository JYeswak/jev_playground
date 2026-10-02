# PREREG — long-result keep/summarize/drop (bead jev-dau5)

Frozen 2026-10-02 before any live call. Outcome-census long class: ~214
harmful/week unreferenced bloat. Design borrows the measured parts of
skill://jev-compaction (judge first 350 + last 350 chars; summarize = clip
to 400 chars; invalid -> KEEP, never drop on error).

## Population (keyless, frozen)

`work/longres/corpus.json`: 200 long toolResults (>=10k chars) from 7d
sessions, seed 20261006, split dev 100 / held 100 by file (no file in both).
Labels (mechanical, disclosed): REFERENCED iff any of 3 evenly-spaced
60-char probes appears later in the same file, else UNREFERENCED.
Extractor `extract.py` also records the weekly >=10k-result volume for the
savings extrapolation.

## Jev design (one Choice)

State: result head 350 + tail 350 chars + the user task (last user message
<=500 chars). Instructions: "This tool result just arrived. How should it be
kept for the rest of the session?" Classes: keep (the task will need its
details), summarize (its gist suffices), drop (it will not be needed).
Decision = Choice top-1; invalid/refused -> KEEP (fail-safe: never lose data
on error). 1 call/row, jev-1.13.0, 20 s timeout.

## Baseline (deterministic, fitted fairly)

DROP iff size >= T AND tool in content tools
{read,bash,eval,grep,glob,find,web_search,web_extract,fetch}; else KEEP
(summarize unused). T = Youden-J fit on DEV (UNREFERENCED as positive),
tie-break highest T (fewer drops). No other tuning.

## Bar (held 100, fixed pre-call)

PASS iff Jev miss rate (drops REFERENCED) <= baseline miss rate AND Jev
tokens saved on held UNREFERENCED rows >= 1.2x baseline savings, where a
summarize decision saves (len-400)/len and drop saves 100%.
Report: miss both arms with Wilson CIs, savings both arms, per-call
model/status/tokens/latency/spend, exclusions. FAIL keeps the baseline;
no enforcement either way (eval only — shadow-before-enforcement holds).

## Caps

<= 200 calls, $0.015 cap (~$0.008 expected: short states), stop 401/402/403,
checkpointed by sample_id. Runner `run_choice.mjs`; receipt
`choice-rows.jsonl` (sample_id, choice, probs, status, tokens, latency;
result text excluded, row hash joins). NO-CLAIM beyond sampled long results.

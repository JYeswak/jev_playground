# Does "none of the above" still work at 150 intents? Full CLINC150, Jev vs Haiku (bead `jev-pm3`)

JevVariance (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** `jev-qw8` ([receipt](choice-clinc150-20260924.md), verified by VerifySST5) passed on
one CLINC150 domain of 15 intents: non-inferior on plain answers (688 vs 681 of 750) and a clear
win once both arms answer only at peak probability >= 0.60 (685 vs 650). Banking77 showed accuracy
falling as the label set grows (96.0% at 10 intents, 80.1% at 77; `jev-k3k`, `jev-4jf`). Does the
same method hold on the whole CLINC150 test split, one Choice over all 150 intents plus "none of the
above", against Claude Haiku 4.5 through TypeSafe's adapter?

**Corpus.** CLINC150 (Larson et al., EMNLP 2019, CC-BY-3.0), `clinc/oos-eval` at
`828f8093932c8fe6ca7936c3d2e52903b1c523de`, `data/data_full.json` and `data/domains.json`, sha256
pinned as in jev-qw8. **Rows: the whole test split, no sampling.** Every `test` row (4,500: 150
intents x 30) then every `oos_test` row (1,000), in file order: 5,500 rows, 18.2% out-of-scope,
each tagged with its domain. `work/choice-clinc150/full.jsonl`, sha256
`2ecf72aee4b8f49211378744beba883d1e99385ce76ebbec42be20708595f126`. Rebuild and diff:
`python3 work/choice-clinc150/sample.py --set full --check`. The 750 jev-qw8 rows are a subset
(matched by text; CLINC's 5,500 test texts are unique).

**Constant first.** Always "none of the above": 1,000/5,500 (18.2%) overall, 0/4,500 in-scope, OOS
recall 1,000/1,000. It is also the always-abstain control for the gate (handles 1,000).

**The question, identical in both arms** (`work/choice-clinc150/run.py --set full`). State
`{"user_request": <text>}`. One Choice named `intent`, instructions *"The intent of this request to
a virtual assistant"* (jev-qw8's said "car and commute assistant"; one domain's wording cannot
cover 150 intents), 151 options: the 150 intent names humanized (underscores to spaces), sorted,
undescribed, then `none of the above` described as *"A request that fits none of the above"*, last,
as in jev-qw8. 151 is under the vendor's documented cap of 255 options
(`docs-mirror/typesafe/primitives/choice.md:355`).

**Arms.** Concurrency 16 in both (8 in jev-qw8; it changes wall time, not the request).
- **Jev:** `typesafe-sdk-python` `TypeSafeClient`, `model="jev-1.13.0"`, 30 s client timeout.
- **Incumbent:** `upstream/typesafe-ai/system-one-adapter-python` (`adffc2e`),
  `anthropic/claude-haiku-4-5`, `llm_answer_mode="probabilities"`, `normalize_probabilities=True`,
  default `RetryPolicy`. Every Haiku row records the adapter's `debug.probability_errors` for the
  question (`probabilityError`), the raw sum before renormalization (`rawSum`), transient retries
  and malformed-structure retries.

**Haiku's output mode, and the fallback, declared now.** In `jev-4jf`, Anthropic rejected every
native-structured-output request for a 77-option Choice, verbatim *"400 The compiled grammar is too
large, which would cause performance issues. Simplify your tool schemas or reduce the number of
strict tools."* ([receipt](choice-banking77-full-20260924.md), second preregistration). 151 options
make a larger grammar, so this bar fixes the procedure before any call:
1. **Probe.** Native structured outputs (`structured_outputs=True`) on the first 16 rows:
   `run.py --set full --limit 16 haiku` -> `rows-full-haiku.jsonl`.
2. **If any probe row is rejected with the grammar-cap message** (the scorer matches
   `compiled grammar is too large`), the structured arm is recorded as capped, its rows are kept as
   evidence, and the whole Haiku arm runs as **prompted JSON**: `run.py --set full haiku-prompted`
   -> `rows-full-haiku-prompted.jsonl`, all 5,500 rows. That is jev-4jf's variant exactly:
   `structured_outputs=False` (the adapter puts the output schema in the prompt and validates the
   reply) and `n_retry_malformed_structure=1`, every other setting unchanged. The prompted rows are
   the scored Haiku arm.
3. **If no probe row hits the cap,** the structured arm continues on the remaining rows and is the
   scored Haiku arm; the prompted variant is not run.

The scorer applies this rule itself (`set_files()` in `work/choice-clinc150/score.py`). The
two-stage hierarchical fallback is not used, for jev-4jf's reason: it would change the question
for both arms.

**Order of runs.** Jev on all 5,500 rows, then the Haiku probe, then the Haiku arm the rule selects.
Each arm gets one resume pass for failed rows (rerunning the runner retries only rows without an
answer).

**The adapter's zero-mass behaviour** (`jev-mly`, [receipt](adapter-uniform-20260924.md)): as in
jev-qw8, every Haiku result is scored twice, as shipped and with each `rawSum == 0` row read as
"none of the above", and each verdict is the worse of the two for Jev.

**Measures, gate, shippable bar, paired test:** exactly jev-qw8's. Overall correct over 5,500;
in-scope accuracy over 4,500; OOS recall over 1,000; OOS precision; Wilson 95%. The gate routes a
row only when the chosen option is an intent and peak probability >= t: primary t = 0.60 (the
vendor's `MIN_CHOICE_PROBABILITY`), also 0.80 and 0.90, and on each arm's returned `confidence` at
0.5 / 0.7 / 0.9 (descriptive). Shippable: misroute rate <= 2.0% (110 rows) and in-scope coverage
>= 80% (3,600 rows). McNemar exact on per-row correctness. Latency p50/p95 and tokens per arm.

**Pass rule, fixed now** (jev-qw8's, on its two primaries, overall correct and handled at peak >=
0.60, constant 1,000 for both):
- **Failed rows:** an arm with more than 1% failed rows (55) after its resume pass is
  **NOT-SCORED**, and so is every primary verdict (a Jev option-count rejection, or a prompted Haiku
  run that keeps producing malformed output, lands here). NOT-SCORED is not a pass.
- **Feasibility:** an arm below 50% in-scope accuracy: no verdict.
- **LOSE** if Jev does not beat the constant (1,000), or is more than 3.0 percentage points (165
  rows) below Haiku.
- **WIN** if Jev-only-correct > Haiku-only-correct and McNemar p < 0.05; else **NON-INFERIOR**.
- Jev **PASSES** if both primaries are WIN or NON-INFERIOR under the worse Haiku reading. A LOSE on
  either goes to `NEGATIVE_EVIDENCE.md` with a retry condition.

**Descriptive only (no verdict):** in-scope accuracy by domain (10 x 450 rows); and the 750 jev-qw8
rows answered with 16 options there and 151 here, per arm (the instructions also differ, and for
Haiku the output mode may too, so this is the whole question changing, not the option count alone).

**Scorer.** `python3 work/choice-clinc150/score.py --set full` (stdlib, no key). Without
`--set` it still prints jev-qw8's output byte-for-byte (checked against the scorer committed at
`2842340`). Keyless self-check on planted rows outside the tree: a 16-row structured probe that all
hit the cap selects the prompted file; 100 zero-mass Haiku OOS rows give recall 900/1,000 as
shipped and 1,000 as none; 60 failed Jev rows (over 55) make both primaries NOT-SCORED, 50 do not.

**Spend, planned.** 5,500 Jev calls; 16 structured Haiku probe calls; if the cap fires, 5,500
prompted Haiku calls. From jev-4jf's prompted per-call use at 77 options (about 2,100 input and 980
output tokens), 151 options is roughly 4,000 in and 1,900 out per call: about 22M input and 10.5M
output tokens, on the order of $75 at $1 / $5 per MTok list price `[INFERENCE: an estimate, not a
bill]`. There is no call budget (AGENTS.md, 2026-09-21); the receipt states what was spent.

## Result (live, 2026-09-24 03:17-03:47 UTC, bar at `defed49`)

**Verdict: BLOCKED-until-cap, not a result and not a FAIL.** Jev's arm is complete. Anthropic's
account usage limit stopped the Haiku arm at 3,863 of 5,500 rows. Under the bar that is more than
1% failed rows (1,637 vs 55), so both primaries are NOT-SCORED. The bead stays open until the cap
lifts, which the provider message dates at 2026-10-01 00:00 UTC; raising it is Joshua's call. No
NEGATIVE_EVIDENCE entry is due: nothing lost. Re-score (no key, about 3 s):
`python3 work/choice-clinc150/score.py --set full`.

**What happened, in order.**
1. Jev: 5,500/5,500 answered, 0 failed, all rows `jev-1.13.0` (committed `5025e45`).
2. Haiku structured probe: 16/16 rows rejected verbatim with *"400 The compiled grammar is too large,
   which would cause performance issues. Simplify your tool schemas or reduce the number of strict
   tools."* (`rows-full-haiku.jsonl`). This is jev-4jf's cap, so the declared prompted-JSON fallback
   ran.
3. Haiku prompted JSON: 3,863 rows answered. The first launch ran under a 300 s tool deadline and was
   killed at 733 rows (no error rows; in-flight calls lost). Five further launches were cancelled
   within seconds, still under that deadline, and recorded 0 rows; any calls they had in flight
   were lost and are not counted `[unmeasured]`. The run then resumed under a supervised process
   (`hub`), which answered 3,130 more rows before every remaining request, 1,637 rows, came back
   verbatim:
   > `TypeSafeBadRequestError: 400 You have reached your specified API usage limits. You will regain
   > access on 2026-10-01 at 00:00 UTC.`
4. The bar's one resume pass, limited to 4 rows so as not to loop on a dead endpoint (pane 1's
   fleet order was not to retry), got the same message 4/4. Those 1,637 rows are **NOT_RUN** (1,341
   in-scope, 296 out-of-scope, spread across the file). The error rows stay in
   `rows-full-haiku-prompted.jsonl` as the evidence.

**Jev, all 5,500 rows** (measured, `[live]`, N = 5,500):

| Measure | Jev | Always none |
|---|---:|---:|
| Overall correct | 4,960 (90.2%, Wilson 89.4-90.9%) | 1,000 (18.2%) |
| In-scope accuracy | 4,087/4,500 (90.8%) | 0 |
| OOS recall | 873/1,000 (87.3%) | 1,000 |
| OOS precision | 873/1,004 (87.0%) | 18.2% |
| Latency p50 / p95 | 161 / 386 ms | |
| Tokens in / out | 7,662,132 / 6,866,522 | |

| Jev gate on peak | Routed right | Misrouted (in-scope / OOS) | Misroute rate | In-scope coverage | Handled | Shippable |
|---:|---:|---|---:|---:|---:|---|
| 0.60 | 3,953 | 203 / 95 | 5.4% | 87.8% | 4,858 | no |
| 0.80 | 3,622 | 144 / 58 | 3.7% | 80.5% | 4,564 | no |
| 0.90 | 3,364 | 114 / 42 | 2.8% | 74.8% | 4,322 | no |

Jev is not shippable under the preregistered bar (misroute <= 2%, coverage >= 80%) at any fixed
threshold, on peak or on returned `confidence`. Its commonest errors are near-synonym intent
pairs: `accept_reservations -> restaurant_reservation` x30 and `reminder_update -> reminder` x30
(every test row of each), `cancel -> none` x19, `distance -> directions` x17. It also routes some
out-of-scope rows to intents, e.g. `oos -> time` x15. In-scope accuracy by domain runs from 84.0%
(kitchen_and_dining) to 98.4% (travel).

**From 15 intents to 150, on the same 750 jev-qw8 rows** (descriptive; the instructions changed
too): Jev overall 688 -> 646, in-scope 395 -> 391 of 450, out-of-scope said none 293 -> 255 of
300, handled at 0.60 685 -> 640. Almost all of the loss is on out-of-scope rows: with 150
candidates, Jev finds an intent for more requests that have none.

**Haiku, the 3,863 rows it answered** (`[live]`, partial; no verdict): p50 / p95 6,252 / 11,770 ms,
12,623,465 input / 6,131,815 output tokens. The adapter renormalized 43 rows
(`debug.probability_errors` > 0, raw sums 0.51-2.49); 0 zero-mass rows; 0 transient retries; 2
malformed-structure corrective retries.

**Descriptive, not preregistered, no verdict: the 3,863 rows both arms answered** (3,159 in-scope,
704 OOS). The NOT_RUN rows are the ones in flight or queued when the cap hit; which rows those are
depends on timing, not content `[INFERENCE]`, but that is not tested.

| Measure | Jev | Haiku | Jev-only / Haiku-only | McNemar p |
|---|---:|---:|---|---:|
| Overall correct | 3,459 (89.5%) | 3,300 (85.4%) | 295 / 136 | 1.4e-14 |
| Handled at peak >= 0.60 | 3,395 (87.9%) | 3,272 (84.7%) | 297 / 174 | 1.6e-8 |
| In-scope correct | 2,844/3,159 (90.0%) | 2,733/3,159 (86.5%) | 227 / 116 | 2.1e-9 |
| OOS said none | 615/704 (87.4%) | 567/704 (80.5%) | 68 / 20 | 2.8e-7 |

The scorer's primary table counts the 1,637 NOT_RUN rows as Haiku errors, per the bar's
failed-row rule. That is why its Haiku column reads 3,300/5,500 and its paired "WIN" lines show
p = 0. **Those lines are not a result and must not be cited.** The bar's failed-row limit is what
voids them.

**To finish after 2026-10-01 00:00 UTC (or when Joshua raises the cap):** rerun
`run.py --set full haiku-prompted`. It retries only the 1,641 rows without an answer (1,637 plus the
4 resume-probe rows, same ids). Then re-score. Nothing in the bar changes.

**Spend.** Jev: 5,500 calls, tokens above. Haiku: 16 structured calls rejected (400); 3,863 prompted
calls answered (12.6M in / 6.1M out, about $43 at $1 / $5 per MTok list `[INFERENCE: not read from
a bill]`); 1,641 prompted calls rejected with the usage-limit 400; plus any in-flight calls lost
in the six killed or cancelled launches `[unmeasured]`.

## NO-CLAIM

- No Jev-vs-Haiku verdict on the full set: the Haiku arm is BLOCKED-until-cap.
- The both-answered comparison was not preregistered and carries no verdict.
- Haiku ran as prompted JSON (native structured output is capped at this size). Whether that mode
  helps or hurts it is unmeasured.
- One run per arm; no variance.
- CLINC's labels were not re-adjudicated; the near-synonym pairs above are the dataset's
  distinctions.

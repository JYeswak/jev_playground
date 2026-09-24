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

## Result

NOT_RUN. Filled in after the runs.

# Duel: turning Jev into something relevant and usable

Date: 2026-09-25

## Scope and evidence boundary

This is a design memo, not a Jev result and not an implementation claim. No Jev/API call was
made for this memo. I read all of `AGENTS.md` and `README.md`, the current proposal under
`notes/deep/next-gen/NEXT-STAGE-PLAN.md`, `SYNTHESIS.md`, and `BRIEF.md`, plus the relevant
`work/`, `scripts/`, `.omp/`, and `foundation/` seams. The requested
`notes/deep/next-gen/NEXT-SCODE-PLAN.md` is absent from the checkout; `NEXT-STAGE-PLAN.md` is the
present filename for the proposal under debate, and that filename drift is noted rather than
silently invented.

The architecture is already unusually close to a product: `work/jev-client` is the single
sanctioned SDK-backed caller with lazy SDK loading, explicit failure classes, a billing hold,
transport injection, and strict response guards; `.omp/` has model-callable screen/rerank/claim
check/flag tools, an advisory diff extension, an observe-only gate hook, and a report-only
compaction hook; omp 18.3 has native `judge()`, `judge_batch()`, `jevify`, `find`, and `toks`
but the profiles do not yet expose a configured Jev judge role; `foundation/` has receipts,
self-testing gates, claim coverage, readiness, promotion, and negative-evidence machinery.
The gap is therefore not another question template. The gap is one consumer loop, one reusable
package, one evidence kernel, and a stranger path that works without reading this lane's history.

Important measured constraints carried into every idea:

- Jev is cheap and fast enough to ask repeatedly, but not free of engineering: roughly 127--162 ms
  p50 on short states, about $0.042/M input tokens, and a hard state-size limit that already caused
  71% of R112's loss when ignored.
- Calibration is workload-specific. It is strong on several verification/injection sets and poor
  on phishing, toxicity, pure chance, and some safety surfaces. Thresholds must be per seat and
  must have an abstain/review side.
- Existing omp tools mostly have no organic consumer. The gate's best measured criteria arm caught
  77--79/100 risky commands at 1--3/300 false alarms, but real traffic and the agreed in-place-edit
  slice show that a shadow signal is not yet a blocking policy.
- The README already has twenty demos and is almost at its size limit. It is a measurement ledger,
  not a five-minute stranger experience. More demos without a path to a repeated consumer would
  repeat the failure the proposal names.
- TypeSafe's use-case map and the local playbook place these ideas in Harness Engineering,
  Universal Verification, AI Map Reduce, Real-time Applications, or Gaming; the decision shapes
  are Choice, Score, Noul, fan-out, confidence-gated routing, and composite scoring. I do not
  treat a thirteenth invented pattern as a virtue.

## Thirty candidate ideas

Each item has the mechanism, how it feels to a user, a pragmatic implementation seam, and the
main failure mode. The ideas are deliberately broad before winnowing; the ranking is below.

### 1. OMP shadow decision plane with human outcome feedback

**Mechanism:** Keep the existing observe-only tool-call gate, but make it a real decision plane:
redacted command hash, state version, five Jev probabilities, policy decision, latency, and later
human outcome in one append-only ledger. Start in silent shadow mode on every eligible real bash
action; sample review prompts only where the policy is uncertain or high impact, then use the
labels to calibrate a per-seat threshold before any blocking. **User perception:** the agent feels
unchanged at first, then gains a small, explainable "review suggested" signal instead of a surprise
hard block. **Implementation:** `.omp/hooks/post/jev-gate-observe.ts` already owns the event and
redaction seam; add a durable outcome join and a `jev doctor/score` report, not a second caller.
**Risk:** the hook is blind to eval-prelude browser/computer calls, and current real-traffic labels
are not enough to block. Keep it advisory until a preregistered held-out false-alarm/recall bar
passes.

### 2. `jev-kit`: one thin TypeScript/Python decision package

**Mechanism:** Extract the stable core already present in `work/jev-client`: pinned model, typed
Choice/Score/Noul/Bundle calls, strict validators, state-size preflight, transport injection,
fail-safe policies, billing hold, and structured receipts. **User perception:** a stranger can
write `judge.choice(...)`, run the fake asker offline, and understand exactly what happens when a
key is absent or an answer is malformed. **Implementation:** keep the official SDK as the wire
owner; publish a tiny TS surface first and a matching Python surface only where the existing
SDK/ecosystem needs it. `npm run quickstart`/`uv run` should be one command and exercise the same
policy in fake and live lanes. **Risk:** package growth can become a second framework; zero
runtime dependencies, no prompt registry, and no compatibility shims keep it accretive.

### 3. Experiment kernel: one preregistration, preflight, scorer, receipt, resume loop

**Mechanism:** Replace bespoke `work/*/live.mjs` runners with one kernel that freezes a bar,
imports a non-authored corpus, checks answer reachability and token size, hashes code/modules,
runs the SDK with bounded retries, writes partial/resumable rows, scores with the source scorer,
and supports the existing anytime-valid e-process. **User perception:** experiments become a
predictable command rather than a new local dialect every week; a refused experiment explains why
before spending. **Implementation:** compose `scripts/bar-reachable.py`,
`scripts/jev-state-size.py`, `work/oracle-kit/index.mjs`, existing receipts, and the client's
failure taxonomy behind a stable JSON schema. **Risk:** a kernel can become process theater; every
field must gate a downstream action, and the first consumer should be the next real live run rather
than another abstraction document.

### 4. Native omp Judge-role bridge with a safe project profile

**Mechanism:** Turn omp 18.3's native `judge()`/`judge_batch()` into the default path for this
project: configure the `judge` role to `typesafe/jev-latest`/pinned Jev, load the key through the
host-owned resolver, expose model id and lane in results, and leave the shell environment keyless.
**User perception:** a stranger can use the same `judge()` primitive that omp already exposes,
without installing a custom MCP server or learning this repository's client. **Implementation:**
add project-profile configuration, a keyless diagnostic, and a small wrapper only for receipt and
fail-safe policy; use native `judge_batch` rather than reimplementing fan-out. **Risk:** profile
configuration is easy to mistake for a live proof, and native `judge()` may be unavailable on a
fresh machine. The doctor must say `loaded`, `NOT_RUN`, or live with exact model identity.

### 5. `jevify`: guarded bulk classification over local files and logs

**Mechanism:** Generalize omp's native `jevify` idea into a data-to-decision command: freeze the
question/rubric, prefilter locally, batch all eligible rows, read only flagged rows, and emit a
redacted receipt with prevalence, cost, latency, and abstentions. **User perception:** "classify
these 10,000 local items" becomes a useful command rather than a notebook or bespoke loop. **Implementation:**
use `judge_batch()` with a map-reduce state contract, `toks` for budget, a deterministic row id,
and human-review export; examples should be command safety, diff triage, and stale-cache checks.
**Risk:** bulk data can leak secrets or produce an impressive but useless number. Secret taint,
size refusal, a majority baseline, and an outside label/next action are hard gates.

### 6. Redacted score register with replay and drift reports

**Mechanism:** Extend the existing `work/jev-score-register` pattern into a first-class register
of state hash, question hash, model, outcome, usage, latency, and policy version, without storing
raw state. **User perception:** users can answer "what did this cost, and did it change?" without
shipping sensitive prompts. **Implementation:** canonical JSON hashing, append-only JSONL, replay
against fake askers, and a diff/drift report for identical requests across model revisions. **Risk:**
a register can become a passive graveyard; every row type needs a reader (cost dashboard, threshold
calibration, or regression detector).

### 7. `omp doctor jev`: readiness before a call or a claim

**Mechanism:** A single diagnostic checks model pin, judge-role resolution, SDK materialization,
key source without printing it, state-size calibration, hook discovery, receipt path, and whether
the current bar is reachable. **User perception:** a failed quickstart gives a fixable reason
instead of `NOT_RUN` buried in a demo. **Implementation:** compose existing key-status,
`jev-state-size`, config/profile inspection, and foundation gate preflights; never call Jev during
the doctor. **Risk:** another checker with no consumer. Make the quickstart and every live runner call
it and refuse on red.

### 8. Taint-aware state builder and secret-safe redaction contract

**Mechanism:** Build states from structured fields with explicit `public`, `private`, and
`derived` classes; redact or refuse private values before serialization and record the reason,
size, and hash. **User perception:** users know what leaves their machine and why a decision was
skipped. **Implementation:** a small schema/taint layer used by `jev-kit`, `.omp` tools, and the
kernel; reuse the gate's filter owner instead of copying regexes. **Risk:** false redaction can
remove the evidence that makes a judgment useful; provide a preview/hash mode and fail closed when
classification is uncertain.

### 9. Per-seat calibration and coverage profiles

**Mechanism:** Treat each production question as a named seat with its own held-out labels,
prevalence, threshold, abstain band, confidence reliability, and refresh trigger. **User
perception:** "0.8 confidence" stops being a magical global promise and becomes a documented
policy for this exact decision. **Implementation:** reuse foundation calibration receipts and
`oracle-kit`, generate threshold recommendations, and refuse cross-seat threshold reuse. **Risk:**
small labeled sets overfit; require a minimum prevalence/sample rule and expose uncertainty instead
of selecting the most flattering cut.

### 10. Human review queue as the explicit fail-safe consumer

**Mechanism:** Every low-confidence, malformed, budget-refused, or policy-disagreement result
becomes a compact review item with context hash, evidence excerpt, and one-click label. **User
perception:** Jev is a quiet triage assistant, not an invisible autonomous authority. **Implementation:**
start with JSONL plus a terminal/web viewer, then feed labels to calibration and shadow gates.
**Risk:** queues become ignored spam; cap volume, prioritize by expected information value, and
measure reviewer actions rather than merely row count.

### 11. One-request fan-out API with policy combinators

**Mechanism:** Expose a single typed bundle builder for several Noul/Choice/Score questions over
one state, with deterministic `all`, `any`, `max-risk`, confidence gate, and review policies.
**User perception:** users describe one decision and its checks, not five HTTP loops. **Implementation:**
formalize `askJevBundle`, schema validation, cost estimation, and combinators in `jev-kit`; emit
one receipt per state. **Risk:** fan-out can hide which question failed; return per-question
provenance and do not let a missing answer silently pass the aggregate.

### 12. Compaction hook from shadow report to selective action

**Mechanism:** Use the existing `.omp/hooks/pre/jev-compact.ts` report-only path to collect real
human keep/drop outcomes, then promote only a proven sub-policy (for example, protect error and
failure evidence, drop repetitive tool output) with a rollback flag. **User perception:** long
sessions stay useful without mysterious summarization. **Implementation:** label actual compacted
sessions, use byte-identical retention checks, and require a held-out Wilson bound before changing
omp's keep set. **Risk:** compaction can destroy context invisibly and the hook is not the
summarizer; keep shadow mode until the consumer boundary is measured.

### 13. Diff-review feedback loop, not just advisory decoration

**Mechanism:** Connect `.omp/extensions/jev-review.ts` advisory rows to whether a human requested
changes, accepted, or reverted the diff. **User perception:** the review hint becomes calibrated
over time instead of a mysterious warning line. **Implementation:** capture only redacted diff hash,
score, advisory, and later review action; replace the current blunt real-diff label proxy with
actual review outcomes. **Risk:** reviewer action is delayed and biased; report it as feedback data,
never immediate accuracy, and never give the extension merge authority.

### 14. Tool-result evidence-density triage

**Mechanism:** Score a tool result for task-relevant signal, preserve errors and security evidence,
and trim or collapse low-density noise before context injection. **User perception:** less context
bloat without losing the line that explains a failure. **Implementation:** a `tool_result` or
post-processing surface with Score/Noul plus hard deterministic preserves; use `jevify` batches for
offline calibration. **Risk:** `tool_result` cannot flip the wrapper's error verdict and eval-prelude
calls are invisible; document both limits and fail safe to full content.

### 15. Semantic cache-validity gate

**Mechanism:** Before reusing an old answer, judge whether the cached answer still satisfies the
new task/state, returning reuse, recompute, or review. **User perception:** faster agents reuse safe
work without pretending stale results are current. **Implementation:** hash state/question, retain
provenance and expiry, ask a Noul/Score on semantic compatibility, and sample human invalidations.
**Risk:** stale cache false positives are expensive; cache only advisory at first and make the
recompute path deterministic.

### 16. Receipt-driven README and example generation

**Mechanism:** Generate the results table, model/date/lane labels, live boundaries, and runnable
command index from receipts rather than hand-authored prose. **User perception:** the README is a
short truthful tour instead of a near-size-limit ledger. **Implementation:** extend existing claims
coverage and stranger-run inventory into a generated section checked in CI; keep explanatory prose
handwritten. **Risk:** generated docs can inflate activity while hiding a bad result; require a
receipt hash, explicit NOT_RUN, and an independent stranger command run.

### 17. Five-minute stranger package runner

**Mechanism:** Make `bash scripts/quickstart.sh` install nothing, answer one offline policy with a
fake asker, show the exact live command, and print a copy-paste starter for the native omp judge
role. **User perception:** clone-to-understanding is measured in minutes, not archaeology. **Implementation:**
add a tiny `jev-kit` example, portable prerequisite messages, and a single README path; use the
existing stranger-run harness as the test. **Risk:** another fixture demo that does not consume
real data; include `--mine` on local logs and a clearly separate live smoke.

### 18. Typed question/state compiler

**Mechanism:** Accept a small JSON/TypeScript schema for a decision and generate the state-size
check, question body, validator, fake fixture contract, and receipt schema. **User perception:**
new decisions feel like declaring an interface, not hand-writing prompt plumbing. **Implementation:**
generate only boring data-shape code on top of the sanctioned client; preserve human-authored
policy and thresholds. **Risk:** generated code can obscure the actual bar; emit readable files and
require the generated negative tests to be reviewed.

### 19. Free-incumbent differential runner

**Mechanism:** A contract-level adapter runs the exact same state/questions through Jev and an
allowed free comparator, producing paired accuracy/cost/latency rows without mixing paid comparator
runs into the lane. **User perception:** users can tell whether Jev is buying useful speed/stability,
not just see a Jev-only score. **Implementation:** reuse `system-one-adapter-python` and free
OpenRouter feasibility, with one receipt schema and no fallback that hides refusal. **Risk:**
comparator availability and provider drift; require a pinned free model and mark NOT_RUN rather than
filling gaps.

### 20. Anytime-valid experiment runner

**Mechanism:** Put `oracle-kit`'s e-process into the kernel so a live run can stop early for a
clear pass, fail, or continue decision without peeking at a fixed horizon. **User perception:**
long experiments spend only until the decision is clear and explain why they stopped. **Implementation:**
freeze hypotheses/alpha, stream rows, persist the e-process and resume cursor, and render a compact
receipt. **Risk:** optional stopping is invalid if the statistic/bar is altered; make the kernel
own the frozen contract and test planted RED/green sequences.

### 21. `jev_select`: best-of-N agent trajectory portfolio selector

**Mechanism:** Given several agent attempts and a shared task, Choice selects the trajectory with
the strongest completion evidence; an external task checker scores the selection. **User perception:**
users can run multiple cheap/fast agents and let a typed judge choose instead of trusting first
completion. **Implementation:** scale the released OSWorld Best-of-N design to a powered, non-overlap
universe; expose the same selector as an omp tool for subagent attempts; use result rows only for
scoring, never state. **Risk:** the 24-task retry was provably underpowered (`294b9bce`); do not
repeat it, and do not call this a Jev result until a full-power bar is reachable.

### 22. Browser action lattice plus verifier slot

**Mechanism:** Enumerate element/operation candidates, let Jev choose a next action, then ask a
second Noul/Score whether the resulting DOM transition achieved the intended subgoal. **User
perception:** browser automation can recover from a wrong click rather than blindly continue. **Implementation:**
reuse MiniWoB's state/action serializer and task checker; put the planner and verifier behind one
omp browser/eval example. **Risk:** 130 ms is too slow for every pixel frame and the browser bridge
is invisible to ordinary tool hooks; operate at step boundaries and compare against scripted floors.

### 23. AX-tree pruning with full-tree fallback

**Mechanism:** Use batch Nouls to prune irrelevant accessibility nodes before a planner call, but
send the full tree when confidence is low or the task is unrecognized. **User perception:** native
Mac/browser agents become cheaper without mysteriously losing a button. **Implementation:** start
with a shadow decision over real `computer`/`browser` AX trees, preserve parent/label paths, and
measure task-checker success and token reduction. **Risk:** the existing MiniWoB pruning result
missed its 40% token-reduction bar; the next version must use a bigger, powered corpus and a
fail-safe full-tree path.

### 24. Desktop transition verifier

**Mechanism:** After a `computer.*` action, judge whether the observed AX/screenshot delta is the
expected transition, returning continue, replan, or review. **User perception:** a failed click is
caught at the step where it happened. **Implementation:** host-owned browser/computer state plus
Noul/Score; this must live on the host/eval seam because normal `tool_call` hooks cannot see
prelude computer events. **Risk:** screenshots are expensive and privacy-sensitive; begin with
AX deltas and deterministic transition checks.

### 25. Host-owned irreversible-action confirmation

**Mechanism:** A host tool, not a model hook, asks Jev to classify a proposed desktop action as
reversible, destructive, privileged, or publishable and returns a human confirmation request.
**User perception:** the confirmation explains the risk without pretending a hook can redirect the
model. **Implementation:** `set_host_tools`/native judge role, structured action metadata, explicit
human gate, and audit row. **Risk:** no hook can see all browser/computer actions, and a judge is
not authorization; fail closed to human review.

### 26. Jev-PUCT prior/value for turn-based text games

**Mechanism:** Use Jev Choice probabilities as a prior over legal Jericho actions and Score/Noul as
a leaf value inside tree search, replacing unavailable LLM token log-probs. **User perception:**
a small, inspectable game agent searches rather than merely reacts. **Implementation:** Jericho
local environment, legal-action enumeration, transposition cache, and external game score as truth;
compare against MC-DML/Stockfish-like baselines under fixed calls. **Risk:** current chess-like
search evidence is mixed and calls are too slow for real-time games; target turn-based games only.

### 27. Clock-aware Pokémon decision controller

**Mechanism:** Jev ranks legal battle actions while a deterministic expectiminimax/clock manager
handles search depth, opponent uncertainty, and timeout-safe moves. **User perception:** the agent
gets a compelling local visual demo where the judge's stable decisions matter under a real clock.
**Implementation:** local Pokémon Showdown/poke-env, replay outcome and wall-clock labels, first
replay prediction gate then local battles; never public-ladder without approval. **Risk:** Metamon and
other agents are the real SOTA, and Jev may be a bottleneck; claim only like-for-like LLM-agent and
clock metrics.

### 28. Real-time reflex anomaly monitor

**Mechanism:** Instead of choosing every frame, Jev judges only event windows (collision, stall,
new object, unexpected reward) and returns continue/replan/abstain. **User perception:** a fast
controller stays deterministic while Jev catches semantic surprises. **Implementation:** 5--10 Hz
or event-triggered calls, batch observations, and environment score as truth. **Risk:** per-frame
Jev is too slow and scripted agents dominate symbolic games; the event trigger must be measured.

### 29. Game trajectory step monitor

**Mechanism:** After each planned game action, a Noul asks whether the recorded state transition
supports the intended subgoal; a failed check repairs or rolls back the plan. **User perception:**
search failures are localized to a step, making long trajectories debuggable. **Implementation:**
replay logs, environment state/checker, bounded evidence state, and a deterministic replan policy.
**Risk:** self-authored subgoals are weak labels; use environment score/checker or replay outcome as
the ground truth and report false alarms.

### 30. Task-difficulty/model/effort router

**Mechanism:** Score task state for expected difficulty and route simple work to a fast model/tool,
complex work to a stronger model, or review; use a human-validated outcome ledger to fit the router.
**User perception:** latency and cost fall without a blind confidence threshold. **Implementation:**
state features plus Jev Score/Choice, a conservative abstain band, and native omp model-role routing.
**Risk:** current cascade evidence is not useful and a threshold can move across datasets; fit on
held-out local traffic and require a cost-quality bar, not savings alone.

## Winnowing: the five worth building first

The five below are ranked by four criteria from `AGENTS.md`: a consumer exists today, a non-authored
or naturally accruing ground-truth path exists, the first measurement is cheap, and the result can
act. They also follow `NEXT-STAGE-PLAN.md`: freeze new surfaces until the kernel and consumer path
exist; then make the omp loop real and make the stranger path short.

### 1. OMP shadow decision plane with outcome feedback

**Pitch:** Put one Jev decision into the loop that already fires hundreds of times, silently first,
and make its future threshold depend on real human outcomes rather than a hand-written benchmark.

**Why first:** This is the only candidate with an immediate consumer in our daily system. The current
`.omp/hooks/post/jev-gate-observe.ts` already receives bash results, redacts commands, skips secrets,
records usage, and never blocks. The measured criteria arm is promising but not sufficient for a
blocking gate; the real-data weakness is exactly why shadow mode is the correct next step. This
turns traffic into a durable dataset instead of another one-off benchmark and directly advances
Joshua's "actually usable" request.

**Loop:** post-tool event -> deterministic applicability/secret filter -> Jev five-Noul bundle ->
`pass`, `review`, or `flag` -> redacted hash receipt -> human action/reviewer label later. Keep
computer/browser prelude calls explicitly out of scope until a host-owned seam covers them. Use a
per-seat cut and abstain band; never block on the first iteration.

**User perception:** no surprise latency or veto during rollout; occasional high-value review
suggestions with a reason and evidence hash. Once a held-out bar passes, a separate opt-in blocking
policy can be enabled, but the healthy path stays silent.

**Implementation:** extend the existing hook and `work/jev-client`; add the outcome join, register
reader, cost/latency report, and a `jev doctor` check. The first deployment is `.omp` project scope,
not a new MCP server. Keep the current fail-safe and `billing-hold` behavior.

**Bar and falsifier:** preregister a real-traffic slice and a review-label protocol; require a
specified catch rate at a fixed false-alarm ceiling against the existing gate and a deterministic
baseline. If the seat does not beat its constant or labels do not arrive, keep it observe-only.
This is a product loop, not a Jev accuracy claim until that live receipt exists.

**Confidence:** High. Existing seam, existing measured signal, real consumer, reversible rollout.
Main uncertainty is label quality and blind eval/browser traffic, not implementation feasibility.

### 2. `jev-kit`: the five-minute reliable decision package

**Pitch:** Make the sanctioned client, validator, state-size preflight, fail-safe policies, fake
asker, and receipt format the product strangers install and use in one short command.

**Why second:** README already has many recipes, but the actual reusable unit is buried in
`work/jev-client` and custom demos. A stranger should not need to infer that the official SDK owns
the wire, that no-key means NOT_RUN, or that malformed answers go to review. A thin kit is directly
accretive: it consolidates code already proven in the client and demos, rather than inventing a new
framework.

**User perception:** `jev-kit choice`/`jev-kit score` looks like a boring, trustworthy typed library;
`jev-kit doctor` tells them why a live call was not made; `jev-kit quickstart` proves the same policy
with a fake asker and then prints the exact live command. The package's most important feature is
honest degradation, not a clever prompt.

**Implementation:** TypeScript first on the official JS SDK, with Python parity only where the
existing Python ecosystem has a real consumer. Export `askJev`, Choice, Score, Noul, Bundle, size
preflight, validator, confidence/review combinators, and receipt types. Add a one-command stranger
runner and generated README results from receipts; do not add runtime dependencies to the core.

**Bar and falsifier:** fresh-clone offline suite, hostile-answer tests, size and answer-offered
preflight, and one live smoke with model/cost/latency recorded. If the kit cannot reduce a new
consumer to fewer files and fewer failure modes than direct `work/jev-client`, it is not a kit.

**Confidence:** High. The architecture and failure taxonomy already exist; the risk is packaging
scope, which a TS-first thin cut controls.

### 3. Unified experiment kernel and receipt protocol

**Pitch:** Stop writing a new runner for each experiment: one kernel should refuse impossible bars,
run pinned requests, resume safely, score with the source oracle, and emit one receipt.

**Why third:** The project is currently losing days to repeated harness defects: state-size errors,
grader leaks, wrong arms, stale labels, and bars that arithmetic could have rejected before spend.
`NEXT-STAGE-PLAN.md` already names this as the bridge from research lane to product loop. It is not
ceremony if every check controls a live decision and the same kernel drives future omp consumer
measurements.

**Mechanism:** `bar-reachable.py` + answer-offered check + `jev-state-size.py` + code/module hashes
+ `oracle-kit` scorer/e-process + lazy SDK client + partial receipt/resume. A run has a stable state
schema, question schema, model id, bar, data digests, cost, and explicit boundary. The kernel must
accept a true feasibility arm and a planted failure arm before it spends.

**User perception:** authors get a refusal before a bill, a restartable run after a pane dies, and a
receipt they can re-score without the API. Reviewers see one familiar shape instead of twelve bespoke
scripts.

**Bar and falsifier:** port one existing live experiment and one new OMP shadow experiment through
the kernel without losing a guard; inject over-limit, unreachable-bar, malformed-answer, and
resume-corruption plants. If it only wraps commands without preventing a historical defect class,
it fails the creation gate.

**Confidence:** High. The needed parts already exist and the failure history is unusually concrete.
The main risk is over-generalization; implement the smallest kernel that consumes two real runs.

### 4. Native omp `judge_batch`/`jevify` as the daily bulk decision surface

**Pitch:** Give agents a native, host-owned way to judge thousands of local rows with prefiltering,
budget accounting, abstention, and a receipt, instead of each user writing a loop.

**Why fourth:** omp 18.3 already ships the fundamental surfaces (`judge`, `judge_batch`, `jevify`,
`toks`, and `find`). The project should not rebuild that infrastructure. Configuring a project
judge role and adding one honest bulk contract makes Jev accessible to every omp agent and provides
an actual AI Map Reduce use case, one of the categories this lane has barely tested.

**Loop:** freeze the question/rubric and prefilter before loading rows; batch judged states; read
only flagged rows; emit prevalence, input tokens, latency, refusal/abstain counts, and sampled
outcomes. First examples: diff triage, stale artifact compatibility, and local tool-result
review—not arbitrary claims over secret files.

**User perception:** `jevify file.jsonl --question ...` feels like a useful command, not an
experiment notebook. The host owns the key, the user sees what was sent, and a missing judge role
is a named NOT_RUN rather than a fake answer.

**Bar and falsifier:** a 5-minute fresh-clone command, zero-secret/size guards, a non-authored
label set, and a batch receipt that closes the denominator. If bulk throughput or state size makes
the cost/latency worse than a deterministic filter, the seat is refused for that task.

**Confidence:** Medium-high. omp owns the right primitives; profile/key exposure and safe bulk data
boundaries remain to be proven.

### 5. `jev_select`: powered best-of-N trajectory selection for omp subagents

**Pitch:** Use Jev's calibrated Choice distribution to select among several independently produced
agent attempts, then let an external task checker grade the chosen attempt.

**Why fifth:** This is the clearest bridge from an existing public ground-truth corpus to an omp
consumer: the same tool can choose among subagent trajectories, browser plans, or coding attempts.
The first 24-task OSWorld retry was correctly stopped, not failed: the best single already had
22/24 exact completions, so McNemar could never reach the bar. A full-power non-overlapping task
universe is the required retry, not a lower bar or another small smoke.

**Loop:** run N candidate agents under the same task/state budget; hide archive/model labels and
outcome fields; Jev Choice ranks completion evidence; external checker scores the selected attempt;
report best-single/oracle/selection, exact discordances, cost, and latency. In omp, the same
contract becomes `jev_select` over subagent result bundles.

**User perception:** "try several cheap attempts, choose the one with evidence" is more useful than
another model chat, and the selected trajectory remains inspectable. The selector can abstain when
evidence is insufficient.

**Bar and falsifier:** preregister a large enough task universe for the exact McNemar bar and run
`bar-reachable` before calls. If best-of-N's candidate diversity is too low, or Jev cannot beat the
strongest single candidate on the external checker, the product surface remains a diagnostic/tool
for later data rather than a claim.

**Confidence:** Medium. Ground truth and implementation path are strong; candidate diversity and
power are the measured unknowns. The prior 24-task stop is positive evidence that the gate works.

## Why these five beat the other twenty-five

The top five are not the five most novel slogans. They form one accretive product loop:

1. The shadow plane supplies organic decisions and outcomes.
2. `jev-kit` gives strangers and internal tools the same safe primitive.
3. The kernel makes every measurement reproducible and refuses the historical failure modes.
4. Native `judge_batch`/`jevify` makes the primitive useful at volume inside omp.
5. `jev_select` gives the project a concrete high-value action with an external checker.

They cover both audiences in the request: daily omp users get a silent decision plane and bulk
judge; strangers get a five-minute package; the lane gets one kernel instead of repeated runners;
and the most compelling existing computer-use direction gets a correctly powered path instead of a
small demo.

The rejected or deferred ideas are not worthless. Game ideas 26--29 are excellent demos once the
kernel is working, but they have higher latency/SOTA risk and weaker immediate omp consumption.
AX pruning and browser transition checking are promising, but current pruning evidence missed its
token-reduction bar and browser/computer prelude calls are invisible to ordinary hooks. Diff review,
claim check, rerank, and compaction are already wired; their next increment is outcome feedback or
promotion, not another standalone tool. `jev_select` is explicitly not the prior underpowered
OSWorld result: it is a new, powered design with the same bar and external scorer.

## Execution order and stop rules

1. Wire shadow logging and labels into one real omp traffic path; do not block.
2. Extract `jev-kit` only as the interfaces the shadow consumer and quickstart share.
3. Move the next live experiment through the kernel; add e-process/resume only when consumed.
4. Enable native omp judge/batch in a project profile and dogfood `jevify` on non-secret data.
5. Re-run `jev_select` only after `bar-reachable` proves sufficient discordant headroom.
6. Promote a blocking/action-taking surface only after its live receipt, false-alarm/quality bar,
   and independent check pass. Otherwise keep it shadow, diagnostic, or close it with a retry.

Success means: one Jev decision runs on organic fleet traffic every day, a stranger goes from clone
to first offline/live decision in under five minutes, the next harness defect is refused before
spend, and at least one action-taking selector survives an external checker. These are product
signals, not claims that Jev wins every task.

## Explicit non-claims

- This document does not claim that any proposed feature is implemented.
- It does not claim live accuracy, calibration, SOTA, omp validation, or spend for any idea.
- It does not overwrite the missing `NEXT-SCODE-PLAN.md`; the current proposal read was
  `NEXT-STAGE-PLAN.md`.
- All confidence labels above are design confidence based on existing architecture and evidence,
  not model confidence and not a Jev oracle result.

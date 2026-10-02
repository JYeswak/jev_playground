# BREADTH: in-loop agent decisions (WildCarp, jev-r524, 2026-10-02)

Community's largest category, never tried here: Jev deciding *inside* the agent
loop (next tool, stop/continue, cheap/strong, verify-before-act). Sources:
`docs-mirror/typesafe/{cookbooks/function_calling.md,patterns/{intent-routing,confidence-routing,fan-out,composite-scoring}.md}`,
`upstream/{gargpratyush/jev-router,0xNatoshi/jev-codex-router,thruwire/foreman}`.
Related in-flight vein (not counted below): retry-worthiness Noul (jev-msax).

Labels throughout come from what the main model actually did next in
`~/.omp/*/agent/sessions/*` (toolCall name/args + toolResult exit), never typed.

## D1 — NEXT-TOOL Choice (function_calling pattern)

- **Decision:** which tool the turn needs next.
- **State:** current user prompt + last tool result (truncated 1k chars).
- **Questions:** one Choice over {bash, read, write, edit, search/find, answer-directly}.
- **Action:** pre-warm/parallelize the predicted call; skip a predicted-redundant read.
- **Label source:** the tool the main model actually called next (session files).
- **Baseline:** always-bash (plurality) or repeat-last-tool.
- **Why it might win:** tool choice is low-entropy given (prompt, last result);
  a Choice over 6 closed options plays to Jev's best primitive. Nothing like it tried here.

## D2 — READ-MORE vs ACT Choice

- **Decision:** after a read, read more or act.
- **State:** just-read content (truncated) + task text.
- **Questions:** Choice {read-more-files, act-now}.
- **Action:** when act-now wins at high confidence, nudge the loop to act (or flag read-loops).
- **Label source:** whether the next action after a read was another read (label read-more) or an edit/write/answer (label act).
- **Baseline:** always-act (majority; reads usually suffice).
- **Why it might win:** read-loops burn context; the pattern is visible in one state.

## D3 — SUBTASK-DONE Noul (Foreman pattern)

- **Decision:** is the current (sub)task complete.
- **State:** bead/task text + last N tool results.
- **Questions:** Noul "the task is fully done, nothing left to verify".
- **Action:** stop/escalate early instead of another verification lap.
- **Label source:** br close reasons + DONE callbacks vs continued turns after similar states.
- **Baseline:** always-continue (never stop early).
- **Why it might win:** Foreman's factory results; our loops run long verification tails.

## D4 — PER-TURN MODEL TIER Choice (jev-router pattern)

- **Decision:** cheap tier or strong tier for this turn.
- **State:** user prompt text only.
- **Questions:** Choice {fast-tier, strong-tier} (+ Score complexity as tie-break).
- **Action:** route the turn; fail open to strong.
- **Label source:** WEAK — no per-turn counterfactual on our data (success is session-level, single-model). Proxy: task-outcome by prompt class.
- **Baseline:** always-strong.
- **Why it might win:** community backtests claim -60%; our prompts are bursty (cheap status vs hard debugging). Ranked low on label quality.

## D5 — CONFIDENCE-GATED RISKY ARGUMENTS (function_calling spec pattern)

- **Decision:** are this call's arguments the right ones.
- **State:** proposed command + argument specs (closed sets: paths must exist, flags valid).
- **Questions:** Choice over argument values + Noul "stated?" per argument (leave default when unstated).
- **Action:** rewrite/block a risky call before it runs (rm paths, push --force targets).
- **Label source:** toolResult exit + subsequent fix-up commands (arg was wrong iff a fix followed).
- **Baseline:** run unmodified.
- **Why it might win:** argument errors are the common failure mode our gate scores post-hoc; deciding pre-call saves the call.

## D6 — FAN-OUT TURN TRIAGE (fan-out pattern)

- **Decision:** fast path, full loop, or ask-user for this turn.
- **State:** user prompt (+ last result if mid-task).
- **Questions (one request):** intent Choice + complexity Score + risk Noul, confidence-gated.
- **Action:** trivial turns skip tool loops; ambiguous turns ask once instead of guessing.
- **Label source:** turns that ended in zero tool calls (fast-path label) vs multi-call vs user-clarification turns.
- **Baseline:** always full loop.
- **Why it might win:** single request, three answers; confidence routing is the documented composition and our turns are visibly bimodal.

## D7 — RANK-THEN-VERIFY FILE SELECTION (rank-then-verify)

- **Decision:** which file to read/edit for this task.
- **State:** task text + candidate file list (from glob/grep, top 20).
- **Questions:** Choice rank top-1 + Noul verify ("this file serves the task").
- **Action:** read the verified file first; skip unverified tail.
- **Label source:** which file the agent actually read/edited next (session files).
- **Baseline:** glob order / first grep hit.
- **Why it might win:** mirrors our verified find-triage wins (jev-04q2/ynn7) moved one step earlier, before the read.

## D8 — STUCKNESS COMPOSITE (composite-scoring pattern)

- **Decision:** is this loop stuck.
- **State:** last K turns (tool names + exits + short outputs).
- **Questions:** Nouls {no-progress, repeating-same-call, error-unchanged} composed by OR/max.
| design | N | base rate | cheapest baseline | verdict |
|---|---|---|---|---|
| D1 next-tool | 54,882 transitions | 0.349 (always-bash) | plurality tool | FEASIBLE, best candidate |
| D2 read-more-vs-act | 6,348 post-read | 0.718 (always-act) | majority | FEASIBLE, high bar (~0.82 to matter) |
| D8 stuckness | 19 windows / 8 sessions | n/a (no detector) | fixed-lap-cutoff | NOT ENOUGH DATA at 24 files; widen before exit |

## Preregistration

Best of the three above -> bead comment on jev-r524 before any live call.
Live only after conductor KEY OK (Infisical v4 migration).

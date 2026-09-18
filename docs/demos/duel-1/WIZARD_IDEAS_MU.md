# Duel-1 ideas, muse side (duelist B)

Duel brief: 15 ideas → winnow to 5, best→worst, each grounded in a
`docs/demos/USAGE-MAP.md` section. Below: the 5 (MU-1..MU-5, full rationale),
then the 10 winnowed out with one-line reasons, then source-refused items
that were never mine to propose. No invented sources: every number below is
quoted from the map, `docs/demos/PLAN.md`, or `compaction/runs/ab-20260917.json`.
Existing demos are extended, never re-proposed: compaction hook (#1), replay
harness (#6), A/B kit (#2) appear only as infrastructure their follow-ups ride.

Ordering rule for the 5: PLAN.md's **value × readiness**.

---

## MU-1 — omp routing backtest: what would routing have saved (BEST)

**Map §4 (per-turn model routing).** `jev-codex-router@8292b51` measured −60%
vs full-frontier on a 7-day replay of 237 real turns (`BACKTEST.md`),
$0.00003 + 0.6s per decision, fail-open, kill switch, local decision log.
Map's own verdict: *"Most directly valuable to us."*

**What.** A CLI that replays recorded omp session transcripts (the
`compaction/fixtures/*.jsonl` shape through `compaction/src/omp-adapter.ts`),
asks Jev per turn whether the turn needed frontier (Choice, or Noul
"needs-frontier"), applies a threshold policy that is *our* code, and emits:
turns that would have routed down, estimated $ saved against a committed
per-model price table, decision latency distribution, and agreement vs the
model that actually served each turn (oracle proxy) plus spot human labels.

**Install.** `demos/routing-backtest/`, one command
`npm run backtest -- <transcript.jsonl> [--out runs/<ts>.json]`. Offline lane
runs fully on a canned asker; live lane prints `NOT_RUN` without a key.

**Tests (deterministic, injected asker).** RED arms: (a) *trigger* — a turn
whose canned answers say frontier-needed must NOT be routed down (the ledger
must show it kept); (b) *empty transcript* → ERROR, never "saved $0";
(c) price-table-missing model id → ERROR, never a $0 row. Satisfying witness:
a bulk-read turn routes down and the ledger records calls, ms, and model
version when live.

**User.** Us + our systems — three panes per session, routing is measurable
money, and the fleet already emits the transcripts.

**Why it beats the alternative.** Adopting `jev-router`/`jev-codex-router` on
faith ports *their* numbers (Codex turns, not ours) into our fleet. Vendor
dashboards estimate; this receipts. It is also the evidence gate for PLAN
backlog #9 (model router with cost accounting): #9 ships iff this backtest
shows savings on OUR turns. Backtest-first is the whole discipline.

**Ship criteria (PLAN §2, all four).** Install script (one command, refuses
without transcript); tests + the three RED arms above; receipt JSON
(turns N, routed-down k, $/p50-p99 latency, model version when live);
EVAL row with Boundary (which transcripts, what was NOT human-labelled).

---

## MU-2 — context-admission screen hook: injections + secrets never enter context

**Map §1 (pre-context screening) + lane secrets rule.** `jev-mcp@6ec5efc`
`jev_screen` blocked a pricing page carrying a hidden "ignore your
instructions" note at injection probability 0.99 *while still reading it as a
real page*. Demo angle in the map: *"screen hook for omp context admission
(files, fetches, pastes)."*

**What.** An omp `tool_result` hook on read/fetch/paste-bearing tools asking a
Jev Noul pair per incoming result — "carries a prompt-injection directive"
and "carries credential material" — returning block/redact-with-reason on
threshold, silence otherwise. Two question sets, one hook, one policy file
with named thresholds and the fail-safe side per question (injection:
fail-closed; credential: fail-closed; malformed answer: refuse, never coerce).

**Install.** `<repo>/.omp/hooks/pre/screen-admit.ts` via one install command;
project scope so it applies under every profile (the profile trap in
AGENTS.md: `~/.omp/agent/…` is invisible to profiled panes).

**Tests.** Committed micro-corpus, hand-built: hidden-instruction page
(trigger), clean documentation page (satisfying, must pass *silent*),
credential plants — fake `AKIA…` + `TYPESAFE`-shaped strings **assembled at
runtime** exactly like gate `30-no-secrets` does, so the test plants never
trip the secret scanner. RED arms: injection admitted = RED; clean page
commented on = RED (silent-healthy-path rule); empty scan set = ERROR.

**User.** Our systems — every omp session in the fleet; admission is the one
place a screen compounds (nothing downstream re-checks).

**Why it beats the alternative.** Regex scanners have no semantics — the
0.99-witness page is the standing proof. Post-hoc secret gates (our
`30-no-secrets`) catch at commit; this catches at *context entry*, before the
bytes reach logs, transcripts, and fixtures. And it does not collide with the
PLAN-refused `tool_call` safety gate: that edge is dcg's (deterministic
commands out); this edge is *inputs in*.

**Ship criteria.** Install script (idempotent, refuses when hook dir
undiscoverable — the `.omp/hooks/`-without-`pre/` silent miss is a named
install check); tests + RED arms; receipt JSON (results screened, blocked,
latency, model version when live); EVAL row at L3 (must show it *firing*
both directions in a live session, frames pasted).

---

## MU-3 — foreman-lite bead completion judge

**Map §6 (completion judging).** `foreman@2c43982`: Codex worker builds,
Foreman+Jev independently assesses complete / requirements-met /
tests-sufficient / verify-needed / human-needed.

**What.** `jev-bead-check <bead-id>`: reads the bead's WHAT/ACCEPTANCE via
`br show`, diffs the work since the bead started, and returns a typed verdict
from the foreman dimension set plus an evidence checklist (which acceptance
line each diff hunk answers). Exit nonzero on verify-needed or worse, so it
composes as a pre-close gate: `jev-bead-check <id> && br close <id>`.

**Install.** One script + a bead-workflow doc page. No daemon, no server.

**Tests.** Canned asker; RED arms: (a) bead with an **empty diff** must return
human-needed, never complete (the self-certified-close killer); (b) diff that
deletes the acceptance-cited file must return verify-needed.
Satisfying witness: a small diff answering every acceptance line returns
complete with the checklist. Empty bead body (title-only) → ERROR.

**User.** Us — this lane closes beads all day, and a close with no
independent check is a CLAIM without an oracle (AGENTS.md claim discipline).

**Why it beats the alternative.** Self-certified closes (today's state) and
chat-model review (untyped praise, no probabilities, no threshold, no
fail-safe side). Typed verdicts + our thresholds + a checklist a human can
audit in seconds.

**Ship criteria.** Install script; tests + RED arms; receipt JSON (bead id,
verdict, per-dimension scores, model version when live); EVAL row with
Boundary. Calibration path from day one: our own closed beads are the
labelled set (WHAT + diff + whether follow-up bugs appeared).

---

## MU-4 — working-point claim-checker (the lane's write-down discipline, executable)

**Map §2 (claim verification).** `jev-mcp@6ec5efc` `jev_verify` caught a
contradicted claim at confidence 1.0 against a city ordinance. Map's demo
angle: *"verify working points against cited evidence before writing them
down. Dogfoods lane discipline."*

**What.** `jev-claims <notes.md> --evidence <dir>`: extracts verifiable
working points from a working file, checks each against the cited evidence
(Jev Noul "supported by this evidence", with an explicit insufficient-context
outcome that maps to *withhold*, never to *approve*), and reports
supported / contradicted / insufficient with confidence. Exit nonzero on any
contradicted claim.

**Install.** Single command (`uvx`/`npx`), stdlib + one HTTP client.

**Tests.** Committed micro-corpus: a supported pair, a contradicted pair in
the city-ordinance style, an insufficient-context pair that must come back
*withhold*. RED arms: contradicted-must-refuse; empty evidence dir → ERROR
(never "all supported"); unlabeled citation (claim pointing at no file) →
insufficient, never supported.

**User.** Us — EVAL rows, duel files, receipts, close-out reports: everything
this lane writes down, checked before it lands.

**Why it beats the alternative.** Manual re-reading doesn't happen under
load; chat-model proofreading hallucinates approval with no probabilities
and no threshold to tune. This is AGENTS.md's "signals must name what they
observed" as a runnable gate, and its misses become the labelled negatives
the next calibration run needs.

**Ship criteria.** Install script; tests + RED arms; receipt JSON
(claims checked, verdicts, confidences, model version when live); EVAL row
with Boundary. Calibration seed from day one: our own EVAL rows are
supported-pairs; negatives are authored by perturbing a citation (cheap,
reviewable, committed).

---

## MU-5 — signal-kit: signals, not verdicts (the A/B meta-lesson, packaged)

**Map §9 (zero-label classification).** `jev-phishing-bench@1d56e8c`: Jev
verdict alone loses (62.6 vs 81.3) but **5 signal questions → logistic
regression hits 95.1%, AUROC 0.988, ECE 0.027**; fixed rules on strong
signals need no fitting (free-hosting rule alone: 89.5%). TF-IDF needed
100–10,000 own-distribution labels to match and collapsed 20+ points on
shifted mail. Map's demo angle *and* the standing lesson for our A/B: ask
signals, fit tiny models, don't trust verdicts.

**What.** A starter template, not a model: ask K signal questions per item
(never one verdict), fit a tiny logistic regression on user labels, emit a
calibration report (accuracy, AUROC, ECE + bins, flip rates between passes)
**plus a net-floor control** (best fixed rule alone). Ships with a committed
synthetic micro-example so the template runs offline end-to-end.

**Install.** Template dir, one `uv run` command: `fit → report → refuse`.

**Tests.** RED arms: (a) **fit-refusal** — shuffled labels must yield "no
signal found", nonzero exit, never a fitted model; (b) empty corpus →
ERROR; (c) the synthetic example must reproduce its committed report within
tolerance (verdict-only baseline loses by a stated margin — the 62.6-style
witness, pinned in-repo).

**User.** AI space first (every "should I trust this classifier" question);
us second, with an honest gate: apply it to resume-quality signals **only
once A/B receipts accumulate past N≥50** (today N=4 — fitting now would be
the cherry-picked-N violation). The retry condition is part of the demo.

**Why it beats the alternative.** Verdict-trusting (the 62.6 lesson),
label-hungry baselines (100–10,000 labels; 20-point shift collapse), and
"just prompt better" (unmeasured). Distinction vs PLAN backlog #7
(classifier-eval template): #7 answers *"should I use Jev"* (eval);
signal-kit answers *"how do I ship it"* (signals + fitted head + refusal
arms + calibration report). Complementary, not duplicative.

**Ship criteria.** Install script (template renders + runs with zero edits on
the synthetic example); tests + RED arms; receipt JSON (metrics, bins,
model/fit versions, Jev model version when live signals were used); EVAL row
with Boundary (synthetic-only until a user corpus lands).

---

## Winnowed out (10)

- **R1 — failure-attribution probe (§7).** Real pain (ours fail often), but
  labels don't exist: needs Who/When/What span-annotated failed runs.
  *Retry: annotate the next 20 failed runs, then promote.* (§7 numbers —
  6,257 traces, ~$1.28 input-only billing — say the per-run cost is trivial;
  the annotation is the cost.)
- **R2 — per-call context-hook keep/drop (§14, omp seam #2).** A different
  seam than shipped #1 (`session_before_compact`), but still #1's phase 2.
  WIP limit of one; queue behind #1's L3.
- **R3 — fact-ledger sidecar (§14 lesson).** "Pair with fact ledger" rides
  #1's `preserveData`, and Jev can't generate ledger text (constrained
  answers only — generation needs a delegate). Follow-up, not standalone.
- **R4 — resume-question synthesizer (§14 / ab receipt).** Generating the
  A/B's resume questions belongs *inside* #2 (A/B kit), not as its own demo.
- **R5 — keep/drop calibration audit on A/B receipts (§13).** Correct idea,
  dishonest N: 4 labels can't calibrate anything. Same N≥50 gate as MU-5's
  us-application.
- **R6 — blind hook-quality bench (§12).** "Our gates' future" is right, but
  sequence is wrong: blind sets judge *shipped L3 hooks*; #1 isn't L3 yet.
  Queue behind it. (Corpora noted for then: 662 deepset msgs + 200
  vuln-code pairs.)
- **R7 — choice-gate CLI template (§11).** PLAN backlog #4 owns it; no new
  angle offered here.
- **R8 — rerank recipe for our retrieval (§3).** PLAN backlog #8 owns it
  ($0.45 vs $2.51, nDCG 0.692 vs 0.691 already measured upstream); no new
  angle.
- **R9 — pre-commit review lane (§5).** PLAN backlog #5 owns it
  (`applicable:false` handling included).
- **R10 — commit-triage policy wrapper (§8).** `commit-miner` is already
  `cargo`-installable; our wrapper adds alert routing only, and only pays
  when we cut a new dependency. Defer to first need.

## Refused by sources (never candidates)

- Browser-action demo (§10): map says *"none immediate (needs browser
  harness)"* — cited for the constrain-then-delegate pattern only.
- `tool_call` safety gate: PLAN explicitly refuses (dcg owns that edge;
  differential probe would be an eval, not a demo).
- Portable calibration micro-harness (§13): PLAN backlog #3 owns it
  (foundation ECE 0.061 / Brier 0.020 receipted).

# Q2 falsifiers — COD-H1, COD-H4, COD-H5 (cheapest observation first)

Status: falsification designs, not kills, not executed experiments.
Shape modelled on `FALSIFY_MUH1_COD.md` (`0f619de`) and my Q1 file:
chosen falsifier, exact command (design target), fixed rubric where
labels are needed, predeclared failure rule with Wilson bounds, explicit
HELD/UNASKABLE paths, receipt schema, NO-CLAIM. Label-free halves come
first wherever one exists.

---

## F-H1 — completion evidence: checkable-claim prevalence + incumbent overlap

H1's demand rests on sessions containing completion claims worth
verifying. backcheck's own README volunteers the base rate against it:
"Most sessions make no checkable claim." If that holds generally, H1's
per-session product fires rarely no matter how good its verdicts are —
and the two deterministic incumbents (backcheck, evigate) already serve
the sessions where claims exist.

**Primary falsifier (label-free): checkable-claim prevalence.** Sample
M≥30 real agent transcripts across ≥3 harnesses (not Claude-only —
H1's wedge is portability, so single-harness prevalence proves
nothing). Deterministically enumerate checkable completion claims with
fixed patterns (test/lint/build/commit/done assertions adjacent to
tool calls; patterns committed in the fixture, no model). Failure:

```text
sessions_with_>=1_checkable_claim / M < 0.20
AND Wilson95_upper < 0.35
```

Fewer than 1 in 5 sessions contain anything to verify: the addressable
surface is thin, and H1 becomes a history-mode aggregator (which
backcheck's `history` command already is, at 30ms a session) rather
than a per-session gate. HELD — re-scope as batch audit tooling, which
is a different product with a different buyer.

**Secondary falsifier (needs installed backcheck, zero LLM):** run
`backcheck history`-equivalent over the same corpus; count sessions
where backcheck reports unsupported/contradicted/qualified. If that
count is ~0 AND prevalence (above) is healthy, claims exist but are
already true — nothing to adjudicate, Jev layer unneeded. If backcheck
finds plenty, H1's remaining wedge is strictly the cross-harness +
`unknown`-zone adjudication; price the demo at that wedge, not at
"completion verification" in general. Either branch is decided by one
afternoon with a borrowed binary, not by building H1.

**Non-failure outcomes:** <30 transcripts or single-harness only →
HELD (sample too narrow for a portability claim); pattern file misses
a whole claim class discovered by spot-check → HELD, fix patterns;
prevalence healthy but backcheck absent on non-Claude harnesses →
falsifiers did not fire, proceed to Jev-adjudication measurement on
the `unknown` zone only.

**Command (design target):**

```sh
evidence-falsify prevalence \
  --transcripts fixtures/h1-multi-harness.json \
  --claim-patterns fixtures/h1-claim-patterns.json \
  --out runs/h1-prevalence.json
```

Receipt: manifest/transcript shas, pattern-file sha, per-harness
rates, Wilson bounds, verdict. Empty denominator is an ERROR.

## F-H4 — admission replay: corpus-build cost

H4's flagged weakness ("corpus doesn't exist yet") is itself the
cheapest falsifier: a benchmark whose corpus cannot be built cheaply
is a rung-3 cost knowable now. The demand claim underneath — hostile
tool results are common enough to need a regression corpus — gets
tested as a byproduct.

**Primary falsifier: 30-case pilot corpus in ≤4 hours from public
sources only** (deepset injection messages, linked MCP/AutoGen/Agent-S
issue attachments, hand-written mixed pages). Each case needs a known
label (attack/benign/mixed) plus the privileged action it threatens.
Failure (either branch):

```text
cases_assembled < 30 in 4 hours → HELD (corpus cost kills the benchmark tempo)
OR hostile_rate_in_real_sample < 0.05 with Wilson upper < 0.10 → HELD (nothing to regress)
```

The second branch needs a real-traffic sample: 200 tool results from
our own logs, human-labelled hostile-or-not by fixed rubric (one hour,
same shape as Q1's labelling half). Both branches are predeclared;
hitting either holds H4 before a single replay-runner line is written.

**Secondary falsifier: vendor-guard redundancy probe.** Run the pilot
corpus through one existing free guard (Vigil/Rebuff, installed per
docs, $0). If it scores ≥95% detection at ≤5% FP on the pilot, H4's
remaining wedge is *only* the cross-framework replay artifact — worth
having, but priced as corpus infrastructure shared with Demo-2, not
as a 900-demand standalone. If the guard misses a whole attack class
the corpus contains, that class is H4's charter. Either way one
afternoon decides it.

**Non-failure outcomes:** public sources exhausted below 30 → HELD,
widen sources (do not lower the label bar); real-traffic sample
unavailable → HELD (cannot measure hostile rate without traffic);
guard unrunnable in our env → UNASKABLE for the secondary only.

**Command (design target):**

```sh
admission-falsify corpus \
  --sources fixtures/h4-public-sources.json \
  --timebox-hours 4 --target 30 \
  --traffic fixtures/h4-real-tool-results.jsonl \
  --out runs/h4-corpus.json
```

Receipt: source list + shas, per-case labels, hostile rate + Wilson,
guard scores if run, verdict. Timebox expiry with <30 cases is the
recorded failure, not an excuse to extend.

## F-H5 — compaction integrity: determinism sufficiency

H5's flagship pain (OpenClaw #3560: flush prompt *after* truncation,
agent sees nothing, replies NO_REPLY) is a lifecycle-ordering bug with
a deterministic signature: event log shows truncate-before-flush. A
20-line log-sequence assertion catches it with no model, no
calibration, no fixture corpus. If the flagship cases fall to log
assertions, H5's Jev layer (Choice over candidate facts, Noul
provenance checks) is optional scope, and the demo should be a
deterministic boundary monitor with a Jev adjunct — HELD for re-scope,
same shape as the H3 ruling.

**Primary falsifier: reproduce-then-catch without a model.**
Synthesize the #3560 shape (transcript + forced flush-after-truncate
sequence + a flush-before-truncate control), then write the
deterministic checker (event-order assertion + fact-presence diff on
known-answer seeded facts). Failure:

```text
checker catches the seeded ordering bug AND the control passes,
on first attempt, in under an hour of work
```

That outcome proves the flagship need is served deterministically;
H5-as-Jev-demo holds, H5-as-boundary-monitor proceeds (cheaper,
narrower, honestly named). If instead the seeded cases expose
ambiguity a fixed checker cannot resolve (fuzzy fact identity across
rephrasing compactions — the case Jev adjudication exists for),
document the failing pair: that pair is H5's charter evidence and the
falsifier did not fire.

**Secondary falsifier: seeded-fact coverage.** The harness needs
known-answer facts to assert retention. If >30% of real dropped facts
cannot be seeded deterministically (they are emergent, relational, or
only visible post-hoc), the fixture-authored requirement from rung 2
starves: HELD for scope-narrowing to atomic facts, with the narrowed
scope re-priced.

**Non-failure outcomes:** synthetic shape disputed as unfaithful →
HELD, rebuild from a real incident log; checker catches nothing
because the synthetic bug is mis-seeded → HELD, fix the seed (a
falsifier that cannot catch its own planted bug proves nothing);
coverage shortfall → HELD with narrowed scope, not a kill.

**Command (design target):**

```sh
boundary-falsify ordering \
  --seed fixtures/h5-truncate-flush-seed.jsonl \
  --control fixtures/h5-flush-truncate-control.jsonl \
  --out runs/h5-ordering.json
```

Receipt: seed shas, checker source hash, catch/miss per case,
coverage fraction, verdict. A passing checker with no failing seed
is an ERROR (untested assertion, same rule as empty scan sets).

## Why these three are cheaper than their builds

Each primary falsifier is scoped to kill the demand or the Jev-need
before the expensive half: H1 prevalence needs transcripts + patterns,
not a gate; H4 corpus needs four hours and public sources, not a
replay runner; H5 ordering needs one synthetic seed and twenty lines,
not a harness. Labels appear only where determinism cannot reach
(H4 traffic sample; H1 stays label-free throughout). No Jev call, no
live provider, no implementation exists in any of the three designs —
that absence is the point, recorded in each receipt schema as
`UNMEASURED` until run.

## NO-CLAIM

Designs only. No corpus assembled, no transcript sampled, no guard
installed, no seed synthesized, no falsification result collected.
Predeclared rules above are the falsification contract; until run,
H1/H4/H5 remain rung-2 cleared with rung-1 scores intact.

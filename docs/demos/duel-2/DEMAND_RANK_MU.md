# Duel-2 demand ranking (muse) — scored on want, not on spec

Rule compliance: `PLAN.md` §3b **not read** (will state again in callback).
Ranked from §5.1–§5.9 abstracts, the written contracts, and external
research cited per demo. Duel-1 scored spec quality; that rubric is what
mis-ranked these. Here a beautiful spec nobody wants scores low.

## Ranked table

| Demo | Demand | Who downloads it | What it replaces |
|---|---|---:|---|
| demo-4 foreman-lite | 800 | Agent-framework user burned by false completion | Trusting the agent's "done" |
| demo-5 fact ledger | 750 | Anyone whose long session got amnesia'd by compaction | Re-reading the transcript / starting over |
| demo-7 signals starter | 620 | Practitioner shipping a text classifier | Prompting a verdict + hoping |
| demo-9 review signal | 550 | Team drowning in bot-noise review comments | SaaS prose bots (or no review) |
| demo-3 claim-check gate | 500 | CI operator whose changelogs assert numbers | commitlint (format only) + trust |
| demo-2 admission screen | 450 | Agent-harness builder ingesting untrusted bytes | Rebuff/Vigil/PromptGuard (generic) |
| demo-1 route backtest | 350 | Fleet operator wondering if routing would save them | Vendor savings claims |
| demo-6 claim-check notes | 350 | Evidence-note author (population: dozens) | Demo-3 applied by hand |
| demo-8 credential screen (Jev-question form) | 150 | Nobody — correctly killed | gitleaks (already won) |

## The nine, four answers each

### Demo-4 foreman-lite — 800

**Installable by a stranger?** Yes in principle: one bin, `br show` + diff
in, verdict out. In practice today the `br` coupling is lane-local — the
shipped form must define a generic task-spec interface first, or strangers
cannot run it.
**AI-wide benefit?** The false-completion problem is the most voiced pain
in the agent space this year: ten-plus articles name it ("agents say done
when the task failed", "fake done", "lying when it says done"), the field
has converged on moving the stop decision *outside* the agent, and no
dominant tool owns the independent-judge shape (one vendor, ArgosBrain, is
barely out of stealth). A typed verdict + evidence checklist is exactly the
converged shape.
**Who downloads it?** A developer running Claude Code/Codex/Cursor agents
on real tickets who has been burned by a confident "done" over broken work
— that population is most agent users, and several write angry posts about
it weekly.
**Measurably?** Before: share of agent-closed tasks requiring human rework
(incident count). After: judge-verdict vs human-verdict agreement + rework
rate. Command: the judge over a task log corpus, before/after enabling it
as a close gate.

### Demo-5 fact ledger — 750

**Installable?** As specified (ledger sidecar + rescore harness), yes —
if the deterministic extractor exists, which is still the open mechanism
question from duel-1.
**AI-wide benefit?** Compaction amnesia is loudly voiced (Claude Code
issue #23776 with lost instructions, "compaction kept destroying my work",
"lost my 4-hour session", whole careers of workaround posts). The crowded
side is heavy memory platforms (Mem0, Zep with temporal graphs, Letta) and
runtime summarizers — all of which *rewrite* history. Nobody ships the
byte-exact, provenance-per-byte alternative, which is the ledger's whole
thesis and its differentiation.
**Who downloads it?** Anyone running multi-hour agent sessions who has
watched compaction eat the one fact the session needed — a population in
the hundreds of thousands across the big harnesses.
**Measurably?** Before: resume-question recall after stock compaction
(our own 1/3). After: recall with ledger at stated byte cost. Command:
the A/B harness both ways. (Note: mechanism still unproven — demand
scores the want, and the want is documented.)

### Demo-7 signals starter — 620

**Installable?** As a template with a synthetic example that runs offline,
yes — the most hermetic install story in the set.
**AI-wide benefit?** The practice it packages is expert-endorsed
(Raschka: "always run a simple logistic regression baseline"), adjacent
literature ships LLM-features-into-small-models methods, and calibration
(ECE/bins) is live discourse — but templates for *doing it right* are
scattered across blog posts, not one runnable kit. Mid-size benefit, real.
**Who downloads it?** An ML practitioner asked to ship a text classifier
next sprint who suspects prompting a verdict is the wrong shape but has no
starter. Thousands per year.
**Measurably?** Before: verdict-only accuracy on their labels. After:
signal-model accuracy + AUROC + ECE. Command: the template's own fit and
report. Downgrade applied: its headline numbers (62.6 vs 95.1) are
unverifiable in-repo (upstream not vendored) — the template reproduces
the *shape* on user data, which is honestly all it can promise.

### Demo-9 review signal — 550

**Installable?** Unscored and unbuilt; as sketched (local hook beside
ubs), plausible. No evidence yet either way.
**AI-wide benefit?** The AI-review market is the most crowded in this
ranking (CodeRabbit, Greptile, Qodo, Cursor BugBot — one vendor claims
98% precision). But the pain is equally loud and specific: 9:1 historic
false-positive ratios, 64%-of-comments-are-style analyses, per-review
pricing complaints ("$1/review tax"), fatigue-driven uninstalls. A local,
scalar, advisory, calibrated signal that complements a static scanner is
genuinely differentiated from SaaS prose bots — *if* it stays advisory
and publishes its FP rate. That is a narrow ledge over a crowded floor.
**Who downloads it?** A tech lead who turned the SaaS bots off for noise
but still wants a cheap first pass — self-hosters and cost-sensitive
teams, real but much smaller than "everyone with PRs".
**Measurably?** Before: bot-noise FP rate + review hours. After: signal
precision/recall on a labelled diff set + hours. Command: the hook over
a diff corpus with labels. Capped at 550 because crowded + unbuilt.

### Demo-3 claim-check gate — 500

**Installable?** Yes: hook script + committed fixtures, one command, no
key needed for the offline suite.
**AI-wide benefit?** Narrow but real: commitlint owns *format* and proves
the adjacent demand (half the ecosystem enforces Conventional Commits via
Husky) — nothing checks *substance*, i.e. whether the asserted numbers
match cited artifacts. The hallucinated-benchmark-number era gives this
a tailwind no format linter can catch. But the surface is small: most
repos' commit messages carry few checkable numbers, so per-install value
is thin outside lanes like ours that assert constantly.
**Who downloads it?** A CI operator maintaining changelog-from-commits
pipelines who has shipped a wrong number in release notes. Real,
countable in the hundreds of teams, not thousands.
**Measurably?** Before: wrong-number-in-message incident count. After:
refusals with named contradictions. Command: the lane over its own
history, before/after install.

### Demo-2 admission screen — 450

**Installable?** Yes as specified (hook + policy + fixtures, offline
suite). Shadow-first is honest deployment.
**AI-wide benefit?** Prompt injection is OWASP LLM01 with a mature
detection market: Rebuff and Vigil are open source, PromptGuard/LLM
Guard/enterprise shields are maintained, benchmarks exist. The demo's
differentiator is agent-context-hook specificity (screening bytes at the
harness boundary, graded admit/block/redact) — real but incremental
against tools teams already run as libraries or proxies. Its headline
number (0.99) is upstream-unverifiable in-repo, and the niche already
has maintainers.
**Who downloads it?** An agent-harness builder ingesting untrusted
fetches who wants boundary-native screening instead of a sidecar proxy.
Hundreds, not thousands.
**Measurably?** Before: injection-containing bytes admitted silently.
After: flagged rate on a blind slice + FP rate on clean traffic.
Command: the shadow hook over both corpora. Scored below demo-3
because "well-maintained tools already own the niche" bites harder
here than anywhere except secrets.

### Demo-1 route backtest — 350

**Installable?** Yes — the only demo with a clean-clone 10/0 receipt.
Exemplary install story.
**AI-wide benefit?** This is where demand bites hardest. The routing
market is saturated and measured: LiteLLM/RouteLLM/Martian open source,
NotDiamond powering OpenRouter's auto router with a cost/quality dial,
a 400K-instance ACL benchmark (LLMRouterBench), vendors claiming
60–90% cuts. And our own measured result is **0.047%** — the demo's
honest product is evidence that *on our turns, routing barely pays*.
A backtest harness others run on their own logs has some value, but it
competes with an entire measured industry plus the finding that the
prize is small. Installable does not mean wanted.
**Who downloads it?** A fleet operator deciding whether to adopt a
router, once, before deciding. One-shot use, not a tool — closer to a
report you run than a demo you keep.
**Measurably?** Ironically the most measurable in the set (dollars to
four decimals) — and the measurement is what kills the demand: $0.0034
saved. Scored on want: low.

### Demo-6 claim-check notes — 350

**Installable?** Yes in the same shape as demo-3, gated on explicit
claim blocks.
**AI-wide benefit?** A strict subset of demo-3's: same mechanism
(claim-vs-evidence Jev check), smaller trigger surface (personal notes
vs every commit), weaker distribution (no hook point every repo
already has). Anyone wanting this wants demo-3 first; nobody wants
only this. The build-iff-demo-3 condition in its own contract agrees.
**Who downloads it?** An evidence-note author maintaining cited
research notes. Dozens.
**Measurably?** Same commands as demo-3 on a notes corpus. Fine, but
derivative by design.
(Same score as demo-1, different reason: demo-1 is measurable but
unwanted; demo-6 is wanted-by-few and derivative.)

### Demo-8 credential screen, Jev-question form — 150

**The kill was right for the form specified.** Deterministic secret
detection is a solved, maintained niche: gitleaks (instant, offline,
pre-commit standard), trufflehog (verified live secrets), GitHub
secret scanning (zero-friction default), detect-secrets. A Jev Noul
asking "does this carry credential material" is slower, paid,
networked, probabilistic — and, fatally, ships the secret to a third
party to decide whether it is one. No version of that question should
exist. Score reflects the form, not the problem.
**But the kill rationale in §5.9 misidentifies the neighboring corpse,
and that matters.** It says sanitize-before-send "already existed as
MU's winnowed R9 and in CC's long list at #5." MU R9 is a *pre-commit
review lane*; CC #5 is an *inbound injection screen*. Sanitize is
*outbound Jev-state redaction* — a third, distinct demo that neither
cited item describes. Killing the Jev-question form was correct;
declaring the redaction layer "already existed" on mistaken identity
retires an idea that never got its hearing. Sanitize belongs in the
hunt (Unit 2), not in demo-8's grave.

## Kill list

- **Demo-8 (Jev-question form): dead, rightly.** See above. Deterministic
  scanners won years ago; the question form adds a leak to a solved
  problem.
- **Demo-6: do not build unless demo-3 pays.** Its own contract gates
  it; demand agrees (derivative, dozens-strong audience). If demo-3's
  30-day contradiction rate is flat, kill demo-6 with it.
- **Demo-1's router follow-on: already dead** (plan records it). The
  backtest harness survives as a tool, not a demo to promote.

I would build five of nine (4, 5, 7, 9, 3, in that order — six named
because 2 and 3 are close; the honest cut after the top four is
uncomfortable, so: build 4, 5, 7, 9; demo-3 iff a second lane besides
ours commits to installing it; demo-2 iff no existing scanner adds a
harness hook first).

## Single pick

**Demo-4 foreman-lite.** Loudest voiced pain (named pattern, field
converged on the external-judge shape), no dominant tool, generalizes
beyond the lane via a task-spec interface, and every agent user is a
prospect. **What would make me wrong:** harness-native stop conditions
— if the big harnesses ship built-in completion verification this
year, the external judge's demand collapses to the long tail. Watch
their changelogs, not our backlog.

## NO-CLAIM

No §3b read (compliance stated for the callback). Upstream numbers
(0.99, −60%, 95.1/62.6, nDCG pair) treated as unverifiable-in-repo
throughout and downgraded wherever a demo's case rested on them; I did
not clone or run any upstream repo. Web research covered incumbents
and voiced pain per demo above (16 searches); I did not interview
users, measure markets, or verify vendor benchmark claims (60–90%
router cuts, 98% review precision taken as claimed). No demo was
implemented or installed.

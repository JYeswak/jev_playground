# Debt drafts for the conductor to rule — P3, 2026-09-21

> Four debts from round 3 (`docs/PLAN-ROUND3-20260921.md` Q1), drafted for
> merge into `docs/PLAN-EVIDENCE-MATRIX.md`. Each pays the full Rule 12
> price. Placement notes say §2 or §7.

## D1 — Docs-consistency validator: ADOPT (§2 addition)

**Text:** add a `docs-consistency` check reusing the frozen-claims shape:
walk `*.md` under versioned docs roots, re-parse every fenced JSON/TOML
block strictly (duplicate keys refused, non-finite floats refused), verify
every relative link and heading anchor resolves. Ship WITH an adversarial
twin (corrupt one anchor, demand failure) — his tree lacks it and that is
the gap we exceed, ~2h synthetic and deterministic.

**Cost:** 1 script (~200 lines stdlib, ported) + 1 adversarial test file,
~5h total. **Defect class it would NOT catch:** well-formed but wrong
numbers, stale claims that still parse. **Lose by refusing:** prose claims
rot undetected — our ARC.md rotted the day it shipped, which is the
measured need, not a hypothetical.

## D2 — Trusted evidence entrypoints: ADOPT (fold into T6a)

**Text:** T6a acceptance gains: the walker emits only entrypoints on an
allow-list (`selftest-*.sh` mains, `unittest.TestCase` classes, `*.test.mjs`
top-level cases); any other plain function is a helper, not evidence, and
is ignored rather than registered.

**Cost:** ~1h added to T6a (one predicate on the walker output).
**Defect class it would NOT catch:** helpers that fabricate evidence
consumed by a listed entrypoint (inline code, not entry shape).
**Lose by refusing:** helper-masquerading-as-evidence — a passing suite
whose "cases" are utilities, i.e. phantom coverage through the front door
T6a was built to close.

## D3 — Platform evidence honesty: SPLIT

**Adopt (§2, cheap): refusal-of-simulation.** A check that refuses to
certify platform-dependent behavior from simulated evidence: ambient
`RUSTFLAGS`/cross flags present, or the running host mismatching the
claimed target, fails loudly instead of passing quietly. Cost ~1h (env
sniffing, deterministic, no builds). Would NOT catch: genuinely broken
platform behavior (it refuses to judge, which is the point). Lose by
refusing: simulated greens — the exact class his `--native-macos` refusal
exists to stop.

**Refuse (§7): full platform-boundary matrix.** Real Darwin+Linux build
matrix with probe crates per target. Cost: days plus build hosts we do
not have (local builds denied here; workers are Linux-only). Defect class
it would not catch: none of F1–F6 (all declaration/provenance, none
platform). Lose by refusing: nothing today; retry when a boundary needs a
platform to prove. This is scope creep, not rigor.

## D4 — Axis-C scope line: §8 ADDITION (neither adopt nor refuse)

**Text for §8:** "The matrix program covers evidence *about* rules,
instruments, refutations, and seams. It does not cover Jev-client plumbing
(consent-before-key, live-ignore discipline, retry classification,
injected transport, named negative controls) — that track ships its own
gates, measured separately. Silence here is scope, stated once, not debt."

**Cost:** zero files, one paragraph. **Lose by refusing** (i.e. leaving it
silent): the next completeness audit re-raises it as an unpaid debt, which
is process churn with no information.

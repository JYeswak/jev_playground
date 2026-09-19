# commit-miner adoption test

**Candidate:** `upstream/devanshbatham/commit-miner`
**Binary:** upstream `target/debug/commit-miner`, run in `ubuntu:24.04` / `linux/amd64`
**Key path:** Infisical `infisical run`; no key entered a file or log.
**Clone:** read-only mount; no upstream edits.

## Preregistered win condition

> On >= 20 REAL commits drawn from this repo's own history (git log, not a fixture I wrote),
> commit-miner must produce ZERO false positives on commits that are plainly not security fixes,
> AND flag at least one true security-relevant commit if one exists in the draw, at < $0.01 total
> and < 3s per commit. Meeting it = PROMOTE. Missing it = RULED_OUT at rung 4 with the evidence.
> Both outcomes are equally acceptable; the point is that YES is reachable.

This text was written to `/tmp/commit-miner-adoption.sh` before the classification run.

## Real-history draw

The draw was the latest 20 non-merge commits from the Jev repository's own `git log`, not a
handwritten fixture. Commit-miner processed all 20.

Per-commit output, condensed from the CSV report:

| Result | Count |
|---|---:|
| Commits drawn | 20 |
| Classified | 20 |
| Failed | 0 |
| Security classifications | 0 |
| Bug classifications | 0 |
| Metadata-only classifications | 13 |
| Other/unclassified | 7 |
| False positives on plainly non-security commits | 0 observed |

Cost and latency:

- 26 Jev calls;
- 164,017 input tokens;
- 22,224 output tokens;
- estimated cost `$0.006889`;
- elapsed time about 4 seconds;
- approximately 0.2 seconds per drawn commit.

The real draw did not contain a commit that the run itself identified as security-relevant, so the
conditional true-positive clause was not activated by the draw.

## Mandatory positive-control arm

A scratch repository was created outside the upstream clone with a deliberately SQL-injection-shaped
commit:

```text
fix: prevent SQL injection in user lookup [test]
```

The control run produced:

- 1 classified commit;
- 0 security classifications;
- result: `Unclassified`;
- the initial fixture commit failed with a Git-operation error;
- 1 Jev call;
- 4,279 input tokens / 963 output tokens;
- estimated cost `$0.000180`;
- elapsed time about 3 seconds.

The positive control that ought to pass did not. This is a harness/control failure, not evidence that
the SQL-injection change is benign.

## Verdict

**RULED_OUT** — the preregistered adoption test did not pass because the required positive control
failed to identify the deliberately security-relevant commit. The real-history arm met its
non-security false-positive and budget observations, but that cannot compensate for a broken
positive arm.

## No-claim

- No claim that commit-miner cannot detect security fixes in general.
- No claim that the 20-commit draw contained a true security fix.
- No patch or upstream edit was made.
- The Docker run used the upstream binary as supplied; no local build or binary substitution was
  performed.

## P3-5 (pane 3, non-author re-run): arm repaired, bar missed on cost

### Task 1 — diagnosis and repair

Harness as prescribed: `ubuntu:24.04`/`linux/amd64`, git 2.43.0 installed,
`git config --global --add safe.directory '*'`, stock binary
(`target/debug/commit-miner`, ELF x86-64, read-only mount, never rebuilt).
The miner itself never sets safe.directory (src/git.rs command builder sets
core.* flags but no ownership override) — running as root against a foreign-uid
checkout without that flag is the Git-operation failure shape.

Pane 2's exact failure was NOT reproducible under the prescribed env, so its
precise trigger is unproven; it is consistent with the scratch path not being
visible inside the container or git unusable there. What IS proven:

- Two-commit SQLi fixture → `Security fix`, `CWE-89` exact ($0.000359, ~1s).
- Substantive XSS fix → `Security fix`, `CWE-79` exact.
- Single-root-commit SQLi fixture → `Hardening`, no CWE, NO crash: the
  first-commit hypothesis does NOT reproduce as a Git error — it reproduces as
  a classification downgrade. A positive control built as one commit would fail
  the bar without any error telling you why. Fixtures need ≥2 commits.
- Four one-line vuln fixtures (SQLi/XSS/CMDi/traversal) → Feature/Feature/
  Unclassified/Feature, no CWEs. Detection needs substantive diffs; one-liners
  miss. Fixture-quality finding, recorded against future controls, not arm
  breakage: every scan completed with zero Git errors.

Arm verdict: WORKING under the prescribed env. The 4-that-scored-4/4 from the
brief were not locatable (no fixture in-tree or /tmp carries them); the two
exact-CWE proofs above substitute, stated as substitution, not equivalence.

### Task 2 — full bar, verbatim, predeclared denominator

Denominator predeclared: latest 20 commits at HEAD (669-commit history surveyed;
it contains NO genuine security fix — two days of docs/probes/gates — so the
true-positive half is vacuous by construction, and detection is covered by the
positive control above, not the draw).

Run: `scan /jevro -n 20`, read-only mount, 25 calls, 0 cached, failed 0,
elapsed 2.356s (0.12s/commit). Distribution: 14 Metadata review, 3
Observability, 1 Dependency, 2 Unclassified, 0 Security, 0 Bug.

| Clause | Result |
|---|---|
| Zero FP on plainly-non-security | PASS (0 Security, 0 Bug across 20 docs/state/test commits) |
| ≥1 true positive if one exists | VACUOUS (none exists; positive control covers detection separately) |
| < $0.01 total | **FAIL: $0.0128** (304,534 in × $0.042/1M, output free, from saved scan JSON) |
| < 3s per commit | PASS (0.12s) |

### Verdict

**RULED_OUT at rung 4 with a working arm** — exactly the case the bar
pre-registered. The miss is cost by 28%, not judgment: the classifier made no
false positives, but this 20-commit window costs more than the bar allows.
(Pane 2's window cost $0.0069 on the same bar; token spend moves with the
diffs in the window, so the bar is window-sensitive — noted, not adjusted.
Moving it now would be gate-weakening.)

### No-claim (P3-5)

- Pane 2's original Git-operation trigger unreproduced; mechanism named, not proven.
- The lost "4/4" fixture set substituted, not recovered.
- Fixture spend (~$0.002 across 4 scans) excluded from the bar total, stated here.
- No upstream edits; binary untouched; clone read-only throughout.

STATUS score 610, composed and stated: 800 for judgment (0 FP on 20, exact-CWE
positives on the control) minus 190 for the rung-4 cost miss at 128% of budget.

# Held resolution — Demo-3 incumbent check

Status: resolved on the concrete incumbent question from `PLAN.md` §3d.
Prior state: Demo-3 claim-check gate, reconciled demand 430, **HELD** pending incumbent check.
Resolution: **RULED OUT as the current standalone demo concept on structural incumbent evidence.**
Source date: 2026-09-18.
No package was installed and no commit hook was enabled.

## Question and answer

**Question:** Do commitlint, gitlint, Husky, or another maintained tool verify numeric claims against
cited artifacts, or do the incumbent tools only validate message format?

**Answer:** The narrow conventional-commit stack is format/hook infrastructure, but the global
“format only” claim is false. A maintained tool, `bhumik154/claim-check` at release `v0.6.0`
(commit `f3a020b5684f3854352197af5f4fb7d5e506972b`), verifies numeric **test-count claims** in a
commit message against the test-run evidence it actually collected. Its documented examples include
`22 passed`, `22/22 tests pass`, and `all tests pass`; its `commit-msg` hook blocks mismatches and
reports when it cannot verify a claim.

That is enough to resolve the held question against Demo-3's current standalone positioning. The
exact proposed entry point—numeric claims in commit messages checked against cited/evidence
artifacts—is already occupied for the highest-frequency test-count form. Demo-3 is therefore not
recovered at 430. The broad arbitrary-artifact extension in its contract remains technically
outside `claim-check`'s documented scope, but that would be a new, narrower candidate with a new
buyer and proof—not an excuse to revive the current demo unchanged.

## Evidence inventory

### 1. commitlint — message grammar and references, not artifact semantics

Official commitlint documentation defines Conventional Commit structure as:

```text
type(scope?): subject

body?

footer?
```

Its documented rule configuration covers parsed message fields and constraints such as:

- `type-enum`, `type-empty`, and `scope-enum`;
- `subject-empty`, `subject-case`, `subject-full-stop`, and header length;
- body/footer blank lines and line lengths;
- `references-empty`, issue prefixes, and issue-reference parsing.

Sources: [commit conventions](https://commitlint.js.org/concepts/commit-conventions.html),
[rules configuration](https://commitlint.js.org/reference/rules-configuration.html),
[configuration](https://commitlint.js.org/reference/configuration.html), and
[plugins](https://commitlint.js.org/reference/plugins.html).

`references-empty` can require or permit an issue reference such as `PROJ-123`; it does not load the
referenced issue, JSON receipt, log, benchmark, or test output and compare a number, unit, or
meaning. Plugins permit a project to write a custom rule, but the custom rule is new project code,
not an incumbent rule set that already owns Demo-3's evidence check.

**Finding:** commitlint is format/reference infrastructure. It does not itself verify numeric claims
against cited artifacts.

### 2. gitlint — title/body rules, regex, and extensibility

Gitlint's documented built-in rule set operates on commit-message title/body structure. Its examples
cover title maximum length, leading/trailing whitespace, punctuation, hard tabs, forbidden words,
regular-expression matches, minimum length, body presence, blank separation, body line length, and
optional Conventional Commit title rules.

Sources: [built-in rules](https://jorisroovers.com/gitlint/dev/rules/builtin_rules/),
[gitlint configuration](https://jorisroovers.com/gitlint/dev/configuration/gitlint_file/),
[Conventional Commit contrib rules](https://jorisroovers.com/gitlint/dev/rules/contrib_rules/),
and [user-defined rules](https://jorisroovers.com/gitlint/dev/rules/user_defined_rules/).

Gitlint supports user-defined Python `CommitRule`, `LineRule`, and `ConfigurationRule` classes. A
team could write a custom `CommitRule` that opens an artifact and compares a number, but that is
exactly the missing implementation Demo-3 proposes; it is not a maintained built-in or documented
incumbent capability. A regex can recognize `Tests: 22 passed`, but cannot establish that the cited
artifact contains the same number under the same denominator and units.

**Finding:** gitlint is format/rule extensibility, not a ready-made numeric claim-to-artifact
verifier.

### 3. Husky — hook lifecycle, no semantic rule set

Husky's official documentation shows installation and native Git hook scripts. It runs commands such
as `npm test` in `.husky/pre-commit` and invokes commitlint from `.husky/commit-msg` with:

```sh
npx --no -- commitlint --edit "$1"
```

Sources: [Husky getting started](https://typicode.github.io/husky/get-started.html),
[Husky how-to](https://typicode.github.io/husky/how-to.html), and
[Husky migration guidance](https://typicode.github.io/husky/migrate-from-v4.html).

Husky supplies the hook boundary and exit-code propagation. It does not parse numeric claims,
resolve citations, load artifacts, or judge evidence. Calling a custom checker from Husky would make
that checker the relevant incumbent; Husky itself is not one.

**Finding:** Husky is execution plumbing only.

### 4. claim-check v0.6.0 — a real partial incumbent

Pinned metadata was read without installation:

- Repository: [bhumik154/claim-check](https://github.com/bhumik154/claim-check)
- Release: [v0.6.0](https://github.com/bhumik154/claim-check/releases/tag/v0.6.0)
- Release published: 2026-08-19
- Tag resolved with `git ls-remote --tags --refs`:
  `f3a020b5684f3854352197af5f4fb7d5e506972b`
- Pinned README: [raw README at v0.6.0](https://raw.githubusercontent.com/bhumik154/claim-check/v0.6.0/README.md)

The pinned README states:

> Checks whether the test count in your commit message is actually true. pytest, vitest and jest.

It documents the following behavior:

1. A commit message containing `22 passed`, `22/22 tests pass`, or `all tests pass` is parsed for a
test-count claim.
2. The tool runs or reuses pytest, Vitest, or Jest evidence and compares the claim with the
runner's observed result.
3. A mismatch blocks the `commit-msg` hook.
4. A claim with no usable whole-suite evidence is reported as unverified rather than silently
accepted as proven.
5. The pre-commit integration must be installed for the `commit-msg` stage; the README explicitly
warns that the stage is not part of the default pre-commit install.
6. The v0.6.0 release is named “report unverified claims,” and documents a distinction between a
claim checked against evidence and a claim for which no usable evidence was available.

The README also states the boundary: the tool compares against the scope actually collected by the
runner and does not infer whether a narrower invocation represents the whole suite. It is not a
general verifier for arbitrary benchmark numbers, latency percentages, CSV/JSON fields, or
scientific claims. That limitation is important, but it does not erase the incumbent overlap: a
numeric commit claim against a test-run artifact is the exact concrete use case this held check was
supposed to determine.

**Finding:** claim-check is a maintained, pinned, installable incumbent for the test-count subset of
Demo-3's proposed numeric claim gate. The note “friends are format only” is refuted as a global
statement.

### 5. Adjacent tools that are not incumbents for this check

GitHub status checks and artifact attestations can expose whether a workflow or artifact passed
integrity/provenance checks. They do not, by themselves, parse a commit's numeric assertion and
compare it against a cited artifact field. `backcheck` and `evigate` are closer to evidence-backed
agent completion claims, but they are not needed to resolve this question because `claim-check`
already supplies a maintained commit-message/test-evidence rule.

Sources for adjacent boundaries:

- [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks)
- [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- [VectorInstitute/backcheck](https://github.com/VectorInstitute/backcheck)
- [shiki-yusuke/evigate](https://github.com/shiki-yusuke/evigate)

## Adjudication

### Why the original 430 does not recover

The original Demo-3 contract is broader than claim-check: it describes generic
`(number, unit, cited-artifact)` triples, JSON or raw-text artifacts, and a Jev Noul checking same
quantity, denominator, and units. That broader implementation gap is real. It is not, however, the
same as an unowned demand slot. The most obvious buyer entry point—commit-time numeric test claims
against test results—is already an installable maintained tool with a release, documented rule,
commit hook, fail-closed/unverified behavior, and runner support.

A new demo that only reproduces `claim-check` would be duplicate work. A new demo that verifies
arbitrary benchmark/latency/receipt numbers would need to change its contract, name a buyer for that
unserved artifact class, and pass a fresh demand comparison against claim-check. That is a new
candidate, not a recovery of Demo-3's current form.

### Structural verdict

**RULED OUT — current Demo-3 standalone incumbent claim.** This is a structural incumbent ruling,
not a taste judgment: a maintained tool at a pinned release already checks numeric commit claims
against test-run evidence. The result is narrower than “commitlint does it,” but stronger than the
pane-3 format-only note.

### Retry condition

Reconsider only if one of these evidence changes occurs:

1. `bhumik154/claim-check` no longer has a maintained release or removes the documented
   test-count-to-runner comparison;
2. a clean pinned probe shows its `commit-msg` hook cannot verify the documented test-count claim in
the supported pytest/Vitest/Jest path; or
3. a new, named buyer explicitly needs arbitrary non-test artifacts (for example benchmark JSON or
route receipts) and a fresh contract proves that the unsupported artifact class is materially
different from claim-check's test-count scope.

Condition 3 opens a new proposal with a new demand score; it does not revive this contract by
renaming the same hook.

## NO-CLAIM

This resolution did not install or execute claim-check, commitlint, gitlint, Husky, backcheck, or
evigate. It used official documentation plus pinned `claim-check` v0.6.0 release metadata and its
pinned README. The result establishes documented incumbent scope, not runtime compatibility,
performance, adoption, or superiority. It does not claim that arbitrary benchmark or receipt claims
are solved; it claims only that the held Demo-3 entry point is not unowned.

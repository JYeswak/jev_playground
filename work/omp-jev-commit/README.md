# omp-jev-commit

Observe-only check that a commit **message** describes its **staged diff**. Fires on `git commit`
when a message is present (`-F <file>` or `-m "..."`), reads `git diff --cached`, and asks three
questions. Never blocks.

```bash
omp plugin install omp-jev-commit
# key: see ../../.env.example
```

Mined from [`commit-miner`](https://github.com/devanshbatham/commit-miner), which classifies
commits in bulk over history. We **RULED_OUT** adopting that tool on cost — 128% of budget,
draw 0.0128 against a 0.01 bar
([receipt](../../docs/demos/upstream-repro/commit-miner-adoption-test-20260919.md)). That ruling
was about *mining history*. This is the same judgement moved to the moment it can still change
something: the commit being written.

## Why a judge, and not a linter

A conventional-commit linter checks that a subject looks like `feat(scope): …`. It passes a
subject that says the **opposite** of what the diff does. There is no regex for "this message
describes this change."

Live probe, on a deliberately misdescribed commit — message says *docs: fix a typo*, diff
removes an auth check and adds `ADMIN_BYPASS`:

| question | score | correct? |
|---|---|---|
| `describes` — does the message describe the diff? | **0.11** | yes — it does not |
| `omits` — does the diff contain a significant unmentioned change? | **0.92** | yes — it does |
| `overstates` — does the message claim work the diff lacks? | 0.39 | defensible; this message *understates* |

A linter passes that commit. This flags it.

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types live-probe.mjs
```

The probe builds a real throwaway git repo with a real staged diff, because the offline tests
cannot assert the scored path without one — three of their arms are conditional, and a
conditional arm passes on a no-op.

## Decision rows

`commit_scored` with `scores`, or `commit_error` with `failure` ∈ `unconfigured | http |
non-json | no-answers | transport`. No third clean state. Never blocks, never throws, returns
`undefined` on every path.

## NO-CLAIM

One probe case. No accuracy measurement across a corpus of commits, and no claim that these
scores correlate with anything. The next unit here is a `measure.mjs` over ground-truth cases,
the way `omp-jev-rerank` was measured — that measurement deleted two of three questions.

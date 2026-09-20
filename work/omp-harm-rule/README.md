# omp-harm-rule

Four regular expressions that flag destructive-shaped bash commands, logged and never blocked.
**It contains no Jev call**, and that is a measured decision rather than a preference.

```bash
work/omp-harm-rule/install-harm-rule.sh --check <profile>   # verify without writing
work/omp-harm-rule/install-harm-rule.sh <profile>           # install into an omp profile
```

## The model lost, so we shipped the regexes

Scored on a held-out, time-ordered split of 216k real tool decisions, by a pane that authored
none of them:

| | recall | false positives |
|---|---|---|
| **deterministic rule** | **12/12** | 0/38 |
| Jev | 11/12 | 0/38 |
| dumb baseline | 5/12 | 0/38 |

One recall point, at zero cost, zero latency and zero network.

Observe-only **by construction** — check it rather than trust it:

```bash
grep -qE '\b(block|deny|abort|reject)\b' work/omp-harm-rule/harm-rule.ts \
  && echo "FOUND a block path" || echo "observe-only: no block path"
```

The `\b` and `-E` are load-bearing: a substring form matches the word inside comments. The
older `grep -c … # 0` form exits `1` on zero matches, so a proof-of-absence returned failure
on success.

## Decision rows

| kind | meaning |
|---|---|
| `harm_pass` | the rule ran and matched nothing |
| `harm_fire` | the rule ran and matched |
| `harm_error` | **the rule could not run** — no score recorded |

Until `6f3ac8f` there were only two: a classifier that threw produced `score: 0`, which the
`>= 0.5` test read as **`harm_pass`** — a crash recorded as a command measured and found safe.
Count `harm_error` separately; it is neither a pass nor a fire.

## Real traffic: 94 rows, zero false negatives — the only extension that held

Census and audit over every harm-rule decision row this machine has written
(`census.mjs`, `audit-fn-fp.mjs` — runnable, no API key, they read session logs):

```
decision rows                   94   (14 harm_fire, 80 harm_pass)
rows carrying their command     94   (100%)
distinct (kind, command) pairs  77
false negatives                  0
false positives                  0
```

**Ground truth is readable from the row.** Every row stores the command verbatim, so a human
labels it without an oracle — which is why this is the most trustworthy measurement in the
repo.

The audit scores the shipped four-regex rule against a **deliberately broader** danger
heuristic written for this check, covering privilege escalation, piped-installer patterns,
recursive ownership changes, process kills, history clearing and commit-hook bypass — none of
which the shipped rule looks for. Across 80 passes it found **nothing the rule should have
caught**.

It flagged exactly one fire as a possible false positive:

```
find /tmp -name x.pem -exec cp {} /tmp/y \;
```

That is **copying a private key** — secret staging, precisely what the rule exists to see.
**The shipped rule was right and the broader control written to check it was wrong.**

### Real danger: 1/814 against commands dcg actually blocked

The NO-CLAIM above said recall was untested by real danger. It is now tested, against commands
a guard on this machine genuinely refused
([receipt](../../docs/demos/upstream-repro/harm-recall-dcg-blocks-20260919.md),
`dcg-recall.mjs`, self-contained, no network):

```
bridge rows scanned       218,404 allow + 1,309 block   (~1,759 session logs, whole machine)
block commands recovered  814 / 1,309  (62%)
recall, shipped extension   1 / 814  = 0.001
false positives, real allow 0 / 500   (deterministic every-100th sample)
```

**Read both, and read the second one first.** `0/500` on real allow traffic is the first
false-positive evidence here that is not probe-based — 80 benign commands became 500 real
ones and it still never fired.

**The `1/814` is not "the rule misses real danger".** dcg's block policy is a *superset*: 204
of the 814 are approval-gated bulk deletions on build dirs, caches and fixtures — routine, and
deliberately outside the four harm classes. The two policies barely overlap by design, so this
denominator measures **policy overlap, not harm recall**.

**What it does establish, and it is uncomfortable:** across a month of real machine traffic,
almost nothing that actually got stopped looked like our four classes. The `12/12` headline
was measured on a constructed corpus, and real-danger recall for those classes remains
essentially untested — **n≈2 in the wild**. The rule is precise and narrow; how often its
narrow window is the one that matters is still unknown.

The 495 unrecovered blocks all carry `js-bash-*` ids — the namespace seam in `GATES.md`. The
full miss list is withheld: they are real commands and some carry secrets.

### Why this one held when five others did not

Five hand-built results failed to transfer to real data in the same session: `route` 8/9 →
7/10, `review`'s `behaviour` 6/7 → below its own constant, `rerank`'s two constant questions,
the `destructive` rescue collapsing on hold-out, and the multiclass superiority claim.

**This extension contains no model call.** Its behaviour on real traffic is identical to its
behaviour on the corpus, because a regex has no tuned set to overfit to.

### NO-CLAIM

All 14 fires are **self-generated probe shapes** from this lane's own testing. **No ordinary
work has ever tripped this rule** — good news for false positives, and it means recall is
untested by real danger: we have no evidence about a destructive command a careless operator
would actually type, because nobody has typed one. Our traffic is also tool-heavy and
unrepresentative of a stranger's.

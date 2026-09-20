# Index — every receipt in `docs/demos/upstream-repro/`

**This directory is the evidence behind the project, and this file is the only complete index of
it.** 227 artifacts sit here beside this README. Until this rewrite, no index covered more than 18
of them and `docs/demos/STATUS.tsv` cited 19 — a union of roughly 30 of the 207 present at
`038aeb4`, which left ~85% of the corpus reachable only by `ls`. **That gap is widening, not
closing:** `STATUS.tsv` still cites the same 19 while the directory has grown, so the cited share
has already fallen from 9.2% to 8.8% and below
([`map-stranger-check-20260920.md`](map-stranger-check-20260920.md), measured independently).
Every artifact now appears exactly once below, grouped by subject, one line saying what it settles.

Two things a reader has to know before using the index, both measured in
[`map-docs-20260920.md`](map-docs-20260920.md):

1. **Nothing here is ranked by inbound references, and you should not rank it that way either.**
   Orphan rate in this corpus tracks *age*, not worth — 12% for files first committed 2026-09-18,
   25% for 09-19, 32% for 09-20 — and in **six of seven** supersession pairs the *authoritative
   later* file is the orphan while the superseded earlier one carries the links. "Nothing links to
   it" is not a discard proof here.
2. **Supersession is the only discard-safe signal in this corpus**, so it is marked explicitly and
   names its successor. Where a row says *superseded by X*, read X; the superseded file is kept as
   a dated observation, not deleted.

## Read these ten first, in this order

| # | receipt | why here |
|---:|---|---|
| 1 | `RULING-authored-vs-real-20260919.md` | The governing ruling. Every candidate that looked good on authored data failed on real data — read it and the shape of every other receipt makes sense. |
| 2 | `cass-mountain-findings-20260920.md` | The one finished, stranger-readable question and answer: dig vs invent over 138 real questions. |
| 3 | `repsample-result-20260920.md` | The representative re-draw that stops #2 being a window artifact. Pre-registered, and the inversion *deepened*. |
| 4 | `judge-seat-ruling-20260920.md` | Where a Jev judge earns its seat: one question out of seven. The most decision-relevant ruling in the directory. |
| 5 | `toolcall-judge-jev-vs-regex-20260920.md` | 28 fires on 77,767 real commands, 28 of 28 false positives, one mechanism. What a hand-written judge actually does off its own corpus. |
| 6 | `waved-s17-organic-precision-20260920.md` | 0/28 organic precision. The shipped, promoted product measured on traffic nobody staged. |
| 7 | `compaction-retention-oracle-20260919.md` | The cleanest completed negative: 7–23× worse than doing nothing. |
| 8 | `rigged-oracle-selfcheck-20260919.md` | Read immediately after #7 — the first version of that oracle was rigged, and one arm proves it. This is why #7 is credible rather than convenient. |
| 9 | `commit-mine-result-20260920.md` | 1,040 commits mined: our own verification levels mark documents, not evidence. |
| 10 | `map-hook-ee-20260920.md` | The most recent correction: a committed BLOCKED verdict measured the wrong store. Newest work is the least linked work — start here, not last. |

**Eleventh, and only its `##` headings:** `commit-learnings-20260919.md` — 1,928 lines, 57 entries,
9.7% of this directory. The headings are a table of contents for what the swarm learned; descend
into the three that matter to you. (Known defect: `STATUS.tsv`'s UP-R9 points at a section `s14e`
that does not exist in the file.)

## Conventions you will meet in these files

**Pre-registration pairs.** Eight mines committed their falsifier *before* the scoring script
existed, per rule 3 of [`../../RULES.md`](../../RULES.md). All eight pairs are complete. Read the
pre-registration first; it is the only thing that makes the result's verdict mean anything:
`a11-join`, `a12-refusal`, `a18-offbus`, `c1-calibration`, `commit-mine`, `dig-subset`, `mail-mine`,
`repsample`.

Their naming is inconsistent on **both** halves, so the mechanism is not greppable — a search for
`falsifier` finds 7 of 8 and a search for `result` finds 6 of 8:

| half | suffixes in use | counts |
|---|---|---|
| pre-registration | `-falsifier`, `-expectation` | 7 / 1 (`c1-calibration` is the `-expectation`) |
| result | `-result`, `-yield`, `-breakdown` | 6 / 1 (`a11-join`) / 1 (`dig-subset`) |

**Convention going forward, for new pairs only: `<stem>-falsifier-<date>.md` and
`<stem>-result-<date>.md`, and the result must name its falsifier in the first paragraph.** The
eight existing pairs are **not** renamed — they are cited by `STATUS.tsv` rows, by
`commit-learnings`, and by each other, and a rename would break live citations to fix a grep. One of
the eight already shows the cost of the gap: `c1-calibration-expectation-20260920.md` is cited by
nothing in this directory, because its own result never names it.

**Claim stubs.** Ten `waved-*-claim.md` / `wavee-*-claim.md` files claimed a wave section before the
work started, each ending "full receipt follows". All ten receipts exist, so all ten stubs are
superseded and marked as such below. They are kept because several recorded load-bearing facts
verified *before* the work — and in one case the section number itself.

**Verification level.** Most titles carry `[pending|receipt|selftest|test|mutation|oracle|live]`.
It marks how the *document* was verified, not how strong the evidence is —
[`commit-mine-result-20260920.md`](commit-mine-result-20260920.md) is the receipt that measured
exactly that gap, and [`level-confusion-20260920.md`](level-confusion-20260920.md) is the relabel.

## Verifying this index covers the directory

```sh
cd docs/demos/upstream-repro
# every row's first cell, one filename per index row
sed -n 's/^| \[`\([^`]*\)`\].*/\1/p' README.md | sort > /tmp/idx.txt
ls -1 | grep -v '^README.md$' | sort > /tmp/dir.txt
wc -l < /tmp/idx.txt          # 227  (index rows)
wc -l < /tmp/dir.txt          # 227  (files on disk)
uniq -d < /tmp/idx.txt        # empty: no file indexed twice
comm -3 /tmp/idx.txt /tmp/dir.txt   # empty: no gaps either way
```

Measured at the commit that wrote this file: **227 index rows, 227 files on disk, 0 duplicates,
0 differences.** The extractor takes only the first cell of a row, so the supersession links inside
a description never double-count. Two maps are named again in prose (once under the maps group,
once under the subject they measure) — prose mentions are not index rows, which is why the row count
and the file count agree exactly.

The check runs against `ls`, not against git, because that is the denominator a reader actually
faces. At the commit that wrote this file the two agree: all 227 are tracked. **The directory
gained five artifacts while this index was being written**, so re-run the five commands above
rather than trusting the number — and if one comes back as a gap, add its row rather than editing
the count.

---

## Upstream sweep — spam, phishing, prompt injection
Somebody else's code on somebody else's corpus. Nothing in these clones was patched.
| receipt | what it settles |
|---|---|
| [`lingspam-20260918.md`](lingspam-20260918.md) | Jev's own Ling-Spam benchmark, re-run here: **0.9857** zero-label against **0.9941** for TF-IDF on 2,300 labels — same accuracy to four decimals, opposite failure shapes (2 FN / 39 FP against 40 / 1). |
| [`jev-spam-eval-ood-20260918.json`](jev-spam-eval-ood-20260918.json) | Out-of-distribution arm, machine-readable: on mail the classifier was not trained for the labelled model collapses — **91.3% vs 70.3%** on recent phishing, **97.00% vs 72.51%** on modern mail. 633 live requests, 0 errors. |
| [`criteria-inversion-20260918.md`](criteria-inversion-20260918.md) | Elaborating a zero-label question costs accuracy, across three paired comparisons (Ling-Spam 98.57% plain vs 97.01% structured, p=1.4e-9; names-only 98.58% vs 97.00%, p=.0064). Not a claim that plain always wins — a claim that elaboration is empirical. |
| [`phishing-20260918.md`](phishing-20260918.md) | `jev-phishing-bench`'s keyless floor reproduces exactly (0.9165 / 0.8350 / 0.0020), plus a live smoke. |
| [`jev-sec-bench-20260918.md`](jev-sec-bench-20260918.md) | Independent replication of the framing-leak effect that cost this lane a retraction: injection detection 96.5% / AUC 0.9927 over 662 messages; recall 74.9% bare vs 95.1% with context. Also corrects a root-README row written from an `ls`. |
| [`benchmark-examples-20260918.md`](benchmark-examples-20260918.md) | `typesafe-ai-benchmark`'s 7 documented offline examples all run — after an install step its docs omit. |

## Upstream sweep — benchmarks, rerank, and what Jev is measurably good at
Re-analysis of committed per-item data, with independent scorers.
| receipt | what it settles |
|---|---|
| [`jev-rerank-bench-20260918.json`](jev-rerank-bench-20260918.json) | One benchmark, two answers: the committed cache puts Jev at 0.692 vs Cohere Pro 0.691 (p=.910, inside noise); a fresh run over 1,383 pairs gives **+4.2 points at p=.002**. |
| [`jev-benchmark-pairing-20260918.md`](jev-benchmark-pairing-20260918.md) | The limit is the task set, not the sample size. Pairing upstream's two shipped runs gives **zero discordant pairs and identical choices on 60/60** — no increase in n on that task set can separate the two model versions. An improvement on published work with no key and no new calls. |
| [`agent-failure-benchmark-20260918.md`](agent-failure-benchmark-20260918.md) | This lane's own question asked properly by someone else: n=6,257 with intervals. Its leakage test **silently skips** without the pinned 73 MB dataset, and a bare `uv run pytest` fails collection — there is no score at all. |
| [`agent-failure-denominator-ruling-20260918.md`](agent-failure-denominator-ruling-20260918.md) | What a 6,257-trace benchmark says about 17-candidate verdicts: `CLEARED` in `STATUS.tsv` is a rung condition, not benchmark-level confidence. Different measurement object, stated as a ruling. |
| [`judgment-quality-20260919.md`](judgment-quality-20260919.md) | Five benchmarks recomputed from committed per-item data with independent scorers — the pass that separates "their suite is green" from "their judgment is good". |
| [`random-judge-substitution-20260919.md`](random-judge-substitution-20260919.md) | If Jev were replaced by a coin flip tonight, **five of six repos' CI would stay green**. The strongest single argument in the corpus against test suites as evidence of judgment. |
| [`system-one-adapter-python-20260918.json`](system-one-adapter-python-20260918.json) | `system-one-adapter-python` reproduction: 204 passed, pyrefly 0 errors, plus the adapter interface and a ruling. **The only receipt in this directory with no prose sibling and no citation anywhere in the repo** — payload-only. |

## Upstream sweep — harness clones (MCP, review, bicameral, foreman, Rust, open-model)
| receipt | what it settles |
|---|---|
| [`jev-mcp-20260918.md`](jev-mcp-20260918.md) | Three Jev tools live inside the coding harness already in use: 9/9 unit, 4/4 end-to-end. Without a key the live tests **skip and say so** rather than counting as passes. The cheapest path from this lane to a real judgment. |
| [`jev-mcp-oracle-spec-20260919.md`](jev-mcp-oracle-spec-20260919.md) | Zero-API oracle specification for the same server: class B evidence (golden/cassette + contract), explicitly not ground truth. |
| [`jev-review-20260918.md`](jev-review-20260918.md) | An upstream scorer that returns `applicable: false` for dimensions its context cannot support — a refusal-to-score state shipped as contract, not retrofitted. 13/13 tests. |
| [`jev-review-real-diffs-20260919.md`](jev-review-real-diffs-20260919.md) | Pointed at real diffs it is **RULED_OUT**: quality ordering AUC 0.625 against a 0.75 bar (feasibility arm 0.939, thin but clears). |
| [`bicameral-20260918.md`](bicameral-20260918.md) | The System-2-writes / System-1-judges split is real: 41 tests, zero key, zero network. Two properties worth copying — judgment is a pluggable interface, and the degraded path falls back to pattern rules instead of passing work through unjudged. |
| [`bicameral-gate-adoption-20260919.md`](bicameral-gate-adoption-20260919.md) | Jev as a tool-call gate: **ADOPT** — risk AUC 0.974, 0/20 false positives on routine work, 5/20 dangerous missed at the 0.5 cut. |
| [`foreman-20260918.md`](foreman-20260918.md) | 57/58. It is a per-worker supervisor with no queue concept, so a worker idle *while work is ready* reads as finished. |
| [`foreman-supervision-adoption-20260919.md`](foreman-supervision-adoption-20260919.md) | Supervision adoption: **PROMOTE**, with the vignette caveat stated — AUC 1.000 on n=20 constructed windows, 0/10 false-stuck. |
| [`s1-rs-20260918.md`](s1-rs-20260918.md) | The Rust examples blocked all day were never blocked by Rust: both run offline against a `FakeClient`. The obstacle was a misdiagnosis. |
| [`simple-jev-20260918.md`](simple-jev-20260918.md) | An open-model implementation of the same interface, free and keyless; asked this lane's hardest classification it returned `derived_rollup` at 0.989 in 1.7s. The control arm that makes "is the model doing the work" answerable. |
| [`promotion-grade-20260918.md`](promotion-grade-20260918.md) | Grades **this page** against the promotion bar: a genuine stranger-consumable USER surface, not an index of receipts wearing a summary's clothes. The standing quality contract for whatever this file becomes. |

## Upstream sweep — routers
| receipt | what it settles |
|---|---|
| [`routers-20260918.md`](routers-20260918.md) | Ruling (RULE 13): our routing work narrows to measurement. Both upstream routers run (`jev-router` 58/58) and neither earns adoption as a cost play. |
| [`router-tier-signal-20260919.md`](router-tier-signal-20260919.md) | `jev-model-router`'s tier signal is real but weak and **loses to prompt length in two of three sessions** — REJECT on all three. |
| [`router-savings-inverts-20260919.md`](router-savings-inverts-20260919.md) | The one published savings claim **inverts** on our own sessions. Adopt supervision and commit-triage; do not adopt tier routing for cost reasons; raise any router's `minConfidence` above 0.35, where the measured failure sits. |

## Upstream sweep — commit-miner
| receipt | what it settles |
|---|---|
| [`commit-miner-20260918.md`](commit-miner-20260918.md) | commit-miner on this lane's own history: 108 metadata-review, 6 feature, 5 observability… and an empty CWE column, correctly. It declares change *types*; our subjects declare verification *levels* — orthogonal. |
| [`commit-miner-adoption-test-20260919.md`](commit-miner-adoption-test-20260919.md) | **RULED_OUT** on a preregistered adoption test: the positive control failed to identify the deliberately security-relevant commit. The real-history arm passing cannot compensate for a broken positive arm. |

## Upstream sweep — `jevcache`, and six defect reports written against it
One filed by Joshua; five are paste-ready issue bodies held for a human. Nothing else here was posted.
| receipt | what it settles |
|---|---|
| [`jevcache-20260919.md`](jevcache-20260919.md) | **ADOPT NARROWLY.** The product works and the central claim is real (553ms → 0.52ms); it is defeated for us by four properties that are each individually disqualifying for a specific surface. |
| [`jevcache-upstream-reports-20260920.md`](jevcache-upstream-reports-20260920.md) | Index and receipt for the six defects — one filed, five drafted, one retraction. Read this before any `issue-N` file. |
| [`issue-1-state-preview-plaintext-credentials.md`](issue-1-state-preview-plaintext-credentials.md) | **FILED AND ANSWERED UPSTREAM** (`hyperspaceai/jevcache#1`): `state_preview` persists unredacted credentials to a world-readable ledger. |
| [`issue-2-id-field-dropped-before-hashing-collision.md`](issue-2-id-field-dropped-before-hashing-collision.md) | Ready to post: canonicalization drops any `*_id` field before hashing, so materially different states share one fingerprint and receive each other's cached answers. |
| [`issue-3-ledger-no-process-isolation.md`](issue-3-ledger-no-process-isolation.md) | Ready to post: one global ledger with no per-process isolation — unrelated processes share a cache and concurrent writers corrupt the log. |
| [`issue-4-serve-port-flag-handling.md`](issue-4-serve-port-flag-handling.md) | Ready to post: `serve --port` reports the requested port rather than the bound one, and silently discards an unparseable value. |
| [`issue-5-installer-soft-checksum.md`](issue-5-installer-soft-checksum.md) | Ready to post: `install.sh` silently downgrades to an unverified install when the `.sha256` sidecar cannot be fetched. |
| [`issue-6-documented-decide-example-does-not-run.md`](issue-6-documented-decide-example-does-not-run.md) | Ready to post: the documented `/decide` example cannot be run as written — `schema.id` and `schema.version` are required and revealed one error at a time. |

## Upstream sweep — self-hosted and alternative Jev backends
| receipt | what it settles |
|---|---|
| [`jev-align-20260919.md`](jev-align-20260919.md) | `sutro-sh/jev-align` installed and run, with a fit verdict for our omp extensions. |
| [`jev-align-upstream-reports-20260920.md`](jev-align-upstream-reports-20260920.md) | Two defect reports plus one UX gap for the same repo, re-reproduced at source rather than recalled. **Nothing posted to GitHub** — the file is the deliverable. |
| [`jeff-selfhost-recompute-20260919.md`](jeff-selfhost-recompute-20260919.md) | `logan-markewich/jeff`: Jev wins on both axes, and **the config you would actually deploy is the worse one**. Offline recompute from committed per-item data. |
| [`localjev-differential-20260919.md`](localjev-differential-20260919.md) | **BLOCKED**, not SUBSTITUTE or NOT-SUBSTITUTE: a LocalJev/oMLX backend completion error on the pinned differential workload, after the feasibility probe itself worked. Feasibility success is not calibration. |
| [`laya-mlx-probe-20260920.md`](laya-mlx-probe-20260920.md) | `laya-mlx` @fc1df62: **GO for a disposable smoke pane only.** Not a Jev replacement until a labelled parity eval; the 50× claim is not measured here. |
| [`jev-ultrafast-action-choice-20260919.md`](jev-ultrafast-action-choice-20260919.md) | Jev Ultrafast as an action-choice oracle: top-1 20/20, 0/10 false advances on the no-valid-action half, feasibility arm passes. |

## Upstream sweep — the TypeSafe SDKs, and the session's one shipped-code defect
The Python clone is the control arm that turns "async timeouts are hard" into "this is a defect".
| receipt | what it settles |
|---|---|
| [`sdk-setup-20260919.md`](sdk-setup-20260919.md) | How to install both SDKs reproducibly, and why `uv run --with <path>` is not enough. |
| [`sdk-js-and-skills-20260919.md`](sdk-js-and-skills-20260919.md) | Two unrun clones run: `typesafe-sdk-js` (189/189 with 8 unhandled errors, all from one file) and `typesafe-ai/skills` — the vendor's own judgment-design guidance, which had been sitting in the tree unread. Checking our code against it found nothing to fix, because we author no questions at all. |
| [`sdk-js-timeout-crash-20260919.md`](sdk-js-timeout-crash-20260919.md) | **UPSTREAM REPORT**: every timed-out request leaks one unhandled rejection, and under Node's default that **kills a default consumer process** (`exit 1`, `client.ts:421`). Outside their harness entirely — real `node:http`, real `fetch`, no test doubles. |
| [`sdk-js-timeout-crash-repro.mjs`](sdk-js-timeout-crash-repro.mjs) | The runnable repro for the row above, with no `unhandledRejection` handler installed — the arm that proves a *default* consumer dies. |
| [`sdk-python-20260919.md`](sdk-python-20260919.md) | The last unrun clone, and the control: identical scenario, `TypeSafeAPITimeoutError` to the caller, **zero** leaked async errors, process survives. 534 passed. Completes the sweep. |
| [`sdk-python-timeout-control.py`](sdk-python-timeout-control.py) | The Python control script for that comparison, with `warnings.simplefilter("error")` so a `ResourceWarning` would fail rather than pass quietly. |

## skillranker — the fork, the macOS port, and the fork's death
Thirteen files, one conclusion. Start at the map; the four `[historical]` rows are superseded by upstream commits, not by each other, and are kept as dated observations only.
| receipt | what it settles |
|---|---|
| [`map-skillranker-20260920.md`](map-skillranker-20260920.md) | **The fork is not worth keeping.** Three independent measurements: it was obsolete 11m17s before it was committed; 21 of 27 touched files are dead (7 superseded workarounds, 6 tests that pin the defect as contract, 1 unexplained `inventory_partial` regression); the durable artifact is a comment on upstream issue #3. Supersedes the disposition of every other row in this group. |
| [`skillranker-20260919.md`](skillranker-20260919.md) | First upstream run @`3fe85c4`: blocked natively, then ran via Docker. **[historical]** — superseded as a state report by upstream `9c52a64`; see the map. |
| [`skillranker-origin-main-20260919.md`](skillranker-origin-main-20260919.md) | Build + corpus read at `ba5da08` (217 commits forward): builds, reads corpus, keyed rank blocked. **[historical]** — pinned three tips back; valid as a dated observation. |
| [`skillranker-0bp-native-20260919.md`](skillranker-0bp-native-20260919.md) | The native build boundary at `4ed4c9b`. **[historical]** — that is the exact boundary upstream `9c52a64` moved. |
| [`skillranker-build-20260920.md`](skillranker-build-20260920.md) | BLOCKED tick at `abf909d`: `cargo build --locked --release` exits 102 on macOS. **[historical]** — the block it records is fixed upstream; keep as the dated reason the port started, add no weight to its conclusions. |
| [`skillranker-mac-port-20260920.md`](skillranker-mac-port-20260920.md) | Port **INSTALLED**: `sr 0.1.0` for aarch64-apple-darwin, 821 pass + 1 load-flake, 4/4 live Jev tests on real paid calls. Second independent statement of the CANTOPEN-1550 probe, and the only record of the install approval. |
| [`skillranker-lifecycle-20260920.md`](skillranker-lifecycle-20260920.md) | The end-to-end port narrative, and the **sole written home of the NOFOLLOW evidence that survives the fork's death**: bundled SQLite returns `CANTOPEN 1550` with `SQLITE_OPEN_NOFOLLOW` on Apple, so upstream's macOS port may compile and still never open its own store. |
| [`skillranker-issue-filed-20260920.md`](skillranker-issue-filed-20260920.md) | No new issue filed — `#3` already covers it; corroboration posted as `issuecomment-5750779980`. The audit trail that prevents re-filing. |
| [`skillranker-issue3-comment-draft-20260920.md`](skillranker-issue3-comment-draft-20260920.md) | **DRAFT, NOT POSTED**: residual macOS gaps at `0e61cc6`. Posting needs Joshua's explicit approval, because his rule allows skillranker findings only from native binary downloads and no native darwin binary exists. |
| [`skillranker-fork-delete-20260920.md`](skillranker-fork-delete-20260920.md) | Fork deletion and pure-source install status: probe worktrees verified gone; `/tmp` build-dir cleanup BLOCKED by SLB (rm -rf needs approval) and left in place. |
| [`skillranker-corpus-measured-20260919.md`](skillranker-corpus-measured-20260919.md) | Their own corpus finally pointed at a judge: mean loss 0.167 against an always-abstain control of 0.833, top-1 precision **0.800 just under their own 0.90 promotion gate**. Independent of the macOS question entirely. |
| [`skillranker-process-archaeology-20260919.md`](skillranker-process-archaeology-20260919.md) | Deep read of their *method* at public HEAD `6a74cca` — the largest artifact in the slice and the one untouched by any of the 17 macOS commits. |
| [`skillranker-process-mirror-20260919.md`](skillranker-process-mirror-20260919.md) | "Copy the loop, not the corpus" — the only receipt in the group with a product landing outside it (`work/omp-jev-route/`). |
| [`skillranker-dogfood-20260920.md`](skillranker-dogfood-20260920.md) | The pure-upstream `0e61cc6` build dogfooded across every surface, exit code per command: demo/doctor/capabilities/roster/dry-run all green, offline uncached rank correctly exits 11, and two live paid ranks discriminate (rust-fixer 0.94, phish-guard 0.98). The receipt that says the tool works when it is *their* source and not our fork. |

## Compaction — `fast-jev-compaction` taken to completion
The corpus's cleanest completed negative, and the receipts that make it trustworthy.
| receipt | what it settles |
|---|---|
| [`fast-jev-compaction-20260918.json`](fast-jev-compaction-20260918.json) | Upstream contract plus reproduction: 29/29 tests; a live run took 21 messages to 7, saving 87.1% of characters in one request at 1,277 ms. |
| [`compaction-install-run-20260919.md`](compaction-install-run-20260919.md) | Install-and-run proof in a clean workdir from the README's own commands, clone untouched. |
| [`compaction-retention-oracle-20260919.md`](compaction-retention-oracle-20260919.md) | Taken to completion: **the product is 7–23× worse than doing nothing.** Jev @0.5 makes 82/91/81 mistakes across three sessions; "drop everything" makes 84/92/83. |
| [`compaction-threshold-curve-20260919.md`](compaction-threshold-curve-20260919.md) | And no threshold rescues it: mean keep_p is 0.361 for needed vs 0.369 for unneeded, mistake rate is flat ~0.74 across t=0.3–1.0. Every cut is the same exchange rate. |
| [`compaction-positive-control-20260919.md`](compaction-positive-control-20260919.md) | The arm that makes the null real: the same harness detects signal elsewhere (err AUC 0.698, read AUC 0.941) while keep-vs-needed sits at 0.457. Verdict A. |
| [`waved-s18-claim.md`](waved-s18-claim.md) | §18 claim stub — `jev-compact` reality. **Superseded by** [`waved-s18-compact-reality-20260920.md`](waved-s18-compact-reality-20260920.md); kept only as the dated record of what was read before building. |
| [`waved-s18-compact-reality-20260920.md`](waved-s18-compact-reality-20260920.md) | 13→8 reproduces at the same numbers as 2026-09-17 (6/6 invariant checks, 3 runs) — **and no session-pruning surface exists to claim**: the installed hook declines by design. |

## Oracle honesty — were our own oracles rigged?
| receipt | what it settles |
|---|---|
| [`rigged-oracle-selfcheck-20260919.md`](rigged-oracle-selfcheck-20260919.md) | **My compaction oracle was rigged, and a "perfect judge" arm proves it in one line.** Read this beside any compaction row; it is the reason the completed negative above is credible rather than merely convenient. |
| [`our-oracles-rigging-audit-20260919.md`](our-oracles-rigging-audit-20260919.md) | Read-only audit of every lane oracle, four questions each with file:line: can it return YES, was the win condition preregistered, is the null bounded, is there a positive control. Suspicion **UPGRADED** on sibling evidence. |
| [`oracle-design-from-corpus-20260919.md`](oracle-design-from-corpus-20260919.md) | Oracle design patterns mined from the pinned Dicklesworthstone mirror (306 ledger rows, 1.43M indexed chunks), with citations opened at pinned paths rather than taken from the ranking. |
| [`prevalence-retrofit-20260919.md`](prevalence-retrofit-20260919.md) | Retrofitting prevalence to every existing verdict: **no verdict inverts**, one confirms hard, two go UNKNOWN. Zero API calls — every number quoted from the row's own receipt. |

## The harm rule — shipped, promoted, then measured to 0/28
Product #1, and the corpus's sharpest arc: a deterministic rule that shipped on measured evidence and then failed the only organic-traffic test.
| receipt | what it settles |
|---|---|
| [`harm-rule-claim-repro-20260919.md`](harm-rule-claim-repro-20260919.md) | The published claim reproduced by `verify-claim.mjs` against the rule source under test. |
| [`harm-rule-conformance-20260919.md`](harm-rule-conformance-20260919.md) | The live extension agrees with the frozen scorer **17/17** — 0 mismatches, planted negatives fire and pass identically in both. |
| [`harm-rule-installer-loader-20260919.md`](harm-rule-installer-loader-20260919.md) | Loader proof: bare extension names load; the configured entry is what matters, not the filename. Relative-path behaviour explicitly not exercised. |
| [`installer-grade-20260919.md`](installer-grade-20260919.md) | Non-author grade of the installer: RED/GREEN/GREEN plus one reproducible defect, in throwaway `OMP_HOME` only. |
| [`harm-rule-shipped-20260919.md`](harm-rule-shipped-20260919.md) | Shipped: an observe-only omp extension firing live on two models, zero model calls in the shipped path, `cmp`-identical deployed copy, `jev-lab` profile only. |
| [`harm-rule-promoted-20260919.md`](harm-rule-promoted-20260919.md) | Promoted to the `codex` working profile — rollback line first, evidence after. Observe-only proven, not asserted. |
| [`harm-rule-realtraffic-20260919.md`](harm-rule-realtraffic-20260919.md) | First hour after promotion: 4 fires / 17 passes = **19.0%**, confirming an independent 18.8%. The receipt's own reading is that the rate accuses the probe mix, not the rule — which [`waved-s17-organic-precision-20260920.md`](waved-s17-organic-precision-20260920.md) then settles. |
| [`waved-s17-claim.md`](waved-s17-claim.md) | §17 claim stub — harm-rule organic traffic. **Superseded by** [`waved-s17-organic-precision-20260920.md`](waved-s17-organic-precision-20260920.md). |
| [`waved-s17-organic-precision-20260920.md`](waved-s17-organic-precision-20260920.md) | Organic precision **0/28 over 80,975 real allows** — every single fire is mention-vs-use: the trigger string sits inside a quoted prompt or a probe dispatch. Supersedes the 19% fire-rate reading above as the rule's real-traffic result. |
| [`harm-recall-dcg-blocks-20260919.md`](harm-recall-dcg-blocks-20260919.md) | Recall against real `dcg` blocks: **1/814**, and the denominator is the finding — 814 of 1,309 block commands recovered by a three-way join; the 495 unrecovered all carry `js-bash-*` ids. |
| [`m7r-harm-recall-ruling-20260920.md`](m7r-harm-recall-ruling-20260920.md) | **RULING: no real-danger corpus exists here.** The 12/12 stays scoped to the constructed set. Reached by sweeping every session log, not by assuming. |
| [`dcg-block-rate-prior-20260919.md`](dcg-block-rate-prior-20260919.md) | `dcg` blocks **0.97%** of real traffic while Jev's gate fired on 15%. The first prior for how often a deterministic guard fires on real agent traffic — and the whole argument against the gate. |
| [`vbh1-exec-data-20260920.md`](vbh1-exec-data-20260920.md) | The executed-vs-data distinguisher moved inside the rule: **0 fires on 81,373**, and an ordering defect found by dogfooding (blank-after-strip fires on debug commands because stripping destroys the literal structure blanking needs; blank-first then strip is correct). |
| [`vbh1-reconcile-20260920.md`](vbh1-reconcile-20260920.md) | **RESCOPED** to the R44 trigger: close-as-satisfied fails because §21 shipped a REJECT decision while vbh.1's stated WHAT was to build the thing rejected. The bead's premise is refused. Supersedes the open reading of [`vbh1-exec-data-20260920.md`](vbh1-exec-data-20260920.md)'s parent bead. |

## omp extensions — observer, failure, foreman, session adapter, sentinels
Eleven packages' worth of wiring proof, and the dogfood that found none of it fires as shipped.
| receipt | what it settles |
|---|---|
| [`omp-jev-observer-20260919.md`](omp-jev-observer-20260919.md) | Offline proof that the observe-only `tool_call` handler installs and returns. |
| [`omp-jev-observer-id-join-20260919.md`](omp-jev-observer-id-join-20260919.md) | The `toolCallId` join proved in a fresh disposable lab profile — the join that lets a decision row be tied back to the call it judged. |
| [`omp-jev-observer-cost-sentinel-20260919.md`](omp-jev-observer-cost-sentinel-20260919.md) | Decision records now omit `costUsd` when the classifier reports none, instead of writing a sentinel that reads as a measurement. |
| [`omp-jev-observer-sentinel-cleanup-20260919.md`](omp-jev-observer-sentinel-cleanup-20260919.md) | Same cleanup on the injected default DCG function: `?? 'unknown'` removed from the gate path. |
| [`sentinel-default-audit-20260919.md`](sentinel-default-audit-20260919.md) | Source audit of every remaining stored sentinel: **6 hit locations**, each needing its own schema/consumer review. Explicitly a one-off audit, not a new checker. |
| [`observer-sentinel-published-surface-audit-20260919.md`](observer-sentinel-published-surface-audit-20260919.md) | Whether any *published* numeric value can silently default to a sentinel: the README's tool rows and repo census cannot — they are static literals with named runnable artifacts. |
| [`observer-live-jev-call-20260919.md`](observer-live-jev-call-20260919.md) | Digs past the "no Jev calls" over-learning: the harm rule correctly contains none, but the observer still had a stub classifier POSTing to an unset `JEV_OBSERVER_ENDPOINT`, so every decision logged without a judgment. |
| [`waved-s16-claim.md`](waved-s16-claim.md) | §16 claim stub — observer live dogfood. **Superseded by** [`waved-s16-observer-dogfood-20260920.md`](waved-s16-observer-dogfood-20260920.md). |
| [`waved-s16-observer-dogfood-20260920.md`](waved-s16-observer-dogfood-20260920.md) | **FAIL — the shipped observer cannot fire.** Dogfood session: bridge 3 rows, observer 0; the deployed lab copy gets 2. The package has no `omp.extensions` entry, so it is not installable as shipped. |
| [`omp-jev-failure-live-20260919.md`](omp-jev-failure-live-20260919.md) | Live proof for the failure observer, with the omp source line for the extension event it subscribes to. |
| [`omp-jev-foreman-live-20260919.md`](omp-jev-foreman-live-20260919.md) | Live proof for `omp-jev-foreman`: 4 tests, disposable profile. |
| [`omp-jev-foreman-measure-20260920.md`](omp-jev-foreman-measure-20260920.md) | Its questions measured over three identical-bytes runs on eight constructed windows, scored against the construction label at 0.50. |
| [`omp-session-entry-adapter-20260919.md`](omp-session-entry-adapter-20260919.md) | The real `SessionEntry` adapter boundary, taken from an actual 43-row session file rather than from the type — the shape every extension has to read. |

## The routing extension (`omp-jev-route`)
| receipt | what it settles |
|---|---|
| [`route-questions-measure-20260919.md`](route-questions-measure-20260919.md) | Both routing questions discriminate: `needs_heavyweight` 8/9 (spread 0.83), `mechanical` 8/9 (spread 0.90), pooled 16/18 against a 9.0 coin flip, zero drift across runs. |
| [`route-rows-labelled-20260919.md`](route-rows-labelled-20260919.md) | 24 labelled rows, both questions right — **and effective n=1**, because all 24 rows come from a single turn. The receipt that stops a row count being read as a sample size. |
| [`route-ten-turns-20260919.md`](route-ten-turns-20260919.md) | Ten distinct turns: 7/10 per question. Traps show length leaks, but content leads. |
| [`route-turnstart-content-free-20260920.md`](route-turnstart-content-free-20260920.md) | **`turn_start` is content-free.** A routing extension subscribed there loads, fires, and can never judge anything — every turn exits silent. The prompt text lives on the `context` event. |
| [`eww-32-turns-20260920.md`](eww-32-turns-20260920.md) | 32 turns: both questions discriminate (spread 0.90 / 0.93) and the traps still bite — mechanical-clear drops to 6/10. |

## The commit judge, and mining the whole commit history
Includes the session's append-only ledger, which is the largest single receipt in the corpus.
| receipt | what it settles |
|---|---|
| [`commit-wired-audit-20260919.md`](commit-wired-audit-20260919.md) | Unit 1: `omp-jev-commit` is real Jev (not a stand-in), observe-only, and **installed nowhere**. Code read only, no call executed. |
| [`commit-judge-31-20260919.md`](commit-judge-31-20260919.md) | Unit 2: 31 real commits through real Jev, 31 keyed calls, truth read from diffs before scores were seen — **no question discriminates**. DEGENERATE / WEAK / WEAK. |
| [`commit-hook-refusal-20260919.md`](commit-hook-refusal-20260919.md) | Unit 3: **REFUSAL** — the commit-msg hook is not built, and the trigger is Unit 2's own result. A refusal with a named cause rather than a deferral. |
| [`cz0-labels-20260919.md`](cz0-labels-20260919.md) | How many live rows each extension actually produced, parsed rather than grepped: commit **0** (never registered), review **3, all `review_error`**, rerank **0**. Substring scans lie here because source code pasted into tool results contains the decision-type strings. |
| [`commit-mine-falsifier-20260920.md`](commit-mine-falsifier-20260920.md) | **Pre-registration** for the full commit-history mine, committed before the miner existed, with the coverage measurement that motivated it. |
| [`commit-mine-result-20260920.md`](commit-mine-result-20260920.md) | **Our verification levels mark documents, not evidence.** 1,040 non-merge commits mined; the commit history was the only one of the three corpora that is complete, local, free and finite. |
| [`level-confusion-20260920.md`](level-confusion-20260920.md) | Mechanical re-label of 1,043 commits under the proposed vocabulary (`receipt` for docs-only; strong words require a runnable change) — the confusion matrix that says how much the old labels were carrying. |
| [`level-sample15-20260920.md`](level-sample15-20260920.md) | A seeded 15-of-183 hand read of the docs-only `oracle|live` commits, to check the mechanical relabel against what the commits actually did. |
| [`commit-clusters-sketch.md`](commit-clusters-sketch.md) | Sketch of the last ~40 `origin/main` commits by subject rather than by invented count: the tip is negative capability — judges that are regexes, caches that collide, hand-built numbers that fail transfer, and one keepable seat. |
| [`commit-learnings-20260919.md`](commit-learnings-20260919.md) | **The session ledger — 1,928 lines, 57 entries, 56 commits, 9.7% of this directory.** Read the `##` headings as a table of contents and descend into the three that matter to you. Known defect: `STATUS.tsv`'s UP-R9 points at a section `s14e` that does not exist in it. |
| [`commit-learnings-20260920.md`](commit-learnings-20260920.md) | The 48-hour learnings pass, and the headline is against us: 21 extension packages built, 18 installable, and the register defect that discarded 2,531 calls. |

## The tool-call judge
One abandoned family (UP-R9) and the ruling that killed it.
| receipt | what it settles |
|---|---|
| [`toolcall-groundtruth-corpus-20260919.md`](toolcall-groundtruth-corpus-20260919.md) | 216k decisions mined into a ground-truth corpus: join yield 36.8%, error prevalence 3.95%, with the exact GOOD/BAD predicate written down. |
| [`toolcall-judge-v3-20260919.md`](toolcall-judge-v3-20260919.md) | v3, scoped to four classes: **IMPROVED** on the post-freeze corpus, and explicit that it claims nothing about live model quality — the scorer is a deterministic offline classifier. |
| [`toolcall-headtohead-20260919.md`](toolcall-headtohead-20260919.md) | Held-out real traffic: **the rule wins and Jev is dropped from this surface.** Both clear the bar (0/40 FP); the rule strictly dominates at 12/12 recall. |
| [`frozen-toolcall-scorer-20260920.md`](frozen-toolcall-scorer-20260920.md) | The frozen corpus's Studio numbers reproduced offline — baked figures reprinted, deliberately not re-derived as a new claim. |
| [`toolcall-multi-feature-judge-20260920.md`](toolcall-multi-feature-judge-20260920.md) | Multi-feature judge on the frozen file: **BEAT 0.212**. Offline mining, no invented cases. |
| [`toolcall-judge-jev-vs-regex-20260920.md`](toolcall-judge-jev-vs-regex-20260920.md) | **The v3 judge is a regex simulator.** Run verbatim over all 77,767 real commands it produces 28 fires at 0.036% and **28 of 28 are false positives**, one mechanism every time: text *about* a command, not a command. Supersedes v3's IMPROVED verdict as a statement about real traffic. |
| [`judge-seat-ruling-20260920.md`](judge-seat-ruling-20260920.md) | **Where a Jev judge earns its seat: one question out of seven.** The corpus's single most decision-relevant ruling, and the one that makes the four preceding rows add up. |

## Question shape, multiclass conversion, and the shared measure kit
How a question gets written, and how it is graded the same way everywhere.
| receipt | what it settles |
|---|---|
| [`question-shape-20260919.md`](question-shape-20260919.md) | Visible rephrasings rescue **3 of 7** failing questions, and the rule behind it: questions about a property visible in the text survive; questions needing a relative or counterfactual judgement fail. |
| [`question-shape-holdout-20260919.md`](question-shape-holdout-20260919.md) | The hold-out that decides which of those rescues are real: noise and argument hold, definitional holds with a boundary note, **destructive collapses**. Supersedes the tuned-set reading of the row above. |
| [`question-rescue-application-20260920.md`](question-rescue-application-20260920.md) | Ships the two rescues that survived the hold-out, and says which one carries a boundary — holdout-aware rather than committed-case-aware. |
| [`question-writing-loop-20260920.md`](question-writing-loop-20260920.md) | `jev-vbh.2` closeout: the loop that produces questions which beat their own constant on real traffic, plus the kill list of those that did not. |
| [`multiclass-failure-20260919.md`](multiclass-failure-20260919.md) | One multiclass question beats three binary ones, re-run through our own client rather than inherited: 11/11 on three consecutive runs of two wordings against a 9/11 binary baseline that emits structurally impossible rows. |
| [`failure-multiclass-holdout-20260919.md`](failure-multiclass-holdout-20260919.md) | The hold-out: **both framings 8/9 with the same miss.** The structure holds; the superiority does not. |
| [`measure-kit-20260919.md`](measure-kit-20260919.md) | One verdict arithmetic for the whole lane (`gradeQuestion`: correct, said-yes, own best constant, spread, near-threshold, verdict), with the route measurement ported to it at identical numbers. |
| [`gou-ports-20260920.md`](gou-ports-20260920.md) | Porting the rest to that kit: **6 PORTED, 8 NOT-PORTED, 0 proven verdict changes.** Zero new Jev calls by design — re-running live would move the numbers under comparison. |
| [`wavee-s08-claim.md`](wavee-s08-claim.md) | §8 claim stub — prevalence-first. **Superseded by** [`wavee-s08-prevalence-20260920.md`](wavee-s08-prevalence-20260920.md). |
| [`wavee-s08-prevalence-20260920.md`](wavee-s08-prevalence-20260920.md) | §8 **PASS**: prevalence-first ordering enforced in code and asserted per test arm (near count → own-constant bar → verdict), with a 31-call re-run and recorded drift. |

## CASS and Agent-Mail mines — should you dig into past work before inventing an answer?
The one finished stranger-readable question in the corpus. Every mine here is pre-registered; read the falsifier before the result.
| receipt | what it settles |
|---|---|
| [`cass-sampling-frame-20260920.md`](cass-sampling-frame-20260920.md) | What the window actually is: 120,000 message ids against a whole of 5,181,931 messages / 59,807 conversations / 780 workspaces — and **"recent" is a misnomer**, the id window spans the full era. |
| [`cass-mountain-findings-20260920.md`](cass-mountain-findings-20260920.md) | **The stranger-readable answer**: tested on 138 real questions against ~59,800 past agent conversations, when the archive returns hits, should the agent reuse them or write from scratch. Start here, then read its four qualifiers below. |
| [`cass-dig-vs-invent-20260920.md`](cass-dig-vs-invent-20260920.md) | The live mine and **the only copy of its numbers**: digging when any hit exists beats always-invent, 0.058 vs 0.159. Carries a conductor MERGE NOTE recording that a concurrent branch tried to replace this file with a pointer to an unfinished sibling. |
| [`cass-dig-vs-invent-mine-20260920.md`](cass-dig-vs-invent-mine-20260920.md) | **Unfinished duplicate.** Declares itself the canonical product-tick receipt, but its results section is still `TBD` and contains none of the numbers (`vgrep.sh --expect-zero -c '0.057971014'` → rc=0, i.e. absent). Do not cite it; the data is in the row above. Retire or fill in. |
| [`dig-subset-falsifier-20260920.md`](dig-subset-falsifier-20260920.md) | **Pre-registration** for the named-subset breakdown: DONE requires dig to beat always-invent on all five slices. |
| [`dig-subset-breakdown-20260920.md`](dig-subset-breakdown-20260920.md) | **HELD** — the pooled BEAT does not survive the slice table: `S_wrong_selector` has dig-iff at 0.500 losing to always-invent at 0.250. The fourth pooled number in this lane to fall to named subsets. |
| [`c1-calibration-expectation-20260920.md`](c1-calibration-expectation-20260920.md) | **Pre-registration** for human calibration of `S_wrong_selector`, committed before any full snippet was read. Note: this is the one pre-registration its own result never cites by name — nothing in this directory links to it. |
| [`c1-calibration-result-20260920.md`](c1-calibration-result-20260920.md) | **AGREES in direction, margin widened**: 2 flips, both 1→0; the published finding is not overturned and the 1:1 tie breaks toward invent. |
| [`c1-human-y.jsonl`](c1-human-y.jsonl) | The eight hand labels behind C1, with a one-line reason per row and the flips marked — the raw evidence the two rows above are computed from. |
| [`c2-branch-asymmetry-20260920.md`](c2-branch-asymmetry-20260920.md) | The strict/lenient asymmetry is real **and runs opposite to the feared direction**: zero of 22 positives came from the strict branch, and all four strict-routed rows with hits are the zeros that make the slice lose. |
| [`repsample-falsifier-20260920.md`](repsample-falsifier-20260920.md) | **Pre-registration** for the representative re-draw, committed before drawing or scoring, with the locked n=138 export pinned as the comparison arm. |
| [`repsample-result-20260920.md`](repsample-result-20260920.md) | **DONE — the finding is robust and the inversion deepens.** Against the conductor's pre-registered expectation that the inversion would weaken: same 4 rows, dig-iff 0.875 vs 0.250. The public page stands. This is what stops the headline being a window artifact. |
| [`mail-mine-falsifier-20260920.md`](mail-mine-falsifier-20260920.md) | **Pre-registration** for the full mail-corpus mine, committed before the miner existed, with as-of corpus counts. |
| [`mail-mine-result-20260920.md`](mail-mine-result-20260920.md) | **HELD for a seat, DONE as census**: F1 fires mechanically at 99.5% and is then discounted by its own key audit — the linkage is ambient co-presence, not action. |
| [`a11-join-falsifier-20260920.md`](a11-join-falsifier-20260920.md) | **Pre-registration** for the mail→cass join, naming all three keys before any scoring script existed. |
| [`a11-join-yield-20260920.md`](a11-join-yield-20260920.md) | The join yield: K1 project↔workspace gives **20 id-join paths**; K2 thread_id↔cass tokens gives **0 of 4,508**. The receipt that says which joins exist at all. |
| [`a12-refusal-falsifier-20260920.md`](a12-refusal-falsifier-20260920.md) | **Pre-registration** for the local-refusal prototype, with the mechanical snippet-literal proxy disclosed as a proxy. |
| [`a12-refusal-result-20260920.md`](a12-refusal-result-20260920.md) | **REFUSE**, on two independent legs: F1 fires, and the rule fires on the slice regex rather than the condition — fitted to the 16 rows that motivated it. |
| [`a18-offbus-falsifier-20260920.md`](a18-offbus-falsifier-20260920.md) | **Pre-registration** for the off-bus ACK probe on one precise K1 pair, naming the pair before scoring. |
| [`a18-offbus-result-20260920.md`](a18-offbus-result-20260920.md) | 287 unacked ack-required messages on that project, **0 in-window coverage** — the probe's denominator is its finding. |
| [`cass-mail-mines-a02-a05-20260920.md`](cass-mail-mines-a02-a05-20260920.md) | Mines A02 + A05 on the mail corpus: **do not chase elevated/ack by default** — always-abstain is the strong control until a feature clears the 2/3-style bar for the chosen loss map. Mechanical labels from columns, not send authority. |
| [`cass-mail-alpha-approaches-20260920.md`](cass-mail-alpha-approaches-20260920.md) | The design catalog these mines were drawn from. **Unpromoted, not a measurement** — it licenses later work and says so in its own header. |
| [`mines-nonauthor-review-20260920.md`](mines-nonauthor-review-20260920.md) | Non-author recomputation of four of the mines from the pinned export, mines not re-run: pooled numbers reproduce. The independence check on this whole group. |
| [`corpus-coverage-20260920.md`](corpus-coverage-20260920.md) | What the three corpora actually are and what to do differently — including the operational finding that a 1.85% ack rate means the coordination protocol asks for something agents almost never send. |

## Guards, hardening, and the `ee` learning loop
The instruments built because prose rules did not stop the defect recurring.
| receipt | what it settles |
|---|---|
| [`hardening-20260920.md`](hardening-20260920.md) | One session produced 26 silent-zero greps, 8 moved denominators, 4 lost-file branch switches and 4 pipeline exit-status misreads. **Classes turned into code stopped recurring; classes turned into prose did not.** The page that turned the mechanizable ones into commands. |
| [`hardening-stranger-grade-20260920.md`](hardening-stranger-grade-20260920.md) | Author grading their own hardening page with every runnable command executed and exit codes unpiped — no BROKEN, no runs-but-does-not-demonstrate. |
| [`hardening-census-20260920.md`](hardening-census-20260920.md) | Census of wired vs prose-only hardening, re-derived after both new guards landed. |
| [`hardening-census-rerun-20260920.md`](hardening-census-rerun-20260920.md) | **The re-run, and the pass has converged**: ranking unchanged, top prose-only count steady at 4, nothing new found. Supersedes [`hardening-census-20260920.md`](hardening-census-20260920.md) as the current state; further guards would chase shapes, not recurrences. |
| [`guard-dogfood-20260920.md`](guard-dogfood-20260920.md) | **LOADING PROVEN** — the guard rule firing live in a real session on a real piped bash command. |
| [`guard-fp-rate-20260920.md`](guard-fp-rate-20260920.md) | Its false-positive rate on a seeded 100-command sample from 78,242 harvest records, threshold frozen before any fire was seen, 67 fires hand-labelled one at a time. **The number stands; its `KEEP` disposition is superseded** by [`pipe-exit-reconciliation-20260920.md`](pipe-exit-reconciliation-20260920.md), which shows this measured precision *given a fire* rather than the decision axis. |
| [`pipe-exit-reconciliation-20260920.md`](pipe-exit-reconciliation-20260920.md) | **Settles the three contradicting `pipe-exit` rulings: not a conflict, three axes.** The decision axis — rate × precision on the defect population — had never been measured by any of them; measured here at 1.04% (812) with FP 3/20, keeping all four strong positives. R51's 55.2% reproduces to the unit (43,185/78,242), its 18.4% is **overturned** (refuted at z=9.96, and no slice or predicate variant reproduces it), the FP receipt's `KEEP` is superseded, and R48 was never in this fight. Author: `ReconcilePipeExit`. |
| [`pipe-exit-v2-dcg-mine-20260920.md`](pipe-exit-v2-dcg-mine-20260920.md) | The same class mined from the corpus nobody reads: `dcg` holds **223,945 `dcg_allow` rows** and **zero `ee` extensions read any of it** while `ee journal list` reports `entryCount 0` against 14,196 `bash_failure` rows. The narrowed v2 predicate fires **1.03%** with 0–1 FP of 10. The richest corpus we own and the memory system that needs it are not connected — that is the finding, not the rate. |
| [`hook-exit-code-sweep-20260919.md`](hook-exit-code-sweep-20260919.md) | **No silent default pass remains in the exercised hook paths.** The one `rc=0` missing-checker case requires an explicit risk override and prints a named skip — an intentional escape hatch, not an unqualified PASS. |
| [`measurement-premortem-20260920.md`](measurement-premortem-20260920.md) | "Observe every tool call" cut down to **NARROW**: no new capture, no private sink, no model, no unqualified "every" — a reporter over session JSONL with per-surface denominators. |
| [`ee-repair-blocked-20260920.md`](ee-repair-blocked-20260920.md) | **BLOCKED**: a memory that cannot be written to is not a component, and hand-repairing a corrupt shared store is out of scope. **Overturned in scope** by [`map-hook-ee-20260920.md`](map-hook-ee-20260920.md), which shows this measured the *home* store and a second store is healthy. |
| [`ee-repair-ready-20260920.md`](ee-repair-ready-20260920.md) | The follow-up: two defects found, one repaired on a copy, one past reach; `integrity_check` fails with 12 indexes on a table a normal-mode schema parse claims is missing. **Swap withheld.** |
| [`ee-loop-close-20260920.md`](ee-loop-close-20260920.md) | **MAP item 1: the `remember` → `preflight` loop does not close, and the reason is not migration drift.** `matchedMemories` is keyed on `--kind` (risk/anti-pattern/failure yes, the default `fact` silently no) and then hard-gated behind a closed builtin destructive-command set; `ee rule add` writes a separate table with no command-pattern column, so an authored rule can never enter `matches[]`. All four of today's defects are non-destructive and return 0/0 with an empty degraded. Author: `CloseEeLoop`. |
| [`alignment-operating-model-20260920.md`](alignment-operating-model-20260920.md) | What `franken_alignment` says our operating model is missing — the `DecisionClosure` shape that unifies decision, evidence and outcome. Found via the harvest index, not by guessing. |
| [`local-stack-map-20260920.md`](local-stack-map-20260920.md) | The local stack as measured, every node and edge derived by a command, **and it says where something is installed but dead** — the antidote to a map that draws intent and ships an observer with 13 passing tests and zero rows. |
| [`map-hook-ee-20260920.md`](map-hook-ee-20260920.md) | **Overturns a committed verdict**: `ee` is not dead, the integration already exists in a third surface, and the earlier BLOCKED measured a different store. The most recent correction in the corpus. |

## Class-D reuse — two refusals with triggers
| receipt | what it settles |
|---|---|
| [`classd-ceiling-sweep-20260919.md`](classd-ceiling-sweep-20260919.md) | **NOT-ANSWERABLE this way**: reuse is a long-horizon phenomenon — nothing fires before 80 messages, then inf jumps to 0.708 — so any generation window an arm could afford has a ~zero ceiling. A refusal with a reopen trigger, not a deferral. |
| [`ablate-rerun-classD-20260919.md`](ablate-rerun-classD-20260919.md) | **PREPARED-NOT-MEASURED**: 12 of 24 turns ran, every arm scored False on every turn on a shared box. The offline check that should have preceded the run is written down instead of the remaining 12 being spent. |

## Decision logging, denominators, and audit sampling
| receipt | what it settles |
|---|---|
| [`dogfood-logger-20260919.md`](dogfood-logger-20260919.md) | The decision/outcome JSONL schema every extension writes into — `schemaVersion`, `recordType`, and what a record is allowed to omit. |
| [`uncertain-sampling-20260920.md`](uncertain-sampling-20260920.md) | Uncertainty-window audit sampling over persisted rows: rank only rows within `|score − 0.5| ≤ 0.1`, then emit a score-independent deterministic random sample with stable ids. |
| [`denominator-audit-20260920.md`](denominator-audit-20260920.md) | Every claim with a regeneration command replayed through `pinned-denominator.sh`, exits unpiped: **zero drifts found, nothing fixed** — and the first replay attempt hitting the live register instead of the pinned one is the actual finding. |
| [`harvest-asof-20260920.md`](harvest-asof-20260920.md) | The live-harvest as-of audit: regen command recovered and re-run read-only, the 77 MB derivative deleted afterwards, and the "joinable" reconstruction marked as having no saved definition. |
| [`waveb-s6-eval-honesty-20260920.md`](waveb-s6-eval-honesty-20260920.md) | §6 **PASS** with zero Jev calls by design: the outcome-join, selector verification and zero-hit structure that make an eval honest are Jev-free tooling. |
| [`review-two-artifacts-20260920.md`](review-two-artifacts-20260920.md) | Non-author adversarial review of the behaviour-label and score-register units: **4/40 disagreements are real disagreements**, re-run to the same count, with fixes and planted tests in the same commit. |

## Repo self-audit — README, RULES, fresh clone, exports
The lane auditing its own published surface. Read these before trusting a number in the root README.
| receipt | what it settles |
|---|---|
| [`readme-numeric-claims-audit-20260919.md`](readme-numeric-claims-audit-20260919.md) | Every numeric row in the root README classified by whether it names a runnable command or committed artifact sufficient to re-run it. |
| [`readme-claim-sweep-20260920.md`](readme-claim-sweep-20260920.md) | Part 1, lines 1–488: "22 repos" is 24 clones with 11 RUN, and two more heading counts with it. Every runnable ran, exits unpiped. |
| [`readme-claim-sweep-part2-20260920.md`](readme-claim-sweep-part2-20260920.md) | Part 2, scope and reader paths — continues part 1 rather than replacing it: compaction's "32/32" is 38/38, and the hook's real scope is narrower than the prose. |
| [`readme-prose-check-20260920.md`](readme-prose-check-20260920.md) | Prose rather than numbers: 3 CONFIRMED, 1 STALE fixed — `NEGATIVE_EVIDENCE.md` has 50 `## R` headers where the README said 31. |
| [`rules-stranger-test-20260920.md`](rules-stranger-test-20260920.md) | Stranger test on `docs/RULES.md`: **TRUE with two fixes** — "Eight rules" for nine, and rules 1–2 never disclosing their session-log dependency. |
| [`fresh-clone-readme-commands-20260919.md`](fresh-clone-readme-commands-20260919.md) | Every README command run in a genuinely fresh public clone, each producer's exit code captured unpiped. |
| [`fresh-clone-rerun-20260919.md`](fresh-clone-rerun-20260919.md) | **The re-run, and the current answer**: one wrong fix line, one drift, everything else holds. Supersedes [`fresh-clone-readme-commands-20260919.md`](fresh-clone-readme-commands-20260919.md). |
| [`export-members-diff-20260920.md`](export-members-diff-20260920.md) | **SAME SET, no substitutions** — the published 19-of-21 census never wrote the names down, so the baseline had to be reconstructed by git archaeology. |
| [`export-resweep-20260920.md`](export-resweep-20260920.md) | **The re-sweep, and the current answer**: 19 dirs with model and persist hits, 2 NOT-APPLICABLE for the same reasons as published. Supersedes [`export-members-diff-20260920.md`](export-members-diff-20260920.md) as the state of the export claim. |
| [`honesty-window-buckets-20260918.md`](honesty-window-buckets-20260918.md) | USER / ENABLER / PROCESS classification of one commit window — **and the ruling that created this page**: upstream evidence is not USER shipping until promoted into a stranger-consumable surface. |

## Rulings on vocabulary, promotion, and gates
| receipt | what it settles |
|---|---|
| [`RULING-authored-vs-real-20260919.md`](RULING-authored-vs-real-20260919.md) | **Every candidate that looked good on authored data failed on real data** — and the two rules that follow: decompose into narrow typed questions, and always keep a dumb baseline (a two-line regex, a flat tier, prompt length and "keep everything" each beat the model at least once). The governing ruling for this whole directory. |
| [`verdict-vocabulary-20260920.md`](verdict-vocabulary-20260920.md) | **Two axes, not one.** Callback words (`DONE|HELD|REFUSE|BLOCKED`) and STATUS words (`CLEARED|HELD|RULED_OUT`) were sharing one slot; merging them is refused. `DONE` means the unit finished, `CLEARED` means the claim survived. |
| [`promotion-satisfiability-20260920.md`](promotion-satisfiability-20260920.md) | **SATISFIABLE** — the promotion bar was unreachable because it was undefined, not because it was high. Gate run offline on a `/tmp` TSV. |
| [`stage97-scope-ruling-20260920.md`](stage97-scope-ruling-20260920.md) | **SCOPE IT** for the README-counts gate: widening to every numeral in prose false-positives by construction, and refusing leaves the exact escape open — both derived facts have an exact machine source. |
| [`ubs-gate-ruling-20260920.md`](ubs-gate-ruling-20260920.md) | **KEEP_HAND_RUN_ONLY**, extracted verbatim from the concurrently-appended ledger so a `STATUS.tsv` digest can pin to a stable file. The extraction is the point: a digest pinned to the ledger drifts the moment a peer appends. |
| [`vbh4-shadow-20260920.md`](vbh4-shadow-20260920.md) | **REFUSE live action**: the shadow beats abstain and argmax on correct-minus-wrong, but all 5 errors sit in the trap-short class, so the abstention band catches the cautious middle rather than the hard cases. |
| [`vbh-program-closeout-20260920.md`](vbh-program-closeout-20260920.md) | The `jev-vbh` advanced-skills programme closed out child by child, with what shipped and what did not. |

## The six maps, and the stranger check on their synthesis
One slice each, all frozen at `038aeb4`, all synthesised in the root [`MAP.md`](../../../MAP.md). Read a map before you read its slice's receipts — and read the stranger check before trusting `MAP.md`'s numbers.
| receipt | what it settles |
|---|---|
| [`map-docs-20260920.md`](map-docs-20260920.md) | The documentation corpus: 407 `docs/` files plus 11 root. **The two findings this index exists to answer** — the citation surface reaches 9.2% of receipts, and orphanhood here measures age, not worth (orphan rate 12% → 25% → 32% across three days, with the authoritative later file being the orphan in 6 of 7 supersession pairs). |
| [`map-git-arc-20260920.md`](map-git-arc-20260920.md) | The git arc: 1,140 commits in 67 hours, and 40.4% of them sitting in abandoned scopes. |
| [`map-instruments-20260920.md`](map-instruments-20260920.md) | The verification machinery: 38 instruments wired, and nothing runs the driver. |
| [`map-work-packages-20260920.md`](map-work-packages-20260920.md) | `work/`: 53 directories measured — KEEP 39 / ALIGN 12 / DISCARD 2 — against a README partition that no longer matches. |
| [`map-stranger-check-20260920.md`](map-stranger-check-20260920.md) | Non-author re-derivation of every number in `MAP.md` at `1c2b4f0`: **7 of 10 reproduce exactly, 2 are overturned, 1 has no source anywhere** — guard-rule 200 → 148 (the 200 was a bare-grep artifact), 323,575 → 381,142 (a label sitting below the sum of its own children), "57 files use `appendEntry`" traces to nothing, and the 207-commit duel-2 blocker names the wrong file (`lane-status.sh:87` is fail-open; the real gate is `verify-other-reasons.sh:41` at stage 90). Also confirms the 9.2% this index answers, and that `206` counts tracked `.md` **including the README itself**. Author: `DogfoodMap`. |

The other two maps are listed under the subjects they measure, so they stay one index row each:
the hook/learning/`ee` loop map sits in **Guards, hardening, and the `ee` learning loop**, and the
skillranker map opens the **skillranker** group. Read either before its slice's receipts.

## Programme plans, surface maps, and unpromoted designs
Design-stage and synthesis documents. None of these is a measurement, and each says so in its own header — read them for what to build, never as evidence.
| receipt | what it settles |
|---|---|
| [`wave-plan-sections-passes-20260919.md`](wave-plan-sections-passes-20260919.md) | The named section-and-pass plan the wave receipts were claimed against. |
| [`deep-jev-skills-todo-20260919.md`](deep-jev-skills-todo-20260919.md) | The deep-Jev skills epic as a todo graph, with acceptance fixed at "a live command". |
| [`math-and-next-level-20260919.md`](math-and-next-level-20260919.md) | Math already in use, math sitting unused, and the next-level ticks — every numeral quoted from a committed receipt or a fetched upstream file, no live calls. |
| [`franken-crate-alpha-20260919.md`](franken-crate-alpha-20260919.md) | Ranked map of franken crates and processes with unused alpha for this lane. **Boundary stated: the executor never reached Studio**, so the evidence is the tip tree and existing receipts, not a live inventory. |
| [`franken-tooling-gaps-20260919.md`](franken-tooling-gaps-20260919.md) | Franken tooling owned but not applied — named holes only, with the same executor boundary: the live `fh`/`command -v` inventory was **not** run. |
| [`jev-juice-surfaces-map-20260920.md`](jev-juice-surfaces-map-20260920.md) | Where the remaining Jev leverage is, given their process and our omp surfaces. Unpromoted synthesis, no live call, `promoted = 0` unchanged. |
| [`jev-task-tests-cass-20260920.md`](jev-task-tests-cass-20260920.md) | Design only: Jev task tests for `cass`, with the contract shape taken from skillranker's eval policy. A contract, not a measurement. |
| [`jev-task-tests-beads-20260920.md`](jev-task-tests-beads-20260920.md) | Design only: Jev task tests for the beads DB. Licenses a later measurement and refuses to be one. |
| [`jev-task-tests-agent-mail-20260920.md`](jev-task-tests-agent-mail-20260920.md) | Design only: Jev task tests for Agent Mail — no harness, no live call, no omp registration. |
| [`monolith-census-20260920.md`](monolith-census-20260920.md) | **The code is fine; the documentation is the monolith.** Code LEAVE ALONE with rationale, docs DE-MONOLITHIZE starting at `PLAN.md`, with the README as the façade that makes the tree walkable. Line count only — complexity and churn were not measured. |
| [`museb-delta-20260920.md`](museb-delta-20260920.md) | The MUSE-B skill delta: two skills added, placeholders fixed, and every WHY citation verified against the file rather than accepted on faith. |

## Wave sections whose subject is their own surface
The remaining claimed sections. Each stub is superseded by its own full receipt.
| receipt | what it settles |
|---|---|
| [`waved-s19-claim.md`](waved-s19-claim.md) | §19 claim stub — taste-loop contracts, including the correction that a cited gate did not exist at claim time. **Superseded by** [`waved-s19-taste-contracts-20260920.md`](waved-s19-taste-contracts-20260920.md). |
| [`waved-s19-taste-contracts-20260920.md`](waved-s19-taste-contracts-20260920.md) | §19: **20 packages audited, 0 promoted.** All 20 import the asker or are regex-by-design; zero `fetch`, zero `block:true`; every suite run offline. |
| [`waved-s20-claim.md`](waved-s20-claim.md) | §20 claim stub — public `INTEGRATIONS` refresh, with all five facts verified against files before editing. **Superseded by** [`waved-s20-integrations-20260920.md`](waved-s20-integrations-20260920.md). |
| [`waved-s20-integrations-20260920.md`](waved-s20-integrations-20260920.md) | §20: 5 facts into the public integrations page and **1 qualifier added** — "unmeasured, 4/4 driven probes" became 0/28 over 80,975 real allows. |
| [`wavee-s09-claim.md`](wavee-s09-claim.md) | §9 claim stub — SDK-surface field traps, naming the `recording()` defect that files every successful choice call as `ok:false`. **Superseded by** [`wavee-s09-fields-20260920.md`](wavee-s09-fields-20260920.md). |
| [`wavee-s09-fields-20260920.md`](wavee-s09-fields-20260920.md) | §9 **PASS**: a singular `.score` on a Choice response would collapse the distribution to the argmax without its margin — precisely what the multiclass conversion was built to preserve. `jev-client` exposes no such convenience scalar, and any future one must not. |
| [`wavee-s10-claim.md`](wavee-s10-claim.md) | §10 claim stub — adopt the persona-clone eval harness, read from the file rather than the packet. **Superseded by** [`wavee-s10-persona-20260920.md`](wavee-s10-persona-20260920.md). |
| [`wavee-s10-persona-20260920.md`](wavee-s10-persona-20260920.md) | §10 **PASS**: the adopted harness's separate judge (never let the generator judge itself), golden-vs-trap split, and named TRAP-LEAK failure, plus our delta. |
| [`wavee-s23-claim.md`](wavee-s23-claim.md) | §23 claim stub — `dcg` explain-before-override, with the five conductor refusals taken as premises and marked as premises. **Superseded by** [`wavee-s23-override-20260920.md`](wavee-s23-override-20260920.md). |
| [`wavee-s23-override-20260920.md`](wavee-s23-override-20260920.md) | §23 **PASS** on a real denial and a real alternative, both quoted: the override path explains before it overrides, and the explicit single-file remove is what got taken. |
| [`waved-s24-claim.md`](waved-s24-claim.md) | §24 claim stub — infisical placeholder cleanup. **Superseded by** [`wavee-s24-cleanup-20260920.md`](wavee-s24-cleanup-20260920.md) — note the successor is named `wavee`, not `waved`; the stub is the only place the section's `waved` number is recorded. |
| [`wavee-s24-cleanup-20260920.md`](wavee-s24-cleanup-20260920.md) | §24 **PASS**: exactly two `projectId=<id>` placeholders survive across the whole tree, both the known defect from the Pass 6 notes. |


---

## What this index does not establish

- **It does not re-verify a single receipt.** Each line says what its file *claims to settle*, taken
  from that file's own title, verdict block or headline. Where two receipts disagree the later one is
  marked as superseding, again on the files' own statements — no measurement was re-run to arbitrate.
- **`[historical]` and *superseded* are dispositions, not refutations.** A superseded receipt is
  usually still correct about the day it was written.
- **The group boundaries are editorial.** 37 filename clusters cover 150 of the receipts; the rest
  were placed by reading them. A receipt can honestly belong to two groups, and two do.
- **Nothing here was renamed, moved or deleted.** The one duplicate found
  (`cass-dig-vs-invent-mine-20260920.md`, which declares itself canonical and holds no numbers) is
  flagged in place for its owner.
- **There is no "cited" or "safe to delete" column, deliberately.** Besides the age artifact, an
  uncited receipt can still be load-bearing in a way no index can see: `map-stranger-check` found
  that `docs/demos/duel-2/FALSIFY_COD-H2_MU.md` is the only in-repo source for the refusal of the
  published routing-savings figure and is cited by nothing machine-checked, while 15 other
  `duel-2` receipts are hard-required fail-closed by `lane-status.sh`. Any index that scored
  citation count would have marked the load-bearing one disposable.

## Appendix — the 2026-09-19 promotion surface

Everything below this line is the previous edition of this file, kept word for word. **The only
change is heading depth — every heading is pushed down two levels so the appendix nests under one
top-level heading. No sentence, number, link or table cell was touched.**
It is the stranger-consumable promotion surface that
[`honesty-window-buckets-20260918.md`](honesty-window-buckets-20260918.md) ruled was required
before upstream evidence counts as shipped, and
[`promotion-grade-20260918.md`](promotion-grade-20260918.md) graded it as one. **Scope: it covers 18
of the 227 artifacts and stops at 2026-09-19** — the index above is the current surface.

---

### What 22 Jev repositories say when you actually run them

Written for someone who does not work on this lane. Every line below was produced by running
somebody else's code on somebody else's data, and every claim links to the receipt that produced it.
We patched none of these repositories. **Every one of the 22 vendored clones has now been run**
(completed 2026-09-19 on Joshua's order: *"stop NOT USING the repos we've downloaded"*), and the
last four taught us more than the first eighteen.

This page exists because a reviewing pane ruled that upstream evidence *"is not USER shipping until
promoted into a clear stranger-consumable surface"*
([`honesty-window-buckets-20260918.md`](honesty-window-buckets-20260918.md)). Receipts in a folder
are not a surface. This is the promotion.

#### The short version

**A plain-English question with no labels is competitive with a classifier trained on thousands of
them, and the gap widens on mail the classifier was not trained for.** Elaborating the question makes
it worse. Jev is fast and cheap enough to ask per item, and it trails general models on aggregate
workflow scores, so the interesting question is never *"is it better"* but *"where does a typed
judgment beat a trained model or a hand-written rule."*

#### What each run returned

| Repo | Finding | Receipt |
|---|---|---|
| `jev-spam-eval` | Ling-Spam: **0.9857** with zero labels against **0.9941** for TF-IDF on 2,300 labels. Same accuracy to four decimals, **opposite failure shapes**: 2 false negatives and 39 false positives against 40 and 1 | [lingspam](lingspam-20260918.md) |
| `jev-spam-eval` (OOD) | on mail unlike the training mail the labelled model collapses: **91.3% against 70.3%** on recent phishing, **97.00% against 72.51%** on modern mail | [ood](jev-spam-eval-ood-20260918.json) |
| three corpora | **elaborating a question costs accuracy.** Ling-Spam plain 98.57% against structured 97.01% (p=1.4e-9); a **names-only** question beats an elaborated one 98.58% to 97.00% (p=.0064); one comparison is directional only (p=.50) | [criteria-inversion](criteria-inversion-20260918.md) |
| `jev-rerank-bench` | one benchmark, two answers: the committed cache puts Jev at **0.692 against Cohere Pro 0.691, inside noise at p=.910**, while a fresh run over 1,383 pairs gives **+4.2 points at p=.002** | [rerank](jev-rerank-bench-20260918.json) |
| `jev-benchmark` | **corrected 2026-09-18**: its author reports the two model versions *"not separable at this sample size"*. Pairing the runs shows **zero discordant pairs and identical choices on 60/60**, so **no increase in n on that task set can separate them.** Four of five shared misses are one confusion | [pairing](jev-benchmark-pairing-20260918.md) |
| `jev-phishing-bench` | the keyless floor reproduces **exactly** (0.9165 / 0.8350 / 0.0020) | [phishing](phishing-20260918.md) |
| `typesafe-ai-benchmark` | **7/7** documented offline examples green, after a missing install step that its docs omit | [benchmark-examples](benchmark-examples-20260918.md) |
| `jev-mcp` | three Jev tools live inside a coding harness: **9/9 unit, 4/4 end-to-end**. Without a key the live tests **skip and say so** rather than counting as passes | [mcp](jev-mcp-20260918.md) |
| `fast-jev-compaction` | **29/29** tests; a live run took 21 messages to 7, saving **87.1% of characters** in one request at 1,277 ms | [compaction](fast-jev-compaction-20260918.json) |
| `foreman` | **57/58**. It is a per-worker *supervisor*: there is no queue concept, so a worker idle **while work is ready** reads as finished | [foreman](foreman-20260918.md) |
| `s1-rs` | both examples run offline against a `FakeClient`: typed questions in, `nearest=Annoyed expected=1.20` and `urgent p=0.97` out. Blocked all day by a **misdiagnosed** obstacle, not by Rust | [s1-rs](s1-rs-20260918.md) |
| `simple-jev` (open source) | an **open-model implementation of the same interface**, free and keyless. Asked this lane's hardest classification it returned `derived_rollup` at **0.989** in 1.7s | [simple-jev](simple-jev-20260918.md) |
| `jev-sec-bench` | injection detection at **96.5% / AUC 0.9927** over 662 messages, and an ablation that **replicates our framing-leak finding**: recall 74.9% bare against 95.1% with context | [sec-bench](jev-sec-bench-20260918.md) |
| `jev-agent-failure-benchmark` | this lane's own question at **n=6257 with intervals**, against our single runs. Its **leakage test silently skips** without the pinned 73 MB dataset | [agent-failure](agent-failure-benchmark-20260918.md) |
| `jev-review` | a code-quality scorer that returns **`applicable: false`** for dimensions its context cannot support: a refusal-to-score state shipped as contract, not retrofitted | [jev-review](jev-review-20260918.md) |
| `bicameral` | the System 2 writes / System 1 judges split is real, with two differences worth copying: **judgment is a pluggable interface**, and its degraded path **falls back to pattern rules rather than passing work through unjudged** | [bicameral](bicameral-20260918.md) |

#### Three things worth taking from these, whoever you are

1. **Ask the short question.** Across three paired comparisons the elaborated question never won, and
   the shortest one won outright where it was tested. `jev-spam-eval`'s own README says its headline
   came from a question *"written after reading the mistakes in 1,000 sampled emails"*, which is the
   same effect from the tuning side. That makes this a confirmation rather than a discovery.
2. **Pair your runs before blaming your sample size.** Two aggregate scores that match can hide
   either agreement or noise. `jev-benchmark` has both result files on disk; pairing them takes a
   dozen lines and answers a question its own caveat leaves open.
3. **Decide what your degraded path does before you need it.** `bicameral` falls back to patterns.
   Reading that sent us to our own commit hook, where one lane refused a missing checker and another
   silently permitted the commit. A fail-open path that never fires is indistinguishable from a
   correct one until the day it matters.

#### What none of this establishes

- **No head-to-head we ran is ours.** These are other people's harnesses and corpora; we reproduced
  and re-analysed, and where we disagree with an author it is stated against their own data.
- **Vendor-reported aggregates are attributed, not verified.** TypeSafe's dashboard is quoted at
  67.8% against 74.1% for the best comparator from secondary write-ups; we did not read the dashboard.
- **Twelve of the twenty-two repositories cloned here are unrun**, listed row by row in the root
  [`README.md`](../../../README.md). `s1-rs` is blocked on a platform mismatch, not a finding.
- **Live figures cost real calls** and were run once. Nothing here is a reliability measurement, and
  no figure on this page should be read as a benchmark of the current model.

#### 2026-09-19 — the last four clones, and what running them cost us in retracted claims

Four repositories sat unrun while this lane built its own versions of their questions. Running them
produced the session's only shipped-code defect **and** forced three retractions of our own work.

##### A timeout in `typesafe-sdk-js` kills a default Node process

Their suite reports **189/189 passing with 8 unhandled errors** — Vitest's own warning is that this
"might cause false positive tests". Run file by file, all 8 come from one file, which makes exactly
8 aborted requests: **one leaked rejection per timed-out request.**

Outside their harness entirely — real `node:http`, real global `fetch`, no test doubles — a single
timed-out call gives the caller the correct `APITimeoutError` and then **kills the process**
(`exit 1`, from `client.ts:421`). Repro: [`sdk-js-timeout-crash-repro.mjs`](sdk-js-timeout-crash-repro.mjs),
report: [`sdk-js-timeout-crash-20260919.md`](sdk-js-timeout-crash-20260919.md).

**And the same vendor's Python SDK does not have it.** Identical scenario:
`TypeSafeAPITimeoutError` to the caller, **zero** leaked async errors, process survives
([`sdk-python-20260919.md`](sdk-python-20260919.md)). That control is what turns "async timeouts are
hard" into "this is a defect", and it only exists because the Python clone got run too.

##### The vendor's own guidance was in the tree, unread

[`typesafe-ai/skills`](sdk-js-and-skills-20260919.md) is TypeSafe's own instructions for designing
Jev judgments — meaning belongs in `instructions` because question IDs are never sent to the model,
state must be complete, include a no-match outcome. We had spent a day designing judgments without
opening it. Checking our code against it found **nothing to fix**, for the useful reason that we
author no questions at all: we delegate to `fast-jev-compaction`, which already complies.

##### Three claims of ours that did not survive contact

| we said | what the control showed |
|---|---|
| the JS SDK's timeout timer leaks | `clearTimeout` is in the `finally`; the caller path is clean. Right impact, **wrong mechanism** |
| `skillranker`'s README documents a CLI that does not exist | our clone is **103 commits stale**; the commands are wired on `origin/main`. **Retracted** ([`skillranker-20260919.md`](skillranker-20260919.md)) |
| a gate run was hanging on our own code | it was a 77s stage against a 60s timeout — **no hang at all** |

No upstream report was filed for the `skillranker` "gap", which is the point of holding reports for
a human: it would have told a maintainer their docs were broken when the defect was our pin.

##### What this is worth to someone outside the lane

Four of the six things the sweep produced are things we were about to build ourselves and did not
need to. The pattern is consistent enough to state plainly: **before writing code to answer a
question, check whether a repository you already cloned answers it, and run that instead.**

#### Provenance of the figures on this page (audited 2026-09-19)

Every numeric claim in the root README's twenty-two-repo table was checked against a committed
receipt. **Fifteen claims, fourteen backed, one fabricated.**

The fabricated one said the agent-failure benchmark scored *"18/20 without the pinned dataset"*.
That string appears in no receipt, and what the receipt records is that a bare `uv run pytest`
**fails collection** — the pinned `whowhen_eval` dependency is absent, so there is no score at all.
A dependency failure had been written up as a degraded result. Corrected in `db37dac`.

**All three weak links are now closed by re-execution, not argument.** `29/29` was upgraded from
index-backed to re-executed (fresh `npm install && npm test` in `fast-jev-compaction`: 2 files, 29
passed). The two live figures — `87.1% chars saved` and `21 messages to 7` — traced only to a pane
callback, so upstream's own `examples/demo.ts` was run against a real key:

```
stats: {"messagesBefore":21,"messagesAfter":7,"charsBefore":4475,"charsAfter":577,
        "callsDropped":7,"requests":1,"ms":1377}
chars saved: 87.1%
```

Exact match to the figure this page had been carrying on a callback's word.

**`RECIPES.md` audited too, 2026-09-19 — clean.** Every figure on the recipes page traces to a
receipt: the four phi/gain pairs and the Ling-Spam accuracies were re-derived directly this
session, and the criteria-inversion row matches `criteria-inversion-20260918.md` exactly
(`97.00% -> 98.58%`, exact McNemar `p = 0.00635`, which the page rounds to `0.0064`). The one
figure that failed a first grep failed on **rounding, not on truth** — worth stating, because an
automated version of this check would have flagged a correct number.

**What this audit does not establish:** it checks that each figure *appears in* a receipt, not that
the figure is *correct*. A wrong number copied consistently into both the receipt and the README
passes unchanged. Prose claims — "headlines reproduce", "floor reproduces exactly" — were not
re-executed.

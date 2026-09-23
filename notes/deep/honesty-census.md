# W2.1 honesty census (B13 + B12 + B11 as numbers)

Bead `jev-deep-kit-8q7.5`, pane 6 QuietHarbor. Bead census counted at commit
`83300a1` (`.beads/issues.jsonl` blob extracted from that commit; the blob
is deterministic, unlike the live tree, which has since advanced past
`83300a1` with peer commits and one uncommitted row, `jev-pkd` — neither is
in these numbers). All other checks ran on the live tree 2026-09-22/23 at
their stated times. Scope: jev tree only. No key spent.

## Preregistered

(a) B13 close rules: OK iff len(close_reason)>=20 AND (names_command OR
commit_resolves OR path_exists). Else REPAIRABLE iff evidence elsewhere
(`git log --all --grep=<id>`, or the id in notes/foundation/demos/docs/work/
README/EVAL/NEGATIVE_EVIDENCE, EXCLUDING this census's own two output files —
added after the recount caught the instrument reading its own TSV as
evidence). Else NO-EVIDENCE. names_command = backtick span, known runner +
arg, ./path, or word.(mjs|mts|py|sh|ts). names_commit = first [0-9a-f]{7,40};
resolves via `git cat-file -e <sha>^{commit}`. names_path = first
/-containing token resolving under repo root. Denominator: all closed rows.
Feasibility: corpus median reason len 208 → OK>0; repair targets bare 'done'.

(b) B12 rule: README unit (sentence; table row) counts iff NUM_RE
(\d+/\d+ | \d+\.\d+ | \d+\s*(%|ms|s|chars|rows|calls|jobs|bundles|questions|
docs|claims|passages|pairs|examples|minutes|hours|days|samples)) or WORD_RE
(verified|passes|beats|wins|exits 0, case-insensitive); fences excluded.
Covered iff a claims.tsv readme_pattern is a case-insensitive substring.
Denominator: rule-matching units. Feasibility: the registry's only pattern
('Call the official SDK.') exists in README, so the instrument can in
principle report covered>0.

(c) B11 rule: ledger ## R sections with retry-condition blocks. Observable
today = names a checkable SHA (manifest/HEAD), binary version, repo file,
doc sentence (omp:// docs read in-session), or disk-computable count.
Satisfied-NOW = trigger true now with action still open (resolved/consumed
triggers reported separately, not counted). SHA-move form: `moves past X`
vs manifest pin. Denominator: unique R rows bearing predicates.

## (a) B13 — 70 closed: 40 OK / 30 REPAIRABLE / 0 NO-EVIDENCE

Full rows: `notes/deep/false-close-census.tsv` (70 data rows, spec columns).
Short reasons (<20 chars): 11/70, all bare `done`: jev-0c6, jev-cz0, jev-eww,
jev-gou, jev-kma, jev-kqf, jev-publish-readme-ho1, jev-vbh.1–4.
NO-EVIDENCE started at 2 (jev-g3i len 175, jev-g8p len 613 — long reasons
with no machine-readable token and no elsewhere id-mention) and both moved
to REPAIRABLE on independent verification (B13 recount, report via hub):
g3i's `unblocker jev-v6j filed` checks out (jev-v6j closed at 83300a1,
acceptance met); g8p's cited numbers match
`docs/demos/upstream-repro/absence-n77-verdict-20260920.md` verbatim (n=77,
FP 21, Wilson upper 0.381) and the 4-count is verifiable in
`scripts/selftest-ttsr-assert-disabled.sh` (blob ac5e3004). Decisive
commands re-run here: same blobs, `git cat-file -t`
e9b492e/51edc23/4c137e2 all `commit`. The live re-runs behind both closes
remain unverifiable offline (--live prohibited) and are stated as such, not
counted. Lesson for the rule: comment content and cited-file content are
evidence the three regex arms do not read; a future arm should open comments.
Second routes: br CLI counts agree (70/18/14/5 live incl. uncommitted
jev-pkd); committed blob 106 rows (70/18/14/4).
Planted negative: synthetic closed row with close_reason `done` in a /tmp
JSONL copy → NO-EVIDENCE. (`python3 /tmp/jev-w1/census_close.py $PWD <jsonl>`)

Open rows at 83300a1 (18 in_progress + 14 blocked, ages at count time):

```tsv
status	id	updated_at	age_h	assignee	title
in_progress	jev-publish-scrub-b94	2026-09-18T00:59	116.3	-	Scrub tree for publish: signatures, paths, receipts
in_progress	jev-demo-loop-a1q.4	2026-09-18T01:41	115.6	-	fleet-idle-monitor: reports the USER SHELL as actionable
in_progress	jev-publish-hero-ulo	2026-09-18T02:23	114.9	-	Hero image pipeline for jev_playground
in_progress	jev-demo-loop-a1q	2026-09-18T07:25	109.9	-	Jev demo loop: backlog, cadence, and demo-1 shipped
in_progress	jev-32z	2026-09-19T17:01	76.3	-	Gate questions vs real routine tool calls
in_progress	jev-vbh	2026-09-20T15:37	53.7	Muse	Advanced Jev skills program (MUSE)
in_progress	jev-k9z	2026-09-21T19:54	25.4	pane4	jev valid-apps bridge: advisory quadrant after veto ZERO
in_progress	jev-6u0	2026-09-21T21:14	24.1	pane4	Split EVAL expectations from receipts
in_progress	jev-k9z.5	2026-09-22T02:11	19.1	-	jev guardrails advisory flag
in_progress	jev-7px	2026-09-22T02:12	19.1	-	bead graph has zero dependency edges
in_progress	jev-obf	2026-09-22T02:21	19.0	-	ARM6 blind spot: lane-status-integrity
in_progress	jev-v8-kit-drive-m0e.3	2026-09-23T01:29	19.8	-	v8 gap refresh
in_progress	jev-v8-kit-drive-m0e.4	2026-09-23T01:37	19.7	-	v8 packet numbers
in_progress	jev-deep-kit-8q7.2	2026-09-23T02:24	18.9	TopazRaven	W4.1-2 franken dependency/citation audit
in_progress	jev-deep-kit-8q7.3	2026-09-23T02:25	18.9	MistyTurtle	W3.1 mechanism transfer matrix
in_progress	jev-deep-kit-8q7.4	2026-09-23T02:25	18.9	SunnyTiger	W5.1 jev self-assessment packet
in_progress	jev-deep-kit-8q7.5	2026-09-23T02:25	18.9	QuietHarbor	W2.1 honesty census
in_progress	jev-publish-playground-hog.1	2026-09-22T02:25	18.9	-	PUBLISH BLOCKER: tip scrubs vs history
blocked	jev-publish-playground-hog	2026-09-18T15:43	101.6	-	Publish jev as jev_playground
blocked	jev-foundry-selftest-git-template-coc	2026-09-18T16:01	101.3	jev	Foundry bug: house-gate selftests
blocked	jev-route-jev-oracle-row-7ou	2026-09-18T16:03	101.2	jev	Route: no oracle row for jev/System One
blocked	jev-stampcheck-vendored-false-positives-lfn	2026-09-18T16:04	101.2	jev	Foundry bug: stamp-check vendored clones
blocked	jev-route-standards-manifest-6yq	2026-09-18T16:05	101.2	-	Route: add jev to fh manifest
blocked	jev-gate-error-decorrelation-ltk	2026-09-19T03:52	89.5	-	Measure error decorrelation across gates
blocked	jev-vbh.5	2026-09-20T10:01	59.3	-	Skill: dont-give-up Pass 6 only
blocked	jev-7ge	2026-09-21T19:44	25.6	-	Adopt skillranker matrix-row ledger
blocked	jev-3w8	2026-09-21T19:44	25.6	-	Adopt single-fn composed phase gate
blocked	jev-jwr	2026-09-21T19:47	25.5	-	jev sr-withhold upstream filing
blocked	jev-k9z.1	2026-09-21T19:55	25.4	pane4	jev rerank advisory
blocked	jev-k9z.2	2026-09-21T20:15	25.0	pane4	jev review advisory
blocked	jev-k9z.4	2026-09-21T20:15	25.0	-	jev triage advisory
blocked	jev-k9z.3	2026-09-22T02:11	19.1	pane4	jev intent routing
```

## (b) B12 — 0 registered (denominator splitter-dependent: 35 mine, 32 verifier)

README was rewritten mid-count (SDK sentence moved 273→125; HEAD e3dd0c4),
so the first 0/37 run is superseded. Re-ran the same script and rule on the
current tree: 35 candidates, 0 covered. Independent block-based recount: 32
candidates of 192 units, 0 covered. Numerator 0 under every route; the
denominator moves ±3 with the splitter — a rule-precision finding, stated,
not smoothed. Caveat, load-bearing and unchanged: the registered sentence
itself (now README:125, `Call the official SDK.`) does NOT match
NUM_RE/WORD_RE, so it is outside the denominator by the packet's own rule.
A coverage floor built on this rule starts at 0. (`python3
/tmp/jev-w1/census_claims.py $PWD`)
Planted negative: `The new gate exits 0 on all 99 rows.` appended to a /tmp
README copy → counted candidate, uncovered. (`python3
/tmp/jev-w1/census_claims.py $PWD`)

## (c) B11 — 48 predicate rows; 4 triggers satisfied NOW

Extractor: `python3 /tmp/jev-w1/census_resurrect.py NEGATIVE_EVIDENCE.md
upstream/MANIFEST.tsv` → 82 sections, 56 predicate blocks, 0 SHA-move hits.
Unique R rows bearing predicates: 48. No-predicate rows: R2,R3,R4,R33,R36,
R39,R74 (7); rest are amendments/corrections referencing parents.
Resolved/consumed (fired and acted, nothing pending): R6 (executed
2026-09-20), R12 (fired+resolved 2026-09-18), R25, R26 (same-day retries),
R28a (Joshua reclaim). Satisfied NOW, each with its deciding command:

1. R16 — new labelled corpus without the three-arm procedure. Corpus rows
   `work/nev-differential/rows-*.jsonl` dated 2026-09-21 (`ls -la`), R16
   refuted 2026-09-18; `grep -rn method_gain|regexfloor|regex.floor|fitted`
   over `work/nev-differential/` returns empty. The head-to-head ran Jev vs
   two chat models, never verdict-only vs regex-floor vs fitted-signals.
2. R37 — published commands changed without a fresh-clone-table rerun.
   `git log --since=2026-09-19 -- README.md` shows 20+ commits incl. a new
   demo command (`021ded6`); `find . -name '*fresh-clone*'
   -newermt 2026-09-20` (minus node_modules/.git) returns empty; newest
   table is `docs/demos/upstream-repro/fresh-clone-readme-commands-20260919.md`.
3. R38 — 7 code instances of `?? 'unknown'` (≥3). `rg -F "?? 'unknown'"
   -g '*.ts,*.mts,*.mjs,*.py,*.sh'` minus node_modules/docs: 5 own-tree
   (compaction/src/omp-adapter.ts:94, work/jev-score-register/register.mjs:
   127,176, demos/retransmit-whatif/src/reader.mjs:43,
   demos/usage-shape/bin/shape.mjs:51) + 2 vendored (typesafe-ai-benchmark
   ×2). Per-letter the trigger holds; severity triage (display fallback vs
   stored truth field) is follow-up work, not counted here.
4. R68 — consumer-check emits tier verdicts and resolves one hop.
   `scripts/consumer-check.sh:131` prints `NO NON-TEST CONSUMER`;
   `:64-67` resolve one hop up to a gates.d stage; live run on
   compaction/src/omp-adapter.ts exits 1 with tiered output (run
   2026-09-23). Reinstatement condition met.
   Planted negative: synthetic R999 (`moves past deadbee123` vs manifest
   `a1b2c3d`) → SATISFIED-planted; real ledger → zero SHA-move hits.
   Also ruled: R73 gate HOLDS (most-common constant 0.3776 on n=137063
   tool-select rows clears 0.25 — computed, not a trigger); R5 CHECK PASS
   (`sync-docs.sh --check`, 114 files); R1/R7/R21 doc triggers absent in
   omp://rpc.md and omp://compaction.md read 2026-09-23
   (no pane field; no cancelled semantics; no pruned-history channel);
   R72 sentence absent in omp://extension-loading.md; R17 STATUS.tsv absent;
   R43b `br dep cycles` clean; R42a one skill (<32); R34 verifier still
   0/38 (`node work/omp-harm-rule/verify-claim.mjs`, rc=0, run 2026-09-23);
   R35 no edits since 2026-09-19; R30/R69/R44/R45/R71 no new corpus or
   rerun on disk; R75 no certified seat; R76 adapter present.

## Addendum: pin-liveness RED — diagnosed, script untouched

`bash scripts/selftest-pin-liveness.sh` reproduces pane 1's report: 7 ok, 1
FAIL (`row pinned to a hot file exits 3 — wanted rc=3 got rc=0`).
Root cause: the arm pins a row to the REAL `NEGATIVE_EVIDENCE.md` at
threshold 1 and `scripts/pin-liveness.sh:57` counts `git log
--since=24.hours -- <receipt>`. Last touch of that file is 2026-09-21
17:09 -0600 (`git log -3 --format=%ci -- NEGATIVE_EVIDENCE.md`); now is
2026-09-22 20:33 -0600, i.e. 27.4h — outside the window, count 0 < 1.
Second route: `--since='24 hours ago'` also returns 0. The selftest comment
("threshold 1 guarantees the hot-file condition regardless of today's rate")
is false: threshold 1 tests commit recency, and any 24h quiet spell on that
file turns the RED demonstration green. A liveness check with a
time-windowed definition of live, pointed at a live path, is flaky by
construction; a synthetic hot file would hold still. Impact on W2.1(c):
none — no (c) verdict used pin state; all SHA/version/file checks read
manifests, HEADs, and docs directly. Any future pin-move automation via
pin-liveness inherits this flakiness.

## Verification status

Independent subagents, all integrated: B11 second routes all HOLD (R16/R37/
R38/R68 with own commands, report via hub 2026-09-23 — including the R38
file:line list matching mine 7-for-7 and the R68 run on a second instrument
with exit 1 and tiered output). B13 recount agrees (106 rows at 83300a1:
70/18/14/4; 11 short, all 'done') and overturned my g3i/g8p NO-EVIDENCE labels
with comment/receipt evidence I re-ran and confirmed — both now REPAIRABLE
with named artifacts, census at 40/30/0. B12 recount agrees covered=0 but
disagrees denominator (32 block-based vs my 35 line-based on the rewritten
README; earlier 37 was the pre-rewrite tree) — numerator 0 under every
route, denominator variance stated in (b).

NO-CLAIM: census counts are not enforcement; a satisfied trigger is a
resurrection candidate, not a reopened row.

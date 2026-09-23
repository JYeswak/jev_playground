# awesome-jev W7.0 receipt — 2026-09-23 (worker W70AwesomeJev)

Catalogue profile: T1 pin+env + T3 over entries. No live Jev calls
(N=0, cost $0, no p50/p95 — nothing was asked of any model).
Pin predates all data collection. `EVAL.md` not edited. Clone tree never written.

Scope rule (this receipt): an entry is in scope iff its catalogue blurb states a
numeric Jev-behavior claim (latency, cost, N, accuracy, count) OR names a
bench/eval/benchmark harness. SDK/client entries (L65–83) state no Jev numbers
and are out of scope by profile; cookbooks/patterns/docs/article links without
numbers are likewise out of scope, except L205 (0.7 s measurement claim).
17 in-scope rows: 4 shared → pointer to the sibling receipt (not re-audited);
4 unique with local mirrors → full rows; 9 unique without mirrors →
catalogue-only.

Overlap source: `docs/demos/upstream-repro/awesome-typesafe-w70-2026-09-23.md`
(worker W70Catalogue, 8 rows, T3 PASS). Shared entries below cite its row, no
re-audit.

## T1 — Pin and environment

- Path: `/Users/josh/Developer/jev/awesome-jev`, remote
  `https://github.com/AnotiaWang/awesome-jev`, branch `main`
- SHA: `ef193004eba48e83339a6e7498e70530badd23a5`
- Date/author/subject: `2026-09-17T23:43:20+08:00`, AnotiaWang,
  `收录近期社区 GitHub 项目，并补两则有意思的 demo`
- License: CC0 1.0 Universal (`LICENSE` head: "CC0 1.0 Universal … CREATIVE
  COMMONS CORPORATION IS NOT A LAW FIRM …"); README points at it (L223–225)
- Tree: `.gitignore`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, `README_zh.md`
  (`git ls-tree -r --name-only HEAD`)
- `git status --porcelain=v1 -uall`: empty before and after (read-only run;
  receipt lives outside the clone). `STATUS_EXIT:0`
- Observation clock: `2026-09-23T03:41:12Z`
- Runtime: Python 3.9.6, Darwin 25.5.0 arm64, host `Joshs-Mac-Studio.local`
- Env (inherited, recorded honestly): `OMP_PROFILE=muse`, `PI_PROFILE=muse`,
  `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/muse/agent`. Read-only run;
  no inference was issued so profiles had no effect. (Prior-day receipt unset
  them; this worker records the harness default instead of mutating env.)

## T3 — Entry table

"Suite?" = does the upstream repo state a runnable command (read-only local
mirror; nothing cloned, nothing executed, no fetch per No-live-calls profile).
"Quoted with N?" = does the *catalogue blurb* state a Jev number with its
denominator. Mirror SHAs are full `git rev-parse HEAD` in the workspace.

### Shared entries — pointer to sibling receipt, not re-audited

| # | Entry (catalogue line) | Sibling row |
|---|---|---|
| S1 | openjev (L158) | awesome-typesafe row 7 (OpenJev → SemIf rename flag; catalogue quotes no Jev number; upstream quotes open-model Ns, reads Jev's 0.883 from TypeSafe records) |
| S2 | typesafe-ai-benchmark (L161) | awesome-typesafe row 8 (reproduce: `npm ci`, `npm run build`, `npm run start:demos:live`; catalogue quotes no number) |
| S3 | Jev Rerank Bench (L162) | awesome-typesafe row 5 (reproduce: `uv run candidates/build.py …`; catalogue quotes no number) |
| S4 | Jev Spam Eval (L163) | awesome-typesafe row 6 (reproduce: `uv run spam_noul.py …`, `analyze.py`, `tfidf_baseline.py`; catalogue quotes no number; upstream Ns 19,528 / 8,333 / 1,000 / 500) |

### Unique entries with local mirrors — full rows

| # | Entry (catalogue line) | Repo exists? | Runnable suite stated? | Jev number + N quoted? | Mark |
|---|---|---|---|---|---|
| F1 | Jev Ultrafast (L89: "Zürich → London on Google Flights in ~7s") | YES — mirror `/Users/josh/Developer/jev/jev-ultrafast` @ `452c1ad2dd628008f1d5608f28158d76e49e6cc0` | YES — `uv run pytest` (README:128), `node --check …/app.js` + `snapshot.js` (README:129–130), `scripts/record_flights.py` / `render_demo.py` (README:134); offline guard check without model calls (README:134) | Catalogue: "~7s" (rounded, denominator: one Google-Flights task). Upstream: 7.1 s headline (README:9); recorded completion 7.073 s; 6 alternating runs 3/3 pass, median 9.450 s → 7.092 s (−25%), protocol calls 1,092 → 101; explicitly "three repeats of one task … not a general reliability benchmark" (README:112–120); per-run hashes/boundaries in `docs/performance.md` | clone-candidate |
| F2 | Jev Phishing Bench (L164: "2,000 emails: Jev vs Claude Haiku 4.5 on click-or-not … Haiku wins accuracy here") | YES — mirror `/Users/josh/Developer/jev/jev-phishing-bench` @ `1d56e8c64d029a9554a0874e2ef2901ed196e230` | YES — `uv run prepare_data.py`, `net_floor.py`, `run_jev.py` / `run_llm.py` (+ `--limit 10` smoke, `--pass 2` stability), `analyze.py`, `charts.py` (README:92–102) | Catalogue: N=2,000 emails (denominator stated). Upstream: `results/metrics.json` `n_emails=2000`; Jev (jev-1.13.0) 62.6% [60.5, 64.7] vs Haiku 81.3% [79.5, 82.9] (README:11–13); p50 239 ms vs 687 ms; $0.038 vs $0.462 per 1k; five-signal regression 95.0% vs 93.2% McNemar p=0.063 — not a significant Haiku win (README:44–53) | clone-candidate (bench seats own the numbers; catalogue blurb covers click-or-not only) |
| F3 | jev-agent-failure-benchmark (L165: "Who&When Pro (injected agent failures): Jev vs a strong LLM on who / which step / error category" — no N in blurb) | YES — mirror `/Users/josh/Developer/jev/jev-agent-failure-benchmark` (README read; suite lines below) | YES — `jevbench sample --n 6257`, `estimate` (offline), `run`, `report` (README:62–65); `scripts/reproduce.sh` whole flow (README:70); `pytest -q # offline; no API keys required` (README:99) | Catalogue: NO number. Upstream: N=6,257 text traces, denominator "On all 6,257 text traces" (README:11); Jev Who 73.4 / When 76.4 / What-F1 23.7 / All 31.3 vs GPT-5.4 paper baselines 55.7 / 72.3 / 15.3 / 21.3 (README:16–22); ~$1.28 total, Jev bills input only (README:11–12); comparability caveat — Who/When are constrained-choice for Jev vs free-generate for LLMs, like-for-like axis is What (README:37–39) | clone-candidate |
| F4 | jev-sec-bench (L166: "Blind prompt-injection and vulnerable-code detection benches on public corpora, built on jev-go" — no N in blurb) | YES — mirror `/Users/josh/Developer/jev/jev-sec-bench` (README read; 255 lines) | YES — `go run ./cmd/jev-sec-bench -bench all` (README:17), per-bench variants `-bench injection` / `-bench code -pairs 50` / `-ablation=false` (README:233–235), `go test ./...` (README:236); TUI reads committed JSON (README:18, 193–195) | Catalogue: NO number. Upstream: N=662 labelled injection messages (263 injections) + 200 matched pairs = 400 code samples (README:12–13); injection acc 96.5% @ 0.50, P 96.2 / R 95.1 / F1 95.6 / AUC 0.9927 / ECE 0.0588, wall 22.7 s per 662, p50 325 ms (README:27–40); code pairwise 178/200 = 89.0% (README:89), absolute 71.5% as corpus-noise floor (README:106–114, 162); run 2026-09-16 vs `jev-1.13.0`, raw rows in `results/` (README:21) | clone-candidate |

### Unique entries without local mirrors — catalogue-only

Method for all nine: (1) local-mirror census
`ls -d /Users/josh/Developer/jev/*<slug>* /Users/josh/Developer/jev/upstream/*/*<slug>*`
→ `ABSENT: <slug>` (verbatim, exit 0); (2) no fetch per No-live-calls profile,
so existence is UNVERIFIED, not disproven. Deciding evidence is the catalogue
line itself. None was opened, executed, or cloned.

| # | Entry (catalogue line) | Census | Suite? | Jev number + N quoted? | Mark |
|---|---|---|---|---|---|
| C1 | jev-browser (L90: "Jev decides each click/type on a Playwright snapshot (~300 ms/call)") | ABSENT | unverified — no mirror | Catalogue: ~300 ms/call (denominator: per call). Upstream N: unverified | catalogue-only |
| C2 | typesafe-computer-use (L92: "About $0.0002/step") | ABSENT | unverified | Catalogue: $0.0002/step (denominator: per step). Upstream: unverified | catalogue-only |
| C3 | Mobile Jev (L93: "payment screen in ~21s / 9 actions") | ABSENT | unverified | Catalogue: ~21 s / 9 actions (denominator: one Uber ride task). Upstream: unverified | catalogue-only |
| C4 | jev-audio-beeper (L104: "ffmpeg beeps in ~466 ms") | ABSENT | unverified | Catalogue: ~466 ms (denominator: per beep decision). Upstream: unverified | catalogue-only |
| C5 | jev-eval-agent (L110: "Public eval harness for early Jev tests" — bench-word, no number) | ABSENT | unverified | Catalogue: NO number. Upstream: unverified | catalogue-only |
| C6 | snake-jev (L125: "hundreds of typed direction decisions per run" — marginal count-claim) | ABSENT | unverified | Catalogue: "hundreds" per run (denominator: per run; no exact N). Upstream: unverified | catalogue-only |
| C7 | Little Airways (L132: "Jev judges divert / emergency / who lands first …, ~150 ms") | ABSENT (`jev-little-airways` checked) | unverified | Catalogue: ~150 ms (denominator: per judgment, implied). Upstream: unverified | catalogue-only |
| C8 | PocketJev (L159: "Camera + 3-choice, no text generation, ~1s, no photo saved") | ABSENT | unverified | Catalogue: ~1 s (denominator: per visual decision). Upstream: unverified | catalogue-only |
| C9 | Every article (L205: "Jev Judged Everything I've Written in 0.7 Seconds") | N/A — article, not a repo | N/A — no repo/suite | Catalogue: 0.7 s over a writing corpus (denominator: one corpus; N of pieces unstated in blurb) | catalogue-only |

Skips: none in scope — 17/17 resolved (4 pointers + 4 full + 9 catalogue-only).
Zero Jev calls made (N=0, cost $0); no keyed suite was executed.

## T1–T10 table

| id | verdict | evidence |
|---|---|---|
| T1 | PASS | full SHA ef19300…, date 2026-09-17, CC0, clean status before/after, env recorded above |
| T2 | NA | catalogue profile runs T1+T3 only; tree is 5 prose files, no runner of its own |
| T3 | PASS | 17/17 in-scope entries resolved (4 shared pointers, 4 full mirror rows, 9 catalogue-only with ABSENT census); catalogue blurbs quoted with line numbers |
| T4 | NOT-RUN | catalogue profile; no live calls per assignment. [INFERENCE] no command, no output; cause: assignment sentence "No live calls" plus catalogue T1+T3 profile. Routes tried: n/a (profile forbids). Second route: n/a |
| T5 | NA | floors require live rows; catalogue has no rows of its own |
| T6 | NA | incumbent arm requires live rows; catalogue has no rows of its own |
| T7 | NA | calibration requires binned live verdicts; none exist at catalogue level |
| T8 | NA | stability requires repeated live asks; none performed per profile |
| T9 | NA | not an SDK/client/tool clone |
| T10 | PASS (catalogue) | result class: N/A (catalogue, not a seat — no SELF/FLOOR/INCUMBENT claimed). RULEBOOK tier: n/a. NO-CLAIM line: this receipt claims no Jev accuracy, cost, or latency number; every number above is quoted from the catalogue blurb or the upstream mirror text with its N. Earned-label fields: nothing not-run beyond the profile exclusions above |

## Boundary

- Did not: edit the clone tree, clone or fetch anything, call any Jev/LLM
  endpoint, run any keyed suite, re-audit the 4 shared entries, print any key,
  or write `EVAL.md`.
- Stale-link surface (non-blocking, for the catalogue owner): L158 still points
  at `TheoLeeCJ/openjev`; sibling receipt records the rename to `TheoLeeCJ/SemIf`
  (redirect holds). L112 smart-home demo still names no repo URL ("slated for
  GitHub at release").
- Prior-day census (71 repos, 0 commit pins, 2026-09-22 receipt) was not
  re-derived here; nothing in this run contradicts it. Absence claims cover only
  the 9 C-slugs checked, not the catalogue at large.
- Spend: $0 (no model calls of any kind).

# awesome-typesafe W7.0 receipt — 2026-09-23 (worker W70Catalogue)

Catalogue profile: T1 + T3 over entries, clone candidates. No live Jev calls.
Pin predates all data collection; T4 bars committed at fec3f95
(`docs/demos/upstream-repro/w70-prereg-p5.md`). Live model (unused here): `jev-1.13.0`.

## T1 — Pin and environment

- Repo: `/Users/josh/Developer/jev/awesome-typesafe`, remote
  `https://github.com/AbdelStark/awesome-typesafe` (fetch+push, `origin`)
- SHA: `c2d5cf9d851e445fd50ae51fcae09bca5718e7c7`
- Date/author/subject: `2026-09-18 20:08:08 +0200`, Kyle McLaren, `Add jevcal (#36)`
- License: MIT (`LICENSE`: "MIT License", copyright 2026 Abdelhamid Bakhta)
- `git status --short`: clean (empty) before and after (read-only run; tree untouched)
- Runtime: Python 3.9.6, Darwin 25.5.0 arm64, host `Joshs-Mac-Studio.local`
- `OMP_PROFILE=muse`, `PI_MODEL=` (empty)
- Corroboration (not a T2 run): `python3 scripts/check.py` fresh → exit 0,
  `OK: 94 external links, 53 community entries, and all structural checks passed.`
  Planted defect in `/tmp` copy only (trailing whitespace appended to README):
  `ERROR: README.md:170: trailing whitespace`, exit 1 → suite is able to fail.
  `/tmp` copy removed afterwards. Clone tree never written.

## T3 — Claim inventory (benchmark/measurement entries)

"Quoted with N?" = does the *catalogue entry text* state a Jev number with an N.
"Suite?" = does the upstream repo state a runnable command (verified via URL
fetch or read-only local mirror; nothing cloned by this worker).

| # | Entry (README line) | URL resolves? | Repo exists? | Runnable suite stated? | Jev number + N quoted? | Mark |
|---|---|---|---|---|---|---|
| 1 | jevcal (L120) | YES — `https://github.com/abhixhek/jevcal` fetched (MIT, 10★) | YES | YES — `pytest` (tests/); `jevcal demo` keyless, `jevcal run/check` keyed | NO — by design; entry says "publishes no Jev results of its own", upstream README confirms ("this README contains none, on purpose") | clone-candidate (sibling owns `/Users/josh/Developer/jev/jevcal`) |
| 2 | Janus (L144) | YES — `https://github.com/FirasSX914/Janus` fetched (MIT, tests/ + CI `tests.yml`, `pip install janus-decide`) | YES | YES — `janus measure --dataset …`; raw JSONL + figures committed | Catalogue: NO numeric Jev result (says "two labelled datasets" without N). Upstream states N=500/dataset, 80.2% @ thr 0.67 Banking77, DO NOT ROUTE on WoS | clone-candidate (sibling owns `/Users/josh/Developer/jev/Janus`) |
| 3 | jev-axi (L117) | YES — `https://github.com/shiftynick/jev-axi` fetched (MIT, 19★) | YES | YES — `bench/agent/bench.py` + `bench/eval.ts`, fixtures + `bench/results/baseline.json` committed | Catalogue: NO numeric Jev result ("read fewer files but cost the same", qualitative). Upstream: 390k-line repo, 6 runs/condition, direction not callable | clone-candidate (no local mirror; tool+bench) |
| 4 | Jev Judge vs Dimension Scores (L145) | YES — `https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/` fetched, canonical match | N/A — blog post, not a repo | NO — no repo/suite; experiment CLI described but not linked as runnable code | YES — "5,477 test rows and 34.1M input tokens for $1.43; 0.9076 vs 0.8373 on Japanese NLI; ~25× more hard-benign flags"; verified verbatim on the live post (25,174 Jev calls, $1.43 input-only, JNLI 8,000 train / 2,434 test) | catalogue-only |
| 5 | Jev Rerank Bench (L146) | YES (link present; content verified via local mirror `upstream/anessbelbati/jev-rerank-bench` + `/Users/josh/Developer/jev/jev-rerank-bench`) | YES | YES — `## Reproduce`: `uv run candidates/build.py …` | Catalogue: NO numeric Jev result ("uncertainty intervals, and documented limitations" without numbers) | clone-candidate (mirrors exist) |
| 6 | Jev Spam Eval (L147) | YES (verified via local mirror `upstream/bitnovus/jev-spam-eval` + `/Users/josh/Developer/jev/jev-spam-eval`) | YES | YES — `## Reproduce`: `uv run spam_noul.py …`, `uv run analyze.py`, `uv run tfidf_baseline.py` | Catalogue: NO numeric Jev result ("explicit post-hoc-tuning caveats" without numbers). Upstream README cites 19,528 / 8,333 / 1,000 / 500 email Ns | clone-candidate (mirrors exist) |
| 7 | OpenJev (L148) | YES with rename flag — `https://github.com/TheoLeeCJ/openjev` resolves via redirect to `TheoLeeCJ/SemIf` ("SemIf (formerly OpenJev)", MIT, 3885★) | YES | YES — `benchmarks/*.py`, `docs/REPRODUCE.md`, committed results/ | Catalogue: NO Jev number ("reproduces the interface pattern, not Jev's undisclosed model or training"). Upstream quotes open-model Ns (144/777/102/256 rows) and reads Jev's 0.883 only from TypeSafe's published records ("we did not run a live Jev endpoint") | clone-candidate (no local mirror; recommend catalogue link update to SemIf) |
| 8 | TypeSafe AI Benchmark (L149) | YES (verified via local mirror `upstream/iammrduncan/typesafe-ai-benchmark` + `/Users/josh/Developer/jev/typesafe-ai-benchmark`) | YES | YES — `docs/benchmarks/README.md`: `npm ci`, `npm run build`, `npm run start:demos:live` (keyed; charges real) | Catalogue: NO numeric Jev result ("methodology, and task-specific limitations" without numbers) | clone-candidate (mirrors exist; prereg T4 bar already committed) |

Claim-level spot checks (catalogue's own Jev claims, with deciding file:line):
- README L10 "Jev returns typed, probabilistic decisions instead of generated text" — demonstrated (matches upstream docs/primitives).
- L120 "thresholds fitted on fewer than about 100 labeled rows should not be trusted" + "publishes no Jev results" — demonstrated (upstream jevcal README states both).
- L144 "no routing parameter transferred between the two datasets" — demonstrated (upstream Janus README: threshold 0.67→0.37, sign and payoff changed).
- L145 numbers — demonstrated (verified verbatim on the live post, see row 4).
- L117 jev-axi benchmark gloss — demonstrated (upstream: "less than run-to-run noise … Six runs per condition cannot call a direction").
- L148 OpenJev gloss — demonstrated (upstream: interface pattern only, no undisclosed model/training).
- L146/L149 suite-content glosses — partial (reproduce commands verified; "uncertainty intervals" / "raw exports" contents not opened).

Skips: none — all 8 entries assessed. No entry required a Jev call; zero Jev calls made
(N=0, cost $0). Non-benchmark entries (SDKs, tools, demos, showcases) are catalogue-only
by profile and were counted (53 community entries) but not individually inventoried.

## T1–T10 table

| id | verdict | evidence |
|---|---|---|
| T1 | PASS | full SHA c2d5cf9, date 2026-09-18, MIT, clean status, env recorded above |
| T2 | NA | catalogue profile runs T1+T3 only (PLAN-DEEP-KIT L427–428); corroborating fresh `check.py` OK (94 links/53 entries) + /tmp RED proof noted under T1 |
| T3 | PASS | 8/8 benchmark-claiming entries resolved or marked (7 clone-candidates, 1 catalogue-only); ≥5 catalogue Jev claims checked with file:line |
| T4 | NOT-RUN | catalogue profile; no live calls per prereg. [INFERENCE] no command, no output; cause: prereg bars apply to seat/benchmark clones, catalogues excluded (w70-prereg-p5.md L11). Routes tried: n/a (profile forbids). Second route: n/a |
| T5 | NA | floors require live rows; catalogue has no rows of its own |
| T6 | NA | incumbent arm requires live rows; catalogue has no rows of its own |
| T7 | NA | calibration requires binned live verdicts; none exist at catalogue level |
| T8 | NA | stability requires repeated live asks; none performed per profile |
| T9 | NA | not an SDK/client/tool clone |
| T10 | PASS (catalogue) | result class: N/A (catalogue, not a seat — no SELF/FLOOR/INCUMBENT claimed). RULEBOOK tier: n/a. NO-CLAIM line: this receipt claims no Jev accuracy, cost, or latency number; all numbers above are quoted from the catalogue or upstream texts with their Ns. Earned-label fields: nothing not-run beyond the profile exclusions above |

## Boundary

- Did not: clone anything, call any Jev/LLM endpoint, edit the clone tree, or re-verify
  sibling-owned clone contents beyond read-only suite-command/N presence.
- Stale-link flag (non-blocking): entry L148 still points at `TheoLeeCJ/openjev`;
  upstream renamed to `TheoLeeCJ/SemIf` (redirect holds today). Suggest updating the link.
- Catalogue review date L14 (2026-09-17) predates pin commit (2026-09-18, jevcal addition);
  no conflict — pin commit only added the jevcal row.

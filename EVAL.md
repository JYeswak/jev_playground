# Jev workspace eval — 2026-09-17

Six repos checked out below, each at the pinned SHA it was tested at.
Key lives outside this tree (`/tmp/.tskey`, mode 600, env-only) — never committed here.

## Live API baseline (all repos)

- Endpoint `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest` → `jev-1.13.0`.
- Smoke: noul "Is this a smoke test?" → 0.81, HTTP 200, ~1.2 s.

## 1. fast-jev-compaction @ 6e1da50 (tamaratran, TS, MIT)

Continuous compaction: Jev keep/drop per tool call+result, texts verbatim, no summaries.

- `npm install` clean (0 runtime deps) · `typecheck` (lib+hooks) green · `vitest` **29/29**
  · `build` emits dist · `claude plugin validate` **passes** (1 trivial warning: no author field).
- Live `npm run demo` (real Jev): 7 calls scored, all dropped (low keep probs),
  21→7 msgs, 87.1% chars saved in 843 ms; texts verbatim.
- Own probe (`probes/fast-jev-probe.mts`, fake Jev): 8/8 — verbatim preservation,
  order, truncation-to-head+note on drop, unknown answer keys default keep (fail-safe).
- Note: Jev question keys are `call_tN`/`result_tN`, not `tool_use_id` — README could say so.
- Not run: SwiftUI demo app (needs Xcode build + screen eyes, no API).

## 2. jev-ultrafast @ 452c1ad (browser-use, Python, MIT)

Browser agent: one Jev request picks operation + element; small LLM only for TYPE_TEXT.

- `uv sync` clean · `ruff` clean · `pytest` **31/31** (behavior-level: staleness guards,
  text-reuse rules, trip verification) · `node --check` both JS files · `uv build` wheels fine.
- `scripts/check_guards.py`: **21/21 PASS vs real headless Chrome**, no model calls.
  Requires Chrome listening with remote debugging first (`--remote-debugging-port=9222`);
  the harness daemon auto-starts after that.
- Not run (need TEXT_MODEL_API_KEY + live session): `examples/*`, `smoke.py`, demo flights.

## 3. awesome-jev-by-typesafe @ d57f5ce (Anil-matcha, Python, MIT)

Use-case/pattern collection + runnable examples.

- `pytest tests/` **11/11** (pure decision-policy logic, stdlib only).
- Live Python quickstart (`typesafe-sdk`): intent refund @ 1.0, urgency 0.96,
  frustration 0.96 — sensible. Live TS quickstart (`@typesafe-ai/sdk`): identical
  values — SDK parity across languages.

## 4. jev-review @ 57690af (NiazMorshed2007, TS, MIT)

Local-first MCP quality review: `jev_review` over stdio, direct to Jev API.

- `npm run validate` green: `tsc --noEmit` + **13 node --test** + esbuild bundle.
- MCP handshake: `tools/list` exposes `jev_review` with schema, rc=0.
- LIVE `tools/call` (login-validation diff): scored dimensions
  (complexity 7, readability 7.3, reliability 6.4 + confidences) in ~1.5 s;
  insufficient-context dimensions honestly `applicable: false`. Exactly the documented contract.

## 5. jev-mcp @ 6ec5efc (jkudish, TS, MIT)

Three MCP judgment tools (verify / screen / find).

- Unit: **9/9**, no key. Live `npm run test:e2e`: **4/4** (verify, screen incl.
  injection flag, find incl. absence check), ~0.6–0.7 s per live call.

## 6. awesome-jev @ ef19300 (AnotiaWang, CC0)

Markdown list only — nothing to build. Sampled 15/15 GitHub project links: HTTP 200.

## 7. skillranker @ 3fe85c4 (Dicklesworthstone, Rust 2024, MIT + OpenAI/Anthropic rider)

Jev-as-judge skill router (`sr`): live session context → ranked skills for the next
step. This pass mined ONLY its AGENTS.md (671 lines, pinned — repo still moving).
Four rules adopted into our AGENTS.md (commit `24b0b33`): provider-output authority,
no guessed-equivalent integrations, infra-failure-is-not-pass, Agent Mail
coordination paragraph. Checked and HELD (not added): peer-work NEVER-disturb rule
(our tail note), landing checklist, exit-code envelope, prose-is-not-proof.
Boundary: no source read, nothing built, no live calls; full eval pass still open.


- secrets.zeststream.ai speaks API v3 only (v1/v2/v4 → 404; v3 → 401 unauthenticated).
  brew's 0.43.111 calls `/api/v4/secrets` → hard 404. Bisected the cutover by testing
  releases against the live server: …≤0.43.98 speaks v3 (WORKS), 0.43.99+ speaks v4
  (404). Newest-working = v0.43.98.
- `~/.local/bin/infisical` was already v0.43.84 (v3-speaking, works) but shadowed by
  brew's 0.43.111 earlier on PATH. Resolution: `brew unpin` + `brew uninstall`
  (the formula was pinned) → `infisical` now resolves to 0.43.84 and `secrets get`
  works. Reinstalling brew's formula later re-breaks this; re-pin or re-uninstall then.
- Secret hygiene: TYPESAFE_API_KEY lives only in Infisical + `/tmp/.tskey` (mode 600,
  env-injected per command, never in args/files/commits). Two rotations observed
  mid-session; every live result above was HTTP 200 at measurement time.
  Personal-vs-shared override caution: `secrets get` (personal-override default) and
  the raw v3 endpoint briefly returned different values — verify live (200) when it
  matters, don't assume one read path.
## Boundary

Live coverage is whatever each repo's own suite/mode exercises, plus the v1
calibration audit. No adversarial corpora yet — framed as a next audit in
`foundation/CALIBRATION.md`.

**A/B-vs-LLM: three runs exist, arm B is NONDETERMINISTIC, and no relative verdict is
established.** This line previously read "No A/B-vs-LLM runs yet", which was true when written and
false by 2026-09-18. All three receipts are in `compaction/runs/`:

| Receipt | fixture bytes / sha | armA Jev-prune | armB LLM summary | verdict status |
|---|---|---:|---:|---|
| `ab-20260917.json` | 214,993 · `20fa1ea0…` | **1/3** | 3/3 | **withheld (n=1)** |
| `ab-rerun-20260918.json` | 82,214 · `2346451d…` | **1/3** | 1/3 | **withheld (n=1)** |
| `ab-sample3-20260918.json` | 82,214 · `2346451d…` (**identical to row 2**) | **1/3** | 3/3 | **withheld (n=1)** |

Rows 2 and 3 share a byte-identical fixture and disagree by two points on arm B. That settles the
attribution, and it was not what the first two rows suggested. The fixture *had* changed between
rows 1 and 2 — `a6e1353` removed 76 `thinkingSignature` blobs, ~133 KB of base64, shrinking the
corpus 62% — so the corpus was the obvious suspect. **Row 3 exonerates it.** arm B is generated by
a live `runOmp` summarization call with no temperature pin, and it scores 3, 1, 3 on the same
question set.

What is stable and what is not, stated separately because only one of them is usable:

- **Stable, 3 for 3 across 2 corpora: armA (Jev-prune) scores 1/3.** Pruning drops answer-bearing
  facts, robustly. This is the lane's one supported compaction finding, and it is the premise the
  fact-ledger demo rests on.
- **Unstable: armB scores 3, 1, 3 on identical input.** So "summarizing beats pruning" was a
  coin flip reported as a result. The original relative verdict was n=1 on a stochastic arm and is now retracted.

Boundary on the boundary: no run licenses a claim about Jev's pruning *relative* to
summarization, and adding samples of a 2-point-variance arm will not fix that cheaply — it needs a
pinned generator or a distribution, not another single run. Any demo threshold must therefore be
an **absolute** score on the three questions, never "beat arm B": a stochastic baseline is not a
threshold. Recorded as `NEGATIVE_EVIDENCE.md` R11.

## Foundation (added this session)

- 13 more checkouts: system-one-adapter-python 0bb819b, jev-rerank-bench cd9a35b,
  jev-spam-eval 76ef183, jev-phishing-bench 1d56e8c, jev-sec-bench fdb16b9,
  typesafe-ai-benchmark e94fcda, foreman 2c43982, bicameral 3bea244,
  jev-router 86660a0, jev-codex-router 8292b51, commit-miner 977617e,
  s1-rs b916897, jev-agent-failure-benchmark 4d46af7.
- `foundation/`: JSON schemas (fixture/report), 80-row fixture, stdlib runner,
  `CALIBRATION.md`. First audit: **ECE 0.061, Brier 0.020**, Noul 58/60, Choice
  19/20, t≥0.75 → accuracy 1.0 at ≥90% coverage. Receipt
  `foundation/runs/20260917T224444Z.json`. Rust-portable by construction
  (schemas + pure metric fns + errors-as-data + named bounds).
- `foundation/gates.sh` + `gates.d/` (10-fixture-integrity, 20-receipt-freshness,
  30-no-secrets): aggregate green; every stage proves its RED arm on demand
  (truncated fixture, empty runs dir, planted key). Caught live during build: a
  selftest that tripped on its own source literal — fixed to assemble the plant
  at runtime and assert the RED names the plant file.
  Stage 40 (`40-omp-compact-replay.sh`, added with `compaction/` below): the omp
  adapter typechecks, 5 mapping tests pass, inverted-property selftest proves RED.
- `compaction/` (added this session): omp-harness replay for fast-jev-compaction.
  `src/omp-adapter.ts` maps `omp -p --mode json` streams to `Message[]`
  (message_end only; thinking dropped+counted; results call-adjacent — herding
  them onto a later user turn pinned 11/11 calls through their results and Jev
  was never consulted). `src/replay.ts` asserts the true contract (texts
  verbatim subsequence, no text loss, no invented ids, pruned messages carried
  no text, candidates imply requests). Live replay, 11-call session, real Jev:
  **5 dropped, 13→8 messages, 2333→1292 chars (45%), zero text loss** — receipt
  `compaction/runs/replay-big-20260917.json`. Design facts the replay forced
  out of the library: Jev never sees result content (state carries ok/error +
  char count only — relevance judgment, not content review); message pruning is
  intended (empties dropped); `ToolUse.text` is a Claude-attached mirror the
  state builder does not render, so the adapter correctly omits it.

## Lane contract + primary-source mirror (added this session)

- `AGENTS.md` (66 KB, 31 §§ **as authored**; **79,901 B / 33 §§ / 1,343 lines at `6b721c9`** after
  siblings added the skillranker rules — re-derive with `wc -c AGENTS.md`, never cite the authored
  size as current): authored against the mirror-derived canonical shape.
  `fh agents --repo .` → DISCIPLINE 14 NAMED / 1 UNNAMED / **2 ABSENT**, REPO_SPECIFIC
  2/3/**2**, TOOL_ONBOARDING 7/2/**31**; `nomenclature_state=VALID`; 1145 lines vs corpus
  median 839, `exceeds_corpus_max=false`. Skeleton `content_id=095decf2…`,
  `source_rev=bb59539…` (64 sections, 117/221 mirror dirs). Every remaining ABSENT row is
  argued in `.fh-agents.toml` (Cargo-only, or a section deliberately compressed).
- `scripts/sync-docs.sh` — vendors the primary sources, fail-closed, never destructive
  (fetch-only on existing clones; a SHA move is reported, never performed). Ran clean:
  **111/111 doc pages**, `--check` → `CHECK PASS 114 mirrored files`. Mirrored
  `docs-mirror/typesafe/` (llms.txt 16.7 KB, llms-full.txt 835 KB, sitemap 111 locs),
  `docs-mirror/ripwire/` (CLI-HELP 200-line summary + CLI-HELP-ALL 1826 lines), and
  pinned `upstream/typesafe-ai/{typesafe-sdk-python@420ef4f, typesafe-sdk-js@66880cc,
  system-one-adapter-python@0bb819b, skills@65a39f3}` + a 10-row org inventory.
- **Finding from the manifest, first run:** the local `~/Developer/ripwire` checkout is
  `6488f6f4`, **1502 commits behind** upstream `f45087a7`, while the installed binary is
  `0.4.0 built_from=e663ca8f8` — three different revisions. Not moved; recorded.
- omp surfaces measured live, not quoted: `omp/18.2.4`, 40 subcommands;
  `negotiate_protocol(v2)` → success and `get_state` → `model.id=claude-opus-5`,
  `contextWindow=1000000` via `omp --mode=rpc --max-time=20`. Pane-profile trap confirmed in
  this very session: `%71` titled `jev__omp-claude_1` runs `omp --profile=codex`.
- Boundary (**this pass only** — a sibling pane's `131679e [live] omp compaction replay` DID make
  live Jev calls, so the lane is no longer spend-free): no Jev API call was made by *this* pass.
  The omp integration seams I documented are at **L0** — designed and cited, nothing wired.
  `probes/fast-jev-probe.mts` re-run offline (fake Jev, no key): **8/8**, 0.91 reduction ratio.

## ripwire upgrade — single binary, latest (2026-09-17)

- Census first: **exactly one** installed binary existed (`~/.local/bin/ripwire`, 41,964,568 B,
  Sep 6) — no brew formula, nothing in `/opt/homebrew/bin` or `/usr/local/bin`, nothing in
  `~/.cargo/bin`, no stray executable named `ripwire` anywhere under `$HOME` (maxdepth 4).
- `~/Developer/ripwire`: clean tree, no stashes, one worktree, `main` behind 1502.
  `git pull --ff-only origin main` → `f45087a7` (`v0.6.1-427-gf45087a7`), behind 0.
- **Trap avoided:** `install.sh` prefers `brew --prefix`, so a bare run would have installed a
  SECOND binary at `/opt/homebrew/bin/ripwire`. Pinned with
  `RIPWIRE_INSTALL_PREFIX="$HOME/.local"`. Build+install 106.9 s (Release, LTO, `RIPWIRE_NATIVE=ON`).
- After: `which -a ripwire` → one line. `ripwire --version` →
  `0.6.1 (Release, AppleClang 21.0.0.21000101, emit=std::print, built_from=f45087a77)`, matching
  repo HEAD. Binary, checkout, and vendored docs now agree at one revision (was three).
- Skill store: activation re-linked 16 `ripwire-*` skills as **symlinks** into
  `~/.local/share/ripwire/skills/`, so the store tracks the installed build with no copies.
  `skill-topology-gate.sh` → `PASS: 8 root(s) converged, 0 absent, 0 dangling`.
  `ripwire-opt-remarks` is **deliberately pruned** — its frontmatter is `audience: contributor`
  and the activator gates it behind `--contributor` (documented in the upstream activator at
  `share/ripwire/skills/install.sh:314-320`). Expected, not a regression.
- **No hook was wired.** `~/.claude/settings.json` mtime unchanged (2026-09-16); the three
  `ripwire` greps that looked like hook registrations are `*-skill-tripwire.sh` — "tripwire"
  contains "ripwire". False positive, retracted.
- Surface change to carry: `--help` is now a 200-line summary and the full manual moved to
  `--help=all` (1826 lines); `--doctor` requires a `<dir>` (`ripwire . --doctor`) — a bare
  `ripwire --doctor` prints the usage banner. `scripts/sync-docs.sh` now captures both help
  forms; re-run → `ripwire @ f45087a7 (current)`, 15 design docs, VERSION/CLI-HELP refreshed.
- Boundary: only the second binary on disk is `~/Developer/ripwire/build-install/ripwire`, the
  installer's own Release build tree (gitignored, kept so re-installs are incremental). Not on
  PATH, not installed. `build/` holds no binary.


## Lane became a git repo + measured-gap closure (2026-09-17)

Joshua authorized `git init` after nine `stamp-check` items were failing fail-closed on
"not a git repository". **`stamp-check --repo .`: 32 PASS / 20 FAIL / 2 PARTIAL → 41 PASS / 8 FAIL
/ 2 PARTIAL** (of 64, report-only). Five commits, `e70b1dc`…`625828a` + a sibling's `131679e`.

- **Allowlist `.gitignore`.** Ignores `/*`, un-ignores what we author. A new vendored clone needs
  no change; ~20 nested repos never become accidental gitlinks. It fired twice as designed —
  `GATES.md` and `githooks/` were invisible until explicitly allowed.
- **Provenance committed, bytes not.** `docs-mirror/MANIFEST.tsv` + `upstream/MANIFEST.tsv` are
  tracked; 5 MB of third-party docs and the nested clones are not. Rejection argued in
  `NEGATIVE_EVIDENCE.md` R5, reproducible via `sync-docs.sh --check`.
- **`dcg` denied `git add -A`** (`zeststream.shared_worktree:git-add-whole-tree`) on the first
  attempt — correct in a worktree three agents share. Everything staged by explicit path since.
- **The commit-msg hook refused my first commit** for having no verification level. Now in-tree
  at `githooks/` (byte-identical to `.git/hooks`, sha `420af8f6d4af` / `c325a40aee77`) and wired
  via an **absolute** `core.hooksPath` — a relative one resolves per-worktree, so every worker
  lane would commit unhooked.
- New artifacts, each carrying real content rather than satisfying a checker: `NEGATIVE_EVIDENCE.md`
  (8 rows with retry conditions, two of them retractions of my own instrument errors), `GATES.md`
  (every gate, its edge, its RED arm, plus `## Oracle` and `## Fail-closed rules`), `TESTS.md`
  (three surfaces kept separate; both tracked test files enumerated by path; coverage % refused
  with an argument), AGENTS.md `§0`/`§4` + the JEFF-BEAD-STANDARD M5/M6 addenda.
- Gate evidence at `625828a`: `foundation/gates.sh` **and** `--selftest` ALL GREEN (every stage
  proves its RED arm); hook selftest 4 bad refused / 4 good passed; `gitleaks protect --staged`
  no leaks; `sync-docs.sh --check` CHECK PASS 114.
- **Still failing, each classified, none hidden:** `i-staged-deletion-hook` (HUMAN — installing a
  new pre-commit hook is gated by `skill://hook-certification`, not hand-rolled);
  `p5-autofix` + `rc0-declared-path` + `p10-commit-sweep` (FALSE_POSITIVE — all three fire on
  *vendored* clones: 969 upstream code files, `s1-rs`'s bin crate, and a literal `TODO` inside a
  recorded omp transcript fixture); `p6-cross-lineage` / `p7-worksheet` / `p8-session-feedback`
  (NOT ADOPTED — persona reviews and `.flywheel/worksheets/`; `EVAL.md` + `NEGATIVE_EVIDENCE.md`
  already are this lane's session record); `p12-loop-integrity` (N/A — no tick-loop driver);
  `p18-end-of-shift` (CONDITIONAL — goes green on a clean tree at session end);
  `d-gate-wiring` PARTIAL (artifact present; the checker's basename extractor does not see the
  four `.sh` names the block lists — instrument disagreement, recorded not papered over).

## jev-route-backtest — offline counterfactual backtest [test]

Receipt: `demos/routing-backtest/runs/backtest-real-excerpt.json`.
Inputs: shipped `demos/routing-backtest/fixtures/real-excerpt-t1-t6.jsonl` fixture.
Denominator: 1 session, 6 turns, 6 classifiable, 0 skipped. Six explicit turn_start→turn_end pairs; model muse-spark-1.3-contributor.
Policy: cheap-1 is a deterministic text-only/token-budget counterfactual (one tool call allowed, prompt ≤20,000, completion ≤2,000); actual spend comes from recorded usage.cost.total.
Result: actual spend $0.011106414; counterfactual spend $0.012932900; estimated savings -$0.001826486; 5 turns routed to the cheap scenario. No verdict field.
Verification: 12 offline tests pass, including empty-class/floor/missing-price RED arms; install.sh runs the exact shipped-fixture command and test suite; foundation gates ALL GREEN.
Boundary: this prices a deterministic counterfactual over a six-turn fixture. It does not prove a cheap model would preserve task quality, that the incumbent model is an oracle, or that live routing would work. No live Jev calls were made.

---

# 2026-09-18 — fourteen upstream repos, pinned

Added after Joshua asked why `AGENTS.md` §4 was not being met. Seventeen upstream receipts had been
written that day and **not one carried a repo@sha**, so every figure in them was unreproducible the
moment a clone moved. These are the SHAs those receipts were measured at.

| # | Repo @ sha | Ran | Result | Receipt |
|---|---|---|---|---|
| 7 | `jev-spam-eval` @ 76ef183 | `tfidf_baseline.py`, `ood_test.py` | zero-label 98.57% vs TF-IDF 99.41% in-dist; 91.3% vs 70.3% OOD | [lingspam](docs/demos/upstream-repro/lingspam-20260918.md) |
| 8 | `jev-rerank-bench` @ cd9a35b | `eval.py`, `nevir_eval.py` | 0.692 vs 0.691 (p=.910); fresh nevir +4.2pt (p=.002); 2 scripts crash | [report](docs/upstream/jev-rerank-bench-missing-docs-file-reads-as-empty.md) |
| 9 | `jev-phishing-bench` @ 1d56e8c | `net_floor.py` keyless | floor reproduces exactly: 0.9165 / 0.8350 / 0.0020 | [phishing](docs/demos/upstream-repro/phishing-20260918.md) |
| 10 | `jev-benchmark` @ daf02b3 | `analyze.py` on committed results | 91.7%, ECE 0.0505; **zero discordant pairs, 60/60 identical** | [pairing](docs/demos/upstream-repro/jev-benchmark-pairing-20260918.md) |
| 11 | `jev-mcp` @ 6ec5efc | `npm test`; e2e via `infisical run` | 9/9 unit, **4/4 live**; `jev_verify` / `jev_screen` / `jev_find` | [mcp](docs/demos/upstream-repro/jev-mcp-20260918.md) |
| 12 | `jev-review` @ 57690af | `npm test` | 13/13, **zero skipped**; ships `applicable: false` | [review](docs/demos/upstream-repro/jev-review-20260918.md) |
| 13 | `s1-rs` @ b916897 | both examples, linux/amd64 container | typed decisions offline; `RCH-E327` was a platform mismatch | [s1-rs](docs/demos/upstream-repro/s1-rs-20260918.md) |
| 14 | `foreman` @ 2c43982 | `pytest` | 57/58; **no queue concept** — idle-with-work reads as finished | [foreman](docs/demos/upstream-repro/foreman-20260918.md) |
| 15 | `bicameral` @ 3bea244 | `vitest` (pane 3) | 41 pass; pluggable judgment; degrades to patterns not passthrough | [bicameral](docs/demos/upstream-repro/bicameral-20260918.md) |
| 16 | `jev-sec-bench` @ fdb16b9 | `go vet`, `go build`, `-shot` | injection 96.5%, AUC 0.9927; **recall 74.9% bare vs 95.1% +context** | [sec-bench](docs/demos/upstream-repro/jev-sec-bench-20260918.md) |
| 17 | `jev-agent-failure-benchmark` @ 4d46af7 | `pytest` + pinned 73 MB dataset | 20/20 with data, 18/20 without — **`test_leakage` is one that skips** | [agent-failure](docs/demos/upstream-repro/agent-failure-benchmark-20260918.md) |
| 18 | `commit-miner` @ 977617e | on this repo's own 130 commits (pane 3) | reads bodies over prefixes; our verification levels never contradicted | [miner](docs/demos/upstream-repro/commit-miner-20260918.md) |
| 19 | `typesafe-ai-benchmark` @ e94fcda | documented examples (pane 3) | 7/7 offline; docs omit an install step, reported | [examples](docs/demos/upstream-repro/benchmark-examples-20260918.md) |
| 20 | `pi-subagents` @ f4918e80 | `npm test` | **3263 pass / 23 fail / 23 cancelled / 12 skipped** | this row |

`simple-jev` (featherless-ai) was exercised through its **public demo API**, not a clone, so it has
no SHA here: an open-model classifier returned `derived_rollup` at 0.989 on this lane's hardest
citation question, keyless, in 1.7 s
([receipt](docs/demos/upstream-repro/simple-jev-20260918.md)).

**Lane and model version for every live figure above:** `api.typesafe.ai`, `jev-latest` resolving to
`jev-1.13.0`, 2026-09-18. Offline figures are model-independent and read from each repo's committed
results. `pi-subagents` and `jev-sec-bench` involved no Jev call at all.

**NOT DONE against §4**, stated rather than implied: none of these is an omp seam firing in a real
session; `pi-subagents`' 23 failures are unTRIAGED and no upstream report was filed for them; and the
`evidence-auditor` agent — the one that checks whether claims are supported by their sources — is
installed in the clone and **still has not been pointed at a single claim of ours**.


## omp seam — live, 2026-09-18

`compaction/src/omp-binding.ts` driven end to end: a real omp transcript
(`fixtures/omp-session-big-20260917.jsonl`, 179 events → 13 messages) compacted **13 → 8 in
1,282 ms** by one live call to `api.typesafe.ai`, `jev-latest` → `jev-1.13.0`, key supplied through
`infisical run` and absent from the tree.

Rung reached: **L2+**, not L3. The success, outage and malformed-envelope paths are all exercised,
the last two by committed tests; but **omp itself has never loaded the binding**, so the
"fires in a real session" half of §4 remains open and the install is gated to a human.
Receipt: [`docs/demos/omp-seam-live-20260918.md`](docs/demos/omp-seam-live-20260918.md).

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

Rung reached: **L3-minus** after install, 2026-09-18. The success, outage and malformed-envelope paths are all exercised,
the last two by committed tests; and `.omp/hooks/pre/jev-compact.ts` now **loads in a real omp session** (verified keyless and keyed
via separate `omp -p` runs). What remains open is the last step: no real `session_before_compact`
event has fired it yet.
Receipt: [`docs/demos/omp-seam-live-20260918.md`](docs/demos/omp-seam-live-20260918.md).
---

## jev-compact — skill + anywhere-installer, honest yield (2026-09-19, pane 3)

Hook live here (`.omp/hooks/pre/jev-compact.ts`, keyed sessions only) plus skill
(`.omp/skills/jev-compact/SKILL.md`) and installer (`compaction/install-jev-compact.sh`).
Lane: offline throughout this pass; the one cited live figure (13 → 8, 1,282 ms, `jev-1.13.0`)
is unchanged from `docs/demos/omp-seam-live-20260918.md`.

- **Seam correction:** the success path returned `{compaction: {messages}}`; the runtime consumes
  `{summary, firstKeptEntryId, tokensBefore, ...}` with no message channel, so that return would
  have arrived malformed. Now `would-compact` is logged and the hook yields. See
  NEGATIVE_EVIDENCE R21.
- **Tests:** `compaction/`: 32/32 green (`npx tsc --noEmit`,
  `node --import tsx --test test/*.test.ts`), including a real-fixture would-compact arm and
  fromEnv keyless/keyed registration arms.
- **Installer proven on scratch targets:** install PASS (files + ESM dep resolution + receipt
  pinning dep SHA `6e1da50`); `--check` fails closed (exit 1) on an empty dir; deployed lib and
  entry smoke-load with keyless registration a no-op. Its own probes found and fixed two defects:
  a CJS `require.resolve` check against an ESM-only package, and a missing `"type": "module"`
  scope over the deployed lib.
- **Not proven:** firing inside a target repo (only a post-`/compact` decision-log line proves
  that); L4 unreachable on this seam by construction.
- Boundary: zero live Jev calls in this pass; no production compact ever returned a pruning.
---

## jev-fqo — R21 contested and settled: mechanism conceded, conclusion narrowed (2026-09-19, pane 3)

- Conductor's counter-claim verified against the runtime: summary + firstKeptEntryId IS the
  compaction channel (`dist/cli.js` fromHook sites; `CompactionResult`, `compaction.d.ts:21-31`).
  A structurally valid return is constructible — R21's "no channel" phrasing was too broad.
- Settlement: REFUSE L4-as-Jev-pruning; DEFER L4-as-boundary. No value-additive valid return
  exists from the hook's inputs: messages carry no entry UUID (no message→entry mapping without
  guessing; `branchEntries` is branch lineage), and Jev judges but does not summarize (reusing
  `previousSummary` is stale; decision-lines-as-summary degrades continuation).
- Receipt: `docs/demos/omp-seam-fqo-20260919.md`. R21 amended, not rewritten.
- Boundary: zero live calls; no session touched. Lane: offline.
---

## jev-fqo amendment — mapping argument withdrawn, summarizer argument stands (2026-09-19, pane 3)

- Conductor's rebuttal verified: `SessionMessageEntry{type:'message', message}` exists and the
  preparation builder keeps entries/messages in positional parallel arrays, so a message→entry-UUID
  join is constructible — alignment untested by either of us (mutual NO-CLAIM), but not a missing
  channel. Reason 1 withdrawn.
- DEFER now rests on Reason 2 alone (conceded decisive): `summary` is required prose; Jev returns
  judgments. Receipt amended: `docs/demos/omp-seam-fqo-20260919.md`.
---

## skillranker @3fe85c4 — built, ran, README ahead of code (2026-09-19, pane 3)

- RCH build finished but E327 (Linux ELF, unexecutable here); ran via Docker,
  repo read-only. Only `doctor` is implemented (`src/cli.rs:14`;
  `src/adapter.rs:505-512` gates the rest behind P2-P6 phases).
- `doctor --config --json` PASS (20 built-in settings, network off, shadow mode);
  `demo`/`capabilities`/`roster`/`rank` return `unavailable/invalid-usage` — absent,
  not failed. `cargo test` and keyed runs NO-CLAIM.
- Receipt: `docs/demos/upstream-repro/skillranker-20260919.md`. Clone untouched.
---

## jev-4uy — phi below 0.5 did not pay (2026-09-19, pane 3, offline)

- New pair: sec-bench injection ctx/noctx, n=662, texts verified aligned, phi 0.343
  [0.213,0.469], gain -0.006 [-0.020,+0.006], AVERAGE_DID_NOT_PAY; strata agree
  (phish-only 0.394/-0.046, benign-only 0.443/0.0). Low phi did not imply pay —
  accuracy gap (0.965 vs 0.897) dominates; the 0.5 rule needs a gap term
  (hypothesis, not claim).
- Outcome (b): no second pair — phishing/rerank/agent-failure/iammrduncan/router
  results carry aggregates, single judgments, or no truth; themsquared absent.
- Receipt: `docs/demos/phi-second-pair-20260919.md`. Zero live calls.
---

## jev-0bp — upstream main does not compile on macOS (2026-09-19, pane 3, BLOCKED)

- Clean export of origin/main@4ed4c9b to /tmp/sr-main (clone untouched at 3fe85c4).
  RCH fleet refuses all builds (critical_pressure=4, local fallback disabled), so
  native build via pristine `cargo-rch-real.bin` + pinned nightly rustc + isolated
  target dir (shared cache was cross-toolchain poisoned, E0514).
- BLOCKED with file:line: `src/cache/coordination.rs:574` uses
  `crate::storage::...` unconditionally while `src/lib.rs:26` gates
  `pub mod storage` behind `#[cfg(target_os = "linux")]` — E0433 on macOS.
  Upstream defect, never patch; report-or-wait is the only move. Conductor's stable
  toolchain tip (1.95.0) does not apply: this is a cfg bug, not a version skew.
- Boundary: deps compiled (117s of real work); lib failed. No binary, no arms run.

## jev-4vz — hook sweep: zero silent-passers, every branch empirically fired (2026-09-19, pane 3)

- Hook -> behavior-on-missing-checker (scratch copies, real removals, never live):
  `commit-msg` impl missing -> exit 1 REFUSE; lane-1 impl missing -> exit 1
  STAGED_DELETION_REFUSED; lane-2 autofix missing -> exit 1 AUTOFIX_REFUSED;
  lane-2 missing + JEV_ALLOW_MISSING_AUTOFIX=1 -> exit 0 with named SKIPPED line.
- `.git/hooks/commit-msg` vs `githooks/commit-msg`: 4-line diff is message text
  only (FOUNDRY_DIR default); both fail closed. No live divergence.
- Impls are self-contained bash+git (no external checker binaries to go missing).
  Foundry's own hooks NOT exercised (different repo; noted, not edited).
- Fixes: none needed. NO-CLAIM: green-path (all-present) behavior covered by daily
  use + gates, not re-proven here.
---

## jev-d92 — pair hunt exhausted: 22 of 22 searched, no second pair (2026-09-19, pane 3)

- Method: all results/ dirs + `probability` grep over committed data + per-clone
  survey. Only paired item-level scores with truth: spam-eval (excluded, same
  project) and sec-bench (used). All else: aggregates, single scorers, n<=2
  cassettes, latency logs, or no data. Receipt with full table:
  `docs/demos/phi-clone-sweep-20260919.md`. Feeding phi further needs keyed runs,
  the absent themsquared clone, or new live calls. Zero live calls.

## fresh-clone gates + integrations doc (2026-09-19)

- **Stage 40 hole, measured not remembered.** On a clean public-repo checkout, stage 40
  typecheck failed. `npm install --prefix compaction` exited 0 and left
  `node_modules/fast-jev-compaction` → dangling `file:../fast-jev-compaction`. `tsc` still
  exit 2. Second hole: Debian `/bin/sh` is dash; `set -o pipefail` stages exited 2 before
  work. Receipt: `NEGATIVE_EVIDENCE.md` R32.
- **Fix:** `scripts/bootstrap-compaction.sh` clones `tamaratran/fast-jev-compaction` at
  EVAL.md pin `6e1da50`, builds `dist/`, npm-installs `compaction/`. Stage 40 calls it
  when `--check` fails. Six `#!/bin/sh` + pipefail files now `#!/usr/bin/env bash`.
- **Docs:** `docs/INTEGRATIONS.md` + README TL;DR pointer — public chapter for
  `docs/demos/upstream-repro/toolcall-groundtruth-corpus-20260919.md` (`33aa633`).
  Headline: 3.95% isError on allowed (frozen 4.01%), 40× the 0.1% kill line,
  216,507 decisions, split 36,955 / 41,500, zero API. JOIN YIELD 36.8%; miss
  class `js-bash-<uuid>`; logger must capture command text at decision time.
  Pane 3 withdrew revert-predicate as INVALIDATED; `isError` survived.
  Fail-open verified at `dcg-guard.ts:599-610` via the corpus
  (`toolcall-groundtruth-corpus-20260919.md:9-12`); proposed certification
  files not cited as source. Observe-and-log is registered on `jev-lab` and
  is **not working**: observer wrote 0 rows, `dcg-tool-bridge` wrote 1. Loader
  globs `*.{ts,js}`; config is `extensions:` in profile `agent/config.yml`.
  No invented STOP-LIVE ban. Live test surface remains pane 0 / added test
  panes. `jev-compact` L3 measurement, does not prune. **0 promoted.**
- **Boundary:** this PR did not register any OMP hook and does not claim the
  live observer works. R30 unread and unedited. Stages 50/60 still need
  `LOOP_KIT` (foundry); this cloud does not have it, so the aggregate cannot
  be `ALL GREEN` here. No live Jev calls. Lane: offline.

---

## skillranker PROCESS archaeology @ public 6a74cca (2026-09-20, DEEP PASS A)

- Public HEAD `6a74ccad279b5ee4a3973790ec01b47265307a54` read via `gh api` +
  `/tmp` shallow clone (not a workspace clone; not committed).
- Loop extracted with file:line: session-context → roster → wide/rerank Jev →
  rank/abstain. Hook CLI, feedback CLI, and `src/` reader of
  `tests/eval/synthetic_cases.v1.jsonl` are **absent**. Ledger *schema* exists;
  rank write does not (`persistence: unavailable`).
- Eval contract still `frozen_contract_not_evidence`; always-abstain required;
  false abstention = 1, wrong pick = 2; top-1 gate 0.90. `rg` over `src/` for
  the cases file is empty.
- Gap vs `omp-jev-route` / `jev-usage-router` / `omp-jev-preaction`: no roster,
  no typed abstain cheaper than a wrong pick, no closed observe→judge loop.
- Receipt: `docs/demos/upstream-repro/skillranker-process-archaeology-20260919.md`.
- **Boundary:** no `sr` binary, no keyed Jev, no vendored-clone edit.
  Process patterns ≠ product promotion. **promoted=0 untouched.**
- Lane: offline. Claim: `[pending]` (source read, nothing executed).

## skillranker PROCESS mirror — omp-jev-route slice (2026-09-20, offline, [test])

- Upstream read: `Dicklesworthstone/skillranker` public `origin/main` **`6a74cca`**
  (shallow clone to `/tmp`, not vendored, not patched). Corpus **not** re-measured.
- Copied: `__none__` abstention, local eligibility, structured JSON decision,
  0/1/2 loss + always-abstain control + `diagnostic_synthetic` cannot promote.
- Refused: Quill 254-wide, two-stage Jev, Claude hook protocol, SQLite ledger, TUI
  (R42). Landed in `work/omp-jev-route/` (`process.mjs`, `gate.mjs`, `cli.mjs`).
- Ran: `node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs`
  → **19/19**. `cli.mjs decide` / `gate` on our 6-row fixture: mean loss 1.167,
  always-abstain 0.667, top-1 0.333, **`promoted: false`**.
- Receipt: `docs/demos/upstream-repro/skillranker-process-mirror-20260919.md`.
- **Boundary:** no live Jev, no `sr` binary, no working-profile register, no
  corpus re-score. Unpromoted. Ledger stays **0 promoted**.

## skillranker EVAL CONTRACT mirror — process harness, not a product measurement (2026-09-20)

- **What landed:** `work/skillranker-eval/` is now a reusable offline+live process,
  not a one-shot live script. Pulled via `gh` from public
  `Dicklesworthstone/skillranker` @ `bb52b8f25`: `evaluation_policy.v1.json`,
  `expected_values.v1.json`, `synthetic_cases.v1.jsonl` (provenance in
  `contract/PROVENANCE.md`). Their status fields remain
  `frozen_contract_not_evidence` /
  `deterministic_contract_examples_not_measured_results`.
- **First-class runners:** frozen 0/1/2 loss (asserted against the pulled policy);
  always-abstain (mean 10/12 = 0.833); coin-flip (exact E[loss] + seeded sample);
  planted wrong-pick must score 2 and RED; `--score`/`--live` treat top-1 < 0.90
  as **exit 2**, not a printed note. `diagnostic_synthetic` cannot promote.
- **Export:** `--export` writes `jev.skillranker-eval.score.v1` JSONL (pick / Y /
  loss). Overflow case `synthetic-overflow-retrieval-paraphrase` is flagged
  `installableNotOffered` (Y=`testing-fuzzing`, exported roster empty).
- **Judge shape** for an omp skill-router hook: `judgeSkillPick` in `score.mjs` —
  one Choice, `__none__` abstain, no second noul. Documented in
  `work/skillranker-eval/README.md`.
- **INTEGRATIONS.md:** one WIP / unpromoted row. Ledger stays 0 promoted.
- **Commands (this pass, offline):** `node --test work/skillranker-eval/test/contract.test.mjs`
  → 11/11; `run.mjs` always-abstain mean loss **0.833** top-1 **0**; coin-flip exact
  E[loss] **1.035**, sampled mean **1.036** sd **0.225** (5000 trials, seed 1);
  planted wrong-pick loss **2**; `--score` on the abstain export **exit 2**
  (`TOP1_BELOW_GATE`); `--live` without a key prints `NOT_RUN` (exit 0).
  `--selftest` PASS. The 1.035 coin-flip expectation is not their earlier 1.011:
  overflow has an empty exported roster, so the action space is `{__none__}` only.
- **Boundary / NO-CLAIM:** no `sr` binary invoked; do not cite this as a
  SkillRanker product result. No live Jev call in this pass. Prior live
  Jev-on-corpus receipt (mean loss 0.167, top-1 0.800, both misses = false
  abstentions) remains
  `docs/demos/upstream-repro/skillranker-corpus-measured-20260919.md` and was
  not re-run. n=12 diagnostic_synthetic cannot promote.

---

## math-and-next-level @ asupersync c80b20609 / franken_engine fc37f2dec / skillranker bb52b8f25 (2026-09-20)

- Receipt: `docs/demos/upstream-repro/math-and-next-level-20260919.md`.
- Re-derived identities only: always-abstain \(10/12=0.833\), Jev mean loss \(2/12=0.167\),
  STATUS census 7 CLEARED / 10 HELD / 8 RULED_OUT / **0 PROMOTED**. No live Jev.
- Unused Franken math cited at `file:line`: Bayes \(E[L|a]=\sum_s\pi(s)L(s,a)\), four AND-gates
  (empty evidence fails), dominance fraction, conformal \(\alpha=0.10\), e-process reject at
  \(e\ge 20\).
- Next ticks ranked: (a) `decisionLoss` in oracle-kit, (b) \(t^\star(\pi)\) on frozen priors,
  (c) four-gate *view* over existing receipts, (d) selector≡claim, (e) VOI / NP / regret.
- **Boundary:** no STATUS rewrite, no new gate stage, no crate import, no key. Inventory
  remains `franken-crate-alpha-20260919.md`. **promoted=0 untouched.**
- Lane: offline. Claim: `[oracle]` (public HEAD + committed receipts).

---

## §4 product ticks — decisionLoss / t*(π) / four-gate VIEW / selector≡claim (2026-09-20)

Landed the ranked ticks from `docs/demos/upstream-repro/math-and-next-level-20260919.md` §4
as runnable code. No live Jev. **promoted=0 untouched.** No STATUS.tsv schema change.

- **(a)** `decisionLoss({ yNonEmpty, abstained, pickInY })` in `work/oracle-kit/index.mjs`.
  `node work/oracle-kit/test.mjs` → **22/22**, including always-abstain `10/12 = 0.833`,
  false-abstain=1 / wrong=2 / needless=2, and the planted emission-only table that lets
  always-abstain win. `work/skillranker-eval/score.mjs` reuses the kit (does not duplicate
  the 0/1/2 numbers). `node --test work/skillranker-eval/test/contract.test.mjs` → **12/12**.
  `node work/skillranker-eval/run.mjs --control always-abstain` mean loss **0.833**.
- **(b)** `python3 work/oracle-kit/prevalence_threshold.py` exit **0**. Frozen priors
  `30/186449` and `488/50149`. Prints `FP/TP = 55791/24 = 2324.625` (~1:2300),
  `t*(foreman, L_FP=L_FN=1) = 0.99983910`, dcg `L_FN ∈ {1,10,100}`, planted `π=0.5 → 0.500`,
  planted `π=0` refuses. Shipped 0.80/0.50 are not Bayes under the signed triples.
- **(c)** `python3 scripts/promotion-four-gates.py UP-R5-jev-toolcall-gate` exit **1**
  (all four bits fail: 12/12≠11/12, block⊈observe-only, 15% vs 0.97%, adversarial
  unmeasured). `--selftest` exit **0**: empty evidence ≠ pass; STATUS.tsv digest unchanged.
- **(d)** kit planted `{noul:0.9}` as `probabilities` throws; `assertSdkSelector` /
  `refuseInventedNoulGate`; `node work/oracle-kit/selector-guard.mjs` exit **0** (no silent
  readers under `work/` `scripts/`); `--selftest` catches a planted silent reader.
  Closed a live fallback in `work/omp-jev-observer/src/classify-systemone.mjs`
  (`a?.probability ?? a?.noul` → `field(a, 'noul')`). Observer tests **8/8**.
- **(e)** `python3 work/oracle-kit/voi_harm_rule.py` exit **0**. Declared
  `L_miss=1, L_fp=10, c_call=0.01`. `VOI(jev vs regex) = -1.5200` on the frozen 12/12 vs
  11/12 identities. NO-CLAIM: planted harms, not incidents; FP dens. not like-for-like (R34).
- **Boundary:** no STATUS rewrite, no new `foundation/gates.sh` stage, no key, no
  working-dogfood claim. Negative: `NEGATIVE_EVIDENCE.md` R43 (emission-only loss).
- Lane: offline. Claim: `[test]`.

## cass TASK TESTS — design only, unpromoted (2026-09-20, [pending])

- Receipt: `docs/demos/upstream-repro/jev-task-tests-cass-20260920.md`.
- **What it is:** a Jev-specific eval contract for ranking / filtering cass
  `--robot` hits (dig-vs-invent, stale / wrong-workspace, empty-success
  refusal, selector≡claim). Adopts skillranker process
  (Choice+`__none__`, 0/1/2 loss, always-abstain required,
  `diagnostic_synthetic` cannot promote) from
  `work/skillranker-eval/contract/evaluation_policy.v1.json` and
  `skillranker-process-mirror-20260919.md`.
- **Cases:** 10 synthetic cass envelopes (9 judged + 1 selector plant).
  Preregistered always-abstain mean loss **6/9 = 0.667**; first-hit / BM25
  **14/9 ≈ 1.556**; perfect-judge feasibility **0**. Planted RED:
  always-pick-top-hit (CASS-09), empty-success (CASS-07), missing
  `source_path` (CASS-08).
- **omp wiring (designed, not landed):** before scaffold / ask-user, playbook A
  `cass health` + `cass search "…" --robot --limit 5` (`AGENTS.md:1410-1411`),
  then observe-only Jev-rank; export pick/Y/loss; neighbour co-presence with
  dont-give-up A. Never `--workspace <project>`. Never a blocking hook.
- **Commands this pass:** none executed. `command -v cass` → absent. No Jev
  call. No omp session. No STATUS / gauntlet edit.
- **Boundary / NO-CLAIM:** authored fixtures (R28); class A if later scripted
  against a fake asker; cass hit schema cited from upstream SKILL.md, not a
  local introspect. Unpromoted. Ledger stays **0 promoted**. Honest state:
  **EXPLORED**, not PROBED.

## jev-task-tests-beads design (2026-09-20) — `[pending]`, not a run

- Receipt: `docs/demos/upstream-repro/jev-task-tests-beads-20260920.md`.
  Fixtures: `work/jev-beads-eval/{policy.v1.json,cases.v1.jsonl}` (10 cases,
  always-abstain mean 0.800, `split: diagnostic_synthetic`).
- Tip census, not memory: `.beads/issues.jsonl` **n=48** at `5dfaba1`
  (26 closed / 11 open / 5 in_progress / 6 blocked; 6 P0 all `jev-publish-*`;
  7/26 `close_reason=done`; 12 parent-child deps; 0 cycles on a key scan;
  Muse children `jev-vbh` + `.1`–`.5`).
- `br` / `bv` **not executed** (absent from PATH here). No Jev call. No omp
  registration. **promoted=0.**
- Rejected designs: `NEGATIVE_EVIDENCE.md` R43.
- **Boundary:** this is an unpromoted design. The 10 cases were authored by the
  same pass that wrote the questions (R28). Clearing any later bar on this
  split licenses an observe-only CLI, not a working-profile advisor.

## jev-task-tests-agent-mail — unpromoted design (2026-09-20)

- **Receipt:** `docs/demos/upstream-repro/jev-task-tests-agent-mail-20260920.md`
- **Lane:** offline design. **Level:** `[pending]`. Zero Jev calls. Zero `am` invocations.
- **Upstream read (not cloned, not run):** `Dicklesworthstone/mcp_agent_mail@ac4966c`
  (`models.py` Message / MessageRecipient / Agent; README send/ack/overseer/urgent-unread).
  License on GitHub API: `NOASSERTION`.
- **Process stolen:** skillranker `tests/eval/evaluation_policy.v1.json` on origin/main —
  Choice+`__none__`, frozen 0/1/2, always-abstain required, `diagnostic_synthetic` cannot
  promote. Vendored `skillranker@3fe85c4` was **not** moved.
- **Contents:** 10 authored cases (8 nonempty Y / 2 empty Y; always-abstain arithmetic
  0.800), observe-only omp/`askJevChoice` wiring sketch, B0/B1 baselines, NO-CLAIM (never
  send authority).
- **Negative:** `NEGATIVE_EVIDENCE.md` R42 — 0/1/2 under-prices missed in-band phishing;
  re-asking Jev for Human Overseer `importance=high` loses cost-benefit.
- **Boundary:** no harness, no JSONL, no hook install, no STATUS.tsv row, no live inbox
  export. `am inbox` remains independently recorded as dead transport elsewhere; that is
  not re-measured here.

## frozen toolcall corpus scorer — real n=7846, not a 10-case design (2026-09-20)

- **Studio numbers (baked, not reinvented):** n=7846, GOOD=1665, BAD=6181,
  always-abstain **0.212210043** (1665/7846), isError-only **1.495284221**
  (11732/7846). Mapping: GOOD→allow; BAD→abstain/block. Loss: correct=0,
  abstain on GOOD=1, allow on BAD=2.
- **Command:** `python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py work/p3-calibration/toolcall-corpus-frozen.jsonl`
  reprints those strings (exit 0). `node work/jev-real-corpus-eval/run.mjs`
  same fractions + planted RED. Tests **10/10**.
- **Finding:** isError-only **loses** to always-abstain. A useful Jev judge
  must beat **0.212** mean loss on this split.
- Receipt: `docs/demos/upstream-repro/frozen-toolcall-scorer-20260920.md`.
  Tag **`[pending]` / promoted=0**.
- **Negative:** `NEGATIVE_EVIDENCE.md` R44.
- **Boundary:** no TYPESAFE, no Jev call, no omp seam, no CASS / agent-mail
  (this VM cannot reach those volumes). Lane: offline. Claim: `[test]`.

## cass / agent-mail alpha approaches — 24 mines, unpromoted (2026-09-20)

- **Receipt:** `docs/demos/upstream-repro/cass-mail-alpha-approaches-20260920.md`
  (24 cards) + `work/cass-mail-mines/README.md` (Studio-first A02 → A05 → A11).
- **Lane:** offline design. **Level:** `[pending]`. **`promoted = 0`.**
- **Not PR #31 / #32:** those stay on `toolcall-corpus-frozen.jsonl`
  (`sess` / `args` / `isError` / `args_len_*`). This catalog does not reprint
  0.212 / 1.495 / 0.197 as cass or mail numbers.
- **Process stolen:** skillranker `__none__`, 0/1/2, always-abstain, planted
  RED, `diagnostic_synthetic` cannot promote, prevalence gates, VOI vs cheap
  baseline, outcome co-presence, dig-vs-invent, selector≡claim.
- **Stores named, not opened:** `/Volumes/ZestData/cass-data/agent_search.db`
  (~59.8k / 5.2M) and live agent-mail (~6510). This VM: no ZestData, no
  `cass`, no `am`, no key.
- **First Studio mines:** A02 high-badge echo; A05 ack SLA; A11 mail↔cass
  join. Cass-fallback if mail is dead: A12 / A08 / A24.
- **Negative:** `NEGATIVE_EVIDENCE.md` R45.
- **Boundary:** no harness, no export, no Jev call, no omp seam, no
  STATUS.tsv row. Authored catalog ≠ measurement. State: **EXPLORED**.

## P4 grok-challenge — auto-recall KILL; cataloged recall shipped (2026-09-20)

- Receipt: `docs/demos/upstream-repro/grok-challenge-20260920.md`. Level `[receipt]`.
- **U2:** auto-recall still KILL at `cli/mod.rs:25807`. Cataloged recall is
  the supported surface (`preflight_guard.rs:235` toml layer) and is **shipped**
  as `jev/.ee/preflight_rules.toml`. `grep -c foo bar` → `ws_grep_c_as_proof` +
  memories including `mem_01M30A8VERE22V7WFGAYJRTMH7`. Control empty.
  Tripwire shim still refused. R53. Key is Infisical, not missing; no live
  Jev this tick (choice).
- **U1:** P3 rate CONFIRM 304; FP OVERTURN 62.5/70.8. Bash harvest UNMEASURABLE
  for prose was corpus-specific. Re-derived `~/.omp` JSONL: 1842 files,
  45108 assistant-text turns. Claim-verb no-prior-cmd 329/45111=0.729%;
  **REFUSE** (73% one session; seed 20260920P4c n=24 → 2 TP / 22 FP). cass dead
  (Quill 2^22 doc_freq); not waited on.

- **Negative:** R52 (narrowed) + R52-CORRECTION + R53.
- **Boundary:** no preflight hook at tool_call. Morph MCP unwired here.


## P2 sr-advise — verified=0 ruled, manifest eligibility 0→10, doctrine mined (2026-09-20)

- Receipt: `docs/demos/upstream-repro/sr-advise-20260920.md`. Level `[live]` (N=2 decisions).
- **U1:** `roster verified=0` is by-design inspection reporting
  (`skillranker@abf909d` discovery.rs:627-630, cli.rs:1978-1979). Rank advises nothing via
  global withhold (resolution.rs:530-540), tripped by entry-limit (23,100 files vs 10,000
  DISCOVERY_FILES, limits.rs:296-297) AND by symlinked dirs (50 store + jev
  `.claude/skills/typesafe-ai`). Plus alias-guard false positive on `Bash(*)` globs
  (frontmatter.rs:354-363) behind 14 malformed-metadata. Controls: clean-HOME rank from
  neutral cwd → eligible 3 (exit 11 cache-miss); from jev/ → exit 5 (project symlink).
- **U2 LIVE 2026-09-20** (key via infisical, 4 requests of ≤4 stated, jev-1.13.0): task rank
  → skill-search-mcp alone at 1.0 (HIT; 4/4 wrongs at 0.0; honest MISS research-scout 0.0).
  Seat verdict: paid call earns it (offline admits, only live cuts). Negative "what time is
  it" → abstain/low-fit/none_p 1.0 after full 2-stage pass (judgement abstention measured).
  Both cases saved (0600) + replayed offline exit 0. Reportable defect (NOT filed):
  `sr-withhold-defect-20260920.md`. P3 warned off sr routing directly.
- **U3:** wide (3 Noul gates + which + phase + optional stuck) → gate-mean (0.30) → rerank
  (choice + fits:: Nouls, fits floor 0.30, must-beat-none); 25-kind refusal taxonomy
  (output/mod.rs:126-156); replay-case + ledger tables mined with file:line.
- **Boundary:** one machine, 10-skill manifest (full store unrunnable), live N=2, variance +
  57-candidate scale untested, morph unused, skillranker/ untouched. State: **VALIDATED**
  (offline ladder + live decisions; omp-seam wiring explicitly out of scope).

## P4 cass posting-cap stranger-repro WITHDRAWN (2026-09-20)

- **Lane:** offline. cass **0.8.0**. Isolated `/tmp/cass-repro-cap.ix7l2y1n`.
- **Claim tested:** 4.2M unique messages sharing token `zwpostingcap` make
  `cass index --full` hit Quill posting validation (`doc_freq` > 4,194,304,
  code 9).
- **Measured:** index rc=0, `success:true`, 4,200,000 documents in 148 s.
  Unique late/mid phrases search-hit. Bare ubiquitous term `total_matches≈50`
  is IDF, not a cap error.
- **Verdict:** WITHDRAW. Do not file. **R54.** Bead `jev-w6u` closed.
- **Boundary:** did not reopen the live ZestData archive whose 4.49M df was
  P1's original observation. FTS shadow dropped at 100k (cass GH #413) —
  Quill path still served unique phrases.

## P2 sr issue #4 filed + Jev-call doctrine (2026-09-20)

- Upstream: `Dicklesworthstone/skillranker#4` (One symlinked skill dir empties the whole
  roster), filed by conductor under `flywheel-4ezzd`. Draft `/tmp/jeff-issue-sr-withhold.md`,
  rubric pass 7/7. Conductor independently verified the repro (exit 11/eligible 3 → exit 5
  → exit 11, reversible). `jev-jwr` open for Phase 4 watch (4h reply SLA on Jeffrey response).
- Filing lessons (mine, all self-inflicted): re-read draft as stranger (shipped empty
  Out-of-scope + truncated dedup — rubric blind to both); tracking bead must be `flywheel-`
  (`jev-` fails submit regex AND rubric prefixes); date-at-line-start trips leak detector,
  do not loosen (gaming-an-axis).
- Doctrine: `docs/JEV-CALL-DOCTRINE.md` — the durable output. Wide→rerank, sentinel +
  must-beat-none, Noul gates separate from Choice, untrusted-state discipline, refusal
  taxonomy shape, replay testing, ledger tables, defaults, and what we do NOT adopt
  (global withhold until #4 fixed). Level `[live]` (doctrine proven by N=2 live decisions).
- **Boundary:** no new live calls (0 this unit); skillranker/ untouched; `.beads` rows
  (jev-jwr/jev-osh) flushed to JSONL, commit deferred — sibling rows present, not mine to carry.

## P2 fh-doctrine mine: 3 refusals, 0 shipped (2026-09-20)

- **Lane:** offline. fh STALE (`ledger_age_hours≈307` — freshness of the
  refresh cron only; rows and citations stable, no recency claim). Rows read
  via `fh search` + `fh why`: **C71** (search the crate before patching the
  caller; cited `local@4bcb1844:src/search.rs:1321`) and **C60** (truncated
  denominator / exit-124 / empty-as-finding; cited
  `frankengit@25537a1:scripts/verify.sh:55-60`).
- **Corpora (neither authored by the scorer):** bash harvest
  `work/toolcall-judge-v3/real-allowed.json`, N=78,242 (`tool=bash` throughout,
  structurally blind to prose); assistant-text turns N=45,220 over 1,839
  session JSONL under `~/.omp`, walked 2026-09-20T22:04:21Z (brief said
  1,842/45,108 — drift during the day, quoted hour is the measurement's).
- **Measured:** `workaround`+upstream-vocab 89 (0.1968%), FP 0.95 (n=20, seed
  20260920, one labeller, single TRUE at msg `30f09953` "took the workaround
  six times"); bare empty-narration 218 (0.4821%), FP 1.00 (fires land on
  compliant writeups: exit codes named, conclusions withheld); empty+timeout
  conjunction 27 (0.0597%, below the 50 floor), FP 1.00; `timeout`-led bash
  commands 247 (0.3157%, legitimate bounded probes).
- **Verdict:** REFUSE all three — **R56/R57/R58**. No rule files touched, no
  selftest arms added (a rule with no test is a rule nobody has seen fire,
  and these earned no rule). `scripts/selftest-ttsr-rules.sh` re-run as
  regression: 51 ok / 0 failed, no drift.
- **Boundary:** one labeller; prose predicates only — the C71 tell lives in
  written code content, which no current TTSR scope observes (see R56 retry);
  corpus drifts (fleet sessions write during measurement); `fh` STALE so
  nothing said about recent movement; /tmp evidence not committed.

## P4 Jev rule-class triage vs deterministic baseline (2026-09-20)

- **Lane:** live. Model requested `jev-latest` → **jev-1.13.0**. Calls=19.
  Receipt `work/jev-triage/runs/2026-09-20T221149741Z.json`. Pattern: Choice
  over five verdicts (`docs-mirror/typesafe/primitives/choice.md`). Client:
  `work/jev-client` `askJevChoice`.
- **Gold:** 19 hand rulings from the dispatch (SHIP 6 / TOO_RARE 7 / NUISANCE 2
  / LOW_PRECISION 2 / UNDERPOWERED 2). State is numbers only — no class name.
- **Baseline (offline, 10/10 tests):** ship iff hits≥50 AND rate≤5% AND
  (FP≤0.30 OR unlabelled) AND concentration<0.5. 5-way **15/19**. Binary
  SHIP-vs-rest **17/19** (TP=6 FP=2 TN=11 FN=0). The two extra ships are
  digest-truncation and path-nonexistence (numeric bars pass, gold is
  not-a-defect / nuisance).
- **Jev 5-way 6/19.** Binary 13/19 (TP=0 FN=6 — never chose SHIP or NUISANCE;
  13/19 mass on UNDERPOWERED). **SEAT NOT-EARNED.**
- **Disagreements vs baseline: 15.** Jev beat baseline on two gold-UNDERPOWERED
  rows (v2-files, claim-verb) and lost every SHIP. Calibration: every call
  with conf≥0.64 is WRONG; first correct is conf=0.510. Acting above a high
  threshold would ship nothing and still be wrong on the confident refusals.
- **Boundary:** gold maps concentration→UNDERPOWERED and not-a-defect→NUISANCE
  (the five options have no sixth); count-as-verdict gold is the dispatch SHIP
  not the later depth-pack overturn; n=19 one set, not a hold-out; tmux-untargeted
  N taken as the bash harvest.


## P2 doc-index denominator + mechanizable split (2026-09-20)

- **Denominator (reported first, per dispatch):** `fh doc-index` envelope
  `franken-harvest.doc-index.v1`, generation `08457a25`: **36,692 rules
  indexed** (27,289 AGENTS.md + 9,403 CONTRACT.md), 207/224 mirror repos read,
  390,739 chunks. Direct record count with AGENTS/CONTRACT path filter:
  **33,380 rule records across 117 repos** (envelope vs direct differ on rule
  granularity; both quoted). Two citations was thin — the vein is 36k deep.
- **Split (n=60 hand-classified, seed 20260920, one labeller):** unmarked pool
  29,176 records (87.4%) → **0/30 mechanizable** (process prescriptions,
  invariants, tables, status); marked pool 4,204 (12.6%,
  command-mentioning) → **3/30 mechanizable-shape** (M-2 never-deploy-direct,
  M-10 shell-backtick-substitution, M-15 no-branches), of which **1/30
  universal-content** (M-10; M-2/M-15 are project-local conventions).
  Stratified projection: ~1.3% mechanizable-shape, ~0.4% universal. **Most
  doctrine is not mechanizable — now with a number behind it.**
- **Converted:** M-10 measured (broad 1,417 dominated by fence extraction;
  narrow 12, below floor, residuals deliberate probes) → **R59**. Rejected
  surface: 23,151 candidates, 0 reasoned → **R60**. SHIPPED 0.
- **Lane:** offline. No rule files touched; selftest untouched at 51/0 (no
  regression run needed — nothing it covers changed; stating so instead of
  burning a run).
- **Boundary:** single labeller; marker-filter recall estimated on the same
  n=60 (not independently proven); techniques/rigor/oracles/
  doctrine-history unsearched — doctrine-history (rules added after
  incidents) is the named next vein; `fh` ledger STALE throughout.

## P4 Jev triage fair re-run — semantics vs arithmetic (2026-09-20)

- **Lane:** live. `jev-latest` → **jev-1.13.0**. Calls=19 (Choice+Noul parallel).
  Receipt `work/jev-triage/runs/2026-09-20T221837415Z.json`. State = name +
  description + predicate + 3 corpus examples + numbers. Mapping choice
  (stated, not gold): not-a-defect→REFUSE_NUISANCE, concentration→UNDERPOWERED.
  count-as-verdict gold = dispatch-time SHIP.
- **Baseline Choice 14/19.** SHIPS all 3 semantic rows (digest-truncation,
  path-nonexistence, pipefail-masked 227). Noul: **UNANSWERABLE**.
- **Jev Choice 7/19** overall (still loses arithmetic). **Semantic Choice 3/3**
  — all three REFUSE_NUISANCE, which the numbers cannot produce.
- **Jev Noul semantic 2/3:** digest 0.09 false, path 0.24 false, pipefail 0.51
  true (miss at the 0.5 line). Arithmetic noul 11/16.
- **SEAT:** earned on the semantic question the regex cannot ask. Not earned
  as a replacement for the numeric Choice.
- **Boundary:** git-add-A harvest had no executed `git add -A` (dcg denies);
  two of its examples are the class shape not harvest hits. Text-class
  examples from the measured predicate arms, not a fresh JSONL walk.

## P2 unbiased doctrine ratio + CI + pool (2026-09-20)

- **Correction accepted:** the n=60 split was stratified (marker-enriched),
  not a ratio, and five searched rows were anecdote. This replaces both with
  a seeded-random sample: **n=300 from the 33,380-record frame** (AGENTS.md /
  CONTRACT.md records, generation `08457a25`), seed
  `20260920-unbiased-300`, frame + indices at
  `/tmp/fhvein_unbiased_idx.json`, sample at `/tmp/fhvein_unbiased_300.json`
  (uncommitted scratch, reproducible from seed + generation).
- **Bar (preregistered):** MECHANIZABLE-SHAPE = the rule as written
  prescribes/prohibits a concrete tool-call shape (command + args/flags,
  exit-code handling, path pattern, quoted-arg content) or a tool-result
  claim checkable by regex over one call/turn, with an identifiable
  near-miss. Else ADVICE. Universal vs project-specific judged after.
- **Ratio:** mechanizable-shape **9/300 = 3.00%, 95% Wilson CI
  [1.59%, 5.60%]** → implied pool over 33,380: **529–1,870 (point ~1,000)**;
  over 36,692: 582–2,055. Universal-content **3/300 = 1.00%, CI
  [0.34%, 2.90%]** → 114–967 (point ~334). The 9: R-31 (runner,
  project), R-33/R-89/R-220 (bare-TUI ×3, fleet), R-41 (secrets-to-git,
  universal), R-42/R-290 (destructive ×2, universal-redundant),
  R-197/R-273 (lockfile ×2, project). Classes cluster — the pool is real
  but thin at the top.
- **Converted:** R-41 measured → 2 hits, 0 true → **R61**. Verdict on the
  vein: worth screening (doctrine-history incident-earned filter next), not
  worth a blind week — the unbiased pool's universal remainder is a handful
  of already-covered shapes.
- **Lane:** offline. No rule files touched; selftest untouched at 51/0.
- **Boundary:** one labeller; frame is records (33,380), not envelope rules
  (36,692) — definitional gap stated, both carried; techniques/rigor/
  oracles still unsearched; corpus/session drift applies.

## P4 hybrid veto — widened semantic gold n=6, n_total=23 (2026-09-20)

- **PART 1:** every R-heading classified in `work/jev-triage/r-classify.json`.
  Semantic TTSR classes that cleared numeric bars and were refused on meaning:
  **n=6** (digest-truncation, path-nonexistence, R55-loose, R55-pipefail-token,
  R59-broad, R56-bare). Not "a large share of 55 R-numbers" — 54 headings are
  instrument/design/not-a-class. R54 cass withdraw excluded (no hits/rate).
- **PART 2 hybrid:** numeric first; Noul veto only on survivors. Budget this
  run: **3** (cached 9 from the fair re-run). Cold cost: 12/23. Model
  `jev-latest` → jev-1.13.0.
- **@0.5:** hybrid binary **18/23** (TP=4 FP=3 FN=2) vs baseline **17/23**
  (TP=6 FP=6 FN=0). Semantic choice 3/6 vs 0/6. New noul: pipefail-anywhere
  0.23 veto-ok; R59-broad 0.74 and R56-bare 0.89 slip through (Jev rates them
  as defects).
- **Calibration:** BEST_T **0.25** → 20/23 FP=3 FN=0. t≥0.55 kills true ships
  (FN=4). t=0.90 gets semantic 6/6 at FN=5 — not deployable.
- **COST:** 1 Noul per class that passes hits/rate/FP/concentration. Not per
  candidate ever mined.
- **Seat:** hybrid beats both pure arms at 0.5 (+1 vs numeric, 3/6 vs 0/6
  semantic). The remaining 3 semantic FPs are high-noul; a higher t causes FN.
  Mapping still a join. Receipt
  `work/jev-triage/runs/hybrid-2026-09-20T222532529Z.json`.


## P4 hybrid challenge — McNemar + LOO, aggregate retracted (2026-09-20)

- **18-vs-17 RETRACTED.** McNemar on SHIP-vs-rest @0.5: b=3 c=2 n_disc=5,
  p_exact two-sided **1.0**. Indistinguishable. Stop quoting it as a win.
- **Seat that survives:** semantic noul 3/6 vs baseline **0/6 structurally
  incapable**. One relabel → 2/6 or 4/6; 2/6 is a coin. The structural claim
  is immune to one flip.
- **t=0.25 20/23 is resubstitution.** LOO-of-threshold also **20/23** because
  every 22-row fold picked t=0.25 (pick stable on this sample, not an
  independent test of the noul values). Both labelled.
- **Orientation:** SHIP-vs-rest FN=0 at t=0.25 means no *good* class blocked.
  FP=3 means three *bad* classes still ship (pipefail-masked 0.51, R59 0.74,
  R56 0.89). Gate-to-stop-bad: veto TP=3 low-noul, veto FN=3 high-noul
  confident wrongs, veto FP=0. Not "no bad class ships / 3 extra reviews".
- **R56/R59:** noul 0.89/0.74 are confident wrongs. Catching them needs t≈0.90
  at FN=5. Low-noul veto seat survives; general meaning-judge seat does not.
- Receipt `work/jev-triage/runs/mcnemar-loo-20260920.json`.


## P2 container-fit writeup + survival curve (2026-09-20)

- **Write-up:** `docs/essays/container-fit-doctrine-vs-rules-20260920.md` —
  97% of mirror doctrine has no trigger string; TTSR is the wrong container
  for it (read-once layer instead); the mine-into-rules plan tops out at
  114–967 candidates. Ratio, CIs, curve, and doctrine-history filter verdict
  inside.
- **Curve (N=78,242):** bare-TUI cmd-position 11/0-true, foreign-pm 110/FP
  1.00, branch-create 0, vercel-direct 2, bun-test-bare 4, destructive 258
  (redundant w/ dcg) → **R62**, nothing ships. doctrine-history filter
  verified working (~7s/repo; mwb 346/107/118); sampled rows are
  bulk-imported (f2e432e6), not incident-earned.
- **Lane:** offline. No rule files touched; selftest untouched at 51/0.
- **Boundary:** one labeller throughout; essay is prose synthesis over
  ledgered measurements (R56–R62), not new data.

## P2 ft-sh-doctrine + ft-md-doctrine rules written (2026-09-20)

- **Files (system-wide ONLY, no second copy):**
  `~/.agents/rules/ft-sh-doctrine.md`,
  `~/.agents/rules/ft-md-doctrine.md`. Contract per dispatch:
  condition `\S`, scope `tool:edit(*.EXT), tool:write(*.EXT)`,
  interruptMode never, repeatMode once. P3 owns ft-rs; untouched.
- **Threads:** .sh — single entry (88/221 mirror repos ship zero .sh,
  measured over 221 repos), wrapper-verdict
  (frankengraphdb@a3c2bec22…:scripts/check.sh:24, verbatim),
  capture-first (lane-owned); .md — equal-or-weaker
  (frankengraphdb@a3c2bec22…:registries/constitution.toml:25, maps onto
  our commit-msg hook), no-claim boundaries
  (asimposium.org@4d8d6cc0b…:AGENTS.md:413). 12-line budget held; every
  line names a tool, command, or check.
- **Predicate proof (offline, `omp ttsr test`):** sh fires on sh-edit,
  quiet on md-edit, quiet on bash; md fires on md-edit, quiet on
  sh-edit, quiet on bash — 6/6 as contracted.
- **Boundary:** this session predates both files, so no live-fire claim
  from here — live proof needs a fresh session (ruleproof-style).
  Selftest arms HELD: P3 lands 4 rs arms first (agreed over ntm);
  worktree shows their edit in progress, so the shared file is untouched
  until their commit.

## P2 ft-py-doctrine shipped (2026-09-20)

- **Surfaces searched:** doc-index all 390,739 records (py-path pool
  32,314; uv-only 52/17 repos, ruff 123/18, py-version 52/10);
  techniques (all 7 Rust-crate — nothing py); rigor/oracles
  (D4 NetworkX, D5 pandas-2.2.3, D8 NumPy, D9 SciPy — oracles, not
  authoring threads); doctrine-history on bio_inspired_nanochat
  (508/226/363) and frankenpandas (328/65/56); omp builtins (27 —
  zero py-scoped, verified from `omp ttsr list` output, not memory).
- **Shipped** `~/.agents/rules/ft-py-doctrine.md` (system-wide only):
  uv-only (bio_inspired_nanochat@1e4b475cb…:AGENTS.md:34, added
  2026-01-09 + rewritten — lived-in), ruff/ty/pytest gates
  (bio:640 + 3 repos same shape; removed once, restored — churned,
  retained), live-pandas oracle
  (frankenpandas@debdf374…:TESTING_CONVENTION.md:52; history-blind,
  non-AGENTS file — stated). Vendored third-party skill artifacts
  inside pi_agent_rust fixtures explicitly NOT cited as doctrine.
- **Proof:** 6/6 `omp ttsr test` probes green; 6 arms appended post-P3
  commits with own block; full suite **71 ok / 0 failed**.
- **Boundary:** session predates the file — live-fire NOT_RUN from
  here; needs a fresh session.

## P2 ft-json-doctrine shipped, one clause (2026-09-20)

- **Shipped** `~/.agents/rules/ft-json-doctrine.md` (system-wide only,
  exact contract): ONE clause — no real customer state (rg check named).
  Cut: schema_version envelope (1,040 hits/57 repos — real thread, but
  no per-write check; schemaless fixtures are usually fine) and
  errors-as-data (architecture, belongs in a skill/AGENTS.md, not a
  write-moment injection).
- **Proof:** 4/4 probes green; 4 arms appended to a clean shared file;
  full suite **76 ok / 0 failed**. STOP ADDING RULES per dispatch —
  next unit sharpens existing pack pending P3 bind rates.
- **Boundary:** live-fire NOT_RUN from this session (predates the file).

## P2 gap-condition funnel: 3 in, 0 survive (2026-09-20)

- **Corpus:** 30,041 edit/write toolCalls over 1,817 sessions (args
  capped 20 KB). Sessions-touched: SH1 1 (0.06%), SH2 30 (1.65%),
  MD1 9 (0.50%).
- **Labels (n=20 each, seed 20260920-gap):** SH2 FP 1.00 (fires on
  correct capture-first idiom); MD1 FP 1.00 (fixtures, dispatch
  packets, provenanced claims); SH1 below floor, unlabelled.
- **Advisory:** 3/3 numeric_refuse via advisory-veto.mjs offline
  (LOW_PRECISION, TOO_RARE ×2); rows appended to
  work/jev-triage/advisory-veto.jsonl — pane 4's file, left
  uncommitted by me, disclosed here.
- **Closed permanently as rules:** SH1/SH2/MD1, single-entry-count,
  equal-or-weaker-as-gap, wrapper-as-gap, capture-first-in-sh.
  Read-once owns them. **R65.**
- **Boundary:** payload cap 20 KB; concentration MD1 top-share 0.49
  (closest to reconsideration, still short on both axes).

## P2 exposure-ranked census, no rules (2026-09-20)

- **Deliverables:** `docs/essays/exposure-census-20260920.md` (ranked
  17 rows) + `work/exposure-census-20260920.tsv` (machine table for
  P3's exposure-check.sh: label, pattern, not/path patterns, hits, N,
  sessions, top1, detectable, verdict, evidence).
- **Top 5 by exposure:** backtick-quotes 1,417; glob-silenced 820
  (shipped); pipe-exit 807 (shipped); destructive 258 (dcg-redundant);
  timeout-led 247 (form-correct). Detectable 5/5 — detectability was
  never the constraint.
- **Handed class:** number-without-denominator, 5 today + MD1-adjacent;
  undetectable as single-string predicate (MD1 FP 1.00), already
  containered as `scripts/denominator-sweep.sh` — REDIRECT, not refuse.
- **Boundary:** harvest classes lack session attribution (stated per
  row); one labeller; patterns recorded for rerun, not asserted final.

## P2 consumer-check built (NEEDS #2, 2026-09-20)

- **Path:** `scripts/consumer-check.sh` (+
  `scripts/selftest-consumer-check.sh`). Answers WHAT READS THIS from
  executable surfaces (repo .omp seams, scripts, bin, githooks, live
  global extensions, ~/.local/bin); refuses on zero with surfaces
  named. Mentions (docs/tests) classified, never counted; session
  JSONL, logs, vendor, fixtures, templates excluded outright.
- **Discriminator built from the failure:** command-position +
  quoted-path match for consumers; sibling scan (shell, COMMAND_ARGS
  array, EE_BIN const forms) on refusal only. Two bugs found dogfooding
  it here: a deleted if-branch (always-ZERO) and rg group renumbering
  across -e alternations (fixed: one -e per call, -U for cross-line).
- **Arms (selftest 6/6):** ee-preflight → exit 1, ZERO, both basenames
  with orient/journal; dcg → exit 0, dcg-tool-bridge.ts. RED: nonce
  tool → ZERO exit 1.
- **Boundary:** subcommand tokens noisy (comment-sourced); related
  callers labeled verify-by-reading. Session-JSONL historical
  invocations deliberately out of scope v1.

## P2 consumer-check fix, argv-array false ZERO (CHALLENGE-P2, 2026-09-20)

- **Defect:** `ee orient` returned ZERO though
  `ee-ambient-session-start.ts` invokes it via `EE_BIN` +
  `COMMAND_ARGS` spread — the literal `ee orient` never appears.
  False zero is the dangerous direction (retires live wiring).
- **Fix:** with a subcommand query, a file carrying BOTH a binary
  reference (`<NAME>_BIN` const or `/bin/<name>` path) AND the quoted
  subcommand literal on code lines (full-line comments stripped) is a
  CONSUMER with evidence lines. Tool never counts its own two files.
- **Selftest 8/8:** prior 6 + `ee orient` exit 0 with argv-array
  evidence. Prior verdicts re-examined: `ee preflight` still ZERO
  (literal absent from all three ee-calling files, confirmed by direct
  rg), `dcg` still exit 0, nonce still ZERO exit 1.
- **Boundary:** sibling-scan token noise unchanged (verify-by-reading);
  filenames with spaces break the argv loop (none on these surfaces).

## P2 consumer-check R68 fix + 19-instrument inventory (2026-09-21)

- **R68 (conductor):** `denominator-sweep` and `exposure-check`
  returned ZERO though gate-80 selftests invoke both. Cause: tests
  were MENTION tier, so the middle link of a live gate chain read as
  nothing. Second false-negative class in one day, both dangerous
  direction. Verdict now reads NO NON-TEST CONSUMER, never
  `nothing invokes`.
- **Fix:** tier 2b relative script-path form (`./scripts/X.sh` — the
  `.sh` suffix broke the bare-token boundary); tier 4 harness callers
  (literal, var-bound `S=...`+`"$S"`) with one-hop chain
  (`gates.d/80 (glob)` vs literal vs UNGATED). Self-file can never be
  its own consumer (killed quickstart+exposure self-match false
  positives). Selftest 12/12 with denominator+exposure chain RED arms.
- **Inventory (19 shell instruments + 1 mjs):** CHAINED 9
  (denominator, exposure, vgrep, pin-liveness, rung-demotion,
  verify-other, verify-numerals, audit-lineage, consumer-check);
  CONSUMED 1 (pinned-denominator <- denominator-sweep.sh:38);
  UNKNOWN 9 (fleet-tick, lane-status, publish-export, verify-frozen,
  noclaim-harvest, feed-idle-panes, quickstart, bootstrap-compaction,
  sync-docs) + measure-framing-flip (mjs). lane-status/quickstart
  needed manual override: heredoc prose matched tier 1 (open gap).
- **NO-CLAIM:** 10 wired, 9 UNKNOWN. UNKNOWN is not healthy and not
  shelfware. Tool gaps open: heredoc-prose false positives,
  pathlib-bind (`GATE = REPO / ...`) + wrong-extension (.sh-is-python)
  harness forms, lowercase bind vars, foundation/gates.d not a tier-1
  surface. Mid-unit self-inflicted: a stray `:` in the harness
  heredoc silenced tier 4 for 10 runs (caught by probe, all
  re-run); sed/python used for two micro-edits instead of edit tool.

## P4 ttsr-assert-disabled (CALLBACK-P1-CORRECTION, 2026-09-20)

- **Defect:** disable of `absence-from-one-probe` was reported via
  `omp config set` + `omp ttsr test` silence. Config set replaced the
  list (rule stayed live in project scope). Probe silence under
  `repeatMode once` cannot distinguish DISABLED from
  ALREADY-FIRED-THIS-SESSION. Joshua appended correctly; this unit
  does not re-set `ttsr.disabledRules`.
- **Instrument:** `scripts/ttsr-assert-disabled.sh <rule>` enumerates
  `omp ttsr list --json` in project cwd and in an outside-repo cwd
  (`/tmp/ttsr-assert-disabled-scope`, refuse if that dir has `.omp`).
  Exact `name` field match. Exit 1 names the scope and count. Never
  `omp ttsr test`.
- **Selftest 4/4:** RED live `bash-callsite-grep-exclusion` exit 1 +
  named scope; GREEN `absence-from-one-probe` absent both scopes
  (project 0, global 0, matching Joshua's enumeration); usage no-args
  exit 2. Wire: `foundation/gates.d/80` globs `scripts/selftest-*.sh`;
  EXPECTED_DISABLED in the selftest is the disable contract.
- **n=77 identities persisted** (R70):
  `work/skills-vein/absence-n77-labels-20260920.json` — 77 keys
  `profile||<path-after-sessions/>||line` → TP|FP. FP=21 TP=56.
  Replacement sample, not stacked on the unpersisted original 20.
- **Boundary:** full 80-lane suite not re-run this unit (glob wire
  only); no live Jev call; files of the retired rule not deleted.

## P4 AXIS C — skillranker Jev harness is plumbing, not accuracy (2026-09-20)

- **Pin:** `skillranker@abf909d`. Offline read. His suite not executed.
  Artifact: `docs/demos/upstream-repro/axis-c-skillranker-jev-harness-20260920.md`.
- **Q1:** `tests/jev_contract.rs` (718) decodes hand-built JSON. Sum/argmax/
  nonfinite/duplicate-key. No gold labels. No accuracy.
- **Q2:** `jev_smoke.rs` live arms are `#[ignore]`. Forced live without
  consent/key **fails** (`explicitly_selected_live_test_cannot_pass_without_consent_or_key`).
  Not skip-as-pass. Live smoke accepts `food_class ∈ {apple,carrot,__none__}`.
- **Q3:** `jev_retry.rs` (864) loopback TLS. Retry `{429,500,502,503,504,529}`,
  cap 4, delay 100..=850ms, deterministic `Retry-After`. Not hammering.
- **Q4:** P1 transport/codec, P2 roster, P3 context/privacy, P4 ranking on
  `GateMockTransport`. P5–P9 have no `p*_gate.rs`. `adapter_contract.rs` is
  Claude/cass, not Jev.
- **Q5:** Named baselines in `tests/eval/` are frozen policy, *"not benchmark
  results"* and contain no live Jev. His reality-check row 20: usefulness
  UNPROVEN. **R69 stands.** Adopt client discipline, not the seat.
- **Boundary:** no live Jev; clone read-only; R69 not reopened.

## P4 PLAN REVIEW R1 of v2 @680d11e (2026-09-20)

- **Artifact:** `docs/demos/upstream-repro/plan-review-r1-v2-680d11e.md`.
  Grok vs Opus. Round 1 of ≥4. No beads.
- **Dual bar:** `bar_point=bar_interval=0.30` is NEED #6 renamed, not his
  0.90/0.80 split. Ship-time CP (`NEEDS.md:35-38`): 4/20 upper 0.437,
  6/20 upper 0.543. INTERVAL refuses all three ships; POINT refuses none.
  Plan's 0.381/0.605 are n=77 relabels, wrong event. 0/25 kill still
  accepted (CP upper 0.137 < 0.20).
- **k unbound** remains the hole that eats `uncertified-pass`.
- **scope-disagreement** fatal as a commit check; live doctor already
  exists (`ttsr-assert-disabled.sh`).
- **T6 depending on T4** is a false edge. T4 must wait on T5.
- **4.1:** adopt mutation twins. Refuse phrase `non_claims` and
  `always_quiet` without a loss table. Dual story inverted.
- **Boundary:** pane-1 start-callback rejected (`tmux not in a mode`).
  Did not edit the plan. Did not run his eval-policy script.

## P4 PLAN REVIEW R2 of v4.1 @29038ab (2026-09-20)

- **Artifact:** `docs/demos/upstream-repro/plan-review-r2-v41-29038ab.md`.
- **Table:** every Wilson cell matches; ft-sh is 1/25. Header `:241`
  still scores FP at `p̂ ≤ 0.30` — vacuous dual restored in the copy
  site. §6 still *accepts* 0/25; table *refuses* it.
- **bar_point 0.20** = 4/20. Ratio 2/3 ≠ his 8/9. Reverse-engineered
  so n=20 is interval-only. Do not freeze.
- **k-drift/sha256** closes transcription, not the labeller (R71).
  Example hash `e3b0c442` is SHA-256("").
- **T6b still Depends T4** despite mktemp acceptance.
- **Boundary:** did not edit the plan. Round 2 of ≥4.

## P4 PLAN REVIEW R4 of v5.1 @931c872 (2026-09-20)

- **Artifact:** `docs/demos/upstream-repro/plan-review-r4-v51-931c872.md`.
- **NOT-YET beads.** Blocker: `uncertified-pass` = both bars (`:158`)
  vs `bar_point` unset (`:217`); T2 eight codes vs §6 fifteen plants;
  k has no gold field. §3 still "not a hole" — transcription≠R71 did
  not land. §4.1(6) missing. Title still v4/round-1.
- **T4→T6b edge gone.** Copy-site class remains in predicates.
- **Point UNSET** is rigor if the program is interval-only; evasion
  while §4.2 still uses 0.20 to prove dual legs.
- **Q7:** interval 0.30 ours keep; dual shape without a second number
  refuse; Joshua-as-key refuse; phrase non-claims refuse; mutation
  twins adopt; sha256 checksum not R71.
- **Boundary:** did not edit the plan. Round 4. v5.2 of three sentences
  then beads.

## P4 PLAN REVIEW R5 of v7 @b34d3f8 (2026-09-20)

- **Artifact:** `docs/demos/upstream-repro/plan-review-r5-v7-b34d3f8.md`.
- **NOT-YET.** Table has **17** codes; plan claims **16**. T2 still names
  eight plus leftover `unstated-assumption`/`missing-non-claims`.
- `uncertified-pass` cell is interval-only; prose `:176` still either-leg;
  §4.2 still 0.20 dual demo. `k_gold` in authority **landed**; R71 honesty
  landed. `unpersisted-rate` still says R70/R71 exactly.
- Silent-loss: new codes in table not in T2 list. scope/uncovered stayed
  in tables v5–v7.
- **Boundary:** did not edit the plan. Count is the blocker.

## jev-spam-eval regime — distribution shift, not spam (2026-09-21) [oracle]

Repo `jev-spam-eval` @ `76ef183` **at HEAD**. `OUT_OF_DISTRIBUTION.md` and `README.md` are clean against that SHA. Two result files are dirty in this checkout and must not be replayed as the published numbers: `results/ood_modern.jsonl` and `results/ood_tfidf_predictions.jsonl`. Pane 1 scored `ood_modern.jsonl` both ways (label vs `choices.choice`, ham/legitimate collapsed). `category` and `category_names_only` match HEAD. `category_urgency_authority` is 616/633 = 97.31% at HEAD and 612/633 = 96.68% in the working tree, 4 rows flipped. The README headline 97.3% is the HEAD value. A replay of the dirty file will look like an upstream overclaim. It is our checkout.

In-distribution, a TF-IDF trained on the target's own labels ties or beats Jev (README: 98.3/98.4, 98.6/99.4, 94.2/98.7). Out of distribution, the same lexical baseline falls and Jev does not: Ling-Spam 98.6% vs 73.0%, phishing 2024–25 91.0–93.6% vs 70.3%, modern-mail accuracy **0.9731 at HEAD** vs TF-IDF 0.7251. The working-tree 96.68% is not the cited number. The 97.3% in the TF-IDF modern row is "legitimate posts called legitimate", not accuracy.

Pane 1's sharper edge, not re-run here: the identical method scores 0.9857 trained on Ling-Spam's own labels, 0.7298 trained on email-dataset, and Jev's plain question scores 0.9857 with zero labels (`OUT_OF_DISTRIBUTION.md:28-41`).

**Regime, not a seat.** Bit 1 is YES in-distribution, so no seat. Bit 1 is NO under shift, so that is the regime a later candidate must be in. The repo calls the runs exploratory, each once, `jev-1.13.0`. The 98.3% question was written after reading 1,000 mistakes; the plain question scored 96.0%.

**Boundary.** No live call in this citation. No omp seam. Not a certified seat. The rerank 219-pair result remains thin and uncertified (`work/nev-rerank/live-receipt.json`).

## differential LLM-vs-Jev on jev-sec-bench injection 662 (2026-09-21) [live]

Incumbent arm RULE 14 required: same state + same InjectionBattery via
`upstream/typesafe-ai/system-one-adapter-python` @ `adffc2e` (v0.2.0, venv
synced to lockfile; adapter 40/40 fake-model tests green offline). Full 662,
cut @0.5, one request/row/arm, attended. Bar `work/nev-differential/
PREREGISTER-DIFF.md` @ `3d65229` + Amendment A1 @ `b5e6e1e`, both pre-spend.
Receipt `work/nev-differential/DIFF-RECEIPT.json` @ `57d30e9`.

- Jev `jev-1.13.0` CITED (committed `results/injection.json` @ `fdb16b9`):
  639/662 = 0.9653 (tp=250 fp=10 tn=389 fn=13). Zero new Jev calls.
- grok-4 via xAI custom endpoint: 558/662 = 0.8429, Wilson lower 0.8132,
  discordants arm-only 8 / jev-only 89, exact McNemar p=2.0e-18.
  590,696 in / 30,421 out tokens, mean latency 6.8 s.
- claude-haiku-4-5 via Anthropic: 579/662 = 0.8746, Wilson lower 0.8472,
  discordants 5/65, p=2.2e-14. 687,796 in / 27,388 out tokens, mean 0.94 s.
- OpenAI `gpt-4o-mini` arm INVALID: 401 on every attempt, key rejected;
  error rows on disk, never retried, never silent.
- Gate 4 (Jev exceeds both arms AND p<0.05 vs each) MET — seat certified for
  this corpus only (prompt-injection guard), never Jev in general.

**Boundary.** Public corpus may leak into any model's training. Single run,
fixed cut, no tuning. Cost in tokens reported, dollars not computed. No omp
seam; wiring is the next unit, not this one.

## jev-screen shape vs battery shape, full 662 (2026-09-22) [live]

P2 answers P4's counter-2 (is the seat citation overstated for the
instructions-only tool shape?). Bar `work/nev-screen-shape/PREREG-SHAPE.md`
committed `e494791` pre-spend; runner drives the shipped
`jevScreenTool.execute()` over all 662 bench texts (key via Infisical,
`/tmp/.tskey` absent on this machine — key-canonical-source rule).
Receipt `work/nev-screen-shape/SHAPE-RECEIPT.json` @ `189bf30`.

- Arm S (shipped tool, single instructions-only noul): 639/662 = 0.9653,
  Wilson lower 0.9484, confusion tp=249 fp=9 tn=390 fn=14, 0 failed rows,
  mean latency 148 ms. 662 calls, ~15 s wall, attended.
- Arm B (cited battery shape): 639/662 = 0.9653 (tp=250 fp=10 tn=389 fn=13).
- Agreement 660/662; discordants S-only 1 / battery-only 1; exact McNemar
  two-sided p=1.0. Gate 4 (agree>=630 AND p>=0.05 AND S acc>=0.95) MET —
  CITATION STANDS for this corpus. Criteria-as-prose == criteria-as-fields
  and the severity co-question moves nothing measurable here (2 rows split
  1-1).

**Boundary.** Single run, fixed 0.5 cut, `jev-1.13.0`. Billing unpriced
(jev-client returns no usage on the happy path — same gap as CH-P2c).
Seat scope unchanged: this corpus only. Non-author grade owed per closure
rules.

## jev-screen L2 listed + L3 fires, both directions (2026-09-22) [live keyless + offline]

L2 (`61f8fc0`): extension `.omp/extensions/jev-screen.ts` registered via
`.omp/config.yml` project scope; headless `omp --mode=rpc get_state`
shows `xd://jev_screen_ext_probe` in `data.systemPrompt[0]` by default,
absent under `--no-extensions`, nonce absent. `dumpTools` (11 built-ins)
confirmed blind to extension tools — not used as oracle. Zero model calls.
L3 (`65e34df`): D1 real muse session via host-tool data path (inline hostile
died in harness safety filter first — recorded): `tool_execution_end`
`ordered=false verdict=review reason=unconfigured NOT_RUN`,
`calledModel=false`, 90 frames, served 1. D2 loaded tool + injected asker
p=0.97: FLAG, fetch armed to throw, keys deleted. Zero live Jev calls.
Provisional L4 separately at `31c2eda` (3 keyed calls, flag + 2xpass-silent).

**Boundary.** NOT re-run: the RPC sessions, the driver model calls, the L4
keyed calls. Listed is not firing; L3 is not L4; seat is this corpus only.
Closes `jev-xio`.

## jev-screen provisional L4, keyed session (2026-09-22) [live]

Bar `PREREGISTER-L4.md @e800719` (19:22:47) predates spend `31c2eda`
(19:24:14). Driver `l4-drive.mjs`, 193 frames, 3 texts served in order via
host-tool path, 3 jev_screen executions under cap 8. H1 hostile → flag
p=0.99; B1/B2 benign → bare pass p=0.03/0.02, silence byte-exact; zero
review; calledModel=true throughout. Non-author grade (CopperLake): PASS
with residual — per-call latency/tokens not propagated by the tool
(details carry verdict only); session wall 49 s. L4-full requires
`latencyMs` in tool details.

**Boundary.** One session, three calls, one model version. Provisional only:
not fleet proof, not healthy-traffic silence at scale. Billing unpriced.

## foundation calibration transport onto vendored SDK (2026-09-22) [live]

P2 `jev-cp2` file 2 (`measure-framing-flip.mjs` verified already routed,
zero fetch matches). `run_calibration.py` urllib wire replaced by
`typesafe_sdk` (`TypeSafeClient`, `Noul`/`Choice` builders, `RetryPolicy`
mirroring MAX_RETRIES=2) at `81a1daa`; metrics, bins, sweeps, receipt
schema untouched; model default pinned `jev-latest` → `jev-1.13.0`.
Bar `foundation/PREREG-CALIB-SDK.md` @ `e66058b` pre-spend. Migrated run
`foundation/runs/20260922T020843Z.json`: 80/80 rows, 0 errors, ECE 0.0607,
Brier 0.0188, choice 19/20, thresholds ≥0.75 → 1.0 at 95% coverage.
Agreement vs cited `20260917T224444Z` receipt: 80/80 same verdict class,
fixture sha identical — the wire was NOT shaping results (AGREE).
Gate 20 freshness green on the new receipt; gates aggregate red only on
pre-existing unrelated stages (70 registry drift ×3, 80 lane-status arm).
Runner now requires the SDK clone venv python; `attempts` is SDK-opaque
(1 success, policy max+1 by construction on error).

**Boundary.** Single run, one SDK pin (`0ffd094`), one model id. Billing
unpriced.

**Replication (PearlAnchor, independent live run
`foundation/runs/20260922T021352Z.json`):** 80/80 same verdict class vs
the run above, ECE 0.0614, Brier 0.0195, choice 19/20, 0 errors, pinned
model. Two independent live runs plus the cited receipt all agree —
migration graded by replication, owed grade satisfied.

## jev-screen logging observer (2026-09-22) [live]

P2 `jev-v6j`: thin `work/omp-jev-screen-log/screen-log.mjs`
(`screenRecord` + `recordingScreen` wrapper) appending via dogfood-logger's
`JsonlDecisionLog` (0600, rotation, sha256 digest) — no new append
mechanics. Offline suite
`work/omp-jev-observer/test/screen-log.test.mjs` 4/4 (schema/hash-only,
identical-reference passthrough, malformed→review). Live proof
`proof-session.mts` over H1/B1/B2 (3 keyed calls): 3/3 rows, verdicts
flag p=0.99 / pass / pass, zero verdict changes, latencyMs present.
Privacy: text hashes only, never text (header note). Non-goals honored:
observes only, no blocking, no thresholds.

**Boundary.** One driven session, pinned model. Live log stays in /tmp,
never committed. Non-author grade owed.

## s1-rs own suite on Contabo via RCH (2026-09-23) [test]

AmberWillow, plan W7.2 (`jev-deep-kit-8q7`). `AbdelStark/s1-rs` @ `b916897`,
unmodified. `env -u TYPESAFE_API_KEY RCH_VISIBILITY=verbose rch exec --
cargo test -j 2 --workspace` from `s1-rs/`: RCH selected `contabo-4`,
`Remote command finished: exit=101`. 27 tests pass across five binaries;
the trybuild `ui` test fails because all 4 compile-fail cases
(`bool_without_noul`, `choice_fields`, `duplicate_labels`,
`too_few_variants`) compiled. The derive emits those errors in source
(`s1-derive/src/choice.rs:32`, `:105`; `questions.rs:87`) with
`MIN_CHOICE_OPTIONS = 2`, so four simultaneous misses point at the
environment (trybuild's nested `cargo check` under RCH's source mirror)
more than at s1-rs; undecided. Receipt
[`docs/demos/upstream-repro/s1-rs-rch-20260922.md`](docs/demos/upstream-repro/s1-rs-rch-20260922.md).
First run of the crate's test suite in this lane; the 2026-09-18 run
covered its two examples only.

**Boundary.** Keyless; no example, no live call, no local build. The
owner of the trybuild miss (s1-rs vs RCH) is dispatched to pane 3 as a
second-worker rerun plus one direct compile-fail case.

## jev-ultrafast under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group seat/benchmark). `browser-use/jev-ultrafast` @
`452c1ad`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, before first live call).
Fresh: `uv run pytest` 31/31; `check_guards.py` 21/21 vs real headless
Chrome; /tmp plant (validate_choice raise→pass) turns suite RED 7/24. T4
N=10 disclosed-authored states (prevalence 0.5): 8/10 correct, 0 invalid
executions, p50 193 ms / p95 ~386 ms; floors random ~0.20, majority 0.50,
keyword rule 0.50. T6 gpt-4o-mini arm 6/10 on the same states. T7 bins
reported with counts (directional only at N=10). T8 0 flips, one stably
wrong row over 5 exposures. T9 7/7 refuse incl. live-observed HTTP 520.
Spend: 32 Jev calls vs 25 cap (breach disclosed: unguarded T4 import in the
T8 harness re-ran T4; no further calls) + 10 gpt-4o-mini. Verdict:
BAR-PASS AT FLOOR, class SELF, SEAT HOLD (stable false advance on a
dead-end progress-like link; synthetic-only evidence). Receipt
[`docs/demos/upstream-repro/jev-ultrafast-w70-20260923.md`](docs/demos/upstream-repro/jev-ultrafast-w70-20260923.md).
Pane-6 verification: suite + guards re-run green; bar timing confirmed via
receipt-file mtime.

**Boundary.** No browser driven live; no production action; confidences
uncalibrated at N=10; gpt-4o-mini is a same-state probe, not the
browser-use incumbent.

## jev-align under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group seat/benchmark). `sutro-sh/jev-align` @
`49753df`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, ~6 min before first
live call). Corpus: UCI SMS Spam v.1, seed-7 stratified 20+20 (N=40,
prevalence 50% constructed, 13.4% natural); clone bundles ship unlabelled.
Fresh: pytest 127/127 + ruff clean; /tmp plant (precision off-by-one)
turns core tests RED 2 failures. T4 specified binary question 39/40 =
0.975 vs majority 0.500 (conjunct HOLDS) but ambiguity check fails
(top-quartile err 0.000 vs base 0.025; sole error confident-wrong p=0.02,
sampler would not resample it) → bar verdict REFUSED. Floors: majority
0.500, lexical rule 0.925 — neither ties. T6 vague question 0.750 vs
1.000 paired, McNemar b=5/c=0 (wording moves 0.25). T7 bins with counts
(middle empty). T8 0/10 flips either kind. T9 NA (official SDK path).
Spend: 101 Jev calls of 120 cap, p50 0.179s / p95 0.494s, jev-1.13.0 on
101/101 records. Verdict: REFUSED, class INCUMBENT, tier no-seat. Receipt
[`docs/demos/upstream-repro/jev-align-w70-20260923.md`](docs/demos/upstream-repro/jev-align-w70-20260923.md).
Pane-6 verification: suite re-run 127 green; clone state confirmed.

**Boundary.** GEPA never run (no reflection spend); multilabel/gateway
paths code-present only; sampler application unproven beyond these 40 rows.

## bicameral under W7.0 (2026-09-23) [live]

QuietHarbor, plan W7.2 (group tool; T4+T9). `AbdelStark/bicameral` @
`3bea244`, unmodified (`git status` clean at close). T4 bar committed first
(`notes/deep/dispatch/p6-w70-t4bars.md` @ `070efe6`, before 21:41:48 smoke).
Fresh: pnpm vitest 13 files 41/41; /tmp plant (forced-allow) turns gate
tests 3-fail RED. T4 N=40 authored corpus (DISCLOSED, questions tuned on it
→ SELF at best): 4 overt-exfil rows WAF-blocked at edge (deterministic,
all dangerous); scored N=36 (prevalence 0.444): Jev AUC 1.000, 0 FP/0 FN
vs regex 0.667 / majority 0.556 (McNemar b=12/c=0, p=0.0005). T7 bins
perfectly separated with counts. T8 0/10 flips both arms. T9: degrade path
proven for timeout/throw/429/key-absent, host survives — but malformed-200
+ high-risk degrades to ALLOW (answers.ts:3-10 coerces missing to 0): a
genuine fail-open hole, recorded unpatched (upstream tree). Spend 93/100
calls, p50 188ms/p95 420ms, $ unmeasured. Verdict: characterization only;
transferable piece is the degrade-to-pattern fallback, holed as noted.
Receipt
[`docs/demos/upstream-repro/bicameral-w70-20260923.md`](docs/demos/upstream-repro/bicameral-w70-20260923.md).
Pane-6 verification: suite re-run 41 green; hole mechanism read in-tree;
bar timing via row-file mtime.

**Boundary.** Authored clear-case discrimination only; adversarial phrasing,
heldout re-run, H-benches, $ cost, Pi-extension e2e all untested.

## W7.0 batch — pane 5 SunnyTiger (2026-09-23) [live]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p5.md.
# W7.0 EVAL sections — pane 5 group (STAGING: EVAL.md was reservation-held; pane 1 append)

## EVAL — jev-rerank-bench W7.0 (SELF)

T1–T8+T10 at `cd9a35b`. Committed cache re-scores byte-identically; live rubric reproduces cache 28/30 (bar ≥24/30, N=30 seed 20260923, $0.017876, p50 397.9ms/p95 992.7ms); floors beaten (top-1 10/30 nDCG 0.3811 vs live 15/30 0.4958); Cohere Pro tied (12/30, McNemar p=0.4531, $0.075). Live spend 45 Jev + 30 Cohere. Receipt: `docs/demos/upstream-repro/jev-rerank-bench-w70-2026-09-23.md`. NO-CLAIM beyond the 30 rows + cache re-score.

## EVAL — jev-benchmark W7.0 (FLOOR, seat REFUSED)

T1–T8+T10 at `daf02b3`. Live 52/60 in bar range [52,58]; majority floor 18/60 stated; one-pass lexical cascade 58/60 BEATS live Jev and committed 55/60 → class-A/B task, seat REFUSED for escalation-routing claims. Haiku substitute 49/60 (grok-4 route 404'd); McNemar p=0.146 n.s. T7 weakly observable (1.000-mass 36/56). Receipt: `docs/demos/upstream-repro/jev-benchmark-w70-2026-09-23.md`.

## EVAL — jev-agent-failure-benchmark W7.0 (FLOOR)

T1–T8+T10 at `4d46af7`. N=300 sample: Jev agent 111/139=0.799, Wilson LB 0.7243 > floor 0.1942 → T4 PASS. Lexical-first 0.554, no tie. gpt-5.4 NOT-RUN (401 + no in-clone backend); grok substitute 23/35 vs Jev 28/35, p=0.13 ns. ECE 0.0545 (n=139). 480 Jev calls ($0.1164). Receipt: `docs/demos/upstream-repro/jev-agent-failure-benchmark-w70-2026-09-23.md`.

## EVAL — typesafe-ai-benchmark W7.0 (SELF)

T1–T8+T10 at `e94fcda`. Live 7/7 fixture verdicts match (bar ≥5/7), 35/35 sub-verdicts, 7 calls ≈$0.000121, p50 219.5ms/p95 562.7ms. Floors below (9/12, 16/17, 4/6 vs 35/35). Qwen/Cerebras NOT-RUN (key not held). T7 not observable at N=7. 3× flips 0/28. Receipt: `docs/demos/upstream-repro/typesafe-ai-benchmark-w70-2026-09-23.md`.

## EVAL — awesome-typesafe W7.0 (catalogue PASS)

T1+T3 at `c2d5cf9`. 8/8 benchmark-claiming entries assessed: 7 clone-candidates + 1 catalogue-only (Judge-vs-Dimensions post). jevcal + Janus URLs resolve (cloned by sibling agents this wave). OpenJev link stale (redirects to SemIf — flag for catalogue owner). Zero Jev calls. Receipt: `docs/demos/upstream-repro/awesome-typesafe-w70-2026-09-23.md`.

## EVAL — jevcal W7.0 (T1–T3 earned, T4 proposed)

NEW CLONE abhixhek/jevcal@`ae8f314` (2026-09-18, MIT). pytest 24/0/0; plant turns RED. 8 claims (5 demonstrated, 2 partial, 1 aspirational). T9: 5 fault arms refuse as ProviderError. T4 bar proposed (400-row tickets.jsonl, PASS = status ok on all 3 questions + held-out ≥ target−0.02) — committed bar amendment required before any live call. Receipt: `docs/demos/upstream-repro/jevcal-w70-2026-09-23.md`.

## EVAL — Janus W7.0 (T1–T3 earned, T4 proposed)

NEW CLONE FirasSX914/Janus@`9cb66c4` (2026-09-18, Release 0.3.1, MIT). pytest 38/0/0; plant flips verdict. 8 claims recomputed keylessly (7 demonstrated, 1 partial). T4 bar proposed (Banking77 N=500 ±5pts of 77.80% AND WoS-200 ±5pts of 54.50%, ceiling $2.00) — committed bar amendment required before any live call. Receipt: `docs/demos/upstream-repro/janus-w70-2026-09-23.md`.

## W7.0 batch — pane 2 (2026-09-23) [test]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p2.md (d3d2239).
# W7.0 EVAL sections — pane 2 — 2026-09-23

For SunnyTiger to append to `EVAL.md`. This file is not `EVAL.md`. Agent Mail could not reserve it. Old receipts are leads. Live smokes below were not re-run by pane 2.

## jev-mcp @ 6ec5efc

- Re-run 2026-09-22: `npm test` → 9 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-mcp-w70-20260922.md`, commit `d12027d`.
- T9 fail, source: `dist/index.js:108` maps an unknown choice to `"unknown"` and still copies `confidence`. A missing key exits the process.
- Live smoke in that receipt was not re-run here. N=1 is a smoke, not a certification.
- Boundary: unit suite and the coerce line only.

## jev-review @ 57690af

- Re-run 2026-09-22: `npm test` → 13 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-review-w70-20260922.md`, commit `07041c2`.
- Clone source sends `jev-latest`. The pin in the receipt was applied in the harness, not in the clone.
- Live smoke not re-run here.
- Boundary: offline suite only.

## jev-router @ 86660a0

- Re-run 2026-09-22: clean archive `86660a0248eba0e4523f81645ac2925e9808c000`, `npm test` → 58 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-router-w70-20260922.md`, commit `5929bbf`.
- Production path sends `jev-latest` unless `TYPESAFE_DEFAULT_MODEL` is set. Live smoke not re-run here.
- Boundary: offline suite on a clean archive.

## jev-codex-router @ 8292b519

- Re-checked pin `8292b519659280884627a962c826ac7721136a64`, porcelain empty. Receipt `docs/demos/upstream-repro/jev-codex-router-w70-20260922.md`, commit `6aafeec`.
- `server/jev_server.py:717-718` turns a Jev exception into an astra route. Missing key at line 721 also becomes astra. Host stays up. T9 fail is that coerce.
- Live smoke N=12 not re-run here. No accuracy claim.
- Boundary: pin, cleanliness, and the coerce lines. No second paid call.

## fast-jev-compaction @ 6e1da50

- Re-run 2026-09-22: `npm test` in the dirty tree → 29 pass, 0 fail, exit 0. Lockfile not touched by this run.
- Receipt file `docs/demos/upstream-repro/fast-jev-compaction-w70-20260922.md` is inside `d64c2f1` (subject is pane 4's mechanism-transfer commit, author Josh). Not re-committed by pane 2.
- Live smoke in that receipt not re-run here. T9 in the agent's summary said no client deadline and missing key throws. Not re-derived in this section.
- Boundary: offline suite only.

## W7.0 batch — pane 3 TopazRaven (2026-09-23) [test]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p3.md.

## typesafe-sdk-js — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

`typesafe-sdk-js @ 66880cc` (v0.6.0). `M package-lock.json` pre-existing,
byte-identical before/after. `env -u TYPESAFE_API_KEY npx vitest run`:
189/189 pass, 0 skips, typecheck clean — exit 1 via 8 unhandled AbortError
rejections from native-transport timers. /tmp defect (validateQuestions
neutered) RED at `test/client.test.ts:383`. T9 4/4 vs local stub
(hang→APITimeoutError, 429→RateLimitError, malformed→TypeSafeError,
unset key→TypeSafeError). Class SELF. Receipt
`docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md`.
Boundary: no live calls; T1 cleanliness FAILS on pre-existing dirt.

## typesafe-sdk-python — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

`typesafe-sdk-python @ 0ffd094` (v0.7.1). Clean before/after.
`env -u TYPESAFE_API_KEY uv run pytest`: 671 passed, 52 skipped (17
dev-only, 35 keyless). /tmp defect (`if not key:`→`if False:`): 6
`test_missing_key` FAIL. T9 4/4 vs `127.0.0.1:18923` stub, host survives.
Class SELF. Receipt
`docs/demos/upstream-repro/typesafe-sdk-python-w70-20260923.md`.
Boundary: cassette-free run; async paths via suite only.

## system-one-adapter-python — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless)

Upstream @ `adffc2e` (v0.2.0), clean. `uv run pytest`: 229 passed
(cassette replay, `--block-network`). /tmp defect (×2.0 rescale): 1 fail.
T9: missing-key refuses at construction; 429/malformed map to typed
errors; hang hits the 25 s deadline with no output. Class SELF.
**Root copy `system-one-adapter-python/` @ `0bb819b` is STALE** (upstream's
own v0.1.4 tag-commit; upstream 2 releases ahead, 28 files differ).
Receipt `docs/demos/upstream-repro/system-one-adapter-w70-20260923.md`.
Boundary: live-provider behaviour not evaluated.

## s1-rs client transport — W7.0 SDK profile (TopazRaven, 2026-09-23, keyless, RCH)

`s1-rs @ b916897`, clean. `cargo test -j 2 -p s1 --features
backend-typesafe-rs` on contabo-1, exit 0: ask 4/4, decode 8/8, golden
5/5, policy 10/10, loopback 1/1, ui 1/1 (inner 4/4), doctests 2+1 ignore.
Golden 5/5 re-run by parent. Scratch-copy defect (serde case): exit 101,
2/3 golden RED. T9 5/5 loopback, all `S1Error::Backend`. Class SELF.
Contabo-4 compile-fail anomaly resolved by worker repair (`/dev/null` +
`.rustc_info.json`; re-run exit 0). Receipt
`docs/demos/upstream-repro/s1-rs-client-w70-20260923.md`. Boundary: no
live calls; scratch tree left outside jev pending manual removal.

## work/jev-client — W7.0 SDK profile + fix (TopazRaven, 2026-09-23, keyless)

Own client over vendored `@typesafe-ai/sdk v0.6.0`. Suite 29/0 + 8/0
(measure/uncertain). T9 found a nondeterministic Node host kill via leaked
SDK-timer AbortError (`dist/index.mjs:636`), ~1/3 of timeouts; Bun 2/2
survived. Fixed in `src/index.ts` (`guardedFetch` owns the timeout):
regression test failed pre-fix, green post-fix; Node 30/30 + Bun 30/30
exit 0; suites 38/0. Class SELF (transport only). Receipt
`docs/demos/upstream-repro/jev-client-w70-20260923.md`. Boundary: no live
calls; defect originates vendored-upstream.

## W7.0 batch — pane 4 MistyTurtle (2026-09-23) [test]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p4.md (foreman + sec-bench; phishing/spam to follow).
## foreman W7.0 (2026-09-23) [test]

Clone `foreman @ 2c43982` (thruwire, MIT). jev HEADs: bar `9e8199b`, run
`fcbb050`, receipt `679e5f4`. Receipt
`docs/demos/upstream-repro/foreman-w70-20260923.md` (+ frozen rows
`foreman-w70-rows-20260923.jsonl`).
Suite `PYTHONPATH=src uv run pytest tests/ -q` → 1 failed, 57 passed, exit 1
(lead 57/58 reproduced); /tmp plant (stuck_threshold 0.80→0.99) → RED.
T4 N=12 self-authored vignettes (labels frozen pre-call), prevalence 25%x4:
11/12 = 0.9167 CI [0.6152, 0.9979]; floors always-FINISH 3/12,
always-ESCALATE 3/12, lexical 12/12 → bar (lower-CI > floor) fails →
REFUSED class FLOOR. Latency p50 0.195 / p95 0.330 s; API unpriced. T6
haiku-4-5 via adapter: 9/12, McNemar p=0.5 (inseparable at N=12). T7 not
observable (single bin, zero negatives). T8 48/48 stable. Pane-4 re-runs:
suite, plant, floor row-by-row, incumbent tally.
Boundary: self-authored vignettes, no live Codex run, API cost unpriced.

## jev-sec-bench W7.0 (2026-09-23) [test]

Clone `jev-sec-bench @ fdb16b9` (Gaurav-Gosain, MIT, Go 1.27.1). jev HEADs:
bar `9e8199b`, receipt per commit. Receipt
`docs/demos/upstream-repro/jev-sec-bench-w70-20260923.md`.
`go test -race -count=1 ./...` green uncached; /tmp plant
(metrics_test.go:25 TP!=1→2) → FAIL TestConfusionCounts. T4 INJECTION n=662
prev 39.73%: 640/662 = 0.9668 CI [0.9501, 0.9791], AUC 0.9926, p50 191ms
p95 379ms; tokens 439330/23170 EXACT match committed. CODE n=400 prev 50%:
284/400 = 0.7100 CI [0.6628, 0.7540], pairs 178/200 reproduced. Floors beaten
on both (inj 0.6027/0.6329; code 0.5000/0.5625). T6 haiku-4-5 584/662 =
0.8822, McNemar p=2.6e-13 (injection only). T7 decile bins with counts
(inj ECE 0.0684; code ECE 0.1792). T8 flips 0 repeats; reword 6/150 + 2/120.
Verdict SPLIT: injection INCUMBENT (certified these-662-only), code SELF but
REFUSED (absolute 0.70 bar). Pane-4 re-runs: suite, plant, `ls cmd`
(runner-absence confirmed), all accuracies + token sums from fresh rows.
T3: 5 demonstrated, 1 partial, 1 disproven (`-bench all` runner absent).
NOT-RUN: code LLM arm; live ablation; RunAudit e2e (retries in receipt).
Boundary: public-corpus leakage caveat; single runs; fixed 0.5 cut.

## W7.0 batch — pane 4 MistyTurtle, phishing section (2026-09-23) [test]

Appended by pane 5 as sole EVAL writer. Source: pane-4 message (foreman + sec-bench already landed in 675ea42; spam still pending).

## jev-phishing-bench W7.0 (2026-09-23) [test]

Clone `upstream/anisselbd/jev-phishing-bench @ 1d56e8c` (no LICENSE). jev
HEADs: bar `9e8199b`, run 2026-09-23T03:38Z. Receipt
`docs/demos/upstream-repro/jev-phishing-bench-w70-20260923.md`. Corpus 2000
rows recounted. Status clean before/after. No committed suite; /tmp plant
(`registered_domain`->'') drops floor 0.9165->0.6055. T4 full 2000 calls
(1999 ok): verdict 0.6298 CI [0.6084, 0.6507], p50 195ms, $0.0769. Floor
same rows 0.9165 CI [0.9035, 0.9278] -> REFUSED class A. T6 haiku-4-5
400 shared rows 0.7475, McNemar p=1.3e-5 (incumbent better). T7 ECE 0.1611
observable. T8 flips ~2.4%, reword agree ~0.80. Pane-4 re-runs: status,
corpus count, committed metrics, raw tallies (1259/2000, 1257/2000,
haiku 299/400), analyzer (T4/T5/T6 lines reproduced keyless).
Boundary: one transient 520 row; public-corpus leakage caveat.

## W7.0 batch — pane 6 QuietHarbor, commit-miner section (2026-09-23) [live]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p6.md (skillranker still pending from pane 6).
## commit-miner — PENDING EVAL LANDING (receipt committed; section below for pane 5)

### commit-miner @977617e (W7.2 fresh, 2026-09-23)
- Seat (T1-T8+T10+T9): T2 full suite via RCH 37 pass/0 fail — tests.rs:799 failure from W7.1 (exit 101 on contabo-3+contabo-4) now PASSES on contabo-4 (full), contabo-2 (targeted, second-worker confirmation) and contabo-2 again (pane-6 unpinned rerun, exit=0); root cause was worker /dev/null poisoning, not the clone. Pinned contabo-1 attempts refused RCH-I001 (nothing ran). T2-plant NOT-RUN (earned four fields; RUSTFLAGS --cfg neutral, exit 0).
- T4 (prereg §commit-miner, jev-1.13.0): N=20 unauthored commits (Anil-matcha/awesome-jev-by-typesafe @d57f5ce, SHAs recorded, pre-labelled all-negative BEFORE first call; prevalence 0/20) → 0 FP (20/20 Metadata review, max p 0.14 @0.65) AND $0.00332 ≤ $0.0128 bar; p50 0.40s p95 0.71s over 52 paid calls (cap 60). Controls (disclosed-authored, ≥2-commit): SQLi→Security fix CWE-89 exact, XSS→Security fix CWE-79 exact.
- T5 prefix floor 1 FP (loses); T6 always-majority ties 0/20 (vacuous at prevalence 0); T7 single-bin → calibration not observable; T8 0/30 flips (max |Δp| 0.030); T9 refuses on timeout/429/malformed/key-absent (suite fresh-pass + live 403 in 0.2s), host survives.
- Verdict class SELF, seat NO-GO on this evidence: prevalence-0 draw cannot separate Jev from always-majority; adoption needs a mixed-prevalence public set. NO-CLAIM beyond the 20-SHA window + 2 disclosed fixtures. Clone untouched (porcelain empty, no commit).

## W7.0 batch — pane 4 MistyTurtle, spam section (2026-09-23) [test]

Appended by pane 5 as sole EVAL writer. Source: pane-4 message (phishing already landed; foreman + sec-bench in 675ea42).

## jev-spam-eval W7.0 (2026-09-23) [test]

Clone `jev-spam-eval @ 76ef183` (bitnovus, MIT). jev HEADs: bar `9e8199b`,
run 2026-09-23. Receipt
`docs/demos/upstream-repro/jev-spam-eval-w70-20260923.md`. Status: 2
pre-existing M results files only. No suite; /tmp plants (silent-degradation
finding + numpy RED). T4 4,878 rows $0.2474, all jev-1.13.0: S1 0.9780, S2
0.9848 (tp479), S4 0.9132, S5 0.9731 (tp296) — all recomputed by pane 4
from /tmp/w70 rows. Floors same rows: S1/S2 ties (p=0.31/0.91), S3/S4/S5
Jev wins (S3 floor cross-checked 0.7298 vs 0.7311). T6: S1/S5 ties, S2 grok
loses, S4 BOTH LLMs beat Jev (haiku 807/853 recomputed). T7 bins counted;
S4 single-class not-observable. T8 <=2.58% (pane-4 S1 recompute 3/50 0 vs
runner 2/500, same order). Verdicts: S1+S2 TIE/REFUSED, S3+S5 SEAT-vs-floor,
S4 INCUMBENT/REFUSED. NOT-RUN: phish 3-way (routes in receipt). ~$1.24
total. Boundary: single runs, public corpora, S1 500-sample, 17 dups.

## W7.0 batch — pane 6 QuietHarbor, skillranker section (2026-09-23) [live]

Appended by pane 5 as sole EVAL writer. Source: notes/deep/w70-eval-sections-p6.md.
## skillranker — PENDING EVAL LANDING (receipt committed; section below for pane 5)

### skillranker W7.2 (ROOT @a6f1ff0, 2026-09-23) — SELF, rate-PASS vs floors, gate-FAIL

Fresh run under the W7.0 standard (prior receipts as leads). T4 (N=12 existing synthetic cases, prevalence 10/12 = 83.3%, model jev-1.13.0, 39/40 calls, p50/p95 212/366ms): Jev wide-Choice top-1 8/10 = 0.800, mean loss 0.167 (2 false abstentions, 0 wrong picks) vs always-abstain 0.833/0.000 and lexical BM25-approx 0.583/0.600 — beats both floors beyond the prereg deltas (Δacc +0.200, Δloss −0.416 vs lexical). T8: 0/10 repeat flips, 0/10 reword flips. T7 bins with counts (n=11 asked). T9: codec 15/15 + contract 8/8; key-absent/malformed/timeout all refuse, host survives. T2: full suite build-RED exit 101 on contabo-1 AND contabo-3 (second-worker-confirmed; cause = RCH-synced tree missing tracked tests/fixtures/jev-tls pem/key, present locally and at HEAD — transfer gap, not code defect); fixture-free 8 targets 78 pass/0 fail/4 ignored (live-consent skips with reasons); plant NOT-RUN (RCH refuses /tmp projects). T3: 6 claims (2 demonstrated, 4 partial). Class SELF; promotion FAIL (0.800 < 0.90 sourced lane gate; synthetic split; n=10 positives). NO-CLAIM: not an sr product measurement; bar rate-PASS does not promote. Clones untouched.

## W7.0 batch — pane 2 RedMaple, new-clone section (2026-09-24) [live]

Appended by RedMaple from notes/deep/w70-eval-sections-p2-new10.md. Receipts at 40133aa. Ledger stop at f1dde64.

Lane: live where a call was made. Model pin jev-1.13.0 unless noted. Key via Infisical, never printed.

| clone | SHA | result class | live N | cost | receipt |
|---|---|---|---|---|---|
| Canny | f2c5e53 | FLOOR | 24 scored stops; receipt spend 96 Jev calls, 65800 in / 2016 out. usage.cost absent | not invented | docs/demos/upstream-repro/Canny-w70-20260923.md |
| neo4jev | d157bbe | FLOOR | 3 goals, 2/3; instrumented 10 hops, 168124 in / 4103 out | not invented | docs/demos/upstream-repro/neo4jev-w70-20260923.md |
| prism-liquidity-agent | f503db1 | withheld | smoke N=1, 4 calls, 2818 in / 388 out. Not re-run | not invented | docs/demos/upstream-repro/prism-liquidity-agent-w70-20260923.md |
| jev-curate | d1a3a05 | FLOOR | binary 422s. Corrected list shape: 30/30 HTTP 200, scores 0.98-2.03, clone rule still rejects 30/30. This session 32 calls, measured 18054 in / 1209 out | $0.000758 at README input rate, arithmetic, not an invoice | docs/demos/upstream-repro/jev-curate-w70-20260923.md |
| agent-desktop | a4a695f | withheld | smoke N=4, no execute | not an accuracy | docs/demos/upstream-repro/agent-desktop-w70-20260923.md |
| jev-drone | c0efd03 | FLOOR | 287 Jev calls; prevalence exit 2; no accuracy claim | disclosed-rate arithmetic in the receipt | docs/demos/upstream-repro/jev-drone-w70-20260923.md |
| typesafe-mario | ca22449 | UNEARNED | N=0. No ROM. Not downloaded | $0 | docs/demos/upstream-repro/typesafe-mario-w70-20260923.md |

Ledger port stopped, not built: python3 extract of 1145 labelled turns, ledger 1067/1145 loses to always-not-done 1108/1145, prevalence-check exit 3 WEAK. Receipt docs/demos/upstream-repro/canny-ledger-stop-20260924.md. Spend 0.

Boundary: nothing here is an omp L3 firing. Canny was not installed. prism had no wallet. mario had no ROM. jev-trader was not run. jev-curate upstream issue draft stays unfiled.

## W7.0 batch — pane 4 MistyTurtle, 8q7.8 + k9z.1 sections (2026-09-24) [test]

Appended by pane 5 as sole EVAL writer. Source: pane-4 message (earlier sections already landed).

## jev-deep-kit-8q7.8 structured criteria (2026-09-23) [test]

Variant `spam_structured_focus` vs incumbent `spam_generic_criteria`,
held-out lingspam parts 9+10 (580 rows, 97 spam), pinned jev-1.13.0, 580
bundle calls + 2 smoke. OOF AUROC (5-fold StratifiedKFold on logit,
3 fold seeds): current 0.9884, variant 0.9848, gap -0.0035 stable.
Focus-free negative (plain+focus minus plain): -0.0068, no gain. Accuracy
variant 0.9190 vs current 0.8741 (order disagrees with AUROC). Post-run
prevalence verdicts both WEAK (exit 3). Bar FAIL (any regression fails);
bead stays OPEN. Latency p50 169 / p95 415ms; cost unstated (no usage
captured). Receipt
`docs/demos/upstream-repro/jev-question-writing-w74-20260923.md`.
Boundary: one split, single run, author-overlap caveat (shapes fixed
verbatim, zero fitting here).

## jev-k9z.1 live rerank (2026-09-24) [test]

Rerank advisory, 219 transcript-mined rows, pinned jev-1.13.0, 2 full runs
(219 rows + 1660 passage-calls each). 219/219 ordered, top-1 75/219 =
0.3425, Wilson lower 0.2828 < lexical floor 0.3242 (71/219 recomputed
keyless) → bar FAIL; McNemar vs lexical 38/34 n.s. Latency p50 1073 / p95
5189 / max 7278ms. Tokens/dollars unpriced (JevScoreResult carries no
usage). L3 keyed: ordered=true 0.917/0.457 changed order; bad input
refused-no-throw at schema validation. Non-author re-score (TopazRaven):
75/219 confirmed, 0 mismatches. Bead stays OPEN. Receipt
`docs/demos/upstream-repro/nev-rerank-live-20260924.md`.
Boundary: one narrow corpus, single model, no TF-IDF ranker exists.

## jev-k9z.5 injection flag on real tool results (2026-09-24) [live]

jev_screen seat question (news-assistant `assistant`, cut 0.5), pinned jev-1.13.0, over 300 real
tool results from jev omp transcripts (0/300 contain injection, all read in full). Jev full
175/300 flagged = 175 FP, Wilson 0.527–0.638 vs ceiling 15 → bar FAIL; evidence-withheld control
12/300 (163 flags come from the persona). Haiku 4.5 via system-one-adapter 286/300; paired 6 vs
117, McNemar p=8.4e-28. Latency p50/p95: Jev 183/289ms, Haiku 773/1700ms. 900 calls, 0 failures.
No hook built; NEGATIVE_EVIDENCE R80. Bead stays OPEN for non-author label re-check. Receipt
`docs/demos/upstream-repro/jev-k9z5-flag-20260924.md`.
Boundary: zero attacks in corpus, so no recall measured; one run per arm; own transcripts only.

## jev-qip context-free injection flag, tool output vs public attacks (2026-09-24) [live]

jev_screen QUESTION, state `{user_message}` (no persona), jev-1.13.0, cut 0.5; bar 845addd before
calls. Plain: catch 213/263 (Wilson lower 0.758 < 0.80) → FAIL; tool false flags 12/300 (pass).
Criteria: catch 187/263 (lower 0.654) → FAIL; tool false flags 4/300 (pass). Haiku 4.5, same
states via adapter: 200/263 with 94/300 tool false flags, and 214/263 with 52/300. Paired McNemar
over the 662 rows: plain Jev 44 vs Haiku 22 (p 0.009); criteria 8 vs 36 (p 2.5e-5). 3,548 new
calls, 0 failures. No hook; NEGATIVE_EVIDENCE R82. Receipt
`docs/demos/upstream-repro/jev-toolout-flag-20260924.md`.
Boundary: public attacks are prompts with persona-relative labels (a proxy); one run per cell.

## jev-k9z.8 jev_rerank L3 on a public SciFact query (2026-09-24) [live]

Seam `.omp/tools/jev-rerank.ts` via project extension `.omp/extensions/jev-rerank.ts`, current tree,
omp 18.3.0. Five real `omp --profile claude -p --mode json` sessions (claude-sonnet-5 driver, oauth;
comparator keys unset); the model reaches the tool as `write xd://jev_rerank`. Query by a rule
committed before any call (25311f1): qid 36, BM25 top-20, abstracts cut to 500 chars. Keyed positive
(jev-1.13.0): `ordered=true calledModel=true`, the one relevant top-20 doc 11705328 moves from BM25
7 to 5, all 20 returned texts byte-identical. Keyed 1 and 31 passages: schema refusal, isError, no
throw, no Jev call (one earlier 31-passage session made no call: the model declined, prompt
reworded). Keyless: `ordered=false reason=unconfigured NOT_RUN`, input order, but details carry
`calledModel: true` (jev-t7oq). 20 Jev requests, 0 failed, ~$0.002 estimated (tokens not surfaced).
Rung L3. Receipt `docs/demos/upstream-repro/jev-rerank-l3-scifact-20260924.md`.
Boundary: one query, one run, truncated passages; MAX_PASSAGES truncation unreachable and untested; no L4, no latency.

## jev-k9z.9 rerank question on NevIR: run.py's one-passage Noul vs the shipped rubric (2026-09-24) [live]

Prereg `4cb97ed` before calls. NevIR test (1,383 pairs, 2,766 questions; `jev-rerank-bench@cd9a35b`
candidates, HF `6263585`), strict paired accuracy, jev-1.13.0, 3 runs per arm. Noul
(`work/rerank-nevir/nevir.py`, run.py's QUESTION imported): 927/929/918. Rubric through the shipped
`rerank()`+`liveAsker` (`tool.mjs`): 968/984/989; the upstream committed score-batch 984 reproduced
keyless (f1). LOSE in all 12 paired-bootstrap pairings (−0.028 to −0.051) → WORSE, no switch,
NEGATIVE_EVIDENCE R101. Tokens/question 1,100 vs 1,456 (0.76×). 33,192 requests, 0 failed, $0.89.
Receipt `docs/demos/upstream-repro/rerank-nevir-20260924.md`.
Boundary: one negation set, one pin, run.py's wording only; upstream's `jev-noul-pair` wording not re-run.

## jev-jy7t.1.3 PokéJev Stage B local battles (2026-09-24) [live]

Prereg `1a37ee4` before the bar arm; `jev-1.13.0`; pinned PokéChamp/Showdown environment and
Gen 9 OU Clock. Keyless selftest, zero-call control, live Random feasibility arm (19/20, 0 time
losses), then live Abyssal bar arm (200/200 rows, 0 harness errors, 0 time losses). PokéJev won
112/200 = 0.560 (Wilson 0.4907–0.6270), versus 79/200 = 0.395 for the zero-call control.
The preregistered `<0.70` KILL bar fired; tier-1 PASS required ≥0.84. Live-minus-control was
+16.5 pp, z=3.303, two-sided p=0.001. The run made 9,334 Jev calls, 33,273,577 input tokens,
and $1.397490234 estimated spend; decision latency p50/p95/max 1088/2424/5064 ms. Resolved
model ids: `jev-1.13.0`. Fallbacks: 271 no-credit API errors, 5 timeouts, 105 unknown-move
errors. Receipt `docs/demos/upstream-repro/pokejev-stage-b-results-20260925.md`, aggregate
`work/poke-jev/stage-b/receipt.json`. Bead stays open for non-author check.
Boundary: this is not a ladder result or calibration claim; no LLM comparator; no Metamon stretch
run; compact result and decision JSONL are committed for keyless re-score, replay HTML is not.
The API credit exhaustion occurred during the live arm and is disclosed in the receipt.

## jev-jy7t.1.6 MiniWoB AX observation pruning [prepared-not-measured]

Preregistration `dd04baf` precedes all Jev calls. The four arms (`full`, `code`, `jev`, `random`)
share the existing MiniWoB v1 planner and differ only in the AX observation passed to it; seeds
200 (dev) and 300 (held-out) are fixed in the preregistration. Harness selftest and scorer
selftest passed keyless; `ubs work/miniwob-ax-prune/ax_prune.py work/miniwob-ax-prune/score.py`
returned exit 0. Offline receipt commits: `9eab0c0` and refreshed `1d500a4`.

Boundary: this is PREPARED-NOT-MEASURED, not a live result. The live arm waits for the pane-5
MiniWoB v2 dependency. Once rows exist, `work/miniwob-ax-prune/score.py` reports per-arm success
counts/rates and the number of the 50 tasks succeeding in at least one arm for each split.

## jev-9gtw.2 OSWorld Best-of-N loss-depth dev and held-out audit (2026-09-25) [live]

Preregistration `0990712` preceded the four dev arms; the outcome-selected held-out audit manifest
was committed in `886c0d8`. Pinned OSWorld source `xlang-ai/OSWorld@b138d348256078fa634fc3b73567a7337c793e6b`;
task manifest `work/osw-bestofn/dev_slice.json` (N=60). Public instructions came from
`evaluation_examples/examples/<domain>/<id>.json`; result.txt contents, official rewards, and
grader output were not sent to Jev. Dev command:
`infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- env
OSW_STATE_FILE=var/agent-tmp/osw-bestofn-dev-43091/states.jsonl
OSW_SLICE_FILE=work/osw-bestofn/dev_slice.json
OSW_DEV_RECEIPT=var/agent-tmp/osw-bestofn-dev-43091/original.json
node work/osw-bestofn/dev_replay.mjs original`, repeated for each preregistered variant.

Dev live: `original`, `goal`, `neutral`, `noul`, 60 calls each, 0 failures; all 240 successful rows
resolved `jev-1.13.0`. Mean official reward / exact / input tokens / spend: original
`0.0166667 / 1/60 / 477,436 / $0.020052312`; goal
`0.0166667 / 1/60 / 480,164 / $0.020166888`; neutral
`0 / 0/60 / 481,756 / $0.020233752`; Noul
`0 / 0/60 / 511,156 / $0.021468552`. `goal` recovered one baseline failure but regressed one
baseline success; neutral and Noul recovered zero. No variant qualified under the strict
preregistered improvement rule.

The 57-task held-out audit was the complement inside the original 361-task failure-class union,
selected from prior Jev picks and floor outcomes; it reuses the R104 pool and is outcome-selected.
Its `original` run completed 57/57 calls, all `jev-1.13.0`, 456,282 input tokens, `$0.019163844`;
these numbers are **NOT-SCORED** and are not a held-out retest. A valid retest requires a different
OSWorld-Verified run set or step budget over all tasks, selected and committed before outcomes;
deferred until after Jericho. Combined spend was `$0.101085348`. Receipt
`work/osw-bestofn/dev_live_receipt.json`; report
`docs/demos/upstream-repro/osw-bestofn-loss-depth-dev-20260925.md`; R106 correction commit
`28747e4`. Boundary: no valid held-out variant, H5 terminal-status arm, MiniWoB, comparator,
different step budget, or deployment policy. `ubs work/osw-bestofn/dev_replay.mjs` exit 0.

## jev-9gtw.1 leaf evaluator Arm C (2026-09-25) [live]

Author IvoryCreek (pane 3); row appended by pane 1 at their request, with pane 1's non-author
recount. Prereg `docs/demos/upstream-repro/loss-depth-pokejev-leaf-c-prereg-20250925.md` @46d09b8
(before any C fit); dev receipt `work/loss-depth/pokejev-components/leaf-c-dev-v1.{json,md}`
@9ee47e5; held-out receipt `leaf-c-heldout-v1.{json,md}` @45607d3. Split
`decision-split-v1.json`, whole battles.

Dev: 95 battles, 2,060 rows. 5-fold GroupKFold AUC: code-only 0.6260 ± 0.0334, code + 3 Jev Nouls
0.6422 ± 0.0333, per-fold deltas +0.0170, -0.0025, +0.0272, +0.0288, +0.0109. (The dev table's
0.6652 / 0.6803 are in-sample fits, not dev estimates.)

Held-out, fit once on all dev rows, scored once: 95 battles, 2,274 rows (1,171 won / 1,103 lost;
172 fallback and 395 unusable rows excluded, 0 missing turns). Row AUC with battle-cluster
bootstrap (5,000, seed 20260925): A action-prior value 0.5642 [0.5357, 0.5929]; B chosen leaf
value 0.5663 [0.5264, 0.6075]; C code-only 0.7015 [0.6119, 0.7805]; C code + Nouls 0.7132
[0.6233, 0.7893]. Both C variants pass the preregistered bar (AUC >= 0.65, lower bound > 0.60).
Held-out Nouls: 2,274 `jev-1.13.0` calls, 1,439,630 input / 125,070 output tokens,
`$0.060464460`, 0 failures.

Pane 1 recount (`/tmp/verify-leafc.py`: leaf_c.py for data only, own fit, rank AUC and bootstrap):
point AUCs reproduce exactly (0.7015, 0.7132). Paired held-out delta, Nouls minus code-only,
+0.0117, 95% [-0.0089, +0.0310], 13.1% of resamples <= 0: **the Jev Nouls' contribution is not
distinguishable from zero**; the leaf fix comes from the code features. Each Noul alone: ko_now
0.566, danger_now 0.436, switch_needed 0.410 (the last two point the expected way). The
held-out features read Stage B replay HTML under `work/poke-jev/stage-b/replays-abyssal/`,
which is untracked (0 of 200 files in git), so a stranger cannot re-run this from a clone.

Boundary: no battle run; the receipt authorizes a separate battle preregistration only. No
comparator model, no causal or counterfactual claim, no claim that Jev improves the leaf.

## jev-jy7t.1.4 Jericho Jev-PUCT paired pilot (2026-09-25) [live]

Preregistration `docs/demos/upstream-repro/jericho-jev-puct-20260925.md` was amended before any
further Detective or Deephome live invocation (`2b63914`) after reading the experimental-design
and statistical-power skills. The initial three-seed independent-means plan was replaced by a
same-seed blocked pair: only matching Jev/uniform final `status=ok` rows form a score difference.
Jev Zork1 seeds 1–3 completed at `jev-1.13.0` (3,976 prior requests, 2,005,910 input tokens,
344,827 output tokens, `$0.084248220`); scores were 25, 44, 44. Keyless uniform Zork1 seeds 1
and 3 completed at scores 25 and 25; seed 2 hit the 3,600-second wrapper with an arm64
Jericho/Frotz worker segfault and has no final row.

The two complete pairs give differences `[0, 19]`, mean `9.5`, sample SD `13.435`. The
pre-registered `+5` smallest effect, two-sided `alpha=.05`, power `.80`, and paired t-test
recipe require 59 complete pairs (`dz=.3722`, raw `n=58.619`, achieved power `.8026`; SciPy
1.18.1 / statsmodels 0.15.0). Observed Jev and complete-uniform mean wall times project
24.712 hours for 59 pairs before overhead, so the powered count does not fit one attended day.
This is a descriptive pilot, not a confirmatory pass/kill.

Detective had already been launched before the hold: seed 1 `status=error`, seed 2 `status=ok`,
seed 3 `status=error`; it is unpaired and descriptive only. All Deephome rows are incomplete
without a final row; seed 2 was interrupted by its wrapper and seeds 1/3 were cancelled. No
partial or unpaired row is averaged into the original bar. Commits `af76109` (Zork rows),
`2b63914` (amendment + uniform pair rows), and `3f8ef5f` (bead evidence).

Boundary: no further live call after the amendment; no powered 59-pair continuation, no
Detective/Deephome paired analysis, no comparator, and no Laya endpoint. Uniform pair rows are
`work/jev-if/rows/zork1-uniform-s1.jsonl` and `zork1-uniform-s3.jsonl`; full raw run details and
NOT-SCORED conditions are in the receipt.

## jev-9gtw.4 MiniWoB v3 row provenance and harness-bug accounting (2026-09-25) [offline-verified]

Keyless test command: `env -u TYPESAFE_API_KEY -u JEV_API_KEY /tmp/jev-miniwob-jev/venv/bin/python work/miniwob-jev/v3_options_test.py` → **4/4 passed**. The new row-writer test drives `JevPolicy` with `FakeAsker("greedy")` and reads one JSONL row; it asserts the exact `sha256(jev_arm.py)` plus UTC `started_utc` and `finished_utc` with `finished_utc >= started_utc`.

The v3 report marks six harness-bug row files **NOT-SCORED**: `c7651c4` (`05:35:41Z`) dropped text-input candidates and `afd8a5b` (`07:25:58Z`) restored them; every run in that window typed 0 times. The 11 untracked `miniwob-jev-v3-dev-*.jsonl` copies remain untouched.

Boundary: no TypeSafe calls, no held-out run, no live lane, and no score is claimed. `foundation/gates.sh` and `foundation/gates.sh --selftest` both returned **ALL GREEN**. `ubs work/miniwob-jev/jev_arm.py work/miniwob-jev/v3_options_test.py` returned exit 1 with baseline Python findings in the two files; this is not a clean UBS pass.

## jev-t54m Fleet watcher stalled-wait reading (2026-09-25) [offline-verified]

Keyless command: `python3 -m unittest work/fleet-idle-watch/test_fleet_idle_watch.py` → **28/28 passed** (24 existing plus 4 stalled-wait/paging tests). Real screen/process fixtures remain the basis; the new cases cover a stale wait with only MCP/LSP helpers, a CPU-active child, and a session age of 599 seconds. A temporary mutation that ignored the session-age threshold classified the 599-second case as `stalled-wait`, so the test turned RED as required. `ruff format --check`, `ruff check`, and `ubs scripts/fleet-idle-watch.py work/fleet-idle-watch/test_fleet_idle_watch.py` returned 0.

One keyless `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/fleet-idle-watch.py --once` poll returned CI, judge, skills, and inbox lines. No `jev` tmux session was available, so no live pane state was observed; the hub watcher was not restarted.

Boundary: no TypeSafe calls, no Jev spend, no live stalled pane, and no hub restart. The remaining live-pane proof requires the fleet session to be present.

## jev-b0b4 New experiment row provenance checker (2026-09-25) [offline-verified]

Keyless tests: `python3 -m unittest work.row-provenance-check.test_row_provenance_check` → **5/5 passed**. The fixtures cover a valid experiment row, a missing code hash, a missing UTC timestamp, a pre-cutoff file, and a non-experiment JSONL file; the missing-hash fixture's first bad row is row 2. A source mutation that replaced the timestamp guard with `if False` made the suite RED. `ubs scripts/row-provenance-check.py work/row-provenance-check/test_row_provenance_check.py` returned exit 0, and `foundation/gates.sh` returned **ALL GREEN**.

The committed main-tree scan `python3 scripts/row-provenance-check.py` returned exit 0 and reported **5 experiment row files / 94 experiment rows**. It uses the first adding commit after `2026-09-25T09:00:00Z`, accepts either `code_sha256` or `run_py_sha256`, requires a valid ISO-8601 UTC timestamp, and reports the first bad row per file. Commits `fd02991` and `77a4324`.

Boundary: no TypeSafe API call, no paid spend, no model judgment, and no claim about row correctness; this validates only deterministic provenance enforcement and its fail-safe diagnostics.

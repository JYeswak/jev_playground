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

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


## jev-xvzi reach receipt binding @9f0daace [offline-verified]

- Changed `scripts/bar-reachable.py` to require an explicit `reach-mode:` declaration when producing a receipt with `--prereg`/`--items`; receipts carry absolute `prereg_path`, `prereg_sha256`, `items_sha256`, and computed `mode`.
- Changed `kit/experiment/run.py` to require `--prereg` for live runs and refuse mode mismatch, preregistration hash drift, path mismatch, or item hash mismatch.
- Verification: `python3 -m unittest scripts.test_bar_reachable kit.experiment.test_run` — **17/17**; `python3 -m py_compile scripts/bar-reachable.py kit/experiment/run.py`; `ubs` on all four changed Python files — **exit 0**; commit hook format check — **4 clean**.
- Boundary: no Jev API calls; this verifies the offline receipt policy only, not model behavior or live experiment outcomes.
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

## jev-5v4s Arm action-mix sanity checker (2026-09-25) [offline-verified]

Keyless tests: `python3 -m unittest work/arm-sanity/test_arm_sanity.py` → **6/6 passed**. Committed fixtures prove PokéJev r3 code vs stage-b mix-v1 exits 1, mix-v1 vs mix-v1-control exits 0, the c7651c4-window MiniWoB rows report `type=type arm=0.000` and exit 1 against the pre-window rows, the difference-only fixture (switch 0.750 vs 0.410) exits 1 without concentration, and too few eligible rows exits 2. A temporary mutation removing the offered-type filter made the explicit eligible-row test pass with 0 instead of exit 2, so the plant was RED.

Direct keyless commands reported the expected exit sequence `1, 0, 1, 2`; `ruff format --check`, `ruff check`, and `ubs scripts/arm-sanity.py work/arm-sanity/test_arm_sanity.py` were run. No TypeSafe calls or spend were used.

Boundary: no live arm, no model judgment, no comparator, and no Jev API call. The TESTS.md row is now updated; pane-1 non-author verification remains required before bead closure.

## jev-9gtw.1 leaf evaluator Arm C, r2 to r4 (2026-09-25) [oracle]

Supersedes the leaf conclusion of the Arm C row above (7fd80a3), whose code features used an
HP sum over replay-seen Pokémon that a live battle cannot compute. Author IvoryCreek (pane 3);
row by pane 1 with its non-author recount (`/tmp/verify-leafc.py`: leaf_c.py for data only, own
fit, rank AUC, 5,000-resample battle-cluster bootstrap, seed 20260925). Held-out split is the
same 95 battles, 2,274 rows (1,171 won; 172 fallback and 395 unusable rows excluded).

- **r2 battle (fb0f003), NOT-SCORED harness bug:** `run.py:439` used `r"(\\d+)%"`, which never
  matches digits, so candidates differed only in the action-type feature; the arm switched on
  1,518 of 1,532 offered turns (Stage B 41%). Zero Jev calls in the leaf.
- **r3 (d201a3f prereg, 4af5ce5 refit and held-out, 7ba9742 battle partial):** features a live
  battle can compute. Held-out code-only 0.6458 [0.544, 0.741], failing the 0.65 bar; code + 3
  Nouls 0.7175 [0.636, 0.788]; paired Noul gain +0.0717 [+0.0044, +0.1607]. Battle NOT-SCORED:
  977 of 982 offered turns switched, because one feature was the recorded action type
  (`leaf_c.py:237`) and none scored the opponent's side (R109).
- **r4 (c98a9d4 prereg with an action-ranking gate, 9fbe996 refit and held-out):** action type
  dropped, opponent HP remaining and HP differential added; model sha256 `ad8cd164…73c49b`.
  Keyless gates: switch rate 33/100 on recorded Stage B turns against the 41% reference (within
  the 10-point sanity band). Held-out code-only 0.8269 [0.7547, 0.8835], code + Nouls 0.8242
  [0.7539, 0.8820]; paired Noul delta -0.0027 [-0.0150, +0.0081], 67% of resamples <= 0. Pane 1
  recount reproduces every figure.

Reading: once the leaf sees both sides' HP, the three Jev Nouls add nothing measurable to
winner prediction. r4 is the third read of this held-out split (each round preregistered before
scoring, each change driven by a harness or design defect found in battle, not by held-out
numbers), so its 0.83 is optimistic by an unknown amount. Spend across r2 to r4: none on
TypeSafe (held-out Nouls came from the cached rows of 45607d3).

Boundary: no scored battle exists for any leaf arm. Winner AUC does not certify action ranking;
the next battle must check its action-type mix against the reference arm after its first rows.

### r4 supervised code-only battle partial — `NOT-SCORED` (commit `50c30a7`)

The supervised `leaf-c-r4-code` process wrote 991 decision rows and stopped at
the existing interim marker after the action-mix gate. Stop-time reading by pane
1 at `2026-09-25T09:39:29Z`: 245 eligible decisions, offered-switch rate
`0.078` versus the Stage B reference `0.362`, absolute difference `0.284`,
checker exit `1`. After workers drained, the final 991-row file had 415
eligible decisions and the keyless checker read switch `0.089` versus `0.362`,
absolute difference `0.272`, exit `1`; the child footer was `exit_code=1`.
Both readings fail the preregistered `0.10` band. The arm is `NOT-SCORED`, not
a battle result. Receipt:
`docs/demos/upstream-repro/loss-depth-pokejev-leaf-c-r4-partial-20250925.md`.

Keyless autopsy: `work/poke-jev/player.py:248-262` sends both move and switch
candidates through `leaf.step(orders[a], o_orders[o])`; the simulator switches
before the opponent action and applies damage to the active Pokémon
(`pokechamp/poke_env/player/local_simulation.py:440-454,475-482,500-512`).
`player.py:74-85` and `battle/run.py:447-478` carry both sides' post-action HP
into the score. The failure is action-mix mismatch, not omitted opponent reply.
No new leaf Noul calls were made; the prior held-out Noul delta was about
`-0.003`, so this leaf line is parked. Boundary: no battle win rate, Wilson
interval, or Jev-vs-battle claim; no continuation of this arm.

## jev-ztp9 MiniWoB in-process arm-sanity stop gate (2026-09-25) [offline-verified]

Keyless `v3_options_test.py` → **8/8 passed**. A fake click-only Jev reaches four eligible decisions, returns arm-sanity exit 1, and writes an `arm_sanity_stop` row with the checker output and counts. Restarting a stopped output refuses with exit 5 unless a tracked continuation note is supplied. A resumed gate seeded with 150 prior rows triggers at the 50th new row (200 eligible total). `scripts/arm-sanity.py` is loaded in-process from its one source; no logic is copied. The current no-flag selftest stdout/stderr and exit code match the pre-gate `jev_arm.py` at `4ad081d`. Mutations ignoring checker exit, restart refusal, or prior-row seeding are RED.

Boundary: no TypeSafe calls, no Jev spend, no live MiniWoB run, and no claim about model behavior. TESTS.md registry row is updated; pane-1 non-author verification remains pending.

## jev-e3on README stranger run — `JYeswak/jev_playground@108c22c` (2026-09-25) [test]

From a fresh GitHub clone at `108c22c1f97c8affc57696b33d9b25b5232024b9`, the generator
ran 82 unique commands extracted from README fenced blocks and inline command spans,
preserving all README line occurrences in
`docs/demos/upstream-repro/stranger-run-20260925.md`. The child environment had a
clean `HOME`, only the permitted tool PATH, and no API-key variables. Result: 71
commands exited 0 and 11 exited nonzero. The table records exit code, wall time,
same-line quoted-number containment, failure class, and first error line.

Reproduce with:
`env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --out docs/demos/upstream-repro/stranger-run-20260925.md`.

Boundary: no Jev or comparator request was authorized or sent; README.md was not
edited; the command-output number check is textual containment, not semantic
recalculation; nonzero rows are classified in the receipt for pane-1 routing.

## jev-3e2i SST-5 free incumbent and row-provenance repair (2026-09-25) [live]

The free comparator cell `nex-agi/nex-n2.5-mini:free` completed **500/500 SST-5 rows** after
one permitted resume pass: 6 initial `TypeSafeAPITimeoutError` rows were retried, yielding
500 answered, 0 failed, 6 zero-mass, and 506 retained attempt records. `score.py` self-check
passed; Jev was the preregistered MAE-sign-test **WIN/HOLDS** against all three committed Jev
runs (`p=6.63e-37`, `2.51e-35`, `1.83e-36`). The cell used 506 requests, 82,666 input
tokens, 550,574 output tokens, and $0 OpenRouter spend. Receipt:
`docs/demos/upstream-repro/openrouter-incumbents-20260924.md`; rows commit `9195999`.

The subsequent keyless provenance repair is in `869aa44` (runner writes `run_py_sha256` and
`recorded_at_utc` on every appended row), `1d6de07` (success and failure-row tests), and
`66fac9b` (SHA-pinned exemption for the already committed pre-provenance rows; rows were not
rewritten). `python3 scripts/row-provenance-check.py` reports 6 experiment files, 137 rows,
and 2 exempted files. The registered runner suite reports **14 tests, OK**.

Boundary: no other SST-5 set, comparator model, paid comparator, or TypeSafe call was run in
this repair pass; no paid comparison was attempted. The six exempted legacy rows remain
unmodified and are not evidence that future runner output may omit provenance.

## jev-e3on README stranger run — second pass at `JYeswak/jev_playground@ee4f0b3` (2026-09-25) [test]

The fresh-clone rerun recorded in
`docs/demos/upstream-repro/stranger-run-20260925.md` used clone
`ee4f0b3051cf340fb0914f9b7431def639141b0d`, a clean `HOME`, and no API-key
variables. It ran 82 README command rows: **72 exited 0, 9 were nonzero, and
1 was a TEMPLATE**. The nine nonzero rows are listed below; L193 is the
README's documented expected-nonzero claim-check bar, and the other eight are
named prerequisites or keyless `NOT_RUN` rows:

- L160: keyless `NOT_RUN`; `component_eval --heldout` lacks the named
  `pokechamp@0f84c46` checkout.
- L193: expected nonzero `FAIL`; `jev-claim-check/score-close.py` is the
  documented failing-bar command.
- L224: keyless `NOT_RUN`; `measure-framing-flip.mjs` had no TypeSafe key.
- L233,262: named prerequisite; `br` was not on PATH.
- L233,239,262: named prerequisite; portable foundation gates require `br
  sync --import-only`.
- L235,261: named prerequisite; normal foundation gates require `br
  sync --import-only`.
- L243: named prerequisite; `gh` was not installed.
- L249,264: named prerequisite; `omp` was not on PATH.
- L256: named prerequisite; `quickstart.sh --mine` had no session logs.

Boundary: **0 API requests**; no Jev, OpenAI, Anthropic, xAI, or OpenRouter
request was authorized or sent. The quoted-number check remains textual
containment, not semantic recomputation. The TEMPLATE command was listed and
not executed.

## jev-u6qc Decision-log provenance enforcement (2026-09-25) [offline-verified]

Keyless tests: `python3 -m unittest work/row-provenance-check/test_row_provenance_check.py` → **14/14 passed**. Decision/action rows are detected and validated; checker-owned `work/row-provenance-check/fixtures/` is skipped so deliberately failing future fixtures cannot trip the live scan; committed legacy decision logs remain SHA-exempted without rewriting. The live checker exits 0 and reports **4 experiment row files / 3273 rows / 2 decision logs / 4 exempted files**. A mutation skipping decision-log detection turns the suite RED. No TypeSafe calls or spend.

Boundary: no model judgment, no live Jev call, and no row content was rewritten. The TESTS.md registry row needs the 12/12→14/14 count update; pane-1 non-author verification remains pending.

## jev-30q7 Revoked TypeSafe key guard (2026-09-25) [offline-verified]

Keyless fake-key tests: `python3 -m unittest work/key-status/test_key_status.py` → **6/6 passed**. The revoked fingerprint command returns exit 3 without printing the key or full hash; the Best-of-N, gate-question, and MiniWoB live entrypoints all refuse the same fake revoked key before requests. No real key or Infisical invocation was used.

Boundary: no TypeSafe call, no live runner, no spend. TESTS.md rows and pane-1 non-author verification remain pending.

## jev-9gtw.4.1 MiniWoB v3 post-rotation run sheet (2026-09-25) [offline-verified]

Keyless run: `bash work/miniwob-jev/run-after-rotation.sh --fake --steps quoted,date_time` completed two episodes per selected step and ran row-provenance validation for each output. The revoked-fake plant returned exit 3 at step 1 before writing rows. The `--live` path is wired to the preregistered isolated sections and combined 400-404 held-out command, with `scripts/key-status.py` before every step.

Boundary: no TypeSafe calls, no live runner, no spend. TESTS.md row is registered; pane-1 non-author verification remains pending.

## jev-ljle README stranger regression gate (2026-09-25) [test]

The nightly gate is in `.github/workflows/stranger-run.yml`. `scripts/stranger-run-jev-playground.py`
now accepts `--source` for the checked-out repository, `--expect` for the committed
`docs/demos/upstream-repro/stranger-run-expected.tsv`, and `--selftest`. The expectation has 82
rows and was generated from the f2e61b0 receipt; it pins outcome classes and stable cause markers,
not wall time or commit SHA. The planted selftest passes and names
`python3 work/stranger-planted/untracked-input.py` as a new README row.

The clean baseline checkout `ee4f0b3051cf340fb0914f9b7431def639141b0d` completed the full local
`--source` run with **`EXPECTATION PASS rows=82`**. After fixing the real CI portability drift
(missing `uv`, then the hard-coded MiniWoB venv), workflow dispatch
**`36135948301`** ran on checkout commit `514502285d4e4c0bb75dcbca2286e1dd0d718e3d` and passed
in **7m18s**. The uploaded receipt reports **82 rows, 72 exit 0, 9 nonzero, 1 TEMPLATE**; its
nine nonzero rows are the committed expected claim-check bar, keyless/no-key results, and named
environment prerequisites. The CI job installs `uv`, uses `--source "$GITHUB_WORKSPACE"` rather
than cloning the target repository, and uploads the receipt artifact.

Boundary: this is keyless/offline CI evidence only; **0 Jev/API requests and $0 spend**. The
workflow does not prove the substantive judged results in the README. Earlier RED dispatches
36131647900 and 36134076882 were retained as regression evidence: they caught a changed failure
cause and the hard-coded MiniWoB venv before the final green run.

## jev-3e2i STS-B free cell partial (2026-09-25) [live]

`nex-agi/nex-n2.5-mini:free` was run against the public STS-B dev pairs used by the committed
`jev-jzzs` Jev arm. The cell stopped at the account-wide free-budget reserve after **380/1,500
unique rows**: 352 answered and 28 failed (24 timeouts, 4 not-found errors); 5 answered rows
had zero-mass probability maps. Every row carries `run_py_sha256` and `recorded_at_utc`.

The first session hit the 3,600-second command deadline at 210 retained rows. A second main pass
used the remaining-20 cap and stopped at its 170-request cap. The account counter ended at
975/1,000 used, 25 remaining; the next reset is **2026-09-26T00:00Z**. Row SHA-256:
`c4a6d5cae591ea2f9c856e0e74b8dbfd83748bb5bc5fec7737c3d62ad087fece`. Receipt and rows:
`006aef1`.

**No `score.py` run and no comparator verdict.** This is a PARTIAL cell that must resume after
the reset until all 1,500 rows exist. Boundary: no other comparator model or set ran in this
continuation; no paid call was attempted.

## jev-gbdb README stranger status and pane-1 pager (2026-09-25) [test]

Keyless fixture tests use recorded GitHub JSON for stranger runs `36135948301`,
`36134076882`, `36131647900`, and `36131541214`, plus the recorded failed-log
mismatch line. `scripts/ci-main-status.py` now reports the newest completed
`workflow_dispatch` or `schedule` run, its age, first `row changed`/`new README
command` mismatch, `STALE` after 36 hours, and `NOT_RUN` when no completed run
exists. `scripts/fleet-idle-watch.py` prints the line and pages pane 1 once per
failed run id, including stale failures; failed sends remain retryable.

Evidence: `python3 -m unittest work/ci-main-status/test_ci_main_status.py
work/fleet-idle-watch/test_fleet_idle_watch.py` → **52/52 passed**; the wrong
workflow plant is RED, and watcher pager tests cover fresh failure, stale
failure, duplicate suppression, failed-send retry, success, and NOT_RUN.
`python3 scripts/ci-main-status.py` on this machine printed
`README stranger nightly: success 36135948301 20m ago`. A real
`python3 scripts/fleet-idle-watch.py --once` printed the same nightly line
without paging because the newest run was successful.

Boundary: **0 Jev/API requests and $0 Jev spend**; this change observes GitHub
workflow status only and does not claim the README's substantive judgments.

## jev-9gtw.2 valid 100-step Best-of-N preflight [live NOT_RUN]

The preregistered retest from `667b447`/`8208af3` was **not run**. The fixed
`work/osw-bestofn/heldout_valid_slice.json` manifest has 361 tasks, but
`ouroboros_task_final.json` is exactly `{}` (2 bytes) for
`chrome/3720f614-37fd-4d04-8a6b-76f54f8c222d` in both pinned Ouroboros packages.
The allowed acting-evidence state therefore cannot be constructed for that task without
reading excluded outcome/manifest files. This is the preregistered state-construction
hard stop, before any Jev call.

Receipt: `work/osw-bestofn/valid_preflight_receipt.json`
(`fd4b03dd765b3107ee23386628f8f71e1a088a7d5882902b1fe8f1fef72e89bc`).
**0 live calls; $0 spend; no rows or bar score.**

Boundary: no Best-of-N selection, official-reward join, comparator, or Jev result is claimed.

## jev-pvdp readout-5 live preflight [live NOT_RUN]

The rotated key preflight passed twice (`KEY: OK (not on the revoked list)`), and the
frozen extract was committed as `55d30a4` before the live attempt. The exact live command
then refused before an API call because `readout5.py ready` found
`labels-5-1.jsonl` not committed and clean. The required label files
`labels-5-1.jsonl`, `labels-5-2.jsonl`, and `labels-5-adjudicated.jsonl` are absent from
the workspace; they were not authored or inferred.

Receipt: `work/gate-question-gap/live_preflight_receipt.json`.
**0 Jev calls; $0 spend; no flags-5 rows, readout5 score, or verdict.**

Boundary: the frozen extract and API-key status are proven, but the preregistered
non-author labels/power gate remains unmet, so the live pass is not claimed.

## jev-9gtw.4.1 Isolated MiniWoB v3 live pass (2026-09-25) [live-verified (N=889)]

The approved Infisical run completed all six isolated steps from a clean archived root. Receipt: `work/miniwob-jev/live-20260925/receipt.json`; committed rows: `work/miniwob-jev/live-20260925/rows/`. Counts: quoted 16, date_time 10, page_text 35, color 12, drag 87, none 11; **171 rows, 889 Jev calls, 2,199,227 input tokens**. Recorded input-token billing at $0.042/M gives **$0.0924 estimated Jev spend**; no comparator spend. Every step printed `KEY: OK` and passed row provenance. No 401/402 occurred. The combined held-out step was not run.

Boundary: the runner receipt does not record a resolved model version, so no model-version claim is made; no model-quality ruling is made. The live run used the clean archived root to avoid stale untracked output rows in the shared checkout.

## jev-cni7 Rule 13 five-clone census (2026-09-25) [test]

Pinned upstream rows and keyless outcomes:

| Clone | Owner / license | Exact command or blocker | Result |
|---|---|---|---|
| `killmyidea@bc853421f2eb6f17da435621896dd6cd881a051c` | monteduro / no `LICENSE` file | `env -u TYPESAFE_API_KEY -u JEV_API_KEY npm test`; `env -u TYPESAFE_API_KEY -u JEV_API_KEY npm run typecheck` | Vitest **7 files / 48 tests passed**; TypeScript build passed. |
| `OneVOneJev@365b339d04446836352687b3650762106ea37f17` | emrickgarrett / no `LICENSE` file | `env -u TYPESAFE_API_KEY -u JEV_API_KEY npm run build` | Shared, server, and client builds passed. The pinned tree contains **0 test files**, so there is no upstream test suite to run. |
| `metamon@0a00a759c9a4382a2877088d828302ec294a05a5` | UT-Austin-RPL / MIT (`LICENSE:1`) | Not re-run: `work/poke-jev/README.md:53` records the released-Metamon **B stretch as pending**, and the pinned tree has no committed test-like paths. | Named refusal: the existing PokéJev work has not run this stretch arm; no keyless Metamon suite exists in the pinned tree. |
| `pokemon-showdown@e64915c0eab066db1d3e732b1280386468dd7415` | jakegrigsby / MIT (`LICENSE:1`) | Not re-run: PokéJev already pins and runs this fork (`work/poke-jev/README.md:23,35`; `docs/demos/upstream-repro/pokejev-stage-b-results-20260925.md:20-27`). | Existing PokéJev Stage B ran its keyless selftest, local server, 200-battle control, random feasibility arm, 200-battle live arm, and score. This census adds no duplicate run. |
| `skillranker-tip@2a16486239a5fba90e46e62f49ea92cba46bb917` | Dicklesworthstone / MIT + OpenAI/Anthropic Rider (`README.md:15`) | **Refused before execution:** this pane's OpenAI model is covered by the Rider restriction in `AGENTS.md`; it forbids executing, testing, analyzing, or indexing this clone. | No command run and no claim about the clone's suite. |

For `killmyidea`, the policy tests read `src/lib/evaluate.test.ts` (composition, malformed
responses, goal-specific dimensions, and the clarity gate) and `src/lib/scoring.test.ts`
(normalization, weighted averages, ties, and KILL/FIX/SHIP thresholds). In a sanctioned scratch
copy, flipping `needsDetail` from `< LOW_CLARITY_WARNING` to `>=` made
`npm test -- --run src/lib/evaluate.test.ts` go **RED: 2 failures / 10 tests**; the scratch
source was restored and `cmp` confirmed `evaluate.ts` byte-identical to the clone. The pinned
clone itself remained clean.

Clone status after this census: `killmyidea`, `OneVOneJev`, `metamon`, and `skillranker-tip`
printed no status lines. The PokéJev Showdown clone was already dirty and remains unchanged:
` M config/chat-plugins/mafia-logs.json`, ` M config/chat-plugins/seasons.json`, and
`?? config/custom-formats.ts`. The untracked format is the PokéJev local format copied by
`work/poke-jev/serve.sh`; this census did not clean or overwrite another agent's files.

Boundary: this census made **0 Jev/API requests and $0 spend**. The cited PokéJev Stage B
receipt is a separate prior live run; it reports `jev-1.13.0`, 9,334 calls, and 33,273,577
input tokens. No Metamon stretch battle, paid comparator, ladder run, or skillranker execution
is claimed here.

## jev-9gtw.2 amended OSWorld Best-of-N retest preflight (2026-09-25) [NOT_RUN]

Verified amendment `c1131b9` before any live call: the effective task universe is `N=360` after
excluding `chrome/3720f614-37fd-4d04-8a6b-76f54f8c222d`; newline-joined effective-ID SHA-256 is
`e838ec31f15b515f2f2cd04c705a8575bff95b6ca50ae0fb40da3f250d0509fc`. The pinned-source preflight
then found an unplanned missing official row: in
`razzant/ouroboros-osworld-verified-sonnet46@0e8ad516a4eeaa586607ead400429885814e7633`,
`multi_apps/6d72aad6-187a-4392-a4c4-ed87269c51cf` has neither `ouroboros_task_final.json` nor
`result.txt`; the c1 directory has `ouroboros_task_final.json` exactly `{}` and `result.txt`.
Under the committed stop rule, the official result cannot be joined unambiguously, so the run
stopped **before Jev**. Receipt:
`work/osw-bestofn/live_preflight_receipt_r3.json`.

Exact preflight command: `python3 var/agent-tmp/osw-bestofn-r3-360/build_states.py`. No API key
was used, no Jev request or response exists, no rows or bar score were produced, and no task was
replaced. Boundary: a new input-only amendment is required before any live call can be made.

## jev-9gtw.2 exhaustive OSWorld presence preflight (2026-09-25) [test]

Commit `f256089` supersedes the one-task preflight with one input-only rule over all 360
effective IDs: in both pinned packages, require a structurally non-empty
`ouroboros_task_final.json`, structural acting evidence (`loop_outcome.final_text` and a non-empty
`loop_outcome.trace_refs.tool_call_refs`), and a present `result.txt`; exclude the task if any
condition is false in either package. `uv run python var/agent-tmp/osw-bestofn-r3-360/exhaustive_preflight.py`
scanned 360/360 rows with 0 scan failures, excluded 23, and retained 337. Receipt:
`work/osw-bestofn/live_preflight_presence_r3.json`, SHA-256
`9f7f5d2e26d3f64f5d11b10e2057a509cf846dcd40401d00b719e8a0063cb153`; retained ID-list
SHA-256 `c2f320a71b86a6b35ae66dbdb4d2fb9d368aee181b21787f149b48516440aaf2`.

Boundary: the scan read only pinned path metadata and final-file structure needed for presence or
emptiness booleans; it did not read `result.txt` contents, official outcome values, rewards,
success/status fields, or any Jev response. Jev calls, scoring, and the bar remain **NOT_RUN**
pending non-author receipt verification.

## jev-9gtw.2 amended OSWorld Best-of-N live selection (2026-09-25) [live-verified (N=337)]

After non-author verification of `f256089`, key status passed with
`infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- python3 scripts/key-status.py`.
The amended state/floor build completed keylessly with
`uv run python var/agent-tmp/osw-bestofn-r3-360/build_states.py`. Guard commit `f167936` refused
the planted 336-task floor mismatch (exit 2) and accepted the valid 337-task floor/state pair:
both sorted task-ID digests are
`c2f320a71b86a6b35ae66dbdb4d2fb9d368aee181b21787f149b48516440aaf2`, and the state order matches
the `seed=20250925` permutation.

Live command:
`env OSW_STATE_FILE=var/agent-tmp/osw-bestofn-r3-360/states-goal-337.jsonl OSW_FLOOR_RECEIPT=var/agent-tmp/osw-bestofn-r3-360/floor-337.json OSW_LIVE_RECEIPT=work/osw-bestofn/live_receipt_r3.json OSW_LIVE_ROWS=work/osw-bestofn/live_rows_r3.jsonl infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- npx tsx work/osw-bestofn/live_select.mjs`.

Pinned model `jev-1.13.0`; `337` calls, `12` answer failures, `3,713,209` input tokens,
`13,325` output tokens, `$0.155954778`, wall time `60.127s`. The independent score check
recomputed the 337 row choices against the frozen keyless floor: selected reward sum
`296.43182811259345`, mean `0.8796196679898916`, exact-task count `283`, delta versus best
single `-0.020642468334476027`, and exact McNemar `b=2,c=8,p=0.109375`. This is a loss to the
best single comparator on the retained universe, not evidence of a routing win.

Receipts: rows
`work/osw-bestofn/live_rows_r3.jsonl` SHA-256
`66ea5c2c897b8bbeceb897bead74bfa05554486790ada9ddd2d18a39a0e335c0`; live receipt
`work/osw-bestofn/live_receipt_r3.json` SHA-256
`dc9e7504e0f667de690c94c080c1b8c4c3b59bd8d4ce271493396398568b3094`; independent score check
`work/osw-bestofn/live_score_check_r3.json` SHA-256
`1bf117202c14610d2f7d6bcd103935a7adcda77c4f48f845be71abc159af0173`.

Boundary: every result above covers the retained `337` tasks after the exhaustive presence rule,
not all `361` base IDs. The 23 rule exclusions plus the initial excluded ID are not silently
replaced. No paid comparator, second model, significance claim beyond the preregistered exact
McNemar result, or full-base-universe result is claimed.

## jev-9gtw.2 post-run input-limit audit (2026-09-25) [test]

The updated Rule 15 feasibility checker was run against the exact 337-task state file with the
484-byte choice question:
`uv run python scripts/jev-state-size.py var/agent-tmp/osw-bestofn-r3-360/states-goal-337.jsonl --question-bytes 484`.
It classified 324 requests as `FITS`, 10 as `NEAR`, and 3 as `OVER`. All 12 live failures were
HTTP 400 `max_tokens_exceeded`; the original live row set was not changed or rescored after this
audit. The result therefore remains an observed retained-universe run with 12 input-limit
failures, not a clean 337/337 feasible-request run.

The live receipt was updated with this audit:
`work/osw-bestofn/live_receipt_r3.json` SHA-256
`7154c9beef9c04f2da76d3101750dd6b3a38460b4c33e05025e76d00d778611f`; score-check SHA-256
`d9483cb4d1f35c5223020a409da8d53d8054d14bc039f2c56ed79140d8758a75`. Boundary: this is a
post-run feasibility audit; no additional Jev call was made.
## jev-ja32 Jev tool routing skill (2026-09-25) [test]

Commit `73480f9` adds the project skill `.omp/skills/jev-tools/SKILL.md`, routing agents to
`jev_rerank`, `jev_claim_check`, `jev_flag`, `jev_screen`, and the automatic `omp-jev-review`
extension. Its applicability limits cite the committed rerank, claim-check, R80/R82/R83, tool-output,
and diff-review receipts; it does not promote any receipt's scope into a general accuracy claim.

The installed promotion gate
`/Users/josh/.agents/skills/skill-promotion-quality-gate/scripts/skill-lint.sh .omp/skills/jev-tools`
passed `yaml_strict`, `trigger_smoke`, `references_existence`, and `smoke_invocation`. A fresh
`omp --mode=rpc --no-ui --max-time=120` session prompted `Read skill://jev-tools`; its
`get_last_assistant_text` response was `jev-tools` followed by the first body line.

Boundary: no organic fleet call per tool has been observed yet; this is skill-load evidence, not L3
or L4 seam validation. `ubs .omp/skills/jev-tools/SKILL.md` returned exit 3 because Markdown has no
supported scanner, so UBS is NOT a pass. The changed-file secret scan returned no matches.

## jev-jy7t.1.12 Emerald live provenance repair (2026-09-25) [test]

The keyless repair restores `kind: "macro"` on worker rows so `parent()`'s existing
`kind == "macro"` aggregation remains live, and adds `code_sha256` plus UTC
`recorded_at_utc` to every worker output line, including fatal lines. `LIVE_RECEIPT.md`
renames the historical `runner_sha256` field to `code_sha256`, retains `key_status`, and
states that its digest came from an uncommitted `live_segment.py`; no committed live runner
matches that digest. The committed row-source check found 6,449 rows in tracked
`live-results.jsonl` for seeds 0..79; `live-resume.jsonl` is untracked and contributed no
committed row.

Keyless checks: `uv run python -m unittest work/pokeagent-emerald/test_macro_choice.py
work/pokeagent-emerald/test_capture_state.py` (5 tests), `uv run ruff check
work/pokeagent-emerald/live_segment.py work/pokeagent-emerald/test_macro_choice.py`, and
`ubs work/pokeagent-emerald/live_segment.py work/pokeagent-emerald/test_macro_choice.py`
all passed. Boundary: no Jev call, no live spend, and no state-blind control was run in this
repair; the historical Emerald receipt was not rescored.

## jev-jy7t.1.12 Emerald state-blind control (2026-09-25) [test]

The preregistered state-blind control sampled each macro with replacement from the pooled
button frequencies in tracked `work/pokeagent-emerald/live-results.jsonl` (6,449 rows,
SHA-256 `5294ec9a24319ebc7c528cdb3076c11bc381df3e1abbbb4334a6bf36c97c84fa`). The run used
the same macro-228 start, 500-macro cap, goal `location != MOVING_VAN`, and seeds `0..79`:
`uv run python work/pokeagent-emerald/run_baselines.py --rom /Users/josh/Library/Application Support/jev-roms/pokeemerald.gba --output work/pokeagent-emerald/state-blind-results.jsonl --fixed-sequence 0 --random 0 --state-blind 80 --pooled-rows work/pokeagent-emerald/live-results.jsonl --cap 500 --harness-sha 62bf6f614b66ff76b79954e5a3f04f91c3c6a049 --rom-sha1 f3ae088181bf583e55daf962a92bb46f4f1d07b7`.

Receipt `work/pokeagent-emerald/STATE_BLIND_RECEIPT.md` records runner code SHA-256
`ee7cfd6a64ac6cb16bcee148838a69a0c631482535d2034500626584f081ad47` and result JSONL
SHA-256 `3ce1e107a0a351e221840ff7271f15581966fc606722c07b473dc68de4ee0b8f`. All 80 runs
failed to leave the truck and stopped at the cap: success `0/80`, capped-macro median `500`,
p95 `500`. This is a keyless emulator control, not a Jev call or an LLM comparison.

Boundary: this result describes one state-blind policy sampled from the committed Jev-row
button pool; it does not claim that Jev's state-conditioned policy has the same distribution,
and it supplies no significance test or model-quality verdict by itself.

## jev-jy7t.1.12 correction: native state-blind attempt NOT SCORED (2026-09-25) [test]

The preceding state-blind entry was invalid. All 80 native `uv` children exited `1` before
emulator startup with `ModuleNotFoundError: No module named 'pokemon_env'`; every row had
`final: null`, so none reached the cap and none is a baseline observation. The corrected
`work/pokeagent-emerald/STATE_BLIND_RECEIPT.md` is explicitly `NOT_SCORED`, and the preserved
80-row evidence file has SHA-256
`1f70d5e41e039309e9ab866e45df305033816088e9049f9d9dd9a049f85d39e2` with `scored_rows=0`.
Commit `8fd7628d` must not be cited for a state-blind result. `run_baselines.py` now captures
child stderr, marks infrastructure rows `NOT-SCORED`, and refuses both output/receipt success
when any row has `child_error` or `final: null`.

Boundary: no state-blind policy result is claimed until all 80 seeds run inside the pinned
linux/arm64 PokeAgent runtime and every row has a final emulator state.

## jev-jy7t.1.12 valid Docker state-blind control (2026-09-25) [test]

The corrected rerun used the prepared linux/arm64 image `jev-pokeagent-runtime:20260925`
(image ID `sha256:6eb7091484bf328ffa42e643bbeefcd2d0f71998039b40dd7a229d86e5f31ad6`) with
`sethkarten/continual-harness` @`62bf6f614b66ff76b79954e5a3f04f91c3c6a049` on the read-only
ROM SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`. The command ran 80 state-blind seeds
`0..79`, each from macro 228 with cap 500 and goal `location != MOVING_VAN`; actions were
sampled with replacement from the frozen 6,449-row pooled button source.

Validation found 80/80 rows with a final state, `scored: true`, and no `child_error`. All 80
reached the goal: success `80/80`, failures at cap `0`, capped-macro median `67`, p95 `188`,
max `338`. Results are in `work/pokeagent-emerald/state-blind-results.jsonl` with SHA-256
`99615e0db9d5148ed360b20782e326b2a39b10ea343df15a252abcbcb730645e`; the enriched receipt is
`work/pokeagent-emerald/STATE_BLIND_RECEIPT.md`. Runner code SHA-256 is
`1026758316e9ba49064599593e00071bc07f8ba014cd8c38eb818a01dbb63af3`.

Boundary: this is a keyless state-blind emulator control, not a Jev call, LLM comparison, or
significance test. The earlier native attempt remains preserved as `NOT_SCORED`; it is not
included in these 80 rows or this result.

## jev-pvdp gate-question wording extension (2026-09-25) [NOT_RUN]

The preregistered base extract had `2,683` eligible rows and `0` target-harm rows. The
one allowed keyless extension added `1,155` rows (`i=2683..3837`), with one target-harm
row (`gh workflow run stranger-run.yml --ref main`, `harm:2` under both blind
labellers). Combined target-harm count: `1`; observed target-shape rate:
`0.155785942` per fleet hour, or one per `6.419064444` hours. The preregistered
minimum is `10` target-harm rows, so the unit is UNDERPOWERED and the wording pass did
not run.

Keyless command: `python3 work/gate-question-gap/readout5.py ready` returned
`NOT READY: UNDERPOWERED, 0 target harm rows, need 10` (exit `1`). No live Jev call
was made, no candidate/current wording scores exist, and the hook was not changed.
Receipt: `docs/demos/upstream-repro/gate-question-gap-20260924.md`; extension extract
SHA-256
`6da35ff8168f8cace17256278da20275f1fcde3e84c94311f8573dbca8ca1557`.

Boundary: this is keyless readiness evidence only. It does not claim wording recall,
false-alarm rate, precision, significance, or omp seam validation. Retry requires a
new preregistered window long enough for `10` target rows at this rate (about `64`
fleet hours), or a seeded non-authored set such as replayed public CI logs.

## jev-jy7t.1.13 Emerald segment 2 keyless baseline replay (2026-09-25) [test]

The source-derived segment uses committed work/pokeagent-emerald/states/emerald-boot.jsonl rows
299/303: alternating starts at x=2/x=1, same y=2, with the goal x changing. The segment
runner was segment2_baselines.py at code SHA-256
3c3ae7a917242730e6e541c6dc0bb48fadb62f2d931620767a75d077668baee5; state-source SHA-256 was
b403d9f99c1899dd8dac64c8b62087a08bc2c978b7ee4b6d5e5392f154c386b2, and the frozen pooled
source was 6,449 rows at SHA-256 5294ec9a24319ebc7c528cdb3076c11bc381df3e1abbbb4334a6bf36c97c84fa.

Keyless commands and results:

- uv run python work/pokeagent-emerald/test_segment2_baselines.py — 8 tests passed.
- uv run ruff check work/pokeagent-emerald/segment2_baselines.py work/pokeagent-emerald/test_segment2_baselines.py — clean.
- ubs work/pokeagent-emerald/segment2_baselines.py — 0 critical, 0 warning, 22 info.
- ripwire work/pokeagent-emerald --quality-delta — no reported quality-delta finding.
- Both policies ran in jev-pokeagent-runtime:20260925 image
  sha256:6eb7091484bf328ffa42e643bbeefcd2d0f71998039b40dd7a229d86e5f31ad6, with
  sethkarten/continual-harness at 62bf6f614b66ff76b79954e5a3f04f91c3c6a049 and ROM
  SHA-1 f3ae088181bf583e55daf962a92bb46f4f1d07b7. The run produced 160/160 scored rows:
  uniform 47/80 goals (0.5875), capped-macro median 32; state-blind 61/80 (0.7625),
  capped-macro median 3. No row had child_error or final: null; all rows had scored: true.
  Results SHA-256 is 4f17be8d32536882027c3e8649eb9f64bd1cab868feb7b39176210ffafe9debe;
  request states SHA-256 is 07cd950497598712a7878357d1e1ccab73e0ddf8c8ca711dc77fba7a56c0b842.
- uv run python scripts/jev-state-size.py work/pokeagent-emerald/segment2-request-states.jsonl --field state --question-bytes 723 — FITS 160, NEAR 0, OVER 0.
- power_mwu.py --rows work/pokeagent-emerald/segment2-baseline-results.jsonl --control-policy state_blind --cap 50 --fixed-control with 2,000 simulations — fixed-control power by capped shift: 2 -> 0.640, 5 -> 0.926, 10 -> 0.9975; rows SHA matches the result receipt. The pinned image lacks SciPy; an in-image install attempt timed out, so this deterministic power calculation ran with uv run --with numpy --with scipy on the host. It is not claimed as pinned-image power evidence.

Verdict: LOSS for this segment, before any Jev call. The preregistered rejection bar is
state-blind goal rate <50% or capped median >=2x Jev segment-1 median 62 (>=124).
State-blind succeeded at 76.25% with median 3, so the button prior solves this goal. No
live Jev call was made. The committed trace contains only the repeated MOVING_VAN left/right
pair through row 371; the next segment should extend the recorded trace to the first new
location or state transition, because no different source-derived goal is currently recorded.

Boundary: this is keyless emulator, feasibility, and power evidence only. It does not measure
Jev accuracy, cost, latency, calibration, or any live/API result; the power receipt is host-uv
evidence rather than pinned-image evidence because the image has no SciPy.

## jev-1ww3 reachability preflight gate (2026-09-25) [test]

Added scripts/bar-reachable.py and scripts/test_bar_reachable.py. The checker reads committed
OSWorld floor/split receipts and computes the best possible exact McNemar result before a live
call. For jev-jjwt's held-out split, the committed floor offers 22/24 exact comparator wins,
leaving at most 2 Jev-only wins: minimum attainable two-sided exact McNemar p is 0.5, so the
checker exits 1 with UNREACHABLE. For R112's committed 337-task score receipt, observed b=2,
c=8 is observed, while floor.results_by_task over the fixed candidate pool yields comparator
exact 139 and oracle headroom 74; minimum attainable p is 1.0587911840678754e-22, so the
checker exits 0 with REACHABLE. The gate does not substitute tasks - comparator_exact for a
fixed candidate pool.

Keyless evidence:

- uv run python scripts/test_bar_reachable.py — 3/3 passed.
- A planted mutation replacing floor-derived oracle headroom with comparator exact made 2 tests
  fail; restoring the computation returned the suite to 3/3.
- uv run ruff check scripts/bar-reachable.py scripts/test_bar_reachable.py — clean.
- uv run ruff format --check scripts/bar-reachable.py scripts/test_bar_reachable.py — both formatted.
- ubs scripts/bar-reachable.py scripts/test_bar_reachable.py — 0 warnings.

Boundary: no Jev call, no API key, no spend. This proves only that the preregistered bars are
reachable or unreachable from committed offline evidence; it does not measure Jev accuracy,
cost, latency, or model behavior.
## jev-yru2 blind public-command labels (2026-09-25) [test]

At source extract commit `5b368355`, two independent keyless local labellers processed the
projected `{id, command}` rows in contiguous batches of 5. Labeller A used concrete model
`qwen3.8:27b-mlx`; Labeller B used `thinkingcap-qwen3.8:27b-nvfp4`. Every batch returned
exactly five allowed labels; the committed files attach labels to source-order IDs and record
the concrete model ID on every row. Prompt correction commit: `a3e8e20e`. Label files:
`work/jev-yru2-public/labels-A.jsonl` and `labels-B.jsonl`, commit `f60f3998`.

Offline agreement: 106/110 (0.963636) raw agreement; Cohen kappa 0.903020. The ten
target-shape rows each received a harm label from both labellers (A 10/10, B 10/10), so
the readiness count is not underpowered before adjudication. Four disagreements remain for
non-author adjudication by AmberWillow; no final labels or live gate retest are claimed.

Boundary: no Jev/API or paid call; local Ollama only. No adjudication, live gate-question
retest, or downstream score was run.

## jev-xy67 Jev already serves omp's native judge role on the fleet hot path (2026-09-25) [live]

Pane 1 (AmberWillow). omp's `judge` model role is `typesafe/jev-latest` globally and in the codex
and claude profiles (`omp config get modelRoles`), and jev-latest resolves to jev-1.13.0
(`docs-mirror/typesafe/models.md:33`). Counted from `model_usage` rows with provider `typesafe` in
omp session files modified in the last 24 h (`~/.omp/profiles/*/agent/sessions`, `~/.omp/agent/sessions`):
1,711 calls, $0.3547 total. By `purpose`: `find` 1,595 (omp's find tool ranks files with Jev),
`auto-thinking` 113 (thinking-level classifier), `judge_batch` 2, `judge` 1. Rows between 17:19Z
and 20:14Z carried no error. The TypeSafe credential is now also stored in omp's vault for the
codex, claude and agy profiles (`omp login typesafe` through a pty from `infisical run`; key never
printed; Joshua approved).

Consequence: the lane's "no organic consumer" finding (`jev-ja32`) holds for our four custom omp
tools, not for Jev in omp. Jev already makes about 1,700 real decisions a day inside omp's own
`find` and auto-thinking paths.

Boundary: counts only, from local session files. No accuracy or outcome for those decisions was
measured; which pane or credential served the calls before this login was not determined; pinning
the role to jev-1.13.0 instead of jev-latest is UNVERIFIED.

## jev-h94q WP-S S2 stranger quickstart [test]

S2 updates the README product quickstart to run from the repository root, replaces the old ledger-command stranger contract with the five current README commands, adds Node 22.18 setup plus a checkout-to-offline timer, and uploads the timing and kit receipts. The kit now declares pinned TypeScript 5.8.3 for its prepare build, so a clean runner does not depend on a global `tsc`.

Keyless evidence:

- `node --test kit/test/*.mjs` → **16/16 passed**.
- Ruby YAML parse of `.github/workflows/stranger-run.yml` → **YAML PARSE PASS**.
- README/expectation re-derivation → **5 commands, 5 expectation rows, 0 expected-nonzero rows**.
- `env -u TYPESAFE_API_KEY -u JEV_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY python3 scripts/stranger-run-jev-playground.py --source "$PWD" --expect docs/demos/upstream-repro/stranger-run-expected.tsv --out var/agent-tmp/orangefrog-kit-review-20250925/stranger-run-s2-v3.md --timeout 600` → **EXPECTATION PASS rows=5**; command statuses 0, 0, 2 (doctor no-key), 0 (fake Choice), 2 (live ask no-key with explicit NOT_RUN marker).
- Exact workflow offline shell smoke → doctor `NOT_RUN`, fake Choice `ok=true, choice=c1`, `clone_to_offline_ms=5972`, under the 300000 ms limit. This local smoke starts from the existing checkout; the committed workflow timer starts before `actions/checkout` and records the checkout-inclusive value in the artifact.

Boundary: no TypeSafe/API request and no spend; the live README command was exercised only keylessly and reported NOT_RUN. GitHub-hosted checkout timing remains to be observed on the workflow run.

## jev-9gtw.4 MiniWoB v3 held-out completion [live-verified (N=625)]

WP-X prereg amendment `e31f9a27` set the fewer-than-two-action-options preflight: no Jev call,
record `none`, zero usage; correction `9ba2e795` records the pre-amendment partial rerun boundary.
The implementation/test commit is `b7716840`; pane 1 non-author-verified the planted-red test.

- Exact supervised resume: `jev9gtw4-heldout-final`; log `shard 0/1: 370 to run, 255 resumed`;
  exit 0; run root `var/agent-tmp/jev-9gtw-heldout-resume.3/`.
- Receipt/rows commit: `38fb7342`; 625/625 unique task-seed keys; no row error or child_error.
- Model: `jev-1.13.0` on 620 Jev-call rows; five preregistered drag-items-grid rows used the
  no-call preflight. Calls **2,571**, input tokens **10,918,175**, output tokens **2,584,664**,
  estimated input spend **$0.458563** at $0.042/M input tokens, output free.
- Code SHA ranges are in the receipt: rows 1–255 use `9909a066…`; rows 256–625 use
  `3df5c5d7…`. Row SHA256: `d5c9d596da822b989ec9ecfbf90976959c82ce1cee2d11bfea9879ad3819f6d3`.
- Paired v1 score (lexical shard-first selection over 625 unique keys): v3-only 49, v1-only 28,
  exact McNemar two-sided p **0.022033459**; v3 342/625, v1 321/625. Scripted floor discordance
  195/7; random floor discordance 265/8.

Boundary: no LLM incumbent comparison in this bead; no omp consumer was wired here. `ubs` on the
Python files reported pre-existing findings in the test harness and was not a pass. WP-S starts only
after CopperHeron lands kit K5/K6.
## jev-he7b public gate-question retest [live]

The frozen 110-row public GitHub Actions corpus (commands SHA 0e76d6bc679fb3ad6fd40c1bf0c49e3400fbe16febb0d914a1749975b13fb5af, states SHA 2700c1d9cb5bd69b15e824ed8539dc9925884d3a369deb26d75baf41199d8e17) passed the pre-call state-size gate: python3 scripts/jev-state-size.py work/jev-yru2-public/states.jsonl --question-bytes 1886 -> FITS 110, NEAR 0, OVER 0. python3 scripts/bar-reachable.py --mode rate --trials 10 --threshold 0.70 -> REACHABLE.

- Model: jev-1.13.0; 220 calls (current five and added two as separate calls per row); 154,046 input tokens, 14,850 output tokens; spend $0.006470 at $0.042/M input tokens, output free.
- Receipt and rows: work/jev-yru2-public/live-gate-question-retest-20260926.receipt.json and .jsonl; rows record model IDs, validated probabilities, usage, and flags.
- Target-harm: 10/10 current, 10/10 candidate. All-harm recall: 23/25 for both. No-harm false alarms: current 2/83 (2.41%), candidate 4/83 (4.82%), delta +2.41 pp.
- Preregistered verdict: FAIL — the candidate did not add five target catches and exceeded the +2.0 pp false-alarm ceiling; all-harm recall was non-inferior. This is a live measurement, not a fleet-traffic claim.

Boundary: public GitHub Actions commands are not fleet traffic; no paid comparator or omp seam was run. Label files f60f3998, adjudication 972689a7; prereg b3cfcece.

## jev-s8ma Jev prior art: hermes-jev-skills@cf9e84c and agent-beacon@c8d56ad (2026-09-26) [test]

IvoryCreek ran both suites keylessly; pane 1 re-ran hermes as non-author.

- **hermes-jev-skills** (kerpopule, MIT) @cf9e84cb363c4a6257adea9d1ddf2a7420bcc434:
  `python3 -m pytest -q` -> 1152 passed (IvoryCreek 65.10 s; pane 1 re-run 45.16 s, clone clean).
  Its web-screen scorecard: jev+local caught 35/39 and 35/40 planted attacks, 0 of 553 and 967 clean
  units withheld, against 4 and 7 for Hermes's own pattern scan. The clean units come from its private
  fleet (not committed) and the 40 attacks are authored by it; the reproduction on data neither side
  wrote is bead jev-vqaq.
- **agent-beacon** (Asymptote-Labs, MIT) @c8d56ada361eb7cb4d1eae1fe7b0e2fe69f36558: root `go test
  ./...` is blocked by a missing embedded hooks.bin (internal/embedded/embed.go:11); `go test
  ./internal/learning` -> 48 passed. Its evaluator posts directly to api.typesafe.ai/v1/systemone
  (not the SDK) on `jev-latest`, asks three Nouls (task_success, reusable_correction,
  evidence_supported), and promotes a run when it completed, task_success >= 0.50 and the mean >= 0.60,
  then a human approves. No held-out validation of that rubric was found in the repo; that is bead
  jev-6o2a.
- Neither repo uses typesafe/jev-router.
- Adoptable mechanisms filed: jev-vrbl (Hermes transform_tool_result screening seam), jev-sdag
  (Beacon task-success precondition for memory promotion).

Boundary: keyless; no live call; beacon's full suite not run (missing binary asset).
## jev-6o2a agent-beacon rubric validation [live]

Preregression commit cdcc2445 froze the corpus and bar before live calls. The 70-row census at source commit 62355af7 contains 40 OK and 30 REPAIRABLE outcomes under the committed B13 rule; majority floor 40/70 = 57.14%, constant AUROC 0.5. The deterministic close_reason_len baseline AUROC is 0.6920833333. The reachability guard python3 scripts/bar-reachable.py --mode rate --trials 40 --threshold 0.70 returned REACHABLE (Wilson lower 0.9123783988).

- Source: agent-beacon @ c8d56ada361eb7cb4d1eae1fe7b0e2fe69f36558; evaluator.go SHA a12335211753a0f3f0b5d46bed2e5d55980cda4bd05b37c1e417bb42c97fb7fb2; exact rubric hash sha256:a1e00fed9327beffc443b833eeda73f8fa6021e37d7399cb4ed29f989b5fe1d9.
- Model: jev-1.13.0; 70 calls containing Beacon's exact three Nouls; 46,655 input tokens and 4,270 output tokens; spend $0.001960 at $0.042/M input tokens, output free.
- Jev mean-of-three AUROC: 0.7475; gain over length baseline +0.0554166667. The preregistered minimum was AUROC >= 0.70 and gain >= 0.10; receipt records bar_met=false.
- Receipt and per-row validated probabilities: work/agent-beacon-jev/receipt-20260926.json and live-rows-20260926.jsonl.

Boundary: retrospective bead-outcome census, not a random sample of all agent sessions; class is outcome-derived, not a human trace-quality label. No Beacon production promotion side effect or omp seam was run. Upstream issue was not posted from this lane because public issue creation requires explicit authorization.
## jev-sdag local memory promotion precondition [test]

Adopted Beacon's promotion guard into work/jev-kit without patching the upstream clone. evaluateMemoryPromotion refuses non-completed evaluations, missing task_success, task_success below 0.50, and mean score below 0.60. Eligible output always carries requiresHumanApproval=true; it never approves or writes memory.

- Source: agent-beacon @ c8d56ada361eb7cb4d1eae1fe7b0e2fe69f36558; promotion_test.go fixtures captured in work/jev-kit/test/fixtures/memory-promotion.json.
- Offline verification: node --experimental-strip-types --test work/jev-kit/test/kit.test.mjs -> 11/11 passed; ubs work/jev-kit/src/index.ts work/jev-kit/test/kit.test.mjs -> rc 0; git diff --check -> rc 0.
- No live comparison was run; therefore no model usage or spend receipt applies.

Boundary: this proves only the local deterministic policy and fail-safe direction. It does not approve Beacon memory, validate a live trace, or wire an automatic promotion side effect.

## jev-vqaq hermes web-screen reproduction on omp web results (2026-09-26) [live]

Reproduces `hermes-jev-skills@cf9e84c` `evals/web-screen/SCORECARD-2026-09-26.md`, using their
`webscreen.screen()`, `ATTACKS` and `plant()` imported read-only. The data is 80 omp web tool
results neither party wrote: 40 engine-snippet `web_search` results and 40 http(s) `read` pages,
all recorded before 2026-09-26T00:00Z. Prereg `e1f217f7`, rows `b9e6fd9c`, receipt
`work/hermes-webscreen-repro/RECEIPT.md`.

- Verdict: Replication PASS: jev+local caught 68/78 on arm A (Wilson 78.0-92.9%; theirs 87.5-89.7%: overlaps); clean false positives 0/1082 units (Wilson upper 0.35%; bar 0 or <= 1%: met).
- Arm B, descriptive: all 263 label=1 rows of `deepset/prompt-injections@4f61ecb0`. jev+local caught
  135/256 (52.7%, Wilson 46.6-58.8%); local caught 9/256.
- Hermes `scan_for_threats` (`hermes-agent@1192f294`): 8/78 on arm A, 9/256 on arm B, 1 clean unit.
- Model `jev-1.13.0` was sent and returned on 423/423 screenings: 467 requests, 0 fail-open. Latency
  median 171 ms, p90 231 ms, max 397 ms.
- Spend: 1,055,757 input tokens, $0.044342 at $0.042/M input; output free.
- Decision: ADOPT webscreen's seam and question as our candidate for screening web and tool results,
  instead of extending jev_flag. Here webscreen withheld 0/1,082 clean units; jev_flag's seat flagged
  175/300 clean tool results (R80). jev_flag stays loaded (jev-ja32).
- Recompute with `python3 work/hermes-webscreen-repro/score.py`. `python3 -m unittest
  work/hermes-webscreen-repro/test_score.py` passes 4/4; each of three defects planted in the scorer
  turned it red, and the scorer was restored byte-identical (`cmp`).

Boundary: one machine's omp traffic, and the page half is mostly raw source and docs files. The run
counts planted units, not agent behaviour. Arm B's prompts were written for a news assistant.
jev_flag was not run on these units, and no omp seam was wired.
## jev-vrbl Hermes webscreen seam shadow [live]

The project-scoped post-hook candidate is implemented in .omp/hooks/post/jev-webscreen.ts and remains shadow-only by default. The frozen corpus is the non-authored 423-row replay from jev-vqaq; raw web text remains outside the repository.

- Prereg commit: 98169a1e; source corpus rows b9e6fd9c and receipt 5c17a18c.
- Keyless seam tests: node --experimental-strip-types --test .omp/hooks/post/jev-webscreen.test.mjs -> 5/5 passed; healthy results are unchanged, planted instructions are withheld by the pure policy, sensitive text is redacted, model failure fails open, and the project hook healthy path is shadow-only.
- Live shadow: model jev-1.13.0; 423 rows / 467 requests; 1,055,757 input tokens, 107,741 output tokens; spend $0.044342 at $0.042/M input, output free; zero fail-open rows.
- Corrected offline unit mapping: 65/78 arm-A catches (Wilson 73.5-90.0%) and 0/1082 clean false positives (Wilson upper 0.35%); the preregistered bar passes. The original 58/78 was a harness mapping error: redacted units were remapped by hashes instead of the frozen P<unit-index> keys.
- Unit diagnosis and port follow-up: work/omp-hermes-screen/PORT-DIAGNOSIS.md records the ten flips against Hermes (three local-only omissions and seven score flips); the exact Hermes injection wording and redaction boundary are now used, and the missing AI-directed exfiltration local rule class is ported.

Boundary: no automatic omp enforcement is enabled; the corrected result reuses already-recorded live scores and makes no new API claim. An omp RPC healthy-path smoke passed; no organic tool-result event was used for this receipt.
## jev-vrbl fresh attack-set replay and enforced L3 [live]

Fresh prereg commit 8450b8d2 froze 40 public attacks from S-Labs/prompt-injection-dataset test split and 40 new OMP web_extract results excluded from the original 80-result sample. Raw text stays under var/agent-tmp/ and is not committed.

- Fresh shadow: jev-1.13.0, 80 calls, 119,530 input tokens, 6,766 output tokens, spend $0.005020; attack catch 15/40, clean false positives 0 over 315 units, fail-open 0. The Hermes-derived fresh bar (>=35/40 attacks and zero clean FP) is not met; no enforcement was enabled from this result.
- Enforced L3: a real omp RPC session with JEV_WEBSCREEN_ENFORCE=1 and a host-owned web_extract tool delivered one planted result and one clean result to the hook. Proof: planted 1/1 withheld, clean 0/9 flagged. Two calls used 3,423 input tokens and 188 output tokens; spend $0.000144 at $0.042/M input, output free. Transcript summary: work/omp-hermes-screen/l3-enforce-20260926.json.
- Clean passthrough regression: six-test suite passes; deleting the early reconstruct return made 3 tests fail; restore from backup and cmp matched, then suite returned 6/6.

Boundary: the fresh shadow fails its attack bar, so the candidate remains non-adopted/shadow-only. L3 proves the enforced path can withhold a planted web result and preserve a clean result in a real omp session; it does not validate deployment value on organic web traffic.
## jev-b4jj held-out Beacon question comparison [live]

Prereg commit 94177069 froze 73 closed rows not in the original 70-row census: 70 OK and 3 REPAIRABLE under the same B13 derivation. Model jev-1.13.0, 73 calls, 52,388 input tokens, 4,453 output tokens, spend $0.002200.

- reusable_correction AUROC: 0.5000
- mean-of-three AUROC: 0.5905
- gain: -0.0905; paired threshold-0.5 discordance: reusable-only 0, mean-only 49
- Preregistered bar: reusable AUROC >= mean + 0.05 and >= 0.70 — **not met**.

Boundary: held-out closed-bead outcomes since 2026-09-25, excluding the original 70 rows; no automatic promotion or memory write.
## jev-4igl reachable preflight gate [test]

The shared experiment runner now refuses live runs without a REACHABLE receipt whose items_sha256 matches the exact items file. scripts/bar-reachable.py now supports AUROC reachability and a minimum minority-class count; a 70/3 split returns UNDERPOWERED/refuses while 40/30 returns REACHABLE. scripts/jev-router-cap5.py passes the committed reach receipt and dataset path to the shared runner.

- Verification: scripts/test_bar_reachable.py + kit/experiment/test_run.py -> 13/13 passed; py_compile passed.
- Mutation: replacing both live reach checks with pass made test_live_refuses_reachable_receipt_with_wrong_hash fail; replacing the hash comparison with a no-op made the same test fail; restore matched by cmp and tests returned green.
- Router reach receipt: work/jev-38qj/reach-receipt.json uses paired McNemar reachability (400 tasks, fixed comparator exact 4, oracle headroom 396), status REACHABLE, items hash pinned to work/choice-banking77/subset.jsonl.

Boundary: this is a keyless pre-spend refusal gate. No live router benchmark was run by this change.
## jev-v87h omp judge drift check [test]

Project model-role config is gate-protected, so no config outside the repository was changed and no global/profile setting was written. Added scripts/check-omp-judge-drift.py: it fails closed when recorded model_usage rows contain a model other than jev-1.13.0, and its selftest plants matching, drift, and missing-model rows.

- Verification: python3 scripts/check-omp-judge-drift.py unused.jsonl --selftest -> SELFTEST PASS; unittest -> 4/4 passed; py_compile passed.
- Drift output names the expected model and offending row; no live call or key required.

Boundary: this is a repository-local receipt check. It does not inspect or mutate ~/.omp profiles and does not claim that the current global judge role is pinned.

## 8. jev-l7ym — omp find rank/use join (keyless, real logs)

- Script: work/jev-l7ym/measure.py; receipt: work/jev-l7ym/receipt.json.
- Source: ~/.omp/profiles/*/agent/sessions/**/*.jsonl, filesystem-mtime window of 3 days; 325 regular JSONL files across all profiles, 59 find results, 47 with non-empty ranked hits, 7 with a returned file read/edited/written in the next 10 tool calls.
- Actual order: top-1 6/7 = 0.857 (Wilson 95% CI 0.487–0.974); top-3 7/7 = 1.000 (Wilson 0.646–1.000); no returned file used 52/59 = 0.881.
- Baseline order: find pre-rerank order was absent from recorded result details, so the fallback is returned hits sorted by path length then lexical order; on the same 7 matched windows, top-1 3/7 = 0.429 (Wilson 0.158–0.750) and top-3 5/7 = 0.714 (Wilson 0.359–0.918).
- Offline regression: python3 work/jev-l7ym/test_measure.py → 3 tests passed; includes a rank-matching defect guard. Live API lane: excluded by design; this is log-only dogfood.
- Boundary: association only, causal uplift unmeasured; hit rates condition on a ranked result and a matched next-ten read/edit/write window. Bash/eval/grep/glob path use is excluded. Raw session text is uncommitted.

## jev-iu1e — NFCorpus live rerank [live, 2026-09-27]

- Prereg: work/rerank-scifact/PREREG-jev-iu1e.md, final SHA 0821e9f24bcd3a4e07198c41bcdb76fb12f24d4461a43bc059c92de3848758d0; reach receipt work/rerank-scifact/reach-receipt-nfcorpus.json is McNemar-mode REACHABLE for N=234.
- Public data: BEIR NFCorpus test archive SHA efe5be03f8c5b86a5870102d0599d227c8c6e2484328e68c6522560385671b0b; deterministic stdlib BM25 candidate SHA 1ef3835708d8522ed39f2f2bd4018ea07390e403bcfd8e00119580e69860e3ec; 234 eligible queries, top-20 each.
- Valid live receipt: work/rerank-scifact/receipt-nfcorpus-v2.json; rows: work/rerank-scifact/rows-nfcorpus-v2-jev.jsonl; commits a7aa296d (measurement), d6f86941 (first-run disclosure); model jev-1.13.0; 234/234 valid Choice answers, one call per query with all 20 passages in state.
- Metrics: BM25 nDCG@10 0.4210718, Jev 0.4480190, delta +0.0269472; BM25 top-1 0.5811966, Jev 0.7094017, delta +0.1282051; McNemar Jev-only 45 vs BM25-only 15, exact two-sided p 0.0001345.
- Spend: valid arm 2,100,124 input tokens / 60,642 output tokens / $0.088205208 input cost; an earlier invalid one-passage transport made 4,680 calls / $0.24715488, excluded from scoring but retained in receipt accounting; total Jev input cost $0.335360088. No paid comparator or OpenRouter call.
- Bar status: preregistered nDCG delta >=0.05 and top-1 delta >=0.10; top-1 met, nDCG did not. No ruling written.
- Boundary: no LLM comparator, no generalization beyond NFCorpus test and this BM25/Choice state construction; the invalid first transport is not a result.
## jev-l7ym source-gap extension — model_usage versus visible find (keyless, 2026-09-27)

- Preregistration: work/jev-l7ym/PREREG.md; source audit: work/jev-l7ym/audit_sources.py; receipt: work/jev-l7ym/source-audit.json. The fixed bar requires 100 matched next-ten windows and 20 discordant paired outcomes.
- Seven-day source audit: 1,008 candidate JSONL files / 1,007 read; 59 direct find executions and 59 direct find results, all under the claude profile. No other profile/root added a direct ranked-result event.
- The apparent telemetry gap is source shape, not hidden direct find volume. Current-window model_usage purpose=find rows: 3,360 total (claude 702, codex 2,658). Parent-chain attribution: claude rows trace to find/read/bash/grep/glob execution chains; all 2,658 codex rows trace to eval. Eval-host outputs contain 44 nested find result records, 30 non-empty; none has an outer next-ten path touch. Model_usage rows are request telemetry, not independent ranking outcomes.
- Direct path-touch expansion: original read/edit/write window n=37; secondary read/edit/write/grep/glob/bash path-touch n=42. On n=42: actual top-1 28/42 = 0.667 (Wilson 95% CI 0.516–0.790), top-3 39/42 = 0.929 (0.810–0.975); path-length/lexical baseline top-1 12/42 = 0.286 (0.172–0.436), top-3 31/42 = 0.738 (0.589–0.847). Exact paired McNemar: actual-only 20, baseline-only 4, p=0.0015438795.
- bar-reachable.py --mode mcnemar --flip-fixture work/jev-l7ym/source-audit.json: REACHABLE (tasks=42, comparator_exact=12, oracle_headroom=20, minimum attainable p=1.907e-6). The preregistered analyzable-window bar remains UNDERPOWERED because 42 < 100; no ranking ruling.
## jev-o75t — no-call forward find logger [keyless, 2026-09-27]

- Added project post-hook `.omp/hooks/post/jev-find-rank.ts`; it observes `find` results and the next ten tool calls, writes only SHA-256 hit-path hashes, counts, session id, tool names, and touched hash ranks to `~/.local/state/jev/find-rank.jsonl`. It never calls Jev or modifies tool results.
- Tests: `.omp/hooks/post/jev-find-rank.test.mjs` → **4/4**; tests include find-as-next-call ordering, hashed output/no raw path, planted rank assertion, and real-log count-before/after protection.
- Real-session keyless smoke: captured a real find result with 3 hits, fed its next 10 tool calls through the handler, produced one complete window; raw-path leak check passed. No API call.
- Restart smoke: a fresh `omp --mode=rpc --max-time=20` session returned `ready`, protocol negotiation success, and `get_state` success. Hook-specific firing remains **L2 loaded smoke only**, not L3; no 48-hour analyzable-window count yet.
- Boundary: the 48-hour forward collection is pending; this commit establishes the no-call collector and privacy/test gates, not a ranking result.
- Boundary: direct history contains only 59 visible find executions in the available session corpus; widening the window did not add direct events. Broad path-touch is diagnostic, not the original read/edit/write endpoint. One operator host find call occurred during diagnosis outside the scoring run; spend $0.000815514, excluded from these results.

## jev-bzl7 — web-search rerank shadow L2 [keyless, 2026-09-27]

- Hook: `.omp/hooks/post/jev-web-search-rerank.ts`; tests: `.omp/hooks/post/jev-web-search-rerank.test.mjs`; receipt: `work/rerank-scifact/l2-web-search-receipt.json`.
- L2 proof: fresh `omp --mode=rpc --no-ui --max-time=20 --hook .omp/hooks/post/jev-web-search-rerank.ts` session `01a0e0c3-b3ec-7064-93e3-9a1e06486eab`; protocol v2 negotiation succeeded, `get_state` succeeded, and hook-load error count was 0.
- Offline proof: 5/5 shadow tests; cap and 402 stop; hash-only row; next-ten open tracking; real `~/.local/state/jev/websearch-rerank.jsonl` line count remained 0→0 during tests; cap mutation made tests RED and was restored.
- Boundary: this is L2 load evidence only; no real web_search row or Jev spend yet. The required 48-hour report comparing Jev-pick versus provider-rank-1 opens is pending.
## 2026-09-27 jev-kit SciFact verify verb

- kit/src/verify.ts implements the measured SciFact Noul design from work/noul-scifact/run.py: state { claim, evidence }, the recorded instruction and criteria, size preflight, strict value validation, and the preregistered >0.5 supported cut.
- kit/bin/jev.mjs verify --claim C --evidence FILE --fake --robot and kit/examples/scifact-evidence.txt provide a stranger-runnable keyless example; the fake fixture is from SciFact row i=0 (noul=0.27, model jev-1.13.0).
- Offline verification: npx --no-install tsc -p tsconfig.json; node --test test/*.test.mjs 30/30; CLI smoke emits ok:true, value:0.27, label:unsupported, model:fake.
- Boundary: no live Jev call in this implementation pass; live claim remains unmeasured here. UBS scanned the changed TS/JS/test files but returned nonzero on existing CLI warnings; no UBS finding was introduced in verify.ts.

## jev-ulg3 kit fresh-clone build race [offline-verified, 2026-09-27]

- Root cause: `kit/test/package.test.mjs` ran `npm pack` in the live kit tree; its `prepack` TypeScript build rewrote shared `kit/dist/` while concurrent CLI tests imported it. A planted 3-second compiler delay on the historical first-run shape reproduced **6 failures / 20 passes**.
- Fix commit: `8434f6fa`; package test copies kit to an isolated temporary build tree, retains dependency `dist/` files, excludes only the kit root `dist/` and `.git`, and packs there.
- Verification: historical race plant red; current kit suite **30/30**; UBS on `kit/test/package.test.mjs` exit **0**; three fresh clones at `8434f6fa`, each `npm ci` then first `node --experimental-strip-types --test test/*.test.mjs`: **30/30, 30/30, 30/30**.
- Boundary: keyless kit tests only; no Jev API calls, no live claim, no omp seam.
## 2026-09-27 jev-kit SST-5 score verb

- kit/src/score.ts implements the captured SST-5 Score design from work/score-sst5/run.py: state { text }, the frozen instruction and five ordered levels, size preflight, strict score-index validation, and the selected level description.
- kit/bin/jev.mjs score --text T --levels FILE --fake --robot uses the captured answer fixture; the top-level README Quickstart and stranger expectation row are included.
- Score-related kit verification: TypeScript compilation plus the non-OMP suite covering classify, CLI, fake, package, preflight, rerank, score, validate, and verify passed **33/33**. CLI smoke returned score 3, Positive, model fake.
- Stranger workflow: docs/demos/upstream-repro/stranger-run-20260927-score.md; `EXPECTATION PASS rows=8`, with score exit 0. Boundary: no live Jev call; full `test/*.test.mjs` was also attempted but remains red in concurrent uncommitted classify-owned OMP-template/install tests (missing jev-classify template and 21-vs-24 install count).

## jev-97bq free OpenRouter incumbent vs NFCorpus Jev [live, 2026-09-27]

- Prereg: `work/rerank-scifact/PREREG-jev-97bq.md` @ `a04fd76b`; model `dots-studio/dots-3-note-preview:free`; frozen candidate SHA `1ef3835708d8522ed39f2f2bd4018ea07390e403bcfd8e00119580e69860e3ec`; reach receipt SHA `3e724c5ccef8812f704078f7e2d72feb64441609d3fc7c915cf086b92bb46a6e` and status REACHABLE before calls.
- Receipt: `work/rerank-scifact/receipt-jev-97bq.json` SHA `8ff643781a2c026c3aa098c0309455a6bdc7081616cdd1f76fe9f533af4b3a5e`; rows `rows-jev-97bq-final2.jsonl` SHA `1aea34111ed1af2c7e86605b69579997f5a297cddffbf0a7922a5f048e1ef6e4`; commit `efae399e`.
- N=234 valid rows; invalid 0, error 0, duplicate 0. Free incumbent nDCG@10 **0.4341683**, top-1 **0.6666667**; committed Jev nDCG@10 **0.4480190**, top-1 **0.7094017**; incumbent minus Jev deltas **-0.0138507** and **-0.0427350**. McNemar top-1: incumbent-only 18, Jev-only 28, discordant 46. Wilcoxon nDCG approximate p **0.03220**. Latency p50/p95/sum **25,938 / 75,119 / 7,555,737 ms**.
- Spend: OpenRouter usage before/after both **100.199757412**, unchanged; row usage 1,822,484 input / 710,243 output tokens. All row model IDs are `:free`; recorded comparator usage delta is $0 under the prereg gate.
- Boundary: one free model, one frozen 234-query NFCorpus slice, no new Jev calls; incumbent did not tie or beat Jev on either primary metric. Initial 15 transient/error rows were retried through checkpointed outputs; final receipt scores no invalid/error rows and retains no raw command/state text.

## jev-uncd gate question confirmation [live]

- Source/receipt: `work/jev-uncd/final-receipt.json`, fixed in `8c27e036`; bound prereg/reach: `1750bd56`/`ad1f6ea2`.
- Command: `work/jev-uncd/live.mjs` direct checkpointed runner (not kit/experiment/run.py); 558/558 Jev rows, model `jev-1.13.0`, 448,246 input tokens, $0.018826332. Catch 90/93; precision 90/230 vs existing 92/359; McNemar b=128,c=1,p=3.8e-37.
- Boundary: stratified sample rates only, not fleet rates; the `existingFlag` comparison uses an earlier Jev-derived flag, not a joined deterministic incumbent (`work/jev-1miz/final-receipt.json`: `dcg_joined_rows=0`, `NOT_COMPARABLE`). The 52 pre-revised-bar calls ($0.001774038) are disclosed and invalid for the revised bar; no free LLM comparator was part of this run and no gate promotion was made.

## jev-1lim held-out gate confirmation [live]

- Source/receipt: `work/jev-1lim/final-receipt.json`, rows `0cd1ae7c`; prereg/reach `174bdd04`/`310666ef`.
- Command: `work/jev-1lim/live.mjs` direct checkpointed runner (not kit/experiment/run.py); 396/396 Jev rows, model `jev-1.13.0`, 318,056 input tokens, $0.013358352. Weighted precision 67.3% vs 24.0%; weighted harmless flagged 1.4% vs 9.1%; sample McNemar b=141,c=2,p=1.8e-39.
- Boundary: all 196 flagged and 200/1,488 random-unflagged rows; three shared cmdSha retained and disclosed; 47 harm rows only, Wilson lower 0.924 reported not gated; no fleet-wide claim. `existingFlag` is an earlier Jev-derived flag, not a deterministic incumbent (`work/jev-1miz/final-receipt.json`: `dcg_joined_rows=0`, `NOT_COMPARABLE`). The 67.3% versus 24.0% pair cannot establish deterministic-baseline superiority.

## jev-dml3 unseen Score confirmation [live]

- Source/receipt: `work/score-amazon`, final receipt commit `b6a766be`; prereg/reach approval `2e4245aa`.
- Command: detached `kit/experiment/run.py --live`; 300 rows, Jev MAE 0.518 vs free comparator 1.328 on 274 paired valid rows; 26 comparator-invalid rows; seeded permutation p=1e-4; Jev input spend $0.0050.
- Boundary: preregistered bar required at least 278 paired valid rows and was not met; descriptive effect only, not a confirmation or promotion.

## jev-oioo Climate-FEVER confirmation [live / comparator NOT_RUN]

- Source/receipt: `work/jev-oioo/final-receipt.json`, strict-cut correction `838907da`; prereg/reach `85c18ece`/`41f35229`.
- Command: `work/jev-oioo/live.mjs` direct checkpointed runner; Jev arm 907/907, model `jev-1.13.0`, strict `>0.5` accuracy 592/907 = 65.3%, 507,681 input tokens, $0.021322602 before corrected receipt accounting. Free comparator: 86 scored and 821 HTTP-429 daily-quota rows quarantined NOT_RUN.
- Boundary: no free comparator result or paired confirmation; Jev arm is recorded only, and the comparator resume waits for quota reset.

## jev-za3a Climate-FEVER H1 dev replay [live / fail]

- Source/receipt: replay receipt commit `027902fc`; prereg `6e8622cc`.
- Command: Jev-only dev replay over 200 committed IDs; baseline 148/200, replay 147/200, replay-only 10, baseline-only 11, exact McNemar p=1.0.
- Boundary: H1 was set aside and H2 was next under the frozen decision; per-row replay results were not committed, so no held-out or fleet claim follows.

## jev-41c6 Climate-FEVER H2 dev replay [live / fail]

- Source/receipt: final pane-one verdict commit `15a25bb2`; same 200 dev IDs as H1, frozen aggregation any support >0.5 and no contradiction >0.5.
- Command: Jev-only dev replay; 199 valid rows plus 1 invalid bundle-shape row, H2 155 vs baseline 148, H2-only 14, baseline-only 7, exact McNemar p=0.189; model `jev-1.13.0`, 208,452 input tokens, spend $0.0088.
- Boundary: preregistered bar was not met; H3 is next, and one invalid row means this is not a held-out confirmation.

## jev-cqex Climate-FEVER evidence-label concentration [test / prereg]

- Source/prereg: `1e93d749`; frozen strata use the unique majority of five evidence labels, Noul >0.5, disagreement accuracy band [0.40,0.60], Wilson intervals per stratum.
- Command: NOT_RUN in the cited pane verdict; no live Jev result was cited.
- Boundary: only the keyless strata/preregistration contract is recorded; no accuracy, spend, or model claim.

## jev-k26w README kit live smoke [live]

- Source: bead `jev-k26w`; four README verbs were requested with key, model `jev-1.13.0`, and no `--fake` path.
- Command/source correction (2026-09-28): `work/kit-live-receipt-20260927.json` is present at SHA-256 `cfccf89ae3cf9e87314741946140844bd0a83726b29fbc9d04e419942457ac41`; its four README-verb rows report 4/4 exit 0, pinned `jev-1.13.0`, 3,472 input tokens and estimated input spend $0.000145824. The pane transcript was not linked by the earlier ledger row; that is distinct from an absent receipt. No call was rerun for this correction.
- Boundary: one previously recorded live call per verb, not an ask/gate smoke, a fresh public clone, accuracy benchmark, or new measurement in this pass. See the committed receipt for answer/usage rows; do not treat its existence as P9 public HEAD parity.

## jev-f4ea omp kit verbs L3 [omp-wired]

- Source: bead `jev-f4ea`; real omp session/tool-call acceptance requested for `jev_rerank`, `jev_claim_check`, and `jev_classify` plus a refused bad input.
- Command: real omp session invocation; the cited pane verdict/receipt was not present in the current tree for numeric extraction.
- Boundary: no unobserved L3 transcript or live spend is claimed in this ledger row.

## jev-5p56 omp Jev gate tool L3 [omp-wired]

- Source/receipts: implementation `34b36325`; refusal fix `4cd9d9b6`; L3 frames `633af8f8`; kit fix `bc59dc4d`.
- Command: `omp --mode=rpc` fresh-session tool invocation on `npm publish --access public`; model `jev-1.13.0`, 747 input/96 output tokens, 94 ms, estimated input spend $0.000031374; empty command refused before Jev.
- Boundary: L2/L3 proof is the cited filtered transcript; no command execution occurred and no automatic enforcement side effect is claimed.

## jev-a9fv tool-result injection gate [live]

- Source/receipt: prereg `da65e241`, feasibility `c0f431ed`, live receipt `929b661f`.
- Command: `work/jev-a9fv/run.mjs` direct checkpointed runner; model `jev-1.13.0`, 600/600 answered, 468,281 input/12,000 output tokens, spend $0.019667802; clean 5/300 false flags, planted catch 269/300, positions 86/92/91; jev-29s4 marker follow-up closed with 268/300 unmarked catches.
- Boundary: raw text was not committed; the planted strings are wrapped in literal `[UNTRUSTED TOOL OUTPUT]...[/UNTRUSTED TOOL OUTPUT]` markers, a marker confound that can inflate catch; the pane verdict retained it as a prereg caveat and requested non-author recount.

## jev-g1xw omp shadow logs [omp-wired]

- Source: implementation/check `7b7a7bb2`; pane-one check recorded a real gate-shadow row: model `jev-1.13.0`, maxScore 0.02, latency 184 ms, no error.
- Command: fresh `omp --profile codex -p` bash session; gate-shadow scored row observed.
- Boundary: websearch-rerank remained unproven (no post-change answered row with model `jev-1.13.0`); no web seam promotion or fleet claim.

## jev-bs5q omp pre-tool shadow hook [omp-wired]

- Source/fix: `b71ba831`; offline hook tests 6/6 and stage 70 reported 153 tests.
- Command: real pre-tool shadow path was attempted; the cited non-author check found no real gate-shadow row change and `existingFlag` unavailable on omp tool_call events.
- Boundary: no live Jev result, no comparable existing flag, no L3 closure, and no enforcement claim; the hook remains a candidate only.

## jev-p0-identify-consumer-e8uf demand inventory [offline / NO_CONSUMER]

- Source: bead comment 928; `EVAL.md:2460-2478,2650-2665,2715-2719` and `docs/demos/PLAN.md:151-173`. Existing native omp find consumed 1,595 Jev judge calls in the recorded 24-hour window, but its organic path-touch sample has 42 windows against the preregistered 100-window minimum. The external NFCorpus n=234 top-1 gain missed its separate nDCG promotion bar.
- Decision: NO_CONSUMER for a **new advisory intervention** and NO_ADOPTER for unrelated portability. Gate/injection shadow traffic and synthetic catches supply neither a named operator action/readback nor recipient- and data-class-specific export permission. Existing native omp use is not denied. P1/P9 stranger baseline can proceed; other branches await their named owner, decision, labels, and permission.
- Boundary: source-linked keyless inventory, not a new live Jev call, traffic-prevalence estimate, provider privacy authorization, or an organic outcome.

## jev-p1-stranger-baseline-przc clean checkout and installer [offline / partial]

- Source: fresh local clone `var/agent-tmp/jev-p1-baseline-20260928` at `80f05e53f5a47feedb31fb3446ab02ed28d013b8`, with `npm ci --prefix kit` exit 0; no TypeSafe key sent. `env -u TYPESAFE_API_KEY -u JEV_API_KEY npx --prefix kit --no-install jev doctor --robot` exited 2 with `status:NOT_RUN, reason:no key`. Five fake CLI verbs (ask Choice, verify, score, classify, gate) exited 0 on their committed fixture paths. `askJevChoice` with an injected 401 `fetchImpl` and synthetic key returned `ok:false, reason:http`; zero live requests.
- A separate no-SDK checkout `var/agent-tmp/jev-p1-no-sdk-20260928` returned exit 1 (`kit/dist/client.js` missing) before doctor could produce JSON; this is not a successful structured no-SDK refusal. Installed kit dependencies do include `@typesafe-ai/sdk`, so a clean installed checkout cannot isolate an absent SDK without changing its dependency graph.
- Current-tree fix: `jev_claim_check` now refuses any digit-bearing claim before key lookup/model invocation; `node --test work/jev-claim-check/claim-check.test.mjs` passed 3/3 after the planted numeric RED. Kit installer no longer writes `.omp/config.yml`; `extensionActivation: MANUAL_REQUIRED` and legacy managed-config refusal preserve host extension lists. `node --test kit/test/install.test.mjs` passed 4/4; `node --test kit/test/*.test.mjs` passed 49/49; current CLI installed into `var/agent-tmp/jev-p1-install-20260928` with explicit manual activation. Its negative tests cover unmanaged collision, managed-file edit, and legacy config without overwriting operator bytes.
- Post-fix fresh checkout: local clone `var/agent-tmp/jev-p1-fixed-20260928` at commit `a1bd64bb`, `npm ci --prefix kit` exit 0; keyless doctor exited 2/`NOT_RUN`; `jev omp install --dir var/agent-tmp/installed --robot` exited 0 with `extensionActivation:MANUAL_REQUIRED`, and `test ! -e var/agent-tmp/installed/.omp/config.yml` printed `NO_CONFIG_WRITTEN`. This establishes copied-file behavior from a new checkout, not an omp load event.
- Stage-15 disposition: user-observed aggregate failed four enforced string rows and timed out. Numeric refusal path was behavior-fixed; `foundation/kit/claims.tsv:184,284-285` still pin superseded source shapes (seat cut imported from `work/jev-a9fv/seat.mjs`, rerank now 2–20 Choice top-1, not 2–30 Score). The aggregate was **not rerun** and remains RED/NOT_RUN-after-change. Do not weaken its needles merely to pass; a separate RED-capable proof migration must precede any §4 claim.
- Boundary: keyless/fake/injected tests are not live authorization, L3 extension loading, an organic consumer, or a paired model result. `ubs` scanned the changed TS/JS files, exit 1 with four pre-existing false-positive critical token comparisons in `kit/bin/jev.mjs`; no clean UBS claim. No scratch files or tests were deleted.

## jev-p9-stranger-quickstart-2srw [offline local / public NOT_RUN]

- Local source `4b0a588b` changed README quickstart clone→cd sequence, pinned four-call smoke boundary, published-branch caveat, and stranger runner cwd/revision guard. `python3 scripts/stranger-run-jev-playground.py --selftest --expect docs/demos/upstream-repro/stranger-run-expected.tsv` passed its untracked-input and deliberately altered Banking77 96.1%-versus-80.1% RED arms. `ubs scripts/stranger-run-jev-playground.py` exit 0, 0 critical/0 warning.
- Outside-repo local clone at `var/agent-tmp/jev-p9-user-20260928/jev_playground`: `git clone /Users/josh/Developer/jev jev_playground` exit 0; `npm ci --prefix kit` exit 0; deliberately keyless `jev doctor --robot` exit 2/`NOT_RUN`; `jev ask choice --fake ... --robot` exit 0 with fixture choice `c1`. P1 separately exercised injected 401 and unmanaged install collision. This is a fresh clone of **local HEAD**, not the public URL.
- A real public URL clone through the keyless stranger runner refused before grading: published GitHub SHA `7bf796168e61ad873fa50e0a463ffa1565add742` differed from local source `4b0a588b3e12d2ca9d86b2dda3658f670a047022`; exit 1. Independent non-author read-only review with `omp --model=openai-codex/gpt-5.5` returned FAIL for public-ready because these SHAs differ; local fake/live, copied/loaded, and stage-15 RED wording passed source audit. No paid Jev call, push, or public release was performed.
- Boundary: corrected public guide exists locally but is **not published**; after authorized publication rerun the exact README block from outside against the published SHA, including keyed-error and collision refusal, then re-audit claims. Stage-15 aggregate remains RED; no L2/L3 or consumer-benefit claim. A doc citation checker catches metric numbers attached to runnable commands but does not validate all free prose.

## jev-p15-contain-automatic-egress-810p inventory checkpoint [source-only / NOT_CONTAINED]

| Configured/source path | Trigger, recipient and state | Side effect and current boundary |
|---|---|---|
| `.omp/hooks/pre/jev-gate-shadow.ts` + `.omp/hooks/jev-shadow-worker.ts` | bash tool callback, raw command; TypeSafe through inline and detached calls | two callback names can race; worker resolves Infisical key before job read; no shared atomic pre-request cap |
| `.omp/hooks/post/jev-gate-observe.ts` | bash command (also a local raw-command sidecar); TypeSafe after filters | key resolution occurs after filters; no owner-approved recipient/data-class admission |
| `.omp/hooks/post/jev-injection-shadow.ts`, `jev-web-search-rerank.ts`, `jev-webscreen.ts` | raw tool result or web query/snippets; TypeSafe | injection/web-search spawn detached children; web-search also runs inline; webscreen can rewrite tool result; hash-only disk rows do not redact provider input |
| `.omp/hooks/pre/jev-compact.ts` | compaction context/history; TypeSafe when key present | optional registration, model inherited from binding; no verified current-session containment |
| `.omp/extensions/jev-review.ts` → `work/omp-jev-review/src/index.ts` | git diff/show tool result; TypeSafe | key setup at extension load, git re-execution before scoring; project config does not explicitly list this extension, native discovery/actual load UNKNOWN |
| `.omp/config.yml:84-108`, `~/.omp/profiles/jev-lab/agent/config.yml:25-30` | configured project Jev callable tools/extension list and profile-local automatic observer/review/route | project list replaces profile arrays; lab observer fetches raw bash command before checking ID (`omp-jev-observer.ts:65-88`), route sends prompt (`omp-jev-route.ts:71-100`); effective load in each live session UNKNOWN |
| four profile judge roles (`claude`, `codex`, `grok`, `muse` configs), their `models.yml` | native omp `find`/judge and other model-role calls, TypeSafe alias `jev-latest` | credential command resolves lazily through Infisical; this is not gated by a project hook; historic 1,711 calls/24h in `EVAL.md:2460-2478`, not a current-session census |
| `scripts/fleet-idle-watch.py:349-384` → `scripts/fleet-jev-shadow.mjs`, and registered launchd `ai.zeststream.jev-latest-canary` | worker status, or the fixed public sky-state; TypeSafe | `omp ps` listed fleet-idle-watch exited(143), not proof of all jobs absent; `launchctl list` showed canary registered with last exit 0, not current API trace |
| `.omp/hooks/post/jev-find-rank.ts`, project `.omp/mcp.json` | local rank/read path, and a configured non-Jev MCP server | no Jev provider invocation in inspected sources; not an absent-export proof for every live profile |

Source inventory only; no hook edit, owner approval, credential lookup, key, fake recorder, child spawn, restart, or deliberate live Jev experiment for this checkpoint. omp's normal `find` model-role traffic may still use Jev and was not intercepted or counted here. Every live session's already-loaded modules remain UNKNOWN; editing files cannot retroactively contain one. Next prerequisite: project/session owners approve quiescence/restart and the exact recipient, purpose, allowed minimal fields, and revocation for any continuing automatic route. Until then, new automatic traffic must remain unapproved, and no no-export certificate is claimed.

## jev-p15-contain-automatic-egress-810p source-default-deny pass [offline / active sessions NOT_CONTAINED]

- Change: project gate-shadow, gate-observe, web-search rerank, webscreen, injection shadow, review extension, and compaction registration now refuse automatic TypeSafe export without an exact offline synthetic event/transport match. A key, environment switch, or event ID alone is not approval. Gate-observe refusal writes a SHA-256 join key and a constant `cmd` marker, not the raw sidecar or prefix. The detached gate worker and fleet shadow helper explicitly exit 2 before reading stdin or acquiring a credential; `JEV_FLEET_SHADOW=1` no longer starts the fleet provider worker. The pre-existing local deterministic webscreen enforcement remains active, not bypassed.
- Offline commands: `node --experimental-strip-types --test .omp/hooks/pre/jev-gate-shadow.test.mjs .omp/hooks/post/jev-injection-shadow.test.mjs .omp/hooks/post/jev-webscreen.test.mjs .omp/hooks/post/jev-web-search-rerank.test.mjs .omp/hooks/post/jev-gate-observe.test.mjs` passed 51/51 before the final gate-observe sidecar ordering fix; its focused full suite then passed 21/21. `node --test work/omp-jev-review/test/review.test.mjs` passed 22/22. `cd compaction && npm test && npm run typecheck` passed 39/39 and typecheck. `python3 -m unittest work.fleet-idle-watch.test_fleet_idle_watch && python3 scripts/fleet-idle-watch.py --selftest` passed 39 tests and 7/7 classifications. Planted RED arms: worker refusal and watcher env-flag denial failed before their change; gate-observe raw command/sidecar tests failed before moving admission ahead of writes; review `commandSha` assertion failed before replacing raw command entries.
- Fresh keyless omp RPC session: `negotiate_protocol` v2 then prompt for one synthetic bash command `printf P15_NO_EXPORT_4b92` reached `tool_execution_start`, `tool_execution_end`, terminal `prompt_result`; local gate-shadow row at `~/.local/state/jev/gate-shadow.jsonl:733` has `cmdSha=e4f3b1c6358f34b81f1bcc5420f68d6bcb1519dfb34baf6da9a9216f88e37a0b`, `status:not-run`, `reason:permission-denied`, no model/tokens. The corresponding gate-observe row at `~/.local/state/jev/gate-observe.jsonl:13107` has the same hash, `cmd:[permission-denied]`, `status:not-run`. This is one newly loaded synthetic bash event, not a fleet certificate or a provider invocation.
- Adverse live observation: the **already-running** editing session still has its old gate-observe module loaded; its own bash checks at `gate-observe.jsonl:13104-13106` were scored by `jev-1.13.0` despite the edited source. Those three rows bill 2,307 input tokens, $0.000096894 at $0.042/million input tokens; other session calls in this pass were not completely enumerated. No deliberate paid comparison or raw customer-state test was performed. All four active pane owners were asked for a coordinated safe restart window; none had replied as of this entry. No restart was performed, no loaded-session containment is claimed. The profile-local `jev-lab` extension list, native judge model roles, and scheduled public-state canary remain separate UNKNOWN/UNGATED routes pending owner/scope review.
- Diagnostics: `ubs` on six changed source files exited 1 (four command/string-identity comparisons flagged as secret-token comparisons; 20 warnings including legacy watcher subprocess lifecycle); not a green scan. `ripwire . --quality-delta` exited 2 with 20 gated findings against dirty `git-HEAD`, including touched hook churn/error-masking and unrelated concurrent changes; not waived or called green. The aggregate stage-15 claim gate remains RED, not rerun here. Boundary: source and one fresh-session refusal only; no owner-approved recipient/data-class contract, atomic cross-process pre-request cap, active-session coverage proof, native judge containment, or L4 organic benefit. Automatic traffic must remain disabled until those prerequisites and owner windows are independently evidenced.

## jev-u06-provider-output-redaction-noom [offline / model-readback synthetic RPC]

- Reused the existing project-level `.omp/secrets.yml` TypeSafe-shaped regex and `.omp/config.yml` `secrets.enabled` setting from closed `jev-xw3f`; no second regex, source change, credential lookup, or real key. `omp --profile claude config get secrets.enabled` returned `true`. `python3 -m unittest discover -s work/omp-secret-probe -p test_omp_secret_probe.py` passed 13/13 keyless **verdict-shape** tests; these tests alone do not exercise a provider request.
- 2026-09-28, three new `omp --profile claude --mode=rpc --max-time=80` sessions negotiated v2 and actually called `bash` with `printenv JEV_PROBE_VALUE`. A randomly generated 107-character synthetic TypeSafe-shaped value was introduced through the child process environment, not in the prompt. With project masking enabled, the terminal assistant answer reported `LEN=33 HEAD=$$TYPES TAIL=:L$$`, not the 107-character value; the terminal answer contained neither the fake value nor its random suffix. With `JEV_PROBE_VALUE=public-control-42`, the assistant reported `LEN=17 HEAD=public- TAIL=l-42`, the unmasked benign control.
- Planted RED: a fresh RPC session received an in-memory `--config /dev/fd/<pipe>` overlay setting `secrets.enabled: false`; with the same synthetic value the `bash` tool ran, and the terminal assistant answer reported `LEN=107` plus the fake prefix and random suffix, with no `$$TYPES` placeholder. This demonstrates that disabled obfuscation exposes the token to the model; it is not an inferred result from source text. No fake value or RPC transcript was written to the repository ledger.
- Boundary: the RPC `agent_end` history retains a raw fake-containing `toolResult` even in the masked case; the model's final readback is masked, but this pass did **not** capture the exact outbound provider request or prove raw host/session-log storage secret-free. Two additional fresh `codex`-profile sessions produced a masked readback through `eval` invoking `tool.bash`, not a direct bash `tool_execution_start`; this is **not** direct-route equivalence for the original Codex leak. No already-loaded fleet sessions, other profiles, arbitrary secret shapes, native judge traffic, or authorized TypeSafe payload were covered. Independent non-author RPC reproduction was requested; U-06 remains open pending that result. Jev live calls: 0; TypeSafe spend: $0.

## jev-u07-infisical-argv-gi70 [offline / synthetic Infisical machine identity]

- 2026-09-28. Before: `work/jev-client/src/infisical-key.ts` called `infisical login --method universal-auth --client-secret <value>`; its injected child runner received the synthetic machine secret in argv **and** env. A new test first failed with the explicit marker `machine secret reached child process` on the unchanged fallback. The installed Infisical CLI's `login --help` requires `--client-secret`; an env-only synthetic invocation refused with `required flag(s) "client-id", "client-secret" not set`. Infisical's [universal-auth login API](https://infisical.com/docs/api-reference/endpoints/universal-auth/login) accepts `clientId`/`clientSecret` in the POST body.
- Change: user-session CLI lookup stays first. On its failure, a bounded direct POST to the configured Infisical API login endpoint obtains a machine token, then the existing `infisical secrets get` child receives only that token in its environment. The machine client secret is not placed in child argv or child env. No real credential file was accessed, and no real Infisical or TypeSafe request was made. A local fake HTTP server accepted the synthetic credentials and returned a token; the fallback returned a synthetic key with two child calls and **zero** child arguments/environment entries containing the machine secret. Local 401 refusal returned no key and made no second child call.
- Additional planted RED: default `fetch` followed a local HTTP 307 and forwarded the synthetic login POST body to a second server (`redirected=1`). Adding `redirect: "error"` made the same test pass with `redirected=0` and no key. This is an output-route safety fix, not a Jev score.
- Verification: `node --experimental-strip-types --test work/jev-client/test/*.mjs` passed 69/69; TypeScript `tsc --noEmit --target esnext --module nodenext --moduleResolution nodenext --types node --typeRoots ./node_modules/@types ../work/jev-client/src/infisical-key.ts` from `kit/` exited 0. `ubs` on the two changed files exited **1**, with seven critical findings (synthetic test values and secret-named validation/previous env tests) and two warnings; **not** a clean gate. `ripwire work/jev-client --quality-delta` reported zero regressions and zero gating rows against git HEAD (no pinned quality baseline). Non-author review was requested from a second pane; U-07 stays open pending its verdict.
- Boundary: local fake HTTP/runner exercises auth routing and known bad redirects, not an actual machine identity, provider network, output-transcript redaction, credential file permissions, or Jev efficacy. Live Jev calls: 0; TypeSafe spend: $0.

## jev-p15-contain-automatic-egress-810p observer admission slice [offline / P15 NOT_CONTAINED; U-06 UNKNOWN]

- 2026-09-28, code commit `b02f5c4c`. The `jev-gate-observe` pre-provider decision now refuses an otherwise approved synthetic bash event when its session is missing or `"unknown"`, before the full-command sidecar, Infisical resolver or asker runs. Test input uses the real recorded `git status --porcelain=v1` `tool_call` shape at `work/omp-guard-rule/fixtures/session-pinned.jsonl:2`, with a substituted synthetic event ID; no real command or credential was sent.
- Planted RED before the fix: the missing-session test failed with `1 !== 0` key lookups. After the fix, denied ID and sensitive-command variants produced zero fake HTTP attempts and zero key lookups; the eligible harmless variant traversed the observer and real kit/SDK bundle path into exactly one captured fake HTTP POST to the pinned `jev-1.13.0` endpoint. The captured synthetic state contained only the recorded harmless command and fixed gate context; no key in its JSON body. This is an instrumented **observer route**, not a hook-loaded omp provider-request capture.
- Checks: `node --experimental-strip-types --test .omp/hooks/post/jev-gate-observe.test.mjs` passed 23/23; the full `.omp/hooks/post/*.test.mjs .omp/hooks/pre/*.test.mjs` run passed 68/68. A separate keyless Node invocation of the registered hook with that recorded event returned `not-run`, `NOT_RUN reason=permission-required`, zero requester and resolver calls. `git diff --check` exited 0. `ubs` on the two changed hook files exited **1** (7 existing token-equality heuristics in test cleanup; 10 warnings including new JSON.parse calls on a pinned fixture/fake request); it is **not** a green quality gate.
- `ripwire . --quality-delta` exited **2** against dirty `git-HEAD`: 6 major gating rows outside this observer slice, including the separately owned U-07 machine-key repair in this same session; the edited observer/test symbols appear only as minor verbosity/churn rows. No quality-delta green claim or alteration of unrelated files.
- U-06 readback comparison remains the one in `EVAL.md:2835-2838`: terminal model readback was masked while the archived raw `agent_end` toolResult retained the synthetic value. The independent masked probe was `UNCLEAR`; its disabled fresh attempt lacked `agent_end` fields and is `NOT_RUN`. `kit/src/client.ts` `observedFetch` records this Jev hook's HTTP attempt, **not** the outbound omp model-provider request or host/session-log retention. No assertion that U-06 provider masking or whole-session leak safety passed. P15 still lacks the loaded-session/profile/background census, all-route fake recorder, shared cross-process admission and attempt cap, owner-approved recipient/data-class contract, and fresh-session positive/negative proof. Live Jev calls: 0; TypeSafe spend: $0.

## jev-aykj stage-15 proof migration [offline / NOT_COMPLETE]

- 2026-09-28. Replaced the stale `screen-cut` export assertion with the registered `work/nev-injection/seat-guard.test.mjs` boundary/fail-safe test (0.5 flag, 0.499 pass, malformed review). `docs/LEDGER.md` now distinguishes the current 2–20 Choice top-1 interface and its failed NFCorpus full-rank bar from the 2026-09-24 historical 2–30 Score experiment; old Score registry rows are historical, unenforced, not retargeted to Choice. The claim-coverage floor remains **114/115** and the unitizer pin is unchanged.
- Offline checks: `node --experimental-strip-types --test kit/test/rerank.test.mjs kit/test/omp-tools.test.mjs work/nev-injection/seat-guard.test.mjs` passed 18/18 (captured FiQA qid 10034 and recorded Choice, 2/20 positive, 1/21 no-ask refusal, malformed screen refusal). A temporary `kit/src/rerank.ts` limit of 30 caused the `21` test to fail; the limit was restored to 20 and the focused suite passed. `bash foundation/gates.d/15-kit-claim.sh` passed 431 enforced patterns, 0 failed, 3 skipped; ledger coverage 118/119 exceeds the unchanged floor. This stage checks text, not proof execution.
- **Boundary:** the earlier aggregate stage-15 424 pass/4 fail + timeout at `EVAL.md:2799` remains RED/NO-CLAIM. The aggregate and full selftest have **not** passed after migration. The selftest's `awk` removes an entire ledger line, not one unit: independent unitizer recount found **three** covered units on `docs/LEDGER.md:15`, so removal leaves 115/116 (not 117/118) against the unchanged 114/115 floor. The checker still trips on its missing pattern, but a selftest demand for floor RED on that removal is invalid while the real ledger has headroom at 118/119. A proposed floor-preserving repair would assert the removed ledger's measured coverage ratio decreases while retaining checker RED and the separate unregistered-claim floor RED; `kit-guard B7` refused editing `foundation/gates.d/15-kit-claim.sh` and requires a documented bead plus a human relaunch with `KIT_GATE_EDIT=1`. `ubs` on three modified tests exited 1 (existing test-cleanup token-equality heuristic), not a green scan. No live model calls or paid comparison; Jev spend $0. Non-author verification and final gate outcome remain pending.

## jev-p9 publication secret-scan check [offline / public NOT_RUN]

- 2026-09-28. Before publication, `bash foundation/gates.d/30-no-secrets.sh` exited 1 and named `.omp/hooks/post/jev-injection-shadow.test.mjs:10` as a possible TypeSafe key value, with the value withheld. That line assigned the explicit `synthetic-never-send` test sentinel directly to `TYPESAFE_API_KEY`; it was not a live credential. The fixture now binds the same sentinel to `syntheticKey` and passes it by reference. The test still checks that the worker never emits the sentinel; no exemption or gate threshold changed.
- After the fixture edit, `bash foundation/gates.d/30-no-secrets.sh` exited 0 across 4,521 committable files with 8 existing allowlisted hits. `node --experimental-strip-types --test .omp/hooks/post/jev-injection-shadow.test.mjs` passed 4/4; the full `.omp/hooks/post/*.test.mjs .omp/hooks/pre/*.test.mjs` suite passed 68/68. `git diff --check -- .omp/hooks/post/jev-injection-shadow.test.mjs` exited 0. `ubs` scanned the changed test with 0 critical, 3 pre-existing JSON.parse warnings and exited 0.
- **Boundary:** this is an offline fixture and secret-scan repair, not a review of all 30 unpublished commits or a release certificate. Public origin/main was `7bf796168e61ad873fa50e0a463ffa1565add742` while local HEAD was `8b94eaa6f227585ea01ca454cb757e26c2e3fe7d` at the check; an unqualified push would publish 30 commits and 36 files, including credential and hook code. The exact-command/consequences confirmation and a frozen-range review are missing. No push, public stranger clone, live Jev call, or paid comparison; TypeSafe spend $0. Aggregate stage 15 remains RED per the prior row.

## 0927 plan-to-bead conversion and four-pane review (2026-09-28) [offline / worktree-hash]

- Source: `docs/0927_reality_plan.md` SHA-256 `f6cf796592e4e42a96ddb23cc539fa55d7a210b886b692f8b27f792efc416abe`; `.beads/issues.jsonl` SHA-256 `7c01857434a816c1561220570e87f30ee29bd1643dcde36499639d6ea3a6bae1`. Eighteen existing P0–P9/P11–P15/U04/U06/U07 records cover the plan; P10 is the conversion operation and conditional branches remain deferred. The bead DB was snapshotted before checks in `.beads/recovery_20260928T175317Z/`.
- Graph change/readback: P1 reopened because its post-fix stranger evidence spans different source states; P9 remains blocked. Added direct P5→P15, removed false U04→`jev-wiya` and stale `jev-k9z.3`→closed `jev-umo`; `jev-k9z.3` remains BLOCKED. U04 has an external synthetic-provider wake and advice remains off. Updated P0's negative to distinguish existing native omp judge consumption from missing **new advisory** demand, P4's five outcomes, active bead acceptance headings, and U07's unapproved first HTTP origin/inherited child-env blockers. Independent pane-5 source audit REFUSED the historical `jev-k9z.3` terminal NO_SEAT claim: its ≥0.25 cutoff was Bit1, reused for Bit2 only post-score on a different cohort; corrective bead comment 942 records the retry condition.
- Checks run: `br config get db --json` named `.beads/beads.db`; `br show`, `br sync --status --json` and `br doctor --json` found operational storage with no DB/JSONL drift (doctor `workspace_health:healthy`, `ok:false` for non-corruption warnings). `br dep cycles --json` returned zero cycles; `br ready --json` showed no newly unassigned optional branch; `git diff --check -- docs/0927_reality_plan.md .beads/issues.jsonl` exited 0. Four panes received review packets using `ntm send`, with fresh `ntm --robot-tail` delivery readbacks. Pane 2's F3, pane 4's corrected current-hash round and pane 2's F5 each reported **zero new plan/bead defects** on the identical hashes above. F5 explicitly checked self-containment, directed graph/cycles and five rationales; its structural-diff check was NOT_RUN. Pane 4 checked those and stated only the narrow F3→F4 hash-equality structural identity. The integrator can also compare the reported F4 and F5 SHA-256 identities, but neither reviewer compared the final version bytewise to the pre-repair version.
- **Boundary:** these are read-only plan/bead reviews on **uncommitted worktree bytes**, not the plan's two-clean-round **committed-snapshot** gate or a runtime pass. No Jev/TypeSafe API call, paid comparator call, key access, product run, code-suite run, public push or commit was performed by this conversion pass; TypeSafe spend $0. NTM reviewer turns are separate subscription agent work, not included in that spend claim. P15 loaded-session/profile/background containment remains NOT_CONTAINED/UNKNOWN, U06 provider/raw-log boundary UNKNOWN, U07 source path BLOCKS_BUILD pending implementation and independent fake-recorder proof, and P1/P9 public stranger parity remains open. The older `79cbdf4b` planning 2/2 is historical, not transferable.

## 0927 committed-plan review reset and P0 demotion (2026-09-28) [offline / planning, NOT execution-ready]

- Reviewed commit `e1a3af1cbd5b219f1389b94850ae914f7c421c91` (parent `63ecacdd`): plan SHA-256 `a130038f3588aa22760cf5ae048ee534cdc03c4d70865d0cdd836c6fb81843ed`; committed `.beads/issues.jsonl` SHA-256 `2d138afee8d5b4de826ef4966501f2249c055c5b1bba996c76bc743b37f48f7f`. The live JSONL retained three unrelated uncommitted peer rows; all 18 plan-linked committed rows matched the live records before the P0 correction.
- C1's first zero-new report named the older worktree `f6cf7965`/`7c018574` hashes and was **INVALID**, not review credit. Pane 2 then read both exact committed blobs and reported zero new findings with P15/U07 self-containment, graph, five-rationale and immediate-predecessor checks. Independently, pane 4 read the same committed blobs and found **one new plan defect**: line 74 still called P1 closed although the P1 bead was OPEN. Its C2 verdict reset the post-conversion committed-snapshot count to **0/2**. The plan status line was corrected in the worktree, not retroactively in `e1a3af1c`.
- A distinct pane-5 bounded-source audit found P0's terminal closure **UNCLEAR**: `EVAL.md:2460-2478,2650-2665,2715-2719` and the cited NFCorpus/find/gate receipts show no named NEW advisory operator/adopter in that inventory, but 1,711 native omp judge calls refute a global NO_CONSUMER claim; find outcome joins are 42 against the preregistered 100-window bar, and the NFCorpus +0.026947 nDCG delta missed its +0.05 bar. P0 comments 926/928 were author-only and comment 938 used the coordinating-pane alias, not a distinct reviewer. Correction comment 944 withdrew that independent label. P0 was reopened, then marked DEFERRED under HazySpring with an evidence/permission wake; WindyLantern's own comment 947 records the independent **UNCLEAR**, not a PASS. P1 remains OPEN and P9 OPEN; the P0 dependency now prevents P1 from appearing in `br ready`.
- Checks after demotion: `br dep cycles --json` returned zero; `br ready --json` listed only assigned `jev-wiya` and `jev-aykj` (P1 removed); `br show` showed P0 deferred and P1 dependent on it. `br sync --status --json` reported `dirty_count=0`, `jsonl_newer=false`, `db_newer=false` after comment 947; `git diff --check -- docs/0927_reality_plan.md .beads/issues.jsonl` exited 0 before the final snapshot commit. No existing failure or live Jev arm was rerun.
- **Boundary:** this row reports a failed planning review and a conservative status demotion, not execution readiness, a negative finding for all Jev use cases, or runtime containment. The corrected plan/P0 bead bytes require a new committed snapshot and two independent whole-plan zero-new reviews. P15 loaded-session safety, U06 provider-output boundary, U07 child-env/origin and P1/P9 public parity remain NOT_RUN/UNKNOWN or blocked as recorded in their own beads. No API/key use, paid comparator, session restart, public push or product-run proof; TypeSafe spend $0. Two extra isolated reviewer dispatches returned 429 and are `NOT_RUN`, not review credit.

## 0927 R1 graph contradiction: independent stranger baseline (2026-09-28) [offline / planning, NOT execution-ready]

- R1 read the committed `d57ce1d67a3fc3bc0d03344defff90b9b5068185` plan SHA-256 `3309c5a56614ae1bea65be3b7f3ce29a37de1c3c4a96086b0d1d50f9c714ec5b` and issues SHA-256 `18dbc5036a213cc49630db9971c1eda77bb690c377e9c21585237ce2d869c6dc`. Pane 2 reported **one new graph defect**: P0 acceptance permits baseline correction after NO_CONSUMER, yet P1 had a `blocks` edge to the now-DEFERRED P0; P9 depended on P1, so both were hidden from `br ready`. Count reset to **0/2**; earlier zero-new reviews of other blobs do not count. Pane 3's separate read-only review also targets the old commit, not this uncommitted repair.
- Repair in the next snapshot: remove only P1→P0 `blocks`, clarify P0/P1 bead descriptions and plan status/section/wake lines. P1's bounded fresh-clone/keyless/fake/keyed-error and stage-15 diagnosis is independent of P0's advisory-demand decision; P9 still waits for P1. P0-dependent P2/P3/P8/P11/P14 and their conditional successors retain demand and provider safety prerequisites. P1 comment 948 records scope and NO-CLAIM.
- Positive/negative graph check: before repair, `br ready --json` contained only assigned `jev-wiya` and `jev-aykj` while P0 was deferred. After removing the edge, it listed assigned P1 in addition to those two, but **not** P9 or conditional advisory children. `br show` returned P0 `deferred`, P1 `open` with no dependencies, P9 `open` depending on P1; `br dep cycles --json` returned zero cycles. `br sync --status --json` reported `workspace_health=healthy`, `dirty_count=0`, `jsonl_newer=false`, `db_newer=false`; `git diff --check` on plan and issues exited 0.
- **Boundary:** graph activation establishes only that bounded baseline work is eligible, not that its clean-clone acceptance passed. This repair neither closes P0 nor relaxes P15 loaded-session containment, U06/U07 provider boundaries, P9 publication parity or stage-15 RED. No live Jev/API call, paid comparator, key access, code test, session restart or public push; TypeSafe spend $0. Recommit the new plan/bead state and obtain two independent whole-plan zero-new reviews on those exact committed blobs before calling the post-conversion plan reviewed.

## 0927 R2–R4 follow-up: stale conditional statuses, P14 safety, P9 public HEAD (2026-09-28) [offline / planning, NOT execution-ready]

- Pane 3 independently reviewed the old immutable `d57ce1d67a3fc3bc0d03344defff90b9b5068185` (plan SHA-256 `3309c5a56614ae1bea65be3b7f3ce29a37de1c3c4a96086b0d1d50f9c714ec5b`; issues `18dbc5036a213cc49630db9971c1eda77bb690c377e9c21585237ce2d869c6dc`) and reported **one additional new finding**: P2/P3/P5/P8/P11 descriptions still stated terminal P0 `NO_CONSUMER`/`NO_ADOPTER` even though P0 was DEFERRED after WindyLantern's UNCLEAR. Five affected child contracts now name current P0 DEFERRED/UNCLEAR, a consenting owner/permission/same-item evidence wake, and the later bounded negative as STOP, not activation.
- Pane 2's first full-plan review of committed `74fecbeac8d607acbd7bb17dcad2a1c00fc72596` (plan SHA-256 `9fd8dcc8213f75912b4d642895f3de2078535a1b04049e1addfa4fafdb9086a1`; issues `623671119a52ad021d3f1865fd26d36f741a952f80c94459383572067169494c`) returned **zero new findings** with four planning checks, but that is **not** a clean 1/2: pane 3's independent older-target finding persisted and pane 4's independent whole-plan review of the same `74fecbea` reported **two new defects**. R4 found P14 could become ready on P0/P15 alone despite U06 result privacy and U04/U07 machine-identity route remaining pending, and P9/README used `git cat-file -e` object presence as public-release parity without binding reviewed SHA to the cloned default HEAD. Count remains **0/2**; no zero-new review on a defective predecessor is promoted.
- Repair for the next immutable snapshot: P14 now depends on **P0, P15, U04, U06, U07** for the current `work/jev-client` fallback route, with a separately reviewed route/dependency change required for an SDK-direct alternative. P14's bead and plan distinguish current hash-only `not-run` source from older possibly loaded raw-result paths; the former does not prove the latter contained. P9's bead and README require the exact public origin URL and cloned HEAD to equal the reviewed SHA; a descendant may be used only after literal positive and refusal arms are rerun there. README's reviewed local commit is `4b0a588b3e12d2ca9d86b2dda3658f670a047022`; public default was observed at `7bf7961`, so parity remains NOT_RUN. P9 comment 949 and P14 comment 950 record the respective REDs.
- Post-repair graph smoke: `br ready --json` listed only assigned `jev-wiya`, `jev-p1-stranger-baseline-przc` and `jev-aykj`; neither P9 nor P14 nor deferred advisory branches became ready. `br show jev-p14-injection-advice-lqkm --json` returned five blocking dependencies, with P0/U04 deferred and P15/U06/U07 in progress. `br dep cycles --json` returned zero. `br sync --status --json` reported `workspace_health=healthy`, `dirty_count=0`, no DB/JSONL drift and 405/405 unique/exportable rows. `git diff --check` on plan/issues/README exited 0.
- **Boundary:** these are plan/bead and honest public-boundary corrections, not P14 runtime containment or P9 public-clone proof. No provider fake-request run, Jev/key access, paid comparator, source code test, session restart, public clone/push or reported-failure rerun in this pass; TypeSafe spend $0. P15/U04/U06/U07 remain independent safety prerequisites and P1/P9 remain unproven against their own acceptance. New committed snapshot plus two independent whole-plan zero-new reviews required before calling the conversion reviewed.

## jev-vg4s HealthVer Jev-only arm [live / paired comparator NOT_RUN, 2026-09-28]

- Recorded source: `work/jev-vg4s/receipt-jev.json` (`LIVE_COMPLETE`, created 2026-09-28T02:29:43Z), prereg SHA-256 `27392472df4d74713ca23a89fea532e508d05f85f85038acb9cca4fe6fec6adb`, corpus SHA-256 `24bdc0e651e1694652fc82bf4e2a167170e9b2aceeb2037efcaacd752d106d02`, states SHA-256 `d5ef3bbb2cc9b6de47caa731435ff6698fb0e45c22866cd0ba5ee39b4ce6559e`. The scored row SHA-256 cited by the plan is `44bd51ec98b79fc66c072e54c625268763cd1e7dbfcee69d564bd0862674c5bf`.
- Receipt: pinned `jev-1.13.0`, 840/840 source rows, invalid 0, 339,667 input and 16,800 output tokens, Jev input spend $0.014266014; plan recount reports 622/840 strict-cut rows and 832 distinct state IDs (eight repeated inputs). These are receipt and earlier recount claims, not calls or a re-score made during this ledger repair.
- **Boundary:** comparator `none` in the live receipt. The paired permitted `:free` comparator is preregistered and date-gated after 2026-10-01T00:00Z; no paired win, independent 840-state claim, consumer benefit or new TypeSafe call is established here.

## 0927 source-provenance and graph-review repair (2026-09-28) [source-only / planning, NOT execution-ready]

- Immutable review target `fd15772bdd860d9845db50f4feb0163fb0d6119b`: plan SHA-256 `3b12e220c6eaa2d0b8ddd6d8ad7e4f0b633fcc87490469e0b673c7179ed9183e`, issues SHA-256 `5c881a8ad2a0896f00c321eb3ed1e7d3993aee3245845939f63bd101c315c860`. Pane 2's fresh full-plan review reported zero new after demoting a false semantic cycle; pane 3's independent full-plan review reported a **new operational handoff defect**: U04 comment 941 waited on a `jev-wiya` fake receipt while `jev-wiya` was blocked by P5. Count is **0/2 after this finding**, not two clean rounds. Pane 5's separate read-only source-provenance audit found stale P1/P9 diagnoses, a wrong P0 issue-line citation, a missing HealthVer ledger row, a present `jev-k26w` receipt previously described as absent, comparator provenance and future shadow source-tag gaps; it was **not** a whole-plan clean round.
- Repair in this working snapshot: U04's independent keyless readback depends on U07's authorized fake-provider/child receipt and committed `jev-wiya` implementation, not `jev-wiya` closure; the original `jev-wiya`→P5 edge still blocks its fresh omp scored-row acceptance. Plan/P1/P9/P2/P3/P5 body corrections preserve stage-15 RED, public URL/HEAD NOT_RUN, P15 containment UNKNOWN, and current shadow default `not-run`. Future P3 must persist same-session/`toolCallId` source joins or mark `existingFlagSource` missing; P5 may not compare an earlier Jev-derived flag to an unjoined deterministic incumbent. No current hook behavior changed.
- `work/jev-l7ym/source-audit.json:3` and its generator `work/jev-l7ym/audit_sources.py:420` contain a hard-coded `2,625 codex rows` boundary; the **same recorded receipt** has `model_usage.by_profile.codex=2,658` and `nearest_tool_execution.codex:eval=2,658` at `:104-116`, summing with claude 702 to 3,360. The 33-row discrepancy is stale prose, not a documented subset; use 2,658 for structured telemetry and do not cite 2,625 as measured. Original receipt bytes are retained; this pass did not rerun the 1,007-file audit or change its ranking metrics. It remains UNDERPOWERED (42 attributable windows < 100).
- Graph/store readback after this edit: `br dep cycles --json` reported zero active cycles; `br show` returned U04→U07, P5→P15/U07/U06/U04/P4/P3 and `jev-wiya`→P5. `br ready --json` listed only assigned P1 and `jev-aykj`, not U04/P5/`jev-wiya` or P9. `br sync --status --json` reported healthy, 405 exportable/405 unique, zero dirty and no DB/JSONL drift; `git diff --check` exited 0. `br doctor --json` had a stale `.beads/beads.base.jsonl` warning (`ok:false`), so no clean-doctor claim; `br show` and sync remained operational.
- **Boundary:** graph/text reconciliation only. Positive and planted negative arms are specified, not executed; no new Jev/API call, credential read, provider attempt, reported-failure/test rerun, session restart, public clone/push or organic outcome. TypeSafe spend $0 in this repair. Recommit the corrected plan/bead bytes, obtain two consecutive independent full-plan zero-new reviews against the **same committed blobs**, then address each deferred consumer/provider prerequisite before any execution-ready or safety claim.

## 0927 immutable 9c0bada1 review and jev-wiya non-author refusal (2026-09-28) [source-only / planning, NOT execution-ready]

- Frozen target `9c0bada16c6f991cbf9090e5ee89661d9ef168f0`: `git show` plan SHA-256 `4ceaa4a911e85a6bcc7b8daec83cb0521174c3a315f2f4630a631b916c9dbcf5`; issues SHA-256 `5c6ce8aa6f68081966eac716fae274fdb545af728e8a57b146169ca23a8c3f76`. Pane 2 first returned ZERO NEW on a **bounded safety** review; it explicitly refused full-plan round credit. Its subsequent independent full-plan/all-18-bead review reported **zero new** with self-contained contracts, DAG/false-ready, consumer rationales and structural-diff checks. This is at most **1/2 on that exact frozen pair**, not conversion completion. An earlier request carrying the obsolete `fd15772` hashes was refused as `NOT_RUN`, not counted as a zero; other full-plan reviews were still in flight at this entry.
- Pane 1 non-author source readback of `jev-wiya` recorded Beads comment 952, verdict **REFUSE closure**. `git show 166d2c08 -- work/jev-client/src/infisical-key.ts` shows that claimed fallback revision placed the machine client secret in CLI `--client-secret` argv and child `INFISICAL_CLIENT_SECRET`; the later direct-HTTP code avoids that argv route but still inherits `process.env` in `defaultRunner` (`:22-26`) and sends to an unchecked first origin (`:77-82`), both already recorded U07 blockers. `work/jev-wiya/scored-shadow.json` carries one pinned `jev-1.13.0` scored row, 747 input tokens and reported $0.000031374 input spend, but no session/event identity or fresh-omp/expired-user-session transcript; it is not independent fallback safety or original acceptance. `jev-wiya` stays OPEN behind P5; U04/U06/U07/P15 remain separate prerequisites.
- **Boundary:** source inspection and graph readback only; no new TypeSafe call, real-key read, test or reported-failure rerun, provider attempt, restart, public push, model result, organic benefit or session-wide safety claim. New TypeSafe spend in this pass $0. Beads comment 952 is a later worktree change **not contained in the frozen 9c0bada1 issue blob**; it must not be silently counted as reviewed there. Preserve the exact two-round same-blob gate after the final plan/bead snapshot is committed.
- Pane 5 separately checked the frozen `9c0bada1` `jev-wiya` sources and artifact (scored-row SHA-256 `70ab6d506c305d7d7c39d0ee72daeba39ed1744828e23a439ee600e13706541b`) and independently **REFUSED** the fresh-omp/expired-user-session acceptance: the one row has no session ID, `toolCallId`/event ID or auth-source attribution. This was a bounded source review, **not** a second whole-plan clean round; no test, call, key or restart was run. The historical argv route was removed by the current direct-HTTP revision, but that does not clear U07's inherited environment or unchecked first origin.
- Pane 3's fresh full-plan/all-18 review of the same `9c0bada1` hashes found **one new U07 proof-boundary defect**. `work/jev-client/src/infisical-key.ts:24` builds the final `execFile` child environment from `process.env`, while `work/jev-client/test/key-provider.test.mjs:120-148` injects the higher-level Runner and checks its input, not the final spawned environment; the existing redirect test also cannot prove zero requests to an unapproved *first* origin. The reviewer explicitly did **not** inspect every possible external receipt, so absence of a separate receipt is `NOT_RUN`. Plan repair row 2 and the U07 bead acceptance now require a source-bound final-spawn fake capture, parent-env sentinel and zero first-hop transport/child attempts; Beads checkpoint 953 names positive/RED/NO-CLAIM. U07 remains IN_PROGRESS; U04 remains DEFERRED. The finding **resets post-conversion review credit to 0/2**; pane 2's earlier zero on the superseded pair cannot be carried forward.
- Pane 2's separate **configured** P15 egress census found project hooks/extensions/tools/MCP, 12 profile config roots and 12 model roots, 9 profile-local extensions, four profiles with a `typesafe/jev-latest` judge role, a disabled-by-source shadow watcher and a possible canary. Effective session load, background activation, raw output egress and containment remain UNKNOWN/NOT_RUN; configured is not loaded. This source inventory does not itself authorize a restart, key lookup or live call.
- Pane 4's independent full-plan/all-18 review of the same immutable `9c0bada1` hashes reported **zero new** across contracts, 18-node/24-edge graph, five consumer rationales and the parent diff. It correctly kept P15 loaded-session safety, U06 provider-visible-output proof and P9 public URL/HEAD parity `NOT_RUN`. Its zero is **superseded** by pane 3's same-target U07 finding and cannot count toward two clean post-repair rounds. No tests, calls, keys, issue writes or restarts in that review.
- Pane 5 also completed an independent read-only full-plan/all-18 review of the superseded `9c0bada1` hashes and found the **same one U07 final-spawn/first-hop proof gap**, not a second distinct failure class. It did not search all possible external receipts, run tests or make provider calls. Its positive/RED were specified, not executed; no clean-round credit transfers to the repaired blob.

## 0927 repaired 04a2b11a review candidate (2026-09-29 UTC) [offline / planning, NOT execution-ready]

- Committed target `04a2b11ab27e8ddcd5bbaee962797cbdd511b17f`: plan SHA-256 `eefe092073821d66e09f4062e1e3f9fd05e52e2f725214bf3608b499d6cf848b`; Beads SHA-256 `c82b2a7d1ac8d7d509cd909f5626ccab71ff22b4f96ae48e97830778eb381343`. `git show` and `br dep cycles --json` gave the frozen bytes and zero active cycles; `br ready --json` listed only assigned P1 and `jev-aykj`, not U04/P5/`jev-wiya`. Bead changes from `9c0bada1` are **only** U04 (comment), U07 (description/comment), `jev-wiya` (non-author refusal); P5/P14 edges were inspected, not edited. The plan row-2 change requires actual final child environment capture and first-hop zero attempts before U04 consumes U07.
- Pane 2 first sent a zero verdict that mixed this plan hash with the **old** `5c6ce8aa` issue hash; that report is **NOT_RUN** for the new pair. After fresh `git show` readback it reported independent whole-plan/all-18 **zero new** across contracts, graph, five rationales and the exact parent diff, correcting its initial false P5/P14 diff attribution. Its assertion that all 18 bodies carried exact WHAT/WHY/ACCEPTANCE headings was **refuted** by a frozen-blob recount: only **5/18** have all three as line-start section labels. Its zero therefore cannot certify full Beads conversion. Synthetic approved-provider positive and denied-origin/inherited-env causal RED were specified, **not executed**.
- Pane 5 independently reviewed the exact `04a2b11a` pair and reported **zero *new* defects**, but explicitly found the known Gate-2 failure: 11 historical conditional Beads should not have been created before activation, only **5/18** have literal body headings, and U06 is `in_progress` without them. It confirmed 18 nodes (13 deferred, two open, three in progress), 24 internal edges, zero literal cycles and blocked P9/`jev-wiya` paths. Its check is not an execution-readiness PASS. Pane 3's separate source check again found the already-known final `execFile` inherited-env and first-origin U07 implementation gaps; it was bounded, not a second whole-plan round.
- Integrator then found `docs/0927_reality_plan.md` Gate 1 still described the **removed** U04→`jev-wiya` deadlock as current; the current graph instead has U04→U07. Corrected the stale temporal claim without weakening Gate 2. This is a plan edit **after** both reviews: clean-round credit on the next committed snapshot resets to **0/2**, and the active-body label/conditional activation gate remains **FAIL**. HazySpring owns the in-progress U06 description; a requested literal-heading repair must preserve its substantive privacy/RED bar. Deferred historical branches stay inactive, not made ready by cosmetic labels.
- **Boundary:** this review checks plan text and the Beads dependency representation only; it does not execute the graph's proposed work. U07 fake final-spawn, U06 output, U04 non-author provider check, P15 loaded-session containment, P1/P9 public baseline and `jev-wiya` fresh-omp scored-row acceptance remain pending/NOT_RUN. No fresh Jev/API call, key, provider attempt, test, restart, public push or consumer benefit in this plan review; new TypeSafe spend $0.

## jev-qg1j webscreen shadow-report CLI independent readback (2026-09-29 UTC) [offline test + recorded-data recount]

- Scope: peer's uncommitted `scripts/shadow-report.py` `--web-shadow` argparse repair and `scripts/test_shadow_report.py` CLI regression, read in place; no ownership of those files or Beads closure. `PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/var/agent-tmp" python3 -m unittest scripts.test_shadow_report -v` returned **8/8 OK**, including launching the real CLI with synthetic web/empty inputs and asserting one answered row. The reported pre-fix CLI failure was accepted as given, not rerun.
- Independent source recount: `~/.local/state/jev/webscreen-shadow.jsonl` SHA-256 `7d0f88c8f66ac50a740f2a9c38beb99443903e6d99b6428b782bb48ec48884fd` matches `work/jev-qg1j/latest.json`. Of 60 source rows, 27 precede the recorded test cutoff and 33 qualify; 16 `ok`, 17 `fail_open`, 16 rows with input usage, 17 without. Known input total 13,147 tokens × $0.042/M = **$0.000552174**; first-to-last eligible event span **40.113 h**. Recounted report fields agree, and `spend_complete=false`.
- **Boundary:** zero new Jev/API calls or keys; the first-to-last event span does **not** prove uninterrupted hook uptime, flags 0/16 are descriptive rather than efficacy or accuracy, and missing usage makes spend a lower bound. `jev-qg1j` remains `in_progress`; the 48-hour dependent gate remains separate.

## 0927 Gate-2 active-body repair and review reset (2026-09-29 UTC) [offline / planning, NOT execution-ready]

- Pane 4 later sent an independent whole-plan/all-18 **zero new** report on the exact old `04a2b11a` plan/issues hashes. It checked the U07 final-child/first-hop acceptance, 18-node/24-edge graph, five consumer rationales and actual parent diff, while keeping P15/U07 implementation NOT_RUN. It is historical review evidence only: the Gate-1 text repair and U06 body edit occurred afterward. An earlier review's **zero new** cannot cure a known Gate-2 FAIL.
- In commit `36e94d02`, `br update jev-u06-provider-output-redaction-noom --description-file - --actor ChartreuseAspen` split its already-existing WHAT/WHY/ACCEPTANCE/NEGATIVE/NO-CLAIM/UNBLOCKS prose onto literal body-heading lines. A before/after word-sequence comparison matched exactly; status `in_progress`, assignee HazySpring and dependencies are unchanged. Staged JSONL changed only U06 (description and `updated_at`); peers' dirty `jev-qg1j`/`jev-o75t` rows were neither staged nor committed. The frozen 18-row mechanical heading count increases **5 → 6**; this does not prove provider-output redaction or activate any of the eleven premature conditional Beads.
- Repaired plan Gate-2 wording now distinguishes that active-body fix from the still-failed full-graph conversion. `br sync --status --json` returned `workspace_health=healthy`, no `db_newer/jsonl_newer/coverage_drift`; `br dep cycles --json` returned zero. `br doctor --json` had a non-OK `git_sync_branch` configuration warning, so this is **not** an all-checks doctor pass. The next committed plan/issue pair requires **two fresh full-plan/all-18 reviews on exactly that pair**; current count **0/2**. No TypeSafe/Infisical API call, credential, new provider request or session restart; spend $0.

## 0927 0ff0f82b full-plan review wave (2026-09-29 UTC) [planning reset 0/2, Gate 2 FAIL]

- Frozen target `0ff0f82be0a2645f0f0c695d91e0a6520e67fd8a`: plan SHA-256 `d58679ab674e2a040171e57e9fd5979c3053957833984d1ec76a49c815bf45d3`, Beads SHA-256 `dfb0ef6613bb7b373c698eb33bbe3d6e6127b771c618183037e942a221279e74`. Versus `04a2b11a`, the exact committed scope is plan +5/-1, Beads +1/-1 (**U06 description only**), EVAL +21; 18 linked rows and 24 internal edges remain. Live worktree `jev-qg1j`/`jev-o75t` edits are outside this target.
- **Round 1:** Pane 2 read the whole plan and all 18 frozen rows and reported zero new across contracts, graph, five rationales and diff. Its initial assertion that `04a2b11a` was the immediate parent omitted U06; challenged before credit. It corrected the immediate parent to `36e94d02`, accounted for the complete `04a2b11a→0ff0f82b` plan/EVAL/U06 diff and kept **NEW=0**. **Round 2:** Pane 4 independently read the same plan/18 rows, checked all four axes and reported **NEW=0**. Its initial apparent `0→6`/`5→6` mismatch counted U06 section labels versus the number of fully labeled bodies; challenged and corrected: U06 six line-start labels `0→6`, bodies with all three literal headings **5/18→6/18**. Both reports separately retain the 11 premature conditional records as **Gate-2 FAIL**, not a passing conversion.
- Pane 3 also reported zero new on these hashes, keeping U07 final-child/first-origin evidence and P15 loaded-session containment NOT_RUN; its diff summary did not enumerate EVAL additions, so it is supplementary, not needed for the two-round count. Pane 5 was still running an independent review when this receipt was recorded; any subsequent source-linked **new** finding demotes the pair and resets the counter. Positive approved synthetic provider/child route and causal denied-origin, inherited-env, recorder-missing and duplicate RED are **specified**, not executed here.
- **Boundary:** The initial two zero-new reports are **superseded** by pane 5's later new finding; current planning convergence is **0/2**. This does not fix the historic premature creation of 11 deferred Beads, confer a live consumer, prove output redaction, final `execFile` environment, approved first-hop recipient or already-loaded session containment, clear `jev-wiya` fresh-omp proof, pass stage 15, authorize execution of a conditional plan branch or new live traffic, or demonstrate Jev benefit. Independent bounded P1 baseline work retains its separate contract. No provider/TypeSafe calls, keys, tests or restarts in the review wave; new Jev spend $0.
- **Pane 5 late review, NEW=1 source-locator defect:** On the same `0ff0f82b` plan/issues bytes, P15 pointed to nonexistent `.omp/hooks/post/jev-webscreen.ts:230-263` (current file ends at 230), `.omp/hooks/post/jev-web-search-rerank.ts:273-298` (ends at 274), and `.omp/hooks/pre/jev-gate-shadow.ts:121-133` (ends at 120). This is a citation/current-source mismatch, **not** proof those routes are absent or safe. Independently re-read the current worker (`:1-5` refuses), injection shadow (`:40-55` writes local rows), gate observer (`:278-323,364-376`), webscreen (`:144-165,204-230`) and rerank (`:180-245,267-274`); corrected P15 current-source descriptions and locators in `docs/0927_reality_plan.md:146,148,170,182`, preserving UNKNOWN already-loaded sessions. Historical review rows below their earlier source revision are not current-source citations. Reviewer also reported 18 nodes/24 edges/no false-ready conditional work, 6/18 literal-heading bodies and 11 deferred conditional records, and kept fresh-omp/loaded-session and U06/U07 provider-safety proof NOT_RUN. After this plan revision the next two independent full-plan/all-18 rounds must inspect the **same newly committed plan/issues pair**; neither earlier zero counts. No Beads status/edge change or code execution is claimed.

## 0927 1911c5bd full-plan review wave (2026-09-29 UTC) [planning reset 0/2, Gate 2 FAIL]

- Frozen target `1911c5bdd972e1b945a4929ba4456ec3accc9692`: plan SHA-256 `568f2313e5c947723a75388d9dbc3d8fcffa3a924de55ed97a0c040fa48dd791`, Beads SHA-256 `dfb0ef6613bb7b373c698eb33bbe3d6e6127b771c618183037e942a221279e74`. Versus `0ff0f82b`, only four P15 plan lines were replaced; no Beads row changed. Pane 2 independently read the plan/all 18 rows and reported **NEW=0**, known Gate-2 failure separate; its zero was a provisional first round, not completion.
- Pane 5 independently read the same frozen pair and reported **NEW=1 source-contract finding**, not introduced by that diff: `docs/0927_reality_plan.md:150` claimed `.omp/hooks/pre/jev-compact.ts:34-35` registers `session_before_compact` when `TYPESAFE_API_KEY` is set. In current source `compaction/src/omp-binding.ts:225-227` returns when the optional `admitSyntheticTranscript` callback is absent, before key access or event registration; the project hook passes no callback. Confirmed by source read; corrected P15 to call it a configured/latent route, with explicit synthetic admission + key for a fake positive and older loaded revisions still UNKNOWN. This resets the same-blob count to **0/2**. Pane 5 also found 18 nodes/24 edges/zero cycles, 6/18 literal-heading bodies, 11 prematurely created deferred conditionals; its cited NFCorpus N=234 result does not establish a free-model comparison or operator benefit.
- Positive/RED/NO-CLAIM: the corrected contract requires an eligible admitted synthetic compaction event to reach exactly one fake provider attempt; denied/missing recorder or wrong identity must produce zero disallowed attempts (these are **specified, NOT_RUN**). No live-session containment, U06/U07 output/provider safety, `jev-wiya` session/event join, organic prevalence, adopter or execution authority is proven. Pane 3 sent a separate review of **0ff0f82b**, not this target, and cannot count; pane 4 was busy with its assigned work and was not interrupted. After committing this correction, dispatch two fresh independent full-plan/all-18 reviews on the **same new plan/issues pair**. No new Jev/provider call or secret in this review wave; spend $0.

## 0927 9719ff72 full-plan review pair (2026-09-29 UTC) [planning 2/2 provisional; Gate 2 FAIL]

- Frozen target `9719ff72c7b31b419b04656a35e4c1261abfde2c`: plan SHA-256 `bc22d50c02c286043d9056330920eb67fe744e03ccceeb7bdd326b855e92d3fd`, Beads SHA-256 `dfb0ef6613bb7b373c698eb33bbe3d6e6127b771c618183037e942a221279e74`. Versus `1911c5bd`, one P15 plan paragraph changed, the Beads blob is byte-identical and this ledger gained the superseded-review receipt. `compaction/src/omp-binding.ts:225-227` returns before key lookup/registration for the default hook with no admission argument; `:228-234` is the explicit synthetic-admission-plus-key path. Current default is latent; loaded older sessions remain UNKNOWN.
- Pane 2 read the full plan/all 18 P/U contracts, source and graph and independently reported **NEW=0** on the exact pair; pane 5 independently read the same full pair and independently reported **NEW=0**. Both separated the known Gate-2 conversion FAIL (11 prematurely created conditional Beads still deferred; 6/18 exact line-start WHAT/WHY/ACCEPTANCE headings) from a new contract defect. Pane 5 confirmed 18 nodes/24 internal edges/no cycles or false-ready conditional child, P1 as independent baseline, P9 blocked on P1, U04 blocked on U07, and P5 blocked on P15/P3/P4/U04/U06/U07; the five §2b source/label/incumbent/human-action examples remain proposals, not measured adopters. This is **two independent planning-only zero-new readbacks after the last repair**, not a conversion, safety or readiness pass. A subsequent same-blob NEW resets the count; pane 3 received a further independent review packet and pane 4 was occupied with separate owned work rather than interrupted.
- **Boundary:** Positive and causal RED are specified (authorized synthetic request/row; denied/unknown owner, recipient, recorder or identity refuses), but P15 loaded-session containment, U06 raw-result/provider-output safety, U07 final-child first-hop proof, `jev-wiya` fresh OMP session/event join and P9 public clone parity remain NOT_RUN. No code, tests, key, provider call, restart, new Jev measurement, organic prevalence, consumer benefit or operator adoption was produced by this review wave; new Jev spend $0. Gate 2 remains FAIL and conditional Beads remain deferred. Independent bounded P1 work continues under its separate bar.
- **Additional independent same-blob readback:** Pane 3 subsequently read the entire `9719ff72` plan and all 18 P/U records against the same plan/issues hashes, inspected `jev-compact.ts:34-35` and `omp-binding.ts:225-234`, and reported **NEW=0** without using panes 2/4/5. It also read the latent `jev-1.13.0` pin gap and noted the only synthetic-admission test checks registration, not a provider request. The third zero strengthens the planning-only convergence; it does not make Gate 2, loaded-session containment, provider safety, free-model superiority or organic adoption pass. Pane 4 remains occupied with its own work and has not supplied a 9719 review.

## jev-aykj rerank text regression and P1 bounded stranger baseline (2026-09-29 UTC) [offline]

- Reviewer identified that the FiQA test used document IDs as passage text and projected a recorded 20-way Choice into a two-way case. `kit/test/rerank.test.mjs` and `kit/test/omp-tools.test.mjs` now label that projection and independently exercise distinct passage text: the asker sees exact text in Choice state, and the selected object/installed tool returns the selected text verbatim, including whitespace and newline. The projected two-way case is **not** a captured two-way Jev answer. `foundation/kit/claims.tsv` updates three proof excerpts without reducing the registered 118/119 coverage floor.
- Current workspace before the numeric-refusal fix: rerank+omp tests **11/11**, kit suite **52/52**, kit `tsc --noEmit` exit 0, stage 15 `--selftest` passed and normal stage 15 **431 pass, 0 fail, 3 skip; 118/119 coverage**. Changed test titles initially made three proof excerpts fail; updated those exact excerpts and reran the unchanged stage 15 green. A new installed-tool numeric-claim test went **RED** (`not_run` instead of `refused`): `kit/templates/omp/tools/jev-claim-check.ts` described numeric claims as out of scope but had no pre-ask guard, unlike the project-scoped tool. Added the guard in the installed template; focused installed-tool tests **6/6**, full kit tests **53/53**, kit `tsc --noEmit` exit 0, and stage 15 **431 enforced pass, 0 fail, 3 skip; 118/119** after the fix. `ubs` on the template and two changed tests exited 0 with eight warnings on test awaits and committed-fixture JSON parsing. Independent pane-2 readback found **ZERO new rerank issue**: replacing passage text with IDs would fail both state and selected-text assertions. Its combined test 11/12 ran before the numeric guard fix and exposed that separate RED; do not quote it as post-fix.
- Fresh local clone at `dbc3f3a670a673b74a84c130901821ac4618ba66` under `var/agent-tmp/p1-baseline-20260929-hazyspring`: `npm ci --prefix kit` and `npm ci --prefix work/sdk` exited 0; keyless `npx --prefix kit --no-install jev doctor --robot` reported `NOT_RUN/no key`; keyless `jev ask choice --fake --robot` returned an offline answer; keyless `jev classify --fake --robot` returned `lost_or_stolen_card`, and `jev rerank --fake --robot` returned `181942`. Injected `askJevChoice` transport returned HTTP 401 with exactly one observed request, `ok=false`, `reason=http`, without network. `node --test kit/test/install.test.mjs` in that clone passed **4/4** including unmanaged-tool collision bytes preserved and existing host extension list unchanged. These are keyless behavior checks, not live Jev calls.
- **Boundary:** no real key, API/provider request, live Jev result, installed omp L3 firing, clean remote clone or runtime proof of retained host extensions. Existing four-call pinned receipt is not replayed or promoted into a benchmark. New Jev spend $0. This fresh clone was at the earlier committed revision, so it does not prove the subsequent installed-template numeric guard; current-workspace installed-tool test exercises that guard. P9 quickstart remains blocked on P1 acceptance review and stage-15 aggregate disposition.
- Aggregate `bash foundation/gates.sh` returned **FAIL**: stage `80-lane-instrument-selftests` exit 1 after 11 earlier stages passed; `scripts/selftest-consumer-check.sh` reported 11 ok/1 failed, and `scripts/selftest-test-registry-hook.sh` could not execute missing `githooks/pre-commit-test-registry.sh`. The hook path is absent in the current `githooks/` directory; this is not a clean P1 aggregate receipt and neither failure was waived. Stage 15 alone was rerun after the installed-tool guard and passed 431 enforced / 0 failed / 3 skipped, 118/119 coverage. P1 remains in progress; do not activate P9 from this result.

## jev-pgtu same-state Jev rescore [live-verified (N=491); free comparator NOT_RUN] (2026-09-29)

- Prereg/runner: prereg SHA-256 `424cb18f…`; prereg/runner commit `2c1a72e9`; in-process Infisical stdin handoff `bee800d1`; TypeSafe debug-body log scrub `424fc0f6`; live result receipt commit `f2d687d3`.
- Command: `node --experimental-strip-types work/jev-pgtu/run.mjs --jev-rescore-live`. The launcher reran a keyless exact-hash preflight, then used the repository InfisicalKeyProvider and passed the key only through stdin to the pinned Python SDK (`typesafe-sdk-python@0ffd094`). Model `jev-1.13.0`; max retries 0; one serial request per stale-hash row.
- Live result: `491/491` answered; `247246` input and `10802` output tokens; actual input spend `$0.010384332` at `$0.042/M`; total elapsed `76699.648 ms`. Answer-only rows: `work/jev-pgtu/jev-rescore-rows.jsonl`, SHA-256 `cc0aa3427dfdf8a8a9dd74483cb580619ad9287694eabba1f2341a9321678a9e`. No raw state or response body is in the committed rows.
- Post-commit keyless pairing smoke: `node work/jev-pgtu/run.mjs --preflight-only` returned `NOT_RUN`, `reachability-not-ready`, `provider_requests=0`; it read `300/300` clean and `300/300` planted exact hash pairs, `input_hash_mismatches=0`, and `superseded_stale_jev_rows=491`.
- Data-integrity audit: the fixed `items.jsonl` has `600` rows, `471` unique `inputSha256` values, `69` repeated-hash groups, and `129` duplicate-row excess; `68` hashes occur in both clean and planted labels (`196` rows), max `5` rows/hash. Since assistant and question are constant, these are identical TypeSafe states with contradictory ground-truth labels. Reachability remains `NOT_RUN` with `paired_input_status=MATCHED` and `input_hash_label_consistency=CONFLICT`.
- Boundary / NO-CLAIM: Jev response acquisition only; no OpenRouter/free comparator, no accuracy/AUC/McNemar metric, no model-performance verdict, and no promotion. The prior `5/300` and `268/300` figures remain legacy-source metrics, not scores for the exact-state PGTU corpus. The contradictory label groups block the planned comparison pending provenance-backed corpus repair or a newly preregistered unit/bar; the free-arm date and Pane 1 approval remain.

## jev-p15 configured egress census and queue reconciliation (2026-09-29 UTC) [read-only, NOT_RUN]

- Read-only scope: enumerated the default omp agent root and all 13 current profile roots (12 have both config.yml and models.yml). Four configured profile `modelRoles.judge` aliases point to `typesafe/jev-latest` (claude, codex, grok, muse); `jev-lab` declares five Jev-capable absolute extensions. Project `.omp/` has registered pre/post hooks, project extensions and invoked tools; none of those establishes the loaded state of an already-running session. `scripts/fleet-idle-watch.py:64-67,364-366` now disables shadow worker spawn in source. `launchctl list` exposed scheduled `ai.zeststream.jev-latest-canary` (no running PID at observation); its plist specifies a 09:07 UTC Infisical-backed version probe, a separate entry point. `omp ps --json` listed no ready Jev project daemon; this is only the supervised-process scope.
- Operational checks after Beads reconciliation: `br dep cycles --json` reported zero cycles; `br sync --status --json` reported healthy, zero dirty issues, zero coverage drift, 405 DB-exportable and 405 JSONL IDs. The expired 2026-09-28 free-tier date blocker on `jev-545t` was removed; `jev-qsa6` remains blocked until its **approved 2026-09-30** launch, not the superseded 09-29 note. Of the original 15 active records, five remain assigned to staffed panes, eight moved to blocked, and two actionable but unstaffed returned to the open queue. Thirteen conditional converted P/U Beads remain deferred.
- **Boundary:** configured is not loaded; no older session revision, profile provider role, extension child, scheduled canary invocation, fake recorder, secret resolution, or actual Jev call was exercised by this census. No P15 containment, session-wide no-export, provider-output safety, Jev benefit, or new live spend is claimed. P1 quickstart, P15 interception and independent U06/U07 checks still gate their own claims.

## jev-p15 installed review extension admission [offline, NOT_RUN live] (2026-09-29 UTC)

- Changed the project `.omp/extensions/jev-review.ts` to load `ompJevReview` without registering a global Infisical key provider. `work/omp-jev-review/src/index.ts` now requires separate explicit synthetic approvals for provider egress and local diff re-execution; normal installed entry point supplies neither. Locally approved git reads use `execFile` with `--no-ext-diff --no-textconv`, and refuse `--ext-diff`, `--textconv`, `--no-index` and `--output`. This is a bounded **source + injected-host** fix for one project extension, not session-wide P15 containment.
- Exact offline check: `npm test` in `work/omp-jev-review` passed **26/26**, including provider-only denial, installed-wrapper denial and unsafe-command refusal. A separate keyless Node host smoke imported `.omp/extensions/jev-review.ts`, fired one `tool_call` for `git diff --cached`, and observed `permission-denied`, **0 provider calls**, **2 local rows**; no real git re-execution or provider call was made. `git diff --check` on scoped changed paths exited 0; changed-file literal secret scan (`sk-|Bearer [A-Za-z0-9]|tskey`) found no match. `ripwire . --quality-delta --scope=work/omp-jev-review/src/index.ts,.omp/extensions/jev-review.ts,work/omp-jev-review/test/review.test.mjs` reported 0 scoped gating regressions, 5 minor; 5 out-of-scope gating regressions were excluded, not graded.
- `ubs .omp/extensions/jev-review.ts work/omp-jev-review/src/index.ts` exited 0 (0 critical, 2 async-host-listener heuristic warnings); including `test/review.test.mjs` exited 1 (13 critical heuristic hits on non-secret `undefined`/literal comparisons, 6 warnings, 258 info). No scanner green is claimed for all changed files. There is no dedicated `work/omp-jev-review/tsconfig.json`. Post-commit, `node kit/node_modules/typescript/bin/tsc --noEmit --strict --allowJs --allowImportingTsExtensions --module nodenext --moduleResolution nodenext --target es2022 --typeRoots kit/node_modules/@types --skipLibCheck .omp/extensions/jev-review.ts` exited **0**; without `--allowJs` the standalone command cannot resolve the existing `register.mjs` type. No prior-art pin moved.
- **Boundary / NO-CLAIM:** one fake-host denial is L0, not a real omp L3 trip. Already-loaded session revisions, other project/profile extensions, auto hooks, judge model roles, scheduled canary, U06 raw-result/provider-output redaction and U07 first-hop ownership remain untested here. No Jev answer, model/accuracy assertion or consumer outcome; live requests **0**, incremental spend **$0**. Keep P15 in progress; prove fresh and loaded-session positive/negative paths before lifting the plan's halt.

## jev-u07-infisical-argv-gi70 first-hop and final-child hardening (2026-09-29 UTC) [offline, NOT production-cleared]

- In `work/jev-client/src/infisical-key.ts`, machine identity now requires an explicit caller-approved HTTPS origin before reading the credential file. The configured API URL must share that origin without userinfo, query or fragment; the login POST targets the approved origin with `redirect: "error"` and refuses a redirected or mismatched nonempty response URL. `makeDefaultRunner` gives the final CLI child only `PATH`, `HOME`, `TMPDIR` plus the approved origin and machine token for the secrets lookup; the machine client secret is absent from argv and child env. The default provider supplies no origin approval, so its machine fallback remains disabled. Tests and `work/jev-client/README.md` document the boundary.
- Red/positive provenance: the previous `EVAL.md:2842-2844` records an injected child receiving the synthetic client secret and a real local HTTP 307 forwarding the synthetic POST before `redirect: "error"` was added. This pass's test additions covered rejected 401, redirect refusal, wrong/non-HTTPS first recipients, denied approval with zero credential-file reads, approved synthetic universal-auth POST, and final injected `execFile` child options. `node --experimental-strip-types --test work/jev-client/test/*.test.mjs` passed **72/72**. Standalone strict ES2024 `tsc --noEmit` on `src/infisical-key.ts` exited 0. A separate keyless `node --experimental-strip-types --input-type=module -e <synthetic smoke>` used injected transport, fake credential-file bytes and a fake `execFile` boundary: `approvedFirstHops=1`, `childRuns=3` (approved session+machine and denied session only), `wrongOriginDenied=true`, `parentSecretsInChild=false`. No real key or production HTTP endpoint was used.
- `git diff --check` on the three scoped paths exited 0. `ubs` on source and tests exited **1**: 6 critical / 2 warnings, including URL-identity comparisons and synthetic credential literals in test files; these require location-level adjudication and are **not** a green quality gate. `ripwire . --quality-delta --json --scope=work/jev-client/src/infisical-key.ts,work/jev-client/test/key-provider.test.mjs` reported **1 scoped gating self-churn** row at `machineIdentityKey` (plus two minor rows), not a quality-delta pass. A separate read-only security-reviewer found no independently demonstrable unintended exfiltration path in the scoped source, but explicitly withheld production clearance; the test-oracle reviewer did not run (model 429), not a second verdict.
- Scanner-location disposition (read-only, no suppression): `ubs` printed only **three of five** timing-equality locations—`key-provider.test.mjs:21,26` compare environment values to **undefined**, and `infisical-key.ts:102` compares public HTTPS origin strings. Source inspection also found public URL comparisons at `infisical-key.ts:92,123`, but the scanner did **not** print its remaining two timing-equality locations, so those two remain unadjudicated. The sixth critical flags the explicitly synthetic test token at `key-provider.test.mjs:270`; both warning channels point to `JSON.parse(options.body)` in an asserting fake transport at `:228`, where malformed JSON should fail the test. This does **not** turn `ubs` exit 1 into exit 0 or certify a provider boundary.
- **Boundary / NO-CLAIM:** synthetic fixtures and inspected source do not establish who approved the real recipient, whether a real machine credential works, what an already-loaded omp session sends to a provider, or output/transcript safety. No real credential file, Infisical production request, TypeSafe call or Jev result was used here: live requests **0**, incremental Jev spend **$0**. U07 remains `in_progress`, assigned to HazySpring; require owner-approved origin and a revision-bound independent runtime positive/negative readback before lifting the related plan safety prerequisite. The original 0927 planning two-round gate and P15 containment remain separate.
## jev-p1-stranger-baseline-przc clean HEAD verification (2026-09-29 UTC) [offline / partial]

- Source: fresh local clone `var/agent-tmp/jev-p1-przc-d3c80a7/clone`; actual HEAD `7fecd59dcc84502d265c9d2acac411337edba806` (directory suffix is only a label), cloned from `main` with a clean worktree at creation. `npm ci --prefix kit` exited 0. No TypeSafe, Infisical or OpenRouter credential/provider call was used.
- No-key CLI after build: `npx --prefix kit --no-install jev doctor --robot` exited 2 with `status=NOT_RUN`, `reason=no key`, `model=jev-1.13.0`. An isolated copied-bin/dist tree without SDK, with a synthetic placeholder key only, returned `status=NOT_RUN`, `reason=sdk missing`, exit 2. The pre-`npm ci` doctor invocation failed module resolution (`kit/dist/client.js` absent), exit 1, and is not counted as a doctor result.
- README fake CLI verbs all exited 0: ask Choice `c1`/0.77; verify `unsupported`/0.27; Score 2.99/Positive; Banking77 fake `lost_or_stolen_card`/0.86 (captured row label differs; output only); gate `flag=true`/maxScore 0.89; rerank Choice `181942`. Fixture outputs, not answer correctness.
- Injected transport: `askJevChoice` with a synthetic test-only token and fake HTTP 401 `fetchImpl` returned `ok=false`, `reason=http`, `model=jev-1.13.0`, one injected attempt; smoke exit 0. No provider request.
- `node --test kit/test/*.test.mjs` passed 53/53; `node --experimental-strip-types --test work/jev-client/test/client.test.mjs` passed 45/45. Tests include extension-list byte preservation, `MANUAL_REQUIRED`, and unmanaged installer collision refusal (installer child exits 1; sentinel bytes preserved). Direct disposable `jev omp install --dir var/agent-tmp/jev-p1-installer-positive --robot` returned `status=READY`, exit 0. A separate manual collision shell fixture was blocked by kit-guard B7 before execution; no bypass.
- Stage-15 diagnosis is source-only; the gate was not rerun. The clean clone has the enforced `numeric-out-of-scope` needle in `.omp/tools/jev-claim-check.ts` and `screen() pure thresholds` in its proof test. The historical rerank Score rows are `enforce=no`/retired.
- Fresh-clone `env -u TYPESAFE_API_KEY -u JEV_API_KEY -u OPENROUTER_API_KEY ./foundation/gates.sh --portable` exited 1 at preflight: `.beads/*.db` was absent; the gate instructs `br sync --import-only`. No stage ran. Full aggregate and `--selftest` are NOT_RUN: later stages/selftests delete their own temporary files, and this task has no explicit deletion authorization.
- Boundary: offline CLI/installer behavior only; Jev requests 0, Jev spend $0. No model-accuracy/organic-benefit claim, public GitHub clone parity, extension activation/load, L2/L3 or live authorization claim. README unchanged and retains its local-versus-published boundary. P1 remains in progress pending aggregate resolution and pane-1 independent verification.

## jev-p1-stranger-baseline-przc public-GitHub checkout readback (2026-09-29 UTC) [offline / partial]

- Network-cloned public `JYeswak/jev_playground` at `7fecd59dcc84502d265c9d2acac411337edba806`; keyless `python3 scripts/stranger-run-jev-playground.py --out var/agent-tmp/p1-stranger-20260929.json --timeout 90` ran all 12 README commands in a minimal environment: 10 exited 0, `doctor --robot` and non-fake Choice each exited 2 with explicit `NOT_RUN/no key`. Receipt is local scratch, not committed. No API call or spend.
- In that npm-prepared public checkout, `node --test kit/test/*.test.mjs` passed 53/53, including the unmanaged collision and host extension preservation; `node --experimental-strip-types --test work/jev-client/test/key-provider.test.mjs work/jev-client/test/client.test.mjs` passed 59/59, including injected HTTP refusal, redirect refusal and default no-key paths. The first installer test attempt against the *source-only* checkout failed 4/4 because `kit/dist` was absent; this was a preparation error, not an installer result.
- Publication is **not CI-green**: GitHub Actions run `36605183897` on that SHA failed `gates` (stage 15: 418 pass/13 fail/3 skip, 114/116 coverage below 114/115 floor) and `registered suites` (missing committed `session-pinned.jsonl`, missing runner dependencies, stale seat exports and comparator census). Local stage-70 registered-test coverage passed after an uncommitted `TESTS.md` row and its planted-negative selftest passed; that is not evidence of aggregate success. Gate owners must repair the real defects without lowering bars.
- **Boundary / NO-CLAIM:** keyless CLI, fake answers and injected failures only; no TypeSafe/Infisical/live omp request, installed extension activation or model-accuracy claim. P1 remains incomplete until its aggregate gate and independent proof contract pass; P9 does not activate.

## jev-p2-gate-demand-qdtl local adopter gate census (2026-09-29 UTC) [offline / decision NOT_READY]

- **Consumer:** our own omp gate operator. An outside adopter or outside approval is not a prerequisite for this keyless census or local dogfood; provider-bound traffic retains its separate P15/U04/U06/U07 and data-class safety boundary. Organic window `2026-09-28T18:51:24.925Z` through `2026-09-29T18:51:24.925Z`, selected before joining outcomes from `~/.local/state/jev/gate-observe.jsonl`; log SHA-256 at readback `143c444fba244b6eae1da449fbb2bb6e3dbff1ebbd3774751c94156368068298`. The log and active session files may append later; the timestamp window, not their later EOF, bounds this count.
- **Source census:** 2,750 gate rows across 10 sessions in the window; 2,425 rows in five session IDs with matching `-Developer-jev` transcript files, 325 outside that local-session set. Within those 2,425: 2,026 `scored`, 398 `not-run`, one `error`; 1,972 distinct command SHA-256 values. Same-session command-hash and nearest `tool_execution_start` within 30 seconds found 793 row matches but only 791 distinct tool-call IDs, so the raw 793 cannot be treated as independent actions. 792 matches carried `guard_pass` and one `guard_fire`; the observed transcript contained tool results for all 793. Another 113 scored rows have a hash candidate 30–300 seconds away, but were deliberately not admitted; 1,120 scored rows, all 398 not-run rows and the error row had no matching `(session, cmdSha)` start. This is **join coverage**, not harm detection, action benefit or correct authorization.
- **Outside-author labels:** the earlier `work/jev-1miz/manifest.jsonl`, `labels-A.jsonl`, `labels-B.jsonl`, and `adjudicated.jsonl` supply labels for only five distinct command hashes in this local window (36 repeated events). Four of the five hashes are `no-harm`, one `harm:2`; majority constant on these five unique hashes is **4/5 = 0.80**, not a fleet baseline. Only seven of the 36 repeated labelled events have a 30-second same-event incumbent join; repeating commands does not increase the independent label N. The 560-row prior receipt explicitly states zero observed DCG denials and `NOT_COMPARABLE` (`work/jev-1miz/final-receipt.json:5-9`).
- **Decision / Boundary:** keyless evidence does not support a P2 Jev-vs-DCG judgment or promotion: 5 unique overlapping labels and 7 joined labelled events cannot establish the preregistered same-event independent outcome comparison. Rework on **our** gate traffic: capture a consented cohort with event IDs joining the deterministic incumbent and actual operator action, label distinct events independently, print the majority baseline, then preregister the decision bar before any new pinned `jev-1.13.0` call. This pass made **zero** TypeSafe or comparator calls; incremental spend **$0**. No new authorization, rollout, interception safety, observed harm prevention, or consumer benefit is claimed.

## 0927 plan-to-Beads post-conversion graph audit (2026-09-29 UTC) [offline source review; runtime NOT_RUN]

- Reviewed the 18 converted P/U records against `docs/0927_reality_plan.md` and their `br show` bodies, with four read-only pane reviews requested through `ntm send`. The earlier `79cbdf4b` plan's 2/2 clean reviews do **not** certify the later Beads graph; source-backed failures and retry conditions are recorded in `NEGATIVE_EVIDENCE.md` R125–R128. Corrected the P2/P4/P5/P8 activation and denominator contracts, and documented the U04→`jev-wiya` semantic deadlock repair without converting optional records into permission to run.
- Operational readback at local HEAD `7fecd59d` plus uncommitted shared-tree changes: `br graph --all --json` contained 18 converted nodes and 19 internal edges; `br dep cycles --json` returned zero; `br sync --status --json` returned healthy, `dirty_count=0`, `db_newer=false`, `jsonl_newer=false`, `coverage_drift=false`; `br show jev-p2-gate-demand-qdtl --json` returned its in-progress body. `br doctor --json` exited 1 with workspace health `healthy`: stale `beads.base.jsonl` merge anchor and an unrelated `jev-jy7t.1.4` fully-unblocked-but-blocked status warning. Neither warning is treated as a runtime safety clearance or an instruction to auto-open that experiment. `br ready --json` returned `[]`.
- `git diff --check -- docs/0927_reality_plan.md AGENTS.md NEGATIVE_EVIDENCE.md .beads/issues.jsonl` exited 0. No test, provider call, credential, fresh omp seam, comparator or published public README change was exercised for this audit; incremental spend **$0**. **Boundary / NO-CLAIM:** textual self-containment and acyclic storage do not establish executable provider safety, paired model benefit, operator action/outcome or two fresh independent zero-finding reviews of these newer bytes. P15/U06/U07 and recipient/data-class approvals still gate new provider-bound work; P2/P8 keyless work is separately actionable.
- Two independent read-only whole-plan/18-bead reviews of the later **uncommitted** worktree were source-linked and **finding-bearing**, not clean rounds: consumer review found P6 answer-conditioned assignment risk, P13 shadow/advice stage conflation, P11 SDK-direct data permission and P9 public claim/receipt mismatch; safety review found P15 same-loaded-handler compaction revocation omission, U06 original-route provider-byte capture omission and P14 closure/activation wording drift. Corrected their Beads bodies and corresponding plan clauses; Beads `br update --actor ChartreuseAspen` returned 0 for P15/U06/P6/P13/P11/P9/P14. Neither reviewer executed a provider call or certified runtime behavior. The post-repair plan/Beads gate remains **0/2** until two fresh independent zero-new full-plan reviews read the same committed revision. P0 and P2/P8 local scope remain active; no safety gate was demoted.
- A **second independent pair** read the entire current uncommitted plan/18-bead graph at plan SHA-256 `83baf80eac4b862f9902883189f981fe219c5681852434a7fd9398db28e44e2a` and JSONL SHA-256 `8a8ac2fe3c2fc349209573c4d8eeaa5a9802a2fc08cdba851e9e3169c0b857e3` (before=after within each review). Both returned **new findings**, not clean receipts: P3 `gate-observe` is Jev output, not deterministic incumbent; P2 incorrectly gated offline P4 on provider safety; P8 carried stale P0 status; P14 could close benefit on one L3 row; P11 borrowed omp U06 proof for an unrelated SDK host; U07 code reads machine config before origin check and attempts user-session CLI first despite original wrong-origin RED; current watcher scorer is disabled despite older-loaded UNKNOWN; P1 comment 982 conflated aggregate GREEN with bounded fresh-clone acceptance. Repaired plan/Beads wording, retained original safety bars and added superseding P1 comment 1001. **No source runtime fix, live call or loaded-session check was performed.** Gate remains **0/2** post-repair clean full-plan reviews; incremental spend $0. Exact remaining implementation proofs stay with P15/U06/U07/P1/P2/P8 owners.

## U06 exact synthetic provider capture (2026-09-29 UTC) [offline / local fake provider; P15 NOT_CONTAINED]

- At shared HEAD `7fecd59d` with uncommitted `work/omp-secret-probe/probe.mjs` (SHA-256 `de88ab7ccec00be6b93d8799b13bc28c5bed75299ace89ed51c1dc05d5c3ebda`, **untracked before this pass**) and `test_omp_secret_probe.py` (SHA-256 `c8b07b4bbc84a121438ec466fa88db36c3f9f3eed6b3466dcb5041bfb5f866cc`, previously shared-dirty), the local `u06-local/capture` fake provider retains the **exact second request body bytes** and the raw `tool_execution_end` RPC frame line in `--inspect-result` Base64. The provider-visible role=tool value is also recorded, but that value's Base64 is reserialized JSON, not a byte slice from the outbound body. The Python test decodes and checks that the same role=tool object occurs in the parsed complete request.
- The original `PI_CONFIG_FILES` disabled-control capture was reported by an independent read-only witness as **FAIL**: even with `omp config get secrets.enabled=false`, the model-visible tool message still contained a placeholder. A fresh `--config bypass.yml` overlay on the **RPC child** (the mechanism with the prior RED at `EVAL.md:2837`) instead produced the causal local control. `python3 -m unittest discover -s work/omp-secret-probe -p test_omp_secret_probe.py` passed **15/15** (33.45 s); the new masked exact-request assertion first failed on missing `providerRequestB64` before the capture change, then passed. `node --check work/omp-secret-probe/probe.mjs` and `git diff --check -- work/omp-secret-probe/probe.mjs work/omp-secret-probe/test_omp_secret_probe.py` exited 0. `ubs` scanned both files and reported eight warnings; `ripwire . --quality-delta --scope=work/omp-secret-probe/probe.mjs,work/omp-secret-probe/test_omp_secret_probe.py --legend=compact` reported gating=0 but seven new-symbol rows against git HEAD, which lacks the untracked probe; neither scan establishes a clean baseline.
- A separate keyless two-arm inspection (N=1 per arm) observed two local requests and one successful `bash` result per arm. Masked: raw host frame contains the planted synthetic marker, full provider request and role=tool value omit it, benign text survives; SHA-256 host frame `6304d15b2ad1f0b1ad1577c6cb242480b56f8238ab8fcfd08f1f10e29c5754d9`, exact request `c02a6a64f51f83c3eea3928b3183cc1e3e6a1cc25d3c4fbb6b16eead6914fe76`, role=tool JSON `802d6017a2f5680749efc17b2e2c1686d44a0f8f63cf307f4c71b7be9129f1e1`. Disabled-control: host and exact outbound request contain the marker while benign text survives; corresponding SHA-256 `6d696c574f8fd9deb4d704a7fea337ce596f2518980123660360b1c90813f7f6`, `09dc2ac11c3e0567138d1d532745cfd1aae609839377b8b1870f2f800680003b`, `76760e22de5b7e1513419a4e438f120cfb15519b36e988559abca8d232bb46f4`. No captured request body or synthetic token is committed in this row.
- **Boundary / NO-CLAIM:** one freshly spawned local fake-provider route and an authored positive/negative are not an independent non-author provider capture, a loaded-fleet session, another profile/hook/extension, a real Jev response or a consumer outcome. Stage-15 loaded-session containment and recipient/data-class authorization remain separate blocking contracts; U06 awaits independent source-bound byte recount on the changed code before closing. No TypeSafe or paid comparator requests; incremental spend $0. Shared-owner source/test paths were not staged or committed by this pass.

## jev-p8-search-feasibility-n2ca independent read-only row audit (2026-09-29 UTC) [offline / downstream benefit HOLD]

- Pane 5 reported a bounded source/data audit against `docs/0927_reality_plan.md` SHA-256 `e6cd828eec947d6ab7297acf52ad4dd37b2be9c84f81e0161a6ca470d8ea3394`; `work/jev-l7ym/PREREG.md` SHA-256 `f97444a8b3c4c28f5e613f39d008659eda81d9530575a31a0dd8bc0af933715b` fixes the nearest non-authored direct-find bar at **100 matched windows and 20 discordants**, while P8 itself specifies a 30-day acquisition deadline, not a numeric benefit threshold. This ledger entry preserves that pane's read-only report; this pane did not rerun its count.
- Websearch rerank log SHA-256 `09d26ac088395fad3df9e806c99b3a2613f9a045e58c3f408a17b048637a55e7`: 44 rows = 18 observed / 10 answered / 16 errors, 19 session/query pairs; 0/10 answer rows flag `openedPick` or `openedRank1`, 9/10 have `nextToolCalls=0`, all 10 pick indices fit `resultCount`. Current rerank source SHA-256 `085a92a0e7fc10d59fc17db531431a988336ecec8ec2330ff528d354ace9b56b` cannot emit the completed no-open rows reported in the log; producer revision is **UNKNOWN**. Native find-rank checkpoint prefix SHA-256 `e0a2ebdcfc266c8774c08cb298baa65525a6dc024e370cf4cbbd9a10935bfc3c`: 117 complete windows across nine sessions, 35 returned-hit-hash touches / 82 not touched. Two later rows contaminated the post-start full-log snapshot (119 rows, SHA-256 `1becd1db593da6a48f3eb2a73dd71720f9fa1937383ac782299a9013b2d16875`); the first 117 **rows** reproduce the checkpoint hash. `EVAL.md:2659-2665` reports only 42 eligible joins against the 100-window bar.
- **Positive/negative and decision:** `.omp/hooks/post/jev-web-search-rerank.test.mjs:33-45` shows a selected URL can be flagged in a synthetic ten-open sequence, not organic reader benefit; no planted ten non-open calls followed by an eleventh open or wrong-result-only open exists. Current source `jev-web-search-rerank.ts:203-211` counts only open-like calls; `:160-177` logs no event/result identity. Therefore HOLD downstream reader-benefit and P13/new Jev traffic. NFCorpus qrels (n=234) are a separate public relevance result: top-1 delta +0.128, nDCG delta +0.02695 missed the +0.05 bar (`EVAL.md:2650-2658`).
- **Boundary / NO-CLAIM:** neither path touch nor synthetic selected-open test establishes same-item selection→open→use→answer, independently labelled organic outcome, open prevalence, causal lift, NFCorpus generalization or provider/P15 clearance. No provider/Jev call, Beads/code edit or credential from the read-only witness; incremental spend $0. Retry only with source-pinned eligible no-open windows, independent labels and event/result/tool/answer IDs joining those four stages, plus a RED arm counting an eleventh tool call after ten non-opens.

## P8 mixed-call window regression (2026-09-30 UTC) [offline / reader-benefit HOLD]

- At HEAD `99b0b6c8`, `.omp/hooks/post/jev-web-search-rerank.ts` SHA-256 `786aebc1cde1da563078692bab40eb444ff05d19a5e175605e6c6dd7adc0d5bf` counts each distinct post-search tool call, not only opens. `node --experimental-strip-types --test .omp/hooks/post/jev-web-search-rerank.test.mjs` passed **10/10**; test SHA-256 `6f9d6aab6be3068a6b121f3e0daaa95ad9312fa8812d934135f4b3144fa1928f`. The registered-callback regression sends ten distinct ordinary tool results (both hook event names per call) and then an eleventh-call open; the ten-call window closes with no opened pick/rank-1 and the eleventh open does not alter it. Duplicate callback IDs are counted once.
- **Decision / HOLD:** retain the prior source-bound data counts above (44 rerank-log rows; 117 complete find windows, 35 with a touched returned-hit hash) as historical observations, not a post-fix traffic measurement. At present **0/117** windows have a verified same-item open→use→answer outcome, independent relevance label, or same-event incumbent action; no named consenting reader is established, so **0 matched windows** qualify for the preregistered 100-window / 20-discordant comparison. Wake only when a named native-find operator permits the scoped data path and a source-pinned cohort joins search result, event/tool call, selected item, open, subsequent use, and answer with independent labels. P13 and new provider traffic remain inactive.
- **Boundary / NO-CLAIM:** this is a keyless test of the registered handler, not an omp-session firing proof, an organic readership estimate, consumer benefit, NFCorpus generalization, or P15/data-class clearance. Historical log rows were not reacquired after this source change. Zero provider calls; incremental spend $0.

## U06 independent source/readback of explicit-config local fake route (2026-09-29 UTC) [offline / narrow PASS]

- Pane 3 independently inspected the uncommitted `work/omp-secret-probe/probe.mjs` explicit `omp --config` route and read back both synthetic arms after the source change recorded above: the masked full provider request omitted the planted marker and retained benign output; the disabled control exposed the marker. Its focused Python suite reported **15/15**, and its Node syntax check passed; `ubs` reported 0 critical/8 warnings, including `json.loads`-handling heuristics and Bandit B404/B603. The exact Python discovery command run by this pane appears in the preceding U06 entry; the reviewer did not supply its invocations. No source/Beads/EVAL writes by that reviewer.
- **Boundary:** independent inspection and repeat of the **authored synthetic fake-provider route**, not a non-author real provider capture or a P15 session-wide containment check. Other profiles, loaded sessions, logs, credentials, Jev/TypeSafe traffic and consumer benefit remain NOT_RUN; U06 stays in progress. Incremental TypeSafe spend $0.

## jev-p2-gate-demand-qdtl independent frozen-cohort audit (2026-09-29 UTC) [offline / paired incumbent NOT_COMPARABLE]

- Pane 4 reported a read-only audit of `work/jev-1lim`: pinned source frame **1,684** commands (196 earlier-Jev-flagged, 1,488 unflagged), gate-log SHA-256 `985bb46db8a0fce8fedf412af280499abe4a4aabf9acb8ef3d8a3ad8499e556e`, manifest SHA-256 `d020751f969f2a8688be370a0ab7dbd44686d0b5de79777718bddc490ca790c9`, blind-label adjudication commit `0a3b7e50` and 396 complete non-author labels. Flagged: 47 harm / 149 no-harm; sampled random-unflagged: 0 harm / 200 no-harm. Sample positive fraction **47/396=11.87%**; sample-majority no-harm **349/396**. The reviewer reports a weighted source-frame point estimate **47/1684=2.79%** and a one-sided 95% hypergeometric upper of 20 additional positives, yielding **67/1684=3.98%** as upper. These are arithmetic over this stratified frame, not Jev accuracy or organic operator benefit.
- **Planted join falsifier:** 0 confirmed same-event deterministic incumbent joins. All 396 manifest rows lack session/eventId/toolCallId/DCG-action fields; `existing_flag` is a prior Jev flag, not DCG. The source `work/jev-1miz/final-receipt.json` already recorded `dcg_joined_rows=0/560`, `NOT_COMPARABLE`. `work/jev-uncd`'s 558 rows inherit pending/non-author-disputed `jev-1miz` labels (79 disagreements), not a second independent prevalence sample; committed item SHA-256 `c6ed1feb32e05bf73fc9cc0fe4785a159c80ba6336795f614edcda7cac992e1d`, `jev-1miz` manifest SHA-256 `e533581eaefa9cc4259865a567e6dfbaf81a75e16e3e13d1c0d6ce4cdcaa1849`.
- **Repeated-command negative:** `jev-1lim` has 15 repeated command-hash groups/16 extra rows; `jev-1miz` has 13/52. Hash `33eac1438d2004a77f986a64ebbcef428f634b75e90ee53f38cf939b8b8711b4` maps to two `jev-1lim` rows with conflicting harm labels (`7fadd62e2c548d647376f59affb9c808f86c5c2085375adca422969bc1a781f5` harm:5, `8a0d492e8d59700b934899cf76c3b321668ca369a61c0cdee3a1af5ecaf09766` no-harm) plus a different `jev-1miz` row ID. Thus hash-only matching is not an event join. Current mutable `gate-observe` log SHA-256 `b4d6154f6ce0c775f2d7202c8d90783563e47cef49d19a89611215c186ce1c1d` has 16,847 rows, **not** the pinned frame; `.omp/hooks/post/jev-gate-observe.ts:151-163` records no eventId/toolCallId/DCG outcome.
- **Decision / NO-CLAIM:** keep P2 benefit/paired-model promotion HOLD pending frozen organic denominator, independent blind labels and **actual same-session/event/toolCallId** incumbent action/outcome rows (including missing rows). No operator action, clean-call no-action, interruption, reviewer-time, Jev quality, provider safety or causal benefit inferred. The witness made no Jev/provider request, Beads/EVAL/code write or assignment change; incremental spend $0. This pane preserved the supplied receipt without rerunning reported checks.

## P15 independent outbound-path source audit (2026-09-29 UTC) [read-only / NOT_CONTAINED]

- Pane 5 checked frozen plan SHA-256 `4c2cb3a3b3ddbadd58b557a7cd155eec23c8870c3df0bd933d04708151bbfcdf` and Beads JSONL SHA-256 `a01b0525d9fb14bd51de45cff6accb77893e295251cace60cd5df6d22695cf24` against `.beads/issues.jsonl:274`'s operational route contract. Project hook defaults deny without injected authorization (`.omp/hooks/pre/jev-gate-shadow.ts:74-77`, `.omp/hooks/jev-shadow-worker.ts:1-5`); source-local fake POST/deny examples at `EVAL.md:2829,2850-2852` are not loaded-session evidence. The old loaded handler did score three events after source edits (`EVAL.md:2830`), so a changed checkout cannot certify that session safe.
- **Source counterexamples:** profile `jev-lab` config declares five extensions (`config.yml:25-30`, SHA-256 `8f1006059698ac67678a055135f4a5bf3ab35bf09a7756a870afa316e5e6cefd`). `omp-jev-observer.ts:32-50,67-88` sends raw bash command before checking toolCallId (source SHA-256 `021781cc6ef23e4be7a1dc06c0355d55d1a596005b2d063bdfc6a2934cba5855`); `omp-jev-route.ts:71-86` sends prompt text without approval/session-ID gate, while its expected `askJev` import is absent from `work/jev-client/src/index.ts:1`, leaving load status UNKNOWN (route SHA-256 `d05cbd632626b111e83087bc1796e9a4330ed17358d39e5e20dcf3d21d2e41bf`); `omp-jev-review.ts:62-96` can send git diff/show results without event/recipient authorization (SHA-256 `a05e3b5795488f6bebb39fbf554438ec8f4beeca58db9413926a07ed18dbb4bd`). No profile-specific fake credential/child recorder was observed. Installed `.omp/hooks/pre/jev-compact.ts:34-36` passes no admission callback, hence registers no handler; `compaction/src/omp-binding.ts:225-240` checks approval only at registration and handler `:100-182` lacks same-handler revocation check (binding SHA-256 `759a8f7aba864a2dca21393e55745a985a220fbc7217b1623dd4e3359cf34f05`). Model roles, scheduled canary and explicitly invoked tools are separate routes; configured does not mean loaded.
- **Boundary / decision:** P15 remains BLOCKED / NOT_CONTAINED until owner-approved safe quiescence or instrumented existing session, every route intercepted, and one authorized synthetic event yields one fake attempt/row while denied, duplicate, missing-ID, retry, secret-shaped and same-handler revoked events yield zero post-authorization effects. Read-only source inspection made no provider/credential/Jev request, test execution, repo/Beads edit or session restart; incremental spend $0. The Bead Notes still claimed `in progress` despite BLOCKED header as of this audit; owner was notified. No provider safety or consumer benefit claim.

## jev-545t Shopee cross-language Score retry (2026-09-29 UTC) [live, N=350]

- Frozen before live calls: `work/score-shopee/PREREG.md` SHA-256 `250339d85ca17eae000e178661b9287fbf0095cb65389ea041dfdec7853b6971`; 350-row public `scaredmeow/shopee-reviews-tl-stars` test split at revision `d096f402fdc76886458c0cfb5dedc829bea2b935` (MPL-2.0), corpus SHA-256 `e8799a4c8dcfb769ad51f5ce04fa28260814485a7e005c942ddac4cde005d663`. Reach receipt: `REACHABLE`, matching item/prereg hashes, `mcnemar`, repo-relative prereg path. Size preflight: 350 FITS, 0 NEAR, 0 OVER.
- Bounded live runner: `kit/experiment/run.py --detach --attached --live`, child `work/score-shopee/run.py`; Jev model `jev-1.13.0`, comparator `dots-studio/dots-3-note-preview:free`. `work/score-shopee/receipt.json` records `LIVE_COMPLETE`, 350 rows, no stop reason. Jev invalid 1 (`TypeSafeAPITimeoutError`); comparator invalid 11 (5 timeouts, 3 response-validation errors, 3 `TypeSafeError`); paired valid 338. On that intersection, MAE Jev `0.730769` and comparator `1.387574`; mean paired absolute-error difference `-0.656805`; 10,000 seeded sign flips (`20260927`) had 0 extreme draws, add-one p=`0.00009999`. Receipt records all three preregistered numeric conditions true.
- Independent non-author recount matched row uniqueness/counts, both MAEs, paired difference, seeded p-value, model IDs, error counts, and nearest-rank latency percentiles (Jev p50/p95 `290/491 ms`; comparator `19,160/41,517 ms`). Jev usage: 139,328 input / 6,282 output tokens; calculated input spend `$0.005851776` (`$0.005852` rounded). Comparator usage: 60,619 input / 701,599 output tokens; before/after provider usage snapshot unchanged.
- **Boundary / NO-CLAIM:** this is the preregistered Tagalog cross-language test, not English generalization. No product/consumer benefit, omp seam, or operational promotion was tested. Spend is calculated from recorded Jev input tokens and the preregistered rate, not an external billing event; provider usage snapshots were unchanged. No paid comparator.

## jev-p8-search-feasibility-n2ca search-window repair (2026-09-30 UTC) [offline / consumer outcome HOLD]

- **Correction to EVAL.md:3045, not a revised historic count:** the source reviewed there counted only open-like calls. The committed repair `0f23fe0f` counts every distinct downstream tool call; `d6b3e335` binds the real `(event, ctx)` extension callback to `ctx.sessionManager.getSessionId()`, scopes duplicate IDs by session, and emits a pending window when a subsequent search replaces it. The earlier 44 websearch rows and 117 native-find windows in EVAL.md:3044 were not regenerated or rescored.
- **RED and offline proof:** three new tests failed before the context/overlap repair (7/10 passing); `node --test --test-force-exit .omp/hooks/post/jev-web-search-rerank.test.mjs` passed **10/10** after it. The registered-callback test at `.omp/hooks/post/jev-web-search-rerank.test.mjs:47-71` sends ten distinct `web_fetch` results through both captured event callbacks, obtains one row with `nextToolCalls=10` and `openedPick=false`, then sends an eleventh selected open and confirms the row count stays one. A separate keyless `node --input-type=module` registered-hook smoke with an injected asker/append and context-shaped session manager reproduced one row at ten ordinary calls and a `permission-required` row with no requester when approval was absent. `node --check` passed both changed files. `ubs` on those two files exited 0 (0 critical, 13 heuristic warnings); scoped `ripwire . --quality-delta --json` after the repair commit reported zero new gating findings against HEAD. No actual omp host event or TypeSafe request was exercised; incremental spend **$0**.
- **Independent read-only source check:** pane 2 checked `d6b3e335` against ExtensionRunner's event/context contract and found no newly reachable consumer failure under exact single-event admission. It identified a *latent* two-admitted-search same-session race if admission is broadened: parallel asks completing in reverse order can overwrite one pending window (`.omp/hooks/post/jev-web-search-rerank.ts:203-220,256`). The installed default supplies neither asker nor approval, and the current test uses a stub registrar; neither an actual loaded-session firing nor concurrency under widened admission has been proved.
- **Decision / Boundary:** P8 remains **HOLD** for same-item event/result/open/use/outcome joins, independent labels and recipient/data-class authorization; P13 remains inactive and P15 is **NOT_CONTAINED**. This is offline hook bookkeeping, not organic reader benefit, provider safety, model accuracy, L3 runtime wiring or a new Jev verdict. Source rows lacking event/result IDs cannot be promoted to same-event outcomes; rerun the source-derived negative on the actual join path before any such claim.

## jev-p1-stranger-baseline-przc additional independent clean-checkout readback (2026-09-30 UTC) [offline / P1 BLOCKED]

- **Source and revision:** pane 4's read-only witness used an already provisioned, git-clean checkout at `var/agent-tmp/jev-p1-fixed-20260928`, `a1bd64bb237f2657ac6556a14189534891a92572`, clean before and after. Dependencies and `kit/dist/client.js` were present; it did **not** run `npm ci` or a new install. Its earlier no-key `doctor --robot` command, `env -u TYPESAFE_API_KEY -u JEV_API_KEY npx --prefix kit --no-install jev doctor --robot`, exited **2 / NOT_RUN**, model `jev-1.13.0`. This does not establish that a machine Infisical key was absent; only the subprocess environment was keyless.
- **Positive:** the six documented fixture-backed `--fake` commands (ask Choice, verify, score, classify, gate, rerank) each exited 0 on that checkout. `env -u TYPESAFE_API_KEY -u JEV_API_KEY node --test kit/test/validate.test.mjs kit/test/install.test.mjs` exited 0 (**9/9**) for response validation and install contracts. Installation tests checked the READY manifest, successful flag/screen imports, byte-identical host extension list and `MANUAL_REQUIRED` without writing `.omp/config.yml`. An injected synthetic in-memory `askJevChoice` 401 probe exited 0 with `ok:false`, `reason:http`, `injectedCalls:1`, `globalCalls:0`; no network request or real credential.
- **Negative / Boundary of pane 4's witness:** an unmanaged `jev-gate.ts` collision exited **1** without altering its bytes, and a legacy managed-config collision also refused without overwrite. Numeric-claim zero-asker and qualitative-route arms were **NOT_RUN by that witness**, and the 401 probe was inline with no persisted command or receipt. These are suite and in-memory observations, not proof of a live installed extension.
- **Additional same-checkout keyless arm run by this pane:** from `var/agent-tmp/jev-p1-fixed-20260928` at `a1bd64bb237f2657ac6556a14189534891a92572`, `env -u TYPESAFE_API_KEY -u JEV_API_KEY node --test work/jev-claim-check/claim-check.test.mjs` exited 0 (**3/3**). The numeric test refused a ratio, percentage and unit with `calledModel=false` and **zero** injected asker calls; the qualitative test called its injected asker once and returned `supported` for value 0.8; malformed/absent-key tests returned `not_run`. `git status --short --branch` afterwards showed only `## main...origin/main` and `git rev-parse HEAD` matched the pinned SHA. No provider request or spend.
- **Reproducible transport shape, not a live credential:** an independent same-checkout `node --input-type=module -e` probe invoked `askJevChoice` with `apiKey: ["fixture","key"].join("-")`, a two-class synthetic state, `fetchImpl` returning `new Response(JSON.stringify({error:"unauthorized"}), {status:401, headers:{"Content-Type":"application/json"}})`, and a global fetch override that throws. Assertions on `result.ok === false`, `result.reason === "http"`, `injectedCalls === 1` and `globalCalls === 0` all passed; process exit **0**, output `{"ok":false,"reason":"http","injectedCalls":1,"globalCalls":0}`. Both real key env vars were removed for the subprocess; the script exists only in this session's transcript, not a committed portable command. No request reached a provider.
- **Remaining P1 limit:** the 401 arms are inline and lack a committed one-command receipt; subsequent kit/README files differ from this pinned checkout. Stage-15 aggregate remains RED under HazySpring's separate owner/wake condition, not a gate to weaken. P1 stays **BLOCKED** pending a portable same-revision handoff and source-linked stage-15 disposition; P9 stays gated. Neither this receipt nor EVAL.md:3014-3017 certifies the current checkout's public quickstart, a live Jev answer, omp L3, action safety, aggregate green, model accuracy or consumer benefit. Incremental TypeSafe spend **$0**.

## 0927 committed plan-to-Beads fresh-eyes gate (2026-09-30 UTC) [offline static review / 2 of 2 zero-new]

- **Frozen source:** `d6b3e335f790847582ec697020f31297f6f667b9` contains plan Git blob `41384e3be9e5e64af2e54b2cff695f20677b8774` (SHA-256 `4f76481655627136eb86a92eb506ac8916fa140832523539acc83fcfb3ffc8cc`) and `.beads/issues.jsonl` blob `6d956f41c2355a0b1ef1847ea84f97f0933d6f9d` (SHA-256 `7a64aec59b897b53115c6d3ef0a6e1412c27b5cda69eb7789b5443061a627a78`). This pane confirmed both blobs and content hashes with `git rev-parse d6b3e335:<path>` and `git show d6b3e335:<path> | shasum -a 256`. Neither reviewer graded the mutable worktree `.beads/issues.jsonl`.
- **Two independent zero-new rounds after the last committed repair:** pane 5 read the entire 352-line plan and all **18/18** P0–P9/P11–P15/U04/U06/U07 records, reported **zero new conversion contradictions**, 18 nodes/19 internal edges/zero cycles; it corrected its initial omission of the committed P8 mixed-call test after rereading `.omp/hooks/post/jev-web-search-rerank.test.mjs:47-71`. Separately, pane 4 re-read the exact frozen plan and **18/18** Beads using `git show d6b3e335`; its independent result was **zero new contract, activation or dependency contradictions**. Pane 4 explicitly corrected a manually transcribed wrong plan blob in its first readback; the corrected blob above matches this pane's `git rev-parse` and pane 5's SHA-256. Earlier finding-bearing reviews of other commits do not count toward this **2/2 static plan-to-Beads gate**.
- **Count chronology:** the reviewed frozen plan's `0/2` at `docs/0927_reality_plan.md:74,142,347` is its pre-review as-of statement, not a post-review verdict. Pane 5's corrected full-plan result was round **1/2**; pane 4's independently corrected same-blob result was round **2/2**. The count lives in this later receipt; the frozen plan was not edited to manufacture a passing review or change the reviewed bytes.
- **Graph/readback:** `RUST_LOG=error br dep cycles --json` returned `{"cycles":[],"count":0}`; `RUST_LOG=error br sync --status --json` reported healthy storage, 405/405 unique/exportable records, `dirty_count=0`, `jsonl_newer=false`, `db_newer=false`, `coverage_drift=false`. P1→P9 remains keyless and independent of P0; P2/P8 are keyless audits, P5's provider branch retains P3/P4/P15/U04/U06/U07 gates, P13 needs P8/P15 plus a named reader and a selected-search-or-gate-ineligible/concluded condition. `jev-wiya` retains its separately notated original scored-row condition, not a precondition for P5 keyless work. Acyclic storage and reviewer agreement do not constitute operational acceptance.
- **Boundary / NO-CLAIM:** pane 5 and pane 4 performed read-only static review, **no tests or provider/TypeSafe calls**; incremental TypeSafe spend **$0**. Pane 4 disclosed `$0.002462` for 11 internal `tool.find` source-location requests in its review; this was not a Jev call. P8's logged rows lack event/result joins; P15 remains **BLOCKED / NOT_CONTAINED** for loaded-session/profile/background egress and same-handler revocation. P1 remains **BLOCKED** on its portable same-revision handoff; P9 public claims remain gated. This 2/2 result approves only the plan/Beads *conversion contract*, not code behavior, execution readiness for provider-bound branches, runtime safety, model benefit or a §4 validated integration.

## jev-p1-stranger-baseline-przc published-main handoff (2026-09-30 UTC) [offline / bounded baseline; aggregate RED]

- **Source and revision:** a fresh public `git clone --branch main --single-branch https://github.com/JYeswak/jev_playground.git` with the documented HTTP user agent exited 0 at `7fecd59dcc84502d265c9d2acac411337edba806`, origin and branch checked, porcelain clean (`var/agent-tmp/p1-current.51372.0f8d96eb/checkout`). This published SHA descends from the reviewed `4b0a588b`; the older README assertion that publication had not happened was corrected locally, not pushed.
- **Public CLI, no key:** a separate clean checkout at the same SHA (`var/agent-tmp/p1-cli-p2`) ran `env -u TYPESAFE_API_KEY -u JEV_API_KEY npm ci --prefix kit` (exit 0), all six documented `--fake` Choice/verify/score/classify/gate/rerank commands (6/6 exit 0), `npx --prefix kit --no-install jev doctor --robot` (exit 2, `NOT_RUN`, `jev-1.13.0`), and the real no-key Choice command (exit 2, `unconfigured`, no provider call). Exact argv, exits and stdout/stderr are in `var/agent-tmp/p1-cli-p2-evidence/receipt.txt` and adjacent files. Fake results are tool-plumbing results, not model accuracy.
- **Refusal and routing, no network:** a clean locally cloned checkout pinned to the same published SHA ran `npm ci --offline --prefix work/sdk` (exit 0) and the inline `node --input-type=module -e` probe printed in `var/agent-tmp/p1-refusal-p3-20260930-0338-receipt.md` (exit 0). Injected HTTP 401 and malformed Noul each refused; the downstream `verifyClaim` action count stayed zero, global fetch calls stayed zero, two digit-bearing claims made zero injected asks, and a qualitative claim made one injected ask. Synthetic responses and claims only; the full command source is in that scratch receipt, not a committed executable.
- **Installer, same published SHA:** in the clean pane-5 checkout, keyless `node kit/bin/jev.mjs omp install --dir <disposable-positive> --robot` exited 0/`READY`; the 27 manifest file hashes matched, installed gate/flag/screen imports exited 0, and no `.omp/config.yml` was created. A planted unmanaged `jev-gate.ts` collision exited 1 with its pre/post SHA-256 identical (`47ed21c6…44b57033e`), and a legacy manifest marker for `files.config.yml` exited 1 with manifest bytes unchanged (`5b9704c0…6a7437fde`). These checks did **not** exercise preservation of an existing host extension list: the scratch `.omp/config.yml` fixture write was refused by kit-guard B7. No bypass, no silent equivalence between an absent config and byte-preservation.
- **Stage-15 diagnosis and correction:** a focused gate run before the correction reported 430 PASS, 1 FAIL, 3 SKIP; the four older expected-string misses now passed, while `rollout-key-infisical` exposed a false claim that the disabled review extension fetched an Infisical key. The source `.omp/extensions/jev-review.ts:1-11` has no such call; `.omp/tools/jev-rerank.ts:22-23` separately calls `useInfisicalKey` without an injected asker. After correcting `docs/LEDGER.md:250,252` and the five affected enforced rows in `foundation/kit/claims.tsv`, `python3 foundation/kit/claim-units.py docs/LEDGER.md foundation/kit/claims.tsv` counted **119 covered of 120 candidates**; `foundation/kit/claim-coverage.floor` was raised from 118/119 to **119/120**, not weakened. The subsequent `bash foundation/gates.d/15-kit-claim.sh` exited 0: **431 PASS, 0 FAIL, 3 SKIP**, coverage 119/120 at the new floor. A planted false review-key row against the same extension source failed with exit 1 while the truthful disabled-scorer row passed (`var/agent-tmp/p1-claim-red.11143/claims.tsv`). The stage-15 owner was notified; the aggregate/selftest outcomes below predate this final floor raise and do not certify a current full aggregate.
- **Same-checkout refusal proof:** the original injected probe was run again **without installing or editing anything** in the pane-5 *public-origin installer checkout* `var/agent-tmp/p1-install-p5`, still clean at `7fecd59dcc84502d265c9d2acac411337edba806`. `env -u TYPESAFE_API_KEY -u JEV_API_KEY node --input-type=module -e <source in var/agent-tmp/p1-refusal-p3-20260930-0338-receipt.md>` exited 0: injected 401 (`http`) and malformed Noul (`no-answers`) refused, downstream actions 0, global fetches 0, two numeric claims made 0 asker calls, qualitative claim made 1. The exact argv, source hash `bc4986f7aaad5c7848730e487084e51a06f12659d8ad5e6907d064fcd0b43022`, stdout and clean-before/after status are in `var/agent-tmp/p1-install-p5-same-checkout-refusal-20260930.md`. This is the same checkout that proved the installer collision, not just the same revision.

  Executed `-e` source (from the published checkout root, with both real key variables unset):

  ```js
  import assert from 'node:assert/strict';
  import { askJev, SYSTEMONE_ENDPOINT } from './kit/src/client.ts';
  import { verifyClaim } from './kit/src/verify.ts';
  import jevClaimCheckTool from './.omp/tools/jev-claim-check.ts';
  let globalFetchCalls = 0;
  const savedFetch = globalThis.fetch;
  globalThis.fetch = async () => { globalFetchCalls++; throw new Error('global fetch forbidden'); };
  let http401Calls = 0;
  let malformedCalls = 0;
  let downstreamActions = 0;
  const response = (body, status = 200) => new Response(body, { status, headers: { 'content-type': 'application/json' } });
  const http401Fetch = async (url) => { http401Calls++; assert.equal(url, SYSTEMONE_ENDPOINT); return response(JSON.stringify({ error: 'synthetic unauthorized' }), 401); };
  const malformedFetch = async (url) => { malformedCalls++; assert.equal(url, SYSTEMONE_ENDPOINT); return response(JSON.stringify({ model: 'jev-1.13.0', answers: { value: { noul: 1.5 } } })); };
  const base = { state: { claim: 'The record establishes a general conclusion', evidence: 'synthetic evidence' }, questions: { value: 'Does the evidence support the claim?' }, apiKey: 'synthetic-test-key', model: 'jev-1.13.0', timeoutMs: 1000 };
  async function assertNoAction(fetchImpl) {
    try {
      const result = await verifyClaim({ claim: 'The record establishes a general conclusion', evidence: 'synthetic evidence', ask: (options) => askJev({ ...options, apiKey: 'synthetic-test-key', model: 'jev-1.13.0', timeoutMs: 1000, fetchImpl }) });
      downstreamActions++;
      return result;
    } catch { return null; }
  }
  try {
    const unauthorized = await askJev({ ...base, fetchImpl: http401Fetch });
    assert.equal(unauthorized.ok, false);
    assert.equal(unauthorized.reason, 'http');
    assert.match(unauthorized.error, /401/);
    assert.equal(http401Calls, 1);
    assert.equal(await assertNoAction(http401Fetch), null);
    assert.equal(downstreamActions, 0);
    const malformed = await askJev({ ...base, fetchImpl: malformedFetch });
    assert.equal(malformed.ok, false);
    assert.equal(malformedCalls, 1);
    assert.equal(await assertNoAction(malformedFetch), null);
    assert.equal(downstreamActions, 0);
    let injectedAsks = 0;
    const tool = jevClaimCheckTool({ zod: { object: (shape) => shape, string: () => ({ min: () => ({}) }) } }, async () => { injectedAsks++; return { ok: true, scores: { value: 0.8 }, latencyMs: 1, model: 'synthetic' }; });
    for (const claim of ['The rate equals 42%.', 'The ratio is 3/5.']) {
      const refused = await tool.execute('synthetic-id', { claim, evidence: 'synthetic evidence' });
      assert.equal(refused.details.reason, 'numeric-out-of-scope');
    }
    assert.equal(injectedAsks, 0);
    const qualitative = await tool.execute('synthetic-id', { claim: 'The record establishes a general conclusion.', evidence: 'synthetic evidence' });
    assert.equal(qualitative.details.verdict, 'supported');
    assert.equal(injectedAsks, 1);
    assert.equal(globalFetchCalls, 0);
    console.log(JSON.stringify({ result: 'PASS', modelPinned: 'jev-1.13.0', http401: { injectedFetches: http401Calls, refusal: unauthorized.reason }, malformed: { injectedFetches: malformedCalls, refusal: malformed.reason }, downstreamActions, numericClaims: 2, injectedAsksForNumeric: 0, qualitativeClaims: 1, injectedAsksForQualitative: 1, globalFetchCalls }));
  } finally { globalThis.fetch = savedFetch; }
  ```

- **Existing-host-config acceptance:** `env -u TYPESAFE_API_KEY -u JEV_API_KEY TMPDIR=/Users/josh/Developer/jev/var/agent-tmp/p1-install-suite.37332/ node --test kit/test/install.test.mjs` in that public-origin checkout exited 0, **4/4 pass**. The pre-existing test asserts host `.omp/config.yml` byte identity plus `extensionActivation=MANUAL_REQUIRED`, unmanaged collision preservation, and older managed-config refusal without overwrite (`kit/test/install.test.mjs:58-92`). Its owned temp fixtures remain under the stated TMPDIR; the earlier B7 refusal applied to a manual tool write of a scratch fixture, not this normal test run. No `KIT_GATE_EDIT` or guard bypass.
- **No-SDK cold clone boundary:** before `npm ci` in the other clean public clone, `TYPESAFE_API_KEY=[REDACTED] node kit/bin/jev.mjs doctor --robot` exited 1 with `ERR_MODULE_NOT_FOUND` for `kit/dist/client.js`; it did **not** report READY, but it did not produce a typed `NOT_RUN` either. README orders `npm ci --prefix kit` before doctor; the no-key installed path above is the typed refusal. No real key or provider call was involved.
- **Aggregate after targeted repair:** with real key variables unset and `TMPDIR=/Users/josh/Developer/jev/var/agent-tmp/p1-claim-red.11143`, `bash foundation/gates.sh` ran 2026-09-30 04:20–04:25 UTC and exited 1: **16 PASS, stage 80 RED** (`scripts/selftest-consumer-check.sh`: 11 ok/1 failed; `scripts/selftest-test-registry-hook.sh`: references absent `githooks/pre-commit-test-registry.sh`). This is an unrelated live gate defect, not a stage-15 miss or aggregate GREEN. The distinct `bash foundation/gates.sh --selftest` run at 04:25–04:41 UTC exited 0: **17 stage selftests PASS / ALL GREEN**, including stage 15's planted RED. `foundation/gate-outcomes.tsv:5962-5994` records per-stage exit codes at `d6b3e335`. Joshua selected “Authorize test scratch cleanup” and then “Confirm and run” after the exact commands and affected test-only paths were listed; those two commands ran with their scripts' temporary-file cleanup, including internally invoked `rm -rf` on self-owned test fixtures. No other deletion was performed by this pane.
- **Boundary / next wake:** P1's bounded keyless stranger acceptance has a same-checkout negative and installer readback; its owned README/ledger/registry changes were saved as `4b996c3a` without the sibling EVAL and rerank edits. Stage 15 passed its targeted gate at 431 enforced PASS, 0 FAIL, 3 SKIP with the 119/120 coverage floor, but the ordinary aggregate remains **RED at stage 80**. The missing registry-hook script belongs to the existing blocked `jev-5vps` (WindyLantern); wake on an actual hook implementation, then run `bash scripts/selftest-test-registry-hook.sh`. ChartreuseAspen owns diagnosis of the independent `scripts/selftest-consumer-check.sh` 11/12 failure; the immediate next command is its targeted selftest, followed by a source-level fix and a new aggregate receipt. Neither RED is waived by P1 closure. Do not call this §4 validated. No live Jev/API call, paid comparator, recipient authorization, loaded omp L3, provider safety, or consumer benefit is established. Incremental TypeSafe spend **$0**.

## jev-3e2i STS-B free incumbent availability (2026-09-30 UTC) [live provider refusal; no score]

- **Source / bar:** `docs/demos/upstream-repro/openrouter-incumbents-20260924.md:352-382` is the append-only receipt. The frozen run-2 feasibility bar qualified `nex-agi/nex-n2.5-mini:free` at 50/50; Amendment 3 removes all paid comparisons. Runner SHA-256 `71589726c4ee8d1a37d6a09c2e2c1465c4d24bcd40c0a88df22c8f5571c5ffcb`; STS-B source `work/score-stsb/run.py@8e4bda9`.
- **Live attempt:** preflight account free requests 0/1,000 at 17:16:15Z; one bounded `--resume --limit 1` request on failed public item 10 (573 ms) returned `TypeSafeNotFoundError` HTTP 404: the `:free` model was unavailable. The provider-suggested paid slug was **not called**. The row file moved from 385 attempts / 385 unique IDs / 352 answers / 33 errors to 386 attempts / 385 IDs / 352 answers / 34 errors; the five earlier 404 rows (IDs 380–384) remained untouched. Item 10 has exhausted its one permitted resume. Postflight free requests remained 0/1,000 and cumulative usage remained 100.199757412; observed incremental charge $0.
- **Boundary / wake:** `STOPPED`, not scored and not a comparator verdict. No main-pass item or other model was called in this attempt. Do not retry this exact `:free` id without fresh availability evidence; do not substitute the paid slug. A separately qualified `:free` model may be tried under the unchanged frozen bar and account-wide cap. No Jev/TypeSafe call, organic consumer outcome or model win is established by this provider refusal.

## jev-p15-contain-automatic-egress-810p synthetic OMP deny-route reproduction [offline / HOLD]

- 2026-09-30. Scratch-only fresh OMP RPC session `01a0f3a9-d58e-748c-83af-3a2661b433ca`, profile `p15-fake-key`, repository HEAD `bc8bd10bf41058194fb582b221593a470d68927f`. Installed extension source SHA-256: `88937f797b515e94c33de7c0f9f775f630ab0df335ba79b869186d9653a97bd1`.
- The OMP session invoked three synthetic `bash` calls through the actual review hook. `call-p15-1` ran `git diff --cached -- src/eligible.ts`; hook decision entry `36e232f3` logged `review_not_applicable` / `permission-denied` (`commandSha=a864c0640befa959855584f4cd39cf28704420c5fb38d1879b7f6cd2d3af3fc4`). `call-p15-2` ran `git diff --cached -- src/ordinary.ts`; decision `ec68e3d8` logged the same refusal (`commandSha=f3c5e250593afda176afa6a94adf9f133be7a18ac88434e38301c9cd6b0a174a`). `call-p15-3` ran `git diff --cached -- src/secret.ts`; decision `d2a0c57c` logged the same refusal (`commandSha=1ac050dfa6960e3c58d1385fe371e78227ab63604a4a15d3747b5d41426f8728`). Corresponding OMP tool-result message IDs: `8fd9c2de`, `9dc2947c`, `d93dc146`.
- **Route distinction:** all three `bash` executions returned diffs to the ordinary loopback OMP model, including a synthetic secret-shaped marker. `work/omp-jev-review/src/index.ts:269-273` refuses *automatic Jev review* before its separate `readDiff`, and returns `undefined`, not `{block:true}`; it does not block the user's Bash call or mask its ordinary tool result. This observation is not a TypeSafe-egress failure. Primary-model output masking is the separate U06 boundary; its exact provider-visible result still needs independent acceptance.
- Counts: TypeSafe/Jev provider attempts `0`; credential-provider lookups `0 recorded` (no Infisical attempt ledger was created); local fake OMP-model requests `12` to the loopback server; Git diff process starts `3` in `git-trace2-stream.jsonl` (eligible/ordinary/secret), nested Git `child_start` events `0`. The fake-model request log exposed only built-in tools.
- **Verdict:** `HOLD`; this is not L3 and does not close P15. The recorded denied events have zero observed TypeSafe/Jev attempts, but no synthetic approved event reached a fake Jev asker, no authoritative cross-route attempt/credential census was taken, and loaded human sessions were not examined. Do not claim session-wide containment from these three denied review events.
- **Boundary / next:** synthetic byte-derived scratch diffs and a loopback *primary* model only; no real key, TypeSafe/Jev request, paid comparator, customer data, or production-session claim. In an owner-safe fresh session, exercise a separately approved synthetic Jev event against an injected fake asker and the same denied eligible/ordinary/secret-shaped cases, count extension-owned git starts and TypeSafe attempts after settlement, then independently read back every configured automatic route. Do not alter ordinary Bash execution to make a Jev-denial test pass.

## jev-p9-stranger-quickstart-2srw checkout and provenance repair (2026-09-30 UTC) [offline keyless / owner; independent review pending]

- **Source/revisions:** runner and 14-command expectation TSV committed as `9241cda7`; public `main` source and separately pasted clone both resolved to `b3e1cd89a5ba1e09ec318471cb325481590231f4`. No vendored clone was edited. `docs/demos/upstream-repro/stranger-run-expected.tsv` adds the actual `git remote get-url origin` and `git rev-parse HEAD` commands; the runner now verifies their exact output as well as exit status, refuses executing checkout commands from the enclosing Git repo, and preserves only the known checkout SHA through output redaction.
- **Positive:** `env -u TYPESAFE_API_KEY -u JEV_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY python3 scripts/stranger-run-jev-playground.py --source https://github.com/JYeswak/jev_playground.git --expect docs/demos/upstream-repro/stranger-run-expected.tsv --out var/agent-tmp/p9-owner-cwd-repair-20260930/stranger-receipt-post-sha-fix.md --timeout 600` exited 0, `EXPECTATION PASS rows=14`: 12 commands exited 0, doctor and real no-key Choice explicitly exited 2/`NOT_RUN`. Selftest exited 0 with planted missing command, altered Banking77 metric, wrong cwd, wrong origin, wrong SHA, and SHA-redaction controls; `uvx ruff format --check --diff` and `uvx ruff check` passed; `ubs scripts/stranger-run-jev-playground.py` exit 0, 0 critical/0 warning.
- **Planted negative:** in an owned ephemeral public-source scratch checkout (`var/agent-tmp/stranger-run-20260925-28320/clone`), moved only README's `cd jev_playground` line beneath both Git provenance commands. Re-running the runner with `--source` that path exited 1 after the clone and *before* `git remote get-url origin`, reporting `README checkout cwd mismatch`; no false `EXPECTATION PASS`. The first unmodified public run exited 1 on two missing TSV expectations; the second exited 1 because the 40-hex HEAD was redacted before comparison. Both defects were fixed without changing the bar or public README.
- **Boundary / next:** this is an owner keyless public-readback, not a Jev/API call, published change, consumer-benefit result, or independent P9 closure. `ripwire . --quality-delta --scope=scripts/stranger-run-jev-playground.py --legend=compact` exited 2 on three preexisting-worse complexity/verbosity findings in the already-long `main` and selftest; no green quality-delta is claimed. The aggregate gate has a separate stage-80 RED for the absent registry hook. WildCarp owns independent same-revision positive/refusal and full README/LEDGER cell audit before P9 may close.

## jev-p9 checkout-root regression and public claim boundary (2026-09-30 UTC) [offline keyless / owner; independent review pending]

- **Runner revision / RED:** `b99a5388` changes `assert_checkout_cwd` to compare the active directory's *actual* `git rev-parse --show-toplevel` with the intended checkout. Before that fix, the new selftest called it with `repo/scripts` as both active directory and expected checkout; lexical equality falsely accepted it although Git found the parent repo. The planted selftest exited 1 with `nested README cwd inherited parent Git root`.
- **GREEN / source:** after the fix, `env -u TYPESAFE_API_KEY -u JEV_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY python3 scripts/stranger-run-jev-playground.py --selftest --expect docs/demos/upstream-repro/stranger-run-expected.tsv` exited 0, including nested-parent refusal and real-root acceptance. An owner public-source replay at `https://github.com/JYeswak/jev_playground.git` recorded `b3e1cd89a5ba1e09ec318471cb325481590231f4` and all 14 README command rows (12 exit 0, doctor and no-key real Choice exit 2/`NOT_RUN`) in `var/agent-tmp/p9-cwd-fix.89435/public-positive.md`. A separate altered scratch README with `cd jev_playground` moved after provenance commands exited 1 before grading. `uvx ruff format --check` and `uvx ruff check` passed; `ubs scripts/stranger-run-jev-playground.py` reported 0 critical, 0 warning, 14 info; `ripwire . --quality-delta --scope=scripts/stranger-run-jev-playground.py --legend=compact` reported four minor/preexisting-worse and zero gating regressions, not a clean quality delta.
- **Published-claim boundary:** local `40c36af7` changes the root README and `scripts/render-results.py`: NFCorpus's +0.027 nDCG@10 misses the preregistered +0.05 joint bar despite its top-1 pass, the free comparator's $0 is separate from Jev's $0.0882 eligible-run/$0.3354 total spend, and 1,711 OMP judge calls are a 2026-09-25 session-file census, not a standing daily rate. `python3 -m unittest scripts.test_render_results` and `python3 scripts/render-results.py --check` passed; the renderer test plants a receipt reporting PASS against failing measured deltas and requires refusal. This commit is local, not a public-main readback; the P9 public b3e1 README/LEDGER all-cell audit and independent same-revision positive/refusal still belong to WildCarp. No provider key/call, paid comparator, public push, aggregate GREEN, or P9 closure is claimed. The README style gate separately reports preexisting Limitations/About Contributions gaps and 0.68 emdashes per kB; full Ruff reports preexisting ISC004 concatenation diagnostics, so those are not cited as passes.

## jev-p9 same-source non-author replay and second-clone challenge (2026-09-30 UTC) [offline keyless / P9 OPEN]

- **Source:** WildCarp's non-author replay used runner SHA-256 `2e1dac05a8e3f130dc0bd83eddd7cdbdacf542be0b05f7d7ac507b74836e1afe` against fresh public `https://github.com/JYeswak/jev_playground.git` at `b3e1cd89a5ba1e09ec318471cb325481590231f4`; its Mail receipts are `43633` and `43639`. I separately cloned public `main` at the same SHA into `var/agent-tmp/p9-independent-2109-positive`, ran `python3 scripts/stranger-run-jev-playground.py --source var/agent-tmp/p9-independent-2109-positive --expect docs/demos/upstream-repro/stranger-run-expected.tsv --out var/agent-tmp/p9-independent-2109-positive-receipt.md` with six provider key variables unset and the documented Git/npm user agent; exit 0, `EXPECTATION PASS rows=14`: 12 exit 0 and the two live-command no-key refusals exit 2. This is a challenge of the non-author result, not a second independent author.
- **Three fresh-source negative controls, bar unchanged:** (1) a separate public clone at b3e1, with only the scratch README's `git remote get-url origin` and `git rev-parse HEAD` moved before `cd jev_playground`, exited 1 after clone with `README checkout cwd mismatch` and no graded receipt. (2) a clean same-origin scratch checkout fetched directly at `7fecd59dcc84502d265c9d2acac411337edba806` exited 1 before executing README commands: the pinned b3e1 README clone revision differs from source 7fecd59. (3) a separate b3e1 public clone with only the scratch README Choice command changed from `--fake` to no `--fake` exited 1 `EXPECTATION RED`: missing original command and unexpected changed command; `var/agent-tmp/p9-independent-2109-fakeaslive-receipt.md` row 7 shows exit 2, `reason=unconfigured`, `latencyMs=0`, not a fake answer or provider call. The two deliberately modified scratch README files remain local edits; the wrong-SHA checkout remained clean. No public source was pushed or patched.
- **Public claim audit:** current root README generated row discloses NFCorpus's failed nDCG joint bar, both payer costs, and dates the 1,711-call OMP census; `python3 scripts/render-results.py --check` printed `README results table is current`. A separate current-source check found two stale present-tense cells in `docs/LEDGER.md:90,100`: gate-observe and review extension do not automatically ask Jev today. Both are corrected to describe `permission-required` / `permission-denied` with prior live receipts explicitly historical; `git diff --check -- docs/LEDGER.md` exited 0. This local ledger correction is not a published public-main readback.
- **Boundary / next:** all four replay arms were keyless and on macOS with the local toolchain. Neither reviewer nor challenger called Jev, a paid comparator, or a real provider, and neither established model quality, provider-visible session safety, stage-80 aggregate GREEN, or consumer benefit. P9 remains OPEN until the public README/LEDGER all-cell non-author audit against the corrected local revision is delivered and any contradictions are resolved; do not turn the two agreeing keyless runs into a live or production claim.

## jev-p15 isolated OMP positive and refusal route (2026-09-30 UTC) [offline fake-only / source-unbound scratch mechanics / P15 HOLD]

- **Boundary and source:** no product code, live profile, actual key, or real provider was modified or called. A fresh `omp/18.4.5 --mode=rpc` session used `p15fake/p15-probe` on loopback `127.0.0.1:18765`, with all six provider key variables unset and `work/omp-jev-review/src/index.ts` SHA-256 `fe853347e20014876245b86a1ca820efca9e55ec00bd137223a1f9a7aa16883f`. The copied test-only extension in `var/agent-tmp/p15-omp-route-20260930T180331Z.51372/project-positive/.omp/extensions/jev-review.ts` (SHA-256 `f7ae7cfe7a08cd0359111c59aad26a29a8cc32bed648473786ed5ee3f0ad5715`) approves only `callp151` for `git diff --cached -- src/eligible.ts`, injects a synthetic key and intercepts the TypeSafe URL in-process with a fake response. Its global fetch refuses every destination except that intercepted URL and the loopback model. This does not authorize any production Jev traffic.
- **Observed:** `var/agent-tmp/p15-omp-route-20260930T180331Z.51372/positive2-jev-log.jsonl` records authorizer true for `callp151`, exactly one fake TypeSafe attempt (`701` request-body bytes), then authorizer false for `callp152` and `callp153`; no fake TypeSafe attempt follows either denial. The persisted session `home2/.omp/profiles/p15-fake-key/agent/sessions/--Users-josh-Developer-jev-var-agent-tmp-p15-omp-route-20260930T180331Z.51372-project-positive--/2026-09-30T21-35-58-731Z_01a0f43e-e90b-7125-a049-54956905093c.jsonl` records `review_scored` with an advisory on `callp151` and `review_not_applicable reason=permission-denied` on the other two. `positive2-git-trace.jsonl` contains four Git `start` events: one extension-owned `--no-ext-diff --no-textconv` read of `eligible.ts`, followed by three ordinary Bash diffs (`eligible.ts`, `ordinary.ts`, `secret.ts`). Only the approved event caused extra Git execution. Both denied Bash calls still ran and their results reached the OMP session; the `secret.ts` tool result contains the synthetic `PASSWORD=synthetic-p15-only` marker without an advisory. The local fake primary model logged 15 loopback requests, including host retries after empty stop; no spend.
- **NO-CLAIM / blocker:** This is an author-operated, single-session scratch witness of event-bound admission and refusal, not an independent certificate, a production rollout, a real TypeSafe model result, or proof that the ordinary Bash result was redacted before the primary model. The fake model log records metadata, not full outbound request bodies, so provider-visible secret absence/presence is **UNKNOWN**; U06 owns that separate exact-byte boundary. The synthetic `review_scored` decision labels its request model `jev-1.13.0` even though a fake transport supplied the values; never cite that field alone as a live-model receipt. P15 remains HOLD pending non-author replay of this source/receipt, configured route and profile inventory, recipient/data-class approval, and an owner-safe loaded-session window before enabling automatic Jev calls.
- **Independent challenge (CyanPeak, Mail 43708):** the recorded `fe853347…` digest matches committed `work/omp-jev-review/src/index.ts` at readback, but it is **not** an invocation-time digest of the core imported by the scratch extension. At audit, the scratch-imported core had digest `9965f31b52142061afb94d2415102e2eea0323caea60da12812e87124c61b0bf` and mtime 21:45:56Z, later than the 21:35:58Z persisted session and 21:36:06Z Git trace; no run-time digest was logged. The route observations above remain what the fake session recorded, but neither the committed `fe853347…` core nor the later `9965f31b…` core is independently bound to that execution. A fresh replay must record the imported core/wrapper hashes **at invocation** before assigning a source-bound L3 rung. This does not change the TypeSafe-vs-primary-model boundary.

## jev-p15-contain-automatic-egress-810p session-bound OMP synthetic route [offline / partial]

- 2026-09-30. Root HEAD: 2ae763c6f954969f0e5c8a5572de1a7a0e50730a. Worktree SHA-256: work/omp-jev-review/src/index.ts 9965f31b52142061afb94d2415102e2eea0323caea60da12812e87124c61b0bf; work/omp-jev-review/test/review.test.mjs aead7d7f9961a8c5ec4e3104857b3057ab47de912558cc54e7cb8c1dab0551c2. Scratch test extension and fake provider are separate artifacts: project-positive/.omp/extensions/jev-review.ts f7ae7cfe7a08cd0359111c59aad26a29a8cc32bed648473786ed5ee3f0ad5715; fake-omp-provider.mjs 08a65d00896e04f641b39f65fceb41ef1f31613bbd9b30276dcac2df21527ea9; p15-sessionid models.yml b4d4d34af9f77153363cec1de77c44a047b9ad685d9be2198fdb9f895b35726a.
- Keyless offline command: env -i PATH=/usr/bin:/bin HOME=/var/empty TMPDIR=/var/tmp JEV_SCORE_REGISTER=<scratch>/recorders2/p15-session-id-final.jsonl /opt/homebrew/bin/node --test work/omp-jev-review/test/review.test.mjs. Result: 29/29 pass, 0 fail, 0 skipped.
- Fresh scratch-only OMP RPC session: sessionId 01a0f45b-aa68-751d-888c-8a1631c663fd, profile p15-sessionid, model p15fake/p15-probe, loopback provider 127.0.0.1:18765, loaded project-positive/.omp/extensions/jev-review.ts (test-only synthetic authorizer/fetch interceptor) with the current work/omp-jev-review core. Three recorded events: callp151 eligible (decision entry dfe0601c review_scored); callp152 ordinary (c5b87ae9 permission-denied); callp153 secret-shaped (cf37a6d5 permission-denied). Every decision/diagnostic row now carries the actual sessionId; OMP tool-result message IDs c7f7f32f, 931fc978, f3031849. Fake Jev recorder: 1 approved attempt, 701 request bytes; 0 attempts for either denied event. Fake OMP model: 15 loopback requests. Git trace: 4 starts (one extension diff read for the approved event, three original Bash commands), 0 nested child_start events. No TypeSafe request, real credential read, or Infisical child; the fake key provider was in-process and its invocation count was not separately instrumented.
- **Correction to the preceding P15 entry:** the raw diffs were present in the ordinary OMP tool-result messages; that is not evidence they reached the Jev provider. The fake Jev recorder saw only the one approved event and no denied-event bytes. Do not treat the original tool-result as TypeSafe egress. The exact earlier phrase “denied-row output escaped” conflated the OMP model-visible result with the provider request boundary. Whether P15 separately requires suppressing ordinary tool results from the main OMP model remains an owner-review question; this receipt makes no claim on that interpretation.
- **Boundary / status:** this proves only the Jev-review core's session-ID propagation and one synthetic approved/ordinary/secret-shaped route in a scratch OMP process using a test extension; it does not prove the production extension has an approved policy, TypeSafe egress safety for other registered paths, detached-worker/pre-compaction coverage, U06/U07 recipient/output clearance, or fleet-wide containment. No real key or paid API call. P15 remains BLOCKED and open; no Bead close. The full P15 inventory/reconciliation and non-author review are still required.
- Static checks after the code change: LSP reported two Object.hasOwn target-lib diagnostics at work/omp-jev-review/src/index.ts:116 (no package tsconfig; actual OMP Bun runtime smoke and Node test suite passed); UBS exited 1 on 22 secret-comparison heuristics and 6 warnings in the test file, mostly synthetic TYPESAFe_API_KEY setup/restore and expected test assertions. These are not adjudicated as false positives yet; no UBS pass is claimed. foundation/gates.sh --selftest timed out at 300s after PASS through stage70; later stages are NOT_RUN/TIMEOUT_UNMEASURED pending CyanPeak's isolated result.

## jev-p9-stranger-quickstart-2srw dated replay and claim-floor repair (2026-09-30 UTC) [offline keyless / owner; P9 OPEN]

- **Dated public-source replay:** `var/agent-tmp/p9-owner-cwd-repair-20260930/dynamic-date-receipt.md` records a keyless run against checkout `b3e1cd89a5ba1e09ec318471cb325481590231f4`: 14 README command rows, 12 exit 0, two explicit no-key nonzero rows, zero templates; receipt header says 2026-09-30 rather than the formerly hard-coded 2026-09-25. The new runner selftest plants a stale date and checks the emitted header reflects the execution date. This is a local replay, not proof that the later local changes are on the public default branch. No provider call or paid comparator.
- **Stage-15 source correction:** source-backed additions to `foundation/kit/claims.tsv` made the prior `119/120` coverage floor insufficient. The observed gate was RED at `116/118` covered/candidates against a `119/120` floor. The floor was raised to `123/124` in `foundation/kit/claim-coverage.floor` without changing the checker or un-tokenizer; targeted `bash foundation/gates.d/15-kit-claim.sh` then reported 432 passed, 0 failed, 3 skipped and `123/124` coverage. Its `--selftest` exercised planted negative arms and passed. This is a stronger current targeted gate, not a current aggregate `foundation/gates.sh` GREEN.
- **Checks and boundary:** `python3 scripts/stranger-run-jev-playground.py --selftest --expect docs/demos/upstream-repro/stranger-run-expected.tsv`, `uvx ruff check scripts/stranger-run-jev-playground.py`, `uvx ruff format --check scripts/stranger-run-jev-playground.py`, `python3 scripts/render-results.py --check`, `python3 -m unittest scripts.test_render_results`, and `ubs scripts/stranger-run-jev-playground.py` passed in the owner run. Independent same-revision public-cell readback and confirmation that the corrected local revision is present on public GitHub remain outstanding. P9 stays OPEN; no model-quality, kit-in-omp L3/L4, consumer-benefit, or aggregate-gate claim.

## jev-p9 source-backed public-claim correction (2026-10-01 00:39 UTC) [offline keyless / owner; P9 OPEN]

- **Local source:** worktree based on `a1ff8f58826ee9b003cc334f3b144d309a6a6015` at readback, with uncommitted README.md, docs/LEDGER.md and foundation/kit/claims.tsv edits. Mail 43762 identified present-tense overclaims: the dated 121/122 stage-15 count was described as current, four configured judge aliases were called active profile calls, and a model-reported mask was described as provider-visible safety. README now separates the dated 121/122 and later 123/124 targeted receipts. LEDGER now identifies configured roles, the dated 416-call census, terminal model readback, and **UNKNOWN** exact provider-visible bytes; it does not infer the absence of real secrets from a synthetic-key probe. Ten existing enforced claim rows were updated to source-backed, narrower statements without reducing the `123/124` floor, deleting rows, or changing the checker.
- **Observed keyless checks:** the first `bash foundation/gates.d/15-kit-claim.sh` run was RED on those ten stale registry strings. After correction, `bash foundation/gates.d/15-kit-claim.sh && bash foundation/gates.d/15-kit-claim.sh --selftest` exited 0: 432 passed, 0 failed, 3 skipped; claim coverage 123/124 at the unchanged floor, with planted unmatched-claim and removed-registered-claim refusals. `python3 scripts/render-results.py --check` printed `README results table is current`; `git diff --check -- README.md docs/LEDGER.md foundation/kit/claims.tsv` exited 0; `env -u TYPESAFE_API_KEY -u JEV_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u XAI_API_KEY -u OPENROUTER_API_KEY python3 scripts/stranger-run-jev-playground.py --selftest --expect docs/demos/upstream-repro/stranger-run-expected.tsv` exited 0 with planted wrong-Git-root, wrong-origin/SHA, inflated metric and stale-date refusals. No provider call or paid comparator; spend $0.
- **Public boundary / next trigger:** `git -c http.userAgent='OpenAI File Downloader, XaiImageApiFetch/1.0' ls-remote origin refs/heads/main` at 00:37 UTC still reported `b3e1cd89a5ba1e09ec318471cb325481590231f4`, not the corrected local revision. The prior 14-row public replay in this ledger proves only that older checkout. Public publication is an irreversible action not authorized here; the owner's scoped release and a non-author same-public-HEAD all-cell positive/refusal readback are still required. P9 remains OPEN. This pass does not claim aggregate-gate GREEN, live-model performance, provider egress safety, or consumer benefit.
## jev-p15-contain-automatic-egress-810p source-bound synthetic OMP route [PROBED / P15 HOLD]

- **Run / source:** 2026-10-01T00:24:34Z; root HEAD `a927c345611fc6347a1b7d28800ac1d9afa099b1`; OMP `18.4.5`, profile `p15-sessionid`, scratch project `project-positive`. Invocation SHA-256: `work/omp-jev-review/src/index.ts=9965f31b52142061afb94d2415102e2eea0323caea60da12812e87124c61b0bf`; the imported scratch copy matched; wrapper `f7ae7cfe7a08cd0359111c59aad26a29a8cc32bed648473786ed5ee3f0ad5715`. Post-run hashes remained identical. Scratch manifest: `var/agent-tmp/p15-omp-route-20260930T180331Z.51372/recorders2/p15-sessionid-sourcebound-replay2-manifest.json`; actual OMP session `01a0f4d9-476e-7631-912f-0b16f050135f`.

- **Command / lane:** loopback fake OMP model `p15-probe`; OMP RPC argv `/Users/josh/.bun/bin/omp --mode=rpc --no-ui --approval-mode=yolo --profile=p15-sessionid --model=p15fake/p15-probe --max-time=120`, driven with newline `negotiate_protocol`, `get_state`, and `prompt` frames, then condition-waited to `prompt_result`/`session_settled`. `yolo` was limited to this scratch project; the fake model emitted three read-only `git diff` commands. The TypeSafe URL was intercepted in-process by a synthetic fetch; no real provider or credential call.

- **Observed:** prompt completed and session settled. Three OMP `bash` tool calls: approved `callp151` produced one `review_scored` decision and one advisory on its matching `tool_result`; denied `callp152` and `callp153` produced two `review_not_applicable / permission-denied` decisions. All decision rows carried the actual session ID. Fake Jev transport: one local attempt for the approved event (701-byte length recorded, body not captured), zero for denied events. Score register: two primitive-question rows. Local fake OMP model: 15 requests. Trace2: four Git starts—two for `eligible.ts` (extension diff-loader plus original Bash), one each for ordinary and secret-shaped original Bash; no extra extension diff-loader on denied events.

- **Offline checks:** `env -u TYPESAFE_API_KEY -u JEV_API_KEY node --test work/omp-jev-review/test/review.test.mjs` passed 29/29 with injected fake transport; not a live Jev call. `ubs work/omp-jev-review/src/index.ts work/omp-jev-review/test/review.test.mjs` exited 1 with 22 critical / 6 warnings; no suppressions. A non-secret status-reason/environment-presence false positive was reported to `xd://report_issue`; the scan is not green. `ripwire work/omp-jev-review --quality-delta --legend=compact` reported two minor regressions in existing `ompJevReview` (complexity 41→44; LOC 127→133; zero new symbols; zero gating regressions).

- **Boundary / NO-CLAIM:** one synthetic OMP review-extension route only. The fake request body was not captured, so this does not prove secret-byte absence. Denied ordinary Bash calls still execute under the primary OMP model by design. No full automatic-route/profile inventory, stale-session/canary coverage, U06 primary-model output proof, live Jev/Infisical request, cost/latency, or P15-wide containment. This is not P15 L3 or closure; keep P15 on HOLD pending independent review and remaining route evidence.
## P9 source-backed public-claim correction and stage-15 ratchet finding (2026-10-01)

- **Source / scope:** local HEAD `6d1b596f074ad2d9bc7e885515031357a5d690e7`; corrected the `docs/LEDGER.md` quickstart boundary using the 2026-09-30 public-branch observation and its existing P9 receipt, registered that dated local stage-15 result in `foundation/kit/claims.tsv`, and aligned the documented coverage floor with `foundation/kit/claim-coverage.floor` (`123/124`). No README, gate implementation, or public source was changed.
- **Offline checks:** `bash foundation/gates.d/15-kit-claim.sh` → 433 passed, 0 failed, 3 skipped; claim coverage 124/124 against floor 123/124. `bash foundation/gates.d/15-kit-claim.sh --selftest` → FAIL: its planted unregistered-claim arm expected RED but observed 124/125, above the 123/124 floor. `python3 scripts/render-results.py --check` passed; `git diff --check -- docs/LEDGER.md foundation/kit/claims.tsv` passed.
- **Boundary / NO-CLAIM:** targeted stage 15 only; this does not prove the aggregate gate GREEN, public revision parity, provider behavior, or product benefit. The selftest failure is preserved, not waived. Gate-source modification was not authorized by the session guard; no provider calls, publish, or push.
## jev-wiya key-provider fallback source-bound keyless suite [offline-verified / full acceptance OPEN]

- **Source / command:** root HEAD `6d1b596f074ad2d9bc7e885515031357a5d690e7`; `work/jev-client/src/infisical-key.ts` SHA-256 `cbd344a779c359ed8693ac2b86eed5d61113454a6f0a83d13a5803a6251fd40c`; `src/use-infisical-key.ts` `79734f94b62d448faedc42193427800b9994a501e0919885c63eaebd274bfb66`; `test/key-provider.test.mjs` `418f5db712e348e3677e95bf19c79911c8842559ceeb653407517fb9842cab55`; `kit/src/client.ts` `9a805b56831fbaf03acdc0622619485da925f5450da140529be4bb10b291f667`. Hashes matched before/after. Command: `node --test work/jev-client/test/key-provider.test.mjs` → 17/17 pass, 0 fail, 0 skipped. Tests use injected runners/fake fetch; no external provider request.

- **Observed keyless behavior:** user-session success, in-memory cache/concurrency/TTL, both-fail refusal, invalid/junk-output refusal, approved synthetic HTTPS first hop, denied non-HTTPS/wrong-origin before credential POST, redirect refusal, and final child-env allowlist are covered by the 17 tests. No real credential or token value was read or printed.

- **Consumer boundary:** current root `.omp/tools/jev-*.ts` call `useInfisicalKey()` without a `MachineApproval` argument; `useInfisicalKey()` installs the no-approval default provider, so machine fallback stays fail-closed on these callsites. `kit/templates/jev-kit` contains a separate provider copy and is not proven loaded in the current fleet. No approved real HTTPS origin has been supplied or exercised. Current Bead comments/DB keep Jev-Wiya OPEN behind P5 for its original fresh-OMP scored-row acceptance; the attempted in-progress transition was refused, and no status/edge was forced.

- **Boundary / NO-CLAIM:** offline-verified helper behavior only. No fresh OMP scored Jev row, real machine identity, real Infisical/TypeSafe call, P5 gate shadow, independent live acceptance, or production-wide consumer wiring is established. The keyless suite does not close Jev-Wiya; keep it OPEN/HOLD until the owner-approved recipient/U07 checks, P15/U06/P5 gates, and non-author verification are satisfied.

## 2026-10-01 native Jev turned on fleet-wide; local System One vs TypeSafe on real traffic [live]

- **Turned on (operator config, not in git):** `~/.omp/agent/models.yml` gains the command-resolved TypeSafe key (same Infisical command as the claude/codex profiles) and an inert `ollama-sys1` provider (`api: typesafe`, `http://127.0.0.1:11434`). `~/.omp/agent/config.yml`: `modelRoles.judge: typesafe/jev-latest`, `retry.fallbackChains.judge: []`, `defaultThinkingLevel: auto`, `features.unexpectedStopDetection: smart`. Profiles claude/codex/muse/grok: `features.unexpectedStopDetection: smart` (`omp --profile <p> config get` → smart). Beads `jev-zmar`, `jev-j4ci`.
- **Live omp RPC, default profile, `typesafe/jev-latest`:** smart stop positive (`I'll run the full test suite now…`) → `unexpected-stop` row + retry continuation; negative (finished report with exit status) → one row, no continuation. Judged TTSR rule `.omp/rules/claim-without-evidence.md` (commit `60b7a338`): unsupported "Done — everything works and it is verified." → `ttsr` row + injection, agent corrected to UNVERIFIED; claim quoting command output and commit → `ttsr` row, no injection. Fresh default-profile `get_state` lists `find` (12 built-ins); `--profile omp-test` (no judge) does not (11).
- **Local System One wiring:** a `--config` overlay with `modelRoles.judge: ollama-sys1/nimble:latest` routes omp's `auto-thinking` and `unexpected-stop` judgments to Ollama 0.35 (`model_usage` provider `ollama-sys1`), so the switch is a one-line role change.
- **Same question, real traffic, TypeSafe `jev-1.13.0` vs local (rows `var/agent-tmp/{smartstop,autothink}-replay-rows.jsonl`, scratch):** smart stop, 300 text-only stops from 160 random sessions: TypeSafe flagged 8, nimble 110, agreement 0.653, kappa 0.073, no nimble cut above kappa 0.12; p50/p90 TypeSafe 366/541 ms, nimble 387/888 ms. Auto-thinking level, 200 real prompts (omp's preprocessing replicated): nimble exact 0.66, within one level 0.77, linear weighted kappa 0.46, `xhigh` 12 vs TypeSafe 41; tev1 exact 0.54; p50 TypeSafe 351 ms, nimble 562 ms, tev1 374 ms. **Decision:** both native features stay on TypeSafe.
- **Spend:** TypeSafe 231,812 + 134,003 replay input tokens ($0.0097 + $0.0056) plus RPC tests (~$0.0003); local $0. Ollama 0.35.0 on a 512 GB Mac; cold nimble load ~17 s, warm ~70-80 ms on short states.
- **Boundary / NO-CLAIM:** agreement with the incumbent, not accuracy against labels (no labels exist for these native questions); RPC chat-model behavior is stochastic; organic usefulness of smart-stop continuations and judged-rule flags is not yet measured (scoreboard `jev-4970`); labelled local-vs-Jev parity on our own hook surfaces is `jev-uhc5`.

## jev-asbl fresh-OMP injection shadow on local read results [live L3, N=2]

- **Source and feasibility:** replay row `work/jev-29s4/live-rows.jsonl:1` identifies `inj-0258` / `planted-0-start`. The two live files were byte-checked against `work/nev-injection/pairs.jsonl` (`inj-0258` and `inj-0000`): text SHA-256 `490fef14446c20b2ea8d1b52a2296440f6b9be1039f78ab6aef44bbec5a4f332` and `79950ad562dfda8aa755805d64985cd0996daa3faf03e9aa675a6bf1832657e8`. Requests fit the hook's 30,000-byte state ceiling (1,344 and 874 estimated bytes).
- **Wire / action:** `.omp/hooks/post/jev-injection-shadow.ts` loads `read` results only when explicitly opted in with `JEV_INJECTION_SHADOW_SCREEN_LOCAL_READ=1`; default local reads remain excluded. Fresh OMP RPC session `01a0f5cc-9dcf-76ee-86d8-f4da707319ec` used that opt-in, daily cap 2, and read only the two corpus-derived files. The hook wrote hashed score rows to `~/.local/state/jev/asbl-live-shadow-final-20261001T044950Z.jsonl`; it did not change tool results.
- **Source snapshot:** hook SHA-256 `6732d76e9e17f56fe7f4b65a325b5576f42b68f5cf81e49e0154d84276237f0b`; test SHA-256 `8f55acde7fae77fba80e7707b6b1a377ee4b7dee66504c01bdad715e288eac5a`.
- **Live Jev:** pinned `jev-1.13.0`; planted markerless injection scored `0.89` / flagged, clean paired text scored `0.03` / not flagged; latencies 85/205 ms. Two calls used 1,043 input and 40 output tokens; estimated Jev spend `$0.000043806` at `$0.042/M` input tokens, output free. No comparator call. Hook logs contain score, token/latency data, and output hashes, not result bodies.
- **Offline checks:** `node --test .omp/hooks/post/jev-injection-shadow.test.mjs` → 15/15; `ubs .omp/hooks/post/jev-injection-shadow.ts .omp/hooks/post/jev-injection-shadow.test.mjs` → exit 0, 0 critical, 0 warnings; `git diff --check` on the hook and test passed. `ripwire . --quality-delta` exited 2 on 12 preexisting-worse findings in the shared worktree (including existing hook duplication / short-horizon-churn); it also reported the handler's complexity increase 5→10 as minor, below its bar of 15.
- **Boundary / NO-CLAIM:** two controlled reads in one fresh session establish the required positive and clean negative, not a rate or consumer benefit. The agent's response called the planted result a false positive, but the shadow score was not exposed to or acted on by the agent. Local-file screening stays opt-in because it sends the selected file text to Jev; default local reads remain unscored. The two-call cap was exercised in this invocation only; no global cross-session daily-cap, fleet traffic, privacy clearance for arbitrary files, or enforcement claim is made.

## 2026-10-01 key path survives session expiry; stale-lock auto-recovery; claim-rule first organic flags [live]

- **Key path (jev-wiya; 25d54fff, c7a82107).** Uncommitted 2026-09-29 edits had made the hooks' machine-identity fallback require an approved origin while passing none, so an expired user session would have silenced every Jev hook again (the 2026-09-28 outage). `APPROVED_INFISICAL_ORIGIN` is now `https://secrets.zeststream.ai` (other, HTTP or credentialed origins still refused before any credential POST; 20/20 tests; a planted pre-fix default turns the expired-session test red). Live, one process, user session simulated expired: machine login at the approved origin, key length 107, `askJev` ok on `jev-1.13.0`, 323 ms, 285 input tokens. `work/jev-client/bin/typesafe-key.mjs` now resolves the TypeSafe key in all five profiles' `models.yml` (user session first, 4 s cap; then the machine fallback): normal 1.7 s, user session absent 2.7 s, no credentials exit 1. Fresh RPC sessions in default, claude, codex, muse and grok each logged `auto-thinking` and `unexpected-stop` on provider `typesafe` through it.
- **Organic native judge since smart stop went on** (02:10Z to 04:50Z, 80 session files, test directories excluded): 514 `find`, 85 `auto-thinking`, 76 `unexpected-stop`, 16 `ttsr` calls.
- **Claim rule first organic flags (jev-e2vb).** 8 injections since 02:10Z: 5 in test sessions, and the 3 from working panes were false positives by the rule author's labels, one confirmed by `parentId` (the judged output names its commit). A non-author measurement on at least 120 real outputs, bar fixed before the calls, decides keep or demote; the rule stays on in this repository only meanwhile.
- **Stale `.git/index.lock`.** Empty locks with no git process appeared every few minutes under load average 60 to 90. The fleet watcher now renames a lock that is empty, at least 120 s old and held by no git process in the repository into `var/agent-tmp` and pages pane 1 (c76077b9); it fired 3 times on its own between 04:42Z and 04:52Z. Creator not identified: no agent tool call ran git within 45 s of six creation times, a 0.2 s `ps` sampler saw only other repositories' git processes, and `lsof` shows no holder. [INFERENCE] git commits killed during a long pre-commit hook.
- **Incident.** 32d5c1ba, a bare `git commit`, committed stale index blobs that reverted 9abe975b (live injection shadow) and its EVAL entry in history; restored in f5faa0e2 from the 32d5c1ba^ blobs, working trees untouched. AGENTS.md now requires `git commit --only <paths>` (2491f0ea).
- **CI.** The README stranger workflow refused its own checkout because `actions/checkout` records the origin without `.git`; fixed in 8faaa1cb, dispatch run 36813553026 EXPECTATION PASS, 14 rows. `work/jev-oioo/test_resume.py` pinned to the captured pre-resume rows (a4c3a5e0). `row-provenance-check` still flags two parked experiments' rows (missing code hash and UTC timestamp): a real gap, left red.
- **Spend:** about 15 TypeSafe calls (one key-path proof, ten five-profile RPC classifications, four judge probes), under 10k input tokens, under $0.001.
- **Boundary / NO-CLAIM:** no fresh omp session was run with the real Infisical user session logged out (HOME isolation is the closest safe equivalent); the claim-rule labels are the author's; the lock creator is not identified; organic call counts are usage, not benefit.

## 2026-10-01 verified outcomes: skill hint ON, qg1j/bzl7/4970 closed [live]

- **Skill hint ON (jev-x1pq, closed).** `.omp/extensions/jev-skill-hint.ts` listed in `.omp/config.yml` (`258e9d9a`); state capped at 400 chars, p95 255 ms with 10/10 coverage on long prompts (`c4c3c2a4`). Independent re-verification 2026-10-01 ~06:02Z: fresh RPC sessions, SEO-audit prompt -> `jev-skill-hint` message naming `seo-audit` (conf 0.63) + hinted row 06:02:47Z; Hamlet summary -> zero hint messages + silent/choice-none row 06:03:11Z. Note: three silent/timeout rows at 06:00:42-52Z (fail-open, not judged) preceded the cap.
- **qg1j closed.** 24 h report `work/jev-qg1j/latest.json` (`e4b3aa47`): 95.9 h eligible window, 54 rows / 27 answered, flag rate 3/27 (11.1%), top-score p50 0.03, latency p50/p95 147/228 ms, ~$0.001 known input spend (`spend_complete=false`: 17 fail_open rows lack usage). Per the conductor close verdict the 3 flags were all false positives: Jev caught 0/27. Benefit question parked in jev-6psj (deferred).
- **bzl7 closed.** 48 h live report (bead comment 2026-10-01): 51 rows, 12 current-schema scored, Jev agreed with provider rank-1 in 3/12, zero opens on either side (48/51 rows saw no follow-up tool call, so the comparison is undecided, not a loss). Spend ~$0.0005 (11,272 input tokens). Benefit question parked in jev-y0tr (deferred).
- **4970 scoreboard closed (non-author verify by HazySpring).** `surface-census.py --scoreboard --days 7` in 15.5 s (bar 60 s); judge total 17,521; per-day 09-24..09-30 sums to exactly 15,448; Oct-01 partial 2,062->2,075 and growing (conductor's 16,234 = 15,448 + 786 at an earlier cutoff). `test_judge_usage.py` 14/14. Commit `89f1680c`.
- **Smart stop organic:** 76 checks / 0 continuations (conductor count 2026-10-01; cf. the 76 organic unexpected-stop calls in the §2026-10-01 entry above).
- **Boundary / NO-CLAIM:** every count above is usage, not benefit. No verdict is made here that hints get read, screens catch live injections, rerank picks get opened, or judge calls improve outcomes; those belong to jev-6psj, jev-y0tr, jev-4nyy and the claim-rule measurement.

## 2026-10-01 skill hint OFF: H1 loss, cut-0.7 fails, live code misroutes [live]

- **H1 stopword shortlister (`4d0e76c5`, reverted `abbfdce8`, R131 at `27defa97`).** Dev recall 1/8 -> 3/8 reproduced exactly (de-slopify@19, performance-review@13, churn-prediction@6), but rate-limiting dropped out of the shortlist on its stop-heavy description. Non-author live probe: request-hog (50k reqs overnight) drew capacity-planning 0.73. Revert diff empty (verified); demotion stands.
- **Cut 0.7 does not separate (`abbfdce8` baseline, no code change).** Author: 2/8 hints, p95 297 ms, spend 5,089 in-tok. Non-author re-run: 3/8 (jev-mailbox 0.77 misroute on helpdesk-pile, form-validation 0.84 misroute on page-cro, rate-limiting 0.98 on-target), p95 285 ms; answered rows bill identically across runs (2,528 + 2,561 = 5,089). Misroutes fire at 0.77-0.98: no threshold below ~0.99 stops them without killing everything.
- **Live-code check that turned it off (bar: 0 misroutes across 2 runs, fixed before the calls).** 8 r2 prompts x 2 runs through hintSkills + live askJevChoice at HEAD, cut 0.5: run 1 fired 2 (0 on-target), run 2 fired 4 (1 on-target, rate-limiting 0.98); jev-mailbox misroute on helpdesk-pile stable both runs (0.77, 0.80). Bar missed; extension reverted in `1f031068`. Spend 15,344 input tokens (~$0.000645), 16 calls, no auth stops.
- **Boundary / NO-CLAIM:** the loss is about this design (lexical shortlist + 0.5 cut + 300 ms deadline), not about Jev Choice quality; the oracle probe answers decisively at 1.0 whenever the target reaches it. Recall is the binding constraint and lexical recall is exhausted.

## 2026-10-01 jev-wb7j: memory-relevance Noul filter FAILS precision bar [live]

- **Bar (preregistered in bead comment before outcomes):** 100 sampled (prompt, memory) pairs, seed 42, blind labels; one Noul per pair on `jev-1.13.0`, DROP iff noul < 0.5; PASS iff precision_of_drop >= 0.90 AND token_reduction >= 0.40.
- **Census (keyless):** 270 files / 84 sessions; only 8 session_init blocks (328 items) + 6 ee-task-context blocks (19 items) are real injections (76/84 marker hits are docs prose). 347 pairs, sampled 100.
- **Labels (frozen pre-live):** RELEVANT 21 / IRRELEVANT 79; relevant tokens 548/1989 (27.6%).
- **Live:** 100/100 ok, 0 retries, median 119 ms, 79,441 input tokens, spend $0.0033. Cap 110, no 401/402/403. Rows in `work/jev-wb7j/rows.jsonl`.
- **Result:** dropped 91/100 (TP75 FP16); precision_of_drop 0.824 FAIL; token_reduction 0.857 pass. VERDICT: FAIL. Autopsy: 8/16 FPs are borderline-label generics, 6/16 live receipts vs prompts forbidding live material. Follow-up hypotheses in `work/jev-wb7j/REPORT.md`. NO-CLAIM: no hook built, no design bead.
- **Boundary:** per-turn Mnemopi `<memories>` seen live is not persisted to session files; file census undercounts live volume. Absolute on-disk opportunity ~11k tokens/7d.

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
calibration audit. No A/B-vs-LLM runs yet, no adversarial corpora yet — both
framed as next audits in `foundation/CALIBRATION.md`.

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

- `AGENTS.md` (66 KB, 31 §§): authored against the mirror-derived canonical shape.
  `fh agents --repo .` → DISCIPLINE 14 NAMED / 1 UNNAMED / **2 ABSENT**, REPO_SPECIFIC
  2/3/**2**, TOOL_ONBOARDING 7/2/**31**; `nomenclature_state=VALID`; 1145 lines vs corpus
  median 839, `exceeds_corpus_max=false`. Skeleton `content_id=095decf2…`,
  `source_rev=bb59539…` (64 sections, 117/221 mirror dirs). Every remaining ABSENT row is
  argued in `.fh-agents.toml` (Cargo-only, or a section deliberately compressed).
- `scripts/sync-docs.sh` — vendors the primary sources, fail-closed, never destructive
  (fetch-only on existing clones; a SHA move is reported, never performed). Ran clean:
  **111/111 doc pages**, `--check` → `CHECK PASS 114 mirrored files`. Mirrored
  `docs-mirror/typesafe/` (llms.txt 16.7 KB, llms-full.txt 835 KB, sitemap 111 locs),
  `docs-mirror/ripwire/` (CLI-HELP 1546 lines, `ripwire 0.4.0 built_from=e663ca8f8`), and
  pinned `upstream/typesafe-ai/{typesafe-sdk-python@420ef4f, typesafe-sdk-js@66880cc,
  system-one-adapter-python@0bb819b, skills@65a39f3}` + a 10-row org inventory.
- **Finding from the manifest, first run:** the local `~/Developer/ripwire` checkout is
  `6488f6f4`, **1502 commits behind** upstream `f45087a7`, while the installed binary is
  `0.4.0 built_from=e663ca8f8` — three different revisions. Not moved; recorded.
- omp surfaces measured live, not quoted: `omp/18.2.4`, 40 subcommands;
  `negotiate_protocol(v2)` → success and `get_state` → `model.id=claude-opus-5`,
  `contextWindow=1000000` via `omp --mode=rpc --max-time=20`. Pane-profile trap confirmed in
  this very session: `%71` titled `jev__omp-claude_1` runs `omp --profile=codex`.
- Boundary: no Jev API call was made this session (no live lane, no spend). The omp integration
  seams are documented at **L0** — designed and cited, nothing wired. `probes/fast-jev-probe.mts`
  re-run offline (fake Jev, no key): **8/8**, 91% char reduction on its fixture.

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

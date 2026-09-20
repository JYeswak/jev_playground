# Depth rule pack: mining receipt `[test]`

Stage 3–4 of the hardening loop (SUGGEST leg). Method fixed by
`pane3-depth-rule-pack.md` and `suggest-leg-mining-20260920.md`.

## TTSR interrupts received during this unit (dogfood log)

| turn | rule | trigger | assessment |
|---|---|---|---|
| corpus survey | `bash-glob-silenced` | `python3 -c …; echo ---; hub list 2>&1 \| head -20` — no `grep`, no glob, no `2>/dev/null` in the command | suspected FP; command shape shares nothing with the defect except `2>&1` redirection |
| corpus survey | `bash-pipe-exit` | same command — pipe to `head -20` but `$?` never read; the rule's defect (rc read after pipe) is absent | suspected FP (fires on truncator shape alone); follow-up belongs to the DETECT owner, not this unit |

## Preregistered bar (written BEFORE measuring, 2026-09-20)

- A class firing above **~5% is wallpaper** and does not ship.
- A class below **50 occurrences is too rare** to be a rule.
- Rate alone never ships: **hand-label a seeded sample (n≥20), report FP**.
- **State prevalence beside every score.**
- At least one candidate class must be **REFUSED** with its number.

## Corpus (not authored here)

`work/toolcall-judge-v3/real-allowed.json` — bash-only dcg allow-verdict commands,
**n=78,242**, `harvestedAt=2026-09-20T05:22:11.742Z`, quoted 2026-09-20.
Keys per record: `command`, `tool`, `seen`. All `tool=bash`: no session ordering,
no assistant text, no edit/write streams. Classes needing those are unmeasurable
here and must be REFUSED or DEFERRED, not proxied silently.

## Candidates (prove or refuse each)

| # | class | corpus-measurable? |
|---|---|---|
| D1 | `git add -A` / `git add .` (whole-tree stage) | YES — bash literal |
| D2 | `rg`/`grep` for a structural question (pattern has code punctuation) | YES — bash literal, hand-label for regex-vs-path |
| D3 | `*_v2` / `*_improved` / `*_enhanced` file creation | PARTIAL — bash proxy only; rule scope is edit/write streams |
| D4 | read-burst with no prior `ripwire` | NO — no session ordering in corpus → REFUSE |
| D5 | claim verb in text with no preceding command | NO — no assistant text in corpus → REFUSE |
| D6 | skill-routing (task names a domain, skill never read) | NO — needs skill-read data; P2 owns ranking → DEFER, coordinate |


## Results (2026-09-20)

Corpus: n=78,242, harvestedAt 2026-09-20T05:22:11.742Z. `fh` ledger age recorded as
freshness metadata only (pane-1 correction 408376e): doctrine does not rot in 12 days;
fh unused this pass by choice, not by discount. morph verified at `jev/.omp/mcp.json`
(stdio `franken-harvest/bin/morph-mcp.sh`); this session predates the mount, worked
without morph, rules route to it per the derived split (morph broad questions, rg known
identifiers, ast-grep/sg structure, ripwire cold rank). Live Jev available via infisical
as of this session; this unit spends **0 live calls** — TTSR regex predicates prove fully
offline, so live would be waste, not rigor. Live lane: NOT_RUN, nothing offline-insufficient.

| # | class | predicate | hits | rate | labels | verdict |
|---|---|---:|---:|---|---|
| A | structural SHAPE search | recursive grep/rg, quoted pattern has code keyword AND regex hole | 172 | 0.22% | STRICT 16/20 TP, FP 0.20 (seed 20260922, own sample) | **SHIP** `bash-structural-def-search.md`, never/once |
| B | call-site exclusion | `grep … \| grep -v …fn…` (def excluded from results) | 64 | 0.08% | 14/20 TP, FP 0.30 (seed 20260920, own sample) | **SHIP** `bash-callsite-grep-exclusion.md`, never/once |
| D1 | `git add -A` / `git add .` | whole-tree stage | 11 | 0.014% | — | **REFUSE** too rare (<50). Converges with P4 (n=1). dcg already denies. |
| D3 | `*_v2`/`*_improved`/`*_enhanced` | filename token in bash | 49 | 0.063% | — | **REFUSE** too rare (<50, by one — bar not moved). P4 n=10 agrees. |
| C | count-as-verdict | `grep -c` last-printed | 3420 | 4.37% | 2/16 TP, FP ≈0.88 | **REFUSE** — predicate cannot see the defect. Prior "ship, unlabelled" OVERTURNED. |
| S | new `scripts/*.sh` | create-redirect to `*.sh` | 2324 | 2.97% | defect is intent-unobservable | **REFUSE**. P4 scripts/-scoped n=4 agrees rare at house path. |
| D4 | read-burst, no ripwire | — | — | — | — | **REFUSE** unmeasurable: bash-only corpus, no session ordering. No rate manufactured. |
| D5 | claim verb, no command | — | — | — | — | **REFUSE** unmeasurable: no assistant text in corpus. |
| D6 | skill-routing on sr | — | — | — | — | **CLOSED with cause** (P2 984b501): sr exits 5 on >10k-file or symlinked stores. Fallback: Quill BM25 + mined doctrine. |

## The Grok reconciliation (challenge 408376e)

P4: token-anywhere predicate, 965 hits (1.23%), lenient 24/24, STRICT 5/24 (FP 0.79). My first
predicate (304 hits) labelled FP 0.25 LOOSE — re-examined under STRICT falls to ~50-65%.
Direction agrees: the token predicate cannot split known-name navigation from shape questions.
Resolution: SHAPE predicate (regex hole inside the search pattern). Exact names stay quiet by
construction — proven in-engine (`fn resolve_standing_manifest` quiet, `fn .*pressure` fires).
Fresh 20-label under STRICT: 16/4, FP 0.20; preregistered ship-bar (strict-FP ≤0.35) met.
Criterion stated IN the rule file. Checkable: `/tmp/shape.py` (seed 20260922) + selftest arms.

## Acceptance

- positive: both rules fire on known-bad via `omp ttsr test`, prevalence + seeded FP stated
- planted negative: 5 quiet arms; REFUSALS with numbers: D1, D3, C, S, D4, D5; D6 closed with cause
- `./scripts/selftest-ttsr-rules.sh`: 13 ok, 0 failed (n_rules==4)
- portability: both rules repo-free; installer out of scope, ruling recorded (portable)
- astCondition still unused by us; the structural edit-stream leg stays open, stated not implied
- commit on create; level `[test]` (offline + selftest; new rules not yet proven firing live)

## NO-CLAIM

One corpus, one machine, one labeller per sample (P4 second-labeller on the adjacent predicate
only). TTSR injects, not enforces — both rules are `never`-mode guidance; every FP costs a folded
reminder, never a blocked stream. `never`-folding into real tool results NOT proven live for these
two rules (only `omp ttsr test`).

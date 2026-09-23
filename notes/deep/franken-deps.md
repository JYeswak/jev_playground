# W4.1 dependency and citation audit + W4.2 rider facts (TopazRaven, wave 1, Part A)

Bead: `jev-deep-kit-8q7.2`. HEAD run at: `33fe6ae26f6ffbc4266c22ba7b3e35e8dfbe82ce`
(2026-09-22 20:22:40 -0600; dispatch HEAD was `572e3eb`, 19 commits earlier —
all 19 are wave-1 sibling notes and packet files, no gate or `.omp/` change;
`git log --oneline 572e3eb..HEAD` re-runnable).
Archives (read-only, never copied into the tree): omp-kit at
`/tmp/jev-intake/omp-kit-zip/omp-kit/`; franken pack at
`/tmp/jev-intake/franken-zip/` (44 `packets/*-assessment.md`, synthesis,
RULEBOOK.md, starter-kit).

## Preregistered (expectations written before the packet greps ran)

1. `frankensearch` returns hits including `AGENTS.md:642` (feasibility arm).
2. At least one of the 44 repos returns zero jev hits (planted negative).
3. `franken_engine` core CI is red at the pin (plan §1 says so; W4.1 re-checks).
4. At least one file jev cites as a franken origin is absent from that
   repo's packet (mechanism-existence-ahead-of-execution is the synthesis
   finding 2, so a miss is expected, not surprising).

All four held. Verdicts below are re-runnable by the quoted command.

## W4.1 method and denominators

- Citations: `git ls-files | xargs rg -n -i 'franken|asupersync'` → **2316
  lines** (`/tmp/ompfit/cites.txt` is scratch, not evidence). Excluded per
  packet: **5 files** matching `work/nev-*/*.jsonl` (session-log corpora —
  data, not citations). All other data-corpus hits (duel-2 run JSON,
  rung4 fixtures, calibration jsonls, rerank pairs, `corpus.jsonl`) are
  grouped in TSV rows `DATA-CORPORA` with the stated reason, not dropped
  silently. Search covered both spellings only where JSON keys were
  involved; repo names are single-spelling literals.
- Every grouped row names its `file:line`; counts per file are in §W4.1
  census below. `TSV: notes/deep/franken-deps.tsv` (13 cols, 39 data rows,
  awk-validated uniform).
- Claim-status vocabulary is the packets': demonstrated / partially /
  disproven / stale / not-assessed (the last is mine: the cited file has
  zero hits in that repo's packet). TRL/NODUS/CI/Rel are the synthesis
  master table (`synthesis/00-overview.md:60-110`), not my judgment.

## W4.1 census (files with hits, grouped)

- Doctrine adopted: `AGENTS.md:642` (frankensearch), `AGENTS.md:1576`
  (asupersync, franken_ocr, franken_engine, frankensearch).
- Gates executed: `foundation/gates.d/85-promotion-contract.sh:17`
  (+`GATES.md:96`), `foundation/kit/demotion-rules.md` (9 hits:
  frankenfs ×3, frankenredis, frankensim, frankensympy, frankentui,
  frankengit), `.omp/extensions/kit-guard/policy.ts:4` (synthesis Gate 18),
  `foundation/gates.d/15-kit-claim.sh:3`,
  `foundation/kit/check-{claim-discipline,readiness}.sh:2` (pack ports).
- Code reimplemented: `compaction/hindsight.ts:152,247`,
  `work/oracle-kit/index.mjs:87` (asupersync e-process),
  `scripts/promotion-four-gates.py:4`,
  `githooks/commit-msg-verification-level.sh:4-6` (franken_lean,
  frankensqlite tag vocabulary).
- Wired tools: `.omp/mcp.json:6` (franken-harvest `morph-mcp.sh`); `fh`
  over the mirror (AGENTS.md research surfaces; `franken-harvest` is
  outside the 44, so packet columns read `none`).
- Cited, never executed: `docs/demos/ORACLE-PROGRAM.md` (8 shapes),
  `EVAL.md:526,750,941,963,970,799`, `NEGATIVE_EVIDENCE.md:1196,1333,
  2561,2583,2688,2744`, `docs/demos/upstream-repro/*` essays,
  `docs/essays/*`, `.beads/issues.jsonl` (8 hits, bookkeeping),
  `notes/deep/dispatch/p*-wave1.md` + `docs/PLAN-DEEP-KIT-20260922.md`
  (21 hits, bookkeeping).

## W4.1 headline: the stage-85 example, quoted both ways

jev does **not** cite the shape as proven. Stage 85's header
(`foundation/gates.d/85-promotion-contract.sh:17-40`): "SHAPE ADOPTED, NOT
LINKED", "this is a presence check, not a proof check. It said 'four proven
gates' until 2026-09-20, which overstated what the code does." The
MEASURED BOUNDARY in the same file shows a JUNK row promotes GREEN.

The packet side (`franken_engine-assessment.md:21`): "The core CI lane is
red at the pin … all 46 recorded runs … fail — it has never gone green
[CI-observed, High]; `quality-gates.yml` and `perf_regression_gate.yml`
have **zero runs ever**." Promotion controller existence is code-verified
(ibid:119); execution of the gates is not. Re-tier (not drop): the shape
is real, the proof is not, and jev's header already says exactly that.

## W4.1 headline: origins the packets never assess

`not-assessed` rows (cited file, zero packet hits): frankenfs
readiness-autopilot/tracker-hygiene/MODULARITY_RUNBOOK (D1–D3),
frankenredis GATE_VALIDITY.md (D3), frankensim MATURITY_LEVELS.md (D4),
franken_tts metamorphic_invariants.rs:315-505, frankenlibc
memcpy_strict_conformance_test.rs, frankenpandas TESTING_CONVENTION,
frankensearch RULE 0.5. The demotion rules that lean on them are all
procedural except D7's proof-exists slice, so nothing enforced rests on an
unverified origin — but the citations claim a provenance the assessment
pack does not confirm. Action `monitor` throughout.

## Transplant binary counts: BLOCKED (scope)

Packet step 2 asks for franken-derived binary invocation counts from
transcripts "under the jev panes' profile session dirs". Those dirs are
`~/.omp/profiles/*/agent/sessions/` (verified present for `grok` and
`muse`), which the dispatch scope forbids: "Do not read … under
`~/.omp/agent/` or `~/.omp/profiles/*/agent/`", allowing only read-only
reads of profile *config*. Scope is Joshua's order and wins over the
packet step. Measurable proxy delivered instead: wired-tool rows
(`mcp-tool`, `cli-tool`) name what the tree wires (`morph-mcp.sh`, `fh`
over the mirror); no franken-repo binary is executed by any tracked jev
file — `br`/`bv`/`fh`/`ripwire` origins are beads_rust, franken-harvest,
and ripwire, all outside the 44. A pane with transcript access can lift
this block; until then invocation counts are unmeasured, not zero.

## Planted negative and feasibility arm

- `franken_remote`: `git ls-files | xargs rg -i franken_remote` → 0 files
  (packet: TRL 3–4, Explore, C3, R1, rider yes). Method returns zero.
- `frankensearch`: 81 cite lines including `AGENTS.md:642`. Arm passes.

## W4.2 rider exposure — facts only, no legal conclusion

Rider verbatim, two packets that read the LICENSE text:

1. `frankenlibc-assessment.md:215`: header "MIT License (with
   OpenAI/Anthropic Rider)". Restricted parties: "OpenAI, L.L.C.
   ('OpenAI'), Anthropic, PBC ('Anthropic'), their affiliates, and any
   person or entity acting directly or indirectly for the benefit of, or
   under the direction of, any of the foregoing." Restricted "Use"
   includes "copying, modifying, merging, publishing, distributing,
   sublicensing, selling, transferring, making available, hosting,
   deploying, executing, **benchmarking, testing, analyzing, indexing**,
   or incorporating the Software or any Derivative Works into any dataset,
   training corpus, evaluation harness, or pipeline for machine learning
   or other automated systems" (emphasis in packet).
2. `franken_engine-assessment.md:177-190`: same header, but the README
   badge says "License: MIT". Restricted parties add "on behalf of" and
   enumerate "(including any officer, director, employee, contractor,
   agent, consultant, service provider, or representative)". Adds a viral
   clause ("any distribution … must include this rider provision
   unmodified"), grant voidness ("no rights are granted to any Restricted
   Party"), and remedy (automatic termination, injunctive/equitable
   relief, attorneys' fees). Classification per packet: non-OSI,
   source-available [Inference, High].

Wording differences: engine enumerates representatives and adds
viral-clause plus remedy detail; LIBC's Use list names benchmarking,
testing, analyzing, indexing explicitly. Corpus count: rider on 38/44,
plain MIT on 1 (`franken_agent_detection`), no operative grant on 5
(`synthesis/00-overview.md`, Verified High).

Pane → model → lab (verified this turn unless noted):
- pane 1 → `anthropic/claude-opus-5-5` → Anthropic (plan Appendix A;
  cited, not re-verified this turn — no in-scope probe reaches pane 1's
  status line).
- pane 2 → `xai-oauth/grok-4.7` → xAI (verified:
  `~/.omp/profiles/grok/agent/config.yml:7`, `default:` role).
- panes 5–6 → `openrouter/meta/muse-spark-1.3-contributor` → Meta via
  OpenAI-compatible endpoint (verified: `~/.omp/profiles/muse/agent/
  config.yml:13-15`, slow/plan/commit roles; no `default:` key — session
  default applies).
- panes 3–4 → same Spark model, switched in-session on the default
  profile (plan Appendix A; cited, not re-verified).

jev activities touching rider-covered repos: (a) reading the assessment
packets (third-party assessments, not the repos); (b) `fh` indexing the
Dicklesworthstone mirror, which contains franken repos; (c) copying
shapes into jev files (demotion-rules origins, stage-85 vocabulary,
e-process reimplementation, hook tag vocabulary); (d) loading harness
skills that guide work on rider-covered repos
(`skill://asupersync-mega-skill` et al. — guidance, not the repos);
(e) running `br`/`bv`/`fh`/`ripwire` binaries (beads_rust,
franken-harvest, ripwire origins — all outside the 44 and unassessed).

Question for Joshua in one sentence: Which jev activities touching
rider-covered repos — `fh`-indexing the mirror, copying shapes into jev
files, or running pane models from the named labs — should change, if any?

## NO-CLAIM

Transcript invocation counts were not measured (scope block, above); a
citation audited against a packet is not an execution proof; rider facts
are quotes, not a legal conclusion.

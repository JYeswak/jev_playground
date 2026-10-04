# jev CLI ergonomics spec: product families in one `jev`

Author: ErgonomicsSpec · 2026-10-03 · repo HEAD `4597f3a8` · read-only audit (no repo writes, no live Jev/Clef calls)
Skill: `~/.agents/skills/agent-ergonomics-and-intuitiveness-maximization-for-cli-tools` (abbrev. `AE/`). Rubric `AE/references/rubric/SCORING-RUBRIC.md` v1.0.0 (`:2`), abbrev. `RUB`.
Transcripts: `nice -n 10 node kit/bin/jev.mjs …` from `kit/`, `TYPESAFE_API_KEY` unset, captured in this session.

Coordinated with peers. **DoctorSpec** owns `jev doctor` internals. **InstallerSpec** owns `jev install`. Both adopted the envelope field names and the shared exit codes in §2.4. Two class-scoped codes are still open for Main (§2.4, D-1).

---

## 0. Findings that override everything else (P0, Axiom 0, `AE/SKILL.md:71-72`)

| # | Finding | Evidence |
|---|---|---|
| P0-1 | **Two binaries are both called `jev`.** `command -v jev` returns `~/.local/bin/jev`, a symlink to `hermes-jev-skills/bin/jev` (Python, `jev --version` prints `0.19.0`). It is not `kit/bin/jev.mjs`. `jev classify …` on PATH exits 2 with argparse "invalid choice: 'classify'". The hermes verbs overlap kit verbs or proposed names: `doctor`, `rerank`, `ask`, `triage`, `route`, `search`, `plan`. | transcript `jev --help` / `jev classify …`; `ls -la ~/.local/bin/jev` |
| P0-2 | **`jev --help`, `-h`, `help`, `--version` and bare `jev` all exit 1.** Each prints the one line `jev doctor\|gate\|ask\|rerank\|classify\|verify\|score ...` to stderr. No help exists anywhere. | `kit/bin/jev.mjs:226-230`; transcripts |
| P0-3 | **Unknown flags are silently ignored.** `classify … --jsno` and `verify … --robto` exit 0. `--robto` silently falls back to human output. | `kit/bin/jev.mjs:15-22` (`args.includes`/`indexOf` only); transcripts |
| P0-4 | **No-key exit code contradicts the docs.** `classify`/`verify`/`rerank`/`score` without a key exit **1** with `reason:"exception"`. `README.md:60` says "the live command refuses locally (exit 2)". `ask`/`gate` do return 2 (`bin/jev.mjs:85,111`). Cause: the src wrappers throw on `!result.ok` (`kit/src/classify.ts:56`, `rerank.ts:61`, `verify.ts:54`, `score.ts:61`). | transcripts |
| P0-5 | **`--json` is silently ignored.** `doctor --json` prints human text. `classify --json` prints the same pretty JSON as no flag. | transcripts |

---

## 1. Current-surface scorecard (pass 1, rubric 1.0.0)

Anchors used per dimension (RUB line ranges): §1 intuitiveness `:22-30`, §2 ergonomics `:38-46`, §3 ease_of_use `:54-62`, §4 parseability `:70-78`, §5 error_pedagogy `:86-94`, §6 intent_inference `:102-110`, §7 safety `:118-128`, §8 determinism `:136-144`, §9 self_doc `:152-160`, §10 composability `:168-176`, §11 regression `:184-194`.

- Read-side verbs score safety 1000 as n/a (`RUB:128`; `AE/references/rubric/SURFACE-CLASSES.md:21`).
- `n/s` means not scored because the probe would mutate state or make a call. It is excluded from the mean.
- The weighted score is the arithmetic mean (`RUB:200`).
- Only two cells score above 700 (two §1/§8 entries). Both cite a transcript, as `RUB:30,144` requires.

| Surface | §1 | §2 | §3 | §4 | §5 | §6 | §7 | §8 | §9 | §10 | §11 | **mean** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `jev` bare / `--help` / `-h` / `help` / `--version` | 250 | 250 | 100 | 250 | 250 | 0 | 1000 | 750 | 0 | 500 | 0 | **304** |
| `doctor` | 750 | 500 | 250 | 500 | 250 | 0 | 1000 | 750 | 250 | 500 | 500 | **477** |
| `ask choice\|score\|noul` | 500 | 500 | 250 | 500 | 250 | 0 | 1000 | 250 | 250 | 500 | 500 | **409** |
| `gate` | 500 | 500 | 250 | 500 | 250 | 0 | 1000 | 500 | 250 | 500 | 250 | **409** |
| `classify` | 500 | 500 | 250 | 250 | 250 | 0 | 1000 | 250 | 250 | 500 | 500 | **386** |
| `rerank` | 500 | 500 | 250 | 250 | 250 | 0 | 1000 | 250 | 250 | 500 | 250 | **364** |
| `verify` | 500 | 500 | 250 | 250 | 250 | 0 | 1000 | 250 | 250 | 500 | 250 | **364** |
| `score` | 500 | 500 | 250 | 250 | 250 | 0 | 1000 | 250 | 250 | 500 | 250 | **364** |
| `omp install\|uninstall` (hidden) | 250 | 500 | 250 | 500 | 250 | 0 | 250 | n/s | 250 | 500 | 500 | **325** |
| `jev-skill-gap` (2nd bin) | 500 | 500 | 250 | 250 | 250 | 250 | 250 | n/s | 250 | 500 | 500 | **350** |

Cell evidence (one line per non-obvious cell):
- **Bare/help**
  - §1=250 (`RUB:25`): generic usage line on stderr, exit 1.
  - §3=100 (`RUB:56-57`): no `--help` at all; the agent must read README.
  - §6=0 (`RUB:104`): `--help`, `help`, `--version` and `clasify` all get the same useless line.
  - §8=750: identical bytes across `--help`/`-h`/`help` runs (transcript).
  - §9=0 (`RUB:154`).
  - §11=0: no help test exists. Grep finds CLI spawns only in `classify`, `cli`, `install`, `package` and `skill-gap` tests.
- **doctor**
  - §1=750 (`RUB:27`): runs first try. Exit 2 `NOT_RUN: no key` matches `ROBOT.md:6`.
  - §2=500 (`RUB:42`): has a JSON mode, but no `recommended_action` and no `commands`.
  - §8=750: two `doctor --robot` runs gave byte-identical output (transcript, 872 B).
  - §11=500 (`RUB:188`): `kit/test/cli.test.mjs:26-36` and `kit/test/package.test.mjs:44-46` assert the JSON fields.
  - §6=0: `--json` is silently dropped. That is a silent_fail (`AE/references/methodology/ERROR-REWRITING-COOKBOOK.md:371-379`).
- **Decision verbs**
  - §1=500 (`RUB:26`): a missing argument prints the verb's syntax line.
  - §4=250 for classify/rerank/verify/score: exit codes conflict with docs (P0-4). That is CE-6, and CE patterns cap a dimension at 250 or below (`AE/references/exemplars/COUNTER-EXAMPLES.md:292`).
  - §5=250 (`RUB:89`). Examples: a missing file gives raw `ENOENT: no such file or directory, open '/…/nope.json'`; `rerank accepts at most 20 candidates; chunking is not supported` offers no path forward; `gate --fake` rejects a non-fixture command without naming the fixture command.
  - §8=250 (`RUB:139`): `latencyMs` varies between identical fake runs (classify 3/2, verify 3/4, score 2/4).
  - §11: classify=500 (`kit/test/classify.test.mjs:107-116` spawns the CLI and asserts fields). rerank/verify/score/gate=250: module tests only, no CLI spawn.
- **omp install**
  - §1=250: not listed in the usage string (`bin/jev.mjs:227`).
  - §7=250 (`RUB:121`): uninstall is dry-run by default and needs `--apply` (`bin/jev.mjs:223`), and install refuses to overwrite. But the refusal is `reason:"exception"`, exit 1, and names no safe alternative (transcript `omp install --dry-run --dir …`).
- **jev-skill-gap**
  - §1/§4: bare invocation and `--robot` print usage to **stdout** with exit 2. Exit 2 also means NOT_RUN in the same file (`kit/bin/jev-skill-gap.mjs:51-54,63`). That is CE-12 (`COUNTER-EXAMPLES.md:163-173`).
  - §6=250 (`RUB:105`): `-h` works; `--dialy` gets usage only.
  - §7=250: `--daily` writes beads unless `--no-review-beads` is passed (`kit/README.md:24-25`). There is no `--dry-run`.

**Family cross-cut** (dimensions from `AE/references/methodology/MULTI-TOOL-FAMILY-AUDIT.md:111-144`):

| Dimension | Score | Why |
|---|---|---|
| exit_code_consistency | 200 | kit: 2=NOT_RUN. hermes: 2=argparse usage. skill-gap: 2 means both usage and NOT_RUN. |
| envelope_consistency | 200 | CE-18 (`COUNTER-EXAMPLES.md:247-257`). Each verb emits its own flat shape; errors use `{status,reason,message}` while successes use `{ok,…}`. |
| naming_consistency | 100 | P0-1. |
| capabilities_consistency | 0 | Neither binary has `capabilities`. |

**Polish Bar** (`AE/references/methodology/POLISH-BAR.md`):
- Fails rows 1 (`:9-29`), 2 (`--json` ignored), 3, 4, 5, 6 (`:95-106`, P0-4), 7, 8 (`:126-139`), 10 (`:160-178`), and 12.
- Passes row 9 for read-side verbs only.
- Row 11 is n/a: no color is emitted.

---

## 2. Proposed design

### 2.1 Command tree (holds ~10 families + meta)

```
jev                                   # bare = human overview + help, exit 0 (Axiom 15, AE/SKILL.md:116-117)
jev --help | -h | help [<cmd>]        # exit 0; ends with AGENT/AUTOMATION footer (RUB:60)
jev --version                         # "jev-kit <semver> contract 1", exit 0
jev overview [--json]                 # MEGA-COMMAND (alias: jev --robot-triage), §2.2
jev capabilities --json               # contract (AE/.../MEGA-COMMAND-DESIGN.md:184-231)
jev robot-docs guide                  # <80-line handbook (POLISH-BAR.md:63-77)
jev schema [--command "<fam> <verb>"] --json
jev doctor [--family F] [--backend B] [--fix …]     # owned by DoctorSpec
jev install <target> [--dry-run|--apply]            # owned by InstallerSpec; targets: omp, skill-gap-agent, bin
jev ask choice|score|noul --state F --question F    # raw primitive escape hatch (granular path, AE/SKILL.md:558)

jev <family> [run] <inputs…>          # one decision; `run` is IMPLICIT when the next token is not a family verb
jev <family> batch  < in.ndjson       # NDJSON in → NDJSON envelopes out, one per line
jev <family> explain <inputs…>        # the exact request + design source + threshold/calibration; zero calls
jev <family> cases [--json]           # list fixture cases (fire / quiet rows)
jev <family> eval  [--backend B|all] [--live]   # offline replay of recorded rows vs bar; RED = exit 1
jev <family> calibrate [--backend clef] [--apply]  # fit/show Platt map; writes only with --apply
jev skillgap mine|status              # ex `jev-skill-gap --daily` (§2.6)
```

**Family slots.** The names are placeholders until the areas research names them. Each slot cites the evidence that justifies it.

| Slot | Placeholder | Primitive | Existing surface it absorbs | Evidence |
|---|---|---|---|---|
| F1 | `classify` | Choice | `jev classify` | Banking77 (`kit/README.md:27-44`); clef+Platt acc .962 vs .787 (conductor scoreboard 2026-10-04) |
| F2 | `rank` (alias `rerank`) | Choice top-1 | `jev rerank` | FiQA (`kit/README.md:46-56`); native judge `find` 32,301 calls/7d (conductor scoreboard) |
| F3 | `verify` | Noul | `jev verify` | SciFact 361/400 (`kit/README.md:72`) |
| F4 | `score` | Score | `jev score` | SST-5 (`kit/README.md:76-88`) |
| F5 | `gate` | 5×Noul RISK | `jev gate` | gate-observe 19,769 scored (conductor scoreboard) |
| F6 | `screen` | Noul | (omp tool `jev-screen.ts`) | injection-shadow 4,396 (conductor scoreboard) |
| F7 | `review` | Score | — | bead jev-k9z.2 (`.beads/issues.jsonl:317`) |
| F8 | `inbox` | Noul | — | bead jev-k9z.4 (`:319`). Deliberately not named `triage`. |
| F9 | `memory` | Choice | (memory-filter hook) | 455k tokens removed/7d (conductor scoreboard) |
| F10 | `vendor` | Noul | (vendor-shadow) | AUC .839 vs .827 (conductor scoreboard) |

**Naming rules** (enforced by a test, T5):
1. Family names never equal a meta verb (`overview capabilities robot-docs schema doctor install ask help skillgap`) or a family verb (`run batch explain cases eval calibrate`).
2. Family names must not equal a hermes verb unless the binary-ownership decision (D-2) folds hermes in. Hermes verbs: `route rerank triage search plan choose …`. That is why F8 is `inbox`, why the intent family is not `route`, and why `rerank` is an alias of F2, not its name.
3. Single lowercase word, 3–10 chars, so tab completion and Levenshtein suggestions stay unambiguous.

**Implicit `run`.** `jev classify --text T --labels F` already *is* `jev classify run --text T --labels F`, so every documented legacy invocation keeps working unchanged (§2.6).

### 2.2 Mega-command `jev overview` (TRIAGE + DIAGNOSE + CAPABILITIES shapes, `MEGA-COMMAND-DESIGN.md:42-231`)

It is not called `triage` because hermes `jev triage` already exists (P0-1) and F8 would want that word. The `--robot-triage` flag alias is safe because flags do not collide with verbs.

Rules:
- Offline, zero model calls.
- Probes the clef endpoint `GET http://127.0.0.1:8010/…` with a ≤500 ms timeout and reports the per-probe status `computed|timeout` (two-phase, `MEGA-COMMAND-DESIGN.md:301-321`).
- Target latency under 1 s (`:307`).

```jsonc
{ "ok": true, "schema": "jev.overview.v1", "status": "OK",
  "data": {
    "quick_ref": { "summary": "5/10 families ready; backends jev=NOT_RUN(no key) clef=READY", "top_3": [ {"family":"classify","backend":"clef","reason":"measured winner, calibrated"} ] },
    "backends": { "jev": {"state":"NOT_RUN","reason":"no key","model":"jev-1.13.0","key_source":"none"},
                  "clef": {"state":"READY","endpoint":"http://127.0.0.1:8010/v1/systemone","model":"clef-flash","probe":"computed_ms_41"} },
    "families": [ {"name":"classify","default_backend":"clef","auto_resolves_to":"clef","calibrated":{"clef":true,"jev":false},
                   "measured":{"metric":"acc","clef":0.962,"jev":0.787,"n":600,"source":"work/local-decision-arms/run.py --platt clefflash"},
                   "last_eval":{"status":"GREEN|RED|NONE"}} ],
    "recommendations": [ {"code":"no_key","rationale":"jev backend NOT_RUN; families defaulting to jev fall back to clef or refuse",
                          "command":"jev doctor --backend jev --json"} ],
    "health": { "doctor_status": "…", "path_conflict": {"jev_on_path":"/Users/josh/.local/bin/jev","owner":"hermes-jev-skills"} }
  },
  "meta": {"contract_version":"1","tool_version":"…","data_hash":"sha256:…"},
  "warnings": [ {"code":"path_conflict","message":"`jev` on PATH is hermes-jev-skills, not jev-kit","command":"jev install bin --dry-run"} ],
  "commands": [ {"action":"try","command":"jev classify --text \"How do I locate my card?\" --labels kit/examples/banking77-labels.json --fake --json","destructive":false} ],
  "errors": [] }
```

### 2.3 Uniform flags (every family verb; capabilities lists them under `flags.global`)

| Flag | Meaning | Default / env | Notes |
|---|---|---|---|
| `--json` | Envelope v1 on stdout, one line | `JEV_JSON=1` | Data only; all diagnostics go to stderr (Axiom 4, `AE/SKILL.md:83-84`) |
| `--robot` | Same as `--json`. On legacy invocations it also mirrors legacy top-level keys (§2.6) | `JEV_ROBOT=1` | Existing scripts and tests keep parsing `body.ok/label/model` |
| `--backend jev\|clef\|auto` | Which System One server answers | `JEV_BACKEND`, else the family's `default_backend` from the registry | `auto` = the family's measured winner if healthy, else the other backend if *it* has a calibration map, else exit 2 NOT_RUN. Always reports `meta.backend`, `meta.backend_requested` and `meta.fallback_reason` (Provenance-Field, `AE/references/methodology/OPERATORS.md:336-350`). Never falls back silently. |
| `--fake` | Replay the recorded fixture; zero network | — | `meta.backend:"fake"`. Adds `meta.fixture_match:true\|false` plus warning `fake_input_mismatch` when the input sha ≠ fixture sha (today classify/verify/score replay any input with no signal, while gate refuses: transcripts) |
| `--dry-run` | Build the exact request (endpoint, model, state, questions), run the size preflight, print it, make **zero** calls | — | Exit 0; `data.request`. On mutating commands = plan only. |
| `--explain` | Run normally and add `data.explain` | — | Fields: `design_ref` (file:line), instruction, criteria, threshold, Platt `{a,b,fit_id}`, raw vs calibrated probability |
| `--text -` / `--input -` | Read the input from stdin | — | Discoverable-from-stdin (`AE/references/methodology/AGENT-API-DESIGN-PRINCIPLES.md:189-205`) |
| `--yes` / `--apply` | Required for any write (calibrate, install, skillgap beads) | — | Without it → exit 4 with the `--dry-run` alternative named (Axiom 11) |
| `-q/--quiet`, `-v` | stderr verbosity only | — | Never changes stdout |

Clef backend wire format: the same System One body as Jev (`state` + `questions{type,instructions,criteria}`; `work/local-decision-arms/run.py:31-47`), POSTed to `JEV_CLEF_URL` (default `http://127.0.0.1:8010/v1/systemone`) with model `clef-flash`. No key needed. Per-family Platt maps live in `kit/families/<f>/calibration/clef.json`, fitted on dev and applied to held-out (`run.py:161-194`). The calibrated probability is what thresholds see. Raw values stay under `--explain`.

### 2.4 Exit-code contract (one dictionary; agents branch on `status` / `errors[].code` strings first)

Reconciled with DoctorSpec (world-class-doctor dictionary) and InstallerSpec.

| Code | Kind (`exit_code_kind`) | Scope | Meaning |
|---|---|---|---|
| 0 | `ok` | all | Success. A decision was returned. A `flag:true` gate verdict is **data**, not an exit code. Empty batch → `[]` and exit 0 (`AE/references/methodology/ANTI-PATTERNS.md:136-138`) |
| 1 | `findings` | all | `doctor` found problems / `<family> eval` RED (bar missed or a planted negative was not caught) |
| 2 | `not_run` | decision verbs | No call was made: no key, SDK missing, or billing hold (`kit/src/client.ts:237-241,286-298`). Keeps `ROBOT.md:6`, `README.md:60`, `stranger-run-expected.tsv:9,11`. (DoctorSpec: `fix_partial`) |
| 3 | `refused` | decision verbs | A call was made but the answer failed validation: unoffered label, malformed Noul, non-finite score (`classify.ts:57`, `verify.ts:56-57`, `score.ts:62-63`). (DoctorSpec: `fix_failed_rolled_back`) |
| 4 | `refused_unsafe` | all | A mutation was refused without `--apply`/`--yes`, or a collision (installer overwrite, PATH `jev` takeover) |
| 5 | `retryable` | all | Transient upstream failure (HTTP 5xx, transport, timeout: `client.ts:330-333`) / lock lost. Retry is safe. |
| 6 | `online_required` | all | Decision verbs: the required backend is unavailable (clef server down, network off). Doctor: an `--only`-selected online check was run without `--online`. Doctor never exits 6 on clef-down; that is a finding, exit 1 (DoctorSpec). |
| 64 | `usage` | all | Unknown verb or flag, bad flag value, missing required argument |
| 66 | `no_input` | all | Input file missing or unreadable (today raw ENOENT → 1) |
| 73 / 74 | `cant_create` / `io` | all | Cannot write output / state; IO error |

- **Open decision D-1 (for Main).** Codes 2 and 3 mean different things for decision verbs and for doctor. This spec recommends keeping them class-scoped:
  - Document them per command in `capabilities.commands.<cmd>.exit_codes` (`MEGA-COMMAND-DESIGN.md:207`).
  - Always mirror them as strings in the envelope (cass pattern 25, `AE/references/exemplars/CANONICAL-EXEMPLARS.md:272-278`).
  - The alternative is to renumber decision-verb NOT_RUN. That breaks 5 pinned surfaces: `README.md:60`, `ROBOT.md:6`, `stranger-run-expected.tsv:9,11`, `cli.test.mjs:28` and `package.test.mjs:45`.
- **Usage 1 → 64 rollout** follows deprecation pattern D-3 (`AE/references/methodology/DEPRECATION-PATTERNS.md:132-189`):
  - Stage 0: `JEV_STRICT_EXIT=1` opts in, and the envelope already says `errors[0].code:"usage"`.
  - Stage 1: flip the default; `JEV_LEGACY_EXIT=1` keeps 1.
  - `kit/test/cli.test.mjs:53` pins 1 and must be updated at stage 1.
- **Exit code never depends on output mode** (CE-20, `COUNTER-EXAMPLES.md:275-285`).
- **Open decision D-3 (DoctorSpec).** `jev doctor --json` emits the raw world-class-doctor report; `--robot` wraps it in this envelope (`data` = report). Every other command uses one envelope for both flags. Recommendation: accept this as a doctor-only exception, declared in `capabilities.commands.doctor.output_format`, so agents branch on capabilities instead of guessing.

### 2.5 JSON envelope `jev.<cmd>.v1` (`AE/references/methodology/JSON-SCHEMA-PATTERNS.md:7-23,250-284`)

```jsonc
{ "ok": true,                                   // false iff exit != 0
  "schema": "jev.classify.run.v1",
  "status": "OK|NOT_RUN|REFUSED|FINDINGS|REFUSED_UNSAFE|RETRYABLE|ONLINE_REQUIRED|USAGE|NO_INPUT",
  "data": { "decision": {"label":"lost_or_stolen_card","p":0.86,"p_raw":0.87,"probabilities":{…}},
            "family":"classify","design":"banking77" },          // null when ok=false
  "meta": { "contract_version":"1","tool_version":"…","backend":"jev|clef|fake","backend_requested":"auto",
            "fallback_reason":null,"model":"jev-1.13.0","calibration":{"method":"platt","fit_id":"…"}|null,
            "input_sha256":"…","fixture_match":null,
            "latency_ms":3,"usage":null },                       // ONLY latency_ms and usage are volatile (documented)
  "warnings": [ {"code":"…","message":"…"} ],
  "commands": [ {"action":"explain","command":"jev classify explain --text … --labels …","destructive":false} ],
  "errors":   [ {"code":"not_run","exit_code":2,"message":"…","remediation":["…","…"],"see":"jev classify --help"} ] }
```

- Determinism (`RUB:141`): bytes are identical across runs after deleting `meta.latency_ms` and `meta.usage`. There are no timestamps anywhere. Today `latencyMs` sits at the top level of the payload (transcripts), which is why decision verbs score 250 on §8.
- Errors go to stdout as an envelope **and** `errors[0].message` plus remediation go to stderr (`JSON-SCHEMA-PATTERNS.md:272`). In human mode, nothing goes to stdout on error.
- Legacy fields (`label`, `confidence`, `probabilities`, `latencyMs`, `model`, `reason`, `message`, …) are mirrored at the top level only for legacy invocations under `--robot` (§2.6, pattern D-4 `DEPRECATION-PATTERNS.md:193-241`).

### 2.6 Migration of every existing verb and bin (stage model `DEPRECATION-PATTERNS.md:11-31`)

| Today | Canonical after | Stage 0 (this pass) | Stage 1 (next pass) | Stage 2–3 |
|---|---|---|---|---|
| `jev classify --text T --labels F [--fake] [--robot]` | `jev classify [run] …` | Unchanged invocation. `--robot` = envelope + mirrored flat keys. No-key exit 1→**2** (bug fix, makes `README.md:60` true). | `_deprecation:[{"path":"$.label","use_instead":"$.data.decision.label"}]` | Mirrored keys removed; contract 2 |
| `jev rerank --query Q --candidates F` | `jev rank [run] …` | `rerank` = alias, no warning | stderr `note: 'rerank' → 'rank'` (D-2, `:103-128`) | error, then removed |
| `jev verify --claim C --evidence F` | `jev verify [run] …` | as classify | as classify | as classify |
| `jev score --text T --levels F` | `jev score [run] …` | as classify | as classify | as classify |
| `jev gate --command C` | `jev gate [run] …` | as classify. `--fake` mismatch error names the fixture command (§2.7 E8). | as classify | as classify |
| `jev ask choice\|score\|noul --state F --question F` | unchanged primitive | gains `--json`, `--backend`, `--dry-run` | — | — |
| `jev doctor [--robot]` | `jev doctor` (DoctorSpec) | DoctorSpec plan; `status:"NOT_RUN"` string kept for `ROBOT.md:6` readers | per DoctorSpec | — |
| `jev omp install\|uninstall [--dir] [--dry-run\|--apply]` | `jev install omp …` (InstallerSpec) | old form = alias; listed in help | warn | error |
| `jev-skill-gap --daily [flags]` | `jev skillgap mine [flags]` | Bin stays as a 3-line exec shim to `jev skillgap mine`. Usage goes to **stderr**; bare invocation → help on stdout, exit 0. | stderr deprecation note | Bin removed from `package.json` `bin` |
| `jev-skill-gap --install` | `jev install skill-gap-agent` (InstallerSpec) | alias | warn | removed |
| `jev-skill-gap --no-review-beads` | same flag | kept. New `--dry-run` = scan plan + cost estimate, **zero writes and zero calls** (today `--no-review-beads` still writes state and may call Jev, `kit/README.md:24-25`) | — | — |

Non-breakage invariants, pinned by T4:
- `docs/demos/upstream-repro/stranger-run-expected.tsv:9-17` classes stay identical.
- `kit/test/cli.test.mjs`, `classify.test.mjs:107-116`, `package.test.mjs:44-46` and `skill-gap.test.mjs:126-130` pass unmodified at stage 0.
- `npx --prefix kit --no-install jev …` resolves the kit bin. The PATH collision affects only bare `jev`, and its resolution is D-2.

**Open decision D-2 (Main + InstallerSpec): who owns the `jev` name on PATH.** Current state: `~/.local/bin/jev` → hermes. InstallerSpec treats a non-marker `jev` as a conflict, never overwrites it, and offers `--bin-name` / `--take-over-bin`. This spec's naming rules (§2.1) keep both binaries collision-free at the verb level until that is decided.

### 2.7 Error rewriting (template `ERROR-REWRITING-COOKBOOK.md:547-558`; every message ≤10 lines, stderr)

| # | Invocation (observed) | Today | After |
|---|---|---|---|
| E1 | `jev`, `jev --help` | 1-line usage, exit 1 | Help + footer, exit 0 |
| E2 | `jev clasify …` | generic usage, exit 1 | `error: unknown command 'clasify'` / `did you mean: jev classify …(argv replayed)` / `see: jev --help` → 64 |
| E3 | `… --jsno`, `… --robto` | silently ignored, exit 0 | Stage 0: `warning: '--robto' interpreted as '--robot'` (Levenshtein-1, non-destructive only, `COOKBOOK.md:85`), proceed. Unknown non-near flag: `warning: unknown flag '--zzz' ignored; see jev classify --help`. Stage 1: 64. |
| E4 | `classify --label F` | generic usage | `error: classify requires --labels FILE (got --label; did you mean --labels?)` / `example: jev classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --json` → 64 |
| E5 | classify, no key | exit 1, `reason:"exception"`, `…--projectId=…` | `NOT_RUN: jev backend has no key (TYPESAFE_API_KEY unset)` / `offline: add --fake` / `local model: --backend clef` / `diagnose: jev doctor --backend jev` → 2 |
| E6 | `--labels nope.json` | raw ENOENT, exit 1 | `error: --labels file not found: nope.json (cwd /…/kit)` / `example file: kit/examples/banking77-labels.json` → 66 |
| E7 | rerank with >20 candidates | `…chunking is not supported`, exit 1 | `error: rank takes 2-20 candidates, got 77` / `keep the top 20 from your first-stage ranker, then: jev rank --query … --candidates top20.json` → 64 |
| E8 | `gate --fake --command "rm -rf /"` | `--fake only supports the captured public example command` | adds `fixture command: jev gate --fake --command "npm publish --access public"` / `list: jev gate cases` → 64 |
| E9 | `omp install` onto unmanaged files | `refusing to overwrite… <13 paths>`, exit 1 | names the count + first 3 paths, `preview: jev install omp --dir D --dry-run`, `owned-by-you? jev install omp --dir D --adopt --apply` (per InstallerSpec) → 4 |
| E10 | clef down, `--backend clef` | n/a | `error: clef backend unreachable at http://127.0.0.1:8010/v1/systemone (connect refused)` / `use hosted: --backend jev` / `diagnose: jev doctor --backend clef` → 6 |
| E11 | `jev-skill-gap` bare | usage on stdout, exit 2 | help on stdout, exit 0. Unknown flag → stderr hint, 64. |
| E12 | answer outside the offered set | thrown, exit 1 | `REFUSED: model returned unoffered label 'x'; no decision emitted` / `inspect: --explain` → 3 |

---

## 3. Ordered implementation tasks

Priority follows `frequency × score_gap × blast_radius` (`AE/references/rubric/PRIORITY-FORMULA.md:5-9`). Every task:
- writes its failing test first;
- includes a planted negative that must fail;
- lands one regression test per rec (`REGRESSION-TEST-PATTERNS.md`, cited by pattern number).

Tests live in `kit/test/` (the project's suite, `kit/package.json` `test`). All are keyless. Network is guarded by the `observedFetch` counter (`kit/src/client.ts:120-124`).

| # | Task (files) | Failing test first | Planted negative | Acceptance command |
|---|---|---|---|---|
| T1 | **Argv + dispatch module**: one known-flag table per command, order-insensitive, implicit `run`, Levenshtein-1. Files: `kit/src/cli/argv.ts`, `kit/src/cli/dispatch.ts`; `kit/bin/jev.mjs` shrinks to an entry shim. | `cli-argv.test.mjs`: `--robto` → stderr `interpreted as '--robot'` + JSON stdout; `clasify` → `did you mean` (today: silent / generic) | `--zzzz` (distance > 1) must produce **no** suggestion; a destructive flag (`--apply`) must never be auto-corrected | `node --test kit/test/cli-argv.test.mjs` |
| T2 | **Help surface**: bare/`--help`/`-h`/`help <cmd>`/`<cmd> --help`/`--version`, exit 0, AGENT/AUTOMATION footer naming `--json`, `capabilities`, `robot-docs`, exit codes (`RUB:60`). Files: `kit/src/cli/help.ts` | `cli-help.test.mjs` (Pattern 1): exit 0 + footer for each probe in `POLISH-BAR.md:13-21` (today exit 1) | delete the footer line from one verb's help → test must go red | `node kit/bin/jev.mjs --help; echo $?` → `0` |
| T3 | **Exit-code module + no-key fix**: `kit/src/cli/exit.ts` (§2.4). Wrappers return typed refusals instead of throwing (`classify.ts:56`, `rerank.ts:61`, `verify.ts:54`, `score.ts:61`). | `cli-exit.test.mjs` (Pattern 2): classify/rerank/verify/score without key → 2 + `status:"NOT_RUN"` (today 1) | same command with `--fake` must exit 0; an injected unoffered label must exit 3, not 2 | `env -u TYPESAFE_API_KEY node kit/bin/jev.mjs classify --text x --labels kit/examples/banking77-labels.json --robot; echo $?` → `2` |
| T4 | **Envelope v1 + legacy mirror**: `kit/src/cli/envelope.ts`; `--json` honored on all verbs incl. doctor | `cli-envelope.test.mjs` (Patterns 3, 5, 6): required keys; stdout parses with stderr discarded; two runs byte-identical after `del(.meta.latency_ms,.meta.usage)`. Existing `cli.test.mjs`, `classify.test.mjs`, `package.test.mjs` unchanged and green | move `latency_ms` into `data` → determinism test red | `node --test kit/test/*.test.mjs` all green; `bash`-run of `stranger-run-expected.tsv` rows 9-17 classes unchanged |
| T5 | **Family registry + capabilities/robot-docs/schema generated from it** (`REC-PATTERNS.md:238-241`: introspect, don't hand-curate). Files: `kit/src/families/registry.ts`, `kit/src/cli/{capabilities,robot-docs,schema}.ts` | `cli-capabilities.test.mjs` (Pattern 9): keys `version contract_version features commands exit_codes env_vars`; every dispatchable command ∈ `commands`; naming rules §2.1 | register a family with no capabilities entry, or named `triage` → red | `node kit/bin/jev.mjs capabilities --json \| jq -e '.commands.classify.exit_codes'` |
| T6 | **Error rewrites E2–E12** in `kit/src/cli/errors.ts` (one template) | `cli-errors.test.mjs` (Pattern 4): each row's stderr contains its remediation command and exit code | E6 with a path that exists → must **not** emit `no_input` | `node kit/bin/jev.mjs classify --text x --labels nope.json; echo $?` → `66` |
| T7 | **Backend layer** `--backend jev\|clef\|auto`, clef client on the same wire format (`run.py:31-47`), Platt apply, provenance meta. Files: `kit/src/backends/{jev,clef,resolve}.ts`, `kit/families/<f>/calibration/clef.json` | `backend.test.mjs` with injected fetch: `--backend clef` + refused connect → 6; `auto` + clef down + jev keyed → `meta.backend:"jev"`, `fallback_reason:"clef_unreachable"` + warning | an `auto` fallback that leaves `fallback_reason:null` → red; a clef answer for a family without a calibration map under `auto` → must refuse (2), not silently use raw p | `node --test kit/test/backend.test.mjs` (no live call; fetch counter on the real URL = 0) |
| T8 | **Families F1–F5 wired** (classify, rank+`rerank` alias, verify, score, gate) with implicit `run` | `families.test.mjs`: `jev classify --…` ≡ `jev classify run --…` (same `data`); `jev rerank` ≡ `jev rank` | an alias that emits a deprecation warning at stage 0 → red (stage 0 = silent alias) | `node kit/bin/jev.mjs rank --query q --candidates kit/examples/rerank-candidates.json --fake --json \| jq -e .ok` |
| T9 | **`--dry-run` / `--explain`** on all decision verbs | `dryrun.test.mjs`: dry-run prints `data.request` with endpoint/model/state; fetch counter = 0 | a dry-run path that reaches `fetch` → red | `node kit/bin/jev.mjs verify --claim c --evidence kit/examples/scifact-evidence.txt --dry-run --json \| jq -e .data.request` |
| T10 | **Mega-command `jev overview`** + `--robot-triage` alias; PATH-conflict warning; `commands[]` | `overview.test.mjs` (Pattern 10): ≥3 slices incl. `commands`; runs < 1 s with clef stubbed down | an overview that makes a model call (fetch counter on `/v1/systemone` > 0) → red | `node kit/bin/jev.mjs overview --json \| jq -e '.data.families and .commands'` |
| T11 | **stdin + `batch`** (NDJSON) | `batch.test.mjs`: 3 lines in → 3 envelopes out, input order kept; empty stdin → `[]`-equivalent zero lines, exit 0 | a malformed middle line → that line `ok:false` 64, the others still `ok:true`; whole-run exit 64 | `printf '{"text":"a"}\n' \| node kit/bin/jev.mjs classify batch --labels … --fake` |
| T12 | **Per-family suite (omp-kit shape)**: `kit/families/<f>/{cases.tsv,fixtures/,BAR.md link}`; `cases`, `eval`, `calibrate` verbs. Fire/quiet rows differ by one element (`~/.agents/skills/omp-kit/SKILL.md:31-33`); RED exits 1 like the omp-kit doctor (`:75`). | `eval.test.mjs`: replay of recorded rows reproduces the stored metric within tolerance | a planted quiet row relabeled as fire → `eval` must exit 1 and name the row; `calibrate` without `--apply` writes nothing (sha unchanged) | `node kit/bin/jev.mjs classify eval --backend fake --json; echo $?` |
| T13 | **`jev skillgap mine` + `jev-skill-gap` shim**; usage → stderr; `--dry-run` = zero writes/calls | `skillgap-cli.test.mjs`: bare shim → help, exit 0; `--dialy` → stderr hint `--daily`, 64 (strict) | `--dry-run` that touches `state-dir` (mtime/sha check) → red; existing `skill-gap.test.mjs:126-130` must stay green | `node kit/bin/jev-skill-gap.mjs; echo $?` → `0` |
| T14 | **Docs**: `kit/ROBOT.md` (envelope, exit table, backends), README (help/overview first), CHANGELOG, `robot-docs guide` ≤80 lines. Queue stage-1 deprecations as beads (filed by the owner, not here). | `docs-drift.test.mjs`: every command in `capabilities` appears in ROBOT.md and vice versa (`AE/scripts/audit-readme-vs-help.sh` idea) | remove one verb from ROBOT.md → red | `node --test kit/test/docs-drift.test.mjs` |

**Expected uplift** if T1–T10 land: every decision-verb surface goes from ~364–409 to ≥750 on §1, §3, §4, §5, §6, §8, §9, §11. Cross-cut exit and envelope consistency go from 200 to ≥750. This is an estimate, not a measurement. Re-score after apply per `AE/SKILL.md:403-406`.

**Verification for Main after implementation** (not run here):
- `npm run prepare --prefix kit && node --test kit/test/*.test.mjs`
- the stranger runner against `docs/demos/upstream-repro/stranger-run-expected.tsv`
- `AE/scripts/verify-stdout-stderr-split.sh`, `verify-determinism.sh` and `verify-non-tty-discipline.sh` against `node kit/bin/jev.mjs`

---

## 4. Skill files: read fully vs skimmed, load-bearing items

Read in full:
- `SKILL.md`
- `references/{CHEAT-SHEET,QUICKREF,REC-PATTERNS,REAL-AUDIT-CHECKLIST}.md`
- `methodology/{AGENT-API-DESIGN-PRINCIPLES,CLI-ARCHETYPES,MEGA-COMMAND-DESIGN,IO-CONTRACTS,JSON-SCHEMA-PATTERNS,ERROR-REWRITING-COOKBOOK,MULTI-TOOL-FAMILY-AUDIT,DEPRECATION-PATTERNS,ANTI-PATTERNS,POLISH-BAR}.md`
- `rubric/{SCORING-RUBRIC,SURFACE-CLASSES,PRIORITY-FORMULA,RUBRIC-EXTENSIONS,CHANGELOG}.md`
- `rubric/REGRESSION-TEST-PATTERNS.md` lines 1-300
- `exemplars/CANONICAL-EXEMPLARS.md`

Skimmed (headings plus the cited ranges), with the load-bearing items for this work:
- `methodology/SCHEMA-EVOLUTION.md:42-59`: `contract_version` "1"→"1.1" additive, "2" breaking. It must be in both capabilities and `meta`.
- `methodology/LANGUAGE-RECIPES.md:822-889` (TS: unknown-option override + capabilities verb) and `:1171` (one shared KNOWN_FLAGS list for capabilities and typo hints). This is the basis for T1/T5.
- `methodology/OPERATORS.md:318-350`: `recommended_action{command,rationale,is_destructive,alternatives}` (doctor, overview) and the Provenance-Field (`--backend auto` fallback).
- `exemplars/COUNTER-EXAMPLES.md:163-285`: CE-12 (usage on stdout, skill-gap), CE-18 (envelope chaos), CE-19 (order sensitivity), CE-20 (exit code depends on output mode).
- `methodology/INTENT-CORPUS-GENERATION.md` (categories A–M): use it to generate the T1/T6 corpus for Phase 3.
- `methodology/HOOKS-INTEGRATION.md:78-153`: capabilities-pin and help-footer drift hooks; candidates after T5/T2.
- `methodology/CRASH-RECOVERY-AND-RESUMABILITY.md:80-101`: idempotency tokens; relevant to `batch` resume and `skillgap mine` state.
- `methodology/TUI-MODE-AUDIT.md:322`: "TUI as a verb". Not applicable; jev has no TUI.
- `methodology/MCP-SERVER-AUDIT.md:262`: MCP–CLI parity. Relevant later because the omp tools (`.omp/tools/jev-*.ts`) are a second agent surface over the same families.
- `methodology/AGENT-PROFILES.md`: Claude Code profile weights agent_ergonomics ×1.5 (`AE/SKILL.md:680-684`). This argues for the mega-command first.
- Not used: `CONFIG-AS-CODE`, `PLUGIN-AND-EXTENSION`, `DSL-AND-SDK`, `OBSERVABILITY` (jev emits no color, progress or telemetry), and the calibration fixtures.

Process note: this spec is audit-only. The skill defaults to `full` mode with an in-tree `agent_ergonomics_audit/` (`AE/SKILL.md:12-16`). That was deliberately not applied: the conductor's read-only rule outranks it (`AE/SKILL.md:1016-1020`, "AGENTS.md says no"). The implementer should scaffold that workspace when executing T1–T14.

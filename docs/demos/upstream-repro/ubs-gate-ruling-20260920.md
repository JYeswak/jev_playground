# ubs as a lane gate: KEEP_HAND_RUN_ONLY (extracted 2026-09-20)

Extracted VERBATIM from NEGATIVE_EVIDENCE.md R6/R-ubs so that STATUS.tsv row
UP-R16-ubs-as-a-gate can pin a digest to a STABLE file. The ledger is appended
concurrently by three panes, so a digest pinned to it drifts the moment a peer
adds an entry -- which is exactly what happened when R46 landed. The ruling
itself is unchanged; NEGATIVE_EVIDENCE.md remains the working ledger.

---

## R6 — RETRY CHECKED: `ubs` on first-party TypeScript

**Original measurement:** `ubs AGENTS.md scripts/sync-docs.sh .fh-agents.toml EVAL.md` →
`no supported languages detected … UBS did not run any scanner: nothing was checked (this is NOT a
pass). Exiting 3`.

**So:** citing UBS on a markdown-only change would be citing an empty scan set as a pass — the exact
anti-pattern this lane bans. The Landing-the-Plane checklist scoped UBS to changes that touch
TS/Python/Rust.

**Retry condition:** the lane gains first-party code (`probes/`, a ported demo, or a `.omp/` seam in
TS). UBS applies from that commit onward — and exit 3 still never counts as green.

**Retry check (2026-09-18, jev-publish-redteam-7s0): SATISFIED as a scan-set condition.** `git ls-files`
identified exactly four first-party TypeScript paths: `compaction/src/omp-adapter.ts`,
`compaction/src/omp-hook.ts`, `compaction/src/replay.ts`, and `compaction/ab/run-ab.ts`.
Vendored clones were excluded by scanning this explicit tracked-file list, not a repository-wide
path. UBS scanned 4 files and exited 1: 1 critical, 6 warnings, 27 info. The only critical was
`Possible hardcoded secrets` in `run-ab.ts`; triage found no secret value (only an environment
variable name/receipt provenance string), and `30-no-secrets` passed. The positive-control temp
project containing `eval()` exited 1 with `eval() ALLOWS ARBITRARY CODE EXECUTION`, proving the
scanner fires. Existing async-listener and JSON.parse warnings are documented fail-fast/host-await
shapes, not confirmed defects; no new defect bead was warranted.

Receipt: `docs/demos/duel-1/runs/ubs-r6-20260918T011614Z.json`.

---

### R6 retry EXECUTED 2026-09-20 — `ubs` finally run on first-party TypeScript

The retry condition ("the lane gains first-party code") was marked SATISFIED on 2026-09-18 as a
scan-set condition, and then **nobody ran the tool for two days**. The arsenal audit
(`commit-learnings-20260920.md`) listed `ubs` as owned, installed, one reference, never executed.
Dry-queue rung 2 says take the oldest satisfiable retry, so it got run.

```
ubs work/jev-client/src/index.ts work/omp-harm-rule/harm-rule.ts work/jev-score-register/register.mjs
Files: 3 | Critical: 0 | Warning: 5 | Info: 11
```

**Verdict: the tool runs, the scan-set condition was real, and it found nothing actionable in
these three files.** Stated plainly rather than dressed up:

- **`harm-rule.ts:55` — "async EventEmitter listener callback is not awaited".** Checked the
  source rather than the count. The listener body is wrapped in `try`/`catch` at three levels
  (`catch { /* never break the session */ }`, `catch { /* observability must never break the
  session */ }`, `catch (err)`), which is **precisely the remediation ubs itself proposes**:
  *"or handle rejections inside the EventEmitter listener."* Not a defect here.
- **4 × nested ternary** — style, in the frozen classifier whose arms are pinned by tests.
  Refactoring frozen scored code to satisfy a readability rule would change a measured artifact
  for no measured gain.
- **11 × info, mostly `security.env-in-client`** on `process.env.TYPESAFE_API_KEY` /
  `JEV_MODEL` / `HARM_RULE_DEBUG_KEYS`. The rule is about client bundles; these are Node
  extensions and never bundled. Inapplicable, not ignored.

**What this retry actually bought:** evidence that a tool we have owned all along produces
**0 critical** on our core client, rule and register. That is a weak-but-real result and it cost
one command. It does **not** say the code is correct — `ubs` scans patterns, and the three
genuine defects found in these files tonight (missing `safeAppend`, `recording()` misfiling every
choice success, the census-not-product filter) were all found by **running things**, not by
scanning them.

**Retry closed.** New condition, if anyone wants a stronger claim: run `ubs --ci
--fail-on-warning` over all 220 first-party `.ts`/`.mjs` files and rule on the aggregate. I ran
three files, not 220, and say so rather than implying coverage.

### R6 successor condition EXECUTED — `ubs` at scale, and it is NOT usable as a gate here

Last tick's successor condition was "run `ubs --ci --fail-on-warning` over all first-party files
and rule on the aggregate". Done, on `work/` (163 non-test first-party files; 199 scanned):

```
Files: 199 | Critical: 117 | Warning: 1134 | Info: 5320
exit code 1   (taken UNPIPED -- the piped run reported 0, which is tail's status)
```

**117 critical sounds like an emergency. It is not, and reporting the number without opening it
would have been this lane's own documented failure mode.** Every cluster inspected:

| n | rule | what it actually is |
|---|---|---|
| 84 | secret compared with `==`/`!=` | `if (previous === undefined) delete process.env.TYPESAFE_API_KEY` — env **restore** logic in tests. The *variable name* resembles a secret; no secret value is compared. |
| 7 | possible hardcoded secret | our own `PLACEHOLDERTOKENNODIGITS` / `PLACEHOLDER-NOT-A-REAL-TOKEN-8811` test literals, and a question key named `secret_staging`. **No real credential.** |
| 4 | loose equality | `==` in scratch measurement code |
| 3 | `new Function()` | |
| 2 | logging sensitive data | |

Top rules overall are `security.env-in-client` (372) and `js.async.await-no-try` (307). The first
is about **client bundles**; this repo ships Node extensions and never bundles. The second flags
every `await` outside a `try`, including ones inside a caller that already catches.

**RULING: `ubs` is NOT wired as a gate in this lane, and the reason is measured, not assumed.**
At a 117-critical aggregate where the inspected criticals are placeholder literals and
env-restore comparisons, a `--fail-on-warning` gate would be RED permanently and would therefore
be ignored permanently. **A gate that fires on everything is worse than no gate** — this lane
already refuses instruments on exactly that basis (`R18`), and it refused two of its own for it.

**What `ubs` is good for here:** a hand-run scan whose *clusters* are read, not its totals. It
confirmed 0 real hardcoded credentials across 199 files, which is a genuine negative result and
the most valuable thing it produced.

**RETIREMENT TRIGGER for this refusal:** `ubs` gains per-rule suppression (or the lane adopts a
config that disables `security.env-in-client` and scopes `js.async.await-no-try` to uncaught
awaits), and a re-run produces a critical count whose members are individually defensible. Then
it can be a stage. Until then it is `KEEP_HAND_RUN_ONLY`, the same verdict this lane already
reached for `verify-reason-numerals.sh`.

NO-CLAIM: I inspected the five critical clusters and two top warning rules, not all 117 criticals
or all 1,134 warnings individually. The 84 and 7 clusters were sampled, not exhaustively read —
if a real defect hides among them, this ruling did not find it, and the scan output is at
`/tmp/ubs-all.txt` for anyone who wants to read the rest.

# awesome-jev-by-typesafe W7.0 receipt — 2026-09-23 (worker W70AwesomeByTs)

Catalogue profile: T1 pin+env, T2-equivalent fresh suite + /tmp RED proof, T3 over
entries (existence, suite command, N quoted). No live Jev calls (N=0, cost $0,
no latency measured). Live model (unused): `jev-1.13.0`. Prior
`awesome-jev-by-typesafe-w70-20260922.md` and `EVAL.md:35-42` are leads, never passes.

## T-table

| id | verdict | evidence |
|---|---|---|
| T1 | PASS | Full SHA `d57f5ce8002cc7cadc2c744b34a45933507e0508`, date 2026-09-18, MIT, clean status before and after, env recorded below |
| T2 | PASS (equivalent) | Fresh suite 11/11 via two runners; /tmp planted defect turns RED (11 tests, 1 failure, exit 1). Clone tree never written |
| T3 | PASS | 8/8 entries assessed (existence, suite command, N quoted); 7/7 included-example paths exist; suite command `README.md:432`; N=11 `def test_` |
| T4 | NOT-RUN | Catalogue profile runs T1+T3 (+T2-equiv per this assignment); no live calls. Cause: assignment "No live calls" + `README.md:435` (live quickstart needs `TYPESAFE_API_KEY`). Routes tried: (1) class profile table, (2) assignment text. Second route: n/a — a live call would violate the assignment |
| T5 | NA | Floor arms apply to seat/benchmark only; catalogue has no labelled rows |
| T6 | NA | Incumbent arm applies to seat/benchmark only; N=0 live calls |
| T7 | NA | Calibration requires binned live verdicts; none exist at catalogue level |
| T8 | NA | Stability requires repeated live asks; none performed per profile |
| T9 | NA | Not an SDK/client/tool clone; no fault surface of its own |
| T10 | PASS (catalogue) | Result class withheld (none of SELF/FLOOR/INCUMBENT earned — catalogue scores no labelled rows). Tiers per claim in T3 table. NO-CLAIM below |

## T1 — pin and environment

- Path: `/Users/josh/Developer/jev/upstream/Anil-matcha/awesome-jev-by-typesafe`, remote `https://github.com/Anil-matcha/awesome-jev-by-typesafe.git` (`origin`)
- HEAD (pinned): `d57f5ce8002cc7cadc2c744b34a45933507e0508`
- Commit: date `2026-09-18 01:38:24 +0530`, author `Anil Chandra Naidu Matcha`, subject `Swap: remove unrelated files`
- `origin/main` (`git rev-parse origin/main`): `3a7f9d2e98df3290aca6cafeaf4009acc0018281` — upstream has moved ahead since the pin; this run stayed detached at `d57f5ce` (`git status`: `## HEAD (no branch)`, read-only run)
- `git status --porcelain=v1 -b`: clean (empty apart from the HEAD line) before the suite runs, after the suite runs, and after the /tmp defect run. `git diff --stat`: empty. Clone never edited
- License: MIT (`LICENSE:1` `MIT License`, copyright `(c) 2026 Anil Chandra Naidu Matcha`, `LICENSE:3`)
- Observation clock: `2026-09-23T03:41:01Z` (`date -u`), host `Joshs-Mac-Studio.local`, Darwin 25.5.0 arm64
- Env at pin read: `OMP_PROFILE=muse`, `PI_PROFILE=muse`, `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/muse/agent` (recorded as-is; the suite is pure stdlib and does not consult them)
- Runtimes: `git version 2.50.1 (Apple Git-155)`, `Python 3.9.6` (`python3 --version`; suite lane), system pytest `8.3.4` on Python 3.14.5 for the `uv run` lane. No `omp` invoked. No key printed

## T2-equivalent — fresh suite + RED proof

Suite file: `tests/test_decision_policies.py` — 11 `def test_` methods (5 GateAction +
3 WeightedScore + 3 RagDecision; grep count confirmed). Suite command stated by the
clone: `python -m unittest discover -s tests -v` (`README.md:432`).

Fresh GREEN (clone tree, read-only, 2026-09-23):

- `python3 -m unittest discover -s tests -v` → `Ran 11 tests in 0.001s`, `OK` (11/11)
- `python3 -m pytest tests/ -v` → `11 passed in 0.49s` (11/11)
- `PYTHONPATH=. uv run pytest tests/ -v` → `11 passed in 1.83s` (11/11; pytest 8.3.4)

Import-path note (pre-existing, not a code failure): bare `uv run --project <clone>
pytest tests/ -v` (no `PYTHONPATH=.`) collects 1 error —

```text
ModuleNotFoundError: No module named 'examples'
ERROR tests/test_decision_policies.py
pytest: 1 error in 3.07s (exit 2)
```

Cause: `tests/test_decision_policies.py:3` does `from examples.python.decision_policies
import ...` and neither `examples/` nor `examples/python/` carries `__init__.py`, so
the import resolves only when the repo root is on `sys.path` (`python -m` prepends
cwd; `PYTHONPATH=.` fixes `uv run`). Not edited — read-only per constraints.

Planted-defect RED (/tmp copy only, clone untouched): copied `tests/`, `examples/`,
`README.md` to `/tmp/w70-awesome-jev-red`, planted one defect —
`examples/python/decision_policies.py:29` `if confidence < 0.60:` → `if confidence <
0.61:`. Then `python3 -m unittest discover -s tests -v` in the /tmp copy:

```text
FAIL: test_low_stakes_action_can_run_without_confirmation (test_decision_policies.GateActionTests)
AssertionError: ActionDecision(route='human_review', requires_confirmation=False) != ActionDecision(route='show_balance', requires_confirmation=False)
Ran 11 tests in 0.001s
FAILED (failures=1) (exit 1)
```

11 tests, 1 failure — the suite is able to fail (boundary case `0.60` is exactly what
the defect moves). /tmp copy removed afterwards. `git diff --stat` in the clone still
empty.

## T3 — entry inventory (existence, suite command, N quoted)

"Exists?" = path present in the pinned tree. "Suite?" = the catalogue states a runnable
command for it. "N quoted?" = the catalogue entry text states a Jev number with an N.
Live Jev N=0 throughout; no entry was executed against the API.

| # | Entry (catalogue line) | Exists? | Runnable suite stated? | Jev number + N quoted? | Mark |
|---|---|---|---|---|---|
| 1 | Offline policies + tests (`README.md:417-433`; `examples/python/decision_policies.py`, `tests/test_decision_policies.py`) | YES — all 7 included paths globbed present (`examples/python/quickstart.py`, `workflows.py`, `decision_policies.py`, `examples/typescript/quickstart.ts`, `tests/test_decision_policies.py`, `docs/jev-use-case-playbook.md`, `docs/coding-agent-use-cases.md`, plus `docs/repository-metadata.md`) | YES — `README.md:432` `python -m unittest discover -s tests -v`; pytest runs the same 11 | NO — thresholds (`0.60`/`0.90`, `0.20`, `0.65`, `1.20`) are code-owned policy constants, not Jev measurements; no N claimed | demonstrated (fresh 11/11 + /tmp RED above) |
| 2 | `Anil-matcha/awesome-gpt-6-astra` (`README.md:31`) | Link present; repo NOT opened, NOT cloned (per "do not clone" constraint) | Unknown — not opened | NO Jev number in the blurb | catalogue-only |
| 3 | `Anil-matcha/awesome-agent-apis` (`README.md:32`) | Link present; NOT opened, NOT cloned | Unknown — not opened | NO Jev number in the blurb | catalogue-only |
| 4 | `Anil-matcha/open-business-agents` (`README.md:33`) | Link present; NOT opened, NOT cloned | Unknown — not opened | NO Jev number in the blurb | catalogue-only |
| 5 | `Anil-matcha/awesome-generative-ai-apps` (`README.md:34`) | Link present; NOT opened, NOT cloned | Unknown — not opened | NO Jev number in the blurb | catalogue-only |
| 6 | `SamurAIGPT/llm-wiki-agent` (`README.md:35`) | Link present; NOT opened, NOT cloned | Unknown — not opened | NO Jev number in the blurb | catalogue-only |
| 7 | Live quickstarts (`README.md:77-167`, run `README.md:438` `python examples/python/quickstart.py` / `npx tsx examples/typescript/quickstart.ts`) | YES — both quickstart files exist | YES but KEYED — `README.md:435` "only after setting `TYPESAFE_API_KEY`"; NOT RUN this assignment (no live calls) | EVAL lead (intent refund @ 1.0, urgency 0.96, frustration 0.96, SDK parity) NOT re-run — lead, not a pass | NOT-RUN by profile; file presence [Verified] |
| 8 | Quick-facts snapshot (`README.md:51-66`: alias `jev-latest`, `jev-1.13.0`, `$0.042 / 1M` in / free out, `250,000` tok/s, `1,200` rpm, text-only, `70–500 ms` vendor-reported) | YES — table present; snapshot date `README.md:27` September 18, 2026 | N/A — vendor figures, no suite | Catalogue quotes vendor numbers WITHOUT its own N; `README.md:66` already says treat speed as vendor-reported | partial (snapshot date + vendor caveat in-tree; no live resolution) |

Skips: none — all 8 entries assessed. No entry required a Jev call; zero made.
Non-link entries (18 use-case blurbs `README.md:237-363`, primitives, patterns,
checklist) are prose recipes without out-of-tree existence claims and are covered by
row 1's executable policy core; the topic cap (20, `README.md:443`,
`docs/repository-metadata.md:15-36`) was verified in the prior receipt and unchanged
at this pin.

## T10 — verdict

Result class: **withheld**. None of SELF, FLOOR, or INCUMBENT is earned — this
catalogue scores no labelled rows and T4–T8 are out of profile. N=0 live calls,
cost $0, no p50/p95 latency to report.

RULEBOOK tiers: row 1 [Verified, High] (fresh execution + RED proof); rows 2–6
[Maintainer claim] of the list only (link text present, repos unopened); row 7 file
presence [Verified], live values NOT-RUN; row 8 snapshot [Verified] as text,
vendor numbers [External]-aspirational as measurements.

NO-CLAIM: no Jev accuracy, latency, cost, calibration, or alias resolution was
measured. The 11/11 is an offline stdlib policy suite, not a model result. The five
related-project blurbs are not certified (repos never opened). Do not cite
`EVAL.md:39-42` quickstart numbers as re-verified.

Earned-label fields: not triggered beyond the profile exclusions. T4 NOT-RUN carries
its command-less status above with cause (assignment "No live calls" +
`README.md:435` key requirement) and two routes (class profile table; assignment
text). Rows 2–6 unopened carry cause (assignment "do not clone" + read-only clone
constraint) with routes (1) assignment text, (2) prior receipt's `ls-remote`-only
precedent — no second command run because opening them adds no catalogue verdict.

## Boundary

Clone not edited (`git diff --stat` empty, HEAD still
`d57f5ce8002cc7cadc2c744b34a45933507e0508`). Defect planted only in
`/tmp/w70-awesome-jev-red` (removed). `EVAL.md` not edited. No live Jev call, no
`infisical` run, no key printed, nothing cloned or fetched. Re-run from
`/Users/josh/Developer/jev`: `python3 -m unittest discover -s tests` with cwd
`upstream/Anil-matcha/awesome-jev-by-typesafe` (expect `OK`, 11 tests); RED proof:
copy `tests/`+`examples/` to /tmp, flip `0.60`→`0.61` at
`examples/python/decision_policies.py:29` in the copy, re-run (expect 1 failure).

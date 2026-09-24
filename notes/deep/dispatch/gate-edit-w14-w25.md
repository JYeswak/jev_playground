# Gate-edit session (`KIT_GATE_EDIT=1`) - W1.4 kit-guard rebuild, then W2.5 pre-commit canary

From pane 1 AmberWillow, 2026-09-24. Plan `docs/PLAN-DEEP-KIT-20260922.md` W1.4 (line 198), W2.5
(line 300), Appendix D item 1. Parent bead `jev-deep-kit-8q7`.

## 1. Mission and authority

Validate Jev -> build tools -> liven omp surfaces -> dogfood -> share (AGENTS.md "THE MISSION").
The kit guard is the omp surface that keeps every pane from editing the gates that judge it.

Joshua, 2026-09-24, on the escalation "a `KIT_GATE_EDIT=1` omp session for W1.4 and W2.5": *"approval
on all"*. This pane was launched with `KIT_GATE_EDIT=1` for that purpose only. It edits the guard,
its config, its tests, and `githooks/pre-commit`; nothing else. When both units are done it exits,
and no other session is launched with the flag.

Confirm first: your session start printed `kit-guard: gate files WRITABLE (KIT_GATE_EDIT=1)`. If it
did not, stop and call back.

## 2. W1.4 - config-driven guard (do this first)

Inputs:
- Installed guard: `.omp/extensions/kit-guard/{index,policy}.ts` (from `omp-kit (1).zip`, sha256
  prefix `cea66f8bcb616737`, unmodified since install `572e3eb`).
- Kit's own tests: `/tmp/jev-intake/omp-kit-zip/omp-kit/tests/kit-guard.test.ts` (39 tests).
- Layout table: `notes/deep/kit-guard-jev-cases.tsv` (32 rows, columns `expect ... regex_responsible`).
  Findings: `notes/deep/omp-kit-findings.md` (10 of 14 layout rows mismatch on the installed function;
  each row names the regex responsible). Harness pane 2 used: `/tmp/jev-rc-p1/w13/run.mjs`.

Build, per plan W1.4:
1. New `.omp/kit-guard.json`: `gatePaths`, `hookDir` (resolved from `git config --get core.hooksPath`
   at session start; here it is `githooks`, no leading dot), `requiredPatterns`, `reanchorFiles`,
   `readOnlyBashAllow`. `readOnlyBashAllow` exempts `git config --get` and `git config --list`.
   `gatePaths` includes `foundation/gates.sh`, `foundation/gates.d/*`, `foundation/gates.d/*.exemptions`,
   `githooks/*`, `.omp/config.yml`, `.omp/rules/kit-*.md`, `.omp/extensions/kit-guard/*`, and
   **`.omp/kit-guard.json` itself** (otherwise an agent can widen its own allowlist).
2. `policy.ts`/`index.ts` read that config; the hardcoded lists go. Keep the `KIT_GATE_EDIT` switch
   and the fail-closed behaviour on a missing or malformed config (block and say why, never allow).
3. Port the kit's tests into the tree (e.g. `.omp/extensions/kit-guard/kit-guard.test.ts`), keeping the
   ones that apply, and add the W1.3 rows as table cases. Write expectations from the repo layout,
   not from the new regex.

Acceptance (all, pasted into the callback):
- the W1.3 table at **0 mismatches**, run from the committed test file;
- `bun test` green on the port, with any kit test you dropped named with its reason;
- the config lists its own path;
- a **planted** edit to `.omp/kit-guard.json` from a session WITHOUT the flag is blocked: prove it
  with a fresh `omp --mode=rpc --max-time=60` session from the repo root (no `KIT_GATE_EDIT`), one
  prompt asking for a one-line write to `.omp/kit-guard.json`, and paste the blocked toolResult;
- the healthy path is silent: the same fresh session can write `notes/deep/x.md` (then remove only
  the file it created, via the tool, and say so).

Do not move the `br close` check into `bashVerdict`. The TTSR rule `kit-close-needs-evidence` was fixed
on 2026-09-24 to wait for the complete command (selftest 124/124); a second enforcement point would
need its own RED arms.

## 3. W2.5 - pre-commit canary (after W1.4 lands)

`githooks/pre-commit` already has lane 0 (one main, one worktree). Add a new lane before the real
checks (name it `lane 0b: claim-discipline canary`; do not renumber the others). It runs
`foundation/kit/check-claim-discipline.sh` against a canary false claim and requires RED before any
real check runs. If the checker is absent or not executable, the hook fails closed with a one-line
reason. Origin: frankentui (CHECKLIST B5).

Acceptance: both directions in a throwaway clone (`git clone --local` into `mktemp -d`, never a
worktree). (a) Normal commit passes. (b) With the canary sabotaged so the checker says GREEN on the
false claim, the commit is refused. (c) With the checker removed, the commit is refused. Paste each
run's hook output. `foundation/gates.sh` stays 17/17.

## 4. Rules

AGENTS.md binds, including rule 14 (rider). The guard and the hook are not rider-covered, so any
model may do this work. Reserve paths in Agent Mail before editing, stage explicit paths, read back
`git diff --cached --stat`, no amend, push after each commit, and name the verification level in
each subject. Two commits minimum: W1.4, then W2.5.

## 5. Callback

`CALLBACK-GATE-EDIT-DONE` via `ntm send jev --pane=1`: both commits, the acceptance evidence above,
and a NO-CLAIM. Then exit this session (`/exit`) so the flag does not outlive the unit.

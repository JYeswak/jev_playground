# Addendum to p2-wave1 (W1) — from pane 1 AmberWillow, same bead jev-deep-kit-8q7.1

Joshua pointed us at https://omp.sh/docs/ttsr. Rendered copy: /tmp/omp-ttsr-web.md; in-harness twin:
omp://ttsr-injection-lifecycle.md. Facts from it that change your W1 packets:

1. "Project and user rules are discovered when a session starts. Start a new session after adding or
   changing a file." Settings too. So the six kit rules (b947da1, 19:54) and after-gap/0 (572e3eb,
   20:07) are NOT loaded in panes 2-6 (started 2026-09-21). Pane 1 started 20:02:33: it has the rules
   but repeatMode once — and "fired state is saved with the session", so kit-no-verify has already
   fired once on pane 1 tonight and is now silent there. Put both in W1.1.
2. Use the native harness for W1.3: `omp ttsr test --json --rule <file> --source tool --tool bash '<cmd>'`
   and `--source tool --tool edit --path <p>`; `--verbose` explains non-matches; and run
   `omp ttsr scan --rule .omp/rules/kit-test-skip.md .` (the docs: scan before enabling a broad rule)
   — report how many existing tree files each kit rule would match (vendored clones' tests included).
3. New must-block rows for W1.3: `ttsr.disabledRules` is the documented off switch, so an edit to
   `.omp/config.yml` adding a kit rule to disabledRules, and any edit/delete of `.omp/rules/kit-*.md`,
   are gate weakening. kit-guard protects neither today. Add both.

## Two RED stages that are yours (found running foundation/gates.sh at 33fe6ae: 14 PASS, 3 RED)

Stage 80 (lane-instrument-selftests) is RED on two TTSR instruments:
- `bash scripts/selftest-ttsr-rules.sh` -> 92 ok, 1 FAIL: "12 project rules but only 6 are tested — add
  arms for the new one". The six kit rules landed without arms. Stage 80 has been red since b947da1.
- `bash scripts/selftest-ttsr-assert-disabled.sh` -> 3 ok, 2 FAIL: "GREEN: absence-from-one-probe exit=1
  (still present — disable did not take)". REFUTED hypothesis (pane 1, measured): the project `ttsr:`
  block does not clobber profile disabledRules — from the jev root `omp --profile grok ttsr list` still
  hides absence-from-one-probe and `--profile muse` still hides bash-structural-def-search. Find the
  real cause; write the refutation into NEGATIVE_EVIDENCE.md with a retry predicate.
Diagnose both in W1 Part A (measurement). Fixing selftest-ttsr-rules means writing hit+miss arms for
the six kit rules — that IS W1.3's case table; land the arms from your table, not a second list.
Also: 572e3eb deleted the comment line anchoring the jev-screen note in .omp/config.yml (two `#`
lines now sit orphaned under `- ./.omp/extensions/kit-guard`). Note it in omp-kit-findings.md.

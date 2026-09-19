# Installer grade: RED/GREEN/GREEN, plus one reproducible defect (inline list)

Pane 3 (muse, non-author of the installer), 2026-09-19. Throwaway `OMP_HOME`
only (`/tmp/p3test`, `/tmp/p3test2`); no real profile touched.

## Step 1 — exit codes (fixture: config.yml with `extensions: []`)

```
install-harm-rule.sh --check tp   -> exit 1 (RED, nothing installed)
install-harm-rule.sh tp            -> exit 0 (GREEN)
install-harm-rule.sh --check tp    -> exit 0 (GREEN)
```

## Step 2 — third defect found (not fixed, per unit)

**Inline `extensions: []` produces unparseable YAML while reporting GREEN.**
The installer appends `  - harm-rule` after the inline line, yielding:

```yaml
extensions: []
  - harm-rule
```

Python yaml.safe_load dies on it (`ParserError: expected <block end>, but
found '<block sequence start>'`). Any omp run on that profile now fails config
load — worse than silent non-registration — and `--check` still exits 0
because it greps for the string rather than parsing the YAML. Reproduce with
the commands above (fixture profile `tp`). The no-`extensions:`-key arm works
(clean block appended, parses, lists `['harm-rule']`). Re-run over an existing
install exits 0 (idempotent path not fully exercised beyond that). Read-only
extensions dir NOT tried (left for the fixer; stated).

Suggested direction (not a patch): parse, don't append — or refuse inline
forms loudly. The `--check` should validate YAML structure, not grep text.

## Step 3 — observe-only grep (from the brief)

`grep -cE '\b(block|deny|abort|reject)\b' work/omp-harm-rule/harm-rule.ts`
returns **0** — confirmed. (Caveat the README should probably carry: the file
contains the SUBSTRING "block" inside "blocking" in comments, so a substring
grep without `\b` fires; the word-boundary form is the correct proof.)

## NO-CLAIM

Arms tried: fresh profile, re-run, no-key config, inline-empty config.
Not tried: read-only dir, rollback-after-double-run, non-UTF8 config,
Windows line endings. Real-profile installs: none, by unit order.

## Round 2 — five breakage arms, no fourth defect (pane 3, fixed installer)

All exit codes taken UNPIPED. Fixture profiles under /tmp (OMP_HOME), never
real. Baseline on block-form config: install 0.

1. read-only extensions dir: exit 1, LOUD (cp fails), config unmodified, no
   duplicate entry. Clean.
2. double-run then single rollback: pristine config restored byte-identical,
   file gone, --check RED (1). The kept-pristine-.bak fix holds. Clean.
3. `extensions:` key present but EMPTY: proper block item appended, parses,
   `['harm-rule']`, exit 0. Clean.
4. preexisting harm-rule.ts, unlisted: old content preserved to
   harm-rule.ts.bak, new installed, exit 0. Clean.
5. commented `# - harm-rule`: correctly ignored (not matched as installed),
   real entry appended once, parses to one item. Clean.

"No fourth defect found in the five arms tried." Remaining uncovered (stated,
not attempted): non-UTF8 config, Windows line endings, concurrent installs,
real profiles.

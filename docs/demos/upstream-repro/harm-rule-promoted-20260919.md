# Harm rule promoted to codex: rollback first, evidence after

Pane 3 (muse), 2026-09-19. ONE working profile only (`codex`); claude and
`~/.omp/agent/extensions` untouched. Observe-only: no model call, no network,
returns undefined on every path (proven below, not asserted).

## ROLLBACK (written before registering; tested after)

Remove the registration line (restores the backed-up config verbatim):

```bash
cp /tmp/codex-config-backup.yml ~/.omp/profiles/codex/agent/config.yml
```

Remove the deployed file:

```bash
rm ~/.omp/profiles/codex/agent/extensions/omp-harm-rule.ts
```

Config backup: `/tmp/codex-config-backup.yml` (taken before any edit).
If ANY session errors after registration, run both commands and report
ROLLED-BACK — that outcome is a success for this unit, not a failure.

## Pre-promotion three checks (exact bytes under test)

Source: `work/omp-harm-rule/harm-rule.ts` (classify byte-identical to
c5966a5, re-verified by empty diff at promotion time). Stub-pi probe
(tsx import, six hostile inputs):

- (a) returns undefined on every path: normal bash, undefined event, null
  event, missing input, non-bash tool, throwing store — all `null`
  (JSON for undefined), zero exceptions escaped.
- (b) never throws: including a store whose appendEntry always rejects.
- (c) fires: decision row written for the chmod probe command.

## Post-registration evidence (codex, working profile)

First contact, driven probe (`echo codex-probe-1` + `chmod -R 777
/etc/nonexistent-path-xyz`, both safe): session
`--private-tmp--/2026-09-19T19-33-49` holds 5 harm-rule rows (diagnostics +
harm_pass + harm_fire) and 2 dcg-bridge rows — co-presence in a working
profile on the first try. Session file: 20 rows, 0 unparseable, agent_end
reached, zero errors. No rollback needed. Longer-lived pane traffic still to
be observed; this receipt covers first contact only.

## NO-CLAIM (promotion)

One profile, our own traffic (one driven probe so far), observe-only — this
is not evidence the rule is correct for other users or other workloads, and
not evidence about sustained multi-pane traffic. The rollback above stays
valid for the life of this registration.

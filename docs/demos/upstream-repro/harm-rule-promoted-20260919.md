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

## P3-28 appendix — re-promoted with harm_error fix (pane 3, 2026-09-19)

## ROLLBACK (written before touching anything; backup taken first)

Deployed bytes before swap: `3d519b84bd8a848a`, backed up to
`/tmp/codex-harmrule-backup.ts`. Restore verbatim, no re-derivation:

```bash
cp /tmp/codex-harmrule-backup.ts ~/.omp/profiles/codex/agent/extensions/omp-harm-rule.ts
```

Config untouched (registration by absolute path already works; pane 2 is
separately checking the installer's bare-name form — not this unit).

Repo bytes under test: `5526284ef873299f` (harm_error fix + DI seam;
classify byte-identical to c5966a5, re-verified at swap time).

## Post-swap proof (same session)

`--private-tmp--/2026-09-19T23-01-52`: 2 harm rows (harm_pass echo
reswap-probe, harm_fire chmod) + 2 dcg-bridge rows — the extension fires
with the new bytes, and a known-firing neighbour (bridge) wrote in the same
session, so this is verified against activity, not silence. Rollback
untried-but-ready (nothing errored). NO-CLAIM: the swap changes no published
number, re-runs no head-to-head, and promoted stays 0 in the ledger.

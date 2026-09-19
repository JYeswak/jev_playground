# Upstream report: franken-harvest has no oracle domain for Jev

**Target:** the `fh oracles` catalogue, embedded in franken-harvest rather than in this repo
**Found by:** pane 2 (`WindyJaguar`) claiming `jev-route-jev-oracle-row-7ou`
**Independently confirmed by:** pane 1 (conductor), through a *different instrument* — the
franken-harvest MCP surface rather than the CLI
**Status:** reported for owner routing. Nothing was handrolled locally.

## What pane 2 measured, through the CLI

```
fh oracles --json                  rc=0, 18 domains
fh oracles --domain jev            rc=4  ORACLE_DOMAIN_UNKNOWN
fh oracles --domain system_one     rc=4  ORACLE_DOMAIN_UNKNOWN
```

## What the MCP surface returns, independently

A lexical search for `jev system one oracle domain typesafe` over the loaded corpus — 306 indexed
ledger rows, 178 technical sources, 207 doc repositories — returns **no authoritative Jev oracle
row**. It reports 4,160 lexical hits, and the top-ranked result scores **0.031**: every one of the
eight returned rows is an unrelated digest-domain constant
(`fss.ledger_oracle_history.v1`, `rabs.system-context.sha256.v1`,
`org.frankensim...base-e2e-oracle-manifest.v1`) or an "Oracle" subagent system prompt in
`pi_agent_rust`. None of them is a judgment-model oracle domain.

Two instruments, two code paths, same answer. That is worth more than either alone, and it is why
this is filed as an absence rather than as a lookup failure.

## Consequence for this lane

This lane names its oracle in every claim, per `AGENTS.md`. For the judgment-model calls there is no
catalogue domain to name, so the oracle is cited inline as the session logs plus the price table, or
as the vendored contract files read read-only. That is honest but unregistered, and it means a third
party cannot resolve our oracle through `fh`.

**Not handrolled deliberately.** Writing a local `oracles.tsv` row would make `fh --domain jev`
resolve on this machine and nowhere else, which is the host-dependent-green defect this lane
measured twice today in other tools. An unregistered oracle that says so is better than a registered
one that exists only here.

## Non-claims

- No claim about the 18 existing domains' contents; only the two lookups above were run.
- No claim that a Jev domain *should* exist; that is the catalogue owner's call, and this report
  exists to route the question rather than answer it.
- The MCP corpus reports `ledger_age_hours` of about 235, so the absence is established against a
  snapshot roughly ten days old rather than against the live catalogue.

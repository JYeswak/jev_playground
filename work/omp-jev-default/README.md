# omp-jev-default

Observe-only scorer for **preselected defaults**. Presence of a default
(`defaultChecked`, `defaultValue`, `defaultSelected`, `pre-tick`,
`selected: true`) is a regex and is the only gate: no preselection, no row.
The remainder asks one noul:

> Does this default serve the client, or the vendor?

```bash
# not registered. do not copy into ~/.omp (repo-relative jev-client import).
node --experimental-strip-types --test work/omp-jev-default/test/
```

## Why this one calls Jev

Finding a pre-tick is a regex. Whether it remembers the client's last account
or opts them into partner offers is a judgement the regex cannot make.

## Stop-condition

If every pre-tick is labelled bad, this is a linter: drop Jev. If
`serves_client` is constant at 0.5 on the remainder fixtures, cut the question.

## Decision rows

| kind | meaning |
|---|---|
| `default_scored` | Jev answered; `probabilities` present |
| `default_error` | key unset, transport failed, or a 200 with no probabilities |

Never blocks. Never throws into the host. Returns `undefined` on every path.

## NO-CLAIM

Offline tests only. No live accuracy. Not dogfooded. Not promoted.

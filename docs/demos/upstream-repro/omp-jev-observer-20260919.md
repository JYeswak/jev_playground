# OMP Jev observer — offline proof receipt

**Unit:** P2-13
**Commit:** pending at authoring time
**Surface:** `tool_call` for `bash`

## Contract

`work/omp-jev-observer/src/observer.mjs` installs an observe-only `tool_call` handler. It returns
`undefined` on every path, including disabled, non-bash, DCG-blocked, Jev-error, timeout, logger
failure, and unexpected-error paths. It never returns OMP's `{ block: true, reason }` shape.

The handler asks the injected Jev classifier only after the injected DCG verdict is `allow` or
`unknown`; a `block` verdict is skipped. The default classifier makes one HTTP POST to
`JEV_OBSERVER_ENDPOINT` per eligible bash call, with a 750 ms timeout. Timeout is logged as the
decision error; it is not retried. The decision record carries a stable decision ID, DCG verdict,
question set, probabilities, latency, cost, and error field. Persistence uses OMP's `appendEntry`
when installed and remains fail-open.

## Disable switch

Set `OMP_JEV_OBSERVER_DISABLED=1` without editing code. The default install path treats all other
values as enabled. `JEV_OBSERVER_ENDPOINT` configures the classifier endpoint; an absent endpoint is
an observed configuration error, not a host error.

## Offline proof

```text
node --test work/omp-jev-observer/test/observer.test.mjs
5 tests passed
```

The synthetic `tool_call` event proves `undefined` on classifier success, classifier error, and
classifier timeout. It also proves DCG blocks are skipped and the disable switch is inert.

## Registration command — deliberately UNRUN

```bash
cp work/omp-jev-observer/src/observer.mjs ~/.omp/omp-extensions/omp-jev-observer.mjs
```

This command was not run. No file under `~/.omp` was modified by this unit. Registration requires
human review because an extension load or hook error can affect every tool call in the fleet.

## NO-CLAIM

This extension has **not been registered**, has captured **no live traffic**, and has not been
exercised by a live omp session. Offline tests prove only the synthetic event contract and logger
boundary.

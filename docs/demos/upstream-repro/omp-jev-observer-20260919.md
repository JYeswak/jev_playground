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

## NO-CLAIM AT P2-13 CLOSE

At the P2-13 close this extension had not been registered and had captured no live traffic. P2-15
later registered only the disposable jev-lab copy and added the live evidence below; no Joshua
working profile was modified.

## P2-15 live defect and repair

The initial live attempt produced no observer rows. A minimal registered extension proved the loader and the live event shape: OMP emits nested bash events with event.toolName=\"bash\" and event.input.command; the outer model-facing tool is eval. The observer entrypoint was replaced with a direct registered handler and safe append boundary. It now records the raw event diagnostic first, then always appends a decision record for eligible allow/unknown bash calls when the endpoint is unset or unreachable.

Live commands and evidence:

~~~text
omp --profile=jev-lab --no-extensions --extension=/Users/josh/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts -p 'run exactly: echo observer-minimal-actual'
omp --profile=jev-lab --no-extensions --extension=/Users/josh/.omp/profiles/jev-lab/agent/extensions/omp-jev-observer.ts -p 'run exactly: echo observer-dead-port'
~~~

Both commands exited 0 and executed real nested bash calls. Session JSONL evidence:

~~~text
/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T18-34-35-060Z_01a0baf2-e2b4-75dc-85ca-2dbac80a5889.jsonl
  com.zeststream.omp-jev-observer.diagnostic.v1
  com.zeststream.omp-jev-observer.decision.v1
  error: Error: JEV_OBSERVER_ENDPOINT is not configured

/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T18-35-05-970Z_01a0baf3-5b72-71f8-9afd-90ee0a8cdb47.jsonl
  com.zeststream.omp-jev-observer.diagnostic.v1
  com.zeststream.omp-jev-observer.decision.v1
  error: TypeError: Unable to connect. Is the computer able to access the url?
~~~

The loader was independently proven with a minimal registered .ts extension, emitting minimal_tool_call_marker for both outer eval and nested bash events. No other profile was modified; the tested profile was ~/.omp/profiles/jev-lab.

## NO-CLAIM

Live traffic was produced by OMP agent openai-codex/gpt-5.6-luna (outer eval, nested bash), not by a Claude or Codex CLI profile and not by a live Joshua pane. This proves the disposable jev-lab path and failure logging only; it does not claim live Jev-model quality, production calibration, or registration into any claude/codex working profile.

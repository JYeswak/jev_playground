# omp-jev-preaction

Observe-only omp extension. Logs when a bash command matches the deterministic
wipe / format / forkbomb patterns from the measured `preaction-abstention`
policy. Does **not** call Jev and does **not** block (dcg remains the blocker).

## Install

```sh
omp plugin install /Users/josh/Developer/jev/work/omp-jev-preaction
# or one-shot:
omp --extension /Users/josh/Developer/jev/work/omp-jev-preaction/src/index.ts
```

## Pattern source

`demos/preaction-abstention/policy.json` — seven regexes, pre-registered 2026-09-18.

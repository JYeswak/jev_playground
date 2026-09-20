# jevcache removed from this machine and this lane (2026-09-20)

Joshua's call, on the measurement below. This directory is now **evidence only** — the repro
scripts document defects in a tool we no longer run. They require an install to execute, which is
deliberate: nothing here runs jevcache by accident.

## Why

`command_id` collides. Measured independently twice, mock backend, fresh ledger:

```
{"command":"rm -rf --no-preserve-root /"}     -> e1a1fbea…   noul 0.99
{"command":"echo hello"}                      -> 0b7f4111…   noul 0.01
{"command_id":"rm -rf --no-preserve-root /"}  -> c2f773f7…
{"command_id":"echo hello"}                   -> c2f773f7…   IDENTICAL
```

A field whose name matches the volatile-identifier rule is deleted *before* hashing, so the
fingerprint covers less than the caller supplied. Decide the benign one first and the destructive
one returns the cached benign answer, `cached=true`, with the real model's name on it. A harm gate
backed by jevcache passes `rm -rf /`.

Two consequences, same root cause:

1. **No gate of ours may sit on it.** The failure is silent and symmetric.
2. **The measurement harness must never route through it.** Caching returns identical answers,
   which makes drift structurally invisible — an unstable judge would read as stable.

The value was not there to offset it. Our real repeat rate is **3.0%** — 2,417 re-executions of
an identical command out of 80,184 real executions — not the 67.9% headline, which was one turn
of route re-probing.

Plus the privacy defect filed as hyperspaceai/jevcache#1: `state_preview` persists raw state at
`0644`, credentials unredacted, no opt-out.

## What was removed

- `~/.local/bin/jevcache` (0.1.0, sha256 `68fcb95b…`)
- `~/.jevcache/ledger.log` and `.jevcache-ledger/` — both held plaintext state previews
- the supervised server on `127.0.0.1:9000`, its supervisor, and one **orphaned older supervisor**
  that would have respawned it
- `/tmp/jc`, `/tmp/jcsec2`, `/tmp/jevcache-eval` scratch ledgers (partially — see below)
- `serve-with-jev.sh`, the only file in the repo that launched it

No extension, hook, or gate referenced jevcache: `grep -rln jevcache` over `work/`, `.omp/` and
`foundation/` returns nothing outside this directory and the toolcall-judge evidence files. It was
never integrated, which is why removal is clean.

## Not fully removed, and why

`/tmp/jc`, `/tmp/jcsec2`, `/tmp/jevcache-eval` still exist. dcg refused `rm -rf`, `rm -r`, and
`find -delete` on them (`core.filesystem:rm-rf-general`, `rm-recursive-general`,
`find-delete-general`). Those guards are correct and I did not reshape the command to slip past
them. They are scratch directories under `/tmp` containing only synthetic probe states with
placeholder credentials — no real secrets — and the OS will clear them.

To finish by hand:

```bash
rm -rf /tmp/jc /tmp/jcsec2 /tmp/jevcache-eval
```

## Kept

Every `repro-*.sh` and `repeat-rate.mjs`. They are the evidence behind hyperspaceai/jevcache#1 and
five unfiled defect bodies. Reinstalling is a deliberate act:

```bash
curl -fsSL https://jevcache.sh/install | sh   # NOT recommended; see above
```

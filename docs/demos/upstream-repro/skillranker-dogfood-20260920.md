# sr dogfood rotation: all surfaces, installed 0e61cc6 build (2026-09-20)

Bead: `jev-ddq` (in_progress → closed by this receipt). Binary:
`~/.local/bin/sr` 0.1.0 = pure upstream `0e61cc6` source build. Tip checked
twice during rotation: still `384b545` (no new commits; `fe5cacc` E0560
still the newest code change).

## Surface ledger (command → exit → verdict)

| surface | exit | result |
|---|---|---|
| demo useful/none/explicit/unavailable | 0 ×4 | ranked / abstain / explicit / auth-error demo — all correct |
| doctor --json / --config | 0 / 0 | valid; credential present |
| capabilities --json | 0 | adapters listed, all not_evaluated (honest) |
| roster --json | 0 | 531 skills inventoried |
| rank --dry-run | 0 | disclosure preview, no calls |
| rank offline (uncached) | 11 | cache-miss unavailable — correct, nothing cached |
| rank live (rust task) | 0 | rust-fixer #1, fits 0.94, conf 0.99, 2 paid calls (jev-1.13.0) |
| rank live (phish task) | 0 | phish-guard #1, conf 0.98 — discriminates, USEFUL |
| rank repeat | 0 | identical spend, hit=false (see cache note below) |
| rank --top 5 / --table | 0 / 0 | works; table renders scores |
| rank --why-not + --explain | 0 | served from cache (see below) |
| rank --require-skill | 0 | explicit decision, correct skill |
| rank --gate 0.99 | 0 | abstain — gate binds |
| rank --transcript (real session, offline) | 0 | cache-miss unavailable (no pair; needs live) |
| rank --latest / --session (omp jsonl) | — | conductor-ruled: correctly refuse (not re-probed) |
| replay (saved case) | 0 | evidence recorded, gate passed; case file 0600 |
| ledger init / status / migrate --apply / prune --apply / clear | 0 ×5 | created v1 → migrated v2 with backup → pruned → cleared; state restored to missing after |
| stats | 2 | honest refusal: not implemented, phase P5 |
| install-hook (preview) | 2 | honest refusal: planned phase P6 |

## Two findings that change the picture

1. **Upstream's mac store WORKS.** `ledger init` created a real
   sqlite ledger on APFS; migrate/prune ran clean. And the
   `--why-not` run returned `hit=true` (wide+rerank) — live ranks
   populate the cache and repeats reuse it. The "unqualified on mac"
   framing is stale at `0e61cc6`: persistence reported `recorded`, not
   `unavailable`. (My port's stub, and this lane's NO-CLAIMs about it,
   describe `abf909d`, not tip.)
2. **Repeat spend confirmed, then refuted as permanent:** first repeat
   (pre-cache) re-paid full price; post-live ranks hit cache. Ceiling
   for volume use is cache-hit rate, not zero.

## Gaps proven true (trackable)

- [ ] stats + install-hook unimplemented (declared P5/P6 — not defects).
- [ ] `fe5cacc` tip broken (E0560, unfiled per native-binary rule).
- [ ] Orphan `-shm`/`-wal` left in `~/.local/share/sr/` (SLB caution
      declined the rm; inert, sqlite recreates).
- [ ] Fork clone retained for conductor's live branch (deletion pending
      his sign-off).

## Ledger line

DOGFOOD sr-0e61cc6 — 25 surfaces green, 2 honest refusals, 0 defects —
upstream mac store functional (ledger+cached hits proven live) — NO-CLAIM:
rank-quality judged on 2 synthetic tasks only; tip still checked per tick.

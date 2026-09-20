# A11 mail→cass join — pre-registered falsifier `[pending]`

Committed BEFORE scoring (rule 3, `docs/RULES.md`). The scoring script
`work/cass-mail-mines/scripts/score_a11_join.py` does not exist yet at this
commit; any number it later prints was frozen against these lines first.

## Join keys (A11 card order)

- **K1** `mail.projects.human_key` ↔ `cass.workspaces.path`
- **K2** `mail.messages.thread_id` ↔ cass conversation `external_id`/`title` token
- **K3** `mail.file_reservations` (`project human_key` + `path_pattern`) ↔
  cass conversation workspace + repo-relative file (via `snippets.file_path`
  where present; `snippets` introspected at n=0)

## Normalization (frozen, no tuning after results)

- Strip trailing `/` only. Case-sensitive. No symlink resolution
  (`/private/tmp/X` joins only `/private/tmp/X`, never `/tmp/X`).
- K2/K3 co-presence window: ±24h. Id-join additionally requires shared bead
  id or shared reserved path — co-presence alone is not Y.

## What kills it

- **F1:** K1 exact-match id-join count = 0 → K1 REFUSED (UNMEASURED for
  project-key joins; both-cards stay PREPARED-NOT-MEASURED on this key).
- **F2:** id-join = 0 on all three keys → whole mine REFUSE (UNMEASURED,
  not yield-0). Dead stores are not evidence of no chatter.
- **F3 (cheap-wins):** K1 exact-match captures every id-join found AND joins
  zero plant pairs → HELD for Jev (local exact-match suffices; no model
  seat). The yield number itself is still reported.
- **F4 (plant RED):** exact-match joins any two distinct `/private/tmp/*`
  dirs, or two same-basename different-parent paths → cheap rule RED → that
  key HELD as unsafe, must tighten, no Jev either.

## Plant subsets (named, adversarial)

- P1: distinct `/private/tmp/<different>` mail projects must never join each
  other or a cass workspace of a different dir.
- P2: same-basename different-parent paths (e.g. two `jev` checkouts) must
  not join.
- P3 (card plant): two panes, one tmux session, different project paths →
  must not join.

## Outcome words

DONE = yield printed with exact denominator per key. HELD = F3 or F4 fires.
REFUSE = F1 (per-key) or F2 (whole mine). Aggregate-only claims are not
scored here — the yield table IS the breakdown.

## NO-CLAIM

Live DBs, monotonic, not snapshots: mail n=6510 / reservations n=7316 /
cass conversations n=59807 / workspaces n=792 at introspection time.
`cass search` unavailable (index-busy, repair in flight); sqlite read-only
only, no second rebuild started. Export carries ids/counts/paths only —
no `body_md`, no subject text (secret-scan before git).

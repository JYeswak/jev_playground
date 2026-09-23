# Kit drive

Joshua, 2026-09-23, ordered panes 2-5 to apply `/Users/josh/Downloads/franken-assessments-44-v8.zip` to this repo from the ground up, challenge each other, and callback pane 1 by `ntm send`. This file is the orchestration record. A callback that is not written here did not update the drive.

## What we are accomplishing

A stranger can see which parts of the assessment pack are actually enforced in this repo, and which zip checkers were refused because they do not fail on a planted bad input. The product is the enforced slice, not a copy of the zip.

## What is already true

- v8 `RULEBOOK.md` and `starter-kit/` are byte-identical to v7. The v8 delta is `shareable/` pages, including a site copy of the packets. Measured by comparing `/tmp/jev-rc-p1/fa44` and `/tmp/jev-rc-p1/fa48`.
- `init.sh` was not run. It would install a second pre-commit hook.
- `cef0e02` ports the claim checker. On this `/bin/sh`, the zip checker cannot see an `enforce=yes` row. The port can. One README claim is enforced: the official SDK call.
- `a53190f` ports the readiness checker. A relative path is resolved against an explicit root, not the caller cwd. A sign-off that only says "design" is refused.
- `foundation/kit/packet.md` is a draft, not a sign-off. Three false sentences from `notes/foundation-packet-p5.md` were not adopted: a host `CALIBRATION.md` does not name, score-path `118180e`, and a stage count of sixteen. Recount after `a53190f`: 16 stage scripts plus `44-native-surface.exemptions`.
- Jev cron lines were removed. The omp-orchestrator wake and the 06:00 uds job were left.

## Beads

Parent `jev-v8-kit-drive-m0e`, created_by RedMaple.

| Pane | Mail | Bead | Writes | Does not touch |
|---|---|---|---|---|
| 2 | TopazRaven | `jev-v8-kit-drive-m0e.1` | `notes/v8-checker-challenge.md` | `foundation/kit/` |
| 3 | MistyTurtle | `jev-v8-kit-drive-m0e.2` | `foundation/kit/demotion-rules.md`, `foundation/kit/check-demotion.sh`, `foundation/gates.d/17-kit-demotion.sh` | the two checkers and `packet.md` |
| 4 | SunnyTiger | `jev-v8-kit-drive-m0e.3` | `notes/kit-gap-v8.tsv` | `foundation/kit/` |
| 5 | QuietHarbor | `jev-v8-kit-drive-m0e.4` | `notes/packet-numbers-p5.tsv` | the packet |

Callback shape: `ntm send jev --pane=1 --file=...` with `CALLBACK-P<N>-<bead>-DONE`, the artifact path, and a NO-CLAIM. Mail the sibling you are challenging in the same turn. Do not sit idle after the callback; start the challenge read of the sibling artifact if it exists, and say so in the callback.

## Callback log

2026-09-23T01:40Z CALLBACK-P5-jev-v8-kit-drive-m0e.4-DONE. Artifact notes/packet-numbers-p5.tsv, 16 rows, 16 MATCH, 0 MISS. Re-opened: v1 receipt ece is 0.0613 and brier is 0.0199; CALIBRATION.md rounds those to 0.061 and 0.020. The packet cites the rounded doc, so MATCH against CALIBRATION.md holds. It is not an exact receipt quote. Bead not closed: section numbers and the date parts were not separate rows. NO-CLAIM stands: opened numbers are not a sign-off.
notes/kit-gap-v8.tsv was defective on first read (B7/B8 duplicated, B13/B14 absent). Superseded by the 01:42Z recount: 28 unique ids. foundation/gates.d/17-kit-demotion.sh --selftest exited 0 and named the plant. notes/v8-checker-challenge.md is not on disk.
2026-09-23T01:42Z CALLBACK-P3-jev-v8-kit-drive-m0e.2-DONE. Commit 8d99b9d, three paths, bead closed. Stage 17 --selftest re-run here exited 0 and named the plant. Real registry held official-sdk. NO-CLAIM stands: a green selftest is not a production demotion. notes/v8-checker-challenge.md still absent, so pane 3's challenge of pane 2 is not owed yet.
2026-09-23T01:42Z CALLBACK-P4-jev-v8-kit-drive-m0e.3-DONE. notes/kit-gap-v8.tsv now has 28 unique ids, A1-B14, 13 HAVE / 12 PARTIAL / 3 GAP (B11, B12, B13). The earlier duplicate B7/B8 read is stale. Their claim that notes/packet-numbers-p5.tsv does not exist is false; that file is on disk with 16 MATCH rows. Bead m0e.3 left in_progress until they read it.
2026-09-23T01:45Z CALLBACK-P4-TSV-IDS-UNIQUE. md5 49819948f43c99c335529168987b13df matches the file on disk. 28 unique ids. No edit required. B13 and B14 remain GAP with NONE. Bead m0e.3 still open until they read notes/packet-numbers-p5.tsv.
ntm send reached panes 2, 3, 4, and 5 (exit 0, 2026-09-23T01:29Z). Mail reached TopazRaven, MistyTurtle, SunnyTiger, and QuietHarbor.

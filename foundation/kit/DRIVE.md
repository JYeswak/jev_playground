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

None yet.

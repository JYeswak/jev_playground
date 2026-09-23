# Pane 5 (SunnyTiger) — next units after DEPTH-DONE

From pane 1 AmberWillow. Depth rule (`notes/deep/dispatch/DEPTH-DIRECTIVE.md`) still binds. Use
subagents where the units are independent. Mission and commit discipline as in `p5-wave1.md`.

## U1 — track the calibration reproduction (bead `jev-deep-kit-8q7.4`)

`foundation/runs/20260923T024148Z.json` is untracked, so a fresh clone cannot see the result you
reproduced. Commit it on `main` with a `[live]` subject stating N=80, model, ECE 0.062 vs 0.0614,
Brier 0.0194 vs 0.0195, and the lane (Infisical key, SDK venv). Run `bash foundation/gates.d/30-no-secrets.sh`
and `bash foundation/gates.d/20-receipt-freshness.sh` first and paste both exit codes in the commit
body. If either refuses the receipt, stop and report the refusal verbatim.

## U2 — non-author verification of `jev-v8-kit-drive-m0e.3` and `.4` (bead owner: AmberWillow)

I (AmberWillow, claude-opus-5-5) edited both files at `4bd9fe0`, so I cannot be the one who confirms
them. You are a different model and did not write those rows. Try to refute them.

- `.4`: `notes/packet-numbers-p5.tsv` now has 29 rows. I appended 13 at the end: 11 section-ordinal
  rows (2–12), one MISS (`packet.md:112` cites `notes/foundation-packet-p5.md`, which I found
  untracked by three routes: `git ls-files` empty, `git status` shows `??`, `git log --all` has 0
  commits), and one MATCH (the `23` in `packet.md:122` is the UTC day of `a53190f`). Acceptance:
  every numeric token and every 7–9 character hex token in `foundation/kit/packet.md` appears as a
  row, and a MISS quotes the contradicting line. Re-derive the token set yourself with your own
  extraction (do not reuse mine), check each of my 13 rows against its source, and report
  CONFIRMED or REFUTED per row.
- `.3`: `notes/kit-gap-v8.tsv` row B5 now cites `githooks/pre-commit` and says `.git/hooks/*` is
  inert because `core.hooksPath=githooks` (`.git/config:8`). Confirm or refute from git's own
  behaviour (e.g. which hook actually runs on a commit in a `/tmp` clone), not from the config file
  alone. Acceptance of `.3`: 28 data rows, unique ids, every HAVE or CLOSED row names an existing
  file.

Write `notes/deep/m0e-verify-p5.md` with your commands and outputs.

## U3 — cold read of the README (plan W6.2 acceptance d)

Give a subagent ONLY `README.md` (no other file, no repo access beyond that one file) and ask:
"What is this repository? What do I run first, and what will I see? What did it find? What does it
not claim?" Then check its answers against the tree. Report every place the README misled it, every
dangling reference it could not resolve, and every sentence it read as a claim the README cannot
back. Write `notes/deep/readme-coldread-p5.md`.

Callback: `CALLBACK-P5-NEXT-DONE` via `ntm send jev --pane=1 --file=...` and Agent Mail to AmberWillow.

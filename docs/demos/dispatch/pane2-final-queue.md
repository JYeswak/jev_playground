# P2 — queue of 3

`denominator-sweep.sh` verified here: **8/8 ALL-AGREE unpiped**, and a planted wrong claim makes
the runner exit 1. Two notes from my verification, one of which is a real finding:

- **My planted-drift test produced misleading `rc=127`s** because I copied the script to `/tmp`,
  which re-anchors `$0` and breaks every relative path. That was my artifact, not your bug — but
  it means **the runner is not location-independent**, and a peer who copies it anywhere will get
  eight confident DRIFTs that are all false. Worth a one-line `cd "$(dirname "$0")/.."` guard, or
  an explicit refusal when the expected files are not found. **An eight-false-DRIFT report is
  worse than no report.**
- Deliberately leaving live-harvest unwired was the right call and matches the as-of receipt.

## Unit 1 — make the sweep location-safe, then wire it where it will actually run

Fix the anchoring (or refuse loudly when paths resolve to nothing — an empty scan set is never a
pass). Then decide, with evidence, whether it belongs in `foundation/gates.d/80` via a
`scripts/selftest-denominator-sweep.sh`. **It is currently a runner nobody runs**, which is the
definition this lane uses for process. Either wire it or say in its header that it is hand-run
and why — both are honest, a silent third state is not.

## Unit 2 — close the member-identity gap you flagged

Your own re-sweep receipt says member identity was not diffed: the same **count** can be a
different **set**. Diff the 19 names against the published set and report `SAME SET` or name the
substitutions. You flagged it; close it.

## Unit 3 — then the last unverifiable list

Collect every claim that both audits marked unverifiable into **one** section in
`docs/INTEGRATIONS.md` or the findings page — *numbers a reader cannot verify and neither can
we* — with the reason per line. Short and honest. **Do not build anything to cover them.**

When this queue drains: `br ready`, claim the highest-priority bead you did not author. If the
frontier is still only the blocked epic, take the highest-value artifact you did not write and
review it.

`scripts/vgrep.sh` for proof-greps — it has now caught me five times tonight, twice in the last
hour, including once checking your work. Exit codes unpiped. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

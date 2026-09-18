# DISPATCH — pane 2 · R10 is routed · bead `jev-demo-loop-a1q.4` · 3 units

Your R10 ask is answered: **it is filed as `jev-demo-loop-a1q.4`**, and your dry-queue finding
arrived there independently alongside one of mine. Two paths, one target:

- **Yours** (`735a158`): the shared binary cannot express a **dry queue** — idle-because-finished
  and idle-because-the-packet-ran-out demand opposite responses.
- **Mine** (01:18Z): it reports `IDLE_PROVEN … ACTIONABLE pane=%70`, and `tmux list-panes` proves
  `%70 idx=0 cmd=zsh` — **the user's own shell**, which `tick.md` forbids dispatching. It also
  recommends `uds-ry5d`, a bead from a *different project*.
- **A third, found since:** it reported `WORKING session=jev pane=%73 reason=timer_changed` while
  pane 3 was **idle** — a changing content hash off an animating spinner. That is the fail-open
  direction and the expensive one: false-WORKING kept pane 3 idle while I believed the instrument
  over the artifact.

Three defects, one binary. **Per R10 the remedy is a flag or an upstream bead — never a jev-local
fork.** That fork was already written, measured worse (single-capture `safe_to_dispatch` against
the installed binary's required two captures), and withdrawn.

Also: your audit of my report (`b11aaa5`) was correct on all three qualifications and **all three
are applied** at `3d7725c`. The post-reveal/independent-convergence catch was especially good — it
was a repeat of my own signature error, eleven sections after I corrected it. Thank you for not
softening it.

---

## UNIT 1 — does the binary already have the exclusion? (investigation, read-only)

Do not patch anything yet. Establish what exists:

```bash
~/.local/bin/fleet-idle-monitor --help
strings ~/.local/bin/fleet-idle-monitor | grep -iE 'worker|pane_index|agent_type|zsh|exclude|shell' | head -40
tmux list-panes -a -F '#{pane_id} idx=#{pane_index} sess=#{session_name} cmd=#{pane_current_command}'
```

`cli.js` panes carry an agent and `zsh` panes do not, so `pane_current_command` is a sufficient
discriminator if nothing better is exposed. Report **which** mechanism exists, quoted — a flag, a
filter, an `agent_type` check, or none.

Also find the owning repo so an upstream bead has somewhere to go: the binary is Mach-O, installed
2026-09-04, and both other lanes invoke it. `strings` plus the sibling lanes' repos should name it.

## UNIT 2 — rule on the dry-queue gap, including the right to reject it

The bead's acceptance #5 states the preferred outcome plainly: **the binary cannot know a packet's
unit count, so the dry-queue signal is probably conductor-side state, not a monitor feature.**

Rule on it. If it belongs to the conductor, say so and close that half — a clean out-of-scope
ruling is worth more than an open feature request nobody will build. If you think the binary
*should* carry it, name the input it would need and where that input comes from.

**Do not implement a conductor-side queue tracker.** That is mine, and it needs the tick's packet
format to exist first.

## UNIT 3 — dry-queue default

Unchanged. Highest-value **unreviewed** artifact, non-author only; then oldest satisfiable
`NEGATIVE_EVIDENCE.md` retry condition; then a **QUEUE DRY** callback. Note your last two callbacks
were byte-identical duplicates of one receipt (`735a158` twice) — if the queue is dry a second time
with nothing new considered, say **"QUEUE DRY, unchanged since <sha>"** rather than re-firing the
same row, so I can tell repetition from a fresh pass.

---

## REPLY-VIA — all three legs, per unit

1. `br comments add jev-demo-loop-a1q.4 --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q.4] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. Committed receipt, own files only, verification level in the subject.

Receipt path for units 1–2: `docs/demos/duel-1/runs/r10-monitor-probe-<ISO>.json` (full path,
because a bare filename already cost you two blocked units and that was my defect).

Finish one, fire its callback, then start the next YOURSELF.

## NON-GOALS

No patching the shared binary in place. No jev-local fork — R10 forbids it and the fork was already
measured worse. No conductor-side queue tracker.

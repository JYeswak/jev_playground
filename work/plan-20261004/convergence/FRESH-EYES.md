# Fresh-eyes prompt (give this, and only this, to each background subagent)

Lens agents: dispatch 2-3 subagents with the task tool. Paste the block below verbatim, filling
`<N>` and `<ANGLE>`. Give NO other context: no PACKET.md, no prior findings, no summaries of what we
think is wrong. Each subagent gets a different ANGLE from the list. Merge their rows into your lens
file with `"reviewer":"<you>/fresh-<k>"`, dropping only exact duplicates.

Angles: (a) "would a newcomer be able to build this, bead by bead?", (b) "what will break or lie
in production?", (c) "what does the mission promise that no bead delivers?", (d) "which claims
have no evidence a skeptic would accept?", (e) "what would you cut, and what is missing?".

```
You are reviewing a software project plan you have never seen. Be skeptical; your job is to find
what is wrong, missing, or unprovable, not to praise it.

Repository: /Users/josh/Developer/jev (read-only for you: do not edit files, do not run `br`,
do not call any model API).
Mission: read ROADMAP.md, section "Mission".
The plan is a graph of work items ("beads") in var/agent-tmp/converge/r<N>/issues.jsonl, one JSON
object per line (id, title, status, description, acceptance_criteria, labels, dependencies,
comments). Open items are the plan; closed ones are history.

Your angle: <ANGLE>

Poke holes. For every problem, write one JSON line to stdout or to the file you are told:
{"bead":"<id or NEW>","class":"<short label>","severity":"P0|P1|P2|P3","text":"what is wrong",
"evidence":"file:line, a command and its output, or the bead id and field","fix":"what to change"}
A finding without evidence does not count. If you find nothing, write one line with class "none"
saying what you read and how many items you checked.
```

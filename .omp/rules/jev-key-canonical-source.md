---
condition: 'TYPESAFE_API_KEY|api\.typesafe\.ai'
scope: tool:bash
interruptMode: never
repeatMode: once
---
**The Jev key EXISTS and is in Infisical. Four agents have now reported it missing and all four were wrong** — three recorded in `.env.example`, the fourth on 2026-09-20 off a single probe (`/tmp/.tskey` absent + `$TYPESAFE_API_KEY` unset), which blocked a live test on three panes.

Canonical form, verified 2026-09-20 (`resolved=yes len=107`):

    infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <your command>

Two traps, both measured (`EVAL.md:80-83`, `.env.example`):
- A bare `infisical secrets` from this repo fails because `jev/` has no `.infisical.json`. The message *"run infisical init to connect to a project"* means **UNLINKED DIRECTORY, not MISSING SECRET.**
- brew's `infisical` ≥0.43.111 speaks `/api/v4`; our self-hosted instance serves `/api/v3`. `which -a infisical` must show `~/.local/bin` first (0.43.84). **Decline the 0.43.133 upgrade nag.**

Presence check that never prints the value: `infisical run --projectId=… -- sh -c 'echo len=${#TYPESAFE_API_KEY}'`.

ROUTING rule, not a defect rule: it fires once per session on first contact with the topic and claims no mistake. RETIRE when a 30-day window shows zero false-absence reports.

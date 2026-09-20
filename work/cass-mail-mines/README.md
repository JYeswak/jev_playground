# cass-mail-mines — Studio-first, unpromoted

**Status:** thin runner index. **`promoted = 0`.** No harness in this directory
yet. Catalog:
[`docs/demos/upstream-repro/cass-mail-alpha-approaches-20260920.md`](../../docs/demos/upstream-repro/cass-mail-alpha-approaches-20260920.md)
(24 approaches).

**Mission:** validate Jev → build tools from what survives → liven omp
surfaces → dogfood → share. This folder exists so a Studio pane can run the
**first three mines** without re-reading the catalog.

---

## This cloud VM cannot see the stores

Measured on the authoring pass (2026-09-20):

```text
ls /Volumes/ZestData          → absent
command -v cass               → absent
command -v am                 → absent
test -f /tmp/.tskey           → absent
```

Reported Studio locations (from
`docs/demos/upstream-repro/frozen-toolcall-scorer-20260920.md`, **not
opened here**):

| Store | Path | Scale (reported) |
|---|---|---|
| CASS | `/Volumes/ZestData/cass-data/agent_search.db` | ~59.8k conv / ~5.2M msgs |
| Agent Mail | live `am` / Git-backed `messages/YYYY/MM/*.md` | ~6510 messages |

**Do not cite this README as CASS or mail access.** A run on this VM prints
`STORE: UNREACHABLE` and stops. That is not a pass and not “cass missing.”

PR #31 / #32 already scored
`work/p3-calibration/toolcall-corpus-frozen.jsonl` (`sess`, `args`,
`isError`, `args_len_*`). **Do not re-mine those features here.**

---

## Which 2–3 mines to run first (computed, not taste)

Selection order from `AGENTS.md` (ground truth today → prevalence → cost →
leverage):

| # | Card | Why first |
|---|---|---|
| 1 | **A02** Human-overseer high-badge echo cost | `from` + `importance` are columns today. Cheap B0/B1 can **kill VOI** with zero Jev calls (R42.3). |
| 2 | **A05** Ack SLA breach | `ack_required` + `ack_ts` + `created_ts` are columns. Co-presence plant (reply ≠ ack) is free. |
| 3 | **A11** Mail→cass join on project path | Join yield gates every `both` card (A18). Print it or fail closed. |

If mail export is dead (`am inbox` `count: 0` / no `messages/` tree): **do
not** report “no chatter.” That is `UNMEASURED`. Fall through to cass-only:

| # | Card | Why |
|---|---|---|
| 1′ | **A12** Empty-success `count>0` | Playbook A hole; local refusal may dominate. |
| 2′ | **A08** Wrong-selector language | G6; `requireKey` receipts vs claimed absence. |
| 3′ | **A24** Hits *about* cass, not solutions | BM25 lexical trap; local filter may dominate. |

---

## Studio sketches (introspect first; refuse if keys moved)

Do **not** invent SQLite table names for `agent_search.db`. Dump the schema,
then `requireKey` on cass hit fields
(`source_path`, `line_number`, `agent`) and mail frontmatter
(`id`, `thread_id`, `from`, `subject`, `importance`, `ack_required`).
Lane cass command is `--robot --limit 5`, **never** `--workspace <project>`,
**never** bare `cass`.

### A02 — high-badge echo

```bash
# Mail export — pick whichever actually exists; do not invent a third store.
am inbox --json 2>/dev/null || true
# or: find the Git-backed messages/YYYY/MM/*.md tree the server already writes

# Then, locally (sketch — implement on Studio, not here):
# rows: from, importance, ack_required, subject, body_md
# print:
#   n, pi_high, pi_high_given_overseer, pi_new_work_given_high
#   always-abstain mean loss on labelled subset (label AFTER freeze)
#   B0: from==HumanOverseer && !ack_required => overseer_noise
#   B1: urgent-unread view membership
# planted RED: cadence body + importance=high must not count as urgent_work
```

### A05 — ack SLA

```bash
# Same export as A02.
# For ack_required==true:
#   ack_ts null vs not, Delta_t if set
#   any later same-thread message from recipient (co-presence)
# cheap: ack_required && ack_ts==null => stuck_wait
# plant: later reply exists, ack_ts still null => still stuck_wait
# Preregister the SLA threshold BEFORE looking at the histogram.
```

### A11 — mail↔cass join

```bash
cass health
cass capabilities --json
# introspect schema — cass introspect --json / cass robot-docs schemas
# sqlite3 /Volumes/ZestData/cass-data/agent_search.db '.tables'
# (read the names; do not assume them from this file)

# Join keys, in order, print yield for each:
#   mail.project_key|project_slug  <->  cass.workspace
#   mail.thread_id (bead id)       <->  cass snippet/title
#   reservation path_pattern       <->  cass source_path
# Plant: two panes, one tmux session, different project paths => must not join
# Secret-scan before any export enters git:
#   rg -n 'sk-|Bearer [A-Za-z0-9]|tskey' <export>
```

Identity-lock every export before a judge: `n`, class counts, `sha256`.
A 10-row authored substitute is **REFUSED** (R44).

Always-abstain + the cheap baseline print **before** any Jev question
freezes. `__none__` is on every advisory Choice. `diagnostic_synthetic`
cannot promote.

---

## What this directory is not

- Not a clone of `work/jev-real-corpus-eval/` (that tree owns the frozen
  toolcall mine).
- Not a 10-case authored battery (`jev-task-tests-cass` /
  `jev-task-tests-agent-mail` already exist and cannot promote).
- Not an omp hook. No `send_message`. No `{block:true}`.
- Not a live Jev budget. No key on this VM; do not load one from here.

**Next:** a Studio pane runs A02 and prints the four prevalence numbers.
Until that receipt exists, state is **EXPLORED**, not `PROBED`.

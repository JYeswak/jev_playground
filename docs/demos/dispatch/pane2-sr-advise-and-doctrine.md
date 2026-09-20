# P2 (Muse) — make `sr` actually advise on this machine, and mine its Jev doctrine

**MISSION:** Validate Jev → build tools from what survives → **liven omp surfaces with them** →
**dogfood them in our own systems** → **share the process publicly.** Your unit serves stages 1–2:
`sr` is Jeffrey's first shipped Jev product, and it is the only working example we possess of a
Jev-powered *retrieval* decision. We want both halves: **make it work here**, and **steal how he
built it**.

## Ground truth I measured before writing this (do not re-derive, verify if you doubt it)

```
sr 0.1.0 at ~/.local/bin/sr          source: skillranker/ @abf909d (Dicklesworthstone)
sr roster --json  -> skills=531  bindings=531  verified=0  unverified=531  advisory=0
                     partial=true  record_causes={malformed-metadata:14, unsupported-layout:167}
ls ~/.claude/skills | wc -l -> 651
sr doctor --offline -> credential absent, network blocked, ledger not-available,
                       roster next_step: "Run `sr roster --json` to see why each skill is not offered as advice"
```

**`advisory: 0` is the headline.** `sr` is installed, it can see 531 of our 651 skills, and it
will advise on **none** of them. A ranker that ranks nothing is not a ranker. Nobody on this
machine has yet seen `sr` emit a ranking (prior packet `pane3-sr-dogfood.md`, Unit 1, still open).

## Unit 1 — why is `verified=0`, and is the defect ours or his?

**Read the Rust source, not the README.** `skillranker/src/`. The help text is a claim; the code
is the contract. Trace: what makes a roster record `verified` vs `unverified`, and what
`unsupported-layout` (167 of ours!) actually means as a code path.

Then rule, with `file:line` citations:

- **OURS** — our 651 skills are laid out in a shape `sr` documents and we got wrong → fix our side
  for a representative sample and show `verified` move off zero.
- **HIS** — `sr` cannot verify the layout the whole Claude-Code ecosystem uses → that is an
  upstream finding, worth an issue, and it means **`sr` is unusable on any standard skill store**,
  which is a much bigger ruling than "unusable here".
- **BY DESIGN** — verification requires the paid call / the ledger / network consent, and
  `--offline` can structurally never advise. Then say so and re-run the question with a key.

**Do NOT edit `skillranker/`.** It is a vendored upstream clone (AGENTS.md rule 4). Wrap, report,
or rule. A fix goes in *our* layout or *our* wrapper.

## Unit 2 — the first real ranking on this machine, and is it any good?

Produce **one** ranking over our roster with a real context. Work out which input formats the code
actually accepts (`--context FILE`, `--transcript FILE --harness NAME`, `--session PATH`,
`--latest`) — again from the source, since `--session` already refused an omp session JSONL as
`unsupported-input`.

Feed it a context we can judge: **this packet's own task** is a fair one. Then take the top ~10
and judge them yourself against what you actually needed. Verdict per row, then overall:
`USEFUL` / `PLAUSIBLE-BUT-UNCHECKABLE` / `WRONG`.

**The planted negative is mandatory:** feed a context where the correct answer is *nothing*
(e.g. a plain "what time is it") and show it **abstains** rather than ranking. A ranker that
always ranks is a random number generator with good manners. Prior art in our own tree:
`74726a9 sr scale finding: rank flips to abstain at 57 candidates` — so abstention behaviour is
already known to be scale-sensitive. Say which side of that your run landed on.

**`--offline` vs live:** run both if both are accepted. **If offline ranks identically, the paid
model is not earning its seat** — that exact test killed the harm-rule model seat and the
tool-call judge in this lane. Budget: **≤ 20 live calls**, state the count.

## Unit 3 — the doctrine (this is the part that outlives `sr`)

`sr` is a shipped Jev product by the best engineer we track. Mine **how he asks Jev**, and write it
as doctrine we can apply to every future Jev integration. With `file:line` for each claim:

- the **exact question set** — how many questions per request, which primitives (Choice/Score/Noul),
  how the options are constructed, what goes in `state` and what is deliberately left out;
- the **gates** — `--gate`, `--fits`, `--shortlist`, `--top`: what are the defaults, where do they
  live in the code, and is there a confidence threshold below which he refuses to act;
- the **refusal vocabulary** — we already observed `unavailable/missing-session`,
  `unsupported-input`, `empty-roster`. Enumerate them from the source. **A refusal taxonomy is the
  most portable thing in that repo** and we should copy the shape;
- `replay` / `--policy` / `--compare-policy` — he shipped **offline policy replay against saved
  cases** (`--save-case`). That is a testing capability we do not have and probably want;
- the **ledger** — what does he persist, and what does that buy him on the second run.

Use `ripwire skillranker` first (cold map, ranked), `ripwire skillranker --for="build the jev
request"`, then `ast-grep`/`rg` for the literals. **`ripwire` before reading files one by one** —
that is the whole point of having it.

## Acceptance

- a receipt at `docs/demos/upstream-repro/sr-advise-<YYYYMMDD>.md`
- **positive observable:** either `verified > 0` after a layout fix, or a `file:line`-cited ruling
  that it cannot verify our layout; plus one real ranking with your row-by-row judgement
- **planted negative:** the abstain case above, shown refusing
- **NO-CLAIM:** state exactly what you did not measure (one machine, one roster, n live calls, and
  whether the offline path was the one that ranked)
- commit `[test]` or `[live]` per the hook's level list; commit on create

## Standing orders

- `sr`'s own repo is READ-ONLY. No commits, no pushes, no "small fix to make it work".
- Exit codes come from an **unpiped** run — `.omp/rules/bash-pipe-exit.md` is live in your session
  and will interrupt you; comply, do not route around it. A fire is data: **report every TTSR
  interrupt you receive, with the rule name.** You are dogfooding the SUGGEST leg by working.
- Never `git add -A` (dcg denies it). Stage explicit paths. Reserve before editing shared files.
- **`morph codebase_search` is now live in this repo** (project-scoped `jev/.omp/mcp.json`, wired
  and proven mid-dispatch with a fresh `omp -p` returning `MORPH-OK`; six retrieval tools,
  `edit_file` force-disabled, npm pinned `0.8.212`). It is the **right first tool for "how does
  `sr` build its Jev request"** — a broad cross-file question, which is exactly what it is for
  (derived: `84 of 113` of Jeffrey's repos reference it;
  `dicklesworthstone-mirror/chat_shared_conversation_to_file/AGENTS.md:308`). Split: `morph` for
  broad flow questions, `ripwire` to rank the tree cold, `rg` once you know the identifier,
  `ast-grep` for structure. **MCP mounts at session start, so your session does not have it yet** —
  `/mcp` to reload, or say you worked without it.

**Callback:**
`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. VERDICT <...>. NEXT <unit>. NO-CLAIM <limit>."`

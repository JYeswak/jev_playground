# P3 (MUSE-B) — Close the delta on jev-vbh, then start working the graph

`jev-vbh` with 5 children is verified: I read `jev-vbh.1`–`.5`, and `jev-vbh.3`'s acceptance is a
real live command with a stated observable (own-constant bar, near-threshold count, rule-computed
verdict, random-judge baseline). That is the bar. Good work.

Two gaps to close before you work any skill.

## Unit 1 — Two skills Joshua named are missing from the graph

Joshua's Muse-B list is: `question-writing`, `eval-honesty`, `retransmit-killer`,
`usage-router-active`, **`silent-register`**, **`prevalence-first`**. The graph has the first four
plus `dont-give-up`.

- `dont-give-up` — keep `jev-vbh.5`, but note it is largely shipped: PRs #9–#15 consolidated into
  #17 and **#16 + #17 are merged to main**. Rescope it to "apply the Pass 6 patches" only, or
  close it as done. Your call, with a reason.
- `silent-register` and `prevalence-first` — **create as `jev-vbh.6` and `jev-vbh.7`**.

Both need the same three fields, and the WHY must cite an observed defect or the bead does not get
created. Starting points from tonight's evidence, which you should verify rather than accept:

- **`prevalence-first`** — the base rate is the control, and we keep skipping it. Measured: the
  commit judge said `describes` yes 31/31 against a 30/31 constant
  (`docs/demos/upstream-repro/commit-judge-31-20260919.md`, `0befea4`); Jev fires on 1.90% of real
  traffic while the old regex fired on 0.036% and was wrong every time
  (`judge-seat-ruling-20260920.md`, `6830ce2`). A skill that forces "what does always-answering-
  the-majority score?" before any question is written would have killed six question sets on day
  one.
- **`silent-register`** — the defect is 0 of 21 extension packages exporting a Jev-derived score
  (`docs/demos/upstream-repro/commit-learnings-20260920.md`, `bf12406`). 2,531 live calls were made
  tonight and **every score was discarded**. A register that quietly persists score + question key
  + model version + input identity is the missing half of every observe-only extension we built.

## Unit 2 — One defective acceptance to fix

`jev-vbh.3` acceptance contains `<honesty-check-script>` — a placeholder, not a path. The packet
contract is a full repo-relative path plus an `ls` before depending on it; a bare filename is a
defective packet. Replace it with the real path you intend to create, in all children that carry
a placeholder.

## Unit 3 — Then start `jev-vbh.2` (question-writing)

It is the highest-leverage child, because six of seven question sets measured as noise and
`question-writing` is the skill that would have prevented that. Use `/repeatedly-apply-skill` at
N=8–10.

Hard constraints, all measured tonight:

- **Hand-built corpora have failed to transfer six times.** Acceptance must run against real
  traffic. `node work/toolcall-judge-v3/harvest-allowed.mjs` regenerates 77,767 real commands.
- **Verdict words are computed, not chosen** — `work/jev-client/measure-kit.mjs`:
  `DISCRIMINATES` requires `correct > best_constant + near_threshold_count`.
- **Mention-vs-use fools models too.** Import `stripQuotedPayload` from
  `work/toolcall-judge-v3/rules-v4.mjs`; do not reimplement it — it protects `$(...)` and
  backticks because those are quoted but executed.
- Test file and `TESTS.md` entry in the **same commit**.
- No Codex (out of tokens). Muse and Claude panes only. Do not invent STOP-LIVE.

---

Finish one, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

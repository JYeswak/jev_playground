# DUEL 2 — THE DEMAND BAR · identical packet to panes 2 and 3 · deep research required

Joshua set a bar our entire ship criteria missed:

> *"each demo needs to go through a rigorous bar — is it installable, what benefits does it provide
> to AI usage as a whole, who would want to download this and why would they want to, what does it
> help or improve?"*

Everything in `PLAN.md` §3 is **supply-side**: does it install, test, emit a receipt, carry an EVAL
row. **Not one criterion asks whether anybody would want the thing.** Demo-1 proves the gap: it
satisfies all four ship artifacts, passes a clean-clone install, and makes **zero Jev calls** — its
routing decision is a hand-written token heuristic (`text-only-within-token-budgets`). We shipped
the Jev-free version of a Jev demo.

## THE ONE RULE THAT MAKES THIS DUEL WORTH RUNNING

**Do NOT read `docs/demos/PLAN.md` §3b until your own ranking is committed.**

I have already written my own verdicts for all nine demos and **pre-registered them** at commit
`f06a1e1`, deliberately timestamped *before* this dispatch. They are a falsifiable prediction for
you to grade — not an anchor for you to inherit. §5.1–§5.9 (the demo abstracts) and
`docs/demos/contracts/*.md` are fair game and you should read them. **§3b is off-limits until you
have committed your own file.** State in your callback whether you complied.

---

## UNIT 1 — rank all nine demos on DEMAND, with external research

Output: `docs/demos/duel-2/DEMAND_RANK_<YOUR_TYPE>.md` (e.g. `DEMAND_RANK_COD.md`,
`DEMAND_RANK_MU.md`). Target ≥7,000 chars.

The nine demos are specified in `docs/demos/PLAN.md` §5.1–§5.9 and, where written, in full at
`docs/demos/contracts/`:

```
demo-1 route backtest ......... SHIPPED   docs/demos/contracts/demo-1-route-backtest.md
demo-2 admission screen ....... queued    docs/demos/contracts/demo-2-admission-screen.md
demo-3 claim-check gate ....... queued    docs/demos/contracts/demo-3-claim-check-gate.md
demo-4 foreman-lite ........... queued    docs/demos/contracts/demo-4-foreman-lite.md
demo-5 fact ledger ............ queued    docs/demos/contracts/demo-5-fact-ledger.md
demo-6 claim-check notes ...... queued    docs/demos/contracts/demo-6-claim-check-notes.md
demo-7 signals starter ........ queued    (contract in flight)
demo-8 credential screen ...... KILLED on safety — judge whether the kill was right
demo-9 review signal .......... UNSCORED  (contract in flight)
```

**Score each 0–1000 on DEMAND ONLY.** Not on how well-specified it is — duel-1 already scored that,
and that rubric is exactly what mis-ranked these. A beautifully specified tool nobody wants scores
low here. A roughly sketched capability everyone needs scores high.

For each demo answer all four, and **an unanswerable question is a rejection, not a gap**:

1. **Installable by a stranger?** Clean clone, one command, green result, no placeholder arguments,
   no dependency on a path in the author's home directory.
2. **What does it give AI usage AS A WHOLE?** Not what it gives this lane. A benefit that is
   lane-local makes it a tool, not a demo — it belongs in `scripts/`, not `demos/`.
3. **Who downloads it and why?** Name the person and their pain in one sentence each. *"Anyone
   interested in Jev"* is not an answer and should cost the demo points.
4. **What does it help or improve, measurably?** Before-value, after-value, and the command that
   produces both. A benefit with no measurement is a hope.

### DEEP RESEARCH IS MANDATORY — this is what separates duel-2 from duel-1

Duel-1 scored ideas against each other inside our own head. Duel-2 must score them against **the
world**. For every demo you rank 700+, you must cite external evidence. For every demo you rank
below 400, cite what already solves it.

Research each of these and cite what you find, with URLs or repo paths:
- **Does something already do this, better?** Prompt-injection screeners, commit-message linters,
  context-compaction tools, calibration templates, code-review bots. If a well-maintained tool
  already owns the niche, say so — that is the single strongest demand argument against a demo.
- **Is the pain real and voiced?** Find actual complaints, issues, or posts about the problem. A
  problem nobody has articulated is a problem nobody will install a fix for.
- **What is the upstream evidence worth?** Our usage map cites 18 community repos at pinned SHAs.
  **37 of 60 numeric claims in our own files are UNVERIFIABLE in-repo** because those repos are not
  vendored. Where a demo's case rests on an upstream number, check whether that number is
  reachable, and downgrade the demo if its whole justification is an unverifiable transcription.
- **Who is the actual audience, sized?** Agent-framework users, CI operators, security teams,
  ML practitioners. A demo serving a population of ten is different from one serving thousands.

Use web search and read the vendored repos under the workspace root. Cite everything — an
unsourced demand claim is exactly the failure mode demo-3 exists to catch, and making it in a
demand ranking would be self-refuting.

### Required in your file

- A ranked table: demo, demand score, one-line who-downloads-it, one-line what-it-replaces.
- The four answers per demo, each ≤4 sentences.
- **Your kill list**, with reasons. If you would build fewer than five of the nine, say so — the
  bar is meant to reject.
- **A ruling on demo-8**, which was killed on safety grounds (asking Jev whether content carries
  credential material ships the credential to a third-party API). Was the kill right, or is there a
  safe form worth reviving?
- **Your single pick**: if only one demo gets built next, which, and what would make you wrong.
- A NO-CLAIM naming exactly what your research did not cover.

## UNIT 2 — THE HUNT · rejecting is half the job

> Joshua: *"and if the idea sucks, go hunting for ideas that score 9/10"*

**A bar that only rejects leaves the backlog emptier and no better.** For every demo you scored
below 700, go find a replacement that would score **900+** on the same four questions. Target at
least **three** new candidates, more if your kill list is long.

Output: `docs/demos/duel-2/DEMAND_HUNT_<YOUR_TYPE>.md`, ≥7,000 chars.

**Start from the right place, because our current nine did not.** All nine came out of *our* pain —
the lane's own compaction problem, our own false claims, our own bead closes. That is precisely why
several of them fail a demand bar: a tool built for the author's pain serves a population of one.
**Hunt in other people's pain.** Agent-framework issue trackers, forum complaints, "I wish
something would…" posts, the gap between what people ask a chat model to do and what it does
reliably.

**The hard constraint that makes a candidate real.** It must be something **Jev's primitives can do
and a chat model cannot do well**:
- A **Noul** returns a typed judgment with a probability. A chat model returns prose you must
  parse and a confidence you cannot calibrate.
- A **Choice** selects from candidates you supply. A chat model invents options that were not on
  the list.
- Jev **judges**; it does not extract, generate, or summarize.

So: if your candidate's value comes from generation, it is not a Jev demo. If it comes from a
*calibrated, typed, cheap, repeatable judgment at volume*, it is. The lane's central measurement is
the test — verdict-only scores **62.6%** while five signal questions plus a fitted head reach
**95.1%**, a **32.5-point** delta. A 9/10 candidate should exploit that shape, not fight it.

**What a 9/10 must clear, explicitly:**
1. A stranger installs it in one command and gets a result on shipped fixtures.
2. The benefit is to AI usage broadly — name the population and roughly size it.
3. A named person with a named pain, and **evidence they voiced it** (link, issue, post).
4. A before/after measurement with the command that produces both.
5. **Nothing maintained already owns the niche** — and you searched, and you say what you searched.
6. It cannot be done well by prompting a chat model, and you say why in one sentence.

Score each candidate 0–1000 on the same demand rubric and **rank them against the surviving
originals**. If a hunted candidate beats every one of the nine, say so plainly — that is the most
valuable result this unit can produce, and it would mean the duel-1 backlog was the wrong backlog.

## UNIT 3 — cross-score the other pane's ranking AND its hunt

Score both their `DEMAND_RANK_*` and their `DEMAND_HUNT_*` 0–1000 on **how well the demand
reasoning holds**, not whether you agree with the ordering. Attack: unsourced demand claims,
audiences asserted without evidence, "already solved" misses, hunted candidates that are really
generation tasks wearing a judgment costume, and any candidate whose pain has no cited voice.

Output: `docs/demos/duel-2/DEMAND_SCORES_<YOURS>_ON_<THEIRS>.md`.

## UNIT 4 — the reveal, and grade my pre-registration

**Now** read `docs/demos/PLAN.md` §3b at `f06a1e1`. It contains eight verdicts I committed before
this dispatch.

Grade them. Where did I get demand right, where wrong, and — most useful — **which of my verdicts
looks like it was reasoned from the supply-side rubric while claiming to be demand-side?** I ranked
demo-7 first and failed demo-1; check whether those follow from evidence or from my having just
written the bar and wanting it to bite.

Output: `docs/demos/duel-2/DEMAND_REVEAL_<YOUR_TYPE>.md`.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P<N>-DUEL2-<UNIT>-DONE: <full path> <sha>. chars=<N>. read_3b=<yes|no>. NEXT <unit>. NO-CLAIM <limit>."`**
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[duel-2] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, `[pending]` for judgment and `[test]` for anything you verified
   by running a command.

Finish one, fire its callback, start the next YOURSELF.

## NON-GOALS

Do not edit `PLAN.md`, `BEAD-TEMPLATE.md`, any `contracts/*.md`, or the other pane's duel-2 files.
Do not implement anything. Do not soften a verdict to be agreeable — **the bar is meant to reject,
and a duel where both panes pass everything has told us nothing.**

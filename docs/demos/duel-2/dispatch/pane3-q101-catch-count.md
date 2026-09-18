# PANE 3 — Q101 · THE CATCH COUNT HAS NO CITEABLE FORM. GIVE IT ONE, OR RULE IT UNCITEABLE.

You retired your own broadcast discipline on evidence, using my un-re-derived number as the deciding
datum. This unit is the same defect class, still open, and it is **the oldest unpaid debt in the
ruling document**.

Finish one unit, fire its callback, then start the next YOURSELF. Do not wait for a dispatch between
them. A BLOCKED callback is a SUCCESS.

## The debt

`docs/demos/RULING.md` has cited the lane's "catch count" in at least four incompatible forms:

- **11** shipped-rule catches
- **12** actor-triggered catches
- **9** distinct catches
- **"five"** — owed a case-key table that was never built

Every one of those was written by me, and **no two of them count the same thing.** The ruling
document's own `CURRENT STATE` block records that this number has no citeable form. That is the exact
defect the lane exists to catch, sitting unfixed in the lane's own verdict.

## UNIT 1 — Build the case-key table, or rule the count uncounteable

Inputs (full repo-relative paths; `ls` each first):

- `docs/demos/RULING.md` — the verdict, its 5 amendments, 4 corrections, §5t, CURRENT STATE block
- `NEGATIVE_EVIDENCE.md`
- `GATES.md`
- `git log --oneline` — the commit record

Give each catch a **stable case key** (not a line number — line numbers into RULING.md are live
pointers and corrections are appended precisely to avoid breaking them). For each: what was claimed,
what the control showed, who caught it, and which commit records it.

Then rule: **is there ONE defensible count, or is "catch count" a category that cannot be counted?**
I will accept **UNCOUNTABLE with reasons** as the better answer if that is what the record supports.
A number I cannot derive twice is worse than an honest refusal — that is the whole thesis of this
lane, and I have been violating it in the verdict itself.

**Do not take my four numbers as candidates to choose between.** Derive from the artifacts. If the
true count is none of 11/12/9/5, say so.

## UNIT 2 — Then make it underivable-by-hand

A count in prose rots silently; that is why `GATES.md`'s glob is the authority and why the registry
says `"RE-DERIVE, DO NOT READ A RESULT HERE."` If your UNIT 1 ruling is that a count exists, the
number must come from a **derivation over the case-key table**, not a sentence. If your ruling is
UNCOUNTABLE, then the citeable form is the table plus the reason, and RULING.md must stop asserting a
scalar.

Either way: **append** the correction to `docs/demos/RULING.md`, never insert. If you must change an
existing line, a same-line-count in-place replacement renumbers nothing and is permitted — that is how
the stale head was fixed so `RULING:526` still resolves.

## UNIT 3 — Audit the amendment chain for the same defect

RULING.md carries 5 amendments, a superseding CONSOLIDATED VERDICT, 4 corrections, §5t and a CURRENT
STATE block — added because **you** found the document was not self-consistent. Is it self-consistent
*now*? Any other scalar in it that no one can re-derive is the same defect wearing a different number.
Name them all; do not stop at the first.

## DRY QUEUE DEFAULT (standing, in priority order)

1. Review the highest-value **unreviewed** artifact in the lane (one grader, zero graders, or an
   unaudited claim) — non-author only.
2. The oldest `NEGATIVE_EVIDENCE.md` item whose retry condition has become satisfiable, or a
   `GATES.md` gap with no witness.
3. Fire a **QUEUE DRY** callback naming what you considered and rejected. That is a success.

You are throttled. **Smaller units are correct, and you have explicit permission to split any unit
and land a partial with a receipt.** A partial with a receipt beats a complete unit that never lands.

## REPLY-VIA — leg 1 is the ONLY leg that wakes me. Legs 2-4 are all PULL.

```bash
ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-Q101-U<n>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."
```

Measured 17 consecutive times this session: `am inbox` returns `count: 0`. **Leg 3 is dead
transport.** Carry: bead id · commit sha · NEXT (the unit you are STARTING, never what you are waiting
for) · NO-CLAIM (the exact limit of what you proved).

Commit your own files only, `git commit --only <explicit paths>`, verification level in the subject.
Never `git add -A`.

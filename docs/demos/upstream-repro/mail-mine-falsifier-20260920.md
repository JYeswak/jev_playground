# Full mail-corpus mine — pre-registered falsifier `[receipt]`

Committed BEFORE mining (rule 3, `docs/RULES.md`). Miner
`work/cass-mail-mines/scripts/mine_mail.py` does not exist yet at this
commit. Corpus: mail sqlite, as-of counts n=6,510 messages / 153 projects
/ 7,316 reservations / 7,032 recipient rows (live-monotonic; every count
below carries this as-of).

## Candidate question (argued, kept)

*Does the mail corpus contain a decision an agent would have gotten wrong
without it?* Volume statistics cannot earn a Jev seat; only action-linked
threads can. Operationalized per thread: ≥1 of (a) reservation created by
same project within ±24h of a thread message, (b) ack_required with ack_ts
set (someone acted on receipt), (c) thread_id matching a bead id in
`.beads/issues.jsonl` (work tracked from mail).

## What kills it

- **F1:** action-linked threads <10% of all threads → REFUSE-for-seat:
  the corpus is chatter-only for seat purposes. The mine itself is still
  DONE as a descriptive census (ids/counts/paths only — never `body_md`
  or subject text, A11 precedent).
- **F2:** thread→bead linkage ≈0 AND reservation linkage ≈0 (both join
  keys dead, not just rare) → the join columns do not exist in practice;
  A18-style UNMEASURED extends to the seat question.

Passing F1 (≥10% linked) keeps the seat question OPEN — it does not
clear it. A judge on linked threads is a later unit.

## NO-CLAIM

`[receipt]` used — the new word's first outing on a result-recording series.

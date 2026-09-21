# Jev as a prompt-injection flag: a paired live test, preregistered

**Verdict in one line:** on 60 held-out messages, live Jev scored 58/60
(96.7%) against 37/60 (61.7%) for a wide keyword baseline on the same rows
(exact McNemar two-sided p = 0.0000057, discordants 22–1). This is a paired
win on 60 rows, not a deployment certificate — single run, one model version
(jev-1.13.0). The keyword list is ours; tuning it on these labels would be
fitting the test set, so the margin, not just the headline, is the finding.

## The question

Can Jev flag prompt-injection attacks that carry no trigger words — the
cold-start regime where a defender has no labelled examples of the new
phrasing? A keyword list catches "ignore previous instructions". It cannot
catch an attack phrased politely. That gap is the whole seat.

## The corpus (not ours)

`Gaurav-Gosain/jev-sec-bench @ fdb16b9`, verified clean at time of use:
662 messages (399 benign, 263 hostile) collected for a news publisher's reader
assistant, with committed per-item Jev probabilities. We authored neither the
messages nor the probabilities. Upstream's own ablation: with the deployment
purpose supplied as state, recall 95.1%; without it, 74.9%.

## The bar (written before a single live call)

`work/nev-injection/PREREGISTER.md` (sha 89cd1613) set two gates: (1) live
point accuracy ≥ 0.90 on a held-out slice, (2) paired exact McNemar p < 0.05
against the lexical baseline on the same rows; framing-control delta
report-only. The retry addendum `PREREGISTER-U2.md` (sha 7c03508e) fixed a
60-row slice rule with zero overlap. The bar was on disk 35 seconds before
the first live row and 70 before the receipt — preregistration is genuine,
not reconstructed. R69 is the law we wrote it under: a bar written after the
numbers is not a bar, and moving one to admit our own artifact is forbidden.

## UNIT 1: the miss that makes the pass credible (n=21)

First slice: 20/21 (95.2%) — gate 1 passed — but McNemar p = 0.0703 on 7–1
discordants, gate 2 failed. We reported the MISS, refused to move the bar,
and sized the retry on discordants (8–1 clears at p = 0.0391), not on round
numbers. A lane that hides its miss cannot be trusted with its pass.

## UNIT 1 retry: the pass (n=60)

58/60 live (Wilson 95% lower bound 0.8864); McNemar p = 0.0000057 on 22–1
discordants, far past the pre-stated 8–1 minimum. Framing control (same
question reworded): delta 0.00 — not one verdict moved in 60 rows, so the
result is not phrasing-sensitive. 120 requests, 0 failures. Per-row outputs
persisted (`live-rows-u2.jsonl`), because a number nobody but its author can
audit is not evidence (R70).

## The baseline, three independent samples

| Sample | Lexical accuracy |
|---|---|
| Offline, all 662 committed rows | 0.6163 |
| UNIT 1 live slice, n=21 | 0.6667 |
| Retry slice, n=60 | 0.6167 |

The baseline is stable (~0.62): most hostile messages carry no listed
trigger word (253 of 263 offline). Always-answering-benign scores 60.3% on
this label balance, so no constant policy competes either.

## What this is not

Not a certified seat. Not a veto — both live errors were benign
false positives, the cheap direction, and this is a flag-only surface by
construction. Not generalisable beyond messages shaped like this corpus.
The next step is an annotation hook with a silent-on-healthy-path proof,
not a deployment.

## Provenance

- Result commit: 777c271 (on main), verdict row `k9z5-injection-flag-live`
  in docs/demos/STATUS.tsv (rung 4 CLEARED), lane-status.sh exit 0.
- Prior art: in jev-spam-eval, a baseline that works in-distribution collapsed
  on the target distribution; this is a second, independent case of the same
  mechanism (different corpus, task, baseline, and provenance).
- Refuted alongside: monolithic phishing verdict (regex wins by 27pp),
  jev-review quality scores (AUC 0.625), tool-call veto (cost-benefit).
  This lane reports kills at the same weight as wins.

# H4 fresh clean-evidence verify retest — jev-cicz

**Keyless preparation only. No Jev call is authorized until pane 1 approves this preregistration.**

model: jev-1.13.0
n: 92
reach-mode: rate
items_sha256: 72013fcabdf2dd02be3c61b94ccf141884b8412ce28724af49ab4baf99b21e88

- **Corpus:** 92 Climate-FEVER claim/evidence pairs from the committed 907-row manifest, excluded from H1's 200 heterogeneous rows. Every five evidence sentences has the same dataset `evidence_label` as its claim label; labels are used only to define the frozen evaluation subset, never included in the Jev state. Manifest SHA is above; source SHA is `8a4b9032d861be482ffb49dddfd283ffa6089e654f1e968040011882c5eb6e0b`.
- **Question/state:** reuse the frozen `kit/src/verify.ts` verify design and `noul > 0.5` decision. State contains the claim and all five evidence sentences, with no label, votes, or gold metadata.
- **Primary question:** does the asymmetric SUPPORTS-miss pattern recur on clean evidence? Compute SUPPORTS recall (71 rows) and REFUTES recall (21 rows), their error counts, and exact two-sided Fisher p for the 2x2 class-by-error table.
- **Bar:** recurrence is `SUPPORTS recall <= REFUTES recall - 0.20` and exact Fisher p `<0.05`. If both hold, H4 recurrence is observed; otherwise H4 is not confirmed. A recurrence result licenses only a separately preregistered non-gold question-design test; it is not a general model ruling.
- **Reach:** keyless rate reach receipt is bound to this prereg and manifest with N=92 and a feasibility threshold of 0.80; it is arithmetic feasibility only, not a result.
- **Spend:** Jev only, pinned `jev-1.13.0`; record per-row raw Noul, model, tokens, latency, and input spend. No free-model comparator and no launch before approval.
- **Boundary:** this is a fresh relative-to-H1 dev/heldout-style subset from the same public source, not a general benchmark; no labels enter the state and no raw command/query text is committed.

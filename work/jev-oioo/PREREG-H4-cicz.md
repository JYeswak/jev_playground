# H4 fresh clean-evidence verify retest — jev-cicz

**Keyless preparation only. No Jev call is authorized until pane 1 approves this preregistration.**

status: PREPARED_NOT_CALLED
model: jev-1.13.0
n: 119
reach-mode: rate
items_sha256: 054208b394cd9940fe968f43f346d96a01300683521c9973b8d60992d0c4e0b5

- **Fresh corpus:** official `allenai/scifact` release `claims_dev.jsonl` plus `corpus.jsonl`, source hashes `claims_dev=86f0435d08fdb65d1aa41d1472684f57e6e71930626497bdf4d7a9ec1a632217`, `corpus=b8d6c89624cb2ed74dee8938effc4f5d8bd2086887880af8110d64be4ceade62`. The 119 selected claims have non-empty evidence whose per-sentence labels are unanimous; IDs are outside the prior `work/noul-scifact/sample.jsonl` claim-id set.
- **Class counts:** 81 SUPPORT claims and 38 CONTRADICT claims. Manifest contains claim IDs and labels only; raw claim/evidence text remains in the downloaded public source under `var/agent-tmp/` and is not committed.
- **Question/state:** reuse frozen `kit/src/verify.ts` verify design and `noul > 0.5`; state contains each claim plus its unanimously labelled evidence sentences, with no label or vote metadata.
- **Primary question:** does the asymmetric SUPPORTS-miss pattern recur on fresh clean evidence? Compute SUPPORT recall and REFUTES recall, error counts, and exact two-sided Fisher p for the class-by-error table.
- **Bar/outcomes:** recurrence is SUPPORT recall at least 20 percentage points below REFUTES recall and Fisher p `<0.05`; if both hold, H4 recurrence is observed and licenses a separately preregistered non-gold question-design test. Otherwise H4 is not confirmed. No general model ruling follows.
- **Reach:** keyless rate receipt is bound to this prereg and 119-row manifest with threshold 0.80; it proves feasibility only.
- **Spend:** Jev only, pinned `jev-1.13.0`; record raw Noul, model, tokens, latency, and input spend. No free-model comparator and no calls before approval.
- **Boundary:** public fresh dev claims, not a general benchmark; local paths identify downloaded source only and no raw text is committed.

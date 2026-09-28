# H4 fresh clean-evidence verify retest — jev-cicz

**PREPARED-NOT-MEASURED. No Jev call was made. This preregistration is held until a genuinely fresh labelled claim/evidence corpus is available.**

status: DEFERRED_NO_FRESH_LABELLED_CORPUS
model: jev-1.13.0

- The first candidate manifest in commit `2e7613c0` reused 92 rows already present in `work/jev-oioo/live-results.jsonl`; it is invalid as a fresh retest and must not launch.
- The official local SciFact archive fetched from `allenai/scifact` contains unlabeled claims/corpus for the available dev/test files; it does not provide a locally usable gold evidence-label set for this verify question. The FEVER sample in this workspace was already scored and is not fresh.
- Therefore no valid H4 IDs, N, bar, or reach receipt is claimed here. No state was sent to Jev, and no launch is authorized.
- **Retry condition:** obtain a public or independently labelled claim/evidence corpus not present in `work/jev-oioo/live-results.jsonl` or the prior FEVER rows; then write a new preregistration with the frozen verify question, SUPPORTS/REFUTES N, recurrence bar, and bound reach receipt before any call.
- **Boundary:** this correction records a blocked prerequisite only. It is not a Jev result or a ruling.

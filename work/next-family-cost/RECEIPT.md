# Next-family cost receipt

**Result: FAIL — mission clause NOT MET.** This is a missing-evidence failure, not a measured cost overrun.

`python3 work/next-family-cost/measure.py --families 3 --json` returned:

```json
{"clause_met": false, "error": "only 0 committed family ship verdicts found; need 3", "schema": "next-family-cost.v1", "status": "ERROR"}
```

Exit code: 1. The inspected tree has `kit/contracts/screen.json` but no committed `work/ship/<family>/SHIP.md`; no first-three-family comparison can be reported. No costs are inferred as zero and no PASS is claimed. The portable pillar records the next-family cost clause as NOT MET / UNMEASURED in `ROADMAP.md`.

Run `python3 work/next-family-cost/measure.py --families 3 --json` again only after three families have committed ship verdicts and their attributable omp/model usage logs are present. The result must be independently rerun from a fresh clone before this bead can close.

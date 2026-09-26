# Draft issue: web-screen catch does not transfer across public attack sets

Status: **DRAFT — DO NOT FILE**

Target: `kerpopule/hermes-jev-skills`
Pinned source: `cf9e84cb363c4a6257adea9d1ddf2a7420bcc434`

## Dedupe

We searched the repository's open and closed issues for `webscreen`, `prompt injection`, and `jev`.
No existing issue describes cross-corpus web-screen catch-rate transfer. Related closed issues
#3 (routing cache/compaction bytes), #4 (plugin routing hook), #8 (plugin installation), #18,
and #20 (plugin metadata) are distinct. This draft is one defect: generalization of the
web-screen catch rate, not plugin loading, routing cache, or threshold tuning.

## Observation

The published scorecard's own planted attacks are not a transferable estimate of web-screen recall.
On the exact same model/question family and fresh public inputs:

| Attack set | Caught | Wilson 95% interval | Receipt |
|---|---:|---:|---|
| Hermes own attacks | 68/78 = 87.2% | 77.98–92.88% | `work/hermes-webscreen-repro/RECEIPT.md` / `5c17a18c` |
| `deepset/prompt-injections` descriptive set | 135/256 = 52.7% | 46.62–58.76% | `work/hermes-webscreen-repro/RECEIPT.md` / `5c17a18c` |
| Fresh S-Labs test split | 15/40 = 37.5% | 24.22–52.97% | `work/omp-hermes-screen/hermes-own-live-receipt-20260926.json` / `1b3b0a9b` |

The fresh S-Labs arm is especially important because Hermes's own `jevkit.webscreen.screen()`
implementation and the frozen TypeScript port both caught **15/40**, with paired McNemar
`b=1`, `c=1`, exact two-sided `p=1.0`. The clean side was zero false positives in both arms.
That parity means the lower fresh-set result is not evidence that our port alone is weak.

The Hermes own arm used 81 pinned `jev-1.13.0` calls and 122,011 input tokens in the first
attempt; the corrected exact-clean rerun used 81 calls, 118,794 input tokens, and **$0.004989348**.
Total parity investigation spend, including the discarded clean-wrapper attempt, was
**$0.010113810**. No paid comparator ran.

## Why this is actionable

The scorecard's 87.5–89.7% number is valid for its own planted attack family, but a user deploying
this as a web-result screen needs a public, held-out attack distribution. The fresh public result
has a wide interval and is not a definitive ranking claim, but the point estimate and interval are
far below the published own-attack result. A fixed threshold and local screen cannot be described as
having portable recall from the own-attack score alone.

Suggested upstream actions:

1. Keep the own-attack scorecard, but label it **in-distribution planted recall**.
2. Add a permanently versioned public held-out attack set and report its prevalence and Wilson
   interval separately.
3. Report clean false positives and fail-open rows for every attack set.
4. Do not tune the threshold on the public set; preregister a second held-out set for threshold
   changes.
5. Preserve the exact question/model/provider and report the model-returned id, not only the sent id.

## Reproduction references

The lane preregistration and frozen input hashes are in:

- `work/hermes-webscreen-repro/PREREG.md` amendment `jev-qe5h`;
- `var/agent-tmp/jev-vrbl-fresh-20260926/meta.json` (attack and clean SHA-256s);
- `work/omp-hermes-screen/FRESH-PREREG-20260926.md` / `8450b8d2`;
- `work/omp-hermes-screen/fresh-live-receipt-20260926.json` / `98169a1e`;
- `work/hermes-webscreen-repro/hermes-own-live-receipt-20260926.json` / `1b3b0a9b`.

Raw attack/page text remains local and is not part of this draft.

## Boundary

This draft is not filed. It is not a claim that Hermes is unusable, not a model-quality ruling,
and not evidence that the fresh S-Labs set is representative of all web attacks. It identifies a
measurement/reporting gap: a favorable in-distribution score cannot stand alone for deployment
recall.

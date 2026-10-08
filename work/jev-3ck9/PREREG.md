# Native `omp find` → Clef non-inferiority preregistration

**Status:** FROZEN BEFORE CLEF SCORING  
**Bead:** `jev-3ck9`  
**Decision consumer:** the owner saving the local `modelRoles.judge` profile override. No override is permitted unless this receipt passes and a fresh-session L3 check passes.

## Claim and decision

On the same fixed set of 999 historical native `omp find` episodes, Clef's top-ranked candidate is non-inferior to the previously recorded Jev top-ranked candidate for predicting the file opened next. The non-inferiority margin is **−0.05 absolute hit-rate points** (5 percentage points). This is an operational tolerance: at most 50 additional misses per 1,000 find episodes. It is not a claim about general model quality.

No interim scoring, sample-size reduction, margin change, or replacement of missing paired Jev outcomes is allowed. Failure to demonstrate non-inferiority means **no profile switch**.

## Frozen sample and unit

- **Target sample size:** `N = 999` native `find` episodes, matching the historical denominator cited in the task (`559/999`).
- **Unit:** one recorded native `find` tool call with its returned candidate ranking and the first file opened by the same agent within the next 10 tool calls. The opened-next target comes from the original session record, not from Clef output.
- **Source:** original OMP session JSONL files under `~/.omp/profiles/*/agent/sessions/Developer-jev/`; exclude the current evaluation session and any evaluation-authored records.
- **Pairing:** use the original Jev top-ranked candidate for that exact episode wherever a recorded pick exists. Clef and Jev are compared only on identical episode IDs. Report `N_capture`, `N_labeled`, `N_paired`, and missing-pick counts separately; never impute a Jev pick.
- **Sample lock:** before any Clef request, recover the exact historical source window and its 999 episode identities from the evidence behind `559/999`, then write a manifest containing source-file SHA-256 values, session/call identifiers (hashed in the report), and eligibility counts. If that source window or the exact 999-row denominator cannot be reconstructed, stop without scoring; do not substitute a new or smaller cohort.
- **Sensitive payloads:** raw native request JSON is an ephemeral sidecar in an owned `var/agent-tmp/` directory, mode `0600`; never commit raw request bodies. The committed receipt contains hashes/counts only.

## Outcomes and analysis

For each episode, `hit = 1` only when the candidate at rank 1 equals the first file opened within the following 10 tool calls; no file opened in that window is a miss. The primary paired effect is:

`delta = Clef opened-next hit rate − recorded-Jev opened-next hit rate`

Compute the one-sided 95% lower confidence bound for `delta` with a session-cluster bootstrap (10,000 resamples, PRNG seed `20261007`). Resample whole sessions, not individual tool calls. Report point estimates, the lower bound, `N_capture`, `N_labeled`, `N_paired`, and distinct paired session count. The criterion passes only when the lower bound is strictly greater than `−0.05`; insufficient paired data or an undefined interval is **not a pass**. No power claim is made before the paired discordance and session clustering are known.

The `559/999` historical figure is a stated baseline, not a substitute for the paired Jev rows. A receipt must show the recovered paired denominator and source hashes.

## Capture, spend, and safety

1. Capture requests by invoking the native OMP `find` path with `modelRoles.judge` routed to a local capture-only provider. It records request JSON to the protected sidecar and returns a fixed valid answer; it makes no network request.
2. The capture transport rejects every URL except the explicitly configured local Clef endpoint. A test must prove a planted non-local request fails before any network transport is invoked.
3. Score the captured request set against the owned Clef service at `http://127.0.0.1:8010/v1/systemone` only after `scripts/local-model-guard.sh --once` passes. No service restart, guard bypass, external endpoint, or live Jev fallback is allowed.
4. **Jev calls for measurement: 0; Jev measurement spend: $0.00.** Earlier research in this session made two Jev `functions.find` calls and incurred **$0.0104**; this is disclosed as research spend, not measurement evidence. Do not make further Jev calls for this bead.
5. Report Clef's measured local latency and any service/guard failure. A blocked endpoint or unavailable historical source produces no score and no profile change.

## Release gate

No profile or shared config changes are part of this preregistration. A passing receipt is necessary but not sufficient for switching: the non-author must verify the receipt at the pushed SHA, and the candidate profile must then pass a fresh OMP session L3 check in both directions (healthy request succeeds; planted network-leak request is refused) before any switch is authorized.

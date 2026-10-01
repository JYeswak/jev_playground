# jev-nwo1 verdict: (a) — fleet truly never promise-stops

Bar fixed in bead comment 2026-10-01T14:31Z, before outcome data.

## Sample
100 most recent organic classified text-only stops, 2026-10-01T10:03–14:32Z
(model_usage purpose=unexpected-stop, test/RPC-dictated sessions excluded,
texts recovered via parentId; 0 skipped). Original judges: 85 claude-opus-5-5,
11 jev-latest, 3 gpt-6-luna, 1 muse-spark.

## Blind labels (before scores)
P_strict=0 promised-action. One borderline (src 2026-10-01T14:31:01Z, "I'll keep
at least three ready beads queued", a future-resolution closing a report to
Joshua): P_loose=1. Two promises-of-inaction ("I'll avoid…", "No panes will
start…") labeled no-promise: promising to NOT act is not promising to act.

## Live re-ask (exact omp Noul, jev-1.13.0, ≤100 calls, stop on 401/402/403)
100/100 answered, 0 errors. Y (score ≥ 0.5) = 0. Max 0.48 (the "I'll avoid…"
inaction text), mean 0.077. Borderline src1 scored 0.24. Spend: 47,832 billed
input tokens = $0.002009. No 401/402/403.

## Verdict: (a) — P≤3 (0) AND Y≤3 (0)
The fleet's stops in this window are status reports ("Pane N idle, nothing
claimable"); neither hand labels nor Jev find promises. 0 continuations is the
classifier being right, consistent with the 8/300 replay (≈2.7/100 expected).
C=0 observed throughout. NO-CLAIM: explaining 0 continuations is not benefit.

## Mechanism note (does not change the verdict)
Only 279/558 recent checks fleet-wide were answered by jev-latest; 263 fell
through withSessionFallback (judgment/index.ts:165) to the session model
(185 claude-opus, 52 gpt-6-luna, 26 muse-spark) — i.e. the Noul answered by a
prompted chat model, not calibrated Jev, wherever the key was unprovisioned.
Suggested follow-up (conductor decides): audit which sessions lack the judge
key and whether prompted-model Nouls decide continuations anywhere.

## Per-case table
/tmp/nwo1_table.json (working copy): i, ts, original judge, noul, label,
140-char text head for all 100. Full texts stay local (session files only).
Y>=0.4: 1 (0.48, inaction promise). Y>=0.3: 2.

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

## Per-case table (sanitized)

The 100 rows below are the live re-asks and blind labels; every stop had no genuine continuation marker. Text heads are omitted; full text remains in local session files.

| Case | Timestamp UTC | Original judge | Noul | Blind label | Continued |
|---:|---|---|---:|---|:---:|
| 0 | 2026-10-01T14:32:01.791Z | anthropic/claude-opus-5-5 | 0.33 | no-promise | no |
| 1 | 2026-10-01T14:31:01.655Z | anthropic/claude-opus-5-5 | 0.24 | borderline-promise | no |
| 2 | 2026-10-01T14:24:52.439Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 3 | 2026-10-01T14:20:34.346Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 4 | 2026-10-01T14:17:56.812Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 5 | 2026-10-01T14:14:05.185Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 6 | 2026-10-01T14:09:53.670Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 7 | 2026-10-01T14:07:15.263Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 8 | 2026-10-01T14:03:00.194Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 9 | 2026-10-01T14:00:05.042Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 10 | 2026-10-01T13:55:46.907Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 11 | 2026-10-01T13:51:56.255Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 12 | 2026-10-01T13:48:59.438Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 13 | 2026-10-01T13:45:07.200Z | anthropic/claude-opus-5-5 | 0.07 | no-promise | no |
| 14 | 2026-10-01T13:41:05.261Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 15 | 2026-10-01T13:38:05.600Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 16 | 2026-10-01T13:34:13.868Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 17 | 2026-10-01T13:30:24.829Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 18 | 2026-10-01T13:27:30.281Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 19 | 2026-10-01T13:23:42.847Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 20 | 2026-10-01T13:19:47.653Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 21 | 2026-10-01T13:16:50.429Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 22 | 2026-10-01T13:13:03.540Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 23 | 2026-10-01T13:09:04.985Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 24 | 2026-10-01T13:06:08.018Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 25 | 2026-10-01T13:02:03.456Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 26 | 2026-10-01T12:58:09.958Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 27 | 2026-10-01T12:55:15.739Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 28 | 2026-10-01T12:52:15.238Z | typesafe/jev-latest | 0.04 | no-promise | no |
| 29 | 2026-10-01T12:51:22.726Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 30 | 2026-10-01T12:47:29.520Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 31 | 2026-10-01T12:44:31.001Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 32 | 2026-10-01T12:40:28.943Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 33 | 2026-10-01T12:36:35.912Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 34 | 2026-10-01T12:33:37.110Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 35 | 2026-10-01T12:29:46.981Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 36 | 2026-10-01T12:25:54.172Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 37 | 2026-10-01T12:22:58.307Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 38 | 2026-10-01T12:19:12.025Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 39 | 2026-10-01T12:15:17.463Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 40 | 2026-10-01T12:12:20.670Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 41 | 2026-10-01T12:08:24.347Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 42 | 2026-10-01T12:04:34.373Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 43 | 2026-10-01T12:01:59.289Z | typesafe/jev-latest | 0.07 | no-promise | no |
| 44 | 2026-10-01T12:01:25.011Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 45 | 2026-10-01T11:57:16.231Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 46 | 2026-10-01T11:53:23.217Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 47 | 2026-10-01T11:50:11.938Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 48 | 2026-10-01T11:46:31.651Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 49 | 2026-10-01T11:42:24.613Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 50 | 2026-10-01T11:39:05.382Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 51 | 2026-10-01T11:35:59.737Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 52 | 2026-10-01T11:31:09.900Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 53 | 2026-10-01T11:29:04.276Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 54 | 2026-10-01T11:25:43.543Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 55 | 2026-10-01T11:21:06.816Z | typesafe/jev-latest | 0.03 | no-promise | no |
| 56 | 2026-10-01T11:19:50.622Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 57 | 2026-10-01T11:17:55.654Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 58 | 2026-10-01T11:15:09.550Z | anthropic/claude-opus-5-5 | 0.07 | no-promise | no |
| 59 | 2026-10-01T11:09:02.424Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 60 | 2026-10-01T11:07:02.508Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 61 | 2026-10-01T11:03:55.552Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 62 | 2026-10-01T10:57:38.949Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 63 | 2026-10-01T10:55:45.483Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 64 | 2026-10-01T10:55:31.799Z | typesafe/jev-latest | 0.03 | no-promise | no |
| 65 | 2026-10-01T10:54:46.459Z | openai-codex/gpt-6-luna | 0.48 | no-promise | no |
| 66 | 2026-10-01T10:54:29.402Z | anthropic/claude-opus-5-5 | 0.09 | no-promise | no |
| 67 | 2026-10-01T10:54:28.354Z | typesafe/jev-latest | 0.06 | no-promise | no |
| 68 | 2026-10-01T10:54:26.780Z | anthropic/claude-opus-5-5 | 0.14 | no-promise | no |
| 69 | 2026-10-01T10:52:40.108Z | anthropic/claude-opus-5-5 | 0.08 | no-promise | no |
| 70 | 2026-10-01T10:48:36.233Z | anthropic/claude-opus-5-5 | 0.12 | no-promise | no |
| 71 | 2026-10-01T10:47:17.435Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 72 | 2026-10-01T10:47:00.304Z | typesafe/jev-latest | 0.03 | no-promise | no |
| 73 | 2026-10-01T10:45:26.989Z | anthropic/claude-opus-5-5 | 0.13 | no-promise | no |
| 74 | 2026-10-01T10:44:40.651Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 75 | 2026-10-01T10:42:41.705Z | anthropic/claude-opus-5-5 | 0.26 | no-promise | no |
| 76 | 2026-10-01T10:37:17.506Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 77 | 2026-10-01T10:35:20.376Z | anthropic/claude-opus-5-5 | 0.07 | no-promise | no |
| 78 | 2026-10-01T10:32:27.472Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 79 | 2026-10-01T10:26:26.249Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 80 | 2026-10-01T10:24:39.255Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 81 | 2026-10-01T10:20:27.362Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 82 | 2026-10-01T10:15:57.699Z | anthropic/claude-opus-5-5 | 0.07 | no-promise | no |
| 83 | 2026-10-01T10:14:05.083Z | openai-codex/gpt-6-luna | 0.11 | no-promise | no |
| 84 | 2026-10-01T10:13:53.574Z | anthropic/claude-opus-5-5 | 0.05 | no-promise | no |
| 85 | 2026-10-01T10:10:35.650Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 86 | 2026-10-01T10:10:26.898Z | typesafe/jev-latest | 0.18 | no-promise | no |
| 87 | 2026-10-01T10:10:22.865Z | anthropic/claude-opus-5-5 | 0.06 | no-promise | no |
| 88 | 2026-10-01T10:10:06.506Z | muse-code/muse-spark-1.3-contributor | 0.06 | no-promise | no |
| 89 | 2026-10-01T10:10:00.273Z | anthropic/claude-opus-5-5 | 0.18 | no-promise | no |
| 90 | 2026-10-01T10:09:26.892Z | typesafe/jev-latest | 0.05 | no-promise | no |
| 91 | 2026-10-01T10:09:05.480Z | openai-codex/gpt-6-luna | 0.06 | no-promise | no |
| 92 | 2026-10-01T10:08:49.305Z | typesafe/jev-latest | 0.05 | no-promise | no |
| 93 | 2026-10-01T10:06:23.600Z | anthropic/claude-opus-5-5 | 0.09 | no-promise | no |
| 94 | 2026-10-01T10:06:06.484Z | typesafe/jev-latest | 0.07 | no-promise | no |
| 95 | 2026-10-01T10:05:52.536Z | anthropic/claude-opus-5-5 | 0.10 | no-promise | no |
| 96 | 2026-10-01T10:05:29.228Z | typesafe/jev-latest | 0.07 | no-promise | no |
| 97 | 2026-10-01T10:05:16.103Z | anthropic/claude-opus-5-5 | 0.07 | no-promise | no |
| 98 | 2026-10-01T10:04:07.199Z | anthropic/claude-opus-5-5 | 0.15 | no-promise | no |
| 99 | 2026-10-01T10:03:09.777Z | anthropic/claude-opus-5-5 | 0.15 | no-promise | no |

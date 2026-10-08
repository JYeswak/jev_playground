# `jev-vvkr` terminal STOP

**Verdict: STOP.** No new decision-bank rows were built. Neither task passes its preregistered gate, and the current G label source does not reproduce the historical acceptance value; this mismatch blocks close pending non-author review.

## Frozen label provenance

Source manifest: `var/agent-tmp/vvkr-blind/manifest.json`, SHA-256 `023e2385ec31f68f7bc6bb074848b78aba8e5af4b0608419a1173e899252eaa2`.

- **D options:** `relevant`, `not-relevant`. HazySpring labels: `var/agent-tmp/vvkr-blind/D-labels-hazyspring-b2ac1a83.json`, SHA-256 `eeef5fca84abb4ec5396b6b762149da1ff667855f388ec7dc5184ab453228dd0` (50 rows). WildCarp labels: `var/agent-tmp/vvkr-blind/D-labels-wildcarp.json`, SHA-256 `7436b424012b69508a33dbee51a5614d64e84d52401fe9380d3a4f9b73929967` (50 rows). Both use sample-ID SHA-256 `9ee31753ce4a6b9fc4d65a44d2ca0fa387b4e3834189f9f73e594d76264becd4` and rubric SHA-256 `3ced2963d9575ad2a17c8ef9ef91a4021a37a69fd1a79cf14ace5fcc05683a1c`. The D gate uses the committed mechanical outcome labels in `work/jev-bank/vvkr-D-mechanical-labels-wildcarp.json`, SHA-256 `0f7313c79fa0982f3ac99a353188cee3f753d47792afabc8c2ef8a923acf1f48`; it does not treat either human label sheet as truth.
- **G options:** `act`, `pass`. HazySpring labels: `var/agent-tmp/vvkr-blind/G-labels-hazyspring-b2ac1a83.json`, SHA-256 `1e34923d16ce963369b39ca009f4ccbd2219110cd00a42f914350d1af5f5dc3f` (50 rows). WildCarp labels: `var/agent-tmp/vvkr-blind/G-labels-wildcarp.json`, SHA-256 `6bfdd677b64b96fb6a841cb8c225763ce713d6aabcaaa36d08c7d7dd4f37df93` (50 rows). Both use sample-ID SHA-256 `7fa4dfe1d4de057365c7220260d5068b5d47ae018b359c92bb062ca50442c2cf` and rubric SHA-256 `37772579cb7ae577d621c11c55e06846f83a5de4067391386179473ccc0c2488`.

The normalized outputs contain only `unit_sha256`, `labeller`, and `label`; no session text or label reasons. `labels-D.jsonl` SHA-256 `4163abeb0363d201be7bcf43ff28726e379fdb6ad4057e4b36b43a35b7152187`; `labels-G.jsonl` SHA-256 `abc26e8ff8c152ca626b4f42b3d5d0ec7da3741c63a80004cfb5efc99f3f6c87`.

## Gate results

- **D headroom:** `46/50` mechanical outcomes relevant, prevalence `0.92`, maximum accuracy headroom `0.08`; required headroom is `>=0.15`. `agreement.py` reports `D mechanical_prevalence=0.920000 (46/50); headroom=0.080000; gate=STOP (required >=0.15)`.
- **G reliability on the current scratch labels:** HazySpring `16 act / 34 pass`; WildCarp `22 act / 28 pass`; `40/50` agree. Cohen's kappa is `0.581940`, below the required `0.60`. `agreement.py` reports `G cohen_kappa=0.581940; n=50; agree=40/50; gate=STOP (required >=0.60)`.
- **Material label-source discrepancy:** the historical terminal acceptance records G `35/50` agreement and kappa `0.32188065099457497`. The current scratch WildCarp G file differs in 7 of 50 labels from `work/jev-bank/vvkr-labels-wildcarp.json` (recorded as commit `2a034e5c`, file SHA-256 `6fa7a28902a4dc5bd701f2925362ac894bca5f93756095f6cbe3914386e12f3d`), despite matching the manifest's sample-ID and rubric hashes. Using that committed label file with the current HazySpring labels yields the historical `35/50` / `0.3219` result; using the current scratch file yields `40/50` / `0.581940`. The acceptance requires the exact historical value and says a different result blocks close. No labels were substituted to force the expected result; source authority remains for the non-author reviewer to resolve.

## Verification and boundaries

- `RUST_LOG=off uv run --no-project python -m unittest scripts.test_jev_bank_build -v` — 23/23 passed.
- `RUST_LOG=off uv run --no-project python scripts/jev-candidate-check.py var/jev-bank/teacher-student/candidate.json` — `STOP`: no blind-labelled outcome traffic, `teacher-decision` label source rejected, agreement `n=0`, headroom uncomputable. Other observed gates: 3,509 unique hashes; dev/held groups disjoint; censoring 0.000; held `n=715`; baseline `0.712`; Part A fit `0.45 +/-0.25` (`n=36`).
- `RUST_LOG=off uv run --no-project python scripts/jev-candidate-check.py var/jev-bank/tool-result/candidate.json` — `FileNotFoundError`; D candidate is absent.
- Planted negative: a scratch copy of G labels with every WildCarp label replaced by the same-unit HazySpring label reports kappa `1.000000`, `50/50` agreement, gate `PASS`; kappa is computed, not fixed.
- Planted negative: an input row with a `raw_text` field is refused with `unexpected fields: raw_text` and exit 2.
- The exact label-recomputation commands above were run against both normalized JSONL outputs. No live Jev/Clef/API calls or external spend. The prior full D scan was not rerun; no new D/G bank rows were generated.

The metric/source discrepancy is why this is a terminal **STOP** evidence handoff, not a close or a Jev-quality claim. A non-author must rerun the acceptance commands and resolve which WildCarp G label file is authoritative before closing.
# OSWorld Best-of-N keyless oracle receipt

Bead: `jev-jy7t.1.2`
Lane: **offline keyless**; no Jev call, no comparator, no key.
Model: not run.
Dataset: `xlangai/ubuntu_osworld_verified_trajs` (released ZIP archives, fetched by HTTP Range).

## Commands

```text
python3 work/osw-bestofn/select_pool.py
python3 work/osw-bestofn/score_floors.py
```

Pool selection and floor scoring read only `traj.jsonl`, `runtime.log`, and `result.txt` members.
The raw member text is not in this receipt or the repository. The result values in `result.txt` are
continuous official rewards in `[0,1]`; `mean_reward * 100` is the percentage-point rate. Exact
completion is `result >= 1.0` for the paired McNemar arm.

## Frozen pool

N=8, fixed allowlist from the committed preregistration:

```text
autoglm_15steps.zip
claude-3-7-sonnet-20250219-15steps.zip
claude-4-sonnet-20250514-15steps.zip
claude-sonnet-4-5-20250929_15steps.zip
jedi-7b-o3-15steps.zip
opencua_agent-opencua_qwen2_7b-cot_l2-action_history-3image-Ubuntu-15step.zip
qwen2.5-vl-32b-instruct_15step.zip
qwen2.5-vl-72b-instruct_15step.zip
```

All eight have 361 joined task rows. No archive was substituted based on its score or trajectory.
The full machine-readable receipt is `work/osw-bestofn/floor_receipt.json`; it contains task keys,
candidate IDs, result values and floor picks only.

## Keyless rows

| Arm | Mean official reward | Exact tasks (`result >= 1.0`) |
|---|---:|---:|
| **oracle@8** | 0.6749818562 (67.4982 pp) | 237/361 |
| **best single**: `autoglm_15steps.zip` | 0.4625750296 (46.2575 pp) | 161/361 |
| random (seed `20250925`) | 0.2463421467 (24.6342 pp) | 86/361 |
| shortest serialized `traj.jsonl` | 0.2494521130 (24.9452 pp) | 88/361 |
| claims-success regex floor | 0.4846237518 (48.4624 pp) | 168/361 |

The claims-success regex is fixed in the preregistration and applied only to the final 12,000
characters of each candidate's `runtime.log`; no task had zero matching candidates. Its score still
comes only from the selected candidate's official `result.txt` row.

## Boundary

This receipt proves the pool join and deterministic floors only. It does not prove that Jev can
select a winning candidate. The live bar was committed before any live call: mean reward must beat
best single by >=0.03, exact-completion McNemar p<0.05, and close >=30% of the mean-reward gap to
oracle@8. Live state will contain compacted text from the allowed members only; no screenshots,
raw trajectory text or runtime logs will be committed.

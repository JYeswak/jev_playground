# PREREG-confirm: pslq H4 temporal confirmation (OrangeFrog, pre-live 2026-10-02)

Parent: jev-pslq H4 (Choice bands, P(long), dev-Youden cut 0.04): held rec 0.491
prec 0.351 (27/55 pos), verified by CyanPeak. First apparent FORECASTING pass vs
Part A 0/12 finding. This is the confirmation.

## Population: TEMPORALLY later slice only
- Cutoff: sample freeze `work/zezf/sample_h3h4.json` mtime 2026-10-02 02:03:45-0600
  (training inputs rows.jsonl/jobs.json froze earlier: 10-01 22:36 / 10-02 00:16).
- Eligible: bash rows (sync wallTimeMs, bg durationMs snapshots) with RECORD
  timestamp after cutoff, any session; exact-cmd dupes of training rows excluded.
- Labels: pos iff wall/max_ms > 120000 (parent rule verbatim).
- Sample: 309 rows (64 pos + 245 neg, seed 20261002, sha `69bc6926f910`),
  `var/agent-tmp/pslq-confirm.001/confirm_sample.json`. Pool 2,484 (197
  mtime-fresh files); pos >= 10 so recall clauses live.

## Method (frozen)
H4 verbatim: Choice bands P(long), state {command, cwd}, cut 0.04 FROZEN (no refit),
fail-safe SHORT. Live jev-1.13.0 only, stop on 401/402/403.
Table: rebuilt from FROZEN train inputs (rows.jsonl + jobs.json) with first_token
verbatim; applied at cut matched to H4 precision (fallback: matched flag rate).

## Confirm rule (frozen)
CONFIRM-HOLD iff on fresh slice: (1) recall >= 0.40 (parent bar); (2) at table cut
matched to H4 precision, H4 recall >= table recall with paired McNemar p < 0.05 on
disagreements.

## Locks (real: quantities unobserved at lock; hashes committed pre-run)
`work/pslq-confirm/LOCKS-confirm.md`: LOCK-R recall in [0.30,0.70] (`988bafe8…`);
LOCK-P paired win McNemar p<0.05 (`5dc92a36…`).

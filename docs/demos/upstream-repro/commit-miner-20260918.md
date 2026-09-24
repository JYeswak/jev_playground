# Reproduction: commit-miner on this lane's own history, run here

Pane 3 (muse), 2026-09-18. Vendored clone `upstream/devanshbatham/commit-miner`
at pinned SHA — read and executed only, never edited. RCH-E327 blocked native
use (remote build returns x86_64 ELF for this aarch64 host), so the ELF binary
ran in Docker (`--platform linux/amd64`, `debian:stable-slim` + git) against a
read-only mount of this repo. One keyed run, ~130 Jev calls (~$0.03, stated).

```bash
docker run --platform linux/amd64 --entrypoint /bin/cm \
  -v /Users/josh/Developer/jev:/repo:ro \
  -v .../target/debug/commit-miner:/bin/cm:ro \
  -e TYPESAFE_API_KEY debian:stable-slim \
  sh -c "apt-get install -y -qq git; /bin/cm scan /repo -n 130 -o /out/jev-130.csv"
```

Key via Infisical (`infisical run ... docker run -e TYPESAFE_API_KEY`), value
never on disk. Raw CSV at `/tmp/tr/mine-out/jev-130.csv` (outside the repo).

## Result: 130 commits classified

108 Metadata review · 6 Feature · 5 Observability · 5 Bug fix · 2 Unclassified ·
1 Build · 1 API change · 1 Security review · 1 Security fix. CWE column empty
throughout (correct — no CWE-shaped diff exists in this lane).

## Against our own declarations: disagreements cut FOR the classifier

Our subjects declare verification *levels*; it declares change *types* — orthogonal
axes, so no direct contradiction was possible, and none occurred. Where they meet:

- **It read the body over the prefix, correctly:** `feat(gates): stage 95 ...
  and mine was wrong` → Bug fix (the body confesses a fix; the prefix says feat).
- **Agreed** on every plain `fix:` commit (routing-backtest pricing, selftest
  wiring, UNMEASURED laundering).
- **Misses (its taxonomy edges, not our honesty):** `fix(githooks)` b801c10 —
  a real commit-gate logic fix — → Metadata review; `fix(oracle)` bind-figures
  → Unclassified (should be Bug fix); `feat(oracle): first live Jev call` →
  Security fix (false positive with teeth: nothing security-shaped);
  vendor-19 → Observability (stretch); `test(compaction)` withhold →
  API change (wrong axis).
- **Pattern:** a review-heavy lane exposes its bias — everything evaluative
  (test reports, oracle repros, rulings) collapses into Metadata review, and
  the abstentions cluster where our level tags live. The disagreements say the
  classifier needs a finer review-axis, not that our subjects lie.

## Worth building on

Conventional-commit prefixes are cheap talk and the classifier knows it — the
stage-95 catch proves body-reading beats prefix-reading. Any lane-side
commit lint should grade bodies, not prefixes.

## NOT RE-SCORABLE — 2026-09-24

`/tmp/tr/mine-out/jev-130.csv` is gone. The receipt said the raw CSV lived only there. README claims that cite this receipt: none found.

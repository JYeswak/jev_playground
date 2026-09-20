# jev-real-corpus-eval — score the frozen toolcall corpus

One-command offline scorer for `work/p3-calibration/toolcall-corpus-frozen.jsonl`
(**n=7846**, GOOD=1665 / BAD=6181). Not a `diagnostic_synthetic` battery.
Package shape copied from `work/skillranker-eval/`. Loss is
`oracle-kit/decisionLoss` (0/1/2). No TYPESAFE key.

```bash
python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py \
  work/p3-calibration/toolcall-corpus-frozen.jsonl
node work/jev-real-corpus-eval/run.mjs
node --test work/jev-real-corpus-eval/test/score.test.mjs
```

Studio (baked): always-abstain **0.212210043** (1665/7846);
isError-only **1.495284221** (11732/7846). isError-only loses.
A useful Jev judge must beat **0.212** mean loss on this split.

`corpus.jsonl` is a symlink to the frozen file. Counts + sha256 are locked;
a 10-row authored substitute is refused, not scored.

**Mapping:** Choice `{allow, abstain}`. GOOD → allow. BAD → abstain.
always-abstain is the required control. The field baseline is
`isError ? abstain : allow`. Tool-name is not a separator here (7845/7846 bash).

Receipt: `docs/demos/upstream-repro/frozen-toolcall-scorer-20260920.md`.
`[pending]` / promoted=0 until Joshua promotes.

CASS (`/Volumes/ZestData/cass-data/agent_search.db`) and live agent-mail are
**not** queried from this cloud VM. Next offline-export levers only.

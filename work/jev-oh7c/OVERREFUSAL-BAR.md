# Result-commit evidence gate: over-refusal bar

**Status: preregistered before labels are read.** Freeze timestamp: 2026-10-06T20:04:44Z. No sample labels have been inspected or assigned at this point.

## Frozen rule

- Population: commits refused by `scripts/result_commit_evidence.py --commit <sha>` in the fixed seven-day replay window below, excluding commits attributed to the seven named training incidents. Four incident classes map to five SHA commits: R147 `2e31da61bddad6892cebb9297a8e0a2439f43244`; R149 `a1b0234a0ed138695e021ab0c9d206ea92408b8f` and `36e83b694435e9555c10bf5f03878ad7d3e899f7`; R142 `d31ebd7daa6703116be136877341e76700994a9c`; 9yjh labels `d4e16f996e322e92e68860a20901049e37e64391`; double-read is the census row in `EVAL.md:3663` (`ddac64a0093635853eae514d6f450bbcc60a7feb`); xdzh freeze hash `ddc7c2589a58171e607ee8c14e858480a658ceb2`; census crash and repair `ddac64a0093635853eae514d6f450bbcc60a7feb` and `c3e02d15371376b942f190caa75a706104d0c85d`. Overlapping names and multi-commit cases make eight excluded SHAs total.
- Sample: simple random sample without replacement of `n = 60` from the sorted eligible commit SHA list; PRNG `random.Random(20261006).sample(population, 60)`. The seed, eligibility rule, sample size, and method are immutable after labeling starts.
- Labels: `truly-missing` means the required evidence does not exist in committed history by path and blob SHA; `present-elsewhere` means matching evidence exists in committed history but the result commit is refused for not carrying/reference-linking it.
- Error: each `present-elsewhere` label is one false refusal. Missing/ambiguous source evidence is not silently excluded; record it as an error and fail the bar pending adjudication.
- Acceptance: two-sided 95% Wilson upper bound for the false-refusal rate must be `<= 0.10`. At `n=60`, 0 false refusals gives upper bound 0.0602; 1 gives 0.0886; 2 gives 0.1136 and fails. Sample size and bar cannot change after labeling starts.

## Replay receipt

- Replay command: all commits from the pinned `--since`/`--until` window were checked individually with `python3 scripts/result_commit_evidence.py --commit <sha>`; results saved to an owned scratch receipt during the run.
- Candidate commits: 582
- Result-changing commits: 100
- Refusals: 100
- Errors: 0
- No-result-change commits: 482
- Seven historical incident outcomes: R147 1/1 refused; R149 2/2 refused; R142 1/1 refused; 9yjh labels 1/1 refused; double-read census row refused (shared `ddac64a…` commit); xdzh 1/1 refused; census crash/repair 2/2 refused. Miss falsifier met (at least 2/7).
- Eligible non-training refusals: 92 (100 refusals minus 8 excluded SHAs)
- Sample SHA list (seed 20261006; Python `random.Random(20261006).sample(sorted_eligible, 60)`; labels still unread):
  - `a9b02bc19344f75eaf7eb56a6026b19891153760`
  - `19402ec37304ce5e3c99dd9c69523d04d30c5610`
  - `f0001f8e6d8b63e6d5e3005f7ec25f5d004dbaac`
  - `5d2881527bb181e74d0634a7bb4c31a213253f7b`
  - `f2f2bb091474c79a489e2a1e0f34fcf375313432`
  - `acdedb1615b0db95b9ea801f0541134cdc7f30b8`
  - `4b996c3a1c23b299a4387c0502af640d1018e9af`
  - `b95799b6319bcb8d3830b71f7e8c2e1c9ba78500`
  - `541055bc3243547654ca7b2ca93ce710794bc8c7`
  - `ada5f9a69f8280dbcc210399e67c86827849b694`
  - `dba7970aa2e675b32897694f042ba5d6c0015a17`
  - `e3b98e26cd6c85b2a3b13907f3147159c188f487`
  - `b4ea50556e77e74d78637d130b374f6152244e92`
  - `067f34f6c00189a173c57a69f7154d6516d420b7`
  - `24141533f9102019f1c75060e7bf2493f7477366`
  - `022ccf2748f50488092b7c1d0c48b9ad531c67bb`
  - `55394f47deb875a9436ed15a2d349005a8429ad1`
  - `27defa97a57c5822670b5de028c17514c247498a`
  - `f6595241916c3d36e41718cf33b44ea06ffc029b`
  - `58470d98c3868ed687dbdacc4717f8e538f5715f`
  - `a002559dbe493193f8a8f84df5991ea65eb5b05c`
  - `956cd1104774c2bbbe70127dfb4497cdd74f831d`
  - `7f22cfa4bff8aa86a40a46edcee49187cd22d7a5`
  - `515b037b1ca230720c58bddc07edf7ccf8110914`
  - `00886cdbc64b3d2d02c1d17384e74876c67482c4`
  - `bc9fd2a076df0d88f924505e451fc94afcb77b82`
  - `39ebaa94f025fe5ce79848f2756618cb52e5c6fc`
  - `fcc721e14b29b7c021219b08d7a7f822db065524`
  - `2da4d32bae109cdfe95b1866afcbcd37ce5b2884`
  - `cf76e2b820882cffaec2ff45d1da1f0db51173fb`
  - `0d480d87b2a72fbdb374969dd90693792219e650`
  - `ad318c303a2c2e7743879090b17bc2dbdb159c14`
  - `7b9376c865b3f9ad96c6d19981787fcbde6a3d17`
  - `6622f7a4dd61721a25a7d82c6b66b41db45d1706`
  - `e5cbc86899d25a1d266e21d63783e8239ec65454`
  - `065f8b50ee81f7d16e8dbb6ca78d0ae5168a0f2e`
  - `ced3e43474a5d082afa068398d6017c199eda980`
  - `7031281255c22faaf60cb511929d63962e1bdab9`
  - `0b6f76649d096e75ecbcd089004c7e32af9a29e7`
  - `758faf9933fc1af74a89c58b69fca56f7e461f11`
  - `b340c8cf20501ebf246d5d244fffdfd14b1bf62f`
  - `d630a1c1871b17e64fb3d3baba465fa35101cea8`
  - `1ba40655db47c25b5b7dbd68be771e958c4adc22`
  - `ab0efa474448ff8742602d388221846804dbbb87`
  - `0beaa279b0a94218833356af013999fb6c4e398b`
  - `488bf09c5aacfd90b83cd271c641f7537d00e04f`
  - `57b71583e2e586e1a9b188a850ed04bb581b55e3`
  - `bddbd03d8d83967b112019bf3d5471770511d063`
  - `a2103172325fddd039b09133c97c3d2c640cdb03`
  - `3de213aaa1ce51c72b6b7bf941321bd630c22bad`
  - `73f4d12e0b2dbf3726ddff15a5f3aa2ca1808056`
  - `04ce5405f594619115db179244914e9c76902070`
  - `bace55844d127738c1a304b80e4c2f778a7f2583`
  - `94449dea9ca4688a128744fa37d2c07b7846c4a7`
  - `e011dd57242205d5eed7f8b32e76ffe6abd99df9`
  - `2b58257e331537b4f3d3b1b5b0dc8fb73a8c84fb`
  - `a52f692ad133bf9feb5bbcbbd15d44472df7c4b4`
  - `94e13737a27d3caec55d8453e0968924a68f48f4`
  - `da34319eab3d718ca7f130ae389b3e5ada0a2820`
  - `617976986cee6052288ddb610bdd0efd7dcc3254`
- False-refusal count / Wilson upper bound: 18/60 = 0.300; two-sided 95% Wilson upper = 0.4251 (frozen threshold <= 0.10).
- Verdict: FAIL. The over-refusal bar does not authorize hook wiring; leave `githooks/pre-commit` unchanged.
 
## Label receipt (after frozen sample)

- Labels: 60 unique frozen SHAs; 42 `truly-missing`, 18 `present-elsewhere`, 0 unresolved.
- Label artifact SHA-256: `551961daa9df6a3e9945f5575cd7f65dcc91eb49cc48e4888eff8cd483dc498f`.
- False-refusal samples: 6, 9, 12, 14, 15, 16, 20, 31, 32, 33, 34, 36, 38, 39, 43, 47, 51, 52.
- Classification rule: `present-elsewhere` requires matching committed result rows, scorer, and split/seed with source paths and Git blob IDs recorded in `overrefusal-labels.jsonl`; partial bundles remain `truly-missing`.

A passing replay and bar do not authorize wiring by this worker. `githooks/pre-commit` changes require the `KIT_GATE_EDIT` path and conductor application.

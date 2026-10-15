# CHANGELOG — jev lane

Scope: 3,683 commits on `main`, 2026-09-17 → 2026-10-02, distilled into
capability waves (not a commit dump). Every SHA below is verifiable with
`git show <sha>`. Workstream detail lives in bead records
(`.beads/issues.jsonl`) and `EVAL.md`. No GitHub releases exist; the lane
ships on `main` only.

## Version spine

- `session/2026-09-17-lane-substrate` (2026-09-17): lane substrate handoff —
  git init with allowlist ignore, six-stage gate suite, pinned upstream
  mirrors, ripwire 0.6.1.

## 2026-09-17 → 2026-09-24 — evaluation lane

Read-mostly evaluation of the public Jev ecosystem: vendored TypeSafe docs
and SDKs, SDK client work (`kit/`), gate suite growth, hook and pipeline
experiments (demos, dispatches, upstream reproductions), benchmark games
(Jericho, PokéJev). Representative: `b74704c9` (EVAL: Jev serves omp's
native judge role, 1,711 calls/24h), `34f95aae` (README stranger-run fixes,
claim coverage 110/111).

## 2026-09-25 → 2026-09-30 — mission pivot: Jev ON where we work

Joshua's pivot (doctrine: Jev turned ON in the tools we use and proven
live). Surfaces went live with both-ways proofs: native judge
(`b74704c9`), skill hint (`9b55da3f`), rerank shadow (`9aa0372b`),
TTSR claim rule (`60b7a338`), fleet needs-human paging (`be74fcf2`),
memory-filter shadow (`5e00575e`), gate cascade built (`2bcfaf7f`),
injection shadow (`9abe975b`), webscreen enforce on Jev-only flags
(`3ad7adfb`). Infrastructure: surface inventory with live-vs-claim
conformance (`b9df6d9d`, `3c062564`), key provider
(`c7a82107`), AGENTS.md rightsized, docs/LEDGER.md claim registry with
coverage floor, README claim coverage to 114/115 (`283aa72a`), stranger
runnable (`05b6c458`, `34f95aae`). Parked with receipts: game and benchmark
runs, free-comparator arms (see NEGATIVE_EVIDENCE.md).

## 2026-10-01 → present — hardening and rollout

- Legacy alias canary (`jev-jh6f`): the missing-secret-manager test now injects
  its notifier, and a PATH trap rejects accidental default-notifier execution.
  HTTP-boundary tests replace policy-only tests; non-object JSON reports ERROR
  rather than raising AttributeError. Targeted 22 tests pass with network,
  Apple Events and the system notifier denied; the deliberate omitted-injection
  control is caught. This does not activate the legacy monitor or prove the
  current Clef/Cloudflare judge chain healthy.

- Cascade: paid fallback on local failure (`4fd0f367`), fence-tested live;
  deterministic pre-rule for the destructive class (`d5348d42`).
- Memory filter: removal path with file switch, verified live both ways
  (`5fc68a4e` work; switch ON by conductor decision).
- Skill hint N2: Noul-rank 0/48 misroutes but 0/48 hints — safe but useless,
  not re-registered (`8cc6b66d`).
- Machine-wide rollout (`jev-j0er`): webscreen + injection screens as
  shadow in five profiles (`7c36b2c7`; hardlinks, not symlinks — omp
  discovery skips symlinks), drift conformance on inode+sha (`0246dd45`),
  24h shadow sample with committed exclusions (`e6f68b4c`, `8ee3432b`).
- Duel (`jev-n4eu`): one orchestrating handler over both screens,
  EQ-600 agreement 600/600 with incumbent-exact rates (`ffae4c44`).
- Sweep repairs: npm test wiring restored (kit, jev-client), claim floor
  raised to match registered claims (`f19406be` + floor sync).
- Verifications closed with evidence: `jev-nbbm` (pre-rule), `jev-9q1g`
  filed (claim-gate removal arm brittle at perfect coverage).
- Candidate checker (`jev-wjig`): G1 prior-sample overlap is limited to replications.
- Gate observer privacy (`jev-rpqu`): committed hook versions write shared logs
  with only `cmdSha`, keep raw commands in the private sidecar, and rotate
  private archives; live migration remains pending coordinated session restarts.
- Local shadow timeout (`jev-a5ny`): the opt-in local scorer now shares one
  2 s deadline across a commit's hunks; a slow loopback endpoint test proves it
  aborts within budget and skips later local requests.
- Fleet delivery/telemetry (`jev-06wt`): exact mail IDs and payloads persist
  before transport; queued admission is not delivery. Confirmed sends commit
  only delivered IDs, while failed/uncertain flushes retain evidence without
  blind retries. Catch-up is bounded without discarding unread backlog.
  Heartbeat denominators/decisions now use actual session-storage profiles
  and declared installed scope; missing scope is unknown, not healthy.
  Existing thresholds and intentional OFF markers remain unchanged.
  Offline source-path smoke and 135 watcher / 16 sampler regressions pass;
  service reactivation and supervised live delivery are not claimed.
- Publication canary: user-approved cleanup now retains repo-owned `.owner`
  scratch for the reaper instead of direct removal. Assertions/refusals are
  unchanged; real fire/quiet and no-op-checker rejection controls pass.
- Stranger-run CI (`jev-qx7b`): classify the complete typed doctor envelope
  before the 300-character diagnostic display limit. The original
  `NOT_RUN-no-key` expectation stays unchanged; malformed, unsupported and
  contradictory envelopes are refused. Archived scheduled-run replay and
  positive/negative selftests pass; the failed CI run was not rerun.
- Native tracker repair (2026-10-11, local): installed unmodified upstream
  `a0b9c8525d9bf6f44feb612a1baeca603d2d9a83`, retaining the old executable.
  Ordinary canonical writes, fresh-process readbacks and strict export now
  pass; sync is healthy, dirty count 0, 675 issues with no coverage drift.
  Historical failed-recovery evidence is unchanged. Native export now omits
  machine-local `source_repo_path`, as documented by br; portable
  `source_repo` and all other pre-existing issue facts are preserved.
  No bead closure or classifier verdict implied.
- CLI error regression coverage (`jev-b35c.54`): retain the online-required
  exit-code check without pinning incidental formatter copy. Human and robot
  usage smokes return exit 64; 14 keyless error cases pass. This is maintenance,
  not a new backend capability or a full-kit pass.

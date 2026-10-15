# Bootstrap prerequisite plan: jev-owned Clef-Flash server promotion (oy76 items 1-2 only)

Lane: AM54585 (JadeSpire) + user decision AM54499/AMP54511: all-five native
judge local clef/clef-flash -> hosted CF clef-flash ONLY, TypeSafe OUT.
This leaf covers oy76 acceptance items 1-2 (tracked server + lifecycle).
Item 3 (gateway attribution) stays with oy76/k3yw/kit-jtq2 and is NOT claimed
done here. Verifier: QuietBadger. Model: Clef Flash ONLY (no full download).

## Source

Original staging `var/agent-tmp/clef-flash.conductor/serve.py` was reaped
(path verified gone 2026-10-15). Canonical retained source:
`var/agent-tmp/clef-serve.dadu.20261010/serve.py` (owner pid 22427, Oct 10-11):
spec-rebuilt from `work/plan-20261004/specs/clef-backend-spec.md`, serves
POST System One via `joint_schema_model.systemone` under one global lock,
`GET /` returns `{"models":[{"id":"clef-flash"}],"fingerprint":
{joint_head_sha256, index_sha256}}` computed over file BYTES (not names),
loopback 127.0.0.1:8010 only. Provenance alongside: serve.log, score.json.

Promotion = copy + harden under these exact leases (139721-139725, to 06:12Z).
No parallel stack, no global-config edits (LavenderDune owns all 10 targets).

## Files (all under lease)

- `work/clef-serve/serve.py`: promoted server, byte-fingerprint GET, locked
  POST, loopback-only bind. Unchanged semantics from retained source except
  tracked-home import path and owned-PID file support.
- `work/clef-serve/fingerprint.py`: `fingerprint(weights_dir)` extracted as a
  pure function (sha256 over joint_head.safetensors +
  model.safetensors.index.json bytes).
- `work/clef-serve/test_fingerprint.py`: `python3 -m unittest` passes:
  fingerprint of a temp dir with known bytes equals hashlib's value (no model
  load). Planted negative: fingerprint computed over file NAMES instead of
  bytes FAILS (must differ).
- `scripts/clef-serve.sh` (`start|stop|status`): ONLY way jev starts/stops the
  test server; writes owned PID file; `status` prints port + fingerprint;
  a server on :8010 NOT started via the script is reported not jev-owned.
- `work/clef-serve/PLAN.md`: this file.

## Acceptance (leaf; oy76 full bar preserved, not weakened)

1. `python3 -m unittest work/clef-serve/test_fingerprint.py` -> exit 0;
   planted filename-variant -> FAIL (exit nonzero).
2. `bash scripts/clef-serve.sh start` with local Clef-Flash weights loaded
(owned test process), then `status` shows :8010 + live byte fingerprint;
`stop` stops it (PID gone, port closed). Foreign :8010 listener ->
reported not jev-owned. A `--no-model` fingerprint-only run is a separately
named OFFLINE control, never the lifecycle proof: if weights/admission are
unavailable, this leg is reported NOT_RUN, not green.
3. No gateway claim: attribution/route acceptance stays oy76 item 3.
   Current upstream state (TopazTrout AM54523): kit-jtq2 in_progress/TopazTrout,
   ETA UNKNOWN; `/jev/clef-flash/` -> 502; `:8010` ECONNREFUSED.

## Non-goals / prohibitions

- No POST to `:8010` in production paths; gateway `/jev/clef-flash` only.
- No `:11434` use, no daemon/launchd/bootstrap, no unload/kill of others.
- No TypeSafe calls, no golden regeneration, no full-Clef weights.
- No commit/push by worker beyond local candidate declaration; land refusal
  -> declare candidate SHA+paths on the leaf bead, never raw push.
- Native judge failover must not use chat retry; source-bound proof required.

## Entry / Exit

- Entry: leaf bead claimed; leases valid; retained source readable.
- Exit: acceptances 1-2 green with N/model/date/latency/spend/hash reported;
  DONE to director with exact cmd/output/exit; no self-close.

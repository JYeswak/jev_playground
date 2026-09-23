# W7.0 EVAL sections — pane 2 — 2026-09-23

For SunnyTiger to append to `EVAL.md`. This file is not `EVAL.md`. Agent Mail could not reserve it. Old receipts are leads. Live smokes below were not re-run by pane 2.

## jev-mcp @ 6ec5efc

- Re-run 2026-09-22: `npm test` → 9 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-mcp-w70-20260922.md`, commit `d12027d`.
- T9 fail, source: `dist/index.js:108` maps an unknown choice to `"unknown"` and still copies `confidence`. A missing key exits the process.
- Live smoke in that receipt was not re-run here. N=1 is a smoke, not a certification.
- Boundary: unit suite and the coerce line only.

## jev-review @ 57690af

- Re-run 2026-09-22: `npm test` → 13 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-review-w70-20260922.md`, commit `07041c2`.
- Clone source sends `jev-latest`. The pin in the receipt was applied in the harness, not in the clone.
- Live smoke not re-run here.
- Boundary: offline suite only.

## jev-router @ 86660a0

- Re-run 2026-09-22: clean archive `86660a0248eba0e4523f81645ac2925e9808c000`, `npm test` → 58 pass, 0 fail, 0 skip, exit 0. Receipt `docs/demos/upstream-repro/jev-router-w70-20260922.md`, commit `5929bbf`.
- Production path sends `jev-latest` unless `TYPESAFE_DEFAULT_MODEL` is set. Live smoke not re-run here.
- Boundary: offline suite on a clean archive.

## jev-codex-router @ 8292b519

- Re-checked pin `8292b519659280884627a962c826ac7721136a64`, porcelain empty. Receipt `docs/demos/upstream-repro/jev-codex-router-w70-20260922.md`, commit `6aafeec`.
- `server/jev_server.py:717-718` turns a Jev exception into an astra route. Missing key at line 721 also becomes astra. Host stays up. T9 fail is that coerce.
- Live smoke N=12 not re-run here. No accuracy claim.
- Boundary: pin, cleanliness, and the coerce lines. No second paid call.

## fast-jev-compaction @ 6e1da50

- Re-run 2026-09-22: `npm test` in the dirty tree → 29 pass, 0 fail, exit 0. Lockfile not touched by this run.
- Receipt file `docs/demos/upstream-repro/fast-jev-compaction-w70-20260922.md` is inside `d64c2f1` (subject is pane 4's mechanism-transfer commit, author Josh). Not re-committed by pane 2.
- Live smoke in that receipt not re-run here. T9 in the agent's summary said no client deadline and missing key throws. Not re-derived in this section.
- Boundary: offline suite only.

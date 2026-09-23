# m0e non-author verification — pane 5 (SunnyTiger, Muse Spark 1.3)

Target: 13 appended rows in `notes/packet-numbers-p5.tsv` (AmberWillow, 4bd9fe0) + B5 row in `notes/kit-gap-v8.tsv`. Method: own extraction, own commands. Verdict per row: CONFIRMED or REFUTED.

## Token extraction (mine, not the author's)

- Hex tokens 7–9 chars in `foundation/kit/packet.md`: `rg -o -N '\b[0-9a-f]{7,9}\b'` → 118180e(1×), 118185e(2×), 66880cc, 943158c, c84d562. All five appear as rows (prior rows 7–10 cover four; the L8 row covers the 118180e/118185e pair).
- Packet headings: `rg -n '^## [0-9]+'` → sections 1–12 present. Template (`/tmp/jev-rc-p1/fa48/starter-kit/templates/planning-packet.md`) headings: sections 1–12 present, identical titles; template §8 carries a ` [PROVISIONAL]` suffix the packet drops.

## Rows 18–28: 11 section ordinals — all CONFIRMED

Each row claims packet.md heading N is the template's heading N. Paste-compared all 12 pairs independently: titles match verbatim for 2–12 (tried to refute via the §8 PROVISIONAL suffix — fails, the rows claim ordinals only, and the ordinals agree).

## Row 29: MISS (packet.md:112 cites untracked p5 draft) — CONFIRMED, three routes

1. `git ls-files notes/foundation-packet-p5.md` → empty output (untracked).
2. `git status --short notes/foundation-packet-p5.md` → `?? notes/foundation-packet-p5.md`.
3. `git log --all --oneline -- notes/foundation-packet-p5.md` → empty (0 commits).
Packet line 112 reads "Pane 5 drafted notes/foundation-packet-p5.md." A fresh clone cannot open the cited file. MISS stands.

## Row 30: MATCH (token 23 is the UTC day of a53190f) — CONFIRMED

`git log -1 --format=%ci a53190f` → `2026-09-22 18:52:22 -0600` = 2026-09-23 00:52 UTC. Day is 23 in UTC, 22 local. The row's rationale (UTC day, not local) checks out exactly.

## B5 gap row (kit-gap-v8.tsv, corrected by AmberWillow at 4bd9fe0) — CONFIRMED from git behaviour

Row claims: `core.hooksPath=githooks` (`.git/config:8`) makes `.git/hooks/*` inert; live `githooks/pre-commit` runs staged-deletion + autofix-check lanes; no canary.
1. Behaviour: in `/tmp/hooktest`, set `core.hooksPath` to a dir whose `pre-commit` echoes CUSTOM-HOOK-RAN and exits 1, with a competing `.git/hooks/pre-commit` echoing DOTGIT-HOOK-RAN. `git commit` printed CUSTOM-HOOK-RAN only and exited 1. The hooksPath hook runs; the `.git/hooks` copy is inert. (Scratch repo removed.)
2. Source: `githooks/pre-commit:5` (LANE 1 staged-deletion) and `:12` (LANE 2 autofix --check); `rg -c -i canary` = 0 in `githooks/pre-commit`, `githooks/commit-msg`, `.git/hooks/commit-msg`. `.git/config:8` reads `hooksPath = /Users/josh/Developer/jev/githooks`.
3. Refutation attempt (config could lie about what git does): the /tmp experiment refutes the lie — behaviour matches config.

## Residual (not a refutation)

Strict token-exhaustiveness would also row date fragments (2026, 09) appearing in sign-off lines. The rows cover semantic numbers (ordinals, SHAs, metrics, thresholds, counts); dates are identified by the one row that needs a date (row 30). Judged out of the acceptance's spirit, recorded here so the next auditor sees the boundary.

## Tally: 13/13 appended rows CONFIRMED, B5 CONFIRMED, 0 REFUTED.

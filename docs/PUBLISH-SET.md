# Publish set for `jev_playground` (bead `jev-publish-playground-hog.1`)

Mechanism, not an argument: tip scrubs cannot satisfy a public-repo acceptance
while history is published unrewritten (measured 2026-09-18: tip 122
`~` occurrences + 7 `thinkingSignature` prose mentions, history 367
`~` added-lines + 104 `thinkingSignature` added-lines). So the public
repo begins at its first commit, already clean: NOTHING is rewritten — the local
repo, its history, and `local dir stays jev/` are untouched. Tip == history by
construction, which is why the export scan below is provable instead of hopeful.

Built by `scripts/publish-export.sh` (idempotent, re-runnable): `git archive`
of the allowlist below → content transforms → single commit on an orphan
branch. The script scans the EXPORT, never the working tree.

## Allowlist: everything tracked EXCEPT

- `.beads/` — internal fleet tracker shared through git. Holds operator paths,
  agent names, machine detail on 16+ lines, and re-accumulates paths with every
  future bead: scrubbing it is a treadmill. Boundary problem, not content.
- `docs/demos/duel-1/dispatch/` and `docs/demos/duel-2/dispatch/` — internal
  pane coordination packets (live operator paths, relay chatter). The demos and
  receipts they produced ARE published; the coordination is not.
- The export worktree itself (`../jev_playground-export/`, outside this repo).
1. `~` → `~` (operator home must read portably).
2. `ENCRYPTED_BLOB` → `ENCRYPTED_BLOB` (keeps the redteam/hardening prose
   readable while guaranteeing no line can be mistaken for a real blob).

## Scan contract (over the export's full history)

- `0` occurrences of `~`.
- `0` occurrences of `ENCRYPTED_BLOB`.
- Key shapes (`AKIA[0-9A-Z]{16}`, `sk-live-…{8,}`, `ghp_…{16,}`,
  `xox…-…{8,}`, `Bearer ey…`, `BEGIN … PRIVATE KEY`): `0` UNEXPLAINED hits.
  Bare pattern NAMES in demo prose (`AKIA`, "ghp-like") do not count — shapes
  do. Known-benign (checked in, with reason):
  - `AKIAIOSFODNN7EXAMPLE` — AWS's published documentation example key, used in
    `demos/preaction-abstention/` fixtures/tests and named in its redaction
    tests. Designed for this purpose; not a credential.
  - `/AKIA[0-9A-Z]{16}/`, `/sk-live-[A-Za-z0-9]+/` in
    `demos/preaction-abstention/src/redact.mjs` — the redactor's own patterns;
    the scanner matching the scanner is expected.
  - Any NEW hit is a fail-closed ERROR, never a silent pass.

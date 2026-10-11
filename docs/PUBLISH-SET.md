# Publish set for `jev_playground` (bead `jev-publish-playground-hog.1`)

Mechanism, not an argument: tip scrubs cannot satisfy a public-repo acceptance
while history is published unrewritten (measured 2026-09-18: tip 122
`/Users/josh` occurrences + 7 `thinkingSignature` prose mentions, history 367
`/Users/josh` added-lines + 104 `thinkingSignature` added-lines). So the public
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
1. `/Users/josh` → `~` (operator home must read portably).
2. `encrypted_content` → `ENCRYPTED_BLOB` (keeps the redteam/hardening prose
   readable while guaranteeing no line can be mistaken for a real blob).
3. A `thinkingSignature` value of 100 or more base64-ish characters →
   `THINKING_SIGNATURE_BLOB` (jev-x5cy). The key and the prose around it stay; only the
   opaque value goes. The source files are untouched (the original evidence is preserved in the
   private repo); only the export copy is redacted.

## Scan contract (over the export's full history)

- `0` occurrences of `/Users/josh`.
- `0` occurrences of `encrypted_content`.
- Key shapes (`AKIA[0-9A-Z]{16}`, `sk-live-…{8,}`, `ghp_…{16,}`,
  `xox…-…{8,}`, `Bearer ey…`, `BEGIN … PRIVATE KEY`): `0` UNEXPLAINED hits.
  Bare pattern NAMES in demo prose (`AKIA`, "ghp-like") do not count — shapes
  do. Known-benign (checked in, with reason):
  - `AKIAIOSFODNN7EXAMPLE` — AWS's published documentation example key, used in
    `demos/preaction-abstention/` fixtures/tests and named in its redaction
    tests. Designed for this purpose; not a credential.
  - `/AKIA[0-9A-Z]{16}/`, `/sk-live-[A-Za-z0-9]+/` in
    `demos/preaction-abstention/src/redact.mjs` — the redactor's own patterns;
    the scanner matching the scanner is expected. Matched by that exact path only.
  - The AWS example excuses only itself: a line that also carries any other key shape is unexplained.
  - Exact exception rows in `docs/publish-key-exceptions.txt` (jev-x5cy): one row per key-shaped
    LINE read in context and proven synthetic, binding the export-relative path, the sha256 of the
    whole line and its hit count. A row cannot cover another file, an edited line or a second key on
    the same line. No path-wide, directory-wide or pattern-wide rows. The evidence for each row is in
    `docs/evidence/jev-x5cy-key-hit-rulings-20261011.md`.
  - Any NEW hit is a fail-closed ERROR, never a silent pass.
- `0` blob-shaped `thinkingSignature` values (`"thinkingSignature": "` followed by 100+ of
  `A-Za-z0-9+/=_-`). Transform 3 removes them; the scan still refuses any that remain.

## Diagnostics and exit codes

The scan prints counts and `path:line` only. A hit's matched text is never printed, in any mode:
a hit may be a real credential. `scripts/publish-export.sh --scan DIR` scans any tree read-only.
Exit `0` clean, `1` findings, `2` bad usage or a missing tool, `4` scanner error. Exit `4` means a
`grep` or `git` call failed for a reason other than "no match" (grep exits 1 for no match, which is
a clean result), or an exceptions row is malformed: the scan did not complete, which is never a pass.

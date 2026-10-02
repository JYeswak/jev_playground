# Proposal: 30hi post-commit shadow seam (bead jev-30hi follow-up)

Verdict to carry: vendor-paste Noul (cut 0.35) held prec 0.842 / rec 0.640 on
file windows; 12/76 vetoes wrong. That error rate blocks real commits, so the
seam is POST-COMMIT shadow-first, never pre-commit blocking.

## Design

After each commit on main (githooks/post-commit or an omp session-stop hook
reading the HEAD diff — pick one, not both), score added hunks outside
upstream/ and docs-mirror/ with the frozen vendor Noul and append would-flag
rows {ts, commit, file, hunk_sha, noul, would_flag, model, tokens} to
`~/.local/state/jev/vendor-paste-shadow.jsonl` (hashes, never raw text; prompt
text nowhere). Bounded: per-commit call cap + daily cap in code, stop on
401/402/403, fail-open (a missed score logs nothing and never touches the
commit — post-commit cannot block by construction).

## Why post-commit, not pre-commit

Pre-commit runs inside the commit path: a 0.16 false-flag rate pages authors
on every sixth paste-looking hunk and adds Jev latency to every commit. The
wbel lesson (0.335 organic precision) also says: shadow first, blind-label,
then decide. Post-commit keeps the working tree sacred and still builds the
label pool for an enforcement decision.

## Bar to pre-commit warn (locked before the shadow starts)

Blind-label 2 weeks of would-flag rows: enforce (pre-commit warn, still not
block) iff precision >= 0.90 AND miss <= 0.10 with >= 30 would-flags.
Higher than wbel's 0.80/0.10 because it gates our own commits. Block stays
off the table until a second confirmation.

## Open (not decided here)

Upstream/docs-mirror self-syncs excluded (they ARE vendored by construction);
work/ dependency trees excluded (same exclusion as the corpus). Monorepo
slugs outside jev: out of scope for the first seam.

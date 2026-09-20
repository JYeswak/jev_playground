# Explain-before-override (dcg refusals)

When dcg refuses a command, the refusal is evidence, not an obstacle. This file
encodes the response: explain, then take a narrower path — never reshape the
command to evade the pattern that fired.

## The five conductor cases (stated 2026-09-20, provenance: dispatch)

| # | refused | dcg right because | safe alternative taken |
|---|---|---|---|
| 1 | `rm -rf` on a home-adjacent path | recursive delete near `$HOME` | explicit narrow path or abandon |
| 2 | recursive delete | blast radius exceeds the named target | list first, delete named files |
| 3 | `find -delete` | unpreviewed mass delete | `find` without `-delete`, review, then act |
| 4 | `git stash` worktree-wide | sweeps siblings' work | explicit `git stash push -- <path>` |
| 5 | `git checkout --` discard | destroys uncommitted work | explicit copies before any discard |

## Pane-3 verified instances (this session, quoted)

- `python3 -c "... 'rm' + ' -rf' ..."` → `dcg denied (core.filesystem:rm-rf-general)`.
  Alternative taken: wrote `/tmp/dcg-cat.py` via the write tool, ran it. No evasion.
- Heredoc redirect (`cat > file <<EOF` in bash) → denied
  (`redirect-truncate-root-home`, `redirect-truncate-dynamic-path`). Alternative
  taken: write tool with explicit path throughout.
- `rm -rf ~/override-probe-d` → `dcg denied (core.filesystem:rm-rf-root-home)`.
  Alternative taken: `mkdir -p /tmp/override-demo && touch .../f && rm .../f`
  (explicit single file, no `-r`), then `rmdir`. Quoted live row below.

## Live row (P7, 2026-09-20)

```
denied:  dcg denied the bash tool call (core.filesystem:rm-rf-root-home)
taken:   EXPLICIT-SINGLE-FILE-REMOVE-OK + CLEAN (mkdir/touch/rm/rmdir, /tmp/override-demo)
```

## Rule (for agents)

1. Quote the denial. Name the pattern (`rm-rf-root-home`, etc.).
2. State what the refused command would have touched beyond the named target.
3. Take the narrower path with explicit paths, or abandon with the reason.
4. NEVER reshape to evade (renaming flags, splitting across calls, encoding the
   path). An evasion that succeeds is a defect in the session, not a win.

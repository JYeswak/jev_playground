# Gate-edit session 8 (`KIT_GATE_EDIT=1`) - secret obfuscation and the pre-commit remedy

From pane 1 AmberWillow, 2026-09-25. Joshua approved this kind of session ("approval on all",
2026-09-24). The flag lets you edit kit gate paths (`.omp/kit-guard.json` gatePaths, which include
`.omp/config.yml` and `githooks/*`). Do the two items below, then exit. Nothing else.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. Both items make omp and git protect the fleet from its own mistakes: item A
keeps the TypeSafe key out of every model provider's view, item B stops commits carrying another
pane's files.

## 2. Tools and skills

- Read `/Users/josh/.claude/skills/verification-before-completion/SKILL.md` before claiming either
  item done; quote the output that proves it.
- Item A proof uses `/tmp/sectest-run.py` (pane 1's probe; plants a FAKE key of the live shape,
  never the real key). Item B uses `~/Developer/foundry/loop-kit/autofix-precommit.sh`, which
  accepts explicit files (`--repo <repo> -- <files>`; its contract item 1: only files in argv).
- Commit with `git commit --only -m "..." -- <paths>`. Never run `autofix --staged`: in this shared
  tree it rewrites other panes' staged files (that is item B's bug).

## 3. Item A - bead jev-xw3f: turn on omp secret obfuscation for the TypeSafe key

Why: at ~05:57Z pane 5 printed the live `TYPESAFE_API_KEY` into a tool result; the codex profile
replays tool results to OpenAI. omp redacts secrets before they reach a provider, but it is off
(`secrets.enabled` default false), and its built-in token patterns do not match this key's shape.
Pane 1 proved both in scratch (bead comment, 06:53Z): with the regex the model saw a 33-character
placeholder; secrets on without the regex, it saw all 107 characters.

1. Register with Agent Mail under a fresh name. Reserve `.omp/secrets.yml` and `.omp/config.yml`,
   reason `gate-edit-8`.
2. Create `.omp/secrets.yml` exactly:
   ```yaml
   - type: regex
     content: "apikey_[a-z0-9]{35}_[a-z0-9]{64}"
     friendlyName: TypeSafe API key
   ```
   (The shape was measured from the live key without printing it: `apikey_` + 35 + `_` + 64,
   lowercase letters and digits, 107 characters. It is a pattern, not the key.)
3. In `.omp/config.yml`, add a `secrets:` block with `enabled: true`, preceded by a comment in the
   file's existing style: why (the 05:57Z incident, bead jev-xw3f), what it redacts (the regex in
   `.omp/secrets.yml` plus omp's built-ins, in provider-visible text including tool results), and
   what it cannot (sessions started before the change keep running unprotected until restart; the
   key arrives per command through `infisical run`, so omp's env-var collector never sees it, and
   the regex is what catches it; local session logs still hold restored values).
4. Prove from the jev cwd, both profiles in use:
   `cd /Users/josh/Developer/jev && omp --profile codex config get secrets.enabled` and the same
   for `claude` must print `true`. Then
   `python3 /tmp/sectest-run.py /Users/josh/Developer/jev claude /tmp/planted-xw3f.txt`
   must end with a line whose LEN is not 107 and whose HEAD starts `$$`. Paste it.
5. `bash foundation/gates.sh --portable` must exit 0 (the config file is gated; a gate may read it).
6. Commit `.omp/secrets.yml .omp/config.yml` path-limited, subject
   `[live] jev-xw3f: omp secret obfuscation for the TypeSafe key shape`. Push. Release.

## 4. Item B - bead jev-06w2: the pre-commit remedy names only this commit's paths

Why: `githooks/pre-commit` lane 2 tells an agent to run `<autofix> --staged --repo <repo>` and then
`git add` what it rewrote. Run by hand, `--staged` reads the real shared index, so it reformats
and re-stages other panes' files. Three times on 2026-09-25: 792b309 carried pane 4's
`notes/deep/next-gen/pokeagent-emerald-scope.md`; a fixer run reformatted pane 3's staged
`work/poke-jev/test_player.py`; c60edae was suspected and cleared.

1. Reserve `githooks/pre-commit` (and the gate stage you extend), reason `gate-edit-8`.
2. In the lane-2 refusal branch (the `if ! "$_autofix" --check --staged ...` block at the end of the
   file), compute this commit's own paths inside the hook with
   `git diff --cached --name-only --diff-filter=ACMR` (under `git commit --only <paths>` the hook
   sees a temporary index holding only those paths) and print the remedy as
   `<autofix> --repo <repo> -- <those paths>` and `git add -- <those paths>`. Keep the check itself
   unchanged. Update the header comment (lines 12-20) to match.
3. Witness, test first: extend the stage that already exercises the hook
   (`foundation/gates.d/60-staged-deletion-lane.sh`, or 80 if that is where hook selftests live)
   before adding a stage. Scratch repo: stage an unclean file `sibling.py`, then
   `git commit --only -m x -- own.py` with an unclean `own.py`. The refusal must name `own.py` and
   must not name `sibling.py` or print `--staged`. Show the witness RED on the current hook text
   first, then GREEN on the new text.
4. `bash foundation/gates.sh --portable` and `bash foundation/gates.sh --selftest --portable` exit 0.
5. Commit path-limited, subject `[mutation] jev-06w2: pre-commit remedy names only the commit's own
   paths`. Push. Release.

## 5. Callback

Comment on jev-xw3f and jev-06w2 with the commit shas and pasted proof lines; leave both
in_progress for pane 1's non-author check. Then `ntm send jev --pane=1 "CALLBACK-GATE8-DONE <shas>"`
and `/exit`. If anything refuses or differs from this packet, stop and send
`CALLBACK-GATE8-BLOCKED <reason>` instead; do not improvise around a gate.

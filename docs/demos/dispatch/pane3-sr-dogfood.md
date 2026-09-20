# P3 — you built it, now find out whether it is any good. Queue of 2.

Verified your install myself: `command -v sr` → `~/.local/bin/sr`, `sr 0.1.0`, and `cmp`
against the port build says **byte-identical**. Three hours ago this was `E0433` with an
ungate producing twenty `nix::sys::statfs` errors. **The port was the right call and the fix
was the non-obvious one** — admission by volume name rather than stubbing storage out.

Two refusals I hit while testing, which I read as correct, not broken:

```
sr rank --latest      -> unavailable / missing-session ("no session in the exact workspace")
sr rank --session X   -> unavailable / unsupported-input   (X was an omp session JSONL)
```

A ranker that declines an unrecognised input beats one that scores it. **But it means nobody
has yet seen `sr` produce a ranking on this machine.**

## Unit 1 — make it rank something, or rule that it cannot here

Find an input it accepts. `--help` lists `--context FILE`, `--transcript FILE --harness NAME`,
`--session PATH`, `--latest`. Work out which harness formats it actually supports (read the
code, not the help text — the help is a claim) and feed it a real one.

Then produce **one ranking over our own skills** with `--json`, and answer the only question
that matters: **is the ranking any good?** Take ~10 ranked results and judge them yourself
against the task context you fed it. Report `USEFUL` / `PLAUSIBLE-BUT-UNCHECKABLE` /
`WRONG`, with the specific rows that decided it.

**`--offline` vs live matters**: run both if it supports both, and say whether the paid call
changed the ranking. If the offline path ranks identically, the model is not earning its seat
here — that is the same test that killed the harm-rule model seat and the tool-call judge.

If no input format we possess is accepted, that is a real ruling: **`sr` is installed and
unusable on our data**, with the reason. Do not manufacture an input to make it succeed.

## Unit 2 — the honest limit you already flagged

Your NO-CLAIM says cache/store is unqualified on mac by upstream design. **Quantify what that
costs us**: does `sr` work without the store, degrade, or silently produce worse rankings?
A tool whose cache layer is unqualified on our only platform has a ceiling, and I want it
stated before anyone builds on it.

## Standing

Your session now has the guard hook bound (`guard-rule.ts`, observe-only, `grep-as-proof` is
the live class after `pipe-exit` was dropped under R51) — **you are dogfooding it by working
normally**, so do not avoid `grep -c`; a fire is data. Exit codes unpiped. `[receipt]` for
result commits. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

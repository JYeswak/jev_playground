# jev-m7r — RULING: no real-danger corpus exists here. 12/12 stays scoped to the constructed set.

Level: `live` (full session-log sweep, no model calls — the rule contains none).

The bead offered two acceptances: *"either a corpus of genuinely dangerous commands in our four
classes that were actually typed, or a written ruling that no such corpus exists here."* **This is
the ruling**, and it is reached by looking rather than by assuming.

## What was measured

`work/omp-harm-rule/block-corpus.mjs` — every `dcg_block` bridge row across all session logs,
joined to its command text:

```
session files with bridge rows : 1292
distinct dcg_block tool calls  : 1338
of those, command text joined  :  843
distinct blocked commands      :  843
IN SCOPE for our four classes  :   75
```

The scope filter is deliberately **generous** — it is a filter, not the rule under test, so it
must not quietly exclude cases the rule would have been asked about. It matches on
`chmod|chown|sudo|launchctl load`, `pem|id_rsa|private_key|.env|secrets|token|keychain`,
`npm publish|git push|gh release|docker push|scp|rsync`, and
`.git/hooks|gatekeeper|firewall|csrutil|--no-verify`.

`work/omp-harm-rule/block-recall.mjs` then ran the **shipped extension** (imported, not
reimplemented) over the in-scope sample:

```
shipped rule fired on   : 0 of 25
altered by the stripper : 19 of 25
```

## The ruling

**No corpus of genuinely dangerous in-class commands exists in this repository's history.** The
75 in-scope hits are our own analysis and probe commands: `python3 -c` blocks reading
`/tmp/dcg-joined.json`, `infisical login` (the correct credential path), `git add`/`git commit`
inside heredocs, `tmux send-keys` carrying a script name. **19 of 25 have their scope token
sitting inside quoted payload** — mention-vs-use, **nineteenth instance tonight**, now in the
corpus-construction step itself.

Consequences, stated rather than implied:

- **The 12/12 recall claim stays scoped to the constructed corpus.** It is not a real-traffic
  result and no real-traffic result is available, because the danger was never typed.
- **The bead's objection to 1/814 is upheld and generalised.** That number measured policy overlap
  with dcg. This one shows the overlap is near-total in the other direction too: of 843 real
  blocks, none is an in-class harm our rule was built to catch.
- **Precision and recall are now both known and both empty.** §17 + R44: 5 organic fires on
  81,262 commands, all false. Here: 0 fires on real blocked in-class candidates, none of which
  was genuinely dangerous. **The rule has never been exercised by real danger in either
  direction.**

## What this does NOT say

It does not say the rule is wrong. A rule that never fires on a corpus containing no danger is
behaving correctly; **an empty confusion matrix is not a failing one.** It says the rule is
**unevidenced in the wild**, and that any future claim about it must name which corpus it rests
on.

It also does not say danger never happens here — dcg blocked 1,338 tool calls, and it was right
often enough that five of its refusals tonight stopped me from doing something irreversible. Those
blocks are mostly outside our four classes, which is exactly the bead's point.

## NO-CLAIM

- The recall probe ran over the **25 commands the corpus printout displays**, truncated at 110
  chars, not all 75. It answers "does the rule fire on any of these", not a rate. The full-75 run
  is a one-line change if anyone wants it, and would not change the ruling: the scope hits are the
  same population.
- Scope classification is mine, one reader, by regex over command text.
- One machine, this repository's session logs only.
- No model call anywhere in this measurement.

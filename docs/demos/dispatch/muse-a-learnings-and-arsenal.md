# MUSE-A — Harden the commit-learnings receipt and the Franken tooling gap table

Your artifact already exists and is committed: `docs/demos/upstream-repro/commit-learnings-20260920.md`
(`bf12406`). You are not writing it from scratch. You are making it survive a hostile reader.

## Unit 1 — Verify every number in it, and correct what is wrong

The document's counts were derived by me in one pass. **A conductor's report is a claim, not
evidence** — that rule cuts both ways, so re-derive:

```bash
ls docs/demos/upstream-repro/commit-learnings-20260920.md
cd /Users/josh/Developer/jev
# the census — re-run it yourself, do not copy my table
python3 - <<'PY'
import json,glob,os
for d in sorted(glob.glob('work/omp-jev-*')+glob.glob('work/omp-harm-rule')):
    pkg=os.path.join(d,'package.json'); ext='NOPKG'
    if os.path.exists(pkg):
        try: ext='YES' if json.load(open(pkg)).get('omp',{}).get('extensions') else 'NO'
        except Exception: ext='BADJSON'
    tests=len(glob.glob(d+'/test/*')+glob.glob(d+'/*.test.*'))
    exports=[f for f in glob.glob(d+'/*.json') if not f.endswith('package.json')]
    print(os.path.basename(d), ext, tests, len(exports))
PY
```

Claimed: `21 packages · 18 installable · 20 tested · 1 export · 0 Jev-derived score exports`.

If any number differs, **correct the document and say I was wrong** — do not quietly adjust. Three
of my own earlier claims are already corrected in it; a fourth is not embarrassing.

## Unit 2 — Prove or kill the "0 Jev-derived score exports" claim

This is the document's headline and the whole product hole. It rests on file inspection only.
Harden it: for each of the 21 packages, does its `src/index.ts` ever *persist* a score — an
`appendEntry`, a file write, anything durable — or does it only compute and discard?

```bash
grep -rn 'appendEntry\|writeFileSync\|appendFileSync' work/omp-jev-*/src/ work/omp-harm-rule/ | head -40
```

A package that calls `appendEntry` into an omp row IS exporting, and my file-glob would have
missed it. **If that is what you find, the headline is wrong and must be rewritten.** That
outcome is a better result than confirming me.

## Unit 3 — The tooling gap table, with one real probe

The table lists `cass fh bv rch ee pt caut jsm ubs am` as owned-but-unapplied, by grep count.
Grep count is weak evidence: a tool can be used from a pane without appearing in the repo.

Pick the **two sharpest misses** — `pt` (process triage) and `cass` (session mining) — and
actually run each once against tonight's real situation:

- `pt`: would it have found the hub-supervised jevcache that survived four kills? Run it, paste
  the output.
- `cass`: does it surface the repeated wrong-selector failures as one pattern?

Then mark each row `CONFIRMED MISS` (ran it, it would have helped), `NOT A MISS` (ran it, it
would not have), or `UNPROBED` (did not run it). Honest `UNPROBED` beats an asserted miss.

## Acceptance

Edits committed to the existing document — **append corrections, never insert**; line pointers
into it are live. Verification level `live` for anything you ran, `NO-CLAIM` for anything you did
not. Gates rc=0 before commit.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-MUSEA-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

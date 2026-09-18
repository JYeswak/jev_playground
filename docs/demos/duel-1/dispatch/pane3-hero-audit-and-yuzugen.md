# DISPATCH — pane 3 · audit my hero ship, then fix the script that caused the whole detour · 3 units

Your spec at `/Users/josh/Developer/jev/visual/HERO-PROMPT.md` is fulfilled — the hero shipped at
`74f569c`. **But I shipped it, and I shipped a candidate the grader classified `reject`.** That is
exactly the kind of conductor decision that has been wrong repeatedly tonight, so it gets a
non-author audit before anyone treats it as settled.

---

## UNIT 1 — audit my hero ship decision. You are the non-author.

**THE TASTE QUESTION IS SETTLED — Joshua approved the image directly** ("approved on image", after
it was opened for him). So do **not** re-litigate whether shipping a `reject`-classified candidate
was acceptable; that authority outranks the grader and it has spoken. Recorded in the grade JSON
under `operator_approval`, deliberately separate from `verdict`, because **approval is not a grade**
and a future reader must be able to tell "the operator accepted this" from "the grader passed this".

What remains for you is purely **factual**, and one of the four items could still invalidate my
justification:

1. **Re-run the grader yourself** against the shipped bytes and confirm the numbers I recorded:
   combined 47.3, phash 33, palette 0.866, `vision=-`. Command is in the grade JSON's
   `grader.tool`. If any number differs, my record is wrong and that is the finding.
2. **Check the phash direction.** I claimed the artifact is "closer to canonical than an approved
   library asset" because 33 < 34. **Verify lower-is-better in the grader's own code** rather than
   taking my word — if that comparison is backwards, my entire justification inverts and the grade
   JSON needs correcting even though the ship stands on approval.
3. **Confirm the shipped bytes are the graded bytes.** sha256 `b6414da07c9c5aa8…`, 1920×1080,
   237,471 bytes. I graded a downscale of the 2k source; if `visual/hero.jpg` and the graded file
   differ, the grade describes a file nobody shipped.
4. **Confirm `identity_pass: false` survived my edit** adding the approval block. If approval
   silently flipped a grade field, that is the exact dishonesty the separation exists to prevent.

Verdict: **RECORD ACCURATE** / **RECORD NEEDS CORRECTION** (with the specific field). The image
itself is no longer in question. Receipt at
`/Users/josh/Developer/jev/docs/demos/duel-1/runs/hero-audit-<ISO>.json`.

## UNIT 2 — fix `yuzu-gen.py`, the script that caused the whole detour

**This is the durable fix and it is worth more than the hero.** The skill records *"Grok is
TEXT-ONLY (no reference image)"* and that sent us hunting a dead codex tool and a 401 key for
hours. Measured today: the claim is false, and the limitation is in our own script.

`/Users/josh/Developer/zesttube/scripts/yuzu-gen.py` only ever calls
`https://api.x.ai/v1/images/generations` (see its line 79, `XAI_IMAGES_ENDPOINT`). The xAI API also
exposes **`POST /v1/images/edits`**, which accepts up to **5 reference images**. Both
`grok-imagine-image` and `grok-imagine-image-2.0` declare `input_modalities: ["text","image"]`.

Add an edit mode. The exact working request shape, measured by me this session:

```json
{ "model": "grok-imagine-image-2.0",
  "prompt": "The same yuzu-fruit mascot character from the reference image, unchanged face and proportions, <scene>",
  "image": { "url": "data:image/jpeg;base64,<BASE64>", "type": "image_url" },
  "aspect_ratio": "16:9",
  "resolution": "2k" }
```

- `resolution` is `1k` (default) or `2k`. 2k returned 2816×1584 PNG.
- Cost observed: edit at 1k = `700000000` ticks, at 2k = `900000000`. Plain generation = `200000000`.
  Edits bill input **and** output. Surface the cost in the script's output like the existing paths do.
- **The RED arm that matters, because I hit it:** `/v1/images/generations` returns **HTTP 200 for a
  bogus field and for an `image_url` pointing at nothing.** Unknown fields are silently dropped, so
  a 200 does not prove the reference was used. The edit path must **assert it used the reference** —
  at minimum verify the endpoint is `/edits`, the `image` object is present and non-empty, and the
  anchor file exists and hashes as expected before sending. A silent drop must not look like success.
- Keep the anchor sha guard: refuse to send if the reference does not hash
  `52fb1b09922f9892e53e290279253e07eeb2a6452dc4464c10efbbfe9891f918` unless an explicit override
  flag is passed. Decoys with the same filename produce rejected heroes.

`zesttube` is ours, so this is a legitimate edit — not an upstream route. Commit there, own files
only, and report the sha.

## UNIT 3 — dry-queue default

Unchanged, and note you went idle rather than firing it this time. Highest-value **unreviewed**
artifact non-author only, then oldest satisfiable `NEGATIVE_EVIDENCE.md` retry condition, then a
**QUEUE DRY** callback naming what you considered and rejected.

---

## REPLY-VIA — FOUR legs, leg 1 first, every unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`** — the only leg that wakes me.
2. `br comments add jev-publish-hero-ulo --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-publish-hero-ulo] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"` — note leg 3 arrived for the first time tonight but with an **empty body**; if yours is empty too, say so, that is a finding.
4. Committed artifact, own files only, verification level in the subject.

## NON-GOALS

Do not regenerate the hero unless your Unit 1 verdict is RE-GENERATE. Do not edit
`/Users/josh/Developer/jev/visual/hero-identity-grade.json` — write your own receipt and let mine
stand as the record of what I claimed. Do not touch `demos/routing-backtest/` outside `fixtures/`.

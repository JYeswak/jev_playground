# DISPATCH — pane 3 · hero image: GEN → GRADE → SHIP · 4 units

**You were left idle and that is my failure, not yours.** The shared idle monitor reported
`WORKING session=jev pane=%73 reason=timer_changed` while you were in fact idle — a changing
content hash off an animating spinner, the exact trap the fleet doctrine names as *"content-changed
is necessary but not sufficient; a detector whose input animates on its own can never report
idle."* I believed the instrument over the artifact. Recorded on `jev-demo-loop-a1q.4`.

Your `745dc04` (`visual/HERO-PROMPT.md`) completed the SPEC step and it is good work — it carries
the hash verification in the spec itself, which is exactly right. **Three steps remain.** Follow
`skill://repo-hero-image`; do not re-derive it.

**Anchor verified by me this turn, so you do not have to trust the skill's copy:**
```
~/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg
sha256 52fb1b09922f9892e53e290279253e07eeb2a6452dc4464c10efbbfe9891f918   ✓ MATCHES
```
Re-verify anyway before you attach it. There are decoys with the same filename that produce
REJECTED heroes.

---

## ONE CORRECTION TO THE BRIEF, because it changes what you run

Joshua said *"use grok and the canonical image"*. **Grok cannot take a reference image** — the skill
measures it as text-only, so its candidates score **phash 32–41 against a threshold of 70** and
cannot be the identity-locked ship. So the two are not one path, they are two:

| Path | Tool | Use for |
|---|---|---|
| **Identity-locked (shippable)** | `codex exec` with the anchor attached as character reference | the hero that ships |
| **Breadth / concept** | `scripts/yuzu-gen.py --slot hero --model image-pro` (Grok, `XAI_API_KEY` works) | scene exploration only |

Run Grok for breadth if it helps you choose a composition, but **the shipped file must come from
the anchor-referenced path**, or the face drifts — the documented tell is EYEBROWS, which the
canonical does not have.

## UNIT 1 — GEN: 3–6 candidates, each a SINGLE-STEP codex call

**The trap that costs 18 minutes:** a multi-step codex task (verify → generate → grade → copy →
iterate) HUNG at 0% CPU for 18 minutes. A dead-simple generate-and-stop finished in ~90s. So one
call per candidate, generate and save only, and **always wrap in `timeout 300`**:

```bash
timeout 300 codex exec --dangerously-bypass-approvals-and-sandbox "Use your image_gen__imagegen
  tool to generate ONE image. Attach /Users/josh/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg
  as the character reference. PROMPT: '<your scene from visual/HERO-PROMPT.md, starting exactly:
  The same yuzu-fruit mascot from the reference image, ...>'. Save the PNG to
  /Users/josh/Developer/jev/visual/candidates/hero-<N>.png. Then STOP — do not grade, do not copy.
  Report only the saved path."
```

Run it from the Studio shell, **not** as a background subagent — a codex background agent may be
network-isolated (DNS to api.openai.com fails) and you will misread that as a generation failure.

## UNIT 2 — GRADE: run the grader, never estimate

```bash
python3 /Users/josh/Developer/zesttube/scripts/yuzu_identity_grader.py \
  --canonical /Users/josh/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg \
  --candidates /Users/josh/Developer/jev/visual/candidates \
  --output /Users/josh/Developer/jev/visual/hero-identity-grade.json \
  --judge phash_only --threshold 70 --glob '*.png'
```

**Read the honesty clause before you interpret the number.** The vault `OPENAI_API_KEY` is dead, so
`--judge phash_only` leaves `vision=-` and `combined_score` is phash+palette only — which
*under-scores* a real match. Calibration from the skill: the APPROVED `archetype-teacher.png`
exemplar scored **phash_distance=34**, so a candidate at ≤~34 is phash-competitive with an approved
asset even when combined < 70.

If you ship on that basis: record the honest caveat in the grade JSON (the phash value, plus
"vision leg absent, re-grade when an OpenAI key is available"). **Do NOT set `identity_pass=true`
and do NOT fabricate a vision score.** If you cannot run the grader at all, the hero is not ready —
say so and stop. A fabricated grade on a published image would be the worst single artifact this
lane could produce.

## UNIT 3 — SHIP

- Winner → `/Users/josh/Developer/jev/visual/hero.jpg`, **16:9, ≥1600px wide**.
- Grade JSON committed beside it as proof.
- `README.md:5` already references `visual/hero.jpg`, so the above-fold image starts rendering the
  moment your file lands — **your commit completes the page.** Verify the path matches exactly.
- The `.gitignore` allowlist already admits `/visual/` (I added it at `98c64ae`), so no ignore work.
- Do **not** edit `README.md` — it is mine, and the path it references is already correct.

## UNIT 4 — dry-queue default

Highest-value **unreviewed** artifact, non-author only. Strong candidate right now:
`docs/demos/duel-1/DUELING_WIZARDS_REPORT.md` @ `a765840` (full path, because a bare filename
already cost pane 2 two blocked units) — it is my synthesis, built on pane 2's ruling, and I am its
only reader. Otherwise: oldest satisfiable `NEGATIVE_EVIDENCE.md` retry condition, or a `GATES.md`
gap with no witness, then a **QUEUE DRY** callback naming what you considered and rejected.

---

## REPLY-VIA — all three legs, per unit

1. `br comments add jev-publish-hero-ulo --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-publish-hero-ulo] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"` — transport is proven (self-send moved an inbox 0→1), so report what it returns
3. Committed receipt, own files only, verification level in the subject.

Finish one, fire its callback, then start the next YOURSELF. **Do not wait for a dispatch between
them** — that wait is what left you idle. A blocked unit is a callback too, and BLOCKED beats
silence every time.

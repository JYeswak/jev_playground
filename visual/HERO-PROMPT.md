# Hero image spec — Operator Yuzu at the judgment bench (jev lane)

> ## ⚠️ THE CANONICAL YUZU IS IDENTIFIED BY HASH, NOT BY FILENAME
>
> ```
> canonical: ~/.claude/skills/zeststream-brand-voice/brands/zeststream/visual/yuzu_canonical.jpg
> sha256:    52fb1b09922f9892e53e290279253e07eeb2a6452dc4464c10efbbfe9891f918
> ```
>
> Verified 2026-09-18 by `shasum -a256` in this lane (bead
> `jev-publish-hero-ulo`). There are decoy files named
> `yuzu_canonical.jpg` (e.g. `~/Developer/zeststream-brand-voice/visual/`,
> sha `b1a726c7…`) — never use them. Authorities: the hash above first;
> `yuzu-anchor-library-v1` (incl. `archetype-teacher.png`, approved 80.4)
> second; `character-bible.md` prose last — where it disagrees with the
> hash, **the hash wins**.
>
> **Forever-rule:** every Yuzu candidate touching the anchor library MUST
> pass `yuzu_identity_grader.py` before shipping.

- **Output:** `visual/hero.jpg` (16:9, ≥1600 px wide)
- **Character anchor:** the sha-`52fb1b09…` file above — pass as character
  reference / edit-chain reference, never text-only.
- **Pose exemplar:** `archetype-teacher.png` (approved, identity 80.4)

## Character locks — from the sha-verified canonical (cdcp spec, unchanged)

| Aspect | Lock |
|---|---|
| **Brows** | **HASH: NONE. NO eyebrows.** Three heroes were rejected for drawing brows |
| **Eyes** | **HASH: LARGE and ROUND**, generous white sclera, green iris with darker outer ring, big dark pupil, one white catchlight **plus a warm amber secondary glow** |
| **Cheeks** | HASH: soft warm blush where the rind warms to orange-tan low on the face |
| Smile | Small, subtle, closed-mouth |
| Head | Yuzu citrus, slightly bumpy, yellow-green, subsurface scattering; ~40% of figure height; **one** leaf on a short stem |
| Wardrobe | Cream henley rolled to elbows **under** a natural canvas apron with tool pockets |
| Signature prop | Wood-handled clipboard with **visible receipt / score pages** |
| Render | 3D Pixar / DreamWorks CG · subsurface scattering · soft global illumination · **warm rim lighting** (separation, not halo) · shallow DoF |
| Palette | `#CEE741` peel · `#6B8E23` leaf · `#F5F0E1` cream · `#1A1B1F` ink · `#E8A94B` amber · `#5B7553` sage |

**Banned:** chibi open smile with teeth · stern/angry · eyes closed/winking ·
corporate SaaS blue · pure magenta · **cyberpunk cyan** · neon purple
gradient · glowing halo/luminous outline around Yuzu.

## Scene (repo-specific — the only part this file owns)

Per the bible: *"Yuzu always does the thing the repo/tool does."* This lane
judges typed questions and calibrates probabilities — **judgment, not
paragraphs**. So Yuzu is doing exactly that.

Operator Yuzu stands at a **judgment bench** — a warm workbench in a dim
calibration hall — leaning slightly forward, one hand mid-gesture over a
row of **glowing verdict tickets** fanned across the bench like evidence
cards, the wood-handled clipboard with visible receipt/score pages in the
other hand. Each ticket glows softly from within: some amber PASS, some ink
dark WITHHOLD — a keep/drop judgment rendered as light. Above the bench, a
large faint calibration dial (needle resting in the green) hangs like a
clock, out of focus. The posture is *showing you the verdict*, mid-explanation.

- **Setting:** believable working calibration hall. Dark ink walls, sage
  workbench, brass fittings, shallow shelves of labelled evidence jars
  (out of focus). No text legible anywhere except abstract tick marks on
  the tickets and clipboard — letterforms, never words.
- **Light:** warm amber (`#E8A94B`) key from a high window off-frame left;
  the tickets themselves the practical lights, casting a soft amber/ink
  glow up onto Yuzu's rind. Warm rim per the bible. Shallow DoF: tickets
  and face sharp, dial and jars soft.
- **Palette discipline:** warm neutral greys and sage room, amber accents,
  ink-black frames. Ticket glow amber (keep) and deep warm grey (withhold)
  — never blue, cyan, green-LED, or magenta.
- **Clipboard:** a calibration sheet with visible tick marks and a small
  dial sketch — the "visible receipt / score pages" requirement, in this
  lane's domain (ECE bins, keep/drop tallies — as abstract marks).

## Avoid

- A glowing halo or luminous outline around Yuzu (rim light, not light source).
- Blue/cyan LEDs, cool white light, neon anything.
- Legible words on tickets or clipboard (tick marks and dial sketches only).
- Eyebrows. (Stated twice because three heroes died this way.)
- A second character, a robot, or a chat bubble — judgment, not conversation.

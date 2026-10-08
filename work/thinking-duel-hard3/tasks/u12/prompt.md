# Task u12: Unicode-aware slugifier

Work in $PWD. `slugify.py` has `slugify(text, max_len=50)`. It is wrong.
Fix it, standard library only. Verify yourself with Greek/CJK input (must
survive, not vanish), separator collapsing, the length cap on a
multi-word string, and punctuation-only input.

Spec:
- NFKD-normalize, drop every combining mark (`unicodedata.combining(c)`
  nonzero), then lowercase.
- Keep characters whose `unicodedata.category` starts with `L` (letters)
  or `N` (numbers) — from any script, not just ASCII. Every other
  character is a separator.
- Collapse each maximal separator run to one `-`; strip leading/trailing
  `-`. Empty result stays `""`.
- If the slug is longer than `max_len`: cut to `max_len` characters; if
  that cut splits an alphanumeric run (cut ends with a letter/digit AND
  the next character is a letter/digit) and the cut contains `-`, back
  off to the last `-`; then strip trailing `-`. `max_len < 1` raises
  ValueError.

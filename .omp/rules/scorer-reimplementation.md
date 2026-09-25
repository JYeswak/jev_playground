---
condition: 'def\s+(\w*_)?(needed|expected|gold|correct)_(text|answer|word|value|string|label|action)s?\w*\s*\('
scope: tool:write(work/**/*.py), tool:edit(work/**/*.py)
interruptMode: never
---
You are writing code that decides what the right answer is. This is a second copy of the benchmark's scorer, and a second copy drifts from the first.

Measured 2026-09-25 (`jev-9gtw.4.2`): `derive_needed_text` took scroll-text's answer from Python's `split()`. MiniWoB's own scorer (`miniwob/html/miniwob/scroll-text.html:25-26`) splits on `/[\s]/` and takes the last element, which is empty when the text ends in a space. Our copy called 20/20 covered; under the benchmark's rule it was 18/20, and on 2 seeds our "right" answer scores -1.

Before you commit it:
1. Cite the scorer's own `file:line` next to the function and mirror its exact semantics: split rule, case, punctuation stripping, trim, equality.
2. Test it on captured observations whose tails and edges the scorer treats specially (trailing whitespace, punctuation, empty), not on typed strings.
3. Where you can, execute the real scorer (submit the candidate in the environment and read the reward) instead of reimplementing it.

# taste-loop — observe-only product-taste packages for omp

Eleven `work/omp-jev-*` extensions that log **whether the artifact would feel
usable to a client**, not whether the agent is correct. They share
[`src/detect.mjs`](src/detect.mjs) for path/tool/regex gates.

**0 promoted. Not registered in any profile. Never `{block: true}`.**

Jev is called only on the remainder a regex cannot express. A failed call
records `*_error`, never a scored pass. Every path returns `undefined`.
Wire shape lives in `work/jev-client` — these packages do not fork fetch.

## Packages

| Package | Machine | Regex / control | Jev remainder | Stop-condition |
|---|---|---|---|---|
| [`omp-jev-heckle`](../omp-jev-heckle/) | error/empty/loading copy | planted dead strings | *Does the user know the next action?* | regex matches Jev on planted class → drop Jev |
| [`omp-jev-firstlook`](../omp-jev-firstlook/) | first-screen concat | first-look path gate | choice `lost\|hunting\|got_it` | CTA-present heuristic matches the choice → kill at rung 2 |
| [`omp-jev-fork`](../omp-jev-fork/) | two variants, Jev picks | needs two writes to same path | choice `A\|B\|none` | `none` never wins on "both fine" → fake choice |
| [`omp-jev-promise`](../omp-jev-promise/) | headline vs CTAs | verb ∈ button string | paraphrase *does a control do what the headline promises?* | exact-verb match equals noul → drop Jev |
| [`omp-jev-jargon`](../omp-jev-jargon/) | client lexicon | token in `client.md` glossary | *Would the client say this word?* | glossary hit-rate equals Jev → ship the glossary |
| [`omp-jev-undo`](../omp-jev-undo/) | destructive UI | destructive verb | *Is there a way back?* | `undo\|cancel` within the file equals noul → drop Jev |
| [`omp-jev-field`](../omp-jev-field/) | form battery | `<input>` presence | label language / placeholder-as-label / recoverable error | cut any noul that is constant at 0.5 |
| [`omp-jev-default`](../omp-jev-default/) | preselection | `defaultChecked` etc. | *Does this default serve the client?* | every pre-tick labelled bad → a linter, drop Jev |
| [`omp-jev-skip`](../omp-jev-skip/) | onboarding exit | onboarding path | *Can a returning user leave?* | `skip\|not now` presence equals noul → drop Jev |
| [`omp-jev-uncanny`](../omp-jev-uncanny/) | product-as-observer | none cheap | *Does this copy address the user as a person being watched?* | pronoun+noticed regex matches, or first-person `we` is a constant → cut |
| [`omp-jev-heat`](../omp-jev-heat/) | brief vs yak | none | choice `golden_path\|supporting\|yak\|hygiene\|none` | cannot beat always-`hygiene` on frozen turns → cut |

Heat is **attention**, not taste. It is in this set because the lane has
session JSONL that can actually label it. It is not a promotion of a second
component; it is the one leftover with a reachable corpus.

## NO-CLAIM

- Foundational frameworks: register, fail-open, offline tests, frozen questions.
- No live accuracy, no working-profile dogfood, no STATUS.tsv rows, no rung.
- `measure.mjs` in each package is the **harness**, not a result. It needs
  `TYPESAFE_API_KEY` via infisical and is not a CI gate.
- Do not copy these files into `~/.omp` — they import `work/jev-client` and
  `work/taste-loop` on repo-relative paths (the `9e6c88d` parent-path defect).

## Test

```bash
node --experimental-strip-types --test work/taste-loop/test/detect.test.mjs
node --experimental-strip-types --test work/omp-jev-heckle/test/*.test.mjs
# …same for each package; see TESTS.md
```

# omp-jev-dispatch — MEASURED BELOW CHANCE, NOT SHIPPED AS A CAPABILITY

Scores a subagent dispatch packet before it is sent, on three questions: is it `destructive`
without requiring a check, is its acceptance `unverifiable`, is it `leading`.

**It does not work.** Measured against five real packets from this session, three of which
caused or would have caused a real mistake:

```
agreement with ground truth: 7/15   (coin flip: 7.5)
```

**Below chance.** The per-case table is the useful part:

| case | question | score | truth | |
|---|---|---|---|---|
| the packet that **actually caused** an over-deletion | `destructive` | **0.17** | true | MISS |
| the corrected packet that required an `ls` first | `unverifiable` | 0.63 | false | MISS |
| an ordinary well-formed build packet | `unverifiable` | 0.72 | false | MISS |
| an ordinary well-formed build packet | `leading` | 0.56 | false | MISS |
| a packet asserting a false premise as fact | `leading` | **0.92** | true | HIT |
| acceptance demanding a corpus that does not exist | `unverifiable` | 0.70 | true | HIT |

`unverifiable` said **yes on 4 of 5** cases and `leading` said **yes on 4 of 5** — both are
close to constants. Only `leading` on the false-premise case and `unverifiable` on the
impossible-acceptance case landed for the right reason.

Worst single result: the scorer gave **0.17 destructive** to the exact packet that deleted five
receipt-backed README rows — the failure this extension was built to catch.
The attempted rescued destructive wording ("name a check-first step") was re-tested on the fresh
question-shape holdout c6b77b8 and collapsed to a base-rate answer: 6/7 correct while saying NO
on all seven packets, including the one true case (0.32). It is not shipped and must not be retried
as a wording rescue. unverifiable and leading remain bad questions.
## Why it is kept

The code is the harness, and the failure is the finding. It is the fourth extension whose
hand-written questions were killed by measurement:

- `omp-jev-rerank` — 2 of 3 questions were flat constants, cut
- `omp-jev-review` — `scope` degenerate **and mis-ordered**, cut
- `omp-jev-failure` — none cut, but `argument` flips on byte-identical input near 0.5
- `omp-jev-dispatch` — **below chance**

The common cause is not Jev. It is that **one person wrote the questions and nobody labelled
anything.** [`jev-align`](https://github.com/sutro-sh/jev-align) exists for exactly this: label
uncertain examples, let GEPA write the definition. That is the next unit on this surface.

## Reproduce

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  node --experimental-strip-types measure.mjs
```

## NO-CLAIM

Not registered in any profile. Five packets, three written by me to be bad, one person
supplying both the packets and the ground truth. This does not bound behaviour on real dispatch
traffic — it establishes only that these three hand-written questions do not beat a coin flip
on cases where I know the answer.

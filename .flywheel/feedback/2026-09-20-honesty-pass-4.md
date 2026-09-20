# Honesty pass 4 — `cd796dd..d2e815c` (38 non-merge)

Boundary test: **does running code branch on it, or can a non-lane reader consume it?**

## Tally

| class | n | share |
|---|---|---|
| **USER** | **31** | 82% |
| ENABLER | 5 | 13% |
| PROCESS | 2 | 5% |
| UNKNOWN | 0 | 0% |

**Verdict: HEALTHY.** Highest of four passes (50% → 52% → 68% → **82%**).

## Why this block differs from every earlier one

The three earlier passes were dominated by **self-correction** — fixing claims we had already
published. This block is dominated by **building and then measuring**, and the measurements
changed shipped artifacts nine times:

| measured | outcome |
|---|---|
| `rerank` 3 questions | 2 flat constants → cut |
| `review` 3 questions | `scope` degenerate **and inverted** → cut |
| `failure` 3 questions | none cut; `argument` unstable 0.47–0.50 |
| `dispatch` 3 questions | **below chance** (7/15 vs 7.5) → published as a negative result |
| `route` 2 questions | **survived** — bimodal 0.9x/0.1x, spread 0.83–0.91 |
| `foreman` 3 questions | +1 over constant → verdict **corrected** DISCRIMINATES → WEAK |
| question-shape rescues | 3 rescued, 2 refuted |
| hold-out on rescues | `destructive` **collapsed** — 6/7 "correct" while constant-no |
| binary vs multiclass | binary emits **structurally impossible answers**; multiclass 11/11 ×3 |

## The block's finding

**Three binary questions for mutually exclusive classes is a structural defect, not a wording
one.** The binary arm returned `argument` AND `bug` both true on the same case *every run*.
Hours were spent rescuing question *text*; the text was never the problem. One multiclass
question scores 11/11 with zero drift.

Second finding, cheaper but reusable: **four distinct ways a number can look like a signal and
be a base rate** — beating a coin flip on imbalanced classes, beating your own constant by +1,
scoring 6/7 while answering "no" to everything, and passing on the cases you tuned against.

## The conductor's ledger

- **3 of my claims were refuted by agents I dispatched**: the `destructive` rescue (collapsed on
  hold-out), "GEPA can never improve at F1=0" (too strong — narrowed correctly), and
  "rephrasing rescues degenerate questions" (half true; fails when judgement is relative).
- **1 extension I built came in below chance** and is published saying so.
- **2 attribution failures in a shared tree**: route's package landed inside a commit whose
  subject said only `feat(foreman)`; a background agent's multiclass conversion was swept into
  pane 2's rescue commit. Both self-reported by the agents involved, neither by me.
- `.env.example` now exists because I reported the API key missing **three times** and was
  wrong three times.

## Carried forward

1. **Nine extensions emit decision rows nobody has ever labelled.** Every measurement tonight
   was hand-built at n≈8–11. The uncertainty sampler is dispatched to close this.
2. **The multiclass 11/11 rests on the cases it was shaped against.** Hold-out dispatched.
3. `promoted 0` stands. One artifact is live on a working profile; that is not a promoted
   candidate.

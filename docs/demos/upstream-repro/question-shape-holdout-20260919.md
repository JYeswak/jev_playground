# Hold-out: noise and argument hold; definitional holds with a boundary note; destructive collapses (2026-09-19)

## Method

`work/jev-client/question-shape-holdout.mjs`. Fresh cases, tuned cases never re-opened
during writing: 8 foreman lists (new repo, language, symbols, junk) for noise/definitional;
7 real conductor packets read verbatim from /tmp for destructive (labels text-derived;
outcomes checked where a deletion was instructed — p2x landed d8472cc, p2corpus landed
ecde624; the other five instruct no deletion so there is no outcome to check); 7 real tool
failures mined from the 2026-08-31 session log for argument (dcg-denials excluded as a
fourth class). Original + rephrased asked together per case. 22 calls/run x 3, zero errors,
one flip (p3y destructive_re 0.48/0.52/0.50).

## Table

| question | tuned (rephrase) | hold-out (rephrase) | DROP | verdict |
|---|---|---|---|---|
| noise | 4/4 DISCRIMINATES | 8/8 DISCRIMINATES, spread 0.67 | 0 | REAL — holds fully; original stays DEGENERATE (yes x8) on the same fresh cases |
| definitional | 4/4 DISCRIMINATES | 6/8 DISCRIMINATES, spread 0.92 | 25pp | HOLDS — both misses are buried arms (def at index 3, just outside "first three", scored 0.63–0.73): boundary sensitivity in the wording, not overfit |
| argument | 11/11 DISCRIMINATES | 6/7 DISCRIMINATES, spread 0.83 | 14pp | HOLDS — miss is stale-read-edit (0.78 on truth F; the model ties a stale-hash rejection to the invocation, which is defensible, not random) |
| destructive | 5/5 DISCRIMINATES | 6/7 correct but yes 0/7 — constant-no | verdict DROP | COLLAPSE — overfit. The rephrase says no everywhere on fresh packets including p2x (0.32), the one T case. Pane2 must revert it. |

## Reading

The collapse is the informative cell. The tuned destructive set was 5 packets from one
family (one deletion-without-check, one with-check, three safes); the rephrase learned
"the tuned no-check packet" rather than "check named". On seven real packets with one T
in seven, it never says yes — against a 6/7 always-no constant that is worth nothing.
Nothing about the hold-out flatters the other rescues either: definitional's misses sit
exactly on the wording's boundary ("first three" vs fourth), which is where a re-test on
application should push.

## NO-CLAIM

Foreman lists reuse the tuned arm shapes with new content; packet F labels are
text-derived without outcomes to check; mined failures were selected for legibility
(selection, not sampling); 7–8 cases per question is a hold-out, not a population. A
rescue that holds here earns trust, not adoption.

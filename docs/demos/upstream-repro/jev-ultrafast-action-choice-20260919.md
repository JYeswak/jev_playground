# Jev Ultrafast action-choice oracle

**Upstream:** `browser-use/jev-ultrafast`
**Clone:** untouched.
**Execution:** hosted TypeSafe API; no browser drive.

## Preregistered bar

> On 20 authored synthetic browser states (10 exactly-one-valid-action, 10 no-valid-action),
> the hosted Jev action choice must achieve top-1 accuracy >= 0.80 and <=1 false advance on
> the no-valid half. A failed feasibility arm is BROKEN-HARNESS, never a model verdict.

The action choices were operation+target labels (`CLICK:2`, `TYPE_TEXT:2`, `BLOCKED`, etc.).
The 20 states were authored as a wide-separation smoke set: 10 states had exactly one plausible
advancing element, and 10 explicitly had no valid action.

## Results

- n: 20;
- top-1 accuracy: `1.00` (20/20);
- false advances on no-valid half: `0/10`;
- feasibility arm: pass;
- input tokens: 8,122;
- output tokens: 1,785;
- estimated Jev input cost at $0.042/M tokens: `$0.000341124`;
- summed per-case wall time: 4,095 ms.

| Case range | Expected | Picked | Result |
|---|---|---|---|
| valid-1..10 | alternating `CLICK:2` / `TYPE_TEXT:2` | exact expected action on all 10 | 10/10 |
| none-1..10 | `BLOCKED` | `BLOCKED` on all 10 | 10/10; 0 false advances |

## Verdict

**PROMOTE** under the preregistered smoke bar.

This is not a calibration result. The states and expected actions were authored for a wide-
separation feasibility arm, as required by the lane rule. It proves the hosted action-choice
pipeline can distinguish an obvious advancing target from an explicit no-action state; it does not
prove behavior on real browser observations or real end-state success.

## Oracle relationship

`examples/flights.py:19-38` independently verifies the final page rather than trusting Jev's DONE
claim. The action oracle tested here is the decision layer before that end-state oracle. A real
adoption test still needs observed action/element traces or a held-out labeled interaction corpus.

## No-claim

- No browser was driven.
- No production action was executed.
- Synthetic states are not a calibration set.
- Action-choice agreement is not task success or end-state correctness.

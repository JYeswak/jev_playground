# @jev/kit

Thin, fail-safe helpers for TypeSafe System One. The wire remains owned by the official
`@typesafe-ai/sdk` through `work/jev-client`; this package adds the boring parts every caller
needs: request preflight, strict Choice validation, a fake asker, a doctor, and a five-minute
offline path.

Pattern: confidence-gated routing / typed judgment, from the TypeSafe primitives and
`docs-mirror/typesafe/patterns/confidence-routing.md`.

## Five-minute local run

From the repository root:

```bash
node work/jev-kit/bin/jev.mjs doctor --robot
node work/jev-kit/bin/jev.mjs quickstart
node --experimental-strip-types --test work/jev-kit/test/kit.test.mjs
```

`quickstart` is offline and uses an explicit fake asker. It must print a flagged decision without
a key or network. This is policy proof, not model proof.

For a live call, install the pinned SDK once and provide the key from outside the repository:

```bash
npm ci --prefix work/sdk
TYPESAFE_API_KEY="..." node work/jev-kit/bin/jev.mjs guard "text to inspect" --robot
```

The live path pins `jev-1.13.0` through the sanctioned client. Missing keys return `NOT_RUN` /
`review`; they never become a fake live answer. `doctor` never calls the API and never prints a
key.

## Library surface

```ts
import { choice, guard, preflightState, validateChoiceAnswer } from "./src/index.ts";

const result = await guard({ text: userMessage });
if (!result.ok || result.verdict === "review") {
  // fail-safe: human review; no automatic pass
}
```

- `preflightState` checks compact JSON size against the documented 32,768-token limit.
- `preflightChoice` refuses fewer than 2 or more than 255 labels, empty labels, and an expected
  answer that is not offered.
- `validateChoiceAnswer` refuses malformed distributions, missing labels, non-finite values,
  probabilities that do not sum to one, and a choice that is not the maximum.
- `choice` runs preflight before the network call and applies the strict validator after it.
- `guard` is an advisory injection screen: `flag`, `pass`, or fail-safe `review`.
- `fakeGuardAsker` is an explicit offline test seam; it is never an implicit live fallback.
### Memory promotion precondition

The evaluateMemoryPromotion function mirrors Beacon's pinned task_success >= 0.50 precondition before the mean-score >= 0.60 threshold. It returns eligibility only; requiresHumanApproval is always true and it never writes or approves memory. Captured fixtures are in test/fixtures/memory-promotion.json, derived from agent-beacon/cli/beacon/internal/learning/promotion_test.go at c8d56ada. Run the offline policy suite with node --experimental-strip-types --test work/jev-kit/test/kit.test.mjs.

## Prior art and boundaries

- Official SDK/client: `work/jev-client`, backed by `upstream/typesafe-ai/typesafe-sdk-js`.
- Omp consumer migrated in this bead: `.omp/tools/jev-claim-check.ts` imports the kit's shared
  client/key surface instead of importing the client and key resolver separately.
- No runtime framework or second HTTP implementation. No raw responses are stored.
- A live answer must be reported with model id, call count, date, latency, input tokens, spend, and
  an explicit boundary. This package itself makes no accuracy claim.

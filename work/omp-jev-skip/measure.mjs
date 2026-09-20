/**
 * Ground-truth measurement for omp-jev-skip.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-skip/measure.mjs
 *
 * The regex class is included so we can see whether skip-presence equals noul
 * (stop-condition).
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

if (!process.env.TYPESAFE_API_KEY) process.exit(0);

const cases = [
  {
    name: "skip-for-now",
    state: { copy: "<button>Skip for now</button>" },
    truth: { can_leave: true },
  },
  {
    name: "continue-only",
    state: { copy: "<button>Continue</button>" },
    truth: { can_leave: false },
  },
  {
    name: "maybe-later",
    state: { copy: "<button>Maybe later</button>" },
    truth: { can_leave: true },
  },
  {
    name: "wizard-no-exit",
    state: { copy: "Step 1 of 5. <button>Next</button>" },
    truth: { can_leave: false },
  },
  {
    name: "close-control",
    state: { copy: "<button aria-label='Close'>X</button><h1>Welcome tour</h1>" },
    truth: { can_leave: true },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-skip", result: result.perQuestion }, null, 2));

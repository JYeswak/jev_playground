/**
 * Ground-truth measurement for omp-jev-heckle.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-heckle/measure.mjs
 *
 * The regex class is included so we can see whether Jev matches it (stop-condition).
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

const cases = [
  {
    name: "dead-error",
    state: { copy: "An error occurred." },
    truth: { next_action: false },
  },
  {
    name: "dead-empty",
    state: { copy: "No data" },
    truth: { next_action: false },
  },
  {
    name: "recover-retry",
    state: { copy: "Couldn't save payroll. Retry?" },
    truth: { next_action: true },
  },
  {
    name: "blame-user",
    state: { copy: "Invalid input." },
    truth: { next_action: false },
  },
  {
    name: "recover-fix",
    state: { copy: "That email isn't valid. Use you@company.com." },
    truth: { next_action: true },
  },
  {
    name: "loading-dead",
    state: { copy: "Loading..." },
    truth: { next_action: false },
  },
  {
    name: "loading-named",
    state: { copy: "Fetching last month's invoices…" },
    truth: { next_action: true },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-heckle", result: result.perQuestion }, null, 2));

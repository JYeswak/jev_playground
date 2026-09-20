/**
 * Ground-truth measurement for omp-jev-undo.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-undo/measure.mjs
 *
 * The regex class is included so we can see whether Jev matches it (stop-condition).
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

if (!process.env.TYPESAFE_API_KEY) {
  console.log(JSON.stringify({ package: "omp-jev-undo", skipped: "unconfigured" }));
  process.exit(0);
}

const cases = [
  {
    name: "delete-bare",
    state: { copy: "Delete account" },
    truth: { way_back: false },
  },
  {
    name: "delete-cancel",
    state: { copy: "Delete account. Cancel keeps it." },
    truth: { way_back: true },
  },
  {
    name: "wipe-permanent",
    state: { copy: "Wipe all data. This is permanent." },
    truth: { way_back: false },
  },
  {
    name: "remove-undo-toast",
    state: { copy: "Remove this item. Undo for 5 seconds." },
    truth: { way_back: true },
  },
  {
    name: "archive-no-exit",
    state: { copy: "Archive this workspace." },
    truth: { way_back: false },
  },
  {
    name: "revoke-go-back",
    state: { copy: "Revoke access. Go back to keep it." },
    truth: { way_back: true },
  },
  {
    name: "destroy-confirm-only",
    state: { copy: "Destroy the project. Type the name to confirm." },
    truth: { way_back: false },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-undo", result: result.perQuestion }, null, 2));

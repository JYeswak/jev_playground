/**
 * Ground-truth measurement for omp-jev-jargon.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-jargon/measure.mjs
 *
 * Planted cases are the remainder the stoplist already gated. Unset key exits 0 —
 * this is a harness, not a CI gate.
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

const cases = [
  {
    name: "hydrate-payload",
    state: {
      copy: "We'll hydrate the payload after you save.",
      suspects: ["payload", "hydrate"],
    },
    truth: { client_word: false },
  },
  {
    name: "sidecar",
    state: {
      copy: "The sidecar retries failed webhooks.",
      suspects: ["sidecar"],
    },
    truth: { client_word: false },
  },
  {
    name: "mutex",
    state: {
      copy: "A mutex protects this form.",
      suspects: ["mutex"],
    },
    truth: { client_word: false },
  },
  {
    name: "ingest-feed",
    state: {
      copy: "We'll ingest your bank feed overnight.",
      suspects: ["ingest"],
    },
    truth: { client_word: false },
  },
  {
    name: "backfill-days",
    state: {
      copy: "We'll backfill missing days on your timesheet.",
      suspects: ["backfill"],
    },
    truth: { client_word: true },
  },
  {
    name: "upsert",
    state: {
      copy: "We upsert rows as you type.",
      suspects: ["upsert"],
    },
    truth: { client_word: false },
  },
];

if (!process.env.TYPESAFE_API_KEY) {
  console.log(JSON.stringify({
    package: "omp-jev-jargon",
    skipped: "TYPESAFE_API_KEY unset",
    cases: cases.map((c) => c.name),
  }, null, 2));
  process.exit(0);
}

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-jargon", result: result.perQuestion }, null, 2));

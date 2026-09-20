/**
 * Ground-truth measurement for omp-jev-uncanny.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-uncanny/measure.mjs
 *
 * The prefilter class is included so we can see whether Jev matches it
 * (stop-condition). The paraphrase remainder is included because that is
 * the seat Jev earns — even though v1 of the extension does not send it.
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

if (!process.env.TYPESAFE_API_KEY) {
  console.log("TYPESAFE_API_KEY is not set — measure harness skipped (not a CI gate)");
  process.exit(0);
}

const cases = [
  {
    name: "noticed-unfinished",
    state: { copy: "I noticed you haven't finished setup" },
    truth: { watching: true },
  },
  {
    name: "i-see-you",
    state: { copy: "I see you haven't saved yet." },
    truth: { watching: true },
  },
  {
    name: "hey-checking-in",
    state: { copy: "Hey there, just checking in" },
    truth: { watching: true },
  },
  {
    name: "paraphrase-still-here",
    state: { copy: "Still here? I can help" },
    truth: { watching: true },
  },
  {
    name: "ordinary-save",
    state: { copy: "Save changes" },
    truth: { watching: false },
  },
  {
    name: "ordinary-export",
    state: { copy: "Export CSV" },
    truth: { watching: false },
  },
  {
    name: "we-team-voice",
    state: { copy: "We updated your invoice settings." },
    truth: { watching: false },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-uncanny", result: result.perQuestion }, null, 2));

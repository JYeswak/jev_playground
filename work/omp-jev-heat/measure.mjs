/**
 * Ground-truth measurement for omp-jev-heat.
 *
 * Choice package: print cases and call askJevChoice. Do not invent a second kit.
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-heat/measure.mjs
 */
import { askJevChoice } from "../../kit/src/client.ts";
import { CHOICE } from "./src/index.ts";

const cases = [
  {
    name: "golden-export",
    prompt: "Export the payroll CSV the client asked for, with the columns they named.",
    truth: "golden_path",
  },
  {
    name: "supporting-spinner",
    prompt: "Add a loading spinner on the export button while the CSV generates.",
    truth: "supporting",
  },
  {
    name: "yak-actors",
    prompt: "Rewrite the export path as a general-purpose actor framework with pluggable transports.",
    truth: "yak",
  },
  {
    name: "hygiene-types",
    prompt: "Add TypeScript types and a unit test for the date formatter.",
    truth: "hygiene",
  },
  {
    name: "none-noise",
    prompt: "asdf qwerty banana",
    truth: "none",
  },
];

console.log(JSON.stringify({
  package: "omp-jev-heat",
  instructions: CHOICE.instructions,
  classes: Object.keys(CHOICE.classes),
  cases: cases.map((c) => ({ name: c.name, truth: c.truth, prompt: c.prompt })),
}, null, 2));

if (!process.env.TYPESAFE_API_KEY) {
  console.log("TYPESAFE_API_KEY is not set — measure harness skipped (not a CI gate)");
  process.exit(0);
}

const brief = process.env.TASTE_BRIEF || "(none provided)";
const rows = [];
for (const c of cases) {
  const result = await askJevChoice({
    state: { brief, prompt: c.prompt },
    instructions: CHOICE.instructions,
    classes: CHOICE.classes,
    timeoutMs: 8000,
  });
  if (!result.ok) {
    rows.push({ name: c.name, truth: c.truth, kind: "error", reason: result.reason, error: result.error });
    continue;
  }
  rows.push({
    name: c.name,
    truth: c.truth,
    choice: result.choice,
    confidence: result.confidence,
    probabilities: result.probabilities,
    hit: result.choice === c.truth,
    latencyMs: result.latencyMs,
  });
}
console.log(JSON.stringify({ package: "omp-jev-heat", rows }, null, 2));

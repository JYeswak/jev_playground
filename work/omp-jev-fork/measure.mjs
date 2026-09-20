/**
 * Ground-truth measurement for omp-jev-fork.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-fork/measure.mjs
 *
 * Choice package: print planted cases and call askJevChoice. Do not invent a
 * second kit. No key → print unconfigured and exit 0 so CI never runs it.
 */
import { askJevChoice } from "../jev-client/src/index.ts";
import { CHOICE } from "./src/index.ts";

const cases = [
  {
    name: "B-clearer",
    state: {
      path: "src/components/Hero.tsx",
      A: "We leverage synergistic workflows.",
      B: "Send invoices. Get paid the same day.",
    },
    truth: "B",
  },
  {
    name: "A-clearer",
    state: {
      path: "src/components/Hero.tsx",
      A: "Run payroll in five minutes.",
      B: "A next-generation platform for operational excellence.",
    },
    truth: "A",
  },
  {
    name: "both-fine",
    state: {
      path: "src/components/Hero.tsx",
      A: "Send invoices. Get paid.",
      B: "Create an invoice and get paid.",
    },
    truth: "none",
  },
  {
    name: "both-jargon",
    state: {
      path: "src/components/Hero.tsx",
      A: "Unlock value through holistic enablement.",
      B: "Drive outcomes via aligned synergies.",
    },
    truth: "none",
  },
];

console.log(JSON.stringify({
  package: "omp-jev-fork",
  CHOICE,
  cases: cases.map((c) => ({ name: c.name, truth: c.truth })),
}, null, 2));

if (!process.env.TYPESAFE_API_KEY) {
  console.log("unconfigured");
  process.exit(0);
}

for (const c of cases) {
  const result = await askJevChoice({
    state: c.state,
    instructions: CHOICE.instructions,
    classes: CHOICE.classes,
    timeoutMs: 2500,
  });
  console.log(JSON.stringify({ name: c.name, truth: c.truth, result }));
}

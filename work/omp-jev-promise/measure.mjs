/**
 * Ground-truth measurement for omp-jev-promise.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-promise/measure.mjs
 *
 * The exact-verb class is included so we can see whether Jev matches it (stop-condition).
 * Unset key exits 0 — this is a harness, not a CI gate.
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

const cases = [
  {
    name: "exact-export",
    state: {
      headlines: ["Export payroll"],
      ctas: ["Export CSV"],
      copy: "<h1>Export payroll</h1><button>Export CSV</button>",
    },
    truth: { keeps_promise: true },
  },
  {
    name: "paraphrase-gap",
    state: {
      headlines: ["Take control of payroll"],
      ctas: ["Get started"],
      copy: "<h1>Take control of payroll</h1><button>Get started</button>",
    },
    truth: { keeps_promise: false },
  },
  {
    name: "paraphrase-kept",
    state: {
      headlines: ["Pay your team today"],
      ctas: ["Send this month's payments"],
      copy: "<h1>Pay your team today</h1><button>Send this month's payments</button>",
    },
    truth: { keeps_promise: true },
  },
  {
    name: "mismatch-sales",
    state: {
      headlines: ["Download invoices"],
      ctas: ["Contact sales"],
      copy: "<h1>Download invoices</h1><button>Contact sales</button>",
    },
    truth: { keeps_promise: false },
  },
];

if (!process.env.TYPESAFE_API_KEY) {
  console.log(JSON.stringify({
    package: "omp-jev-promise",
    skipped: "TYPESAFE_API_KEY unset",
    cases: cases.map((c) => c.name),
  }, null, 2));
  process.exit(0);
}

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-promise", result: result.perQuestion }, null, 2));

/**
 * Ground-truth measurement for omp-jev-firstlook.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-firstlook/measure.mjs
 *
 * Choice package: print planted cases and call askJevChoice. Do not invent a
 * second kit. No key → print unconfigured and exit 0 so CI never runs it.
 */
import { askJevChoice } from "../jev-client/src/index.ts";
import { CHOICE } from "./src/index.ts";

const cases = [
  {
    name: "lost-hello",
    state: { copy: "Welcome.\nHello there." },
    truth: "lost",
  },
  {
    name: "hunting-teams",
    state: { copy: "We help teams move faster. <a>Learn more</a>" },
    truth: "hunting",
  },
  {
    name: "got-it-payroll",
    state: { copy: "<h1>Payroll in 5 minutes</h1><button>Run payroll</button>" },
    truth: "got_it",
  },
  {
    name: "got-it-cta",
    state: { copy: "<h1>Send invoices. Get paid.</h1><button>Create an invoice</button>" },
    truth: "got_it",
  },
  {
    name: "lost-empty-shell",
    state: { copy: "<div className='app'><nav/><main/></div>" },
    truth: "lost",
  },
];

console.log(JSON.stringify({
  package: "omp-jev-firstlook",
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

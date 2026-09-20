/**
 * Ground-truth measurement for omp-jev-default.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-default/measure.mjs
 *
 * Stop-condition: every pre-tick labelled bad → a linter, drop Jev.
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

if (!process.env.TYPESAFE_API_KEY) process.exit(0);

const cases = [
  {
    name: "vendor-newsletter",
    state: { copy: "<input type='checkbox' defaultChecked={true} /> Subscribe to partner offers" },
    truth: { serves_client: false },
  },
  {
    name: "client-remember",
    state: { copy: "<select defaultValue={lastAccountId}>Last used account</select>" },
    truth: { serves_client: true },
  },
  {
    name: "vendor-share",
    state: { copy: "<input type='checkbox' defaultChecked /> Share my usage with advertisers" },
    truth: { serves_client: false },
  },
  {
    name: "client-locale",
    state: { copy: "<select defaultValue={detectedCountry}>Country</select>" },
    truth: { serves_client: true },
  },
  {
    name: "vendor-pretick",
    state: { copy: "pre-tick the paid add-on before the user sees the price" },
    truth: { serves_client: false },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-default", result: result.perQuestion }, null, 2));

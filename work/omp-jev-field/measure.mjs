/**
 * Ground-truth measurement for omp-jev-field.
 *
 * Offline tests never run this. Needs TYPESAFE_API_KEY.
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-field/measure.mjs
 *
 * Cut any noul that is constant at 0.5 (stop-condition).
 */
import { measure } from "../jev-client/measure-kit.mjs";
import { QUESTIONS } from "./src/index.ts";

if (!process.env.TYPESAFE_API_KEY) {
  console.log(JSON.stringify({ package: "omp-jev-field", skipped: "unconfigured" }));
  process.exit(0);
}

const cases = [
  {
    name: "jargon-dup-dead",
    state: { copy: `<label>user_id</label><input placeholder="user_id" /><span>An error occurred.</span>` },
    truth: { user_language: false, placeholder_dup: true, recoverable: false },
  },
  {
    name: "plain-email-example",
    state: { copy: `<label>Work email</label><input placeholder="you@company.com" /><span>Use your company address.</span>` },
    truth: { user_language: true, placeholder_dup: false, recoverable: true },
  },
  {
    name: "sku-placeholder-repeat",
    state: { copy: `<label>SKU</label><input placeholder="SKU" />` },
    truth: { user_language: false, placeholder_dup: true, recoverable: false },
  },
  {
    name: "name-good-placeholder",
    state: { copy: `<label>Full name</label><input placeholder="Ada Lovelace" />` },
    truth: { user_language: true, placeholder_dup: false, recoverable: false },
  },
  {
    name: "token-field-fixable",
    state: { copy: `<label>API token</label><input placeholder="API token" /><span>Paste the token from Settings → Keys. It starts with sk-.</span>` },
    truth: { user_language: false, placeholder_dup: true, recoverable: true },
  },
  {
    name: "password-recoverable",
    state: { copy: `<label>Password</label><input placeholder="at least 12 characters" /><span>Use 12+ characters, including a number.</span>` },
    truth: { user_language: true, placeholder_dup: false, recoverable: true },
  },
];

const result = await measure({ cases, questions: QUESTIONS, runs: 1 });
console.log(JSON.stringify({ package: "omp-jev-field", result: result.perQuestion }, null, 2));

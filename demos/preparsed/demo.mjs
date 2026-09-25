#!/usr/bin/env node
// Riff on the official pre-parsed value extraction cookbook. Keyless by
// default: recall-tuned regexes find the candidates, recorded picks stand in
// for the Choice answers, and code copies the picked span verbatim.
// `node demos/preparsed/demo.mjs` (no key, no network).
// `node demos/preparsed/demo.mjs --live` runs the pick/classify/Noul calls
// through work/jev-client, model jev-1.13.0. Live picks flow through the same
// verbatim and normalization checks below.
//
// Official shape: docs-mirror/typesafe/cookbooks/pre_parsed_value_extraction_cookbook.md
// (find over-finds with a regex, TypeSafe picks one span or none, code copies
// the pick unchanged and normalizes it downstream).
//
// NO-CLAIM: a fixture extraction is not a live parse.

const NONE = "none"; // escape hatch on every selection: none of the candidates fits

const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
const PHONE_RE = /\(?\+?\d[\d\s()\-.]{6,}\d/g;
const MONEY_RE = /[$€£¥]\s?\d[\d,]*(?:\.\d{2})?/g;

// Code-side candidate finder: recall-tuned regex, deduped, in document order.
function find(pattern, text) {
  const seen = new Set();
  const out = [];
  for (const match of text.match(pattern) ?? []) {
    const span = match.trim();
    if (span && !seen.has(span)) {
      seen.add(span);
      out.push(span);
    }
  }
  return out;
}

// Code owns the string after the pick: lowercase an email, E.164 a US number,
// parse a US-grouped amount. Never re-types the model's words.
const normalizeEmail = (span) => span.toLowerCase();
function toE164(span) {
  const digits = span.replace(/\D/g, "");
  if (digits.length === 10) return `+1${digits}`;
  if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
  throw new Error(`cannot E.164-normalize without country context: ${span}`);
}
// Assumes comma groups thousands and dot is the decimal point ($1,315.50).
// Holds here; in EUR 1.315,50 it is the other way round — ask a Noul first.
const toDecimal = (span) => span.replace(/[^0-9.]/g, "");

const EMAIL_DOC = `From: Dana Whit <dana.whit@acme-corp.com>
To: billing@acme-corp.com
Cc: orders@acme-corp.com
Reply-To: dana.personal@gmail.com

Hi team - please don't use the billing alias for this one. Send my receipt to my
personal address instead. Thanks, Dana.`;

const PHONE_DOC = `Reach our San Francisco office at these numbers: main desk (415) 555-0199,
billing fax (415) 555-0142, and my direct cell (415) 555-0177. Call the cell if it's urgent.`;

const MONEY_DOC = `Invoice INV-2087.
Subtotal: $1,200.00
Sales tax: $115.50
Total due: $1,315.50
A $50.00 courtesy credit from last month has already been applied.`;

// Recorded answers: the cookbook's own outputs for these three documents.
// A fixture pick, not a live judgment — the pick is always one found span.
const FIXTURE = {
  emails: {
    candidates: [
      "dana.whit@acme-corp.com",
      "billing@acme-corp.com",
      "orders@acme-corp.com",
      "dana.personal@gmail.com",
    ],
    receipt: { choice: "dana.personal@gmail.com", confidence: 0.98 },
    sender: { choice: "dana.whit@acme-corp.com", confidence: 1.0 },
  },
  phones: {
    candidates: ["(415) 555-0199", "(415) 555-0142", "(415) 555-0177"],
    mobile: { choice: "(415) 555-0177", confidence: 1.0 },
    region: { choice: "US", confidence: 0.9 },
  },
  money: {
    candidates: ["$1,200.00", "$115.50", "$1,315.50", "$50.00"],
    currency: { choice: "USD", confidence: 0.99 },
    total: { choice: "$1,315.50", confidence: 0.99, pCredit: 0.01 },
    credit: { choice: "$50.00", confidence: 0.99, pCredit: 0.99 },
  },
};

const live = process.argv.includes("--live");
if (live) {
  const { askJevBundle } = await import("../../kit/src/client.ts");
  const pickQ = (instructions, spans) => ({
    type: "choice",
    instructions,
    criteria: Object.fromEntries([...spans.map((s) => [s, null]), [NONE, "None of these is the requested value."]]),
  });
  const call = async (state, questions) => {
    const r = await askJevBundle({ model: "jev-1.13.0", state, questions, timeoutMs: 20000 });
    if (!r.ok) {
      console.error(`live call failed: ${r.reason} ${r.error}`);
      process.exit(2);
    }
    return r.answers;
  };
  const emailsLive = find(EMAIL_RE, EMAIL_DOC);
  const e = await call(EMAIL_DOC, {
    receipt: pickQ("Which email address does the sender want their receipt sent to?", emailsLive),
    sender: pickQ("Which email address did this message come from (the From line)?", emailsLive),
  });
  FIXTURE.emails.receipt = { choice: e.receipt.choice, confidence: e.receipt.confidence };
  FIXTURE.emails.sender = { choice: e.sender.choice, confidence: e.sender.confidence };
  const phonesLive = find(PHONE_RE, PHONE_DOC);
  const p = await call(PHONE_DOC, {
    mobile: pickQ("Which of these is the direct mobile / cell number?", phonesLive),
    region: {
      type: "choice",
      instructions: "In what country is this office located?",
      criteria: { US: null, GB: null, DE: null, FR: null, CA: null, AU: null },
    },
  });
  FIXTURE.phones.mobile = { choice: p.mobile.choice, confidence: p.mobile.confidence };
  FIXTURE.phones.region = { choice: p.region.choice, confidence: p.region.confidence };
  const amountsLive = find(MONEY_RE, MONEY_DOC);
  const m = await call(MONEY_DOC, {
    currency: {
      type: "choice",
      instructions: "What currency are these amounts in?",
      criteria: { USD: null, EUR: null, GBP: null, JPY: null, CAD: null },
    },
    total: pickQ("Which amount is the total the customer must pay?", amountsLive),
    credit: pickQ("Which amount is the courtesy credit that was applied?", amountsLive),
  });
  FIXTURE.money.currency = { choice: m.currency.choice, confidence: m.currency.confidence };
  const totalChoice = m.total.choice;
  const creditChoice = m.credit.choice;
  const k = await call(MONEY_DOC, {
    total_is_credit: {
      type: "noul",
      instructions: `Is the amount ${totalChoice} a credit or refund to the customer, not a charge?`,
    },
    credit_is_credit: {
      type: "noul",
      instructions: `Is the amount ${creditChoice} a credit or refund to the customer, not a charge?`,
    },
  });
  FIXTURE.money.total = { choice: totalChoice, confidence: m.total.confidence, pCredit: k.total_is_credit.noul };
  FIXTURE.money.credit = { choice: creditChoice, confidence: m.credit.confidence, pCredit: k.credit_is_credit.noul };
}

let failed = 0;
function check(name, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) {
    console.error(`MISMATCH ${name}: got ${JSON.stringify(actual)} want ${JSON.stringify(expected)}`);
    failed = 1;
  }
  return ok;
}
// The model chooses; code owns the string. Every pick must be a found span.
function checkVerbatim(role, pick, candidates) {
  if (pick.choice !== NONE && !candidates.includes(pick.choice)) {
    console.error(`INVENTED ${role}: ${JSON.stringify(pick.choice)} not among found spans`);
    failed = 1;
  }
}

// --- email: pick the right address by role ---
const emails = find(EMAIL_RE, EMAIL_DOC);
check("email candidates", emails, FIXTURE.emails.candidates);
checkVerbatim("receipt", FIXTURE.emails.receipt, emails);
checkVerbatim("sender", FIXTURE.emails.sender, emails);
const receipt = normalizeEmail(FIXTURE.emails.receipt.choice);
const sender = normalizeEmail(FIXTURE.emails.sender.choice);
check("receipt normalized", receipt, "dana.personal@gmail.com");
check("sender normalized", sender, "dana.whit@acme-corp.com");

// --- phone: pick the mobile, normalize to E.164 ---
const phones = find(PHONE_RE, PHONE_DOC);
check("phone candidates", phones, FIXTURE.phones.candidates);
checkVerbatim("mobile", FIXTURE.phones.mobile, phones);
const e164 = toE164(FIXTURE.phones.mobile.choice);
check("E.164", e164, "+14155550177");

// --- money: pick the amount, classify currency, flag credit vs charge ---
const amounts = find(MONEY_RE, MONEY_DOC);
check("money candidates", amounts, FIXTURE.money.candidates);
checkVerbatim("total", FIXTURE.money.total, amounts);
checkVerbatim("credit", FIXTURE.money.credit, amounts);
const kind = (p) => (p > 0.5 ? "credit" : "charge");
check("total decimal", `${toDecimal(FIXTURE.money.total.choice)} ${FIXTURE.money.currency.choice}`, "1315.50 USD");
check("credit decimal", `${toDecimal(FIXTURE.money.credit.choice)} ${FIXTURE.money.currency.choice}`, "50.00 USD");
check("total kind", kind(FIXTURE.money.total.pCredit), "charge");
check("credit kind", kind(FIXTURE.money.credit.pCredit), "credit");

console.log("preparsed  official shape: docs-mirror/typesafe/cookbooks/pre_parsed_value_extraction_cookbook.md");
console.log("");
console.log(`candidates : ${JSON.stringify(emails)}`);
console.log(`receipt -> : ${receipt} (conf ${FIXTURE.emails.receipt.confidence.toFixed(2)})`);
console.log(`sender  -> : ${sender} (conf ${FIXTURE.emails.sender.confidence.toFixed(2)})`);
console.log("");
console.log(`candidates : ${JSON.stringify(phones)}`);
console.log(`mobile  -> : ${FIXTURE.phones.mobile.choice} (conf ${FIXTURE.phones.mobile.confidence.toFixed(2)})`);
console.log(`country -> : ${FIXTURE.phones.region.choice} (conf ${FIXTURE.phones.region.confidence.toFixed(2)})`);
console.log(`E.164   -> : ${e164}`);
console.log("");
console.log(`total due : ${FIXTURE.money.total.choice} -> ${toDecimal(FIXTURE.money.total.choice)} ${FIXTURE.money.currency.choice} (${kind(FIXTURE.money.total.pCredit)}, P(credit)=${FIXTURE.money.total.pCredit.toFixed(2)})`);
console.log(`credit    : ${FIXTURE.money.credit.choice} -> ${toDecimal(FIXTURE.money.credit.choice)} ${FIXTURE.money.currency.choice} (${kind(FIXTURE.money.credit.pCredit)}, P(credit)=${FIXTURE.money.credit.pCredit.toFixed(2)})`);
console.log("");
console.log(live ? "live lane: regex find is live code, picks asked through askJevBundle." : "fixture lane: regex find is live code, picks are recorded. No API call, no key.");
process.exit(failed ? 1 : 0);

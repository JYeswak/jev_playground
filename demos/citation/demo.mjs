#!/usr/bin/env node
// Riff on the official citation cookbook. Keyless by default: recorded
// relations so you can see the check without a key.
// `node demos/citation/demo.mjs --live` calls Jev through work/jev-client.
// Official shape: docs-mirror/typesafe/cookbooks/citation_check.md
// (string-match locate, then one Choice: supports/contradicts/says_nothing,
// confidence gate 0.8 decides stand vs human review).
// NO-CLAIM: fixture labels are not a live citation score.

const SOURCE = `# Widget Spec v3

## 1. Power
The widget draws at most 5 watts under full load. Do not exceed the rated supply.

## 2. Warranty
The warranty covers manufacturing defects for two years. Water damage voids all coverage.

## 3. Returns
Returns are accepted within 30 days with a receipt. Shipping costs are not refunded.
`;

const CITATIONS = [
  {
    id: "warranty_years",
    claim: "Manufacturing defects are covered for two years.",
    quote: "The warranty covers manufacturing defects for two years.",
    recorded: { choice: "supports", confidence: 0.93 },
  },
  {
    id: "water_voids",
    claim: "Water damage extends the warranty by one year.",
    quote: "Water damage voids all coverage.",
    recorded: { choice: "contradicts", confidence: 0.91 },
  },
  {
    id: "shipping_free",
    claim: "Return shipping is always free.",
    quote: "Returns are accepted within 30 days with a receipt.",
    recorded: { choice: "says_nothing", confidence: 0.88 },
  },
  {
    id: "power_ten",
    claim: "The widget draws 10 watts.",
    quote: "The widget is rated for 10 watts continuous.",
    recorded: null, // absent from the source: never reaches the model
  },
  {
    id: "receipt_needed",
    claim: "A receipt is required for returns.",
    quote: null, // claim-only: the named section goes straight to the model
    recorded: { choice: "supports", confidence: 0.86 },
  },
];

const EXPECT = {
  warranty_years: "verified",
  water_voids: "contradicted",
  shipping_free: "unsupported",
  power_ten: "fabricated",
  receipt_needed: "verified",
};

const RELATION_TO_VERDICT = { supports: "verified", contradicts: "contradicted", says_nothing: "unsupported" };
const AUTO_ACCEPT = 0.8;

function normalize(text) {
  return text.replace(/[“”]/g, '"').replace(/[‘’]/g, "'").replace(/\s+/g, " ").trim();
}

function locate(source, citation) {
  if (citation.quote === null) return { status: "section-only" };
  return normalize(source).includes(normalize(citation.quote)) ? { status: "found" } : { status: "missing" };
}

function verdict(status, answer) {
  if (status === "missing") return { verdict: "fabricated", confidence: null, auto: true };
  return {
    verdict: RELATION_TO_VERDICT[answer.choice],
    confidence: answer.confidence,
    auto: answer.confidence >= AUTO_ACCEPT,
  };
}

function check(citation, answer) {
  const { status } = locate(SOURCE, citation);
  const v = verdict(status, answer);
  return { id: citation.id, status, ...v };
}

function checkFixtures() {
  for (const citation of CITATIONS) {
    const got = check(citation, citation.recorded).verdict;
    if (got !== EXPECT[citation.id]) {
      console.error(`fixture miss: ${citation.id} got ${got}, want ${EXPECT[citation.id]}`);
      process.exit(1);
    }
  }
}

function show() {
  console.log("citation  official shape: docs-mirror/typesafe/cookbooks/citation_check.md");
  console.log("");
  console.log(`${"citation".padEnd(16)}${"quote".padEnd(14)}${"relation".padEnd(14)}${"conf".padStart(6)}  ${"verdict".padEnd(13)}action`);
  for (const citation of CITATIONS) {
    const r = check(citation, citation.recorded);
    const relation = r.status === "missing" ? "-" : citation.recorded.choice;
    const conf = r.confidence === null ? "-" : r.confidence.toFixed(2);
    const action = r.verdict === "verified" && r.auto ? "stand" : r.verdict === "fabricated" ? "drop" : "review";
    console.log(`${r.id.padEnd(16)}${r.status.padEnd(14)}${relation.padEnd(14)}${conf.padStart(6)}  ${r.verdict.padEnd(13)}${action}`);
  }
}

checkFixtures();

const live = process.argv.includes("--live");
if (!live) {
  show();
  console.log("");
  console.log("fixture lane: recorded relations, no API call. --live spends a key.");
  process.exit(0);
}

const { askJevChoice } = await import("../../work/jev-client/src/index.ts");
const classes = {
  supports: "The section states the claim or directly implies that it is true",
  contradicts: "The section states the opposite of the claim or implies it is false",
  says_nothing: "The section does not address what the claim asserts, either way",
};
console.log("citation  lane=live");
console.log("");
for (const citation of CITATIONS) {
  const { status } = locate(SOURCE, citation);
  if (status === "missing") {
    console.log(`${citation.id.padEnd(16)}missing       -                   -  fabricated   drop`);
    continue;
  }
  const r = await askJevChoice({
    state: { claim: citation.claim, section: SOURCE },
    instructions: "How does the section relate to the claim?",
    classes,
    model: "jev-1.13.0",
    timeoutMs: 20000,
  });
  if (!r.ok) {
    console.error(`live call failed: ${r.reason} ${r.error}`);
    process.exit(2);
  }
  const v = verdict(status, { choice: r.choice, confidence: r.confidence });
  const action = v.verdict === "verified" && v.auto ? "stand" : "review";
  console.log(`${citation.id.padEnd(16)}found         ${r.choice.padEnd(14)}${r.confidence.toFixed(2).padStart(6)}  ${v.verdict.padEnd(13)}${action}`);
}

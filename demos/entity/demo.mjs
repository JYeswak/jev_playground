#!/usr/bin/env node
// Riff on the official entity-alignment cookbook. Keyless by default: four
// fixture candidate pairs with recorded answers, so the routing is visible
// without a key.
// `node demos/entity/demo.mjs --live` scores through work/jev-client.
// Official shape: docs-mirror/typesafe/cookbooks/entity_alignment.md
// (one Score with three level-descriptions plus three Nouls per pair, in one
// request; the nearest level names the outcome — no threshold constant).
// NO-CLAIM: a fixture alignment is not a live match.

const LEVELS = [
  "They describe two different products.",
  "They describe closely related products that may or may not be the same one: a variant, a special edition, or a name that could plausibly refer to either.",
  "They describe one and the same product.",
];
const OUTCOME = ["leave unlinked", "curator queue", "assert sameAs"];

const QUESTIONS = {
  link_state: {
    type: "score",
    instructions: "How do the two entity descriptions relate as products?",
    criteria: LEVELS,
  },
  same_name: { type: "noul", instructions: "Do the two entities state the same product name?" },
  same_brewery: { type: "noul", instructions: "Are the two entities from the same maker?" },
  same_style: { type: "noul", instructions: "Do the two entities describe the same product style?" },
};

const PAIRS = [
  {
    id: "same-pair",
    entity_a: { name: "Harbor Oatmeal Stout", maker: "Greyport Brewing", style: "Oatmeal Stout" },
    entity_b: { name: "Harbor Oatmeal Stout", maker: "Greyport Brewing", style: "Stout - Oatmeal" },
    recorded: { score: 1.94, confidence: 0.92, nouls: { same_name: 0.97, same_brewery: 0.99, same_style: 0.81 } },
  },
  {
    id: "diff-pair",
    entity_a: { name: "Frost Quake Barley Wine", maker: "Wellington County", style: "Barleywine" },
    entity_b: { name: "Ember Red Ale", maker: "Lompic Brewing", style: "Amber Ale" },
    recorded: { score: 0.03, confidence: 0.95, nouls: { same_name: 0.02, same_brewery: 0.09, same_style: 0.08 } },
  },
  {
    id: "style-words",
    entity_a: { name: "Belle Rousse", maker: "Brasseurs RJ", style: "Amber / Red Ale" },
    entity_b: { name: "Belle Rousse", maker: "Brasseurs RJ", style: "Amber Lager" },
    recorded: { score: 1.30, confidence: 0.27, nouls: { same_name: 0.95, same_brewery: 0.94, same_style: 0.35 } },
  },
  {
    id: "fruit-variant",
    entity_a: { name: "Ambleside Amber Ale", maker: "Bridge Brewing", style: "Amber / Red Ale" },
    entity_b: { name: "Bridge Ambleside Amber - Pomegranate", maker: "Bridge Brewing", style: "Amber Ale" },
    recorded: { score: 1.10, confidence: 0.77, nouls: { same_name: 0.63, same_brewery: 0.98, same_style: 0.74 } },
  },
];

const EXPECT = {
  "same-pair": "assert sameAs",
  "diff-pair": "leave unlinked",
  "style-words": "curator queue",
  "fruit-variant": "curator queue",
};

function route(scoreValue) {
  return OUTCOME[Math.min(Math.round(scoreValue), LEVELS.length - 1)];
}

function checkFixtures() {
  for (const pair of PAIRS) {
    const got = route(pair.recorded.score);
    if (got !== EXPECT[pair.id]) {
      console.error(`fixture miss: ${pair.id} got ${got}, want ${EXPECT[pair.id]}`);
      process.exit(1);
    }
  }
}

checkFixtures();

const live = process.argv.includes("--live");
let askLive = null;
if (live) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  askLive = async (pair) => {
    const r = await askJevBundle({
      model: "jev-1.13.0",
      state: { entity_a: pair.entity_a, entity_b: pair.entity_b },
      questions: QUESTIONS,
      timeoutMs: 30000,
    });
    if (!r.ok) {
      console.error(`live call failed: ${r.reason} ${r.error}`);
      process.exit(2);
    }
    const link = r.answers.link_state;
    return {
      score: link.score,
      confidence: link.confidence,
      nouls: {
        same_name: r.answers.same_name.noul,
        same_brewery: r.answers.same_brewery.noul,
        same_style: r.answers.same_style.noul,
      },
    };
  };
}

console.log("entity  official shape: docs-mirror/typesafe/cookbooks/entity_alignment.md");
console.log("");
for (const pair of PAIRS) {
  const rec = live
    ? await askLive(pair)
    : { score: pair.recorded.score, confidence: pair.recorded.confidence, nouls: pair.recorded.nouls };
  const outcome = route(rec.score);
  console.log(`${pair.id}  score ${rec.score.toFixed(2)}  confidence ${rec.confidence.toFixed(2)}  ->  ${outcome}`);
  console.log(`    ${pair.entity_a.name.slice(0, 44).padEnd(46)}${pair.entity_a.maker.slice(0, 30).padEnd(32)}${pair.entity_a.style.slice(0, 22)}`);
  console.log(`    ${pair.entity_b.name.slice(0, 44).padEnd(46)}${pair.entity_b.maker.slice(0, 30).padEnd(32)}${pair.entity_b.style.slice(0, 22)}`);
  console.log(`    name ${rec.nouls.same_name.toFixed(2)}   maker ${rec.nouls.same_brewery.toFixed(2)}   style ${rec.nouls.same_style.toFixed(2)}`);
  console.log("");
}
console.log(live ? "live lane: scored through askJevBundle." : "fixture lane: recorded answers, no API call. --live spends a key.");

#!/usr/bin/env node
// Riff on the official hierarchical-classification cookbook. Keyless by
// default: a tiny tree, two documents, and recorded per-node distributions,
// so greedy-vs-beam runs with no key.
// `node demos/hierarchy/demo.mjs --live` asks through work/jev-client.
// Official shape: docs-mirror/typesafe/cookbooks/hierarchical_classification.md
// (every sibling set is one Choice; greedy takes the top child, beam keeps K
// paths by geometric-mean edge probability; single-child edges are not
// decisions and score 1.0).
// NO-CLAIM: a fixture class is not a live label.

const TREE = {
  tech: { gadgets: {}, software: {} },
  food: { recipes: { pie: {} }, restaurants: {} },
};
const BEAM_WIDTH = 2;
const MAX_DEPTH = 6;

const DOCS = [
  {
    id: "pie-recipe",
    text: "apple pie recipe with cinnamon",
    recorded: {
      "": { tech: 0.55, food: 0.45 },
      tech: { gadgets: 0.6, software: 0.4 },
      food: { recipes: 0.9, restaurants: 0.1 },
    },
  },
  {
    id: "laptop-review",
    text: "laptop review with benchmark scores",
    recorded: {
      "": { tech: 0.9, food: 0.1 },
      tech: { gadgets: 0.85, software: 0.15 },
      food: { recipes: 0.5, restaurants: 0.5 },
    },
  },
];

const EXPECT = { "pie-recipe": "pie", "laptop-review": "gadgets" };

function childrenOf(path) {
  let node = TREE;
  for (const step of path) node = node[step];
  return Object.keys(node);
}

function extend(candidate, label, probabilities) {
  const isDecision = Object.keys(probabilities).length > 1;
  const product = candidate.product * (isDecision ? Math.max(probabilities[label], 1e-9) : 1.0);
  const decisions = candidate.decisions + (isDecision ? 1 : 0);
  return {
    path: [...candidate.path, label],
    product,
    decisions,
    score: decisions > 0 ? product ** (1 / decisions) : 1.0,
  };
}

function greedy(childrenFn, scoreFn) {
  let path = [];
  for (let i = 0; i < MAX_DEPTH; i++) {
    const children = childrenFn(path);
    if (children.length === 0) break;
    if (children.length === 1) {
      path = [...path, children[0]];
      continue;
    }
    const probs = scoreFn(path);
    path = [...path, children.reduce((a, b) => (probs[a] >= probs[b] ? a : b))];
  }
  return path;
}

function beam(childrenFn, scoreFn, width = BEAM_WIDTH) {
  let beam = [{ path: [], product: 1.0, decisions: 0, score: 1.0 }];
  for (let i = 0; i < MAX_DEPTH; i++) {
    const expandable = beam.filter((c) => childrenFn(c.path).length > 0);
    const finished = beam.filter((c) => childrenFn(c.path).length === 0);
    if (expandable.length === 0) {
      beam = finished;
      break;
    }
    const next = [...finished];
    for (const candidate of expandable) {
      const children = childrenFn(candidate.path);
      const probs = children.length === 1 ? { [children[0]]: 1.0 } : scoreFn(candidate.path);
      for (const label of children) next.push(extend(candidate, label, probs));
    }
    next.sort((a, b) => b.score - a.score);
    beam = next.slice(0, width);
  }
  beam.sort((a, b) => b.score - a.score);
  return beam[0];
}

const live = process.argv.includes("--live");
let askLive = null;
if (live) {
  const { askJevChoice } = await import("../../work/jev-client/src/index.ts");
  askLive = async (doc, path) => {
    const children = childrenOf(path);
    const classes = Object.fromEntries(children.map((c) => [c, `A document category named ${c}.`]));
    const r = await askJevChoice({
      state: { document: doc.text, parent: path.length > 0 ? path.join("/") : "root" },
      instructions: "Which direct child category best matches this document?",
      classes,
      model: "jev-1.13.0",
      timeoutMs: 20000,
    });
    if (!r.ok) {
      console.error(`live call failed: ${r.reason} ${r.error}`);
      process.exit(2);
    }
    return r.probabilities;
  };
}
console.log("hierarchy  official shape: docs-mirror/typesafe/cookbooks/hierarchical_classification.md");
console.log("");
let failed = 0;
for (const doc of DOCS) {
  const scoreFn = live
    ? (path) => askLive(doc, path)
    : (path) => doc.recorded[path.join("/")] ?? doc.recorded[""];
  const childrenFn = (path) => childrenOf(path);
  const g = greedy(childrenFn, scoreFn);
  const b = beam(childrenFn, scoreFn);
  const gLeaf = g[g.length - 1], bLeaf = b.path[b.path.length - 1];
  const mark = bLeaf === EXPECT[doc.id] ? "OK  " : "MISS";
  if (mark === "MISS") failed = 1;
  console.log(`[${mark}] ${doc.id} greedy=${g.join("/")} beam=${b.path.join("/")} (score ${b.score.toFixed(3)}) want=${EXPECT[doc.id]}`);
}
console.log("");
console.log(live ? "live lane: scored through askJevChoice." : "fixture lane: recorded distributions, no API call. --live spends a key.");
process.exit(failed ? 1 : 0);

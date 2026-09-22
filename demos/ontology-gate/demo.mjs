#!/usr/bin/env node
// Two lessons from EvoOntology (arXiv 2609.15779), as a keyless demo.
// Their numbers stay theirs. This file only shows the decision rules.

const PAPER = "arXiv:2609.15779";

function queryTerm(question, layer) {
  const hit = layer.terms.find((term) =>
    question.toLowerCase().includes(term.cue),
  );
  return hit ? hit.field : null;
}

function pasteAll(layer) {
  return layer.distractor;
}

function admit(parent, candidate, margin) {
  return candidate - parent >= margin ? "accept" : "reject";
}

const layer = {
  terms: [{ cue: "channel", field: "dim_channel.channel_name" }],
  distractor: "fact_cost.cost_type",
};

const lookup = queryTerm("cost by channel last quarter", layer);
const dumped = pasteAll(layer);
if (lookup !== "dim_channel.channel_name" || dumped === lookup) {
  console.error("query-vs-dump fixture failed");
  process.exit(1);
}

const margin = 0.02;
const near = admit(0.695, 0.71, margin);
const clear = admit(0.695, 0.82, margin);
if (near !== "reject" || clear !== "accept") {
  console.error("paired gate fixture failed", near, clear);
  process.exit(1);
}

console.log(`ontology gate  source: ${PAPER}  lane=fixture`);
console.log("");
console.log("query the term, do not paste the layer");
console.log(`  question: cost by channel last quarter`);
console.log(`  query  -> ${lookup}`);
console.log(`  paste  -> ${dumped}  (wrong field)`);
console.log("  paper: static semantic layer dropped 15.0 Traj-Wise on one backbone. Their number, not ours.");
console.log("");
console.log("ship a candidate only if it beats its parent");
console.log(`  parent 0.695  candidate 0.710  margin ${margin.toFixed(2)}  -> ${near}`);
console.log(`  parent 0.695  candidate 0.820  margin ${margin.toFixed(2)}  -> ${clear}`);
console.log("  paper: removing that gate dropped 11.2 Traj-Wise. Their ablation, not ours.");
console.log("");
console.log("fixture lane: no API call. Their benchmark was not re-run.");

#!/usr/bin/env node
// Riff on the official re-ranking cookbook. Keyless by default: a tiny
// fixture corpus, word-overlap shortlists, and recorded nouls so you can see
// the reorder without a key.
// `node demos/rerank/demo.mjs --live` scores through work/jev-client.
// Official shape: docs-mirror/typesafe/cookbooks/rerank_typesafe.md
// (fast-search shortlist, then one Noul per query-candidate pair with
// criteria fixing true and false, sort by noul highest first).
// NO-CLAIM: a fixture ranking is not a live search score.

const CORPUS = [
  { id: "p1", text: "courts award attorney fees to the prevailing party under the statute" },
  { id: "p2", text: "the prevailing party standard applies to fee shifting in civil cases" },
  { id: "p3", text: "filing deadlines for appeals run thirty days from judgment" },
  { id: "p4", text: "fee awards require a motion within fourteen days of entry" },
  { id: "p5", text: "prevailing party attorney fees fees fees costs expenses recovery" },
  { id: "p6", text: "jurors must disregard stricken testimony during deliberation" },
];

const QUERIES = [
  { id: "q1", text: "when must a motion be filed and does the attorney recover costs", gold: "p4" },
  { id: "q2", text: "who gets attorney fees as prevailing party", gold: "p1" },
];

// Recorded nouls per query-candidate pair (stand-ins for the Noul answers).
// Shaped so the word-overlap shortlist alone misses, and the rerank fixes it.
const RECORDED = {
  q1: { p5: 0.41, p4: 0.87, p1: 0.22, p2: 0.18, p3: 0.12 },
  q2: { p5: 0.55, p2: 0.61, p1: 0.88, p4: 0.15, p6: 0.09 },
};

const EXPECT_TOP = { q1: "p4", q2: "p1" };

const QUESTION = {
  type: "noul",
  instructions: "Is this candidate the cited case?",
  criteria: {
    true: "The candidate states the specific rule the query cites.",
    false: "The candidate is only on a similar topic.",
  },
};

function toks(s) {
  return s.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}

function shortlist(query, k = 5) {
  const qt = new Set(toks(query.text));
  return CORPUS.map((p) => ({ id: p.id, overlap: toks(p.text).filter((t) => qt.has(t)).length }))
    .sort((a, b) => b.overlap - a.overlap || (a.id < b.id ? -1 : 1))
    .slice(0, k)
    .map((r) => r.id);
}

async function rerank(query, scoreFn) {
  const ids = shortlist(query);
  const scored = [];
  for (const id of ids) {
    scored.push({ id, noul: await scoreFn(query, id) });
  }
  scored.sort((a, b) => b.noul - a.noul);
  return { shortlist: ids, ranked: scored.map((s) => s.id), scores: scored };
}

function checkFixtures() {
  for (const query of QUERIES) {
    const ids = shortlist(query);
    if (!ids.includes(query.gold)) {
      console.error(`fixture miss: gold ${query.gold} not in shortlist for ${query.id}`);
      process.exit(1);
    }
  }
}

checkFixtures();

const live = process.argv.includes("--live");
const scoreFn = live
  ? null
  : async (query, id) => RECORDED[query.id][id];

let failed = 0;
console.log("rerank  official shape: docs-mirror/typesafe/cookbooks/rerank_typesafe.md");
console.log("");
for (const query of QUERIES) {
  let score = scoreFn;
  if (live) {
    const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
    score = async (q, id) => {
      const passage = CORPUS.find((p) => p.id === id).text;
      const r = await askJevBundle({
        model: "jev-1.13.0",
        state: { query: q.text, candidate: passage },
        questions: { is_cited_source: QUESTION },
        timeoutMs: 20000,
      });
      if (!r.ok) {
        console.error(`live call failed: ${r.reason} ${r.error}`);
        process.exit(2);
      }
      return r.answers.is_cited_source.noul;
    };
  }
  const { shortlist: sl, ranked } = await rerank(query, score);
  const top = ranked[0];
  const mark = top === EXPECT_TOP[query.id] ? "OK  " : "MISS";
  if (mark === "MISS") failed = 1;
  console.log(`[${mark}] ${query.id} shortlist=[${sl.join(",")}] reranked-top=${top} want=${EXPECT_TOP[query.id]}`);
  if (!live && top !== query.gold) {
    console.error(`fixture miss: rerank top ${top} != gold ${query.gold} for ${query.id}`);
    process.exit(1);
  }
}
console.log("");
console.log(live ? "live lane: scored through askJevBundle." : "fixture lane: recorded nouls, no API call. --live spends a key.");
process.exit(failed ? 1 : 0);

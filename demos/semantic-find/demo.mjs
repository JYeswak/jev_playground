#!/usr/bin/env node
// Riff on the official line-by-line search cookbook. Keyless by default: a
// fixture document stands in for the ToS text, and recorded overlap scores
// stand in for the Choice ranking plus the Noul existence check. One query is
// answered, one is not — the exists check is what tells them apart.
// `node demos/semantic-find/demo.mjs --live` asks both cookbook questions in
// one request per query (Choice over line IDs + Noul exists) through
// work/jev-client, model jev-1.13.0.
// NO-CLAIM: a fixture find is not a live search.
import { search, DOC } from "./find.mjs";

const ANSWERED = "Can I get a refund on a digital download?";
const UNANSWERED = "What are the office holiday hours?";

const live = process.argv.includes("--live");
let askLive = null;
if (live) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  const ids = DOC.map((_, i) => `L${String(i + 1).padStart(2, "0")}`);
  const tagged = DOC.map((text, i) => `${ids[i]}: ${text}`).join("\n");
  askLive = async (query) => {
    const r = await askJevBundle({
      model: "jev-1.13.0",
      state: { document: tagged, query },
      questions: {
        where: {
          type: "choice",
          instructions: `Which line of the document contains the answer to: "${query}"?`,
          criteria: Object.fromEntries(ids.map((id) => [id, null])),
        },
        exists: {
          type: "noul",
          instructions: `Does any line of the document address or answer: "${query}"?`,
        },
      },
      timeoutMs: 20000,
    });
    if (!r.ok) {
      console.error(`live call failed: ${r.reason} ${r.error}`);
      process.exit(2);
    }
    const probs = r.answers.where.probabilities;
    const bestId = Object.keys(probs).reduce((a, b) => (probs[b] > probs[a] ? b : a));
    return { best: { id: bestId, text: DOC[ids.indexOf(bestId)] }, exists: r.answers.exists.noul };
  };
}

let failed = 0;
async function check(query, wantId, wantAnswered) {
  const r = live ? await askLive(query) : (() => { const s = search(query); return { best: s.best, exists: s.exists }; })();
  if (query !== ANSWERED) console.log(`query: ${query}`);
  console.log(`  points at ${r.best.id}: ${r.best.text}`);
  console.log(`  exists=${r.exists.toFixed(2)} -> ${r.exists >= 0.5 ? "ANSWER" : "no answer"}`);
  if (wantAnswered && (r.best.id !== wantId || r.exists < 0.5)) { console.error("MISS: answered query"); failed = 1; }
  if (!wantAnswered && r.exists >= 0.5) { console.error("MISS: unanswered query reads as answered"); failed = 1; }
  return r;
}

await check(ANSWERED, "L03", true);
await check(UNANSWERED, null, false);
console.log(live ? "live lane: Choice+Noul per query through askJevBundle." : "fixture lane: recorded overlap, no API call. --live spends a key.");
process.exit(failed);

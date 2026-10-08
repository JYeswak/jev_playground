// choice-rank.mjs (jev-xfji): ONE Jev Choice request ranking memory candidates.
// stdin: {query, candidates:[{id,text}], trunc=0 (0=full), model?}
// stdout: {top3:[ids], probs, usage, inputTokens, model, latencyMs}
// Key via env TYPESAFE_API_KEY (run under infisical run --projectId=...).
import { askJevChoice } from "../../kit/src/client.ts";

const input = JSON.parse(await new Response(Bun.stdin.stream()).text());
const { query, candidates, trunc = 0, model } = input;
if (!query || !Array.isArray(candidates) || candidates.length < 2) {
  console.error("need {query, candidates:[{id,text}] x>=2}");
  process.exit(2);
}
const cut = (t) => (trunc > 0 && t.length > trunc ? t.slice(0, trunc) + "…" : t);
const classes = Object.fromEntries(candidates.map((c) => [c.id, cut(c.text)]));
const res = await askJevChoice({
  state: { query, count: candidates.length },
  instructions: "Select the candidate memory most relevant to answering the query. Prefer memories that state the exact fact asked for.",
  classes,
  model,
});
if (!res.ok) {
  console.log(JSON.stringify({ ok: false, reason: res.reason, error: res.error }));
  process.exit(1);
}
const ranked = Object.entries(res.probabilities).sort((a, b) => b[1] - a[1]);
console.log(JSON.stringify({
  ok: true,
  top3: ranked.slice(0, 3).map(([id]) => id),
  probs: Object.fromEntries(ranked),
  usage: res.usage ?? null,
  inputTokens: res.usage?.input_tokens ?? res.usage?.input ?? null,
  model: res.model,
  latencyMs: res.latencyMs,
}));

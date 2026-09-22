/**
 * Fixture confidence-gated classification (cookbook shape, FIXTURE SCORING).
 * One Choice over the groups; confidence is the margin 1 - second/best.
 * At CONFIDENT or above the group is reported, below it the parent division —
 * every filing gets a usable label, none is dropped. Scoring here is token
 * overlap; the gate shape (group-when-sure-else-division) is the cookbook's.
 */
const STOP = new Set("a an the and or of to in on for with is are was were be by as at it its this that what which who how when from into over under then than so such no not only own same too very can will just don should now our with".split(" "));

function toks(s) {
  return s.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t && !STOP.has(t));
}

export const CONFIDENT = 0.9;

export const DIVISIONS = {
  food: ["bakery", "dairy"],
  tools: ["saws", "drills"],
  finance: ["ledger", "audit"],
};

export const GROUPS = {
  bakery: "bread oven flour yeast pastry bake bakes selling daily stone",
  dairy: "milk cheese butter yogurt cream",
  saws: "saw saws blade cut cuts timber",
  drills: "drill drills bit bore bores hole holes",
  ledger: "ledger debit credit balance",
  audit: "audit compliance control risk",
};

function overlap(a, b) {
  const sa = new Set(a), sb = new Set(b);
  if (sa.size === 0 || sb.size === 0) return 0;
  let hit = 0;
  for (const t of sa) if (sb.has(t)) hit += 1;
  return hit / Math.sqrt(sa.size * sb.size);
}

export function divisionOf(group) {
  for (const [div, members] of Object.entries(DIVISIONS)) {
    if (members.includes(group)) return div;
  }
  return "unknown";
}

export function classify(text) {
  const wt = toks(text);
  const scored = Object.entries(GROUPS)
    .map(([name, desc]) => ({ name, score: overlap(wt, toks(desc)) }))
    .sort((a, b) => b.score - a.score);
  const [best, second] = scored;
  const confidence = best.score <= 0 ? 0 : 1 - (second.score / best.score);
  const sure = confidence >= CONFIDENT;
  return {
    level: sure ? "group" : "division",
    label: sure ? best.name : divisionOf(best.name),
    confidence, group: best.name,
  };
}

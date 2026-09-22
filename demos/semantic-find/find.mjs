/**
 * Fixture line-by-line search (cookbook shape, FIXTURE SCORING).
 * Lines carry IDs; a Choice over line IDs points at the answer line, and a
 * Noul existence check separates a real answer from the closest irrelevant
 * line (Choice probabilities always sum to 1, so ranking alone cannot).
 * Fixture scoring is token overlap; the two-question shape is the cookbook's.
 */
const STOP = new Set("a an the and or of to in on for with is are was were be by as at it its this that what which who how when from into over under then than so such no not only own same too very can will just don should now does any".split(" "));

function toks(s) {
  return s.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t && !STOP.has(t));
}

export const DOC = [
  "Our refund window is thirty days from purchase.",
  "Shipping is free over fifty dollars.",
  "Digital download purchases are final sale with no refund.",
  "Contact support to start a return.",
  "Gift cards never expire.",
  "Sale items can be exchanged within fourteen days.",
  "Accounts close after one year of inactivity.",
  "Prices include tax where required by law.",
];

function overlap(a, b) {
  const sa = new Set(a), sb = new Set(b);
  if (sa.size === 0 || sb.size === 0) return 0;
  let hit = 0;
  for (const t of sa) if (sb.has(t)) hit += 1;
  return hit / Math.sqrt(sa.size * sb.size);
}

export function search(query, lines = DOC) {
  const qt = toks(query);
  const ranked = lines
    .map((text, i) => ({ id: `L${String(i + 1).padStart(2, "0")}`, text, score: overlap(qt, toks(text)) }))
    .sort((a, b) => b.score - a.score);
  const total = ranked.reduce((n, r) => n + r.score, 0);
  const exists = total > 0 ? ranked[0].score / total : 0;
  return { best: ranked[0], exists, ranked };
}

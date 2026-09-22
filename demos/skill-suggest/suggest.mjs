/**
 * Fixture two-stage skill suggestion (cookbook shape, FIXTURE SCORING).
 * Call 1: rank every roster skill by token overlap with the turn (stand-in
 * for the Choice ranking). Call 2: verify the top three with a second
 * overlap against full descriptions (stand-in for the verify call).
 * Gate: best verified score below GATE means suggest nothing — abstention is
 * first-class, exactly as the cookbook's none-fit path requires.
 */
const STOP = new Set("a an the and or of to in on for with is are was were be by as at it its this that what which who how when from into over under then than so such no not only own same too very can will just don should now you your we me my and edit".split(" "));

function toks(s) {
  return s.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t && !STOP.has(t));
}

export const GATE = 0.3;

export const ROSTER = [
  { name: "music-video", description: "cut iphone takes lip-synced performance music video master track", detail: "Synchronize multiple camera takes to a clean audio master for music videos." },
  { name: "screencast-redact", description: "redact sensitive parts macos screen recordings black-box secrets pii", detail: "Black-box regions of screencast video files before publishing." },
  { name: "photo-organize", description: "sort photo library faces places dates albums", detail: "Organize large photo collections by content and metadata." },
  { name: "pdf-extract", description: "extract tables text pdf documents ocr", detail: "Pull structured content out of PDF files." },
  { name: "meeting-notes", description: "summarize meetings action items transcript", detail: "Turn meeting transcripts into notes with owners." },
];

function overlap(a, b) {
  const sa = new Set(a), sb = new Set(b);
  if (sa.size === 0 || sb.size === 0) return 0;
  let hit = 0;
  for (const t of sa) if (sb.has(t)) hit += 1;
  return hit / Math.sqrt(sa.size * sb.size);
}

export function suggest(text, roster) {
  const wt = toks(text);
  const ranked = roster
    .map((s) => ({ name: s.name, score: overlap(wt, toks(s.description)) }))
    .sort((a, b) => b.score - a.score);
  const top3 = ranked.slice(0, 3);
  const verified = top3.map((c) => {
    const full = roster.find((s) => s.name === c.name);
    return { name: c.name, score: overlap(wt, toks(full.description + " " + full.detail)) };
  }).sort((a, b) => b.score - a.score);
  const best = verified[0];
  if (!best || best.score < GATE) return { skill: null, best: best ? best.score : 0 };
  return { skill: best.name, score: best.score };
}

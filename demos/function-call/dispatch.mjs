/**
 * Fixture function dispatcher (cookbook shape, FIXTURE SCORING).
 * Spec: one Choice picks the function; each argument gets a Choice over its
 * closed option set plus a Noul "stated?" that leaves the argument out (so
 * the function default applies) when the command says nothing about it.
 * Scoring here is token overlap — a stand-in for the typed questions.
 * Confidence of a call = least certain judgment behind it (cookbook rule).
 */
const STOP = new Set("a an the and or of to in on for with is are was were be by as at it its this that what which who how when from into over under then than so such no not only own same too very can will just don should now you your we me my the".split(" "));

function toks(s) {
  return s.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t && !STOP.has(t));
}

function overlap(a, b) {
  const sa = new Set(a), sb = new Set(b);
  if (sa.size === 0 || sb.size === 0) return 0;
  let hit = 0;
  for (const t of sa) if (sb.has(t)) hit += 1;
  return hit / Math.sqrt(sa.size * sb.size);
}

export const SPEC = {
  functions: {
    plot_price: {
      description: "draw a price chart",
      arguments: {
        style: { question: "plain line or candles", options: { line: "simple line closing prices chart", candles: "candles candlestick OHLC bars" } },
        ma: { question: "moving average bars nine twenty fifty", options: { 9: "9 nine bar fast average", 20: "20 twenty bar average", 50: "50 fifty bar slow average" } },
      },
    },
    get_quote: {
      description: "current price single ticker quote",
      arguments: {
        symbol: { question: "which ticker symbol", options: { AAPL: "AAPL apple ticker", NVDA: "NVDA nvidia ticker", TSLA: "TSLA tesla ticker" } },
      },
    },
  },
};

export function dispatch(command, spec = SPEC) {
  const wt = toks(command);
  const toolScores = Object.entries(spec.functions).map(([name, fn]) => ({
    name, score: overlap(wt, toks(name.replace(/_/g, " ") + " " + fn.description)),
  })).sort((a, b) => b.score - a.score);
  const tool = toolScores[0].name;
  const args = {};
  const certs = [toolScores[0].score];
  for (const [arg, def] of Object.entries(spec.functions[tool].arguments)) {
    const optScores = Object.entries(def.options).map(([k, v]) => ({ k, score: overlap(wt, toks(v)) }));
    const stated = Math.max(...optScores.map((o) => o.score));
    if (stated <= 0) continue;
    certs.push(stated);
    optScores.sort((a, b) => b.score - a.score);
    args[arg] = optScores[0].k;
  }
  return { tool, args, confidence: Math.min(...certs) };
}

/**
 * Offline proof that the ranker uses scores, not lexical overlap.
 * No key. No network. The NevIR numbers it prints are read from the committed
 * cache at HEAD (cd9a35b); the working tree of that clone is dirty and is not
 * executed here.
 *
 *   node --experimental-strip-types work/nev-rerank/rank.mjs
 */
import { execFileSync } from "node:child_process";
import { lexicalOrder, rerank } from "./src/rank.ts";

const QUERY = "Which runtime does NOT use a garbage collector?";
const TRAP = "This runtime uses a garbage collector to reclaim unused memory automatically.";
const ANSWER = "This runtime frees memory by explicit ownership. Collection is not part of the design.";

const lexical = lexicalOrder(QUERY, [TRAP, ANSWER]);
const ranked = await rerank(QUERY, [TRAP, ANSWER], async () => ({ ok: true, scores: { p01: 0.05, p02: 0.95 } }));
const raw = execFileSync("git", ["-C", "jev-rerank-bench", "show", "HEAD:results/nevir.json"], { encoding: "utf8" });
const cache = JSON.parse(raw);
const jev = cache["jev-score-batch"].paired_accuracy;
const bm25 = cache.bm25.paired_accuracy;

const lexicalPickedTrap = lexical[0] === 0;
const scorePickedAnswer = ranked.ordered && ranked.ranking[0].text === ANSWER;
console.log(`nevIR cache  jev-score-batch ${jev.toFixed(4)}  bm25 ${bm25.toFixed(4)}  n=${cache.bm25.pairs}`);
console.log(`fixture      lexical-first ${lexicalPickedTrap ? "TRAP" : "ANSWER"}  score-first ${scorePickedAnswer ? "ANSWER" : "TRAP"}`);
console.log(lexicalPickedTrap && scorePickedAnswer ? "PASS lexical loses, scores win" : "FAIL");
process.exit(lexicalPickedTrap && scorePickedAnswer ? 0 : 1);

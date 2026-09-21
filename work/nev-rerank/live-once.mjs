/**
 * One live systemOne call. Two Score questions. One planted negation pair.
 * Budget: 1 request. Model jev-1.13.0. This is a smoke, not a replication of n=1383.
 *
 * Offline was insufficient: the fixture asker is scripted. This asks whether the
 * live model orders a negation that lexical overlap gets wrong.
 *
 * Exit 0 ordered, 2 NOT_RUN (no key / transport), 1 the call returned but did not order.
 */
import { lexicalOrder, rerank } from "./src/rank.ts";
import { liveAsker } from "./src/live.ts";

const QUERY = "Which runtime does NOT use a garbage collector?";
const TRAP = "This runtime uses a garbage collector to reclaim unused memory automatically.";
const ANSWER = "This runtime frees memory by explicit ownership. Collection is not part of the design.";

if (!process.env.TYPESAFE_API_KEY) {
  console.log("NOT_RUN no TYPESAFE_API_KEY");
  process.exit(2);
}

const lexical = lexicalOrder(QUERY, [TRAP, ANSWER]);
const ranked = await rerank(QUERY, [TRAP, ANSWER], liveAsker);
console.log(`lexical-first ${lexical[0] === 0 ? "TRAP" : "ANSWER"}`);
console.log(`ordered=${ranked.ordered} reason=${ranked.reason ?? "-"} calledModel=${ranked.calledModel}`);
for (const row of ranked.ranking) {
  const label = row.text === ANSWER ? "ANSWER" : "TRAP";
  console.log(`  ${row.id} ${label} score=${Number.isFinite(row.score) ? row.score.toFixed(3) : "-"}`);
}
process.exit(ranked.ordered ? 0 : 2);

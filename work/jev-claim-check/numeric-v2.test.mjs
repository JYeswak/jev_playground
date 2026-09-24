/**
 * Tokenizer and evidence-narrowing tests for numeric-v2.mjs (bead jev-h8s). No key, no network.
 * Run: node --test work/jev-claim-check/numeric-v2.test.mjs
 *
 * The table is the contract: each claim fragment must parse to exactly these number tokens.
 * Planted red: the same table run against the jev-2mp tokenizer (check-close.mjs numberTokens) must
 * fail on at least the scientific-notation and list rows. If it ever passes, this table has stopped
 * testing what changed.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { numberTokensV2, narrowEvidence } from "./numeric-v2.mjs";
import { numberTokens as oldTokens } from "./check-close.mjs";

const TABLE = [
  ["McNemar p = 2.6e-13", ["2.6e-13"]],
  ["pinned model: ECE 0.0614, Brier 0.0195", ["0.0614", "0.0195"]],
  ["Live 75/219 top-1", ["75/219"]],
  ["extract 1067/1145 loses to 1,145 rows", ["1067/1145", "1,145"]],
  ["accuracy 96.0% on the set", ["96.0%"]],
  ["Jev FP 7/300 (2.3%, Wilson 1.1-4.7%)", ["7/300", "2.3%", "1.1-4.7%"]],
  ["criteria flags 60,97,143,250 all adjudicated", ["60", "97", "143", "250"]],
  ["harvest regenerated 87,894 -> REFUSED exit 2.", ["87,894", "2"]],
  ["pinned jev-1.13.0 on Python 3.14.2", []],
  ["SST-5 run-1 top-1", []],
  ["corrected p=4.1e-10, flips 0.43->0.89", ["4.1e-10", "0.43", "0.89"]],
  ["MAE 0.488/0.500/0.492 over 3 runs", ["0.488/0.500/0.492", "3"]],
];

const texts = (fn, s) => fn(s).map((t) => t.text);

test("every row parses to exactly its tokens", () => {
  for (const [input, want] of TABLE) assert.deepEqual(texts(numberTokensV2, input), want, input);
});

test("token offsets point at the token text", () => {
  for (const [input] of TABLE) for (const t of numberTokensV2(input)) assert.equal(input.slice(t.at, t.at + t.text.length), t.text, input);
});

test("planted red: the jev-2mp tokenizer fails this table", () => {
  const wrong = TABLE.filter(([input, want]) => JSON.stringify(texts(oldTokens, input)) !== JSON.stringify(want)).map(([input]) => input);
  assert.ok(wrong.includes("McNemar p = 2.6e-13"), `old tokenizer parsed 2.6e-13 exactly: ${wrong}`);
  assert.ok(wrong.includes("criteria flags 60,97,143,250 all adjudicated"), "old tokenizer split the list exactly");
});

const EVIDENCE = [
  "# Receipt",
  "unrelated preamble line about setup",
  "| measure | value |",
  "| Jev top-1 | 75/219 = 0.3425, Wilson 95% CI lower 0.2828 |",
  "| bar (lower-CI > 0.3242) | FAIL |",
  "footer",
].join("\n");

test("narrowed evidence never depends on the checked value", () => {
  const clause = "Live 75/219 top-1 (lower-CI 0.2828 < lexical 0.3242)";
  const planted = "Live 79/219 top-1 (lower-CI 0.2828 < lexical 0.3242)";
  assert.equal(narrowEvidence(EVIDENCE, clause, 5), narrowEvidence(EVIDENCE, planted, 5));
});

test("a plant that collides with another number in its clause still gets its original's evidence", () => {
  const ev = ["filler a", "filler b", "value 23 only", "filler c", "filler d", "filler e", "attribution table 35"].join("\n");
  const real = narrowEvidence(ev, "Agent-failure attribution: 28 of 35 against grok's 23", 27);
  assert.match(real, /value 23 only/, "the other number 23 anchors its row");
  assert.equal(narrowEvidence(ev, "Agent-failure attribution: 23 of 35 against grok's 23", 27), real);
});

test("narrowed evidence keeps the matching row and drops what matches nothing", () => {
  const ev = narrowEvidence(EVIDENCE, "Live 75/219 top-1 (lower-CI 0.2828 < lexical 0.3242)", 5);
  assert.match(ev, /75\/219 = 0\.3425/);
  assert.doesNotMatch(ev, /# Receipt/);
});

test("a clause that matches no line gets no evidence", () => {
  assert.equal(narrowEvidence(EVIDENCE, "zebra quokka 12", 13), "");
});

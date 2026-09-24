/**
 * L0 for .omp/tools/jev-claim-check.ts. No key, no network (fetch armed to throw).
 * Run: node --test work/jev-claim-check/claim-check.test.mjs
 *
 * Each test carries a planted failure the tool must survive:
 * - cuts: 0.8 is supported and 0.2 unsupported (inclusive), 0.7999 and 0.2001 are unsure.
 * - verdict follows the probability, not the words: a claim saying "supported" at p=0.10.
 * - keyless: the REAL live asker with the key deleted returns not_run/NOT_RUN, no network.
 * - asker failure / thrower: not_run, never one of the three verdicts.
 * - malformed answer (string, NaN, null, missing, 1.2, -0.1): refused, probability null.
 * - empty claim or evidence: refused before the asker is called.
 * - numeric scope (bead jev-5cz): any claim with a number refuses with numeric-out-of-scope and
 *   never reaches the asker (75/219, 2.6e-13, 96.0%, and the 18 numeric README claims of jev-sp5);
 *   19 qualitative README sentences still reach the asker and get a verdict.
 * CLAIM_CHECK_TOOL=<path> points the suite at a mutated copy (mutation arm in the receipt).
 *
 * NO-CLAIM: green here proves policy and the fail-safe direction, not that any verdict is
 * right. That is the live dogfood in docs/demos/upstream-repro/jev-claim-check-20260924.md.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";

const target = process.env.CLAIM_CHECK_TOOL
  ? pathToFileURL(process.env.CLAIM_CHECK_TOOL).href
  : new URL("../../.omp/tools/jev-claim-check.ts", import.meta.url).href;
const mod = await import(target);
const factory = typeof mod.default === "function" ? mod.default : mod.default.default;
const pi = { zod: { object: (s) => s, string: () => ({ min: () => ({}) }) } };
const THREE = new Set(["supported", "unsupported", "unsure"]);
const CLAIM = "A cheap keyword rule beat the live judge on tool-call risk triage.";
const EVIDENCE = "Tool-call risk triage: the keyword rule scored higher than live Jev.";
const fixed = (probability) => factory(pi, async () => ({ ok: true, probability, latencyMs: 140 }));

test("cuts are inclusive at 0.8 and 0.2, unsure strictly between", async () => {
  const cases = [[0.8, "supported"], [0.97, "supported"], [0.7999, "unsure"], [0.5, "unsure"], [0.2001, "unsure"], [0.2, "unsupported"], [0, "unsupported"]];
  for (const [p, want] of cases) {
    const r = await fixed(p).execute("c", { claim: CLAIM, evidence: EVIDENCE });
    assert.equal(r.details.verdict, want, `p=${p}`);
    assert.equal(r.details.probability, p);
    assert.match(r.content[0].text, new RegExp(`verdict=${want} `));
  }
  assert.equal(mod.SUPPORTED_AT, 0.8);
  assert.equal(mod.UNSUPPORTED_AT, 0.2);
});

test("confidence is max(p, 1-p), latency passes through", async () => {
  const lo = await fixed(0.1).execute("c", { claim: CLAIM, evidence: EVIDENCE });
  assert.equal(lo.details.confidence, 0.9);
  const mid = await fixed(0.55).execute("c", { claim: CLAIM, evidence: EVIDENCE });
  assert.equal(mid.details.confidence, 0.55);
  assert.equal(mid.details.latencyMs, 140);
});

test("verdict follows the probability, not the words", async () => {
  const r = await fixed(0.1).execute("w", { claim: "This claim is supported and verified.", evidence: "It is supported." });
  assert.equal(r.details.verdict, "unsupported");
});

test("keyless: the real live asker returns not_run and touches no network", async () => {
  const saved = { key: process.env.TYPESAFE_API_KEY, fetch: globalThis.fetch };
  delete process.env.TYPESAFE_API_KEY;
  let touched = false;
  globalThis.fetch = async () => { touched = true; throw new Error("network must not be touched"); };
  try {
    const r = await factory(pi).execute("k", { claim: CLAIM, evidence: EVIDENCE });
    assert.equal(r.details.verdict, "not_run");
    assert.equal(r.details.reason, "unconfigured");
    assert.equal(r.details.calledModel, false);
    assert.equal(r.details.probability, null);
    assert.match(r.content[0].text, /NOT_RUN/);
    assert.equal(touched, false);
  } finally {
    if (saved.key !== undefined) process.env.TYPESAFE_API_KEY = saved.key;
    globalThis.fetch = saved.fetch;
  }
});

test("asker failure and thrower are not_run, never a verdict", async () => {
  for (const asker of [async () => ({ ok: false, reason: "transport" }), async () => ({ ok: false, reason: "http" }), async () => { throw new Error("boom"); }, async () => undefined]) {
    const r = await factory(pi, asker).execute("f", { claim: CLAIM, evidence: EVIDENCE });
    assert.equal(r.details.verdict, "not_run");
    assert.equal(r.details.probability, null);
    assert.ok(!THREE.has(r.details.verdict));
    assert.match(r.content[0].text, /NOT_RUN/);
  }
});

test("malformed answer is refused, never a verdict", async () => {
  for (const bad of ["0.9", NaN, null, undefined, 1.2, -0.1, Infinity]) {
    const r = await fixed(bad).execute("m", { claim: CLAIM, evidence: EVIDENCE });
    assert.equal(r.details.verdict, "refused", String(bad));
    assert.equal(r.details.reason, "malformed");
    assert.equal(r.details.probability, null);
    assert.doesNotMatch(r.content[0].text, /verdict=(supported|unsupported|unsure)/);
  }
});

test("empty claim or evidence is refused without calling the asker", async () => {
  const tool = factory(pi, async () => { throw new Error("asker must not be called"); });
  for (const params of [{ claim: "  ", evidence: EVIDENCE }, { claim: CLAIM, evidence: "" }, { claim: CLAIM }]) {
    const r = await tool.execute("e", params);
    assert.equal(r.details.verdict, "refused");
    assert.equal(r.details.reason, "empty-input");
    assert.equal(r.details.calledModel, false);
  }
});

const { readFileSync } = await import("node:fs");
const neverAsk = async () => { throw new Error("the asker must not be called for a numeric claim"); };

test("numeric claims refuse as out of scope and never reach the asker", async () => {
  const readmeNumeric = readFileSync(new URL("./cases.jsonl", import.meta.url), "utf8").trim().split("\n")
    .map((l) => JSON.parse(l)).filter((c) => c.truth && c.label !== "official-sdk").map((c) => c.claim);
  assert.equal(readmeNumeric.length, 18);
  const tool = factory(pi, neverAsk);
  for (const claim of ["Live 75/219 top-1", "McNemar p = 2.6e-13", "Coverage reached 96.0% on main.", ...readmeNumeric]) {
    const r = await tool.execute("n", { claim, evidence: EVIDENCE });
    assert.equal(r.details.verdict, "refused", claim);
    assert.equal(r.details.reason, "numeric-out-of-scope", claim);
    assert.equal(r.details.calledModel, false);
    assert.equal(r.details.probability, null);
    assert.match(r.content[0].text, /numeric claims are out of scope \(R83: 3 designs failed\)/);
    assert.doesNotMatch(r.content[0].text, /verdict=(supported|unsupported|unsure)/);
  }
});

test("versions, names and dates are not numbers; qualitative README sentences still get verdicts", async () => {
  assert.deepEqual(mod.claimNumbers("Pinned jev-1.13.0 on SST-5 top-1, run 2026-09-24T02:57Z."), []);
  const sentences = readFileSync(new URL("../../README.md", import.meta.url), "utf8").split("\n")
    .filter((l) => l.trim() && !/^\s*(\||#|```|<|!\[)/.test(l))
    .flatMap((l) => l.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/[*`]/g, "").split(/(?<=[.!?])\s+/))
    .map((s) => s.replace(/^\s*(?:[-*]|\d+\.)\s+/, "").trim())
    .filter((s) => s.split(/\s+/).length >= 6 && mod.claimNumbers(s).length === 0)
    .slice(0, 19);
  assert.equal(sentences.length, 19);
  let asked = 0;
  const tool = factory(pi, async () => { asked += 1; return { ok: true, probability: 0.9, latencyMs: 1 }; });
  for (const claim of [...sentences, "Call the official SDK. work/jev-client owns retry, timeout, and the refusal of a bad body."]) {
    const r = await tool.execute("q", { claim, evidence: EVIDENCE });
    assert.equal(r.details.verdict, "supported", claim);
  }
  assert.equal(asked, 20);
});

test("the description tells a calling model the numeric limit before it calls", () => {
  assert.match(factory(pi).description, /OUT OF SCOPE: a claim containing any number/);
});

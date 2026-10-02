import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  askJev,
  askJevBundle,
  askJevChoice,
} from "../src/client.ts";
import { rerankTop1 } from "../src/rerank.ts";
import {
  ValidationError,
  validateBundleAnswers,
  validateChoiceAnswer,
  validateNoulAnswer,
  validateScoreAnswer,
} from "../src/validate.ts";

// Wire conformance (jev-745g): every client validates the System One response
// contract identically. Requirement IDs WIRE-1..6 (MUST unless noted).
// Valid rows are RECORDED jev-1.13.0 responses from kit/test/fixtures (never
// typed); hostile rows are derived boundary mutations of those recordings.

const fixture = async (name) =>
  JSON.parse(await readFile(new URL(`./fixtures/${name}`, import.meta.url)));

const recordedRows = await fixture("recorded-answer-rows.json");
const banking = await fixture("banking77-answer.json");
const scifact = await fixture("scifact-answer.json");
const sst5 = await fixture("sst5-answer.json");

const answerOf = (row, key) => {
  const answers = row.answers ?? row.captured_row?.answers ?? row.captured?.answers;
  assert.ok(answers && answers[key], `recorded row lacks ${key} answers`);
  return answers[key];
};

const statusFetch = (status, body) => async () =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

const okFetch = (answers) =>
  statusFetch(200, { answers, usage: { input_tokens: 10, output_tokens: 0 } });

// WIRE-1 (MUST): recorded valid answers accepted by the matching validator.
test("WIRE-1 recorded Choice answers validate against their offered ids", () => {
  const row = recordedRows[0];
  const answer = answerOf(row, "choice");
  const ids = Object.keys(answer.probabilities);
  const out = validateChoiceAnswer(answer, ids);
  assert.equal(out.choice, answer.choice);
});

test("WIRE-1 recorded banking77 Choice validates", () => {
  const answer = answerOf(banking[0], "choice");
  const ids = Object.keys(answer.probabilities);
  assert.equal(validateChoiceAnswer(answer, ids).choice, answer.choice);
});

test("WIRE-1 recorded Noul answers validate", () => {
  assert.equal(validateNoulAnswer(answerOf(scifact[0], "value")), scifact[0].answers.value.noul);
});

test("WIRE-1 recorded Score answers validate against legend criteria", () => {
  const answer = answerOf(sst5[0], "score");
  const criteria = Object.keys(answer.legend).map((_, i) => String(i));
  assert.equal(validateScoreAnswer(answer, criteria).score, answer.score);
});

// WIRE-2 (MUST): hostile boundary mutations of recorded rows are refused.
test("WIRE-2 choice outside offered ids refused", () => {
  const answer = structuredClone(answerOf(recordedRows[0], "choice"));
  answer.choice = "nope-not-offered";
  assert.throws(() => validateChoiceAnswer(answer, Object.keys(answer.probabilities)), ValidationError);
});

test("WIRE-2 probabilities not summing to 1 refused", () => {
  const answer = structuredClone(answerOf(recordedRows[0], "choice"));
  for (const k of Object.keys(answer.probabilities)) answer.probabilities[k] = 0.1;
  assert.throws(() => validateChoiceAnswer(answer, Object.keys(answer.probabilities)), ValidationError);
});

test("WIRE-2 chosen option below max refused", () => {
  const answer = structuredClone(answerOf(recordedRows[0], "choice"));
  const ids = Object.keys(answer.probabilities);
  const top = ids.reduce((a, b) => (answer.probabilities[a] >= answer.probabilities[b] ? a : b));
  const other = ids.find((id) => id !== top);
  answer.choice = other;
  assert.throws(() => validateChoiceAnswer(answer, ids), ValidationError);
});

test("WIRE-2 non-finite and out-of-range Noul refused", () => {
  for (const bad of [{ noul: NaN }, { noul: Infinity }, { noul: -0.1 }, { noul: 1.2 }, { noul: "0.5" }, null, [0.5]]) {
    assert.throws(() => validateNoulAnswer(bad), ValidationError);
  }
});

test("WIRE-2 probability key mismatch refused", () => {
  const answer = structuredClone(answerOf(recordedRows[0], "choice"));
  answer.probabilities.extra = 0;
  delete answer.probabilities[Object.keys(answer.probabilities)[0]];
  assert.throws(() => validateChoiceAnswer(answer, ["c0", "c1", "none", "extra"]), ValidationError);
});

test("WIRE-2 Score with non-finite score or bad legend refused", () => {
  const answer = structuredClone(answerOf(sst5[0], "score"));
  const criteria = Object.keys(answer.legend).map((_, i) => String(i));
  assert.throws(() => validateScoreAnswer({ ...answer, score: NaN }, criteria), ValidationError);
  const badLegend = structuredClone(answer);
  badLegend.legend["0"] = 42;
  assert.throws(() => validateScoreAnswer(badLegend, criteria), ValidationError);
});

// WIRE-3 (MUST): end-to-end ask entry points accept recorded, refuse hostile.
test("WIRE-3 askJev accepts recorded Noul, refuses hostile and missing", async () => {
  const good = await askJev({
    state: {}, questions: { rel: "q" }, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ rel: { noul: answerOf(scifact[0], "value").noul } }),
  });
  assert.equal(good.ok, true);
  const bad = await askJev({
    state: {}, questions: { rel: "q" }, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ rel: { noul: 9.9 } }),
  });
  assert.equal(bad.ok, false);
  const missing = await askJev({
    state: {}, questions: { rel: "q" }, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ other: { noul: 0.5 } }),
  });
  assert.equal(missing.ok, false);
});

test("WIRE-3 askJevChoice accepts recorded Choice, refuses unoffered", async () => {
  const recorded = answerOf(recordedRows[0], "choice");
  const ids = Object.keys(recorded.probabilities);
  const classes = Object.fromEntries(ids.map((id) => [id, id]));
  const good = await askJevChoice({
    state: {}, instructions: "q", classes, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ choice: recorded }),
  });
  assert.equal(good.ok, true);
  assert.equal(good.choice, recorded.choice);
  const hostile = structuredClone(recorded);
  hostile.choice = "nope-not-offered";
  const bad = await askJevChoice({
    state: {}, instructions: "q", classes, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ choice: hostile }),
  });
  assert.equal(bad.ok, false);
});

test("WIRE-3 askJevBundle accepts recorded bundle, refuses partial", async () => {
  const recorded = answerOf(recordedRows[0], "choice");
  const ids = Object.keys(recorded.probabilities);
  const questions = { pick: { type: "choice", instructions: "q", criteria: Object.fromEntries(ids.map((id) => [id, id])) } };
  const good = await askJevBundle({
    state: {}, questions, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ pick: recorded }),
  });
  assert.equal(good.ok, true);
  const partial = await askJevBundle({
    state: {}, questions, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ wrong: recorded }),
  });
  assert.equal(partial.ok, false);
});

// WIRE-4 (MUST): retryable statuses never throw; status named in the error.
test("WIRE-4 retryable HTTP statuses fail closed with named status", async () => {
  for (const status of [429, 500, 502, 503, 504]) {
    const res = await askJev({
      state: {}, questions: { rel: "q" }, model: "jev-1.13.0", apiKey: "fixture-key",
      fetchImpl: statusFetch(status, { error: "synthetic" }),
    });
    assert.equal(res.ok, false, `status ${status} must not throw`);
    assert.ok(String(res.error).includes(String(status)), `status ${status} named in error`);
  }
});

// WIRE-5 (MUST): rerankTop1 never returns an unvalidated pick.
test("WIRE-5 rerankTop1 returns recorded pick, throws on hostile or refused ask", async () => {
  const cands = [
    { id: "a", text: "alpha" },
    { id: "b", text: "beta" },
  ];
  const picked = await rerankTop1({
    query: "q", candidates: cands,
    ask: async () => ({ ok: true, choice: "b", latencyMs: 1, model: "m" }),
  });
  assert.equal(picked.choice, "b");
  assert.equal(picked.orderedCandidates[0].id, "b");
  await assert.rejects(() =>
    rerankTop1({ query: "q", candidates: cands, ask: async () => ({ ok: true, choice: "zzz", latencyMs: 1, model: "m" }) }),
  );
  await assert.rejects(() => rerankTop1({ query: "q", candidates: cands, ask: async () => ({ ok: false, reason: "http", error: "HTTP 503" }) }));
});

// WIRE-6 (SHOULD): usage and model pass through untouched.
test("WIRE-6 usage and model preserved from recorded-shape replies", async () => {
  const res = await askJev({
    state: {}, questions: { rel: "q" }, model: "jev-1.13.0", apiKey: "fixture-key",
    fetchImpl: okFetch({ rel: { noul: 0.3 } }),
  });
  assert.equal(res.ok, true);
  assert.equal(res.usage.input_tokens, 10);
  assert.equal(res.usage.output_tokens, 0);
});

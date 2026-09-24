import test from "node:test";
import assert from "node:assert/strict";
import ompJevHeat, { CHOICE } from "../src/index.ts";

const jsonResponse = (body) => new Response(body, {
  status: 200,
  headers: { "content-type": "application/json" },
});

function host() {
  const rows = [];
  let handler;
  let eventName;
  return {
    rows,
    fire: (event) => handler(event),
    pi: {
      on: (e, cb) => {
        eventName = e;
        handler = cb;
      },
      appendEntry: async (type, data) => {
        rows.push({ type, data });
      },
    },
    eventName: () => eventName,
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith("decision.v1"));
const userTurn = (text) => ({
  type: "context",
  messages: [{ role: "user", content: text }],
});
const CHOICE_200 = {
  answers: {
    choice: {
      type: "choice",
      choice: "yak",
      confidence: 0.7,
      probabilities: {
        golden_path: 0.05,
        supporting: 0.1,
        yak: 0.7,
        hygiene: 0.1,
        none: 0.05,
      },
    },
  },
};

test("empty context emits no decision row", async () => {
  const h = host();
  ompJevHeat(h.pi);
  assert.equal(h.eventName(), "context");
  for (const event of [
    {},
    null,
    { prompt: "   " },
    { type: "turn_start", turnIndex: 0, timestamp: 123 },
    { type: "context", messages: [] },
    { type: "context", messages: [{ role: "assistant", content: "hi" }] },
    { type: "context", messages: [{ role: "user", content: "   " }] },
  ]) {
    assert.equal(await h.fire(event), undefined);
  }
  assert.equal(h.rows.length, 0);
});

test("an unset API key records heat_error, never a scored pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevHeat(h.pi);
    await h.fire(userTurn("Refactor the auth boundary."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heat_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records heat_error and never breaks the session", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevHeat(h.pi);
    assert.equal(await h.fire(userTurn("Refactor the auth boundary.")), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heat_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real choice is recorded as heat_scored with all five labels", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify(CHOICE_200));
  try {
    const h = host();
    ompJevHeat(h.pi);
    await h.fire(userTurn("Rewrite this as a general-purpose actor framework."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heat_scored");
    assert.equal(row.data.choice, "yak");
    assert.equal(row.data.confidence, 0.7);
    assert.deepEqual(row.data.probabilities, CHOICE_200.answers.choice.probabilities);
    assert.deepEqual(Object.keys(row.data.probabilities), [
      "golden_path",
      "supporting",
      "yak",
      "hygiene",
      "none",
    ]);
    assert.equal("error" in row.data, false);
    assert.equal(row.data.model, "jev-1.13.0");
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a 200 with no probabilities is an error, not a silent pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify({ unexpected: true }));
  try {
    const h = host();
    ompJevHeat(h.pi);
    await h.fire(userTurn("Refactor the auth boundary."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heat_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a host whose appendEntry throws still returns undefined", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevHeat({
      on: h.pi.on,
      appendEntry: async () => {
        throw new Error("log sink down");
      },
    });
    assert.equal(await h.fire({ type: "context", messages: [] }), undefined);
    assert.equal(await h.fire(userTurn("Refactor the auth boundary.")), undefined);
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("asks exactly the measured choice and no more", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  let sent;
  globalThis.fetch = async (_url, init) => {
    sent = JSON.parse(init.body);
    return jsonResponse(JSON.stringify(CHOICE_200));
  };
  try {
    const h = host();
    ompJevHeat(h.pi);
    await h.fire(userTurn("Refactor the auth boundary."));
    assert.deepEqual(Object.keys(CHOICE.classes), [
      "golden_path",
      "supporting",
      "yak",
      "hygiene",
      "none",
    ]);
    assert.equal(sent.questions.choice.type, "choice");
    assert.equal(sent.questions.choice.instructions, CHOICE.instructions);
    assert.deepEqual(Object.keys(sent.questions.choice.criteria), Object.keys(CHOICE.classes));
    assert.equal(sent.state.brief, process.env.TASTE_BRIEF || "(none provided)");
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

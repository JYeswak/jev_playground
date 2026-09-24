import test from "node:test";
import assert from "node:assert/strict";
import ompJevFirstlook, { CHOICE } from "../src/index.ts";

const jsonResponse = (body) => new Response(body, {
  status: 200,
  headers: { "content-type": "application/json" },
});

function host() {
  const rows = [];
  const handlers = {};
  return {
    rows,
    fire: (name, event) => handlers[name](event),
    pi: {
      on: (e, cb) => {
        handlers[e] = cb;
      },
      appendEntry: async (type, data) => {
        rows.push({ type, data });
      },
    },
  };
}

const decisions = (h) => h.rows.filter((r) => r.type.endsWith("decision.v1"));
const write = (path, content) => ({
  toolName: "write",
  toolCallId: "tc-1",
  input: { path, content },
});

const CHOICE_200 = {
  answers: {
    choice: {
      type: "choice",
      choice: "got_it",
      confidence: 0.8,
      probabilities: { lost: 0.05, hunting: 0.15, got_it: 0.8 },
    },
  },
};

/** Module-level buffer: drain leftovers so tests do not leak into each other. */
async function drain() {
  const h = host();
  ompJevFirstlook(h.pi);
  await h.fire("session_stop", {});
}

test("ignores non-first-look writes and writes no row on session_stop", async () => {
  await drain();
  const h = host();
  ompJevFirstlook(h.pi);
  assert.equal(await h.fire("tool_call", { toolName: "bash", input: { command: "ls" } }), undefined);
  assert.equal(await h.fire("tool_call", write("src/lib/hash.ts", "export const x = 1")), undefined);
  assert.equal(await h.fire("tool_call", write("src/components/Hero.tsx", "<h1>Payroll</h1>")), undefined);
  assert.equal(await h.fire("session_stop", {}), undefined);
  assert.equal(decisions(h).length, 0);
  assert.equal(h.rows.length, 0);
});

test("session_stop with empty buffer writes 0 rows", async () => {
  await drain();
  const h = host();
  ompJevFirstlook(h.pi);
  assert.equal(await h.fire("session_stop", {}), undefined);
  assert.equal(h.rows.length, 0);
});

test("first-look write then session_stop with an unset key records firstlook_error, never a scored pass", async () => {
  await drain();
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevFirstlook(h.pi);
    await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire("session_stop", {});
    const [row] = decisions(h);
    assert.equal(row.data.kind, "firstlook_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records firstlook_error and never breaks the session", async () => {
  await drain();
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevFirstlook(h.pi);
    await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>"));
    assert.equal(await h.fire("session_stop", {}), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "firstlook_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real choice is recorded as firstlook_scored with choice, confidence, probabilities", async () => {
  await drain();
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify(CHOICE_200));
  try {
    const h = host();
    ompJevFirstlook(h.pi);
    await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire("session_stop", {});
    const [row] = decisions(h);
    assert.equal(row.data.kind, "firstlook_scored");
    assert.equal(row.data.choice, "got_it");
    assert.equal(row.data.confidence, 0.8);
    assert.deepEqual(row.data.probabilities, { lost: 0.05, hunting: 0.15, got_it: 0.8 });
    assert.equal("error" in row.data, false);
    assert.equal(row.data.model, "jev-1.13.0");
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a 200 with no answers is an error, not a silent pass", async () => {
  await drain();
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify({ unexpected: true }));
  try {
    const h = host();
    ompJevFirstlook(h.pi);
    await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire("session_stop", {});
    const [row] = decisions(h);
    assert.equal(row.data.kind, "firstlook_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a host whose appendEntry throws still returns undefined", async () => {
  await drain();
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevFirstlook({
      on: h.pi.on,
      appendEntry: async () => {
        throw new Error("log sink down");
      },
    });
    assert.equal(await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>")), undefined);
    assert.equal(await h.fire("session_stop", {}), undefined);
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("asks exactly the measured choice and no more", async () => {
  await drain();
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
    ompJevFirstlook(h.pi);
    await h.fire("tool_call", write("src/app/page.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire("session_stop", {});
    assert.deepEqual(Object.keys(sent.questions), ["choice"]);
    assert.equal(sent.questions.choice.type, "choice");
    assert.equal(sent.questions.choice.instructions, CHOICE.instructions);
    assert.deepEqual(Object.keys(sent.questions.choice.criteria).sort(), ["got_it", "hunting", "lost"]);
    assert.deepEqual(sent.questions.choice.criteria, CHOICE.classes);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

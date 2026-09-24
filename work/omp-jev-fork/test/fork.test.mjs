import test from "node:test";
import assert from "node:assert/strict";
import ompJevFork, { CHOICE } from "../src/index.ts";

const jsonResponse = (body) => new Response(body, {
  status: 200,
  headers: { "content-type": "application/json" },
});

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: {
      on: (_e, cb) => {
        handler = cb;
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
      choice: "B",
      confidence: 0.8,
      probabilities: { A: 0.1, B: 0.8, none: 0.1 },
    },
  },
};

test("first write records 0 decisions; non-user-facing writes are ignored", async () => {
  const h = host();
  ompJevFork(h.pi);
  assert.equal(await h.fire({ toolName: "bash", input: { command: "ls" } }), undefined);
  assert.equal(await h.fire(write("src/lib/hash.ts", "export const x = 1")), undefined);
  assert.equal(await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>")), undefined);
  assert.equal(decisions(h).length, 0);
  assert.equal(h.rows.length, 0);
});

test("second different write with an unset key records fork_error, never a scored pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "fork_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("second write of the same content does not call Jev and still has 0 scored rows", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  let called = 0;
  globalThis.fetch = async () => {
    called += 1;
    return jsonResponse(JSON.stringify(CHOICE_200));
  };
  try {
    const h = host();
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    assert.equal(called, 0);
    assert.equal(decisions(h).filter((r) => r.data.kind === "fork_scored").length, 0);
    assert.equal(h.rows.length, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records fork_error and never breaks the session", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    assert.equal(await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>")), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "fork_error");
    assert.equal("probabilities" in row.data, false);
    assert.equal("choice" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real choice is recorded as fork_scored with choice, confidence, probabilities", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify(CHOICE_200));
  try {
    const h = host();
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "fork_scored");
    assert.equal(row.data.choice, "B");
    assert.equal(row.data.confidence, 0.8);
    assert.deepEqual(row.data.probabilities, { A: 0.1, B: 0.8, none: 0.1 });
    assert.equal("error" in row.data, false);
    assert.equal(row.data.model, "jev-1.13.0");
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a 200 with no answers is an error, not a silent pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify({ unexpected: true }));
  try {
    const h = host();
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "fork_error");
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
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevFork({
      on: h.pi.on,
      appendEntry: async () => {
        throw new Error("log sink down");
      },
    });
    assert.equal(await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>")), undefined);
    assert.equal(await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>")), undefined);
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("asks exactly A, B, none on the wire and no more", async () => {
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
    ompJevFork(h.pi);
    await h.fire(write("src/components/Hero.tsx", "<h1>Payroll in 5 minutes</h1>"));
    await h.fire(write("src/components/Hero.tsx", "<h1>Run payroll. Get paid.</h1>"));
    assert.deepEqual(Object.keys(sent.questions), ["choice"]);
    assert.equal(sent.questions.choice.type, "choice");
    assert.equal(sent.questions.choice.instructions, CHOICE.instructions);
    assert.deepEqual(Object.keys(sent.questions.choice.criteria), ["A", "B", "none"]);
    assert.deepEqual(sent.questions.choice.criteria, CHOICE.classes);
    assert.equal(sent.state.A, "<h1>Payroll in 5 minutes</h1>");
    assert.equal(sent.state.B, "<h1>Run payroll. Get paid.</h1>");
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

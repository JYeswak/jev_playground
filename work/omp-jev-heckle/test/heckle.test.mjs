import test from "node:test";
import assert from "node:assert/strict";
import ompJevHeckle, { QUESTIONS } from "../src/index.ts";

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

test("ignores bash and non-user-facing writes", async () => {
  const h = host();
  ompJevHeckle(h.pi);
  assert.equal(await h.fire({ toolName: "bash", input: { command: "ls" } }), undefined);
  assert.equal(await h.fire(write("src/lib/hash.ts", "export const x = 1")), undefined);
  assert.equal(h.rows.length, 0);
});

test("planted dead string records heckle_regex and does not call Jev", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  let called = 0;
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => {
    called += 1;
    return jsonResponse("{}");
  };
  try {
    const h = host();
    ompJevHeckle(h.pi);
    assert.equal(await h.fire(write("src/app/page.tsx", "An error occurred.")), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heckle_regex");
    assert.equal(row.data.copyClass, "error");
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("an unset API key records heckle_error, never a scored pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevHeckle(h.pi);
    await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heckle_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records heckle_error and never breaks the session", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevHeckle(h.pi);
    assert.equal(await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?")), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heckle_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real score is recorded as heckle_scored with its probabilities", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => jsonResponse(JSON.stringify({ answers: { next_action: { noul: 0.81 } } }));
  try {
    const h = host();
    ompJevHeckle(h.pi);
    await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heckle_scored");
    assert.deepEqual(row.data.probabilities, { next_action: 0.81 });
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
    ompJevHeckle(h.pi);
    await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?"));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "heckle_error");
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a host whose appendEntry throws still returns undefined", async () => {
  const h = host();
  ompJevHeckle({
    on: h.pi.on,
    appendEntry: async () => {
      throw new Error("log sink down");
    },
  });
  assert.equal(await h.fire(write("src/app/page.tsx", "An error occurred.")), undefined);
  assert.equal(await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?")), undefined);
});

test("asks exactly the measured question and no more", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  let sent;
  globalThis.fetch = async (_url, init) => {
    sent = JSON.parse(init.body);
    return jsonResponse(JSON.stringify({ answers: { next_action: { noul: 0.5 } } }));
  };
  try {
    const h = host();
    ompJevHeckle(h.pi);
    await h.fire(write("src/app/page.tsx", "Couldn't save payroll. Retry?"));
    assert.deepEqual(Object.keys(sent.questions).sort(), ["next_action"]);
    assert.equal(sent.questions.next_action.type, "noul");
    assert.equal(sent.questions.next_action.instructions, QUESTIONS.next_action);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

import test from "node:test";
import assert from "node:assert/strict";
import ompJevJargon, { QUESTIONS } from "../src/index.ts";

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
  ompJevJargon(h.pi);
  assert.equal(await h.fire({ toolName: "bash", input: { command: "ls" } }), undefined);
  assert.equal(await h.fire(write("src/lib/hash.ts", "hydrate the payload")), undefined);
  assert.equal(h.rows.length, 0);
});

test("copy without stoptokens records 0 rows", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  let called = 0;
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => {
    called += 1;
    return { ok: true, status: 200, text: async () => "{}" };
  };
  try {
    const h = host();
    ompJevJargon(h.pi);
    assert.equal(
      await h.fire(write("src/app/page.tsx", "<h1>Export payroll</h1><button>Get started</button>")),
      undefined,
    );
    assert.equal(h.rows.length, 0);
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("an unset API key records jargon_error, never a scored pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevJargon(h.pi);
    await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "jargon_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
    assert.deepEqual(row.data.suspects, ["payload", "hydrate"]);
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records jargon_error and never breaks the session", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevJargon(h.pi);
    assert.equal(
      await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save.")),
      undefined,
    );
    const [row] = decisions(h);
    assert.equal(row.data.kind, "jargon_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real score is recorded as jargon_scored with its probabilities", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    text: async () => JSON.stringify({ answers: { client_word: { noul: 0.81 } } }),
  });
  try {
    const h = host();
    ompJevJargon(h.pi);
    await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "jargon_scored");
    assert.deepEqual(row.data.probabilities, { client_word: 0.81 });
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
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    text: async () => JSON.stringify({ unexpected: true }),
  });
  try {
    const h = host();
    ompJevJargon(h.pi);
    await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save."));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "jargon_error");
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a host whose appendEntry throws still returns undefined", async () => {
  const h = host();
  ompJevJargon({
    on: h.pi.on,
    appendEntry: async () => {
      throw new Error("log sink down");
    },
  });
  assert.equal(
    await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save.")),
    undefined,
  );
});

test("asks exactly the measured question and no more", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  let sent;
  globalThis.fetch = async (_url, init) => {
    sent = JSON.parse(init.body);
    return {
      ok: true,
      status: 200,
      text: async () => JSON.stringify({ answers: { client_word: { noul: 0.5 } } }),
    };
  };
  try {
    const h = host();
    ompJevJargon(h.pi);
    await h.fire(write("src/app/page.tsx", "We hydrate the payload after you save."));
    assert.deepEqual(Object.keys(sent.questions).sort(), ["client_word"]);
    assert.equal(sent.questions.client_word.type, "noul");
    assert.equal(sent.questions.client_word.instructions, QUESTIONS.client_word);
    assert.deepEqual(sent.state.suspects, ["payload", "hydrate"]);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

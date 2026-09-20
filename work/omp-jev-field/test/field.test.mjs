import test from "node:test";
import assert from "node:assert/strict";
import ompJevField, { QUESTIONS } from "../src/index.ts";

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
const FORM = `<label>Email</label>\n<input name="email" placeholder="Email" />\n<span>Invalid input.</span>`;

test("ignores bash, non-user-facing writes, and non-form paragraphs", async () => {
  const h = host();
  ompJevField(h.pi);
  assert.equal(await h.fire({ toolName: "bash", input: { command: "ls" } }), undefined);
  assert.equal(await h.fire(write("src/lib/hash.ts", "export const x = 1")), undefined);
  assert.equal(await h.fire(write("src/app/page.tsx", "The quarterly report is ready for review.")), undefined);
  assert.equal(h.rows.length, 0);
});

test("an unset API key records field_error, never a scored pass", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevField(h.pi);
    await h.fire(write("src/app/page.tsx", FORM));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "field_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, "unconfigured");
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a throwing transport records field_error and never breaks the session", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => {
    throw new Error("connection reset");
  };
  try {
    const h = host();
    ompJevField(h.pi);
    assert.equal(await h.fire(write("src/app/page.tsx", FORM)), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, "field_error");
    assert.equal("probabilities" in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a real score is recorded as field_scored with its probabilities", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    text: async () =>
      JSON.stringify({
        answers: {
          user_language: { noul: 0.81 },
          placeholder_dup: { noul: 0.22 },
          recoverable: { noul: 0.67 },
        },
      }),
  });
  try {
    const h = host();
    ompJevField(h.pi);
    await h.fire(write("src/app/page.tsx", FORM));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "field_scored");
    assert.deepEqual(row.data.probabilities, {
      user_language: 0.81,
      placeholder_dup: 0.22,
      recoverable: 0.67,
    });
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
    ompJevField(h.pi);
    await h.fire(write("src/app/page.tsx", FORM));
    const [row] = decisions(h);
    assert.equal(row.data.kind, "field_error");
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test("a host whose appendEntry throws still returns undefined", async () => {
  const h = host();
  ompJevField({
    on: h.pi.on,
    appendEntry: async () => {
      throw new Error("log sink down");
    },
  });
  assert.equal(await h.fire(write("src/app/page.tsx", FORM)), undefined);
});

test("asks exactly the measured questions and no more", async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = "test-key";
  let sent;
  globalThis.fetch = async (_url, init) => {
    sent = JSON.parse(init.body);
    return {
      ok: true,
      status: 200,
      text: async () =>
        JSON.stringify({
          answers: {
            user_language: { noul: 0.5 },
            placeholder_dup: { noul: 0.5 },
            recoverable: { noul: 0.5 },
          },
        }),
    };
  };
  try {
    const h = host();
    ompJevField(h.pi);
    await h.fire(write("src/app/page.tsx", FORM));
    assert.deepEqual(Object.keys(sent.questions).sort(), [
      "placeholder_dup",
      "recoverable",
      "user_language",
    ]);
    assert.equal(sent.questions.user_language.type, "noul");
    assert.equal(sent.questions.user_language.instructions, QUESTIONS.user_language);
    assert.equal(sent.questions.placeholder_dup.instructions, QUESTIONS.placeholder_dup);
    assert.equal(sent.questions.recoverable.instructions, QUESTIONS.recoverable);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

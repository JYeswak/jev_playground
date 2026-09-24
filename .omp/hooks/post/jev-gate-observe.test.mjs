import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import {
  MAX_PREFIX, ROW_KEYS, buildRow, defaultFilter, observe,
} from "./jev-gate-observe.ts";
const wrote = [];
const memAppend = async (path, line) => { wrote.push({ path, row: JSON.parse(line) }); };
const reset = () => { wrote.length = 0; };
const now = () => "2026-09-24T00:00:00.000Z";
const scoredAsker = async () => ({
  ok: true, scores: { exfiltration: 0.1, destructive: 0.9, privilege: 0.2, irreversible_publish: 0.1, secret_staging: 0.05 },
  latencyMs: 410, usage: { input_tokens: 300, output_tokens: 40 },
});

test("row shape keys are frozen", async () => {
  reset();
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker: scoredAsker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.deepEqual(Object.keys(wrote[0].row).sort(), [...ROW_KEYS].sort());
  assert.equal(wrote[0].row.flag, true);
  assert.equal(wrote[0].row.status, "scored");
});

test("flag is false below the cut", async () => {
  reset();
  const asker = async () => ({ ok: true, scores: { a: 0.1, b: 0.2 }, latencyMs: 5 });
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.equal(wrote[0].row.flag, false);
});

test("secret command is skipped and the asker never runs", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: "export K=sk-abcdefghij1234567890" } },
    { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.equal(called, 0);
  assert.equal(wrote[0].row.status, "skipped");
  assert.equal(wrote[0].row.skipped, "secret");
  assert.equal(wrote[0].row.probs, null);
  assert.match(wrote[0].row.cmd, /\[REDACTED\]/);
});

test("asker receives the landed true/false criteria", async () => {
  reset();
  let seen;
  const asker = async (opts) => { seen = opts.questions; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.equal(typeof seen.secret_staging.criteria.true, "string");
  assert.equal(typeof seen.secret_staging.criteria.false, "string");
  assert.equal(seen.secret_staging.type, "noul");
});


test("no key writes NOT_RUN and never throws", async () => {
  reset();
  const asker = async () => ({ ok: false, reason: "unconfigured", error: "no key", latencyMs: 0 });
  const out = await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.equal(out, undefined);
  assert.equal(wrote[0].row.status, "not-run");
  assert.match(wrote[0].row.error, /NOT_RUN reason=unconfigured/);
});

test("throwing asker and throwing fs still resolve undefined", async () => {
  const asker = async () => { throw new Error("boom"); };
  const append = async () => { throw new Error("disk gone"); };
  const out = await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, append, logPath: "/tmp/x.jsonl", now });
  assert.equal(out, undefined);
});
test("secret patterns match real-sample.py, the owning file", () => {
  const src = execFileSync("python3", ["-c",
    "import re;"
    + "src=open('work/bicameral-gate/real-sample.py').read();"
    + "m=re.search(r'PRIVATE = re\\.compile\\(\\s*r\"(.*?)\"\\s*r\"(.*?)\"', src, re.S);"
    + "print(m.group(1)+m.group(2));"
    + "m=re.search(r'SECRET = re\\.compile\\(\\s*r\"(.*?)\"(?:\\s*r\"(.*?)\")?', src, re.S);"
    + "print(m.group(1)+(m.group(2) or ''));",
  ], { cwd: "/Users/josh/Developer/jev" }).toString().trim().split("\n");
  const privateRe = new RegExp(src[0], "i");
  const secretRe = new RegExp(src[1]);
  const fixtures = ["deploy clutter app", "sk-abcdefghij1234567890", "ls -la", "git status"];
  for (const text of fixtures) {
    const mine = defaultFilter(text).drop;
    const theirs = privateRe.test(text) || secretRe.test(text);
    assert.equal(mine, theirs, `parity on ${JSON.stringify(text)}`);
  }
});

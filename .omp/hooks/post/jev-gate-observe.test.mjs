import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import {
  MAX_PREFIX, REAL_SAMPLE, ROW_KEYS, buildRow, defaultFilter, loadFilters, makeFilter, makeHandler, observe, redact,
} from "./jev-gate-observe.ts";
const wrote = [];
const memAppend = async (path, line) => { wrote.push({ path, row: JSON.parse(line) }); };
const reset = () => { wrote.length = 0; };
const now = () => "2026-09-24T00:00:00.000Z";
// Secret-shaped fixtures are built at runtime so this file never carries one.
const fakeKey = "sk-" + "abcdefghij".repeat(3);
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

test("flag is false below the cut and at exactly the cut", async () => {
  for (const top of [0.2, 0.5]) {
    reset();
    const asker = async () => ({ ok: true, scores: { a: 0.1, b: top }, latencyMs: 5 });
    await observe({ toolName: "bash", input: { command: "ls" } },
      { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
    assert.equal(wrote[0].row.flag, false, `max=${top} must not flag: the measured runners use risk > CUT`);
  }
});

test("secret command is skipped and the asker never runs", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: `export K=${fakeKey}` } },
    { asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  assert.equal(called, 0);
  assert.equal(wrote[0].row.status, "skipped");
  assert.equal(wrote[0].row.skipped, "secret");
  assert.equal(wrote[0].row.probs, null);
  assert.match(wrote[0].row.cmd, /\[REDACTED\]/);
});

test("a key straddling the 200-char cut is scrubbed, not logged as a stub", () => {
  const command = "x".repeat(MAX_PREFIX - 10) + " " + fakeKey;
  const logged = redact(command);
  assert.ok(logged.length <= MAX_PREFIX);
  assert.doesNotMatch(logged, /sk-[a-z]/, `partial key leaked: ${logged.slice(-15)}`);
  assert.equal(buildRow({ session: "s", command, now }).cmd, logged);
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

test("handler returns undefined before any work starts, then logs the ctx session id", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  const handler = makeHandler({ asker, append: memAppend, logPath: "/tmp/x.jsonl", now });
  const ctx = { sessionManager: { getSessionId: () => "sess-123" } };
  const out = handler({ toolName: "bash", input: { command: "ls" } }, ctx);
  assert.equal(out, undefined, "a returned promise would put Jev on omp's awaited tool path");
  assert.equal(called, 0, "the asker ran inside the handler's synchronous slice");
  assert.equal(handler({ toolName: "read", input: { path: "x" } }, ctx), undefined);
  assert.equal(handler(null, { sessionManager: { getSessionId: () => { throw new Error("x"); } } }), undefined);
  await new Promise((r) => setTimeout(r, 20));
  assert.equal(called, 1, "non-bash tools are not observed");
  assert.equal(wrote.length, 1);
  assert.equal(wrote[0].row.session, "sess-123");
});

// The owner of the filters is real-sample.py. Python's own parser (ast, no execution) is the
// oracle for what the patterns are; the hook must compile exactly those, not a copy.
const pyPatterns = JSON.parse(execFileSync("python3", ["-c",
  "import ast,json,sys;t=ast.parse(open(sys.argv[1]).read());"
  + "print(json.dumps({n.targets[0].id:{'src':ast.literal_eval(n.value.args[0]),'flags':[ast.unparse(a) for a in n.value.args[1:]]}"
  + " for n in t.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','') in ('PRIVATE','SECRET')}))",
  REAL_SAMPLE]).toString());

test("filters are compiled from real-sample.py, the owning file", () => {
  const f = loadFilters(readFileSync(REAL_SAMPLE, "utf8"));
  assert.equal(f.privateRe.source, pyPatterns.PRIVATE.src);
  assert.equal(f.privateRe.ignoreCase, pyPatterns.PRIVATE.flags.includes("re.I"));
  assert.equal(f.secretRe.source, pyPatterns.SECRET.src);
  for (const word of pyPatterns.PRIVATE.src.split("|")) {
    assert.equal(defaultFilter(`cd ~/Developer/${word.toUpperCase()}`).drop, true, `private term ${word}`);
  }
  const shapes = [fakeKey, "xai-" + "a".repeat(24), "ghp_" + "a".repeat(32), "AKIA" + "A".repeat(16),
    "Bearer " + "a".repeat(24), "-----BEGIN RSA PRIVATE KEY"];
  for (const s of shapes) assert.equal(defaultFilter(`echo ${s}`).drop, true, `secret shape ${s.slice(0, 5)}`);
  for (const ok of ["ls -la", "git status", "git push --dry-run origin main"]) {
    assert.equal(defaultFilter(ok).drop, false, ok);
  }
});

test("a drifted or unreadable owner changes behaviour and fails toward skip", () => {
  const src = readFileSync(REAL_SAMPLE, "utf8");
  const drifted = loadFilters(src.replace("|alps|", "|"));
  assert.equal(makeFilter(drifted)("cd alps").drop, false, "the filter must follow the file, not a copy");
  assert.throws(() => loadFilters("PRIVATE = 1\n"));
  assert.deepEqual(makeFilter(null)("ls"), { drop: true, reason: "filter-error" });
  assert.equal(redact(`echo ${fakeKey}`, "/home/x", null), "[filter-unavailable]");
});

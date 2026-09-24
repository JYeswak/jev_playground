import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";
import {
  MAX_PREFIX, REAL_SAMPLE, ROW_KEYS, SIDECAR_KEYS, buildRow, defaultFilter, defaultSidecarAppend, loadFilters,
  makeFilter, makeHandler, observe, redact, resetKeyCache,
} from "./jev-gate-observe.ts";
const wrote = [];
const full = [];
const memAppend = async (path, line) => { wrote.push({ path, row: JSON.parse(line) }); };
const memSidecar = async (path, line) => { full.push({ path, row: JSON.parse(line) }); };
const reset = () => { wrote.length = 0; full.length = 0; };
const now = () => "2026-09-24T00:00:00.000Z";
// Every observe() below routes both writers to memory: a test must never append to the real sidecar.
const mem = { append: memAppend, logPath: "/tmp/x.jsonl", appendSidecar: memSidecar, sidecarPath: "/tmp/x-full.jsonl", now };
// Secret-shaped fixtures are built at runtime so this file never carries one.
const fakeKey = "sk-" + "abcdefghij".repeat(3);
const scoredAsker = async () => ({
  ok: true, scores: { exfiltration: 0.1, destructive: 0.9, privilege: 0.2, irreversible_publish: 0.1, secret_staging: 0.05 },
  latencyMs: 410, usage: { input_tokens: 300, output_tokens: 40 },
});

test("row shape keys are frozen", async () => {
  reset();
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker: scoredAsker, ...mem });
  assert.deepEqual(Object.keys(wrote[0].row).sort(), [...ROW_KEYS].sort());
  assert.equal(wrote[0].row.flag, true);
  assert.equal(wrote[0].row.status, "scored");
});

test("flag is false below the cut and at exactly the cut", async () => {
  for (const top of [0.2, 0.5]) {
    reset();
    const asker = async () => ({ ok: true, scores: { a: 0.1, b: top }, latencyMs: 5 });
    await observe({ toolName: "bash", input: { command: "ls" } },
      { asker, ...mem });
    assert.equal(wrote[0].row.flag, false, `max=${top} must not flag: the measured runners use risk > CUT`);
  }
});

test("secret command is skipped and the asker never runs", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: `export K=${fakeKey}` } },
    { asker, ...mem });
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
    { asker, ...mem });
  assert.equal(typeof seen.secret_staging.criteria.true, "string");
  assert.equal(typeof seen.secret_staging.criteria.false, "string");
  assert.equal(seen.secret_staging.type, "noul");
});

test("no key writes NOT_RUN and never throws", async () => {
  reset();
  const asker = async () => ({ ok: false, reason: "unconfigured", error: "no key", latencyMs: 0 });
  const out = await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, ...mem });
  assert.equal(out, undefined);
  assert.equal(wrote[0].row.status, "not-run");
  assert.match(wrote[0].row.error, /NOT_RUN reason=unconfigured/);
});

test("throwing asker and throwing fs still resolve undefined", async () => {
  const asker = async () => { throw new Error("boom"); };
  const append = async () => { throw new Error("disk gone"); };
  const out = await observe({ toolName: "bash", input: { command: "ls" } },
    { asker, append, appendSidecar: append, logPath: "/tmp/x.jsonl", sidecarPath: "/tmp/x-full.jsonl", now });
  assert.equal(out, undefined);
});

test("handler returns undefined before any work starts, then logs the ctx session id", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  const handler = makeHandler({ asker, ...mem });
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

test("secret-shaped and filter-error commands write no sidecar row", async () => {
  reset();
  await observe({ toolName: "bash", input: { command: `curl -H "Authorization: Bearer ${"a".repeat(24)}" x` } },
    { asker: scoredAsker, ...mem });
  await observe({ toolName: "bash", input: { command: `export K=${fakeKey}` } }, { asker: scoredAsker, ...mem });
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker: scoredAsker, filter: makeFilter(null), ...mem });
  assert.deepEqual(wrote.map((w) => w.row.skipped), ["secret", "secret", "filter-error"]);
  assert.equal(full.length, 0, "a dropped command reached the full-command sidecar");
});

test("sidecar text equals the scored command, joins by cmdSha, and leaves the prefix row unchanged", async () => {
  reset();
  const command = `cd ${homedir()}/Developer/jev && ` + "echo long-body ".repeat(30) + "| hub send --to pane1";
  let scored;
  const asker = async (args) => { scored = args.state.command; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command } }, { asker, ...mem, session: "s1" });
  assert.equal(full.length, 1);
  const side = full[0].row;
  assert.deepEqual(Object.keys(side).sort(), [...SIDECAR_KEYS].sort());
  assert.equal(side.cmd, scored, "sidecar must hold exactly what Jev scored");
  assert.equal(side.cmd, command);
  assert.equal(createHash("sha256").update(side.cmd).digest("hex"), side.cmdSha);
  const row = wrote[0].row;
  assert.equal(row.cmdSha, side.cmdSha);
  assert.equal(side.session, "s1");
  assert.equal(side.ts, row.ts);
  assert.deepEqual(Object.keys(row).sort(), [...ROW_KEYS].sort());
  assert.equal(row.cmd, redact(command), "the prefix log changed shape");
  assert.ok(row.cmd.length <= MAX_PREFIX && command.length > MAX_PREFIX);
  assert.equal(full[0].path, "/tmp/x-full.jsonl");
});

test("a failing sidecar write still logs the scored prefix row", async () => {
  reset();
  await observe({ toolName: "bash", input: { command: "ls" } },
    { asker: scoredAsker, ...mem, appendSidecar: async () => { throw new Error("disk gone"); } });
  assert.equal(wrote.length, 1);
  assert.equal(wrote[0].row.status, "scored");
});

test("default sidecar writer creates mode 600 and narrows a pre-existing wider file", async () => {
  // Scratch under the OS temp dir; left for the OS to reap (no deletes in this lane).
  const dir = mkdtempSync(join(tmpdir(), "jev-sidecar-"));
  const fresh = join(dir, "nested", "full.jsonl");
  await defaultSidecarAppend(fresh, '{"a":1}');
  assert.equal(statSync(fresh).mode & 0o777, 0o600);
  const wide = join(dir, "wide.jsonl");
  writeFileSync(wide, '{"old":1}\n', { mode: 0o644 });
  assert.equal(statSync(wide).mode & 0o777, 0o644);
  await defaultSidecarAppend(wide, '{"b":2}');
  assert.equal(statSync(wide).mode & 0o777, 0o600);
  assert.equal(readFileSync(wide, "utf8"), '{"old":1}\n{"b":2}\n');
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

test("env key wins over the resolver and is not written", async () => {
  reset();
  resetKeyCache();
  const planted = "sk-" + "envkeyplant".repeat(2);
  const prev = process.env.TYPESAFE_API_KEY;
  process.env.TYPESAFE_API_KEY = planted;
  let resolverCalls = 0;
  let seen;
  const asker = async (args) => { seen = args.apiKey; return scoredAsker(); };
  try {
    await observe({ toolName: "bash", input: { command: "ls" } }, {
      asker,
      keyResolver: async () => { resolverCalls++; throw new Error("must not run"); },
      ...mem,
    });
    assert.equal(resolverCalls, 0);
    assert.equal(seen, planted);
    assert.equal(process.env.TYPESAFE_API_KEY, planted);
    assert.equal(JSON.stringify(wrote).includes(planted), false);
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
    resetKeyCache();
  }
});

test("resolver runs once across tool calls and the value is not logged", async () => {
  reset();
  resetKeyCache();
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  const planted = "sk-" + "resolverplant".repeat(2);
  let calls = 0;
  const asker = async (args) => { assert.equal(args.apiKey, planted); return scoredAsker(); };
  try {
    const deps = {
      asker,
      keyResolver: async () => { calls++; return planted; },
      ...mem,
    };
    for (let i = 0; i < 3; i++) {
      await observe({ toolName: "bash", input: { command: "git status" } }, deps);
    }
    assert.equal(calls, 1);
    assert.equal(process.env.TYPESAFE_API_KEY, undefined);
    assert.equal(JSON.stringify(wrote).includes(planted), false);
    assert.equal(wrote.length, 3);
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
    resetKeyCache();
  }
});

test("resolver failure is cached, logged not-run, and does not throw", async () => {
  reset();
  resetKeyCache();
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  let calls = 0;
  try {
    const deps = {
      asker: async () => { throw new Error("asker must not run"); },
      keyResolver: async () => { calls++; throw new Error("boom"); },
      ...mem,
    };
    const a = await observe({ toolName: "bash", input: { command: "ls" } }, deps);
    const b = await observe({ toolName: "bash", input: { command: "pwd" } }, deps);
    assert.equal(a, undefined);
    assert.equal(b, undefined);
    assert.equal(calls, 1);
    assert.equal(wrote.length, 2);
    assert.equal(wrote[0].row.status, "not-run");
    assert.match(wrote[0].row.error, /NOT_RUN reason=unconfigured key-source=infisical-failed/);
    assert.equal(JSON.stringify(wrote).includes("boom"), false);
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
    resetKeyCache();
  }
});

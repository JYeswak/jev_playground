import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";
import {
  MAX_PREFIX, REAL_SAMPLE, ROW_KEYS, SIDECAR_KEYS, buildRow, defaultFilter, defaultSidecarAppend,
  loadFilters, makeFilter, makeHandler, observe as observeRaw, redact, resetBillingHold,
} from "./jev-gate-observe.ts";
import gateObserveHook from "./jev-gate-observe.ts";
import { askJevBundle, observedFetch, setKeyProvider } from "../../../kit/src/client.ts";
const wrote = [];
const full = [];
const memAppend = async (path, line) => { wrote.push({ path, row: JSON.parse(line) }); };
const memSidecar = async (path, line) => { full.push({ path, row: JSON.parse(line) }); };
const reset = () => { wrote.length = 0; full.length = 0; };
async function waitFor(condition, description = "the asynchronous hook write", timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (!condition()) {
    if (Date.now() >= deadline) throw new Error("Timed out waiting for " + description);
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
}
const now = () => "2026-09-24T00:00:00.000Z";
// Every observe() below routes both writers to memory: a test must never append to the real sidecar.
const mem = { append: memAppend, logPath: "/tmp/x.jsonl", appendSidecar: memSidecar, sidecarPath: "/tmp/x-full.jsonl", now, session: "offline-session" };
// Secret-shaped fixtures are built at runtime so this file never carries one.
const fakeKey = "sk-" + "abcdefghij".repeat(3);
// Captured bash result, byte-identical to work/omp-guard-rule/fixtures/session-pinned.jsonl
// line 2 (real:true row, jev-lab 2026-09-20 live-fire proof). Inlined so the suite passes in any
// checkout without assuming that file is tracked; the file remains the provenance record.
const RECORDED_BASH = {
  event: "tool_call", toolName: "bash", toolCallId: "[ID]", input: { command: "git status --porcelain=v1" },
  real: true, note: "clean pass shape",
};
const scoredAsker = async () => ({
  ok: true, scores: { exfiltration: 0.1, destructive: 0.9, privilege: 0.2, irreversible_publish: 0.1, secret_staging: 0.05 },
  model: "test-model", latencyMs: 410, usage: { input_tokens: 300, output_tokens: 40 },
});

const observe = (event, deps = {}) => observeRaw(event, { ...mem, ...deps });

test("scored row records resolved model, risk flag, usage, and latency", async () => {
  reset();
  await observe({ toolName: "bash", input: { command: "ls" } }, { asker: scoredAsker });
  assert.deepEqual(Object.keys(wrote[0].row).sort(), [...ROW_KEYS].sort());
  assert.equal(wrote[0].row.flag, true);
  assert.equal(wrote[0].row.status, "scored");
  assert.equal(wrote[0].row.model, "test-model");
  assert.deepEqual(wrote[0].row.tokens, { input_tokens: 300, output_tokens: 40 });
  assert.equal(wrote[0].row.latencyMs, 410);
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

test("handler schedules a bash observation without event-ID approval and returns immediately", async () => {
  reset();
  let called = 0;
  const asker = async () => { called++; return scoredAsker(); };
  const handler = makeHandler({ asker, ...mem });
  const ctx = { sessionManager: { getSessionId: () => "sess-123" } };
  const out = handler({ toolName: "bash", input: { command: "ls" } }, ctx);
  assert.equal(out, undefined, "a returned promise would put Jev on omp's awaited tool path");
  assert.equal(called, 0, "the asker ran inside the handler's synchronous slice");
  assert.equal(handler({ toolName: "read", input: { path: "x" } }, ctx), undefined);
  await waitFor(() => wrote.length === 1);
  assert.equal(called, 1, "only the real bash result is observed");
  assert.equal(wrote[0].row.session, "sess-123");
  assert.equal(wrote[0].row.status, "scored");
});

test("daily cap stops same-day calls and resets at the UTC date boundary", async () => {
  reset();
  let timestamp = "2026-09-24T23:59:00.000Z";
  let calls = 0;
  const handler = makeHandler({
    ...mem,
    asker: async () => { calls++; return scoredAsker(); },
    dailyCap: 1,
    dailyBudget: { day: "", calls: 0 },
    now: () => timestamp,
  });
  const ctx = { sessionManager: { getSessionId: () => "cap-session" } };
  for (const command of ["pwd", "date"]) {
    assert.equal(handler({ toolName: "bash", input: { command } }, ctx), undefined);
  }
  await waitFor(() => wrote.length === 2);
  assert.equal(calls, 1);
  assert.deepEqual(wrote.map(({ row }) => row.status), ["scored", "not-run"]);
  assert.equal(wrote[1].row.error, "NOT_RUN reason=daily-cap");
  timestamp = "2026-09-25T00:00:00.000Z";
  assert.equal(handler({ toolName: "bash", input: { command: "date" } }, ctx), undefined);
  await waitFor(() => wrote.length === 3);
  assert.equal(calls, 2);
  assert.equal(wrote[2].row.status, "scored");
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

test("forced-fail Infisical provider records NOT_RUN unconfigured and never reaches fetch", async () => {
  reset();
  resetBillingHold();
  const previousKey = process.env.TYPESAFE_API_KEY;
  const previousFetch = globalThis.fetch;
  let fetches = 0;
  delete process.env.TYPESAFE_API_KEY;
  setKeyProvider(async () => undefined);
  globalThis.fetch = async () => { fetches++; throw new Error("unexpected network"); };
  try {
    const out = await observe({ toolName: "bash", input: { command: "pwd" } });
    assert.equal(out, undefined);
    assert.equal(wrote.length, 1);
    assert.equal(wrote[0].row.status, "not-run");
    assert.equal(wrote[0].row.error, "NOT_RUN reason=unconfigured");
    assert.equal(fetches, 0);
  } finally {
    setKeyProvider(undefined);
    if (previousKey === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previousKey;
    globalThis.fetch = previousFetch;
    resetBillingHold();
  }
});



// jev-nhv9: 233 calls hit HTTP 402 over 4.5 h, one per bash command.
test("401, 402, and 403 hold further calls for 15 minutes, then permit again", async () => {
  resetBillingHold();
  try {
    for (const status of [401, 402, 403]) {
      reset();
      resetBillingHold();
      let clock = 1_000_000;
      let calls = 0;
      const refused = async () => {
        calls++;
        return { ok: false, reason: "http", error: "systemOne HTTP " + status + ": refused", latencyMs: 90 };
      };
      const deps = { ...mem, nowMs: () => clock };
      await observe({ toolName: "bash", input: { command: "ls" } }, { ...deps, asker: refused });
      assert.equal(calls, 1);
      assert.equal(wrote[0].row.status, "error");
      clock += 15 * 60 * 1000 - 1;
      await observe({ toolName: "bash", input: { command: "pwd" } }, { ...deps, asker: refused });
      assert.equal(calls, 1, "no call inside the hold for HTTP " + status);
      assert.equal(wrote[1].row.status, "not-run");
      assert.equal(wrote[1].row.error, "NOT_RUN reason=billing-hold until=" + new Date(1_000_000 + 15 * 60 * 1000).toISOString());
      clock += 1;
      await observe({ toolName: "bash", input: { command: "date" } }, { ...deps, asker: scoredAsker });
      assert.equal(wrote[2].row.status, "scored", "the hold ends at its pinned duration");
    }
  } finally {
    resetBillingHold();
  }
});

test("429, 503, and transport failures do not start the 401/402/403 hold", async () => {
  resetBillingHold();
  let calls = 0;
  const deps = { ...mem, nowMs: () => 5_000_000 };
  try {
    for (const answer of [
      { ok: false, reason: "http", error: "systemOne HTTP 429: rate limited", latencyMs: 1 },
      { ok: false, reason: "http", error: "systemOne HTTP 503: unavailable", latencyMs: 1 },
      { ok: false, reason: "transport", error: "socket hang up after 4020 ms", latencyMs: 1 },
    ]) {
      reset();
      await observe({ toolName: "bash", input: { command: "ls" } }, { ...deps, asker: async () => { calls++; return answer; } });
      await observe({ toolName: "bash", input: { command: "ls" } }, { ...deps, asker: async () => { calls++; return answer; } });
      assert.deepEqual(wrote.map((w) => w.row.status), ["error", "error"], answer.error);
    }
    assert.equal(calls, 6);
  } finally {
    resetBillingHold();
  }
});

test("registered post-hook scores a bash result without synthetic event-ID approval", async () => {
  reset();
  let callback;
  let requests = 0;
  gateObserveHook({ on: (name, handler) => {
    assert.equal(name, "tool_result");
    callback = handler;
  } }, {
    ...mem,
    asker: async () => { requests++; return scoredAsker(); },
  });
  const ctx = { sessionManager: { getSessionId: () => "sess-live-shape" } };
  assert.equal(callback({ toolName: "bash", input: { command: "ls -la" } }, ctx), undefined);
  assert.equal(requests, 0, "the post-hook stays outside OMP's awaited tool path");
  await waitFor(() => wrote.length === 1);
  assert.equal(requests, 1);
  assert.equal(wrote[0].row.session, "sess-live-shape");
  assert.equal(wrote[0].row.status, "scored");
  assert.equal(wrote[0].row.model, "test-model");
});


test("missing session blocks egress but a captured bash result needs no tool-call ID", async () => {
  reset();
  const recorded = { ...RECORDED_BASH, input: { ...RECORDED_BASH.input } };
  assert.equal(recorded.real, true);
  let requests = 0;
  const deps = { ...mem, asker: async () => { requests++; return scoredAsker(); } };
  await observeRaw({ ...recorded, toolCallId: undefined }, { ...deps, session: "unknown" });
  assert.equal(requests, 0);
  assert.equal(wrote[0].row.status, "not-run");
  assert.equal(wrote[0].row.error, "NOT_RUN reason=session-unavailable");
  assert.equal(full.length, 0);
  await observeRaw({ ...recorded, toolCallId: undefined }, { ...deps, session: "recorded-session" });
  assert.equal(requests, 1);
  assert.equal(wrote[1].row.status, "scored");
  assert.equal(wrote[1].row.session, "recorded-session");
});

test("captured bash result without a toolCallId reaches the offline client only after secret filtering", async () => {
  reset();
  const recorded = { ...RECORDED_BASH, input: { ...RECORDED_BASH.input } };
  assert.equal(recorded.real, true);
  const requests = [];
  let attempts = 0;
  const fetchImpl = observedFetch(
    () => { attempts++; },
    async (url, init) => {
      requests.push({ url: String(url), body: JSON.parse(String(init.body)) });
      return new Response(JSON.stringify({
        model: "jev-1.13.0",
        answers: Object.fromEntries(["exfiltration", "destructive", "privilege", "irreversible_publish", "secret_staging"].map((key) => [key, { type: "noul", noul: 0.1 }])),
        usage: { input_tokens: 20, output_tokens: 5 },
      }), { status: 200, headers: { "content-type": "application/json" } });
    },
  );
  const asker = async (options) => {
    const result = await askJevBundle({ ...options, apiKey: "offline-test-only", fetchImpl });
    if (!result.ok) return result;
    return {
      ok: true,
      model: result.resolvedModel,
      scores: Object.fromEntries(Object.entries(result.answers).map(([key, answer]) => [key, answer.noul])),
      latencyMs: result.latencyMs,
      usage: result.usage && { input_tokens: result.usage.input_tokens, output_tokens: result.usage.output_tokens },
    };
  };
  const deps = { ...mem, asker };
  await observeRaw({ ...recorded, toolCallId: undefined, input: { command: "export K=" + fakeKey } }, deps);
  assert.equal(requests.length, 0);
  assert.equal(attempts, 0);
  assert.equal(full.length, 0);
  assert.equal(wrote.at(-1).row.status, "skipped");
  await observeRaw({ ...recorded, toolCallId: undefined }, deps);
  assert.equal(requests.length, 1);
  assert.equal(attempts, 1);
  assert.equal(requests[0].url, "https://api.typesafe.ai/v1/systemone");
  assert.equal(requests[0].body.model, "jev-1.13.0");
  assert.deepEqual(requests[0].body.state, {
    command: "git status --porcelain=v1",
    context: "An AI coding agent proposes running this in the user repository.",
  });
  assert.equal(wrote.at(-1).row.status, "scored");
  assert.equal(wrote.at(-1).row.model, "jev-1.13.0");
  assert.deepEqual(wrote.at(-1).row.tokens, { input_tokens: 20, output_tokens: 5 });
  assert.equal(typeof wrote.at(-1).row.latencyMs, "number");
  assert.equal(full.length, 1);
  assert.doesNotMatch(JSON.stringify(requests), /offline-test-only|sk-abcdefghij/);
});

const cascadeMem = { ...mem, cascade: true, dailyBudget: { day: "", calls: 0 } };
const nimbleClear = async () => ({ ok: true, scores: { destructive: 0.1, exfiltration: 0.05 }, model: "nimble:latest", latencyMs: 800 });
const nimbleFlag = async () => ({ ok: true, scores: { destructive: 0.9, exfiltration: 0.1 }, model: "nimble:latest", latencyMs: 900 });

test("cascade: nimble-negative never reaches the paid asker", async () => {
  reset();
  let paid = 0;
  const asker = async () => { paid++; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: "ls" } },
    { ...cascadeMem, asker, localAsker: nimbleClear, dailyBudget: { day: "", calls: 0 } });
  assert.equal(paid, 0, "a nimble-cleared command must not spend a paid call");
  assert.equal(wrote[0].row.status, "scored");
  assert.equal(wrote[0].row.flag, false);
  assert.equal(wrote[0].row.model, "nimble:latest");
  assert.equal(wrote[0].row.jevSkipped, true);
  assert.deepEqual(wrote[0].row.nimbleProbs, { destructive: 0.1, exfiltration: 0.05 });
});

test("cascade: nimble-positive reaches the paid asker with both scores logged", async () => {
  reset();
  let paid = 0;
  const asker = async () => { paid++; return scoredAsker(); };
  await observe({ toolName: "bash", input: { command: "ls" } },
    { ...cascadeMem, asker, localAsker: nimbleFlag, dailyBudget: { day: "", calls: 0 } });
  assert.equal(paid, 1);
  assert.equal(wrote[0].row.status, "scored");
  assert.equal(wrote[0].row.jevSkipped, false);
  assert.deepEqual(wrote[0].row.nimbleProbs, { destructive: 0.9, exfiltration: 0.1 });
  assert.equal(wrote[0].row.model, "test-model");
});

test("cascade: gateway error is not-run and the paid asker never runs", async () => {
  reset();
  let paid = 0;
  const asker = async () => { paid++; return scoredAsker(); };
  const localAsker = async () => { throw new Error("gateway down"); };
  await observe({ toolName: "bash", input: { command: "ls" } },
    { ...cascadeMem, asker, localAsker, dailyBudget: { day: "", calls: 0 } });
  assert.equal(paid, 0);
  assert.equal(wrote[0].row.status, "not-run");
  assert.match(wrote[0].row.error, /NOT_RUN reason=local-screen-threw/);
});

test("cascade: nimble-cleared commands do not consume the paid budget", async () => {
  reset();
  let paid = 0;
  const asker = async () => { paid++; return scoredAsker(); };
  const budget = { day: "", calls: 0 };
  const cmd = (c) => observe({ toolName: "bash", input: { command: c } },
    { ...cascadeMem, asker, localAsker: nimbleClear, dailyBudget: budget, dailyCap: 1 });
  await cmd("ls");
  await cmd("pwd");
  assert.equal(paid, 0);
  assert.deepEqual(wrote.map((w) => w.row.status), ["scored", "scored"]);
  assert.equal(budget.calls, 0, "free screens must not burn paid budget");
});

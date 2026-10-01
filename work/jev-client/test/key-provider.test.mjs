// Key resolution for omp panes, keyless: askJev* take the key from the call, then
// TYPESAFE_API_KEY, then an installed provider; the Infisical provider caches in memory only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { askJev, askJevScore, keyProviderInstalled, setKeyProvider } from '../../../kit/src/client.ts';
import { makeInfisicalKeyProvider, PROJECT_ID, TTL_MS, FAIL_TTL_MS, infisicalBinary, machineIdentityConfig } from "../src/infisical-key.ts";
import * as keyModule from "../src/infisical-key.ts";
import { useInfisicalKey } from '../src/use-infisical-key.ts';

const fakeHeaders = () => ({ get: (name) => name.toLowerCase() === 'content-type' ? 'application/json' : null });
function answering(seen) {
  return async (_url, init) => {
    seen.push(init.headers.Authorization);
    return { ok: true, status: 200, headers: fakeHeaders(), body: null, clone() { return this; },
      text: async () => JSON.stringify({ answers: { q: { noul: 0.7 } } }) };
  };
}

async function withEnvKey(value, body) {
  const prev = process.env.TYPESAFE_API_KEY;
  if (value === undefined) delete process.env.TYPESAFE_API_KEY;
  else process.env.TYPESAFE_API_KEY = value;
  try { return await body(); }
  finally {
    setKeyProvider(undefined);
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
  }
}

test('with no key in the call or the environment, the installed provider supplies it', () => withEnvKey(undefined, async () => {
  const seen = [];
  setKeyProvider(async () => 'from-provider');
  const r = await askJev({ state: { a: 1 }, questions: { q: 'yes?' }, fetchImpl: answering(seen) });
  assert.equal(r.ok, true);
  assert.deepEqual(seen, ['Bearer from-provider']);
}));

test('the environment key wins and the provider is never asked', () => withEnvKey('from-env', async () => {
  const seen = [];
  let asked = 0;
  setKeyProvider(async () => { asked++; return 'from-provider'; });
  await askJev({ state: { a: 1 }, questions: { q: 'yes?' }, fetchImpl: answering(seen) });
  assert.deepEqual(seen, ['Bearer from-env']);
  assert.equal(asked, 0);
}));

test('a provider that finds nothing, or throws, is unconfigured and sends nothing', () => withEnvKey(undefined, async () => {
  const seen = [];
  for (const provider of [async () => undefined, async () => '', async () => { throw new Error('boom'); }]) {
    setKeyProvider(provider);
    const r = await askJevScore({ state: {}, instructions: 'x', criteria: ['a', 'b'], fetchImpl: answering(seen) });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'unconfigured');
  }
  assert.deepEqual(seen, []);
}));

test('no provider installed: unset key stays unconfigured (scripts and tests are keyless)', () => withEnvKey(undefined, async () => {
  setKeyProvider(undefined);
  const r = await askJev({ state: {}, questions: { q: 'x' }, fetchImpl: answering([]) });
  assert.equal(r.reason, 'unconfigured');
}));

test('useInfisicalKey never replaces a provider the process already pinned', () => withEnvKey(undefined, async () => {
  const pinned = async () => undefined;
  setKeyProvider(pinned);
  useInfisicalKey();
  const r = await askJev({ state: {}, questions: { q: 'x' }, fetchImpl: answering([]) });
  assert.equal(r.reason, 'unconfigured', 'the pinned no-key provider still decides');
  setKeyProvider(undefined);
  assert.equal(keyProviderInstalled(), false);
  useInfisicalKey();
  assert.equal(keyProviderInstalled(), true);
}));

test('Infisical provider: runs the models.yml command, caches for the TTL, refetches after', async () => {
  let t = 0;
  const calls = [];
  const provider = makeInfisicalKeyProvider(async (file, args) => { calls.push([file, args]); return `key${calls.length}\n`; }, () => t, '/bin/infisical');
  assert.equal(await provider(), 'key1');
  assert.deepEqual(calls[0], ['/bin/infisical', ['secrets', 'get', 'TYPESAFE_API_KEY', `--projectId=${PROJECT_ID}`, '--plain', '--silent']]);
  t = TTL_MS - 1;
  assert.equal(await provider(), 'key1');
  t = TTL_MS;
  assert.equal(await provider(), 'key2', 'a rotated key is picked up after the TTL');
  assert.equal(calls.length, 2);
});

test('Infisical provider: concurrent callers share one lookup', async () => {
  let runs = 0;
  const provider = makeInfisicalKeyProvider(async () => { runs++; await new Promise((r) => setTimeout(r, 5)); return 'k'; }, () => 0, 'x');
  assert.deepEqual(await Promise.all([provider(), provider(), provider()]), ['k', 'k', 'k']);
  assert.equal(runs, 1);
});

test('Infisical provider: a failure or junk output is no key, retried only after FAIL_TTL', async () => {
  let t = 0;
  let runs = 0;
  const outputs = [() => { throw new Error('offline'); }, () => 'two words\n', () => 'good'];
  const provider = makeInfisicalKeyProvider(async () => outputs[runs++](), () => t, "x", "/no-machine-home");
  assert.equal(await provider(), undefined);
  t = FAIL_TTL_MS - 1;
  assert.equal(await provider(), undefined);
  assert.equal(runs, 1, 'a failed lookup is not repeated on every call');
  t = FAIL_TTL_MS;
  assert.equal(await provider(), undefined, 'output with whitespace inside is not a key');
  t = 2 * FAIL_TTL_MS;
  assert.equal(await provider(), 'good');
});

test('Infisical provider never writes the key into the environment', async () => {
  const before = process.env.TYPESAFE_API_KEY;
  const provider = makeInfisicalKeyProvider(async () => 'secret-value', () => 0, 'x');
  await provider();
  assert.equal(process.env.TYPESAFE_API_KEY, before);
  assert.equal(Object.values(process.env).includes("secret-value"), false);
});

test("approved HTTPS login refuses rejected authentication without child secret lookup", async () => {
  const previousFetch = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (url) => {
    requests.push(String(url));
    return {ok: false, status: 401, url: String(url), redirected: false,
      json: async () => ({error: "rejected synthetic-machine-secret"})};
  };
  try {
    let childCalls = 0;
    const provider = makeInfisicalKeyProvider(async () => {
      childCalls++;
      throw new Error("user session expired");
    }, () => 0, "infisical", "/synthetic-home",
    () => "export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=https://approved.infisical.test",
    {origin: "https://approved.infisical.test"});
    assert.equal(await provider(), undefined);
    assert.deepEqual(requests, ["https://approved.infisical.test/api/v1/auth/universal-auth/login"]);
    assert.equal(childCalls, 1, "no second child after rejected login");
  } finally {
    globalThis.fetch = previousFetch;
  }
});

test("approved HTTPS login refuses a recorded 307 without a second recipient", async () => {
  const previousFetch = globalThis.fetch;
  const firstHops = [];
  let forwarded = 0;
  globalThis.fetch = async (url, options) => {
    firstHops.push(String(url));
    if (options.redirect === "error") throw new TypeError("redirect rejected");
    forwarded++;
    return {ok: true, redirected: true, url: "https://collector.invalid/collect",
      json: async () => ({accessToken: "fake-machine-token"})};
  };
  try {
    let childCalls = 0;
    const provider = makeInfisicalKeyProvider(async () => {
      childCalls++;
      throw new Error("user session expired");
    }, () => 0, "infisical", "/synthetic-home",
    () => "export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=https://approved.infisical.test",
    {origin: "https://approved.infisical.test"});
    assert.equal(await provider(), undefined);
    assert.deepEqual(firstHops, ["https://approved.infisical.test/api/v1/auth/universal-auth/login"]);
    assert.equal(forwarded, 0);
    assert.equal(childCalls, 1);
  } finally {
    globalThis.fetch = previousFetch;
  }
});
test("machine identity config requires all three non-empty fields", () => {
  assert.deepEqual(machineIdentityConfig("/home", () => "export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=secret\nexport INFISICAL_API_URL=https://example"), {clientId: "cid", clientSecret: "secret", apiUrl: "https://example", projectId: undefined, projectIds: undefined, environment: undefined, loaded: undefined});
  assert.equal(machineIdentityConfig("/home", () => "export INFISICAL_CLIENT_ID=cid"), undefined);
});

test('infisicalBinary prefers ~/.local/bin/infisical and falls back to PATH', () => {
  assert.equal(infisicalBinary('/h', () => true), '/h/.local/bin/infisical');
  assert.equal(infisicalBinary('/h', () => false), 'infisical');
});

test("machine fallback denies wrong or non-HTTPS first recipients before credential POST", async () => {
  const previousFetch = globalThis.fetch;
  const attempts = [];
  globalThis.fetch = async (url) => {
    attempts.push(String(url));
    return {ok: true, json: async () => ({accessToken: "fake-machine-token"})};
  };
  try {
    for (const apiUrl of [
      "http://approved.infisical.test",
      "https://collector.invalid",
      "https://user:synthetic@approved.infisical.test",
      "https://approved.infisical.test/?token=synthetic",
      "https://approved.infisical.test/#fragment",
    ]) {
      const child = [];
      const config = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=${apiUrl}`;
      const provider = makeInfisicalKeyProvider(async (_file, _args, _timeout, env) => {
        child.push(env);
        if (!env?.INFISICAL_TOKEN) throw new Error("user session expired");
        return "synthetic-key";
      }, () => 0, "infisical", "/synthetic-home", () => config, {origin: "https://approved.infisical.test"});
      assert.equal(await provider(), undefined);
      assert.equal(child.length, 1, "only the user-session lookup may execute");
    }
    assert.deepEqual(attempts, [], "no credential POST reaches an unapproved first hop");
  } finally {
    globalThis.fetch = previousFetch;
  }
});

test("machine fallback has no credential-file read without an approved origin", async () => {
  let reads = 0;
  for (const approval of [undefined, {origin: "http://approved.infisical.test"},
    {origin: "https://approved.infisical.test/api"}]) {
    const provider = makeInfisicalKeyProvider(async () => { throw new Error("user session expired"); },
      () => 0, "infisical", "/synthetic-home", () => { reads++; return "synthetic credentials"; }, approval);
    assert.equal(await provider(), undefined);
  }
  assert.equal(reads, 0);
});

test("approved HTTPS first hop uses the recorded universal-auth login shape", async () => {
  const previousFetch = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push({url: String(url), method: options.method, redirect: options.redirect,
      headers: options.headers, body: JSON.parse(options.body)});
    return {ok: true, redirected: false, url: String(url),
      json: async () => ({accessToken: "fake-machine-token"})};
  };
  try {
    const child = [];
    const provider = makeInfisicalKeyProvider(async (file, args, _timeout, env) => {
      child.push({file, args, env});
      if (!env?.INFISICAL_TOKEN) throw new Error("user session expired");
      return "synthetic-key";
    }, () => 0, "infisical", "/synthetic-home",
    () => "export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=https://approved.infisical.test/api",
    {origin: "https://approved.infisical.test"});
    assert.equal(await provider(), "synthetic-key");
    assert.deepEqual(requests, [{
      url: "https://approved.infisical.test/api/v1/auth/universal-auth/login",
      method: "POST", redirect: "error", headers: {"content-type": "application/json"},
      body: {clientId: "cid", clientSecret: "synthetic-machine-secret"},
    }]);
    assert.equal(child.length, 2);
    assert.deepEqual(child[1], {file: "infisical",
      args: ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"],
      env: {INFISICAL_API_URL: "https://approved.infisical.test", INFISICAL_TOKEN: "fake-machine-token"}});
    assert.equal(JSON.stringify(child).includes("synthetic-machine-secret"), false);
  } finally {
    globalThis.fetch = previousFetch;
  }
});

test("final execFile child receives only named environment variables, never inherited secrets", async () => {
  const sentinel = "synthetic-parent-sentinel";
  const parent = {PATH: "/bin", HOME: "/synthetic-home", TMPDIR: "/synthetic-tmp",
    INFISICAL_CLIENT_SECRET: sentinel, TYPESAFE_API_KEY: sentinel, UNRELATED: sentinel};
  const calls = [];
  const fakeExecFile = (file, args, options, callback) => {
    calls.push({file, args, env: options.env});
    callback(null, "synthetic-key\n", "");
  };
  assert.equal(typeof keyModule.makeDefaultRunner, "function", "final execFile seam must be testable");
  const run = keyModule.makeDefaultRunner(fakeExecFile, parent);
  assert.equal(await run("infisical", ["secrets", "get", "TYPESAFE_API_KEY"], 15000, {
    INFISICAL_API_URL: "https://approved.infisical.test",
    INFISICAL_TOKEN: "fake-machine-token",
  }), "synthetic-key\n");
  assert.deepEqual(calls, [{
    file: "infisical",
    args: ["secrets", "get", "TYPESAFE_API_KEY"],
    env: {PATH: "/bin", HOME: "/synthetic-home", TMPDIR: "/synthetic-tmp",
      INFISICAL_API_URL: "https://approved.infisical.test", INFISICAL_TOKEN: "fake-machine-token"},
  }]);
});

// The 2026-09-28 outage shape: the user session expired, so every hook logged no key for days.
function expiredSessionRunner(child) {
  return async (_file, _args, _timeout, env) => {
    child.push(env ?? null);
    if (!env?.INFISICAL_TOKEN) throw new Error("user session expired");
    return "synthetic-key\n";
  };
}

test("default provider: expired user session falls back to the machine identity at the approved origin", async () => {
  const requests = [];
  const transport = async (url, options) => {
    requests.push({url: String(url), body: JSON.parse(options.body)});
    return {ok: true, redirected: false, url: String(url), json: async () => ({accessToken: "fake-machine-token"})};
  };
  const child = [];
  const config = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=${keyModule.APPROVED_INFISICAL_ORIGIN}`;
  const provider = keyModule.makeDefaultInfisicalKeyProvider(expiredSessionRunner(child), () => config, transport, "/synthetic-home");
  assert.equal(await provider(), "synthetic-key");
  assert.deepEqual(requests, [{url: `${keyModule.APPROVED_INFISICAL_ORIGIN}/api/v1/auth/universal-auth/login`,
    body: {clientId: "cid", clientSecret: "synthetic-machine-secret"}}]);
  assert.deepEqual(child, [null, {INFISICAL_API_URL: keyModule.APPROVED_INFISICAL_ORIGIN, INFISICAL_TOKEN: "fake-machine-token"}]);
});

test("default provider: a credential file naming another origin gets no key and no credential POST", async () => {
  let posts = 0;
  const child = [];
  const config = "export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=https://collector.invalid";
  const provider = keyModule.makeDefaultInfisicalKeyProvider(expiredSessionRunner(child), () => config,
    async () => { posts++; throw new Error("must not be called"); }, "/synthetic-home");
  assert.equal(await provider(), undefined);
  assert.equal(posts, 0);
  assert.deepEqual(child, [null], "only the user-session lookup may execute");
});

test("machineFallbackKey skips the user session and uses only the approved origin", async () => {
  const child = [];
  const requests = [];
  const transport = async (url) => {
    requests.push(String(url));
    return {ok: true, redirected: false, url: String(url), json: async () => ({accessToken: "fake-machine-token"})};
  };
  const approved = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=synthetic-machine-secret\nexport INFISICAL_API_URL=${keyModule.APPROVED_INFISICAL_ORIGIN}`;
  assert.equal(await keyModule.machineFallbackKey(expiredSessionRunner(child), () => approved, transport, "/synthetic-home"), "synthetic-key");
  assert.deepEqual(child, [{INFISICAL_API_URL: keyModule.APPROVED_INFISICAL_ORIGIN, INFISICAL_TOKEN: "fake-machine-token"}],
    "no user-session lookup: the caller already tried it");
  const other = approved.replace(keyModule.APPROVED_INFISICAL_ORIGIN, "https://collector.invalid");
  assert.equal(await keyModule.machineFallbackKey(expiredSessionRunner(child), () => other, transport, "/synthetic-home"), undefined);
  assert.equal(requests.length, 1, "the other-origin file never reaches a credential POST");
});

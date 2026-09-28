// Key resolution for omp panes, keyless: askJev* take the key from the call, then
// TYPESAFE_API_KEY, then an installed provider; the Infisical provider caches in memory only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { askJev, askJevScore, keyProviderInstalled, setKeyProvider } from '../../../kit/src/client.ts';
import { makeInfisicalKeyProvider, PROJECT_ID, TTL_MS, FAIL_TTL_MS, infisicalBinary, machineIdentityConfig } from "../src/infisical-key.ts";
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

test("machine identity fallback authenticates without putting client secret in child argv or output", async () => {
  const secret = "synthetic-machine-secret";
  const calls = [];
  const requests = [];
  const server = createServer(async (request, response) => {
    let body = "";
    for await (const chunk of request) body += chunk;
    requests.push({ path: request.url, body: JSON.parse(body) });
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ accessToken: "machine-token", expiresIn: 3600, tokenType: "Bearer" }));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    const config = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=${secret}\nexport INFISICAL_API_URL=http://127.0.0.1:${server.address().port}/api`;
    const provider = makeInfisicalKeyProvider(async (file, args, _timeout, env) => {
      calls.push({ file, args, env });
      if (!env?.INFISICAL_TOKEN) throw new Error("user session expired");
      return "machine-key\n";
    }, () => 0, "/bin/infisical", "/home", () => config);
    const value = await provider();
    assert.equal(calls.some(({ args, env }) => JSON.stringify({ args, env }).includes(secret)), false, "machine secret reached child process");
    assert.equal(value, "machine-key");
    assert.equal(calls.length, 2);
    assert.deepEqual(requests, [{
      path: "/api/v1/auth/universal-auth/login",
      body: { clientId: "cid", clientSecret: secret },
    }]);
    assert.equal(calls[1].env.INFISICAL_TOKEN, "machine-token");
    assert.equal(process.env.TYPESAFE_API_KEY, undefined);
  } finally {
    server.close();
  }
});

test("machine identity fallback refuses rejected authentication without exposing provider error text", async () => {
  const secret = "synthetic-machine-secret";
  let requests = 0;
  const server = createServer(async (request, response) => {
    requests++;
    response.writeHead(401, { "content-type": "application/json" });
    response.end(JSON.stringify({ error: `rejected ${secret}` }));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    const config = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=${secret}\nexport INFISICAL_API_URL=http://127.0.0.1:${server.address().port}/api`;
    let childCalls = 0;
    const provider = makeInfisicalKeyProvider(async () => { childCalls++; throw new Error("user session expired"); }, () => 0, "infisical", "/home", () => config);
    assert.equal(await provider(), undefined);
    assert.equal(requests, 1);
    assert.equal(childCalls, 1, "no secret lookup after rejected login");
  } finally {
    server.close();
  }
});
test("machine identity fallback refuses redirects before forwarding credentials", async () => {
  const secret = "synthetic-machine-secret";
  let redirected = 0;
  const destination = createServer((_request, response) => {
    redirected++;
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ accessToken: "machine-token" }));
  });
  await new Promise((resolve) => destination.listen(0, "127.0.0.1", resolve));
  const origin = createServer((_request, response) => {
    response.writeHead(307, { location: `http://127.0.0.1:${destination.address().port}/collect` });
    response.end();
  });
  await new Promise((resolve) => origin.listen(0, "127.0.0.1", resolve));
  try {
    const config = `export INFISICAL_CLIENT_ID=cid\nexport INFISICAL_CLIENT_SECRET=${secret}\nexport INFISICAL_API_URL=http://127.0.0.1:${origin.address().port}/api`;
    const provider = makeInfisicalKeyProvider(async (_file, _args, _timeout, env) => {
      if (!env?.INFISICAL_TOKEN) throw new Error("user session expired");
      return "machine-key\n";
    }, () => 0, "infisical", "/home", () => config);
    const key = await provider();
    assert.equal(redirected, 0, "credential body was forwarded to redirected host");
    assert.equal(key, undefined);
  } finally {
    origin.close();
    destination.close();
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

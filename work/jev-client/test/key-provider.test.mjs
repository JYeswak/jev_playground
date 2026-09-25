// Key resolution for omp panes, keyless: askJev* take the key from the call, then
// TYPESAFE_API_KEY, then an installed provider; the Infisical provider caches in memory only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { askJev, askJevScore, keyProviderInstalled, setKeyProvider } from '../src/index.ts';
import { makeInfisicalKeyProvider, PROJECT_ID, TTL_MS, FAIL_TTL_MS, infisicalBinary } from '../src/infisical-key.ts';
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
  const provider = makeInfisicalKeyProvider(async () => outputs[runs++](), () => t, 'x');
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
  assert.equal(Object.values(process.env).includes('secret-value'), false);
});

test('infisicalBinary prefers ~/.local/bin/infisical and falls back to PATH', () => {
  assert.equal(infisicalBinary('/h', () => true), '/h/.local/bin/infisical');
  assert.equal(infisicalBinary('/h', () => false), 'infisical');
});

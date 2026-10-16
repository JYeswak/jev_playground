import assert from 'node:assert/strict';
import test from 'node:test';
import projectEntryModule from '../../.omp/hooks/pre/jev-compact.js';


// The entry is what omp loads at session start. A missing optional dependency must not take the
// session down: the entry declines, registers nothing and names the installer. The loader is the
// only seam that can fail, so the missing-package specimen is injected rather than depending on
// whether node_modules happens to exist on the day this test runs.
//
// Observed 2026-10-13: after the kit 0.2.28 restart every pane printed
// "Cannot find package 'fast-jev-compaction'" because the entry imported the binding statically.

type Loader = () => Promise<{ registerOmpCompactionHookFromEnv: (pi: unknown) => void }>;
type Entry = (pi: { on: (e: string, h: unknown) => void }, deps?: { load?: Loader; warn?: (m: string) => void }) => Promise<void>;

// .omp/ has no package.json, so Node treats this file as CommonJS and hands back its default export
// wrapped as { default }. omp loads it on Bun, which does not wrap, so the entry itself stays plain.
// The unwrap lives here, in the test, and checks what it reads instead of assuming a shape.
function callableDefault(module: unknown): Entry {
  if (typeof module === 'function') return module as Entry;
  if (module && typeof module === 'object' && 'default' in module && typeof module.default === 'function') {
    return module.default as Entry;
  }
  throw new Error('entry module has no callable default export');
}
const projectEntry = callableDefault(projectEntryModule);

// The deployed template imports ../../lib/jev-compact/..., a path that only exists in a repo the
// installer has populated. A literal specifier would pull it into tsc and fail resolution here, so
// it is loaded by URL: the runtime load works because its only static import is type-only.
const templateModule: unknown = await import(new URL('../deploy/hook-entry.ts', import.meta.url).href);

const entries: Array<[string, Entry]> = [
  ['project entry .omp/hooks/pre/jev-compact.ts', projectEntry],
  ['deployed template compaction/deploy/hook-entry.ts', callableDefault(templateModule)],
];

function recordingPi() {
  const registered: string[] = [];
  return { pi: { on: (event: string, _handler?: unknown) => { registered.push(event); } }, registered };
}

const missingPackage: Loader = async () => {
  throw Object.assign(
    new Error("Cannot find package 'fast-jev-compaction' imported from /x/compaction/src/omp-binding.ts"),
    { code: 'ERR_MODULE_NOT_FOUND' },
  );
};

for (const [name, entry] of entries) {
  test(`${name}: missing package declines without throwing, registers nothing, names the installer`, async () => {
    const { pi, registered } = recordingPi();
    const warnings: string[] = [];
    const realFetch = globalThis.fetch;
    let networkCalls = 0;
    globalThis.fetch = (async () => { networkCalls += 1; throw new Error('no model call allowed'); }) as typeof fetch;
    try {
      await assert.doesNotReject(entry(pi, { load: missingPackage, warn: (m) => warnings.push(m) }));
    } finally {
      globalThis.fetch = realFetch;
    }
    assert.deepEqual(registered, [], 'no measurement handler may be registered');
    assert.equal(networkCalls, 0, 'zero model calls');
    assert.equal(warnings.length, 1, 'exactly one diagnostic');
    assert.match(warnings[0], /fast-jev-compaction/);
    assert.match(warnings[0], /\.\/compaction\/install-jev-compact\.sh/);
  });

  test(`${name}: any other load failure also declines and keeps the real message`, async () => {
    const { pi, registered } = recordingPi();
    const warnings: string[] = [];
    const broken: Loader = async () => { throw new TypeError('binding exploded at import'); };
    await assert.doesNotReject(entry(pi, { load: broken, warn: (m) => warnings.push(m) }));
    assert.deepEqual(registered, []);
    assert.equal(warnings.length, 1);
    assert.match(warnings[0], /binding exploded at import/);
  });

  test(`${name}: positive control, a loadable binding is registered and nothing is warned`, async () => {
    const { pi, registered } = recordingPi();
    const warnings: string[] = [];
    const ok: Loader = async () => ({
      registerOmpCompactionHookFromEnv: (p) => (p as typeof pi).on('session_before_compact', () => undefined),
    });
    await entry(pi, { load: ok, warn: (m) => warnings.push(m) });
    assert.deepEqual(registered, ['session_before_compact']);
    assert.deepEqual(warnings, []);
  });
}

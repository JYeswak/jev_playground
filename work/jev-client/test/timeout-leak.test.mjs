import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { askJev } from '../src/index.ts';

// A server that accepts and hangs: the SDK timeout must abort the request,
// and that abort must never escape as an unhandled rejection — node:test
// (like a default Node host) fails the run on one, so a green run IS the
// assertion. Regression test for the W7.0 T9 finding: timed-out requests
// killed a default Node host ~1/3 of runs via an AbortError leaked from the
// SDK timer (work/sdk/.../dist/index.mjs:636 Timeout._onTimeout).
// The latency floor proves the timer path actually ran (no vacuous pass).
// Localhost only: keyless, zero external network.
function hangServer() {
  const sockets = new Set();
  const server = http.createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.flushHeaders();
    return; // hang forever
  });
  server.on('connection', (s) => { sockets.add(s); s.on('close', () => sockets.delete(s)); });
  return { server, sockets };
}

test('timed-out requests never escape as unhandled rejections', async (t) => {
  const { server, sockets } = hangServer();
  t.after(() => { server.close(); for (const s of sockets) s.destroy(); });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  process.env.TYPESAFE_BASE_URL = `http://127.0.0.1:${server.address().port}`;
  try {
    for (let i = 0; i < 8; i++) {
      const r = await askJev({ state: {}, questions: { q: 'x?' }, apiKey: 'k', timeoutMs: 50 });
      assert.equal(r.ok, false);
      assert.equal(r.reason, 'transport');
      assert.ok(r.latencyMs >= 40, `timer path ran (latencyMs=${r.latencyMs})`);
    }
  } finally {
    delete process.env.TYPESAFE_BASE_URL;
  }
});

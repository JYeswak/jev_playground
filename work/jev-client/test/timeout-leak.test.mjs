import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { askJev, guardDeadlineMs } from '../../../kit/src/client.ts';

// Timed-out requests must never escape as unhandled rejections: node:test
// (like a default Node host) fails the run on one, so a green run IS that
// assertion. Regression test for the W7.0 T9 finding: timed-out requests
// killed a default Node host ~1/3 of runs via an AbortError leaked from the
// SDK timer (work/sdk/.../dist/index.mjs:636 Timeout._onTimeout).
//
// Two hangs, because two timers can end a request. guardedFetch aborts at
// guardDeadlineMs(timeoutMs) only until headers arrive; after that the SDK's
// own timer (timeoutMs) ends the body wait. The no-headers server forces the
// guard's path every time; the headers-then-hang server (the original T9
// shape) ends on either timer depending on how fast headers land.
//
// No vacuous pass: each result must be a timeout (the message both paths
// carry), and its latency must reach the EARLIEST deadline either timer can
// fire, read from the client itself. 5 ms tolerance covers clock and timer
// granularity (Date.now truncates both ends; libuv starts a timer from its
// cached loop time). The old fixed 40 ms floor sat above the guard's 25 ms
// deadline and failed whenever the guard won (jev-rw2).
// Localhost only: keyless, zero external network.
const TIMEOUT_MS = 50;
const FLOOR_MS = guardDeadlineMs(TIMEOUT_MS) - 5;

function hangServer(t, onRequest) {
  const sockets = new Set();
  const server = http.createServer(onRequest);
  server.on('connection', (s) => { sockets.add(s); s.on('close', () => sockets.delete(s)); });
  t.after(() => { server.close(); for (const s of sockets) s.destroy(); });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function assertTimesOut(server) {
  process.env.TYPESAFE_BASE_URL = `http://127.0.0.1:${server.address().port}`;
  try {
    for (let i = 0; i < 8; i++) {
      const r = await askJev({ state: {}, questions: { q: 'x?' }, apiKey: 'k', timeoutMs: TIMEOUT_MS });
      assert.equal(r.ok, false);
      assert.equal(r.reason, 'transport');
      assert.match(r.error, /timed out/, `a timeout ended the call, not an early failure (error=${r.error})`);
      assert.ok(r.latencyMs >= FLOOR_MS, `a timer path ran (latencyMs=${r.latencyMs}, floor=${FLOOR_MS})`);
    }
  } finally {
    delete process.env.TYPESAFE_BASE_URL;
  }
}

test('no headers: the guard deadline aborts, nothing escapes unhandled', async (t) => {
  await assertTimesOut(await hangServer(t, () => {}));
});

test('headers then hang: whichever timer fires, nothing escapes unhandled', async (t) => {
  await assertTimesOut(await hangServer(t, (req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.flushHeaders();
  }));
});

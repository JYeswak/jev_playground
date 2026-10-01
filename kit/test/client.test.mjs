import assert from "node:assert/strict";
import test from "node:test";
import {
  BILLING_HOLD_MS,
  askJevBundle,
  billingHoldActive,
  resetBillingHold,
} from "../src/client.ts";

const question = { probe: { type: "noul", instructions: "Is this a test request?" } };

for (const status of [401, 402, 403]) {
  test(`HTTP ${status} starts the shared Jev hold before another request`, async () => {
    resetBillingHold();
    const now = 1_000_000;
    let requests = 0;
    const options = {
      state: { probe: "offline status-path test" },
      questions: question,
      model: "jev-1.13.0",
      apiKey: "offline-test-only",
      retry: { maxRetries: 0 },
      timeoutMs: 1000,
      nowMs: () => now,
      fetchImpl: async () => {
        requests += 1;
        return new Response(JSON.stringify({ error: "synthetic status-path response" }), {
          status,
          headers: { "content-type": "application/json" },
        });
      },
    };

    try {
      const first = await askJevBundle(options);
      assert.equal(first.ok, false);
      assert.equal(first.reason, "http");
      assert.equal(requests, 1);
      assert.equal(billingHoldActive(now), now + BILLING_HOLD_MS);

      const second = await askJevBundle(options);
      assert.equal(second.ok, false);
      assert.equal(second.reason, "billing-hold");
      assert.equal(requests, 1, "the hold must stop a second API request");
    } finally {
      resetBillingHold();
    }
  });
}

for (const status of [429, 503]) {
  test(`HTTP ${status} does not start the credential/billing hold`, async () => {
    resetBillingHold();
    let requests = 0;
    const options = {
      state: { probe: "offline transient-status test" },
      questions: question,
      model: "jev-1.13.0",
      apiKey: "offline-test-only",
      retry: { maxRetries: 0 },
      timeoutMs: 1000,
      nowMs: () => 2_000_000,
      fetchImpl: async () => {
        requests += 1;
        return new Response(JSON.stringify({ error: "synthetic transient response" }), {
          status,
          headers: { "content-type": "application/json" },
        });
      },
    };

    try {
      const first = await askJevBundle(options);
      assert.equal(first.ok, false);
      assert.equal(first.reason, "http");
      assert.equal(billingHoldActive(2_000_000), null);
      const second = await askJevBundle(options);
      assert.equal(second.reason, "http");
      assert.equal(requests, 2, "transient statuses remain outside the authorization/billing hold");
    } finally {
      resetBillingHold();
    }
  });
}
test("identical transports share one cached client; distinct ones stay isolated", async () => {
  const { askJev, resetClientCache, clientCacheSize } = await import("../src/client.ts");
  resetClientCache();
  assert.equal(clientCacheSize(), 0);
  const answering = (seen) => async () => {
    seen.push(1);
    return new Response(JSON.stringify({ answers: { probe: { noul: 0.5 } } }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
  const seenA = [];
  const shared = {
    state: { probe: "offline cache test" },
    questions: question,
    model: "jev-1.13.0",
    apiKey: "offline-test-only",
    retry: { maxRetries: 0 },
    timeoutMs: 1000,
    fetchImpl: answering(seenA),
  };
  try {
    const first = await askJev(shared);
    const second = await askJev(shared);
    assert.equal(first.ok, true);
    assert.equal(second.ok, true);
    assert.equal(seenA.length, 2, "both calls dispatch; the client is what is shared");
    assert.equal(clientCacheSize(), 1);
    const seenB = [];
    await askJev({ ...shared, fetchImpl: answering(seenB) });
    assert.equal(seenB.length, 1, "a different transport is never served the cached client");
    assert.equal(clientCacheSize(), 2);
  } finally {
    resetClientCache();
  }
});

import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const api = await import("../src/conformance.ts").catch(() => null);
const contractsApi = await import("../src/contracts.ts").catch(() => null);
const registry = await import("../conformance/registered-adapters.mjs").catch(() => null);
const suiteApi = await import("../conformance/runner.mjs").catch(() => null);
const readJson = async (url) => JSON.parse(await readFile(url, "utf8"));
const gateUrl = new URL("../contracts/fixtures/gate-refuse.json", import.meta.url);
const screenUrl = new URL("../contracts/fixtures/screen-pass.json", import.meta.url);
const recordedUrl = new URL("./fixtures/recorded-answer-rows.json", import.meta.url);
const noNetwork = async (request) => {
  throw new Error(`unexpected network request for ${request?.backendId ?? "unknown backend"}`);
};
const hasWord = (value, words) => words.some((word) => String(value).toLowerCase().includes(word));

test("shared conformance runner and recorded adapter registry are available", () => {
  assert.equal(typeof api?.decide, "function", "kit/src/conformance.ts must export decide");
  assert.ok(Array.isArray(registry?.registeredAdapters), "registered adapters must be explicit");
});

test("shared suite executes C1-C7 for every registered adapter without network", async () => {
  assert.equal(typeof suiteApi?.runConformanceSuite, "function");
  const originalFetch = globalThis.fetch;
  let ambientFetchCalls = 0;
  globalThis.fetch = async () => { ambientFetchCalls += 1; throw new Error("ambient fetch is forbidden"); };
  let suite;
  try {
    suite = await suiteApi.runConformanceSuite();
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(ambientFetchCalls, 0);
  for (const contract of suite.contracts) {
    for (const adapter of suite.adapters) {
      const rows = suite.clauseResults.filter((row) => row.family === contract.family && row.backend === adapter.id);
      assert.deepEqual(rows.map((row) => row.clause).sort(), ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]);
      for (const row of rows) {
        assert.equal(row.status, adapter.id === "regex-rule" && row.clause === "C2" ? "XFAIL" : "PASS",
          `${contract.family}/${adapter.id}/${row.clause}: ${row.detail}`);
      }
    }
  }
});

if (api?.decide && contractsApi?.validateContract && registry?.registeredAdapters) {
  const [gate, screen, recordedRows] = await Promise.all([
    readJson(gateUrl), readJson(screenUrl), readJson(recordedUrl),
  ]);
  const recorded = recordedRows[0];
  const screenState = { record_id: recorded.id };
  const gateState = { command: recorded.id };
  const options = Object.keys(recorded.answers.choice.probabilities);
  const choiceContract = contractsApi.validateContract({
    ...gate,
    family: "recorded-choice-conformance",
    state: { fields: ["record_id"], privacy_allowlist: ["record_id"], maximum_state_text_bytes: 128, raw_transcript_allowed: false },
    question: {
      ...gate.question,
      type: "choice",
      options: Object.fromEntries(options.map((id) => [id, { description: id, action: id === recorded.answers.choice.choice ? "pass" : "refuse" }])),
    },
  });
  const input = { state: { record_id: recorded.id }, result: { id: recorded.id, payload: "unchanged" } };
  const answerTransport = async () => ({
    ...structuredClone(recorded.answers.choice),
    modelId: recorded.model,
    costUsd: recorded.usage.input_tokens * 0.042 / 1_000_000,
  });
  const byId = new Map(registry.registeredAdapters.map((adapter) => [adapter.id, adapter]));
  test("recorded answers for every registered adapter run without ambient network", async () => {
    assert.ok(byId.size > 0);
    const originalFetch = globalThis.fetch;
    let ambientFetchCalls = 0;
    globalThis.fetch = async () => { ambientFetchCalls += 1; throw new Error("ambient fetch is forbidden"); };
    try {
      for (const adapter of byId.values()) {
        let injectedCalls = 0;
        const result = await api.decide({
          contract: choiceContract,
          adapter,
          ...input,
          transport: async (request) => { injectedCalls += 1; return answerTransport(request); },
        });
        assert.equal(result.status, "answered", `${adapter.id}: recorded result accepted`);
        assert.equal(result.choice, recorded.answers.choice.choice, `${adapter.id}: recorded choice preserved`);
        assert.equal(injectedCalls > 0, adapter.usesTransport === true, `${adapter.id}: injected transport policy`);
      }
    } finally {
      globalThis.fetch = originalFetch;
    }
    assert.equal(ambientFetchCalls, 0);
  });

  test("C1 unoffered choice refuses and applies the contract safe side", async () => {
    const adapter = {
      id: "hostile-choice", modelId: "hostile-choice", probabilities: "required",
      async evaluate() { return { choice: "not-offered", probabilities: { c0: 0.1, c1: 0.8, none: 0.1 }, costUsd: 0 }; },
    };
    const result = await api.decide({ contract: choiceContract, adapter, ...input, transport: noNetwork });
    assert.equal(result.status, "refused");
    assert.equal(result.action, "refuse");
    assert.ok(hasWord(result.reason, ["choice", "option"]));
  });

  test("C2 rejects non-finite, rescaled and chosen-below-max distributions", async () => {
    const chosen = recorded.answers.choice.choice;
    const other = options.find((id) => id !== chosen);
    const nanDistribution = Object.fromEntries(options.map((id, index) => [id, index === 0 ? Number.NaN : 0]));
    const rescaledDistribution = Object.fromEntries(options.map((id) => [id, 0.1]));
    const chosenMaxDistribution = Object.fromEntries(options.map((id) => [id, id === chosen ? 0.9 : 0.1 / (options.length - 1)]));
    for (const [choice, probabilities] of [
      [chosen, nanDistribution],
      [chosen, rescaledDistribution],
      [other, chosenMaxDistribution],
    ]) {
      const adapter = {
        id: "hostile-probabilities", modelId: "hostile-probabilities", probabilities: "required",
        async evaluate() { return { choice, probabilities, costUsd: 0 }; },
      };
      const result = await api.decide({ contract: choiceContract, adapter, ...input, transport: noNetwork });
      assert.equal(result.status, "refused");
      assert.equal(result.action, "refuse");
      assert.ok(hasWord(result.reason, ["probabil"]));
    }
  });

  test("C2 accepts the inclusive probability-sum tolerance and rejects just beyond it", async () => {
    for (const [probabilities, status] of [
      [{ c0: 0.02, c1: 0.96, none: 0 }, "answered"],
      [{ c0: 0.019, c1: 0.96, none: 0 }, "refused"],
    ]) {
      const adapter = {
        id: "boundary-probabilities", modelId: "boundary-probabilities", probabilities: "required",
        async evaluate() { return { choice: "c1", probabilities, costUsd: 0 }; },
      };
      const result = await api.decide({ contract: choiceContract, adapter, ...input, transport: noNetwork });
      assert.equal(result.status, status);
    }
  });

  test("C3 timeout applies each contract safe side, returns within budget and logs timeout", async () => {
    for (const [contract, state, action, resultValue] of [
      [gate, gateState, "refuse", undefined],
      [screen, screenState, "pass", input.result],
    ]) {
      const row = { ...contract, budget: { ...contract.budget, latency_budget_ms: 250 } };
      const adapter = {
        id: `hang-${contract.surface_type}`, modelId: "recorded-hang", probabilities: "required",
        async evaluate({ signal }, transport) { return transport({ signal }); },
      };
      const rows = [];
      const start = performance.now();
      const decision = await api.decide({
        contract: row,
        adapter,
        state,
        result: input.result,
        transport: () => new Promise(() => {}),
        logger: (entry) => rows.push(entry),
      });
      assert.ok(performance.now() - start <= row.budget.latency_budget_ms + 50, "allows timer-dispatch scheduling jitter");
      assert.equal(decision.status, "timeout");
      assert.equal(decision.reason, "timeout");
      assert.equal(decision.action, action);
      if (resultValue) assert.strictEqual(decision.result, resultValue);
      assert.ok(rows.some((entry) => entry.reason === "timeout"));
    }
  });

  test("C3 transport errors and missing keys take the safe side", async () => {
    for (const error of [new Error("connection reset"), Object.assign(new Error("missing key"), { code: "missing-key" })]) {
      const adapter = {
        id: "unavailable", modelId: "unavailable", probabilities: "required",
        async evaluate() { throw error; },
      };
      const result = await api.decide({ contract: gate, adapter, state: gateState, result: input.result, transport: noNetwork });
      assert.equal(result.action, "refuse");
      assert.ok(["transport", "missing-key"].includes(result.reason));
    }
  });

  test("C4 cap passes command gates and logs daily-cap without calling adapter", async () => {
    let calls = 0;
    const rows = [];
    const result = await api.decide({
      contract: contractsApi.validateContract({ ...gate, budget: { ...gate.budget, daily_call_cap: 0 } }),
      adapter: { id: "counted", modelId: "counted", probabilities: "required", async evaluate() { calls += 1; throw new Error("must not run"); } },
      state: gateState,
      callsUsedToday: 0,
      transport: noNetwork,
      logger: (entry) => rows.push(entry),
    });
    assert.equal(result.status, "daily-cap");
    assert.equal(result.action, "pass");
    assert.equal(calls, 0);
    assert.ok(rows.some((entry) => entry.reason === "daily-cap"));
  });

  test("C5 oversize and non-allowlisted state are refused before transport", async () => {
    let calls = 0;
    const adapter = { id: "counted", modelId: "counted", probabilities: "required", async evaluate() { throw new Error("must not run"); } };
    for (const [contract, baseState] of [[gate, gateState], [screen, screenState]]) {
      const field = contract.state.fields[0];
      const states = [
        { [field]: "x".repeat(contract.state.maximum_state_text_bytes + 32) },
        { ...baseState, raw_transcript: "private" },
      ];
      for (const state of states) {
        const result = await api.decide({ contract, adapter, state, result: input.result, transport: async () => { calls += 1; } });
        assert.equal(result.status, "refused");
        assert.equal(result.action, contract.safe_side);
      }
    }
    assert.equal(calls, 0);
  });

  test("non-JSON state refuses safely and records no false input hash", async () => {
    const state = { record_id: recorded.id };
    state.self = state;
    let calls = 0;
    const adapter = { id: "counted", modelId: "counted", probabilities: "required", async evaluate() { calls += 1; } };
    const result = await api.decide({
      contract: choiceContract, adapter, state,
      transport: async () => { calls += 1; return answerTransport(); },
    });
    assert.equal(result.status, "refused");
    assert.equal(result.action, choiceContract.safe_side);
    assert.equal(result.logRow.input_sha256, null);
    assert.equal(calls, 0);
  });

  test("C6 same input and recorded answer yield the same decision", async () => {
    const adapter = byId.get("jev-recorded");
    assert.ok(adapter, "recorded Jev adapter is registered");
    const first = await api.decide({ contract: choiceContract, adapter, ...input, transport: answerTransport });
    const second = await api.decide({ contract: choiceContract, adapter, ...input, transport: answerTransport });
    assert.deepEqual([first.action, first.choice], [second.action, second.choice]);
  });

  test("C7 decision logs have ids, timing, cost and input hash but no raw state", async () => {
    const rows = [];
    await api.decide({
      contract: choiceContract,
      adapter: byId.get("jev-recorded"),
      ...input,
      transport: answerTransport,
      logger: (row) => rows.push(row),
    });
    assert.equal(rows.length, 1);
    assert.equal(rows[0].backend_id, "jev-recorded");
    assert.equal(rows[0].model_id, recorded.model);
    assert.ok(Number.isFinite(rows[0].latency_ms));
    assert.ok(Number.isFinite(rows[0].cost_usd));
    assert.equal(rows[0].input_sha256.length, 64);
    assert.equal([...rows[0].input_sha256].every((char) => "abcdef0123456789".includes(char)), true);
    assert.equal(JSON.stringify(rows[0]).includes(recorded.id), false);
    assert.equal("state" in rows[0], false);
  });
}

import assert from "node:assert/strict";
import test from "node:test";

let api = {};
try {
  api = await import("./run.mjs");
} catch (error) {
  if (error?.code !== "ERR_MODULE_NOT_FOUND") throw error;
}

function requireFunction(name) {
  assert.equal(typeof api[name], "function", `run.mjs must export ${name}`);
  return api[name];
}

const hasMessage = (fragment) => (error) =>
  error instanceof Error && error.message.toLowerCase().includes(fragment);

const questions = {
  exfiltration: {type: "noul"},
  destructive: {type: "noul"},
  privilege: {type: "noul"},
  irreversible_publish: {type: "noul"},
  secret_staging: {type: "noul"},
};

function fixture(count = 1) {
  const sample = Array.from({length: count}, (_, index) => ({
    event_id: `event-${index}`,
    cmd_sha: `sha-${index}`,
    dcg_decision: "deny",
    sample_source: "frozen-frame",
  }));
  const labelsA = {
    labeler_id: "human-a",
    labels: sample.map((row) => ({event_id: row.event_id, label: "no-harm"})),
  };
  const labelsB = {
    labeler_id: "human-b",
    labels: sample.map((row) => ({event_id: row.event_id, label: "no-harm"})),
  };
  const commands = new Map(sample.map((row) => [row.event_id, `echo ${row.event_id}`]));
  return {sample, labelsA, labelsB, commands};
}

function success(inputTokens = 8) {
  return {
    ok: true,
    model: "jev-1.13.0",
    resolvedModel: "jev-1.13.0",
    latencyMs: 5,
    usage: {input_tokens: inputTokens},
    answers: Object.fromEntries(
      Object.keys(questions).map((key) => [key, {type: "noul", noul: 0.1, confidence: 0.9}]),
    ),
  };
}

test("resolveLabels requires two independent complete label sets and third-party adjudication", () => {
  const resolveLabels = requireFunction("resolveLabels");
  const sample = [
    {event_id: "event-0"},
    {event_id: "event-1"},
  ];
  const labelsA = {labeler_id: "human-a", labels: [
    {event_id: "event-0", label: "harm"},
    {event_id: "event-1", label: "no-harm"},
  ]};
  const labelsB = {labeler_id: "human-b", labels: [
    {event_id: "event-0", label: "no-harm"},
    {event_id: "event-1", label: "no-harm"},
  ]};

  assert.throws(() => resolveLabels(sample, [labelsA], []), hasMessage("two independent"));
  assert.throws(() => resolveLabels(sample, [labelsA, labelsA], []), hasMessage("independent"));
  assert.throws(() => resolveLabels(sample, [labelsA, {...labelsB, labels: labelsB.labels.slice(0, 1)}], []), hasMessage("missing"));
  assert.throws(() => resolveLabels(sample, [labelsA, labelsB], []), hasMessage("adjudicat"));
  const finalLabels = resolveLabels(sample, [labelsA, labelsB], [
    {labeler_id: "human-c", event_id: "event-0", label: "harm"},
  ]);
  assert.equal(finalLabels.get("event-0"), "harm");
  assert.equal(finalLabels.get("event-1"), "no-harm");
});

test("runSample validates labels before any request", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, commands} = fixture();
  let calls = 0;
  await assert.rejects(runSample({
    sample,
    labelSets: [labelsA],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => { calls += 1; return success(); },
    appendRow: async () => {},
  }), hasMessage("two independent"));
  assert.equal(calls, 0);
});

test("runSample uses one Jev attempt per request and stops immediately on billing refusals", async () => {
  const runSample = requireFunction("runSample");
  for (const status of [401, 402, 403]) {
    const {sample, labelsA, labelsB, commands} = fixture(2);
    let calls = 0;
    const output = [];
    const result = await runSample({
      sample,
      labelSets: [labelsA, labelsB],
      adjudications: [],
      commandByEventId: commands,
      askBundle: async (options) => {
        calls += 1;
        assert.equal(options.model, "jev-1.13.0");
        assert.equal(options.retry.maxRetries, 0);
        assert.equal(options.state.command.startsWith("echo event-"), true);
        return {ok: false, reason: "http", error: `systemOne HTTP ${status}: refused`, latencyMs: 1, model: "jev-1.13.0"};
      },
      appendRow: async (row) => output.push(row),
    });

    assert.equal(calls, 1);
    assert.equal(result.attempts, 1);
    assert.equal(result.stopReason, `http-${status}`);
    assert.equal(output.length, 1);
    assert.equal(output[0].status, "not_scored");
    assert.equal("command" in output[0], false);
    assert.equal("apiKey" in output[0], false);
  }
});

test("runSample stops before the next request when the spend ceiling cannot reserve a full call", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture(37);
  let calls = 0;
  const output = [];
  const result = await runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => { calls += 1; return success(32768); },
    appendRow: async (row) => output.push(row),
  });

  assert.equal(calls, 36);
  assert.equal(result.attempts, 36);
  assert.equal(result.inputTokens, 36 * 32768);
  assert.equal(result.stopReason, "spend-cap");
  assert.equal(output.length, 36);
});

test("runSample enforces the 400-call ceiling and records no raw command text", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture(401);
  let calls = 0;
  const output = [];
  const result = await runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => { calls += 1; return success(1); },
    appendRow: async (row) => output.push(row),
  });

  assert.equal(calls, 400);
  assert.equal(result.attempts, 400);
  assert.equal(result.stopReason, "call-cap");
  assert.equal(output.length, 400);
  assert.equal(output.some((row) => "command" in row), false);
  assert.equal(output[0].status, "scored");
  assert.equal(output[0].jevFlag, false);
});

test("runSample refuses an out-of-range Noul answer and never labels it safe", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture();
  const output = [];
  const result = await runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => {
      const answer = success();
      answer.answers.exfiltration.noul = 1.01;
      return answer;
    },
    appendRow: async (row) => output.push(row),
  });

  assert.equal(result.attempts, 1);
  assert.equal("jevFlag" in output[0], false);
});

test("runSample stops when a successful response omits billable usage", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture(2);
  const output = [];
  let calls = 0;
  const result = await runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => {
      calls += 1;
      const answer = success();
      delete answer.usage;
      return answer;
    },
    appendRow: async (row) => output.push(row),
  });

  assert.equal(calls, 1);
  assert.equal(result.stopReason, "usage-unavailable");
  assert.equal(output[0].status, "not_scored");
  assert.equal("jevFlag" in output[0], false);
});

test("runSample rejects oversized request input before any request", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture();
  commands.set(sample[0].event_id, "x".repeat(100_000));
  let calls = 0;

  await assert.rejects(runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => { calls += 1; return success(); },
    appendRow: async () => {},
  }), hasMessage("over"));
  assert.equal(calls, 0);
});


test("runSample rejects duplicate event IDs before any request", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture();
  sample.push({...sample[0]});
  let calls = 0;

  await assert.rejects(runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => { calls += 1; return success(); },
    appendRow: async () => {},
  }), hasMessage("unique"));
  assert.equal(calls, 0);
});

test("runSample does not score answers from an unexpected resolved model", async () => {
  const runSample = requireFunction("runSample");
  const {sample, labelsA, labelsB, commands} = fixture();
  const output = [];

  await runSample({
    sample,
    labelSets: [labelsA, labelsB],
    adjudications: [],
    commandByEventId: commands,
    askBundle: async () => ({...success(), resolvedModel: "unexpected-model"}),
    appendRow: async (row) => output.push(row),
  });

  assert.equal(output[0].status, "not_scored");
  assert.equal(output[0].reason, "invalid-answer-or-model");
  assert.equal("jevFlag" in output[0], false);
  assert.equal("command" in output[0], false);
});

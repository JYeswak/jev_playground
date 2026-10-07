import { performance } from "node:perf_hooks";
import { readFile } from "node:fs/promises";
import { decide } from "../src/conformance.ts";
import { validateContract } from "../src/contracts.ts";
import { registeredAdapters } from "./registered-adapters.mjs";

const readJson = async (url) => JSON.parse(await readFile(url, "utf8"));
const contractDir = new URL("../contracts/fixtures/", import.meta.url);
const fixtureUrl = new URL("../test/fixtures/recorded-answer-rows.json", import.meta.url);
const discrepancyUrl = new URL("./DISCREPANCIES.md", import.meta.url);

function parseDiscrepancies(markdown) {
  return markdown.split("\n").flatMap((line) => {
    const cells = line.split("|").map((cell) => cell.trim());
    if (cells.length < 7 || !cells[1].startsWith("DISC-")) return [];
    return [{ id: cells[1], backend: cells[2], clause: cells[3], status: cells[4], review_date: cells[5] }];
  });
}


function testResult(family, backend, clause, ok, detail = "") {
  return { family, backend, clause, status: ok ? "PASS" : "FAIL", detail };
}

export async function runConformanceSuite() {
  const [gateFixture, screenFixture, rows, discrepancyText] = await Promise.all([
    readJson(new URL("gate-refuse.json", contractDir)),
    readJson(new URL("screen-pass.json", contractDir)),
    readJson(fixtureUrl),
    readFile(discrepancyUrl, "utf8"),
  ]);
  const discrepancies = parseDiscrepancies(discrepancyText);
  const record = rows[0];
  const optionIds = Object.keys(record.answers.choice.probabilities);
  const choiceContract = validateContract({
    ...gateFixture,
    family: "recorded-choice-conformance",
    state: { fields: ["record_id"], privacy_allowlist: ["record_id"], maximum_state_text_bytes: 128, raw_transcript_allowed: false },
    question: {
      ...gateFixture.question,
      options: Object.fromEntries(optionIds.map((id) => [id, { description: id, action: id === record.answers.choice.choice ? "pass" : "refuse" }])),
    },
  });
  const input = { state: { record_id: record.id }, result: { record_id: record.id, value: "unchanged" } };
  const recordedTransport = async () => ({
    ...structuredClone(record.answers.choice),
    modelId: record.model,
    costUsd: record.usage.input_tokens * 0.042 / 1_000_000,
  });
  const clauseResults = [];
  const conditionResults = [];

  for (const contract of [gateFixture, screenFixture]) {
    const state = contract.state.fields.length === 1 && contract.state.fields[0] === "command"
      ? { command: record.id }
      : input.state;
    const familyInput = { ...input, state };
    for (const adapter of registeredAdapters) {
      const allowed = Object.keys(contract.question.options);
      const invalidChoice = {
        ...adapter,
        async evaluate() { return { choice: "not-offered", modelId: adapter.modelId, costUsd: 0, ...(adapter.probabilities === "required" ? { probabilities: Object.fromEntries(allowed.map((id) => [id, 1 / allowed.length])) } : {}) }; },
      };
      const c1 = await decide({ contract, adapter: invalidChoice, ...familyInput, transport: recordedTransport });
      clauseResults.push(testResult(contract.family, adapter.id, "C1", c1.status === "refused" && c1.action === contract.safe_side));

      if (adapter.probabilities === "unsupported") {
        const discrepancy = discrepancies.find((entry) => entry.backend === adapter.id && entry.clause === "C2" && entry.status === "ACCEPTED");
        const result = testResult(contract.family, adapter.id, "C2", Boolean(discrepancy), discrepancy ? `XFAIL:${discrepancy.id}` : "missing-discrepancy");
        if (discrepancy) result.status = "XFAIL";
        clauseResults.push(result);
      } else {
        const invalidProbability = {
          ...adapter,
          async evaluate() { return { choice: allowed[0], probabilities: Object.fromEntries(allowed.map((id, index) => [id, index === 0 ? Number.NaN : 0])), costUsd: 0 }; },
        };
        const c2 = await decide({ contract, adapter: invalidProbability, ...familyInput, transport: recordedTransport });
        clauseResults.push(testResult(contract.family, adapter.id, "C2", c2.status === "refused" && c2.action === contract.safe_side));
      }

      const hanging = { ...adapter, async evaluate({ signal }, transport) { return transport({ signal }); } };

      const start = performance.now();
      const timeoutResult = await decide({
        contract: { ...contract, budget: { ...contract.budget, latency_budget_ms: 250 } },
        adapter: hanging,
        ...familyInput,
        transport: () => new Promise(() => {}),
      });
      clauseResults.push(testResult(contract.family, adapter.id, "C3", timeoutResult.status === "timeout" &&
        timeoutResult.action === contract.safe_side && performance.now() - start <= 250 + 50));

      const capResult = await decide({
        contract: { ...contract, budget: { ...contract.budget, daily_call_cap: 0 } },
        adapter,
        ...familyInput,
        transport: recordedTransport,
        callsUsedToday: 0,
      });
      clauseResults.push(testResult(contract.family, adapter.id, "C4", capResult.status === "daily-cap" &&
        capResult.action === contract.budget.cap_reached_action && capResult.logRow.reason === "daily-cap"));

      let calls = 0;
      const baseState = contract.state.fields[0] === "command" ? { command: record.id } : input.state;
      const oversizeInput = await decide({
        contract,
        adapter,
        state: { [contract.state.fields[0]]: "x".repeat(contract.state.maximum_state_text_bytes + 32) },
        transport: async () => { calls += 1; return recordedTransport(); },
      });
      const privateInput = await decide({
        contract,
        adapter,
        state: { ...baseState, raw_transcript: "private" },
        result: input.result,
        transport: async () => { calls += 1; return recordedTransport(); },
      });
      const c5 = oversizeInput.status === "refused" && oversizeInput.action === contract.safe_side &&
        privateInput.status === "refused" && privateInput.action === contract.safe_side && calls === 0;
      clauseResults.push(testResult(contract.family, adapter.id, "C5", c5));

      const first = await decide({ contract: choiceContract, adapter, ...input, transport: recordedTransport });
      const second = await decide({ contract: choiceContract, adapter, ...input, transport: recordedTransport });
      clauseResults.push(testResult(contract.family, adapter.id, "C6", first.status === "answered" && second.status === "answered" &&
        first.action === second.action && first.choice === second.choice));

      const rows = [];
      const logged = await decide({ contract: choiceContract, adapter, ...input, transport: recordedTransport, logger: (row) => rows.push(row) });
      const logRow = rows[0];
      const c7 = Boolean(logRow && logRow.backend_id === adapter.id && logRow.model_id &&
        Number.isFinite(logRow.latency_ms) && (logRow.cost_usd === null || Number.isFinite(logRow.cost_usd)) &&
        typeof logRow.input_sha256 === "string" && logRow.input_sha256.length === 64 && !Object.hasOwn(logRow, "state") &&
        !JSON.stringify(logRow).includes(record.id) && logged.logRow === logRow);
      clauseResults.push(testResult(contract.family, adapter.id, "C7", c7));
    }
    const conditions = [
      ["out-of-options", "C1"], ["timeout", "C3"], ["daily-cap", "C4"],
      ["oversize", "C5"], ["privacy-allowlist", "C5"], ["deterministic-replay", "C6"], ["log-redaction", "C7"],
    ];
    for (const [condition, clause] of conditions) {
      const outcomes = clauseResults.filter((entry) => entry.family === contract.family && entry.clause === clause);
      const complete = outcomes.length === registeredAdapters.length && outcomes.every((entry) => ["PASS", "XFAIL"].includes(entry.status));
      conditionResults.push({ family: contract.family, condition, status: complete ? "PASS" : "" });
    }
  }

  const shippedBackends = registeredAdapters.map((adapter) => adapter.id);
  const matrixContracts = [
    { family: gateFixture.family, shipped_backends: shippedBackends },
    { family: screenFixture.family, shipped_backends: shippedBackends },
  ];
  return { contracts: matrixContracts, adapters: registeredAdapters, clauseResults, conditionResults, discrepancies };
}

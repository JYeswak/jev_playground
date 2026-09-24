#!/usr/bin/env node
// Compact demo: instant context compaction, keyless fixture lane.
// Pattern stolen from Movez (@0xMovez) "Jev Engineering" use case 05 —
// score relevance per tool call/result, keep/drop/truncate verbatim, never
// summarize — executed through the vendored clone's own pipeline:
// fast-jev-compaction@6e1da50 (dist/, read-only, never edited) via its
// injected-asker seam: compact(messages, asker, options).
//
// Default lane: a RECORDED fixture asker answers keepCall/keepResult per
// tool, so `node demos/compact/demo.mjs` exits 0 with no key and no network.
// --live asks real Jev through work/jev-client (needs TYPESAFE_API_KEY).
//
// NO-CLAIM: a fixture keep/drop is not a live compaction. No 1M-to-86K
// figure is cited here and none is ours.

import { compact, reductionRatio, collectToolCalls } from "../../fast-jev-compaction/dist/index.js";

const LIVE = process.argv.includes("--live");

// Short transcript: stale exploration (Glob), verbose-but-relevant read
// (Read), failure evidence (Bash). Pinned first + last two stay regardless.
let n = 0;
function call(tool, input, output, isError = false) {
  const tool_use_id = `toolu_${++n}`;
  return [
    { role: "assistant", text: "", toolUses: [{ tool_use_id, tool, input, text: output, isError }], toolResults: [] },
    { role: "user", text: "", toolUses: [], toolResults: [{ tool_use_id, text: output, isError }] },
  ];
}
const user = (text) => ({ role: "user", text, toolUses: [] });
const assistant = (text) => ({ role: "assistant", text, toolUses: [] });

const bigFile = `// router.ts — 600 lines of route tables\n${"  { path: '/api/v1/widgets', handler: handleWidgets },\n".repeat(12)}`;

const messages = [
  user("Route /healthz to the new handler without breaking existing routes."),
  assistant("Checking the route table first, then the handler."),
  ...call("Glob", { pattern: "src/**/*.bak" }, "src/old.bak\nsrc/notes.bak"),
  ...call("Read", { file_path: "src/router.ts" }, bigFile),
  ...call("Bash", { command: "npm test" }, "FAIL routes.test.ts\n  healthz > returns 200\n    Expected: 200\n    Received: 404", true),
  assistant("The healthz route is missing; the table and the failing test agree on the fix."),
  assistant("Adding the route above the catch-all, keeping everything else byte-identical."),
  user("Thanks. Ship it."),
];

// Recorded fixture answers per tool: { keepCall, keepResult }.
const FIXTURE = {
  Glob: { keepCall: 0.15, keepResult: 0.1 }, // stale exploration: drop call
  Read: { keepCall: 0.85, keepResult: 0.3 }, // call matters, verbose result: truncate
  Bash: { keepCall: 0.9, keepResult: 0.88 }, // failure evidence: keep
};

function fixtureAsker(calls) {
  return {
    async ask(_state, questions) {
      const answers = {};
      for (const key of Object.keys(questions)) {
        const m = key.match(/^(call|result)_(t\d+)$/);
        if (!m) throw new Error(`fixture: unexpected question key ${key}`);
        const call = calls.find((c) => c.id === m[2]);
        if (!call) throw new Error(`fixture: unknown call ${m[2]}`);
        const f = FIXTURE[call.tool];
        if (!f) throw new Error(`fixture: no recorded answers for tool ${call.tool}`);
        answers[key] = { noul: m[1] === "call" ? f.keepCall : f.keepResult };
      }
      return { answers };
    },
  };
}

let asker;
if (LIVE) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  asker = {
    async ask(state, questions) {
      const r = await askJevBundle({ state, questions, model: "jev-1.13.0", timeoutMs: 20000 });
      if (!r.ok && (r.reason === "unconfigured" || r.reason === "sdk-missing")) {
        // Refuse before compacting anything; a thrown error would read as a crash (jev-6smc).
        console.log(`live lane: NOT_RUN — ${r.error}`);
        process.exit(2);
      }
      if (!r.ok) throw new Error(`live Jev call failed: ${r.reason} ${r.error ?? ""}`);
      return { answers: r.answers };
    },
  };
}

const calls = collectToolCalls(messages, 2);
if (!LIVE) asker = fixtureAsker(calls);

const result = await compact(messages, asker, { preserveRecentMessages: 2 });

console.log("id | tool | action | keepCall | keepResult");
for (const d of result.decisions) {
  console.log(`${d.id} | ${d.tool} | ${d.action} | ${d.keepCall.toFixed(2)} | ${d.keepResult.toFixed(2)}`);
}
console.log("");
console.log("stats:", JSON.stringify(result.stats));
console.log(`chars saved: ${(reductionRatio(result) * 100).toFixed(1)}%`);
console.log(`messages: ${result.stats.messagesBefore} → ${result.stats.messagesAfter}`);

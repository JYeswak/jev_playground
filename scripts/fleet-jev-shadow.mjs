import { createInterface } from "node:readline";
import { askJevChoice } from "../kit/src/client.ts";

const CLASSES = {
  working: "The pane is actively executing useful agent work.",
  idle: "The pane has an omp agent but no active work evidence.",
  "stalled-wait": "The pane is waiting with no live work and has exceeded the stall interval.",
  "no-agent": "The pane has no omp process in its process tree.",
};

const inputLines = createInterface({ input: process.stdin });
for await (const line of inputLines) {
  if (!line.trim()) continue;
  let input;
  try {
    input = JSON.parse(line);
  } catch {
    console.log(JSON.stringify({ ok: false, reason: "invalid-json" }));
    continue;
  }
  const result = await askJevChoice({
    state: {
      pane_index: input.pane_index,
      worker_panes: input.worker_panes,
      evidence_features: input.evidence_features,
    },
    instructions: "Classify the operational state of this fleet pane from process evidence. Choose no-agent only when the process tree lacks omp; choose stalled-wait only when the evidence says a wait has exceeded its stall interval; choose working when active execution evidence exists; otherwise choose idle.",
    classes: CLASSES,
    model: "jev-1.13.0",
    timeoutMs: 10000,
  });
  console.log(JSON.stringify({
    ts: new Date().toISOString(),
    pane_index: input.pane_index,
    incumbent: input.incumbent,
    evidence_features: input.evidence_features,
    ok: result.ok,
    choice: result.ok ? result.choice : null,
    confidence: result.ok ? result.confidence : null,
    probabilities: result.ok ? result.probabilities : null,
    latencyMs: result.latencyMs,
    usage: result.ok ? result.usage ?? null : null,
    reason: result.ok ? null : result.reason,
  }));
}

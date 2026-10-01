/** Bounded Jev Noul for jev-5qx8. stdin {message}; stdout result JSON. */
import { askJev } from "../kit/src/client.ts";
import { useInfisicalKey } from "../work/jev-client/src/use-infisical-key.ts";
const MODEL = "jev-1.13.0";
const QUESTION = {
  instructions: "Is this assistant message waiting for a human decision or approval before work can continue?",
  criteria: {
    true: "Explicitly asks a human to approve, decide, confirm, or give input; work is blocked until they reply",
    false: "Reports completion, status, or findings; continues work itself; asks no human for a decision",
  },
};
let raw = "";
for await (const chunk of process.stdin) raw += chunk;
let message;
try { message = JSON.parse(raw).message; } catch {
  console.log(JSON.stringify({ ok: false, reason: "bad-input", error: "stdin is not JSON", model: MODEL, latencyMs: 0 }));
  process.exit(0);
}
if (typeof message !== "string" || !message.trim()) {
  console.log(JSON.stringify({ ok: false, reason: "bad-input", error: "message must be non-empty", model: MODEL, latencyMs: 0 }));
  process.exit(0);
}
useInfisicalKey();
const result = await askJev({ state: { message: message.trim().slice(0, 2000) }, questions: { needs_human: QUESTION }, model: MODEL, timeoutMs: 20000 });
if (!result.ok) {
  console.log(JSON.stringify({ ok: false, reason: result.reason, error: result.error.slice(0, 300), model: result.model, latencyMs: result.latencyMs }));
  process.exit(0);
}
console.log(JSON.stringify({ ok: true, score: result.scores.needs_human, model: result.model, latencyMs: result.latencyMs, ...(result.usage ? { usage: result.usage } : {}) }));

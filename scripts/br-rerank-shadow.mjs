import { appendFile, mkdir } from "node:fs/promises";
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { askJevChoice } from "../kit/src/client.ts";

export const MODEL = "jev-1.13.0";
export const SHADOW_LOG = `${process.env.HOME}/.local/state/jev/br-rerank-shadow.jsonl`;

export function rankIds(ready) {
  return ready
    .filter((row) => row && typeof row.id === "string")
    .slice(0, 8)
    .map((row) => row.id);
}

export function buildRequest(ready) {
  const items = ready.filter((row) => row && typeof row.id === "string").slice(0, 8);
  return {
    incumbent: items.map((row) => row.id),
    state: {
      decision: "select the next bead for an agent to work",
      candidates: items.map((row) => ({
        id: row.id,
        title: typeof row.title === "string" ? row.title : "",
        priority: row.priority ?? null,
      })),
    },
    classes: Object.fromEntries(items.map((row) => [row.id, `${row.priority ?? ""} ${row.title ?? ""}`.trim()])),
  };
}

async function append(row) {
  await mkdir(`${process.env.HOME}/.local/state/jev`, { recursive: true, mode: 0o700 });
  await appendFile(SHADOW_LOG, JSON.stringify(row) + "\n", { mode: 0o600 });
}

export async function rerank(ready) {
  const request = buildRequest(ready);
  if (request.incumbent.length < 2) return { ok: false, reason: "too-few-candidates", incumbent: request.incumbent };
  const result = await askJevChoice({
    state: request.state,
    instructions: "Which candidate bead should be selected next for the fleet agent? Prefer the item with the clearest obtainable acceptance and highest current mission leverage. Choose only among the offered bead IDs.",
    classes: request.classes,
    model: MODEL,
    timeoutMs: 10000,
  });
  return {
    ts: new Date().toISOString(),
    model: MODEL,
    incumbent: request.incumbent,
    ok: result.ok,
    choice: result.ok ? result.choice : null,
    confidence: result.ok ? result.confidence : null,
    probabilities: result.ok ? result.probabilities : null,
    latencyMs: result.latencyMs,
    usage: result.ok ? result.usage ?? null : null,
    reason: result.ok ? null : result.reason,
  };
}

async function main() {
  const input = createInterface({ input: process.stdin });
  for await (const line of input) {
    if (!line.trim()) continue;
    try {
      const result = await rerank(JSON.parse(line));
      await append(result);
      console.log(JSON.stringify(result));
    } catch (error) {
      const result = { ok: false, reason: "shadow-error", error: String(error) };
      await append(result);
      console.log(JSON.stringify(result));
    }
  }
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) await main();

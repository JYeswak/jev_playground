import { appendFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";
import { askJevBundle } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";
import { rerankTop1 } from "../../kit/src/rerank.ts";
import { CUT, RISK, STATE_CONTEXT } from "../../work/bicameral-gate/questions.mjs";

type Job = {
  kind: "gate" | "web";
  path: string;
  row: Record<string, unknown>;
  command?: string;
  query?: string;
  items?: Array<{ id: string; title: string; text: string; url?: string }>;
};

async function readJob(): Promise<Job> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));
  return JSON.parse(Buffer.concat(chunks).toString("utf8")) as Job;
}

async function appendRow(path: string, row: Record<string, unknown>): Promise<void> {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  await appendFile(path, JSON.stringify(row) + "\n", { mode: 0o600 });
}

async function main(): Promise<void> {
  useInfisicalKey();
  const job = await readJob();
  try {
    if (job.kind === "gate") {
      const result = await askJevBundle({ state: { command: job.command, context: STATE_CONTEXT }, questions: RISK, model: "jev-1.13.0", timeoutMs: 20_000 });
      if (!result.ok) {
        await appendRow(job.path, { ...job.row, status: "error", error: result.error, model: result.model, latencyMs: result.latencyMs, tokens: null, jevFlag: null, maxScore: null, scores: null });
        return;
      }
      const scores = Object.fromEntries(Object.entries(result.answers).flatMap(([key, answer]) => {
        if (!answer || typeof answer !== "object" || !("noul" in answer) || typeof answer.noul !== "number") return [];
        return [[key, answer.noul]];
      }));
      const maxScore = Math.max(...Object.values(scores));
      await appendRow(job.path, { ...job.row, status: "scored", jevFlag: maxScore > CUT, maxScore, scores, model: result.resolvedModel, latencyMs: result.latencyMs, tokens: result.usage ?? null });
      return;
    }
    const result = await rerankTop1({ query: job.query ?? "", candidates: job.items ?? [] });
    await appendRow(job.path, { ...job.row, status: "answered", pickIndex: (job.items ?? []).findIndex((item) => item.id === result.choice), latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null, outputTokens: result.usage?.output_tokens ?? null, model: result.model });
  } catch (error) {
    await appendRow(job.path, { ...job.row, status: "error", error: error instanceof Error ? error.message : String(error) });
  }
}

await main();

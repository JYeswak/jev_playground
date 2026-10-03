import { createServer } from "node:http";
import { once } from "node:events";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { randomBytes } from "node:crypto";

const ROOT = resolve(import.meta.dirname, "../..");
const BENIGN = "u06-benign-output-survives";

function fakeSecret() {
  const suffix = (n) => randomBytes(n).toString("hex").slice(0, n);
  return `apikey_fakefake${suffix(27)}_${suffix(64)}`;
}

function readJsonBody(request) {
  return new Promise((resolveBody, reject) => {
    const chunks = [];
    request.on("data", (part) => { chunks.push(part); });
    request.on("end", () => {
      try {
        const rawBody = Buffer.concat(chunks);
        resolveBody({ body: JSON.parse(rawBody.toString("utf8")), rawBody });
      } catch (error) {
        reject(error);
      }
    });
    request.on("error", reject);
  });
}

function completion(res, model, message, finishReason, stream) {
  if (stream) {
    const chunk = (delta, finish = null) => ({
      id: "u06-local-response",
      object: "chat.completion.chunk",
      created: 1,
      model,
      choices: [{ index: 0, delta, finish_reason: finish }],
    });
    res.writeHead(200, { "content-type": "text/event-stream", "cache-control": "no-cache" });
    res.write(`data: ${JSON.stringify(chunk({ role: "assistant" }))}\n\n`);
    for (const [index, call] of (message.tool_calls ?? []).entries()) {
      res.write(`data: ${JSON.stringify(chunk({ tool_calls: [{ index, ...call }] }))}\n\n`);
    }
    if (message.content) res.write(`data: ${JSON.stringify(chunk({ content: message.content }))}\n\n`);
    res.write(`data: ${JSON.stringify(chunk({}, finishReason))}\n\n`);
    res.end("data: [DONE]\n\n");
    return;
  }
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify({
    id: "u06-local-response",
    object: "chat.completion",
    created: 1,
    model,
    choices: [{ index: 0, message, finish_reason: finishReason }],
  }));
}

async function run(masking, inspectResult) {
  const marker = fakeSecret();
  let scratch;
  let home;
  let agentDir;
  let modelPath;
  try {
    const tempRoot = join(ROOT, "var", "agent-tmp");
    await mkdir(tempRoot, { recursive: true });
    scratch = await mkdtemp(join(tempRoot, "jev-u0N-route."));
    await writeFile(join(scratch, ".owner"), JSON.stringify({
      pid: process.pid, label: "jev-u0N-route", repo: ROOT, created: new Date().toISOString(),
    }) + "\n");
    home = join(scratch, "home");
    agentDir = join(scratch, "agent");
    await mkdir(home);
    await mkdir(agentDir);
    modelPath = join(agentDir, "models.yml");
    await writeFile(modelPath, [
      "providers:",
      "  u06-local:",
      "    baseUrl: http://127.0.0.1:__PORT__/v1",
      "    api: openai-completions",
      "    auth: none",
      "    models:",
      "      - id: capture",
      "        name: U06 local capture provider",
      "        contextWindow: 200000",
      "        maxTokens: 256",
      "",
    ].join("\n"));
  } catch (error) {
    if (scratch) await rm(scratch, { recursive: true, force: true });
    throw new Error("failed to configure the local-only OMP provider", { cause: error });
  }

  let resolveCapture;
  let rejectCapture;
  const captured = new Promise((resolve, reject) => {
    resolveCapture = resolve;
    rejectCapture = reject;
  });
  let resolvePromptResult;
  const promptResult = new Promise((resolve) => { resolvePromptResult = resolve; });
  let resolveComplete;
  let rejectComplete;
  const completed = new Promise((resolve, reject) => {
    resolveComplete = resolve;
    rejectComplete = reject;
  });
  let requestCount = 0;
  const toolExecutionEnds = [];
  let providerPayloadSummary;
  let child;
  let lines;
  let timeoutId;
  let server;

  server = createServer(async (req, res) => {
    try {
      const { body, rawBody } = await readJsonBody(req);
      requestCount += 1;
      const model = typeof body.model === "string" ? body.model : "u06-local/capture";
      if (!providerPayloadSummary) {
        const offeredTool = (body.tools ?? []).find((tool) => tool.function?.name === "bash");
        if (!offeredTool) throw new Error(`local provider tools: ${(body.tools ?? []).map((tool) => tool.function?.name ?? tool.name ?? "unnamed").join(",")}`);
        const command = `printf '%s\\n%s\\n' "$U06_DATA" '${BENIGN}'`;
        completion(res, model, {
          role: "assistant",
          content: null,
          tool_calls: [{
            id: "call-u06-synthetic-output",
            type: "function",
            function: { name: "bash", arguments: JSON.stringify({ command }) },
          }],
        }, "tool_calls", body.stream === true);
        providerPayloadSummary = { toolChoice: body.tool_choice ?? null };
        return;
      }

      const messages = body.messages ?? [];
      const providerMessageMatches = inspectResult
        ? messages.flatMap((message, index) => Object.entries(message).flatMap(([key, value]) => {
          const serialized = JSON.stringify(value);
          if (!serialized.includes(marker) && !serialized.includes(BENIGN)) return [];
          return [{
            index,
            role: message.role,
            field: key,
            containsMarker: serialized.includes(marker),
            containsBenign: serialized.includes(BENIGN),
          }];
        }))
        : undefined;
      const outputMessage = messages.find((message) =>
        message.role === "tool" && JSON.stringify(message.content).includes(BENIGN));
      const providerVisibleResult = outputMessage ?? null;
      const providerResultText = JSON.stringify(providerVisibleResult);
      if (!providerPayloadSummary.toolResult) {
        providerPayloadSummary.toolResult = {
          markerVisible: providerResultText.includes(marker),
          benignVisible: providerResultText.includes(BENIGN),
          providerRequests: requestCount,
          providerRequestB64: inspectResult ? rawBody.toString("base64") : undefined,
          providerVisibleResult: inspectResult ? providerVisibleResult : undefined,
          providerMessageMatches,
        };
        resolveCapture(providerPayloadSummary.toolResult);
      }
      completion(res, model, { role: "assistant", content: "done" }, "stop", body.stream === true);
    } catch (error) {
      res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: String(error?.message ?? error) }));
      rejectCapture(error);
      rejectComplete(error);
    }
  });

  server.listen(0, "127.0.0.1");
  server.once("listening", () => {
    void startSession();
  });
  async function startSession() {
    try {
      const { port } = server.address();
      const modelConfig = await readFile(modelPath, "utf8");
      await writeFile(modelPath, modelConfig.replace("__PORT__", String(port)));
      const args = [
        "--model", "u06-local/capture",
        "--mode=rpc",
        "--no-session",
        "--no-title",
        "--no-ui",
        "--no-extensions",
        "--approval-mode=yolo",
        "--max-time=40",
      ];
      const bypassPath = join(scratch, "bypass.yml");
      if (!masking) await writeFile(bypassPath, "secrets:\n  enabled: false\n", { mode: 0o600 });
      const bypassArgs = masking ? [] : ["--config", bypassPath];
      const projectDirectory = ROOT;
      const childEnv = {
        HOME: home,
        PATH: process.env.PATH,
        TMPDIR: scratch,
        PI_CODING_AGENT_DIR: agentDir,
        XDG_CONFIG_HOME: join(scratch, "xdg-config"),
        XDG_STATE_HOME: join(scratch, "xdg-state"),
        RCH_LANE_REGISTRY: resolve(ROOT, "../control-plane/registries/rch_lanes.tsv"),
        U06_DATA: marker,
      };
      child = spawn("omp", [...bypassArgs, ...args], {
        cwd: projectDirectory,
        env: childEnv,
        stdio: ["pipe", "pipe", "ignore"],
      });
      lines = createInterface({ input: child.stdout });
      lines.on("line", (line) => {
        try {
          const frame = JSON.parse(line);
          if (frame.type === "response" && frame.id === "n1") {
            if (!frame.success) throw new Error("RPC protocol negotiation failed");
            child.stdin.write(JSON.stringify({ id: "p1", type: "prompt", message: "Run bash once to print U06_DATA and the harmless output, then say done." }) + "\n");
          }
          if (frame.type === "tool_execution_end") {
            const resultContent = frame.result?.content ?? null;
            const resultText = JSON.stringify(resultContent);
            toolExecutionEnds.push({
              toolName: frame.toolName,
              toolCallId: frame.toolCallId,
              isError: frame.isError,
              containsMarker: resultText.includes(marker),
              containsBenign: resultText.includes(BENIGN),
              rawHostToolResultB64: inspectResult ? Buffer.from(line).toString("base64") : undefined,
            });
          }
          if (frame.type === "prompt_result" && frame.id === "p1") resolvePromptResult(frame.status);
        } catch (error) { rejectComplete(error); }
      });
      child.once("error", rejectComplete);
      const exited = once(child, "exit");
      child.stdin.write(JSON.stringify({ id: "n1", type: "negotiate_protocol", protocolVersion: 2 }) + "\n");
      timeoutId = setTimeout(() => rejectComplete(new Error(`local omp route timed out: requests=${requestCount}`)), 45_000);
      const toolResult = await captured;
      const promptStatus = await Promise.race([
        promptResult,
        new Promise((_, reject) => setTimeout(() => reject(new Error("prompt did not settle after local provider reply")), 10_000)),
      ]);
      clearTimeout(timeoutId);
      child.stdin.end();
      await Promise.race([exited, new Promise((resolve) => setTimeout(resolve, 2_000))]);
      if (child.exitCode === null) child.kill("SIGTERM");
      server.close();
      resolveComplete({
        ...toolResult,
        promptStatus,
        providerRequests: requestCount,
        toolExecutionEnds,
      });
      await rm(scratch, { recursive: true, force: true });
    } catch (error) {
      clearTimeout(timeoutId);
      child?.kill("SIGTERM");
      lines?.close();
      server.close();
      await rm(scratch, { recursive: true, force: true });
      rejectCapture(error);
      rejectComplete(error);
    }
  }
  return completed;
}

const masking = process.argv.includes("--mask");
const bypass = process.argv.includes("--bypass-mask");
const inspectResult = process.argv.includes("--inspect-result");
if (masking === bypass) {
  process.stderr.write("usage: node probe.mjs --mask | --bypass-mask [--inspect-result]\n");
  process.exitCode = 2;
} else {
  try {
    const result = await run(masking, inspectResult);
    const output = inspectResult
      ? {
        promptStatus: result.promptStatus,
        providerRequests: result.providerRequests,
        markerVisible: result.markerVisible,
        benignVisible: result.benignVisible,
        providerVisibleResultB64: Buffer.from(JSON.stringify(result.providerVisibleResult)).toString("base64"),
        providerRequestB64: result.providerRequestB64,
        providerMessageMatches: result.providerMessageMatches,
        toolExecutionEnds: result.toolExecutionEnds,
      }
      : result;
    process.stdout.write(JSON.stringify(output) + "\n");
  } catch (error) {
    process.stderr.write(`NOT_RUN: ${error?.message ?? error}\n`);
    process.exitCode = 2;
  }
}

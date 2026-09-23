/**
 * kit-guard: omp extension that makes the starter kit's honesty rules mechanical.
 * Install: copy this directory to <project>/.omp/extensions/kit-guard/ (or ~/.omp/agent/extensions/).
 * Written against @oh-my-pi/pi-coding-agent 18.2.10.
 */
import { existsSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import {
  agentsChangedMessage,
  bashVerdict,
  missingPatterns,
  pathVerdict,
  REANCHOR_AFTER_COMPACTION,
  targetPaths,
} from "./policy";

function mtimeMs(path: string): number | undefined {
  try {
    return statSync(path).mtimeMs;
  } catch {
    return undefined;
  }
}

/** Nearest ancestor containing .git (omp may be launched from a subdirectory). */
export function projectRoot(start: string): string {
  let dir = start;
  for (;;) {
    if (existsSync(join(dir, ".git"))) return dir;
    const up = dirname(dir);
    if (up === dir) return start;
    dir = up;
  }
}

export default function kitGuard(pi: ExtensionAPI) {
  pi.setLabel("kit-guard");
  const allowGateEdit = process.env.KIT_GATE_EDIT === "1";
  let agentsSeenMtime: number | undefined;
  let root = projectRoot(process.cwd());

  pi.registerCommand("kit-guard", {
    description: "Show kit-guard status (gate-edit mode, AGENTS.md pattern check)",
    handler: async (_args, ctx) => {
      let missing: string[] = [];
      try {
        missing = missingPatterns(readFileSync(join(projectRoot(ctx.cwd), "AGENTS.md"), "utf8"));
      } catch {
        missing = ["(AGENTS.md not found)"];
      }
      ctx.ui.notify(
        `kit-guard: gate files ${allowGateEdit ? "WRITABLE (KIT_GATE_EDIT=1)" : "read-only"}; ` +
          `AGENTS.md patterns ${missing.length === 0 ? "12/12 present" : `missing: ${missing.join(", ")}`}`,
        missing.length === 0 ? "info" : "warning",
      );
    },
  });

  pi.on("session_start", async (_e, ctx) => {
    root = projectRoot(ctx.cwd);
    agentsSeenMtime = mtimeMs(join(root, "AGENTS.md"));
    if (allowGateEdit) ctx.ui.notify("kit-guard: KIT_GATE_EDIT=1, gate files are writable this session", "warning");
  });

  pi.on("tool_call", async event => {
    if (event.toolName === "bash") {
      const v = bashVerdict(String((event.input as { command?: unknown }).command ?? ""));
      if (v) return v;
    }
    if (event.toolName === "edit" || event.toolName === "write") {
      for (const p of targetPaths(event.input as Record<string, unknown>)) {
        const v = pathVerdict(p, allowGateEdit);
        if (v) return v;
      }
    }
    return undefined;
  });

  // A9: after any edit to AGENTS.md, check the 12 forbidden patterns survived.
  pi.on("tool_result", async event => {
    if (event.toolName !== "edit" && event.toolName !== "write") return undefined;
    const paths = targetPaths(event.input);
    if (!paths.some(p => p.replace(/\\/g, "/").endsWith("AGENTS.md"))) return undefined;
    let text = "";
    try {
      text = readFileSync(join(root, "AGENTS.md"), "utf8");
    } catch {
      return undefined;
    }
    agentsSeenMtime = mtimeMs(join(root, "AGENTS.md")); // the agent just wrote it; it knows the content
    const missing = missingPatterns(text);
    if (missing.length === 0) return undefined;
    return {
      isError: true,
      content: [
        ...event.content,
        {
          type: "text" as const,
          text: `kit-guard A9: AGENTS.md no longer names these forbidden patterns: ${missing.join(", ")}. Restore them verbatim before doing anything else.`,
        },
      ],
    };
  });

  // Compaction is where process gets forgotten: re-anchor on the next turn.
  pi.on("session_compact", async () => {
    pi.sendMessage(
      { customType: "kit-guard", content: REANCHOR_AFTER_COMPACTION, display: true },
      { deliverAs: "nextTurn" },
    );
  });

  // AGENTS.md is cached in the system prompt for the process lifetime; if a human
  // (or another agent) edits it mid-session, tell this agent to re-read it.
  pi.on("agent_end", async () => {
    const now = mtimeMs(join(root, "AGENTS.md"));
    if (now !== undefined && agentsSeenMtime !== undefined && now > agentsSeenMtime) {
      agentsSeenMtime = now;
      pi.sendMessage(
        { customType: "kit-guard", content: agentsChangedMessage(new Date(now).toISOString()), display: true },
        { deliverAs: "nextTurn" },
      );
    }
  });
}

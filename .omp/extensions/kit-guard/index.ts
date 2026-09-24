/**
 * kit-guard: omp extension that makes the starter kit's honesty rules mechanical.
 * Install: copy this directory to <project>/.omp/extensions/kit-guard/ (or ~/.omp/agent/extensions/).
 * Written against @oh-my-pi/pi-coding-agent 18.2.10.
 *
 * W1.4: config-driven (plan docs/PLAN-DEEP-KIT-20260922.md:198). The protected
 * set comes from `.omp/kit-guard.json`; a missing or malformed config fails
 * closed (block and say why, never allow). KIT_GATE_EDIT=1 still only opens
 * the B7 path gate; the B5 honesty gate (bash) has no override.
 */
import { existsSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import {
  agentsChangedMessage,
  bashVerdict,
  buildReanchorMessage,
  loadGuardConfig,
  missingPatterns,
  pathVerdict,
  targetPaths,
  type GuardConfig,
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

function loadConfigFor(root: string): { ok: true; cfg: GuardConfig } | { ok: false; reason: string } {
  try {
    return { ok: true, cfg: loadGuardConfig(root) };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { ok: false, reason: `${msg}. Refusing to allow (fail-closed). A human with KIT_GATE_EDIT=1 must restore it.` };
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
      const r = projectRoot(ctx.cwd);
      let missing: string[] = [];
      try {
        missing = missingPatterns(readFileSync(join(r, "AGENTS.md"), "utf8"));
      } catch {
        missing = ["(AGENTS.md not found)"];
      }
      const cfg = loadConfigFor(r);
      ctx.ui.notify(
        `kit-guard: gate files ${allowGateEdit ? "WRITABLE (KIT_GATE_EDIT=1)" : "read-only"}; ` +
          `AGENTS.md patterns ${missing.length === 0 ? "12/12 present" : `missing: ${missing.join(", ")}`}; ` +
          `config ${cfg.ok ? "ok" : `MISSING (${cfg.reason})`}`,
        missing.length === 0 && cfg.ok ? "info" : "warning",
      );
    },
  });

  pi.on("session_start", async (_e, ctx) => {
    root = projectRoot(ctx.cwd);
    agentsSeenMtime = mtimeMs(join(root, "AGENTS.md"));
    if (allowGateEdit) ctx.ui.notify("kit-guard: KIT_GATE_EDIT=1, gate files are writable this session", "warning");
    const cfg = loadConfigFor(root);
    if (!cfg.ok) ctx.ui.notify(`kit-guard: ${cfg.reason}`, "warning");
  });

  pi.on("tool_call", async event => {
    const cfg = loadConfigFor(root);
    if (!cfg.ok) return { block: true as const, reason: cfg.reason };
    if (event.toolName === "bash") {
      const input = event.input;
      let command = "";
      if (input && typeof input === "object" && "command" in input && typeof input.command === "string") {
        command = input.command;
      }
      const v = bashVerdict(String(command ?? ""), cfg.cfg);
      if (v) return v;
    }
    if (event.toolName === "edit" || event.toolName === "write") {
      const input = event.input;
      const paths = targetPaths(
        input && typeof input === "object" ? (input as Record<string, unknown>) : {},
      );
      for (const p of paths) {
        const v = pathVerdict(p, allowGateEdit, cfg.cfg);
        if (v) return v;
      }
    }
    return undefined;
  });

  // A9: after any edit to AGENTS.md, check the 12 forbidden patterns survived.
  pi.on("tool_result", async event => {
    if (event.toolName !== "edit" && event.toolName !== "write") return undefined;
    const input = event.input;
    const paths = targetPaths(
      input && typeof input === "object" ? (input as Record<string, unknown>) : {},
    );
    if (!paths.some(p => p.replace(/\\/g, "/").endsWith("AGENTS.md"))) return undefined;
    let text = "";
    try {
      text = readFileSync(join(root, "AGENTS.md"), "utf8");
    } catch {
      return undefined;
    }
    agentsSeenMtime = mtimeMs(join(root, "AGENTS.md")); // the agent just wrote it; it knows the content
    const cfg = loadConfigFor(root);
    const missing = missingPatterns(text, cfg.ok ? cfg.cfg : undefined);
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
    const cfg = loadConfigFor(root);
    pi.sendMessage(
      {
        customType: "kit-guard",
        content: cfg.ok ? buildReanchorMessage(cfg.cfg) : "kit-guard: context was just compacted. Re-read AGENTS.md, GATES.md, and your bead before your next action.",
        display: true,
      },
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

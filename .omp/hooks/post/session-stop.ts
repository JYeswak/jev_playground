/**
 * Project session_stop hook. Discovered from .omp/hooks/post/.
 *
 * Contract: { continue: true, additionalContext } requests one
 * model-visible continuation. stop_hook_active stays silent so the
 * hook cannot loop. Never blocks. Never calls Jev.
 *
 * The condition is the mission, not one missing file:
 *   ready work is still queued, or
 *   the README names a set of demos that are not all on disk, or
 *   the turn is a stand-down while that mission is unfinished, or
 *   the pane is a WORKER (tmux pane index >= 2). A worker always gets one
 *   continuation: finish its own in-progress bead, then claim from br ready,
 *   and if nothing is claimable tell pane 1 it is idle instead of stopping
 *   silently. Measured 2026-09-24: with br ready empty this hook returned
 *   nothing, and 4 of 6 worker panes sat idle until Joshua noticed.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export const MISSION =
  "Mission: prove Jev with the API. A claim about Jev comes only from live calls (pinned jev-1.13.0) on data we did not write, " +
  "against a bar committed before the first call, with the spend stated. Build tools from what survives, liven an omp surface, " +
  "dogfood it, keep the README a stranger can run. Do not stop on a single demo. Do not write a ruling.";

const STAND_DOWN = /standing by|queue dry|nothing further|no further action/i;

export function citedDemos(readme: string): string[] {
  return [
    ...new Set(
      [...readme.matchAll(/node (demos\/[A-Za-z0-9_./-]+\/demo\.mjs)/g)].map((match) => match[1]),
    ),
  ];
}

export function assistantText(message: unknown): string {
  if (!message || typeof message !== "object") return "";
  const content = (message as { content?: unknown }).content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .map((part) =>
      part && typeof part === "object" && "text" in part ? String((part as { text: unknown }).text) : "",
    )
    .join("\n");
}

export function decideStop(
  event: { stop_hook_active?: boolean; signal?: { aborted?: boolean } },
  world: { readyCount: number; missing: string[]; lastText: string; paneIndex?: number },
): { continue: true; additionalContext: string } | undefined {
  if (event.stop_hook_active || event.signal?.aborted) return undefined;
  const standingDown = STAND_DOWN.test(world.lastText);
  const worker = typeof world.paneIndex === "number" && world.paneIndex >= 2;
  if (!worker && world.readyCount <= 0 && world.missing.length === 0 && !standingDown) return undefined;
  const parts = [MISSION];
  if (worker) {
    parts.push("First finish the bead you have in progress; do not stop between its steps.");
  }
  if (world.readyCount > 0) {
    parts.push(
      `br ready has ${world.readyCount} item(s). Claim the highest-priority unassigned one; another pane verifies it before it closes.`,
    );
  }
  if (world.missing.length > 0) {
    parts.push(
      `README names ${world.missing.length} demo(s) not on disk: ${world.missing.join(", ")}.`,
    );
  }
  if (standingDown) {
    parts.push("This turn stood down. Pick the next unfinished stage of the mission and start it.");
  }
  if (worker) {
    parts.push(
      `If you have nothing in progress and nothing in br ready you can claim, run ` +
        `\`ntm send jev --pane=1 "IDLE pane ${world.paneIndex}: <one line on what you finished>"\` ` +
        `so the conductor dispatches you, then stop.`,
    );
  }
  return { continue: true, additionalContext: parts.join(" ") };
}

function readyCount(): number {
  try {
    const out = execFileSync("br", ["ready"], {
      encoding: "utf8",
      timeout: 8000,
      stdio: ["ignore", "pipe", "ignore"],
    });
    return (out.match(/^[0-9]+\. \[/gm) ?? []).length;
  } catch {
    return 0;
  }
}

function paneIndex(): number | undefined {
  const pane = process.env.TMUX_PANE;
  if (!pane) return undefined;
  try {
    const out = execFileSync("tmux", ["display", "-p", "-t", pane, "#{pane_index}"], {
      encoding: "utf8",
      timeout: 3000,
      stdio: ["ignore", "pipe", "ignore"],
    });
    const n = Number.parseInt(out.trim(), 10);
    return Number.isFinite(n) ? n : undefined;
  } catch {
    return undefined;
  }
}

export default function sessionStopHook(pi: {
  on: (event: string, handler: (event: unknown) => Promise<unknown>) => void;
}): void {
  pi.on("session_stop", async (event) => {
    try {
      const typed = event as {
        stop_hook_active?: boolean;
        signal?: { aborted?: boolean };
        last_assistant_message?: unknown;
      };
      const readme = existsSync("README.md") ? readFileSync("README.md", "utf8") : "";
      const missing = citedDemos(readme).filter((path) => !existsSync(resolve(path)));
      return decideStop(typed, {
        readyCount: readyCount(),
        missing,
        lastText: assistantText(typed.last_assistant_message),
        paneIndex: paneIndex(),
      });
    } catch {
      return undefined;
    }
  });
}

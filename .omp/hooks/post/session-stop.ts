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
 *   the turn is a stand-down while that mission is unfinished.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export const MISSION =
  "Mission: validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a stranger can run. " +
  "Do not stop on a single demo. Do not spend a key unless the unit says live. Do not write a ruling.";

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
  world: { readyCount: number; missing: string[]; lastText: string },
): { continue: true; additionalContext: string } | undefined {
  if (event.stop_hook_active || event.signal?.aborted) return undefined;
  const standingDown = STAND_DOWN.test(world.lastText);
  if (world.readyCount <= 0 && world.missing.length === 0 && !standingDown) return undefined;
  const parts = [MISSION];
  if (world.readyCount > 0) {
    parts.push(`br ready has ${world.readyCount} item(s). Claim the highest you did not author.`);
  }
  if (world.missing.length > 0) {
    parts.push(
      `README names ${world.missing.length} demo(s) not on disk: ${world.missing.join(", ")}.`,
    );
  }
  if (standingDown) {
    parts.push("This turn stood down. Pick the next unfinished stage of the mission and start it.");
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
      });
    } catch {
      return undefined;
    }
  });
}

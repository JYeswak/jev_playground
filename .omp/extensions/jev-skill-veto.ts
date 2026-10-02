/** D9 skill veto, SHADOW mode (bead jev-wbel): observe skill loads, never block.
 *
 * On `tool_call` for a skill `read` (a skill-protocol URL or a SKILL.md file read),
 * asks the exact preregistered fits-Noul (cut 0.40) and appends a would-veto row to
 * the shadow log. The handler ALWAYS returns undefined: the load proceeds untouched.
 * Any failure (no key, refused answer, timeout, error, reached daily cap, log
 * unwritable) skips the call silently. Prompt text goes only to the mode-600 sidecar,
 * keyed by its hash, for later blind labeling; the main log carries hashes, never text.
 */
import { appendFile, mkdir, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";
import {
  isSkillReadPath,
  skillNameFromPath,
  vetoCheck,
  requestHash,
  SKILL_VETO_CAP_PER_DAY,
  SKILL_VETO_PROMPT_MAX,
  type NoulAsker,
} from "../../kit/src/skill-veto.ts";

const LOG_DIR = process.env.JEV_SKILL_VETO_LOG_DIR ?? join(homedir(), ".local", "state", "jev");
const LOG_FILE = join(LOG_DIR, "skill-veto-shadow.jsonl");
const SIDECAR_FILE = join(LOG_DIR, "skill-veto-requests.jsonl");

const SKILL_ROOTS = [
  join(homedir(), ".claude", "skills"),
  join(homedir(), ".agents", "skills"),
];

async function readDescription(skill: string): Promise<string> {
  const segs = skill.split("/").filter(Boolean);
  const candidates: string[] = [];
  for (const root of SKILL_ROOTS) {
    candidates.push(join(root, ...segs, "SKILL.md"));
    if (segs.length > 1) candidates.push(join(root, segs[segs.length - 1], "SKILL.md"));
  }
  for (const file of candidates) {
    try {
      // Dev winner 2026-10-02 (jev-wbel): description + body head beat desc-only
      // (misses 4/11 vs 5/11, wrong-vetoes 22/30 both).
      const text = await readFile(file, "utf8");
      const m = /^description:\s*(.*?)\s*$/m.exec(text);
      const desc = m ? m[1].replace(/^["']|["']$/g, "") : "";
      const body = text.split("---").slice(2).join("---").trim().slice(0, 700);
      if (desc || body) return `${desc} — ${body}`.slice(0, 1200);
      return "";
    } catch {
      continue;
    }
  }
  return "";
}

async function todayCount(): Promise<number> {
  try {
    const text = await readFile(LOG_FILE, "utf8");
    if (text.length > 2 * 1024 * 1024) return SKILL_VETO_CAP_PER_DAY;
    const day = new Date().toISOString().slice(0, 10);
    let n = 0;
    for (const line of text.split("\n")) {
      if (line.includes(`"day":"${day}"`)) n += 1;
    }
    return n;
  } catch {
    return 0;
  }
}

async function appendRow(row: Record<string, unknown>, sidecar: Record<string, unknown> | null): Promise<void> {
  try {
    await mkdir(LOG_DIR, { recursive: true });
    await appendFile(LOG_FILE, JSON.stringify(row) + "\n", { mode: 0o600 });
    if (sidecar) await appendFile(SIDECAR_FILE, JSON.stringify(sidecar) + "\n", { mode: 0o600 });
  } catch {
    // Logging never disturbs the turn.
  }
}

/** Best-effort session id for row attribution; "unknown" when unavailable. */
function sessionId(ctx: unknown): string {
  try {
    if (typeof ctx !== "object" || ctx === null || !("sessionManager" in ctx)) return "unknown";
    const sm: unknown = ctx.sessionManager;
    if (typeof sm !== "object" || sm === null || !("getSessionFile" in sm)) return "unknown";
    const fn: unknown = sm.getSessionFile;
    if (typeof fn !== "function") return "unknown";
    const file: unknown = Reflect.apply(fn, sm, []);
    if (typeof file !== "string") return "unknown";
    const base = file.split("/").pop() ?? file;
    return base.replace(/\.jsonl$/, "").slice(-36) || "unknown";
  } catch {
    return "unknown";
  }
}

export function createSkillVetoHandler(deps?: {
  ask?: NoulAsker;
  describe?: (skill: string) => Promise<string>;
  countToday?: () => Promise<number>;
  log?: (row: Record<string, unknown>, sidecar: Record<string, unknown> | null) => Promise<void>;
}) {
  const ask = deps?.ask ?? ((o) => askJev(o));
  const describe = deps?.describe ?? readDescription;
  const countToday = deps?.countToday ?? todayCount;
  const log = deps?.log ?? appendRow;
  let lastPrompt = "";

  return {
    onContext(event: unknown): undefined {
      try {
        if (typeof event !== "object" || event === null || !("messages" in event)) return undefined;
        const messages: unknown = event.messages;
        if (!Array.isArray(messages)) return undefined;
        for (let i = messages.length - 1; i >= 0; i -= 1) {
          const m: unknown = messages[i];
          if (typeof m !== "object" || m === null || !("role" in m) || !("content" in m)) continue;
          if (m.role !== "user" || !Array.isArray(m.content)) continue;
          const text = m.content
            .filter((c: unknown): c is { type: string; text: string } => {
              if (typeof c !== "object" || c === null || !("type" in c) || !("text" in c)) return false;
              return c.type === "text" && typeof c.text === "string";
            })
            .map((c) => c.text)
            .join(" ");
          if (text.trim()) {
            lastPrompt = text.slice(0, SKILL_VETO_PROMPT_MAX);
            break;
          }
        }
      } catch {
        // Snoop failure keeps the previous prompt; never disturbs context.
      }
      return undefined;
    },

    async onToolCall(event: unknown, ctx: unknown): Promise<undefined> {
      try {
        if (typeof event !== "object" || event === null || !("toolName" in event)) return undefined;
        if (event.toolName !== "read") return undefined;
        if (!("input" in event) || typeof event.input !== "object" || event.input === null) return undefined;
        if (!("path" in event.input)) return undefined;
        const path: unknown = event.input.path;
        if (!isSkillReadPath(path)) return undefined;
        if (typeof path !== "string") return undefined;
        if ((await countToday()) >= SKILL_VETO_CAP_PER_DAY) return undefined;
        const skill = skillNameFromPath(path);
        const prompt = lastPrompt;
        const description = await describe(skill);
        const r = await vetoCheck({ prompt, skill, description, ask });
        const day = new Date().toISOString().slice(0, 10);
        const reqHash = requestHash(prompt);
        await log(
          {
            ts: new Date().toISOString(),
            day,
            skill,
            session: sessionId(ctx),
            reqHash,
            noul: r.noul,
            decision: r.vetoed ? "veto" : "allow",
            wouldVeto: r.vetoed,
            reason: r.reason,
            latencyMs: r.latencyMs,
            model: r.model,
            ...(r.usage ? { usage: r.usage } : {}),
          },
          prompt ? { reqHash, prompt } : null,
        );
      } catch {
        // Shadow failure is silent by design; the load always proceeds.
      }
      return undefined;
    },
  };
}

export default function jevSkillVetoExtension(pi: {
  on: (event: string, handler: (event: unknown, ctx: unknown) => unknown) => void;
}): void {
  const h = createSkillVetoHandler();
  pi.on("context", (event) => h.onContext(event));
  pi.on("tool_call", (event, ctx) => h.onToolCall(event, ctx));
}

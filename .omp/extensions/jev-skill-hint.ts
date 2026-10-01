/** Per-prompt skill hint (bead jev-4nyy): Jev Choice over a lexical shortlist.
 *
 * On before_agent_start the prompt is shortlisted (<= 20) over skill
 * name+description, then one Choice (plus 'none') picks the skill to read.
 * A 'Likely relevant skills: ...' custom message is injected when confidence
 * >= 0.5. Fail open: without a roster, a refused answer, 'none', or low
 * confidence the handler yields undefined and the turn is unchanged. Every
 * Choice call appends one checkpoint row (model, tokens, latency, status).
 */
import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJevChoice } from "../../kit/src/client.ts";
import { hintSkills, loadSkillRoster, type ChoiceAsker, type SkillEntry } from "../../kit/src/skill-hint.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const CALL_LOG = join(homedir(), ".local", "state", "jev", "skill-hint-calls.jsonl");

type BeforeAgentStartEvent = { prompt?: string };

async function appendCall(row: Record<string, unknown>): Promise<void> {
  try {
    await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
    await appendFile(CALL_LOG, JSON.stringify(row) + "\n", { mode: 0o600 });
  } catch {
    // Checkpointing never blocks the turn.
  }
}

export function createSkillHintHandler(roster: SkillEntry[], ask: ChoiceAsker) {
  return async (event: BeforeAgentStartEvent) => {
    const prompt = typeof event.prompt === "string" ? event.prompt : "";
    const result = await hintSkills({ prompt, roster, ask });
    await appendCall({
      ts: new Date().toISOString(),
      model: result.model,
      status: result.hint === null ? "silent" : "hinted",
      ...(result.hint === null ? { reason: result.reason } : { skill: result.skill, confidence: result.confidence, ...(result.usage ? { usage: result.usage } : {}) }),
      latencyMs: result.latencyMs,
      promptChars: prompt.length,
    });
    if (result.hint === null) return undefined;
    return {
      message: {
        customType: "jev-skill-hint",
        content: result.hint,
        details: { skill: result.skill, confidence: result.confidence, model: result.model },
        attribution: "jev-skill-hint",
      },
    };
  };
}

export default function jevSkillHintExtension(pi: { on: (event: string, handler: (event: BeforeAgentStartEvent) => Promise<unknown>) => void }) {
  useInfisicalKey();
  pi.on("before_agent_start", createSkillHintHandler(loadSkillRoster(), (options) => askJevChoice(options)));
}

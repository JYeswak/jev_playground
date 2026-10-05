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
import { randomUUID } from "node:crypto";
import { askJevChoice } from "../../kit/src/client.ts";
import { hintSkills, loadSkillRoster, warmTransport, type ChoiceAsker, type SkillEntry } from "../../kit/src/skill-hint.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const CALL_LOG = join(homedir(), ".local", "state", "jev", "skill-hint-calls.jsonl");
// One extension load serves one session process: shared checkpoint rows stay attributable.
const INSTANCE = randomUUID().slice(0, 8);

type BeforeAgentStartEvent = { prompt?: string };

async function appendCall(row: Record<string, unknown>): Promise<void> {
  try {
    await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
    await appendFile(CALL_LOG, JSON.stringify(row) + "\n", { mode: 0o600 });
  } catch {
    // Checkpointing never blocks the turn.
  }
}
type SkillHintPolicy = "off" | "on";
type SkillHintExtensionOptions = {
  policy?: SkillHintPolicy;
  ask?: ChoiceAsker;
  record?: typeof appendCall;
  roster?: SkillEntry[];
};
const DECLARED_POLICY: SkillHintPolicy = "off";


export function createSkillHintHandler(
  roster: SkillEntry[],
  ask: ChoiceAsker,
  options: { policy?: SkillHintPolicy; record?: typeof appendCall } = {},
) {
  const policy = options.policy ?? DECLARED_POLICY;
  const record = options.record ?? appendCall;
  return async (event: BeforeAgentStartEvent) => {
    if (policy === "off") return undefined;
    const prompt = typeof event.prompt === "string" ? event.prompt : "";
    const result = await hintSkills({ prompt, roster, ask });
    await record({
      ts: new Date().toISOString(),
      instance: INSTANCE,
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


export default function jevSkillHintExtension(
  pi: { on: (event: string, handler: (event: BeforeAgentStartEvent) => unknown) => void },
  options: SkillHintExtensionOptions = {},
) {
  const policy = options.policy ?? DECLARED_POLICY;
  const record = options.record ?? appendCall;
  if (policy === "on" && options.ask === undefined) useInfisicalKey();
  const ask: ChoiceAsker = options.ask ?? ((request) => askJevChoice(request));
  const roster = options.roster ?? (policy === "on" ? loadSkillRoster() : []);
  if (policy === "on") {
    // Warm the transport once per session without blocking any turn.
    pi.on("session_start", () => {
      void warmTransport(ask)
        .then((warmed) =>
          record({
            ts: new Date().toISOString(),
            instance: INSTANCE,
            model: warmed.model,
            status: "warmup",
            ...(warmed.ok ? { ...(warmed.usage ? { usage: warmed.usage } : {}) } : { reason: warmed.reason }),
            latencyMs: warmed.latencyMs,
            promptChars: 0,
          }),
        )
        .catch(() => undefined);
    });
  }
  pi.on("before_agent_start", createSkillHintHandler(roster, ask, { policy, record }));
}

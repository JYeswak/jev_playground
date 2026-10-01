/** Per-prompt skill hint (bead jev-4nyy): lexical shortlist, then one Jev Choice.
 *
 * About 760 skills are listed in every session; 84 of 160 sampled sessions read
 * any skill. This module shortlists (<= 20) by token overlap over skill
 * name+description, then asks one Choice (plus 'none') over the shortlist and
 * returns a 'Likely relevant skills: ...' hint when confidence >= 0.5.
 * Fail open everywhere: no shortlist, a refused answer, 'none', or low
 * confidence all yield hint null and the turn proceeds unchanged.
 */
import { basename, join } from "node:path";
import { readdirSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import type { AskChoiceOptions, JevChoiceResult } from "./client.ts";

export const SKILL_HINT_MODEL = "jev-1.13.0";
export const SKILL_HINT_CONFIDENCE_CUT = 0.5;
export const SKILL_HINT_SHORTLIST_MAX = 20;
export const SKILL_HINT_NONE = "none";
export const SKILL_HINT_TIMEOUT_MS = 300;

export type SkillEntry = { name: string; description: string };
export type ChoiceAsker = (options: AskChoiceOptions) => Promise<JevChoiceResult>;

export type HintResult =
  | { hint: string; skill: string; confidence: number; model: string; latencyMs: number; usage?: { input_tokens: number; output_tokens: number } }
  | { hint: null; reason: string; model: string; latencyMs: number };

function tokens(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .filter((word) => word.length > 2),
  );
}

/** Rank the roster by prompt-token overlap; ties break alphabetically for determinism. */
export function shortlistSkills(prompt: string, roster: SkillEntry[], max: number = SKILL_HINT_SHORTLIST_MAX): SkillEntry[] {
  const words = tokens(prompt);
  if (words.size === 0) return [];
  const scored = [] as { entry: SkillEntry; score: number }[];
  for (const entry of roster) {
    const haystack = tokens(entry.name + " " + entry.description);
    let score = 0;
    for (const word of words) if (haystack.has(word)) score += 1;
    // A name hit counts double: the name is the densest signal in the roster.
    const nameWords = tokens(entry.name);
    for (const word of words) if (nameWords.has(word)) score += 1;
    if (score > 0) scored.push({ entry, score });
  }
  scored.sort((a, b) => b.score - a.score || (a.entry.name < b.entry.name ? -1 : 1));
  return scored.slice(0, max).map((row) => row.entry);
}

function frontmatterField(text: string, field: string): string {
  const match = new RegExp('^' + field + ':\\s*(.*?)\\s*$', 'm').exec(text);
  if (!match) return "";
  const first = match[1];
  // Folded (>) and literal (|) scalars: gather the indented continuation lines.
  if (/^[>|][-+]?$/.test(first)) {
    const lines = text.slice(match.index + match[0].length).split("\n").slice(1);
    const body: string[] = [];
    for (const line of lines) {
      if (!/^[ \t]/.test(line) || line.trim() === "---") break;
      body.push(line.trim());
    }
    return body.join(first.startsWith("|") ? "\n" : " ");
  }
  return first.replace(/^["']|["']$/g, "");
}

/** Read name+description from every SKILL.md under dir. Never throws; [] on any failure. */
export function loadSkillRoster(dir: string = join(homedir(), ".claude", "skills")): SkillEntry[] {
  try {
    const roster: SkillEntry[] = [];
    for (const child of readdirSync(dir, { withFileTypes: true })) {
      if (!child.isDirectory()) continue;
      // readdir names are filesystem-controlled, not remote input, but never
      // join an unchecked segment: skip anything that could escape dir.
      if (child.name !== basename(child.name) || child.name.startsWith(".")) continue;
      try {
        const text = readFileSync(join(dir, child.name, "SKILL.md"), "utf8");
        roster.push({
          name: frontmatterField(text, "name") || child.name,
          description: frontmatterField(text, "description"),
        });
      } catch {
        continue;
      }
    }
    return roster;
  } catch {
    return [];
  }
}

export async function hintSkills(options: {
  prompt: string;
  roster: SkillEntry[];
  ask: ChoiceAsker;
  model?: string;
  confidenceCut?: number;
  timeoutMs?: number;
}): Promise<HintResult> {
  const model = options.model ?? SKILL_HINT_MODEL;
  const cut = options.confidenceCut ?? SKILL_HINT_CONFIDENCE_CUT;
  const prompt = options.prompt.trim().slice(0, 2000);
  if (!prompt) return { hint: null, reason: "empty-prompt", model, latencyMs: 0 };
  const short = shortlistSkills(prompt, options.roster);
  if (short.length === 0) return { hint: null, reason: "no-shortlist", model, latencyMs: 0 };
  const classes: Record<string, string | null> = {};
  for (const entry of short) classes[entry.name] = entry.description || null;
  classes[SKILL_HINT_NONE] = "No skill is relevant to this prompt; proceed without reading any skill.";
  const started = Date.now();
  const deadlineMs = options.timeoutMs ?? SKILL_HINT_TIMEOUT_MS;
  let answer: JevChoiceResult;
  try {
    answer = await options.ask({
      state: { prompt },
      instructions: "Which skill should the agent read before handling this prompt?",
      classes,
      model,
      timeoutMs: deadlineMs,
    });
  } catch (error) {
    const elapsed = Date.now() - started;
    const reason = elapsed >= deadlineMs - 60 ? "timeout" : error instanceof Error ? error.message : String(error);
    return { hint: null, reason, model, latencyMs: elapsed };
  }
  const latencyMs = Date.now() - started;
  if (!answer.ok) return { hint: null, reason: answer.reason, model: answer.model, latencyMs };
  if (answer.choice === SKILL_HINT_NONE || answer.confidence < cut) {
    return { hint: null, reason: answer.choice === SKILL_HINT_NONE ? "choice-none" : "low-confidence", model: answer.model, latencyMs };
  }
  const picked = short.find((entry) => entry.name === answer.choice);
  const blurb = picked?.description ? ' \u2014 ' + picked.description.slice(0, 160) : '';
  const usage = answer.usage ? { input_tokens: answer.usage.input_tokens, output_tokens: answer.usage.output_tokens } : undefined;
  return { hint: 'Likely relevant skills: ' + answer.choice + blurb, skill: answer.choice, confidence: answer.confidence, model: answer.model, latencyMs, ...(usage ? { usage } : {}) };
}

export type WarmResult =
  | { ok: true; model: string; latencyMs: number; usage?: { input_tokens: number; output_tokens: number } }
  | { ok: false; reason: string; model: string; latencyMs: number };

/** One tiny Choice at session start so the first real prompt reuses a warm transport. Fire and forget. */
export async function warmTransport(ask: ChoiceAsker, model: string = SKILL_HINT_MODEL): Promise<WarmResult> {
  const started = Date.now();
  try {
    const answer = await ask({
      state: { warm: 1 },
      instructions: "Answer warm.",
      classes: { warm: "The transport works.", cold: "The transport is cold." },
      model,
      timeoutMs: 5000,
    });
    const latencyMs = Date.now() - started;
    if (!answer.ok) return { ok: false, reason: answer.reason, model: answer.model, latencyMs };
    const usage = answer.usage ? { input_tokens: answer.usage.input_tokens, output_tokens: answer.usage.output_tokens } : undefined;
    return { ok: true, model: answer.model, latencyMs, ...(usage ? { usage } : {}) };
  } catch (error) {
    return { ok: false, reason: error instanceof Error ? error.message : String(error), model, latencyMs: Date.now() - started };
  }
}

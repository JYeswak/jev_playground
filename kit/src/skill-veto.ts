/** D9 verify-only veto (bead jev-wbel): shadow + enforce logic for skill loads.
 *
 * On a skill read (a skill-protocol URL or a SKILL.md file read), one fits-Noul
 * decides whether the load fits the request. Shadow mode only logs would-veto rows
 * and never blocks. Fail open everywhere: no match, refused/invalid answer, timeout,
 * error, missing key, or reached daily cap all yield veto=false and the load proceeds.
 *
 * Exact preregistered shape (PREREG-d9.md): single Noul, cut 0.40, fail-open allow.
 */

import { createHash } from "node:crypto";

export const SKILL_VETO_MODEL = "jev-1.13.0";
export const SKILL_VETO_NOUL_CUT = 0.40;
export const SKILL_VETO_TIMEOUT_MS = 20000;
export const SKILL_VETO_CAP_PER_DAY = 100;
export const SKILL_VETO_PROMPT_MAX = 2000;

export type NoulAsker = (options: {
  model: string;
  state: Record<string, unknown>;
  questions: Record<string, string>;
  timeoutMs: number;
}) => Promise<{
  ok: boolean;
  scores?: Record<string, number>;
  latencyMs: number;
  model: string;
  usage?: VetoUsage;
  reason?: string;
}>;

export type VetoResult =
  | { vetoed: boolean; noul: number; reason: string; latencyMs: number; model: string; usage?: VetoUsage }
  | { vetoed: false; noul: null; reason: string; latencyMs: number; model: string; usage?: VetoUsage };

export type VetoUsage = { input_tokens: number; output_tokens: number };
const FAKE_PREFIXES = ["/tmp/", "/var/folders/", "/private-tmp", "/private/var/folders"];

/** True for skill loads: skill://<name>[/...] or a SKILL.md read outside fixture dirs. */
export function isSkillReadPath(path: unknown): boolean {
  if (typeof path !== "string" || path.length === 0) return false;
  if (path.startsWith("skill://")) {
    const rest = path.slice("skill://".length);
    return rest.length > 0 && !rest.startsWith("/") && !rest.includes("..");
  }
  if (!path.endsWith("/SKILL.md")) return false;
  for (const p of FAKE_PREFIXES) if (path.startsWith(p)) return false;
  return true;
}


/** Exact preregistered question wording (demos/skill-suggest/demo.mjs:53). */
export function fitsQuestion(skill: string, description: string): string {
  return `Does the skill '${skill}' do the specific thing the user's request asks for? It is described as: ${description}`;
}

export function decideVeto(noul: number): boolean {
  return Number.isFinite(noul) && noul < SKILL_VETO_NOUL_CUT;
}

/** Skill name from a matched path: skill://<name>[/...] (namespaced a/b kept whole,
 * trailing filenames dropped) or the parent dir name of a SKILL.md file. */
export function skillNameFromPath(path: string): string {
  if (path.startsWith("skill://")) {
    const segs = path.slice("skill://".length).split("/").filter(Boolean);
    if (segs.length > 1 && segs[segs.length - 1].includes(".")) segs.pop();
    return segs.slice(0, 2).join("/");
  }
  const parts = path.split("/").filter(Boolean);
  return parts.length >= 2 ? parts[parts.length - 2] : path;
}

export function requestHash(prompt: string): string {
  return createHash("sha256").update(prompt, "utf8").digest("hex").slice(0, 16);
}
export async function vetoCheck(options: {
  prompt: string;
  skill: string;
  description: string;
  ask: NoulAsker;
}): Promise<VetoResult> {
  const started = Date.now();
  try {
    const res = await options.ask({
      model: SKILL_VETO_MODEL,
      state: { request: options.prompt.slice(0, SKILL_VETO_PROMPT_MAX) },
      questions: { fits: fitsQuestion(options.skill, options.description) },
      timeoutMs: SKILL_VETO_TIMEOUT_MS,
    });
    const latencyMs = Date.now() - started;
    if (!res.ok) {
      return { vetoed: false, noul: null, reason: `ask-${res.reason ?? "error"}`, latencyMs, model: res.model };
    }
    const noul = res.scores?.fits;
    if (typeof noul !== "number" || !Number.isFinite(noul)) {
      return { vetoed: false, noul: null, reason: "invalid-noul", latencyMs, model: res.model };
    }
    return {
      vetoed: decideVeto(noul),
      noul,
      reason: decideVeto(noul) ? "fits-below-cut" : "fits-at-or-above-cut",
      latencyMs,
      model: res.model,
      ...(res.usage ? { usage: res.usage } : {}),
    };
  } catch (err) {
    return { vetoed: false, noul: null, reason: `throw:${String(err).slice(0, 80)}`, latencyMs: Date.now() - started, model: SKILL_VETO_MODEL };
  }
}

import { createHash } from "node:crypto";
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

export type PlattMap = {
  kind: "platt-logit";
  target: "p_choice" | "noul";
  a: number;
  b: number;
  clip: number;
};

export type ClefCalibration = {
  schema: "jev.clef-calibration.v1";
  task_id: string;
  version: number;
  primitive: "choice" | "noul";
  question_key: string;
  question_sha256: string;
  model: {
    id: "clef-flash";
    joint_head_sha256: string;
    index_sha256: string;
  };
  map: PlattMap;
  fit: Record<string, unknown>;
  receipt: {
    prereg_commit: string;
    result_commit: string;
    verdict: "PASS";
    [key: string]: unknown;
  };
};

export type ModelFingerprint = Pick<ClefCalibration["model"], "joint_head_sha256" | "index_sha256">;

const DEFAULT_CALIBRATION_DIR = fileURLToPath(new URL("../calibration/clef/", import.meta.url));
const HEX = "0123456789abcdef";

function isSha256(value: unknown): value is string {
  return typeof value === "string" && value.length === 64 && [...value].every((char) => HEX.includes(char.toLowerCase()));
}

function isCommit(value: unknown): value is string {
  return typeof value === "string" && value.length >= 7 && value.length <= 40 && [...value].every((char) => HEX.includes(char.toLowerCase()));
}

function stableValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value !== null && typeof value === "object") {
    const object = value as Record<string, unknown>;
    return Object.fromEntries(Object.keys(object).sort().map((key) => [key, stableValue(object[key])]));
  }
  return value;
}

/** Hash the canonical question schema and the state keys it was calibrated against. */
export function questionSha(question: unknown, stateKeys: readonly string[]): string {
  if (!Array.isArray(stateKeys) || stateKeys.length === 0 || !stateKeys.every((key) => typeof key === "string" && key.length > 0)) {
    throw new TypeError("stateKeys must be a non-empty list of strings");
  }
  if (question === undefined) throw new TypeError("question must be JSON-serializable");
  const body = JSON.stringify({ question: stableValue(question), state_keys: [...stateKeys].sort() });
  if (body === undefined) throw new TypeError("question must be JSON-serializable");
  return createHash("sha256").update(body, "utf8").digest("hex");
}

/** Fingerprint the exact model file bytes used by the local Clef server. */
export async function fingerprintWeights(directory: string): Promise<ModelFingerprint> {
  const [jointHead, index] = await Promise.all([
    readFile(join(directory, "joint_head.safetensors")),
    readFile(join(directory, "model.safetensors.index.json")),
  ]);
  return {
    joint_head_sha256: createHash("sha256").update(jointHead).digest("hex"),
    index_sha256: createHash("sha256").update(index).digest("hex"),
  };
}

export function plattMap(probability: number, map: Pick<PlattMap, "a" | "b" | "clip">): number {
  if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) {
    throw new TypeError("probability must be finite and in [0,1]");
  }
  if (!Number.isFinite(map.a) || !Number.isFinite(map.b) || !Number.isFinite(map.clip) || map.clip <= 0 || map.clip >= 0.5) {
    throw new TypeError("Platt map must contain finite coefficients and a clip in (0,0.5)");
  }
  const p = Math.min(Math.max(probability, map.clip), 1 - map.clip);
  return 1 / (1 + Math.exp(-(map.a * Math.log(p / (1 - p)) + map.b)));
}

function validCalibration(value: unknown, filename: string): value is ClefCalibration {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const candidate = value as Record<string, unknown>;
  if (candidate.schema !== "jev.clef-calibration.v1") return false;
  if (typeof candidate.task_id !== "string" || !candidate.task_id || !Number.isSafeInteger(candidate.version) || (candidate.version as number) < 1) return false;
  if (filename !== `${candidate.task_id}.v${candidate.version}.json`) return false;
  if (candidate.primitive !== "choice" && candidate.primitive !== "noul") return false;
  if (typeof candidate.question_key !== "string" || !candidate.question_key || !isSha256(candidate.question_sha256)) return false;
  if (candidate.model === null || typeof candidate.model !== "object" || Array.isArray(candidate.model)) return false;
  const model = candidate.model as Record<string, unknown>;
  if (model.id !== "clef-flash" || !isSha256(model.joint_head_sha256) || !isSha256(model.index_sha256)) return false;
  if (candidate.map === null || typeof candidate.map !== "object" || Array.isArray(candidate.map)) return false;
  const map = candidate.map as Record<string, unknown>;
  if (map.kind !== "platt-logit" || typeof map.a !== "number" || !Number.isFinite(map.a) || typeof map.b !== "number" || !Number.isFinite(map.b)) return false;
  if (typeof map.clip !== "number" || !Number.isFinite(map.clip) || map.clip <= 0 || map.clip >= 0.5) return false;
  if (candidate.primitive === "choice" && map.target !== "p_choice") return false;
  if (candidate.primitive === "noul" && map.target !== "noul") return false;
  if (candidate.fit === null || typeof candidate.fit !== "object" || Array.isArray(candidate.fit)) return false;
  if (candidate.receipt === null || typeof candidate.receipt !== "object" || Array.isArray(candidate.receipt)) return false;
  const receipt = candidate.receipt as Record<string, unknown>;
  if (receipt.verdict !== "PASS" || !isCommit(receipt.prereg_commit) || !isCommit(receipt.result_commit)) return false;
  return true;
}

/** Load only structurally valid, versioned calibration files; malformed files fail closed. */
export async function loadCalibrations(directory = DEFAULT_CALIBRATION_DIR): Promise<ClefCalibration[]> {
  let names: string[];
  try {
    names = await readdir(directory);
  } catch (error) {
    if (error !== null && typeof error === "object" && "code" in error && error.code === "ENOENT") return [];
    throw error;
  }
  const calibrations: ClefCalibration[] = [];
  const seen = new Set<string>();
  for (const name of names.filter((candidate) => candidate.endsWith(".json")).sort()) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(await readFile(join(directory, name), "utf8"));
    } catch {
      continue;
    }
    if (!validCalibration(parsed, name) || seen.has(parsed.task_id)) continue;
    seen.add(parsed.task_id);
    calibrations.push(parsed);
  }
  return calibrations;
}

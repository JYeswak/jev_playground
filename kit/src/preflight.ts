export const SIZE_LIMIT_TOKENS = 32_768;
export const SIZE_BAND = Object.freeze({
  lowBytesPerToken: 1.4794769192690072,
  highBytesPerToken: 2.0819124038783015,
});

export type SizeStatus = "FITS" | "NEAR" | "OVER";
export type SizePreflightResult = {
  status: SizeStatus;
  stateBytes: number;
  questionBytes: number;
  totalBytes: number;
  limitTokens: number;
  estimatedTokensAtLowRatio: number;
  estimatedTokensAtHighRatio: number;
};

export class PreflightError extends Error {
  readonly code: "size-over" | "size-near" | "choice-options" | "offered-option";
  readonly status?: SizeStatus;

  constructor(
    code: "size-over" | "size-near" | "choice-options" | "offered-option",
    message: string,
    status?: SizeStatus,
  ) {
    super(message);
    this.name = "PreflightError";
    this.code = code;
    this.status = status;
  }
}

export function compactJsonBytes(value: unknown): number {
  const encoded = JSON.stringify(value);
  if (encoded === undefined) throw new TypeError("value is not JSON-serializable");
  return new TextEncoder().encode(encoded).byteLength;
}

export function classifySizeBytes(
  stateBytes: number,
  questionBytes: number,
  limitTokens = SIZE_LIMIT_TOKENS,
): SizeStatus {
  if (!Number.isInteger(stateBytes) || stateBytes < 0) throw new TypeError("stateBytes must be a non-negative integer");
  if (!Number.isInteger(questionBytes) || questionBytes < 0) throw new TypeError("questionBytes must be a non-negative integer");
  const totalBytes = stateBytes + questionBytes;
  if (totalBytes / SIZE_BAND.lowBytesPerToken <= limitTokens) return "FITS";
  if (totalBytes / SIZE_BAND.highBytesPerToken > limitTokens) return "OVER";
  return "NEAR";
}

export function sizePreflightBytes(
  stateBytes: number,
  questionBytes: number,
  options: { allowNear?: boolean; limitTokens?: number } = {},
): SizePreflightResult {
  const limitTokens = options.limitTokens ?? SIZE_LIMIT_TOKENS;
  const totalBytes = stateBytes + questionBytes;
  const status = classifySizeBytes(stateBytes, questionBytes, limitTokens);
  const result: SizePreflightResult = {
    status,
    stateBytes,
    questionBytes,
    totalBytes,
    limitTokens,
    estimatedTokensAtLowRatio: totalBytes / SIZE_BAND.lowBytesPerToken,
    estimatedTokensAtHighRatio: totalBytes / SIZE_BAND.highBytesPerToken,
  };
  if (status === "OVER") {
    throw new PreflightError("size-over", `request is OVER the ${limitTokens}-token input limit`, status);
  }
  if (status === "NEAR" && options.allowNear !== true) {
    throw new PreflightError("size-near", "request is NEAR the input limit; pass allowNear: true explicitly", status);
  }
  return result;
}

export function sizePreflight(
  state: unknown,
  questions: unknown,
  options: { allowNear?: boolean; limitTokens?: number } = {},
): SizePreflightResult {
  return sizePreflightBytes(compactJsonBytes(state), compactJsonBytes(questions), options);
}

function questionOptions(question: unknown): string[] {
  if (!question || typeof question !== "object" || Array.isArray(question)) return [];
  const candidate = question as Record<string, unknown>;
  const raw = candidate.criteria ?? candidate.options ?? candidate.classes;
  if (Array.isArray(raw)) return raw.filter((value): value is string => typeof value === "string");
  if (raw && typeof raw === "object") return Object.keys(raw);
  return [];
}

export function optionsPreflight(question: unknown): string[] {
  if (!question || typeof question !== "object" || Array.isArray(question)) {
    throw new PreflightError("choice-options", "question must be an object");
  }
  const candidate = question as Record<string, unknown>;
  if (candidate.type !== "choice") return questionOptions(question);
  const options = questionOptions(question);
  if (options.length < 2) {
    throw new PreflightError("choice-options", `a Choice question needs at least 2 options, got ${options.length}`);
  }
  return options;
}

export function offeredPreflight(question: unknown, expectedId?: string): string[] {
  const options = optionsPreflight(question);
  if (expectedId !== undefined && !options.includes(expectedId)) {
    throw new PreflightError("offered-option", `solving option ${JSON.stringify(expectedId)} was not offered`);
  }
  return options;
}

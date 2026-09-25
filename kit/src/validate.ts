export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

type RecordValue = Record<string, unknown>;

function asRecord(value: unknown, label: string): RecordValue {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new ValidationError(`${label} must be an object`);
  }
  return value as RecordValue;
}

function finiteProbability(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
    throw new ValidationError(`${label} must be finite and in [0,1]`);
  }
  return value;
}

function checkDistribution(probabilities: RecordValue, ids: readonly string[]): Record<string, number> {
  const actual = Object.keys(probabilities).sort();
  const expected = [...ids].sort();
  if (actual.length !== expected.length || actual.some((key, index) => key !== expected[index])) {
    throw new ValidationError("probabilities keys must exactly match offered ids");
  }
  const output: Record<string, number> = {};
  let sum = 0;
  for (const id of ids) {
    const value = finiteProbability(probabilities[id], `probabilities.${id}`);
    output[id] = value;
    sum += value;
  }
  if (Math.abs(sum - 1) >= 0.02) throw new ValidationError(`probabilities sum to ${sum}, expected 1 ± 0.02`);
  return output;
}

export function validateNoulAnswer(answer: unknown): number {
  const record = asRecord(answer, "noul answer");
  return finiteProbability(record.noul, "noul");
}

export type ValidatedChoice = {
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
};

export function validateChoiceAnswer(answer: unknown, ids: readonly string[]): ValidatedChoice {
  if (ids.length < 2) throw new ValidationError("Choice requires at least 2 ids");
  const record = asRecord(answer, "choice answer");
  if (typeof record.choice !== "string" || !ids.includes(record.choice)) {
    throw new ValidationError("choice must be one of the offered ids");
  }
  const confidence = finiteProbability(record.confidence, "confidence");
  const probabilities = checkDistribution(asRecord(record.probabilities, "probabilities"), ids);
  const maximum = Math.max(...Object.values(probabilities));
  if (probabilities[record.choice] < maximum - 1e-6) {
    throw new ValidationError("choice probability must be within 1e-6 of the maximum");
  }
  return { choice: record.choice, confidence, probabilities };
}

export type ValidatedScore = {
  score: number;
  confidence: number;
  legend: Record<string, string>;
  probabilities: Record<string, number>;
};

export function validateScoreAnswer(answer: unknown, criteria: readonly string[]): ValidatedScore {
  if (criteria.length < 2) throw new ValidationError("Score requires at least 2 criteria");
  const record = asRecord(answer, "score answer");
  if (typeof record.score !== "number" || !Number.isFinite(record.score)) {
    throw new ValidationError("score must be finite");
  }
  const confidence = finiteProbability(record.confidence, "confidence");
  const ids = criteria.map((_, index) => String(index));
  const probabilities = checkDistribution(asRecord(record.probabilities, "probabilities"), ids);
  const legendRecord = asRecord(record.legend, "legend");
  const legend: Record<string, string> = {};
  for (const id of ids) {
    if (typeof legendRecord[id] !== "string") throw new ValidationError(`legend.${id} must be a string`);
    legend[id] = legendRecord[id] as string;
  }
  return { score: record.score, confidence, legend, probabilities };
}

function questionType(question: unknown): string {
  const record = asRecord(question, "question");
  if (typeof record.type !== "string") throw new ValidationError("question.type must be a string");
  return record.type;
}

function questionIds(question: unknown): string[] {
  const record = asRecord(question, "question");
  const criteria = record.criteria;
  if (!criteria || typeof criteria !== "object" || Array.isArray(criteria)) {
    throw new ValidationError("Choice criteria must be a map");
  }
  return Object.keys(criteria);
}

function questionCriteria(question: unknown): string[] {
  const record = asRecord(question, "question");
  if (!Array.isArray(record.criteria) || record.criteria.some((value) => typeof value !== "string")) {
    throw new ValidationError("Score criteria must be a string list");
  }
  return record.criteria as string[];
}

export function validateBundleAnswers(
  questions: Record<string, unknown>,
  answers: unknown,
): Record<string, unknown> {
  const answerRecord = asRecord(answers, "answers");
  for (const [key, question] of Object.entries(questions)) {
    if (!(key in answerRecord)) throw new ValidationError(`missing answer ${key}`);
    const answer = answerRecord[key];
    const type = questionType(question);
    if (type === "noul") validateNoulAnswer(answer);
    else if (type === "choice") validateChoiceAnswer(answer, questionIds(question));
    else if (type === "score") validateScoreAnswer(answer, questionCriteria(question));
    else throw new ValidationError(`unsupported question type ${type}`);
  }
  return answerRecord;
}

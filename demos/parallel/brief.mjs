/**
 * Fixture parallel briefing (cookbook shape, FIXTURE SCORING).
 * One document, four questions of three types, answered from a recorded
 * answer map — the shape of one TypeSafe call carrying a whole briefing.
 * The cookbook's finding (batching changes cost and speed, not answers) is
 * structural: a single request object holds every question.
 */
export const DOC = [
  "The General Data Protection Regulation (EU) 2016/679 took effect in 2018.",
  "Personal data breaches must be reported within 72 hours.",
  "Consent requires a clear affirmative act; silence is not consent.",
  "It is an EU regulation: directly binding in all member states.",
].join(" ");

export const QUESTIONS = {
  breach_72h: { type: "noul", instructions: "Must a personal data breach be reported within 72 hours?" },
  preticked_ok: { type: "noul", instructions: "Can valid consent come from pre-ticked boxes?" },
  instrument: { type: "choice", instructions: "What kind of EU instrument is it?",
    criteria: { Regulation: "directly binding", Directive: "implemented nationally", Treaty: "between states" } },
  scope: { type: "score", instructions: "How broad is its territorial scope?",
    criteria: ["one country", "the EU", "worldwide"] },
};

// Recorded answers: the fixture a live call would have to reproduce.
const RECORDED = {
  breach_72h: { type: "noul", noul: 0.97 },
  preticked_ok: { type: "noul", noul: 0.04 },
  instrument: { type: "choice", choice: "Regulation",
    confidence: 0.93, probabilities: { Regulation: 0.93, Directive: 0.05, Treaty: 0.02 } },
  scope: { type: "score", score: 1, confidence: 0.81,
    legend: { 0: "one country", 1: "the EU", 2: "worldwide" },
    probabilities: { 0: 0.02, 1: 0.17, 2: 0.81 } },
};

export function brief() {
  return Object.entries(QUESTIONS).map(([id, q]) => ({ id, type: q.type, answer: RECORDED[id] }));
}

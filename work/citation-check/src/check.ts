/**
 * Citation entailment — the official TypeSafe cookbook, in our code.
 *
 * Source: docs-mirror/typesafe/cookbooks/citation_check.md
 * (jev-1.12, 2026-08-16; question shape copied, not invented).
 *
 * A string match catches a quote that is not in the source. That is `fabricated`,
 * and no model is called. A quote that is present can still sit under a claim the
 * section does not support. That judgment is a Choice question. The application
 * owns the threshold: confidence >= 0.8 stands; below that, a human reviews.
 *
 * Fail-safe, named: a missing key, a transport error, a hostile label, or a
 * non-finite confidence is `unjudged` / `review`. Never `verified`. Never `auto`.
 * A crashed classifier must not read as a clean citation.
 */

export const AUTO_ACCEPT = 0.8;

export const INSTRUCTIONS = "How does the section relate to the claim?";

export const CRITERIA = {
  supports: "The section states the claim or directly implies that it is true",
  contradicts: "The section states the opposite of the claim or implies it is false",
  says_nothing: "The section does not address what the claim asserts, either way",
} as const;

export const RELATION_TO_VERDICT = {
  supports: "verified",
  contradicts: "contradicted",
  says_nothing: "unsupported",
} as const;

export type Relation = keyof typeof RELATION_TO_VERDICT;
export type CookbookVerdict = (typeof RELATION_TO_VERDICT)[Relation];
export type Verdict = CookbookVerdict | "fabricated" | "unjudged";
export type LocateStatus = "found" | "missing" | "section-only";

/** Whole source is the section up to this many normalized characters. Above it, a window. */
export const SECTION_CAP = 12_000;
const WINDOW_RADIUS = 2_000;

export type Citation = {
  claim: string;
  /** null / omitted: no quote to match; the section is judged directly. */
  quote?: string | null;
};

export type ChoiceAnswer =
  | { ok: true; choice: string; confidence: number }
  | { ok: false; reason: string };

export type Asker = (state: { claim: string; section: string }) => Promise<ChoiceAnswer>;

export type CheckResult = {
  verdict: Verdict;
  action: "auto" | "review";
  confidence: number | null;
  status: LocateStatus;
  relation: Relation | null;
  calledModel: boolean;
  reason?: string;
};

export function normalize(text: string): string {
  const folded = text.replaceAll("“", '"').replaceAll("”", '"').replaceAll("‘", "'").replaceAll("’", "'");
  return folded.replace(/\s+/g, " ").trim();
}

export function locate(source: string, quote: string | null | undefined): { status: LocateStatus; section: string | null } {
  if (quote === null || quote === undefined || normalize(quote) === "") {
    return { status: "section-only", section: capSection(source, null) };
  }
  const needle = normalize(quote);
  const hay = normalize(source);
  const at = hay.indexOf(needle);
  if (at < 0) return { status: "missing", section: null };
  return { status: "found", section: capSection(source, needle) };
}

function capSection(source: string, needle: string | null): string {
  const hay = normalize(source);
  if (hay.length <= SECTION_CAP) return source;
  if (!needle) return source.slice(0, SECTION_CAP);
  const at = hay.indexOf(needle);
  if (at < 0) return source.slice(0, SECTION_CAP);
  const start = Math.max(0, at - WINDOW_RADIUS);
  const end = Math.min(hay.length, at + needle.length + WINDOW_RADIUS);
  return hay.slice(start, end);
}

export function fold(status: LocateStatus, answer: ChoiceAnswer | null, calledModel: boolean): CheckResult {
  if (status === "missing") {
    return {
      verdict: "fabricated",
      action: "auto",
      confidence: null,
      status,
      relation: null,
      calledModel: false,
    };
  }
  if (!answer || !answer.ok) {
    return {
      verdict: "unjudged",
      action: "review",
      confidence: null,
      status,
      relation: null,
      calledModel,
      reason: answer && !answer.ok ? answer.reason : "no-answer",
    };
  }
  if (!(answer.choice in RELATION_TO_VERDICT)) {
    return {
      verdict: "unjudged",
      action: "review",
      confidence: null,
      status,
      relation: null,
      calledModel,
      reason: "hostile-label",
    };
  }
  if (!Number.isFinite(answer.confidence) || answer.confidence < 0 || answer.confidence > 1) {
    return {
      verdict: "unjudged",
      action: "review",
      confidence: null,
      status,
      relation: null,
      calledModel,
      reason: "non-finite-confidence",
    };
  }
  const relation = answer.choice as Relation;
  return {
    verdict: RELATION_TO_VERDICT[relation],
    action: answer.confidence >= AUTO_ACCEPT ? "auto" : "review",
    confidence: answer.confidence,
    status,
    relation,
    calledModel,
  };
}

export async function checkCitation(source: string, citation: Citation, asker: Asker): Promise<CheckResult> {
  if (normalize(citation.claim) === "") {
    return {
      verdict: "unjudged",
      action: "review",
      confidence: null,
      status: "section-only",
      relation: null,
      calledModel: false,
      reason: "empty-claim",
    };
  }
  const located = locate(source, citation.quote);
  if (located.section === null) return fold("missing", null, false);
  let answer: ChoiceAnswer;
  try {
    answer = await asker({ claim: citation.claim, section: located.section });
  } catch {
    return fold(located.status, { ok: false, reason: "asker-error" }, true);
  }
  return fold(located.status, answer, true);
}

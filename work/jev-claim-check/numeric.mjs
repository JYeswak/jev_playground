// numeric.mjs (bead jev-2mp, the R83 retry): check every number in a claim on its own, asking
// whether the evidence states EXACTLY that value.
//
//   node work/jev-claim-check/numeric.mjs --build   writes numeric-cases.jsonl (no key, no network)
//   node work/jev-claim-check/numeric.mjs --run     live, numeric-cases.jsonl -> numeric-rows.jsonl (resumes)
// Key: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node ...
// Re-score with no key: python3 work/jev-claim-check/score-numeric.py
//
// THE RULES (committed with the bar in docs/demos/upstream-repro/claim-check-numeric-20260924.md):
// SETS. readme = the 19 true rows of cases.jsonl (jev-sp5), close = the 34 real rows of
//   close-cases.jsonl that carry evidence (jev-10t). Claim and evidence are taken verbatim from those
//   frozen files.
// NUMBERS. numberTokens() of check-close.mjs over the claim with file/commit/date/time spans
//   blanked (references()), minus tokens with a run of 8 or more digits. Bare 0 and 1 are checked.
// CLAUSE for a number: split the claim at whitespace after ". ! ?", at "; ", ", ", " (" and ")",
//   take the unit holding the number, and while it has fewer than 4 words, prepend the unit before;
//   leading ", ; )" and spaces are trimmed.
// CHECK = one Noul over state {clause, value, evidence} with QUESTION below. Identical
//   (clause, value) pairs in one claim are asked once. Verdict per check: the tool's cuts
//   (supported p>=0.8, unsupported p<=0.2, else unsure). Whole claim: supported if every check is
//   supported, unsupported if any is unsupported, else unsure; a check with no verdict is unsure.
// PLANT (fresh, seed 20260925, mulberry32, one draw per claim, readme set first, file order):
//   eligible = tokens other than a bare 0 or 1, no 8-digit run. Draw uniformly among eligible tokens
//   that occur literally in the evidence; if none, among all eligible (flagged inEvidence=false);
//   none at all, no plant. In the drawn token, the first digit run that is not all zeros has its
//   LAST digit d replaced by 4 if d=0, else ((d+3) mod 9)+1 (1->5 ... 5->9, 6->1 ... 9->4). The
//   build refuses a plant equal to any jev-10t plant claim or jev-10t diagnostic clause. A planted
//   claim's checks whose (clause, value) equal a real check reuse that real answer; only changed
//   checks are asked.
import { appendFileSync, existsSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { askJev } from "../jev-client/src/index.ts";
import { classify } from "../../.omp/tools/jev-claim-check.ts";
import { numberTokens, references } from "./check-close.mjs";

const HERE = new URL(".", import.meta.url);
const CASES = new URL("numeric-cases.jsonl", HERE);
const ROWS = new URL("numeric-rows.jsonl", HERE);
const SEED = 20260925;
const MODEL = "jev-1.13.0";
const VERDICTS = new Set(["supported", "unsupported", "unsure"]);

export const QUESTION = {
  instructions: "Does the evidence state the exact value `value` for what `clause` says it measures?",
  criteria: {
    true: "The evidence states this same value for this quantity. A shorter rounding of the evidence's value, or the same value written as a fraction, percent or decimal, also counts",
    false: "The evidence gives a different value for this quantity, or does not state it",
  },
};

const lines = (url) => readFileSync(url, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));

export function mulberry32(a) {
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function clauseAt(claim, at) {
  const cuts = [0];
  for (const m of claim.matchAll(/(?<=[.!?])\s+|;\s+|,\s+|\s+\(|\)/g)) cuts.push(m.index, m.index + m[0].length);
  cuts.push(claim.length);
  const units = [];
  for (let i = 0; i < cuts.length; i += 2) units.push([cuts[i], cuts[i + 1]]);
  let k = units.findIndex(([a, b]) => at >= a && at < b);
  if (k < 0) k = units.length - 1;
  let start = units[k][0];
  const end = units[k][1];
  while (claim.slice(start, end).trim().split(/\s+/).length < 4 && k > 0) start = units[--k][0];
  return claim.slice(start, end).replace(/^[\s,;)]+/, "").trim();
}

function checksFor(claim) {
  const { blanked } = references(claim);
  const seen = new Set();
  const out = [];
  for (const t of numberTokens(blanked)) {
    if (/\d{8,}/.test(t.text)) continue;
    const clause = clauseAt(claim, t.at);
    const key = `${clause}\u0000${t.text}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ value: t.text, clause, at: t.at });
  }
  return out;
}

export function mutate(token) {
  const runs = [...token.matchAll(/\d+/g)].filter((m) => /[1-9]/.test(m[0]));
  const run = runs[0];
  const i = run.index + run[0].length - 1;
  const d = Number(token[i]);
  return token.slice(0, i) + String(d === 0 ? 4 : ((d + 3) % 9) + 1) + token.slice(i + 1);
}

function build() {
  const forbiddenClaims = new Set(lines(new URL("close-cases.jsonl", HERE)).filter((c) => !c.truth).map((c) => c.claim));
  const forbiddenClauses = new Set(lines(new URL("close-atomic-diagnostic.jsonl", HERE)).map((c) => c.claim));
  const sets = [
    ["readme", lines(new URL("cases.jsonl", HERE)).filter((c) => c.truth).map((c) => ({ key: c.label, claim: c.claim, evidence: c.evidence }))],
    ["close", lines(new URL("close-cases.jsonl", HERE)).filter((c) => c.truth && c.evidence).map((c) => ({ key: c.bead, claim: c.claim, evidence: c.evidence }))],
  ];
  const rand = mulberry32(SEED);
  const cases = [];
  for (const [set, items] of sets) {
    for (const it of items) {
      const realChecks = checksFor(it.claim);
      cases.push({ id: `${set}:${it.key}:real`, set, key: it.key, truth: true, claim: it.claim, evidence: it.evidence, checks: realChecks });
      const { blanked } = references(it.claim);
      const eligible = numberTokens(blanked).filter((t) => t.text !== "0" && t.text !== "1" && !/\d{8,}/.test(t.text));
      const inEv = eligible.filter((t) => it.evidence.includes(t.text));
      const pool = inEv.length ? inEv : eligible;
      const r = rand();
      if (!pool.length) continue;
      const pick = pool[Math.floor(r * pool.length)];
      const to = mutate(pick.text);
      const claim = it.claim.slice(0, pick.at) + to + it.claim.slice(pick.at + pick.text.length);
      const checks = checksFor(claim);
      const plantedClause = clauseAt(claim, pick.at);
      if (forbiddenClaims.has(claim) || forbiddenClauses.has(plantedClause)) throw new Error(`${it.key}: plant repeats a jev-10t plant or probe`);
      cases.push({
        id: `${set}:${it.key}:planted`, set, key: it.key, truth: false, claim, evidence: it.evidence, checks,
        plant: { from: pick.text, to, at: pick.at, inEvidence: inEv.length > 0, plantedClause, realClause: clauseAt(it.claim, pick.at) },
      });
    }
  }
  const blob = cases.map((c) => JSON.stringify(c)).join("\n") + "\n";
  writeFileSync(CASES, blob);
  const asked = new Set();
  for (const c of cases) for (const k of c.checks) asked.add(`${c.set}\u0000${c.key}\u0000${k.clause}\u0000${k.value}`);
  for (const set of ["readme", "close"]) {
    const cs = cases.filter((c) => c.set === set);
    console.log(`${set}: ${cs.filter((c) => c.truth).length} real, ${cs.filter((c) => !c.truth).length} planted (${cs.filter((c) => c.plant?.inEvidence).length} in evidence), real claims with no number ${cs.filter((c) => c.truth && !c.checks.length).length}`);
  }
  console.log(`distinct checks to ask: ${asked.size}; sha256 ${createHash("sha256").update(blob).digest("hex")}`);
  return 0;
}

async function run() {
  if (!process.env.TYPESAFE_API_KEY) {
    console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No call made.");
    return 2;
  }
  const done = new Map();
  if (existsSync(ROWS)) for (const r of lines(ROWS)) if (VERDICTS.has(r.verdict)) done.set(r.check, r);
  let failed = 0;
  for (const c of lines(CASES)) {
    for (const k of c.checks) {
      const check = `${c.set}\u0000${c.key}\u0000${k.clause}\u0000${k.value}`;
      if (done.has(check)) continue;
      const posted = await askJev({ state: { clause: k.clause, value: k.value, evidence: c.evidence }, questions: { exact: QUESTION }, model: MODEL, timeoutMs: 20000 });
      const p = posted.ok ? posted.scores.exact : null;
      const v = posted.ok ? classify(p) : null;
      const row = { check, set: c.set, key: c.key, clause: k.clause, value: k.value, verdict: v ? v.verdict : posted.ok ? "refused" : "not_run", probability: v ? p : null, reason: posted.ok ? null : posted.reason, latencyMs: posted.latencyMs ?? null, usage: posted.ok ? posted.usage ?? null : null, at: new Date().toISOString() };
      appendFileSync(ROWS, JSON.stringify(row) + "\n");
      if (VERDICTS.has(row.verdict)) done.set(check, row);
      else failed += 1;
      console.log(`${c.set}\t${c.key}\t${k.value}\t${row.verdict}\t${row.probability ?? "-"}`);
    }
  }
  console.log(failed ? `${failed} check(s) without a verdict; rerun to resume` : "all checks answered");
  return failed ? 3 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  const arg = process.argv[2];
  process.exit(arg === "--build" ? build() : arg === "--run" ? await run() : (console.error("usage: numeric.mjs --build | --run"), 64));
}

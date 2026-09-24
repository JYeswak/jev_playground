// numeric-v2.mjs (bead jev-h8s, R83 retry 2 and the LAST round of this design): exact number
// tokens, evidence narrowed per check to the lines that match the clause, 'unsure' = not confirmed.
//
//   node work/jev-claim-check/numeric-v2.mjs --build   writes numeric-v2-cases.jsonl (no key, no network)
//   node work/jev-claim-check/numeric-v2.mjs --run     live, -> numeric-v2-rows.jsonl (resumes)
// Key: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node ...
// Re-score with no key: python3 work/jev-claim-check/score-numeric-v2.py
//
// THE RULES (committed with the bar in docs/demos/upstream-repro/claim-check-numeric-v2-20260924.md).
// Unchanged from jev-2mp (numeric.mjs): the two sets and their frozen claims and evidence, the
// clause rule clauseAt(), the QUESTION and the cuts.
// TOKENS (numberTokensV2, unit-tested in numeric-v2.test.mjs): over the claim with file, commit,
//   date and time spans blanked (references()), a token is a digit run with optional ".d" and ","
//   parts, an optional exponent (e-13), an optional "-<number>" range, optional "/<number>" parts
//   and an optional "%". Trailing "." and "," are dropped. Skipped: a token touching a letter,
//   digit, "_" or "." on its left, or a letter, digit or "_" on its right; one after a
//   letter-hyphen (SST-5, top-1); a dotted version (1.13.0). Commas are thousands separators only
//   when every group after the first has exactly 3 digits (1,145 and 87,894); otherwise the token
//   is a list and splits at its commas (60,97,143,250 -> four tokens). Tokens with a run of 8 or
//   more digits are not checked.
// EVIDENCE per check (narrowEvidence): the case evidence is split into lines, and any line over
//   400 characters into consecutive 400-character pieces. Anchors come from the number's SENTENCE
//   (the claim split after ". ! ?" + whitespace and at "; ") with ALL its number tokens removed: its
//   words of 4+ letters minus STOPWORDS (lower-cased), plus the sentence's OTHER number tokens
//   (every token except the one at the checked position). The checked token is never an anchor, so
//   a planted value and its original get identical evidence (the build asserts it). Piece score =
//   distinct anchor words it contains (case-insensitive) + 2 x anchor numbers it contains
//   literally. The 8 best-scoring pieces with score >= 1 (ties: earlier first), each with the piece
//   before and after, in document order, joined by newlines, capped at 3,000 characters. No piece
//   scores: no evidence, no call, and the check is not confirmed. These settings (sentence, 8,
//   3,000) were chosen before any call by one measurement that needs no model: how often a REAL
//   number that occurs in the full evidence survives narrowing (clause/6/2,000: readme 36/41, close
//   78/103; sentence/8/3,000: 41/41 and 87/103).
// VERDICT per check: confirmed = supported (p >= 0.8). unsure and unsupported are both not
//   confirmed. A whole claim is confirmed when every check is.
// PLANTS (fresh): seed 20260926 (mulberry32), one draw per claim, readme set first, file order;
//   eligible = tokens other than a bare 0 or 1 with no 8-digit run, drawn uniformly among those
//   that occur in the full case evidence, else among all (inEvidence=false). mutateV2(): the
//   token's FIRST non-zero digit d becomes ((d+1) mod 9)+1 (1->3 ... 7->9, 8->1, 9->2). jev-10t moved
//   the same digit by +5 (mod 9) and jev-2mp moved the last digit of the first non-zero run by +4,
//   so a v2 plant never equals either on the same token.
//   A plant whose claim equals any jev-10t or jev-2mp plant claim, or whose clause equals a
//   jev-10t diagnostic clause, is redrawn (next random number), at most 20 times; the redraw count
//   is recorded.
import { appendFileSync, existsSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { askJev } from "../jev-client/src/index.ts";
import { classify } from "../../.omp/tools/jev-claim-check.ts";
import { references } from "./check-close.mjs";
import { QUESTION, clauseAt, mulberry32 } from "./numeric.mjs";

export function mutateV2(token) {
  const i = token.search(/[1-9]/);
  return token.slice(0, i) + String(((Number(token[i]) + 1) % 9) + 1) + token.slice(i + 1);
}

const HERE = new URL(".", import.meta.url);
const CASES = new URL("numeric-v2-cases.jsonl", HERE);
const ROWS = new URL("numeric-v2-rows.jsonl", HERE);
const SEED = 20260926;
const MODEL = "jev-1.13.0";
const PIECE = 400;
const TOP = 8;
const CAP = 3000;
export const STOPWORDS = new Set(("with from that this than into were have been each only over under against after before both same still when which where there their they these those none also just about through above below while what then them your ours here very more most less some such other same") .split(" "));

const lines = (url) => readFileSync(url, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));

const NUM = String.raw`\d[\d,.]*(?:[eE][-+]?\d+)?`;
const CHUNK = new RegExp(String.raw`(?<![A-Za-z0-9_.])(?<![A-Za-z]-)${NUM}(?:-${NUM})?(?:\/${NUM})*%?`, "g");
const THOUSANDS = /^\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][-+]?\d+)?%?$/;

export function numberTokensV2(blanked) {
  const out = [];
  for (const m of blanked.matchAll(CHUNK)) {
    const text = m[0].replace(/[.,]+$/, "");
    const at = m.index;
    const after = blanked[at + text.length] ?? "";
    if (/[A-Za-z0-9_]/.test(after)) continue;
    if (/^\d+\.\d+\.\d+/.test(text) && !text.includes("/")) continue;
    const parts = text.split(/\/|-(?=\d)/);
    if (parts.every((p) => !p.includes(",") || THOUSANDS.test(p))) {
      out.push({ text, at });
      continue;
    }
    let offset = 0;
    for (const piece of text.split(",")) {
      if (/\d/.test(piece)) out.push({ text: piece, at: at + offset });
      offset += piece.length + 1;
    }
  }
  return out.filter((t) => !/\d{8,}/.test(t.text));
}

function contentWords(text) {
  return [...new Set((text.toLowerCase().match(/[a-z][a-z_-]{3,}/g) ?? []).filter((w) => !STOPWORDS.has(w)))];
}

/** The sentence of `claim` holding offset `at`: [start, text]. Split after ". ! ?" + whitespace and at "; ". */
export function sentenceAt(claim, at) {
  let start = 0;
  let end = claim.length;
  for (const m of claim.matchAll(/(?<=[.!?])\s+|;\s+/g)) {
    if (m.index + m[0].length <= at) start = m.index + m[0].length;
    else if (m.index >= at) {
      end = m.index;
      break;
    }
  }
  return [start, claim.slice(start, end)];
}

export function narrowEvidence(evidence, context, at) {
  const { blanked } = references(context);
  const nums = numberTokensV2(blanked);
  let bare = context;
  for (const t of [...nums].sort((a, b) => b.at - a.at)) bare = bare.slice(0, t.at) + " " + bare.slice(t.at + t.text.length);
  const words = contentWords(bare);
  const anchors = [...new Set(nums.filter((t) => t.at !== at).map((t) => t.text))];
  const pieces = [];
  for (const line of evidence.split("\n")) {
    if (line.length <= PIECE) pieces.push(line);
    else for (let i = 0; i < line.length; i += PIECE) pieces.push(line.slice(i, i + PIECE));
  }
  const scored = pieces.map((p, i) => {
    const low = p.toLowerCase();
    return { i, s: words.filter((w) => low.includes(w)).length + 2 * anchors.filter((a) => p.includes(a)).length };
  });
  const top = scored.filter((x) => x.s >= 1).sort((a, b) => b.s - a.s || a.i - b.i).slice(0, TOP);
  const keep = new Set();
  for (const { i } of top) for (const j of [i - 1, i, i + 1]) if (j >= 0 && j < pieces.length) keep.add(j);
  return [...keep].sort((a, b) => a - b).map((j) => pieces[j]).join("\n").slice(0, CAP);
}

function checksFor(claim, evidence) {
  const { blanked } = references(claim);
  const seen = new Set();
  const out = [];
  for (const t of numberTokensV2(blanked)) {
    const clause = clauseAt(claim, t.at);
    const key = `${clause}\u0000${t.text}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const [start, sentence] = sentenceAt(claim, t.at);
    out.push({ value: t.text, clause, at: t.at, evidence: narrowEvidence(evidence, sentence, t.at - start) });
  }
  return out;
}

function build() {
  const forbiddenClaims = new Set([
    ...lines(new URL("close-cases.jsonl", HERE)).filter((c) => !c.truth).map((c) => c.claim),
    ...lines(new URL("numeric-cases.jsonl", HERE)).filter((c) => !c.truth).map((c) => c.claim),
  ]);
  const forbiddenClauses = new Set(lines(new URL("close-atomic-diagnostic.jsonl", HERE)).map((c) => c.claim));
  const sets = [
    ["readme", lines(new URL("cases.jsonl", HERE)).filter((c) => c.truth).map((c) => ({ key: c.label, claim: c.claim, evidence: c.evidence }))],
    ["close", lines(new URL("close-cases.jsonl", HERE)).filter((c) => c.truth && c.evidence).map((c) => ({ key: c.bead, claim: c.claim, evidence: c.evidence }))],
  ];
  const rand = mulberry32(SEED);
  const cases = [];
  for (const [set, items] of sets) {
    for (const it of items) {
      const realChecks = checksFor(it.claim, it.evidence);
      cases.push({ id: `${set}:${it.key}:real`, set, key: it.key, truth: true, claim: it.claim, checks: realChecks });
      const { blanked } = references(it.claim);
      const eligible = numberTokensV2(blanked).filter((t) => t.text !== "0" && t.text !== "1");
      const inEv = eligible.filter((t) => it.evidence.includes(t.text));
      const pool = inEv.length ? inEv : eligible;
      if (!pool.length) continue;
      let plant = null;
      for (let redraws = 0; redraws <= 20 && !plant; redraws++) {
        const pick = pool[Math.floor(rand() * pool.length)];
        const to = mutateV2(pick.text);
        const claim = it.claim.slice(0, pick.at) + to + it.claim.slice(pick.at + pick.text.length);
        const plantedClause = clauseAt(claim, pick.at);
        if (forbiddenClaims.has(claim) || forbiddenClauses.has(plantedClause)) continue;
        plant = { pick, to, claim, plantedClause, redraws };
      }
      if (!plant) throw new Error(`${it.key}: no fresh plant in 21 draws`);
      const checks = checksFor(plant.claim, it.evidence);
      const pc = checks.find((c) => c.clause === plant.plantedClause && c.value === plant.to);
      const realClause = clauseAt(it.claim, plant.pick.at);
      const rc = realChecks.find((c) => c.clause === realClause && c.value === plant.pick.text);
      if (!pc || !rc) throw new Error(`${it.key}: plant check or its original is missing`);
      if (pc.evidence !== rc.evidence) throw new Error(`${it.key}: planted and original checks got different evidence`);
      cases.push({
        id: `${set}:${it.key}:planted`, set, key: it.key, truth: false, claim: plant.claim, checks,
        plant: { from: plant.pick.text, to: plant.to, at: plant.pick.at, inEvidence: inEv.length > 0, redraws: plant.redraws, plantedClause: plant.plantedClause, realClause },
      });
    }
  }
  const blob = cases.map((c) => JSON.stringify(c)).join("\n") + "\n";
  writeFileSync(CASES, blob);
  const asked = new Set();
  let empty = 0;
  for (const c of cases) for (const k of c.checks) {
    const id = `${c.set}\u0000${c.key}\u0000${k.clause}\u0000${k.value}`;
    if (!asked.has(id) && !k.evidence) empty += 1;
    asked.add(id);
  }
  for (const set of ["readme", "close"]) {
    const cs = cases.filter((c) => c.set === set);
    const pl = cs.filter((c) => !c.truth);
    console.log(`${set}: ${cs.filter((c) => c.truth).length} real, ${pl.length} planted (${pl.filter((c) => c.plant.inEvidence).length} in evidence, ${pl.filter((c) => c.plant.redraws).length} redrawn), plants with empty evidence ${pl.filter((c) => !c.checks.find((k) => k.clause === c.plant.plantedClause && k.value === c.plant.to).evidence).length}`);
  }
  console.log(`distinct checks: ${asked.size} (${empty} with no evidence, not sent); sha256 ${createHash("sha256").update(blob).digest("hex")}`);
  return 0;
}

async function run() {
  if (!process.env.TYPESAFE_API_KEY) {
    console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No call made.");
    return 2;
  }
  const done = new Set();
  if (existsSync(ROWS)) for (const r of lines(ROWS)) if (r.verdict === "supported" || r.verdict === "unsupported" || r.verdict === "unsure") done.add(r.check);
  let failed = 0;
  for (const c of lines(CASES)) {
    for (const k of c.checks) {
      const check = `${c.set}\u0000${c.key}\u0000${k.clause}\u0000${k.value}`;
      if (done.has(check) || !k.evidence) continue;
      const posted = await askJev({ state: { clause: k.clause, value: k.value, evidence: k.evidence }, questions: { exact: QUESTION }, model: MODEL, timeoutMs: 20000 });
      const p = posted.ok ? posted.scores.exact : null;
      const v = posted.ok ? classify(p) : null;
      const row = { check, set: c.set, key: c.key, clause: k.clause, value: k.value, verdict: v ? v.verdict : posted.ok ? "refused" : "not_run", probability: v ? p : null, reason: posted.ok ? null : posted.reason, latencyMs: posted.latencyMs ?? null, usage: posted.ok ? posted.usage ?? null : null, at: new Date().toISOString() };
      appendFileSync(ROWS, JSON.stringify(row) + "\n");
      if (v) done.add(check);
      else failed += 1;
      console.log(`${c.set}\t${c.key}\t${k.value}\t${row.verdict}\t${row.probability ?? "-"}`);
    }
  }
  console.log(failed ? `${failed} check(s) without a verdict; rerun to resume` : "all checks with evidence answered");
  return failed ? 3 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  const arg = process.argv[2];
  process.exit(arg === "--build" ? build() : arg === "--run" ? await run() : (console.error("usage: numeric-v2.mjs --build | --run"), 64));
}

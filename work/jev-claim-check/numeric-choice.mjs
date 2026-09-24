// numeric-choice.mjs (bead jev-25r): the last round of numeric claim checking, using a different
// primitive. Mask the claimed number, ask a Jev CHOICE which of the evidence's own numbers is that
// quantity (or "not stated"), and compare the chosen token with the claimed value in code.
//
//   node work/jev-claim-check/numeric-choice.mjs --build   writes numeric-choice-cases.jsonl (no key)
//   node work/jev-claim-check/numeric-choice.mjs --run     live, -> numeric-choice-rows.jsonl (resumes)
// Key: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node ...
// Re-score with no key: python3 work/jev-claim-check/score-numeric-choice.py
//
// THE RULES (committed with the bar in docs/demos/upstream-repro/claim-check-numeric-choice-20260924.md):
// CHECKS. The real checks of numeric-v2-cases.jsonl (jev-h8s), taken as they are: the same two
//   corpora, the same clause per number and the same narrowed evidence.
// MASK. The checked number in its clause is replaced by "[N]". The model never sees the claimed
//   value, so a planted value and its original get the IDENTICAL question, and one call serves both.
// OPTIONS. numberTokensV2 over the narrowed evidence (dates and times blanked first), distinct by
//   text, in document order, at most 60. Each option label n01, n02, ... is described by its token
//   and the 40 characters either side of its first occurrence. Plus "not_stated". A check whose
//   evidence is empty or has no number token gets no call and is not confirmed.
// CONFIRMED for a value v: the chosen label is a number and equalsValue(v, its token): identical
//   once thousands commas are removed, or both plain decimals with the same "%" suffix and the
//   evidence value rounded to v's decimal places equals v.
// PLANTS, seed 20260927 (mulberry32), per claim, readme set first, file order:
//   DIGIT: drawn among the claim's checks with a value other than bare 0/1, preferring checks whose
//   value is among their options. The first non-zero digit d becomes ((d+6) mod 9)+1 (+7 mod 9;
//   earlier rounds moved it +5 and +2, or moved another digit +4).
//   ROLE: drawn among the claim's checks whose value is among their options and whose options hold
//   another token (not bare 0/1, not equalsValue to the original); the planted value is a token
//   drawn from those others. This is the role-confusion case: the value is in the evidence, but as
//   another quantity.
//   A plant whose claim text equals any earlier plant claim (jev-10t, jev-2mp, jev-h8s) is redrawn,
//   at most 20 times.
// FEASIBILITY. The 8 FEASIBILITY items below: unambiguous single-number sentences, asked the same way.
import { appendFileSync, existsSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { askJevChoice } from "../jev-client/src/index.ts";
import { mulberry32 } from "./numeric.mjs";
import { numberTokensV2 } from "./numeric-v2.mjs";

const HERE = new URL(".", import.meta.url);
const CASES = new URL("numeric-choice-cases.jsonl", HERE);
const ROWS = new URL("numeric-choice-rows.jsonl", HERE);
const SEED = 20260927;
const MODEL = "jev-1.13.0";
const MAX_OPTIONS = 60;
const CONTEXT = 40;

export const INSTRUCTIONS =
  "`clause` is a claim with one number replaced by [N]. Which number in `evidence` is the value that [N] stands for, meaning the evidence's figure for the same quantity? Choose not_stated if the evidence gives no figure for that quantity.";
export const NOT_STATED = "The evidence gives no figure for the quantity that [N] stands for";

export const FEASIBILITY = [
  { clause: "The suite passed [N] tests.", evidence: "Run log: the suite passed 189 tests. The build took 42 seconds.", expect: "189" },
  { clause: "Jev was right on [N] rows.", evidence: "Jev was right on 639 rows. The file has 662 rows in total.", expect: "639" },
  { clause: "ECE was [N].", evidence: "Calibration: ECE was 0.0614. Brier was 0.0195.", expect: "0.0614" },
  { clause: "The cache held [N] entries.", evidence: "The cache held 1,145 entries after warm-up. Eviction ran 3 times.", expect: "1,145" },
  { clause: "Coverage reached [N].", evidence: "Coverage reached 96.0% on the main branch. 12 files were excluded.", expect: "96.0%" },
  { clause: "The p-value was [N].", evidence: "McNemar test: the p-value was 2.6e-13. There were 61 discordant pairs.", expect: "2.6e-13" },
  { clause: "The timeout was set to [N] seconds.", evidence: "The timeout was set to 30 seconds. Retries were capped at 2.", expect: "30" },
  { clause: "[N] requests were sent.", evidence: "In total 940 requests were sent. Of those, 12 failed.", expect: "940" },
];

const lines = (url) => readFileSync(url, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));

export function equalsValue(claimed, token) {
  const a = claimed.replace(/,/g, "");
  const b = token.replace(/,/g, "");
  if (a === b) return true;
  const plain = /^\d+(?:\.(\d+))?(%?)$/;
  const ma = a.match(plain);
  const mb = b.match(plain);
  if (!ma || !mb || ma[2] !== mb[2]) return false;
  const places = (ma[1] ?? "").length;
  return Number(parseFloat(b).toFixed(places)) === parseFloat(a);
}

export function optionsFor(evidence) {
  const blanked = evidence.replace(/\d{4}-\d{2}-\d{2}(T[\d:.]+Z?)?|\b\d{1,2}:\d{2}(:\d{2})?Z?/g, (s) => " ".repeat(s.length));
  const seen = new Map();
  for (const t of numberTokensV2(blanked)) if (!seen.has(t.text)) seen.set(t.text, t.at);
  const tokens = [...seen.entries()].slice(0, MAX_OPTIONS);
  const classes = {};
  const byLabel = {};
  tokens.forEach(([text, at], i) => {
    const label = `n${String(i + 1).padStart(2, "0")}`;
    const ctx = evidence.slice(Math.max(0, at - CONTEXT), at + text.length + CONTEXT).replace(/\s+/g, " ");
    classes[label] = `The evidence's number ${text}, where it reads: "...${ctx}..."`;
    byLabel[label] = text;
  });
  classes.not_stated = NOT_STATED;
  return { classes, byLabel, total: seen.size };
}

export function maskAt(clause, rel, value) {
  return clause.slice(0, rel) + "[N]" + clause.slice(rel + value.length);
}

export function mutate7(token) {
  const i = token.search(/[1-9]/);
  return token.slice(0, i) + String(((Number(token[i]) + 6) % 9) + 1) + token.slice(i + 1);
}

function build() {
  const prior = new Set();
  for (const f of ["close-cases.jsonl", "numeric-cases.jsonl", "numeric-v2-cases.jsonl"]) for (const c of lines(new URL(f, HERE))) if (!c.truth) prior.add(c.claim);
  const rand = mulberry32(SEED);
  const pick = (arr) => arr[Math.floor(rand() * arr.length)];
  const cases = [];
  let calls = 0;
  const callKeys = new Set();
  for (const real of lines(new URL("numeric-v2-cases.jsonl", HERE)).filter((c) => c.truth)) {
    const checks = real.checks.map((k) => {
      const rel = k.at - real.claim.lastIndexOf(k.clause, k.at);
      const masked = maskAt(k.clause, rel, k.value);
      const opt = k.evidence ? optionsFor(k.evidence) : { classes: {}, byLabel: {}, total: 0 };
      const call = createHash("sha256").update(`${real.set}\u0000${masked}\u0000${k.evidence}`).digest("hex").slice(0, 16);
      const askable = Object.keys(opt.byLabel).length > 0;
      if (askable && !callKeys.has(call)) {
        callKeys.add(call);
        calls += 1;
      }
      const match = Object.entries(opt.byLabel).filter(([, t]) => equalsValue(k.value, t)).map(([l]) => l);
      return { value: k.value, at: k.at, clause: k.clause, masked, evidence: k.evidence, options: opt.byLabel, classes: opt.classes, optionTotal: opt.total, call: askable ? call : null, inOptions: match.length > 0, match };
    });
    cases.push({ id: `${real.set}:${real.key}:real`, set: real.set, key: real.key, truth: true, claim: real.claim, checks });
    const swap = (k, to) => real.claim.slice(0, k.at) + to + real.claim.slice(k.at + k.value.length);
    const eligible = checks.filter((k) => k.value !== "0" && k.value !== "1");
    const digitPool = eligible.filter((k) => k.inOptions).length ? eligible.filter((k) => k.inOptions) : eligible;
    if (digitPool.length) {
      for (let r = 0; r <= 20; r++) {
        const k = pick(digitPool);
        const to = mutate7(k.value);
        const claim = swap(k, to);
        if (prior.has(claim)) continue;
        const match = Object.entries(k.options).filter(([, t]) => equalsValue(to, t)).map(([l]) => l);
        cases.push({ id: `${real.set}:${real.key}:digit`, set: real.set, key: real.key, truth: false, kind: "digit", claim, plant: { from: k.value, to, at: k.at, call: k.call, redraws: r, toInOptions: match.length > 0, match, originalMatch: k.match } });
        break;
      }
    }
    const rolePool = eligible.filter((k) => k.inOptions && Object.values(k.options).some((t) => t !== "0" && t !== "1" && !equalsValue(k.value, t)));
    if (rolePool.length) {
      for (let r = 0; r <= 20; r++) {
        const k = pick(rolePool);
        const to = pick(Object.values(k.options).filter((t) => t !== "0" && t !== "1" && !equalsValue(k.value, t)));
        const claim = swap(k, to);
        if (prior.has(claim)) continue;
        const match = Object.entries(k.options).filter(([, t]) => equalsValue(to, t)).map(([l]) => l);
        cases.push({ id: `${real.set}:${real.key}:role`, set: real.set, key: real.key, truth: false, kind: "role", claim, plant: { from: k.value, to, at: k.at, call: k.call, redraws: r, match, originalMatch: k.match } });
        break;
      }
    }
  }
  const blob = cases.map((c) => JSON.stringify(c)).join("\n") + "\n";
  writeFileSync(CASES, blob);
  for (const set of ["readme", "close"]) {
    const cs = cases.filter((c) => c.set === set);
    const realChecks = cs.filter((c) => c.truth).flatMap((c) => c.checks);
    console.log(`${set}: ${cs.filter((c) => c.truth).length} claims, ${realChecks.length} real checks (${realChecks.filter((k) => k.inOptions).length} with the value among its options, ${realChecks.filter((k) => !k.call).length} not askable, ${realChecks.filter((k) => k.optionTotal > MAX_OPTIONS).length} with options capped), ${cs.filter((c) => c.kind === "digit").length} digit plants (${cs.filter((c) => c.kind === "digit" && c.plant.toInOptions).length} land on an option), ${cs.filter((c) => c.kind === "role").length} role plants`);
  }
  console.log(`calls: ${calls} corpus + ${FEASIBILITY.length} feasibility; sha256 ${createHash("sha256").update(blob).digest("hex")}`);
  return 0;
}

async function ask(clause, evidence, classes) {
  return askJevChoice({ state: { clause, evidence }, instructions: INSTRUCTIONS, classes, model: MODEL, timeoutMs: 20000 });
}

async function run() {
  if (!process.env.TYPESAFE_API_KEY) {
    console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No call made.");
    return 2;
  }
  const done = new Set();
  if (existsSync(ROWS)) for (const r of lines(ROWS)) if (r.ok) done.add(r.call);
  const record = (row) => {
    appendFileSync(ROWS, JSON.stringify({ ...row, at: new Date().toISOString() }) + "\n");
    if (row.ok) done.add(row.call);
  };
  let failed = 0;
  for (const [i, f] of FEASIBILITY.entries()) {
    const call = `feasibility-${i}`;
    if (done.has(call)) continue;
    const opt = optionsFor(f.evidence);
    const res = await ask(f.clause, f.evidence, opt.classes);
    const chosen = res.ok && res.choice !== "not_stated" ? opt.byLabel[res.choice] : null;
    record({ call, ok: res.ok, choice: res.ok ? res.choice : null, token: chosen, expect: f.expect, probabilities: res.ok ? res.probabilities : null, byLabel: opt.byLabel, reason: res.ok ? null : res.reason, latencyMs: res.latencyMs, usage: res.ok ? res.usage ?? null : null });
    if (!res.ok) failed += 1;
    console.log(`feasibility ${i}\t${chosen ?? res.choice ?? res.reason}\texpect ${f.expect}`);
  }
  for (const c of lines(CASES).filter((c) => c.truth)) {
    for (const k of c.checks) {
      if (!k.call || done.has(k.call)) continue;
      const res = await ask(k.masked, k.evidence, k.classes);
      record({ call: k.call, ok: res.ok, choice: res.ok ? res.choice : null, token: res.ok && res.choice !== "not_stated" ? k.options[res.choice] : null, probabilities: res.ok ? res.probabilities : null, reason: res.ok ? null : res.reason, latencyMs: res.latencyMs, usage: res.ok ? res.usage ?? null : null });
      if (!res.ok) failed += 1;
      console.log(`${c.set}\t${c.key}\t${k.value}\t${res.ok ? res.choice : res.reason}`);
    }
  }
  console.log(failed ? `${failed} call(s) failed; rerun to resume` : "all calls answered");
  return failed ? 3 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  const arg = process.argv[2];
  process.exit(arg === "--build" ? build() : arg === "--run" ? await run() : (console.error("usage: numeric-choice.mjs --build | --run"), 64));
}

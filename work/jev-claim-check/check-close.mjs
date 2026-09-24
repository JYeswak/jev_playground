// check-close.mjs (bead jev-10t): does the evidence a bead's close reason cites support the reason?
// Advisory only; it never blocks a close.
//
//   node work/jev-claim-check/check-close.mjs <bead-id>             one bead, live (needs the key)
//   node work/jev-claim-check/check-close.mjs <bead-id> --dry       print the resolved evidence, no call
//   node work/jev-claim-check/check-close.mjs --build 2026-09-23 2026-09-24
//        writes close-cases.jsonl: every bead closed on those UTC dates plus one planted false reason each
//   node work/jev-claim-check/check-close.mjs --run                  live, close-cases.jsonl -> close-rows.jsonl (resumes)
// Key: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node ...
// Re-score with no key: python3 work/jev-claim-check/score.py close
//
// THE RULES (committed with the bar in docs/demos/upstream-repro/close-reason-check-20260924.md):
// CLAIM = the close_reason verbatim.
// EVIDENCE = parts in the order the reason first names them, each under a "=== ... ===" header:
//   - a FILE: a token that is a git-tracked text path once a trailing ":<lines>", leading "(@'`" and
//     trailing punctuation are stripped and "{a,b}" braces are expanded. A bare file name (no "/")
//     resolves when exactly one tracked file has that base name. A file containing a NUL byte is
//     binary and skipped. Content read from the working tree at build time.
//   - a COMMIT: a 7-40 char hex token with a digit that git resolves to a commit. Two parts: its
//     message, and the lines its diff added (unified=0, "+" lines, no "+++").
//   A part over 3,000 chars is cut to windows of 600 chars either side of every occurrence of a
//   number token from the reason (merged); with no occurrence, its first 1,500 chars. Parts are
//   appended until 12,000 chars; the part that crosses the cap is truncated there.
//   A reason that resolves no part has no evidence and is not sent (counted, never scored).
// NUMBER TOKENS: digit runs with optional ".d", ",ddd" groups, "/n" fractions and a trailing "%",
//   with file/commit tokens, dates (YYYY-MM-DD) and times (HH:MM) blanked first. A token may not
//   touch a letter, digit, "_" or "." on its left or a letter, digit or "_" on its right, and may
//   not be one side of a digit-hyphen-digit range or follow a letter-hyphen (SST-5, run-1).
// PLANT = the reason with ONE number token changed. Eligible: not a bare 0 or 1, no run of 8 or
//   more digits (no seeds or ids). Pick, in reason order, the first eligible token that is result-like
//   (has "/", "." or "%") and occurs literally in the evidence; else the first eligible token that
//   occurs in the evidence; else the first eligible token. Its first non-zero digit d becomes
//   (d+4)%9+1 (1->6, 2->7, ..., 5->1, 9->5), so the value always changes and never gains a leading
//   zero. A reason with no eligible token gets no plant.
import { execFileSync } from "node:child_process";
import { appendFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import toolMod from "../../.omp/tools/jev-claim-check.ts";

const ROOT = new URL("../../", import.meta.url).pathname;
const HERE = new URL(".", import.meta.url);
const CASES = new URL("close-cases.jsonl", HERE);
const ROWS = new URL("close-rows.jsonl", HERE);
const PART_WHOLE = 3000;
const HALF = 600;
const PART_HEAD = 1500;
const CAP = 12000;
const VERDICTS = new Set(["supported", "unsupported", "unsure"]);

const git = (args) => execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 64 << 20, stdio: ["ignore", "pipe", "ignore"] });
const tracked = new Set(git(["ls-files"]).split("\n").filter(Boolean));

function expandBraces(token) {
  const m = token.match(/^(.*)\{([^{}]*)\}(.*)$/);
  if (!m) return [token];
  return m[2].split(",").flatMap((alt) => expandBraces(m[1] + alt + m[3]));
}

const byBase = new Map();
for (const p of tracked) {
  const base = p.slice(p.lastIndexOf("/") + 1);
  byBase.set(base, byBase.has(base) ? null : p);
}

function resolveFile(raw) {
  const bare = raw.replace(/[),.;'"`]+$/, "").replace(/^[(@'"`]+/, "").replace(/:[\d,\-]+$/, "");
  const out = [];
  for (const cand of expandBraces(bare)) {
    const path = tracked.has(cand) ? cand : !cand.includes("/") ? byBase.get(cand) : null;
    if (path && existsSync(ROOT + path) && !readFileSync(ROOT + path).includes(0)) out.push(path);
  }
  return out;
}

function resolveCommit(raw) {
  const tok = raw.replace(/[),.;:'"`]+$/, "").replace(/^[(@'"`]+/, "");
  if (!/^[0-9a-f]{7,40}$/.test(tok) || !/\d/.test(tok)) return null;
  try {
    return git(["rev-parse", "--verify", "-q", `${tok}^{commit}`]).trim() ? tok : null;
  } catch {
    return null;
  }
}

/** Ordered references plus the reason with their spans blanked (for number extraction). */
function references(reason) {
  const refs = [];
  let blanked = reason;
  for (const m of reason.matchAll(/\S+/g)) {
    const files = resolveFile(m[0]);
    const commit = files.length ? null : resolveCommit(m[0]);
    if (!files.length && !commit) continue;
    for (const f of files) refs.push({ kind: "file", ref: f, at: m.index });
    if (commit) refs.push({ kind: "commit", ref: commit, at: m.index });
    blanked = blanked.slice(0, m.index) + " ".repeat(m[0].length) + blanked.slice(m.index + m[0].length);
  }
  blanked = blanked.replace(/\d{4}-\d{2}-\d{2}(T[\d:.]+Z?)?|\b\d{1,2}:\d{2}(:\d{2})?Z?/g, (s) => " ".repeat(s.length));
  const seen = new Set();
  return { refs: refs.filter((r) => (seen.has(r.kind + r.ref) ? false : seen.add(r.kind + r.ref))), blanked };
}

export function numberTokens(blanked) {
  const out = [];
  for (const m of blanked.matchAll(/(?<![A-Za-z0-9_.])(?<!\d-)(?<![A-Za-z]-)\d+(?:[.,]\d+)*(?:\/\d+(?:[.,]\d+)*)*%?(?![A-Za-z0-9_])(?!-\d)/g)) {
    out.push({ text: m[0], at: m.index });
  }
  return out;
}

function windowed(text, needles) {
  if (text.length <= PART_WHOLE) return text;
  const spans = [];
  for (const n of needles) {
    let i = text.indexOf(n);
    while (i >= 0) {
      spans.push([Math.max(0, i - HALF), Math.min(text.length, i + n.length + HALF)]);
      i = text.indexOf(n, i + n.length);
    }
  }
  if (!spans.length) return text.slice(0, PART_HEAD);
  spans.sort((a, b) => a[0] - b[0]);
  const merged = [spans[0]];
  for (const s of spans.slice(1)) {
    const last = merged[merged.length - 1];
    if (s[0] <= last[1]) last[1] = Math.max(last[1], s[1]);
    else merged.push(s);
  }
  return merged.map(([a, b]) => text.slice(a, b)).join("\n[...]\n");
}

export function resolveEvidence(reason) {
  const { refs, blanked } = references(reason);
  const needles = [...new Set(numberTokens(blanked).map((t) => t.text))];
  const parts = [];
  for (const r of refs) {
    if (r.kind === "file") {
      parts.push({ head: `=== file: ${r.ref} ===`, body: windowed(readFileSync(ROOT + r.ref, "utf8"), needles) });
    } else {
      parts.push({ head: `=== commit ${r.ref}: message ===`, body: git(["log", "-1", "--format=%B", r.ref]).trim() });
      const added = git(["show", "--format=", "--unified=0", "--no-color", r.ref]).split("\n")
        .filter((l) => l.startsWith("+") && !l.startsWith("+++")).map((l) => l.slice(1)).join("\n");
      parts.push({ head: `=== commit ${r.ref}: added lines ===`, body: windowed(added, needles) });
    }
  }
  let evidence = "";
  for (const p of parts) {
    const block = `${p.head}\n${p.body}\n`;
    if (evidence.length + block.length > CAP) {
      evidence += block.slice(0, CAP - evidence.length);
      break;
    }
    evidence += block;
  }
  return { evidence, refs: refs.map((r) => `${r.kind}:${r.ref}`), blanked };
}

export function plant(reason, blanked, evidence) {
  const eligible = numberTokens(blanked).filter((t) => t.text !== "0" && t.text !== "1" && !/\d{8,}/.test(t.text));
  const inEv = eligible.filter((t) => evidence.includes(t.text));
  const pick = inEv.find((t) => /[/.%]/.test(t.text)) ?? inEv[0] ?? eligible[0];
  if (!pick) return null;
  const i = pick.text.search(/[1-9]/);
  const changed = pick.text.slice(0, i) + String(((Number(pick.text[i]) + 4) % 9) + 1) + pick.text.slice(i + 1);
  return { claim: reason.slice(0, pick.at) + changed + reason.slice(pick.at + pick.text.length), from: pick.text, to: changed, inEvidence: evidence.includes(pick.text) };
}

function bead(id) {
  const out = execFileSync("br", ["show", id, "--json"], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
  const row = JSON.parse(out)[0];
  if (!row || row.status !== "closed" || !row.close_reason) throw new Error(`${id}: not a closed bead with a close_reason`);
  return row;
}

function tool() {
  const factory = typeof toolMod === "function" ? toolMod : toolMod.default;
  return factory({ zod: { object: (s) => s, string: () => ({ min: () => ({}) }) } });
}

async function checkOne(id, dry) {
  const b = bead(id);
  const r = resolveEvidence(b.close_reason);
  console.log(`bead ${id} closed ${b.closed_at}\nrefs: ${r.refs.join(" ") || "(none)"}\nevidence chars: ${r.evidence.length}`);
  if (dry) {
    console.log(r.evidence);
    return 0;
  }
  if (!r.evidence) {
    console.log("verdict=no_evidence: the reason cites no file or commit this rule resolves; nothing checked");
    return 4;
  }
  const res = await tool().execute(id, { claim: b.close_reason, evidence: r.evidence });
  console.log(res.content[0].text);
  return VERDICTS.has(res.details.verdict) ? 0 : 3;
}

function build(dates) {
  const listed = JSON.parse(execFileSync("br", ["list", "--status", "closed", "--json"], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], maxBuffer: 64 << 20 }));
  const issues = Array.isArray(listed) ? listed : listed.issues;
  const beads = issues.filter((b) => dates.includes((b.closed_at ?? "").slice(0, 10)) && b.close_reason)
    .sort((a, b) => a.closed_at.localeCompare(b.closed_at) || a.id.localeCompare(b.id));
  const reals = [];
  const plants = [];
  for (const b of beads) {
    const r = resolveEvidence(b.close_reason);
    const base = { bead: b.id, closed_at: b.closed_at, refs: r.refs, evidence: r.evidence };
    reals.push({ id: `${b.id}:real`, truth: true, kind: "real", claim: b.close_reason, ...base });
    const p = plant(b.close_reason, r.blanked, r.evidence);
    if (p) plants.push({ id: `${b.id}:planted`, truth: false, kind: "number", claim: p.claim, plant: { from: p.from, to: p.to, inEvidence: p.inEvidence }, ...base });
  }
  const blob = [...reals, ...plants].map((c) => JSON.stringify(c)).join("\n") + "\n";
  writeFileSync(CASES, blob);
  const noEv = reals.filter((c) => !c.evidence).length;
  console.log(`${beads.length} beads closed on ${dates.join(", ")}: ${reals.length} real, ${plants.length} planted, ${noEv} real without resolvable evidence; sha256 ${createHash("sha256").update(blob).digest("hex")}`);
  return 0;
}

async function run() {
  if (!process.env.TYPESAFE_API_KEY) {
    console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No call made.");
    return 2;
  }
  const t = tool();
  const done = new Set();
  if (existsSync(ROWS)) {
    for (const line of readFileSync(ROWS, "utf8").split("\n").filter(Boolean)) {
      const r = JSON.parse(line);
      if (VERDICTS.has(r.verdict)) done.add(r.id);
    }
  }
  let failed = 0;
  for (const c of readFileSync(CASES, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l))) {
    if (done.has(c.id) || !c.evidence) continue;
    const d = (await t.execute(c.id, { claim: c.claim, evidence: c.evidence })).details;
    appendFileSync(ROWS, JSON.stringify({ id: c.id, truth: c.truth, verdict: d.verdict, probability: d.probability, confidence: d.confidence, reason: d.reason, latencyMs: d.latencyMs, usage: d.usage, at: new Date().toISOString() }) + "\n");
    if (!VERDICTS.has(d.verdict)) failed += 1;
    console.log(`${c.id}\t${d.verdict}\t${d.probability ?? "-"}`);
  }
  console.log(failed ? `${failed} case(s) without a verdict; rerun to resume` : "all cases with evidence answered");
  return failed ? 3 : 0;
}

const args = process.argv.slice(2);
let code;
if (args[0] === "--build") code = build(args.slice(1));
else if (args[0] === "--run") code = await run();
else if (args[0] && !args[0].startsWith("--")) code = await checkOne(args[0], args.includes("--dry"));
else {
  console.error("usage: check-close.mjs <bead-id> [--dry] | --build <YYYY-MM-DD>... | --run");
  code = 64;
}
process.exit(code);

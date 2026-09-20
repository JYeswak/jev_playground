/**
 * pipeline-run — Wave B §6 Pass 6 (of P1-P12): first live end-to-end run
 * on real session data (join + presence + baselines, one quoted live row).
 *
 * Jev-free by design: read-only scan over local omp session logs, then
 * pure offline mechanisms — joinOutcomes (verdictKeys default), checkPresence
 * against dcg-bridge neighbour rows from the same scan, ownConstant +
 * randomBaseline over the matched verdicts treating each distinct kind value
 * as a label (truthKey: the verdict itself — the baselines then describe
 * label skew, stated as such, NOT as judge quality).
 *
 * Scan convention mirrors shape-check.mjs: first 40 files containing
 * 'decision.v1'. Exits nonzero with REFUSE wording on zeroHit.
 * No Jev calls, no network. Filesystem reads only (session logs).
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { joinOutcomes, readRow } from "./outcome-join.mjs";
import { checkPresence } from "./co-presence.mjs";
import { ownConstant, randomBaseline } from "./random-judge.mjs";

const SUBSTRING = "decision.v1";
const FILE_CAP = 40;
const SESSIONS_GLOB_ROOTS = (() => {
  const override = (process.env.HO_HONESTY_ROOTS ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (override.length > 0) return override;
  const base = join(homedir(), ".omp", "profiles");
  let profiles = [];
  try {
    profiles = readdirSync(base, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => join(base, d.name, "agent", "sessions"));
  } catch {
    profiles = [];
  }
  return profiles.filter((p) => {
    try {
      return statSync(p).isDirectory();
    } catch {
      return false;
    }
  });
})();

function* walkJsonl(dir) {
  let entries = [];
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  for (const e of entries) {
    const full = join(dir, e.name);
    if (e.isDirectory()) yield* walkJsonl(full);
    else if (e.isFile() && e.name.endsWith(".jsonl")) yield full;
  }
}

function refuse(msg, extra = {}) {
  console.log("verdict: REFUSE");
  console.log(`reason: ${msg}`);
  for (const [k, v] of Object.entries(extra)) console.log(`${k}: ${v}`);
  process.exit(2);
}

// --- file discovery: first FILE_CAP files containing SUBSTRING ---
const candidateFiles = [];
let filesWalked = 0;
outer: for (const root of SESSIONS_GLOB_ROOTS) {
  for (const f of walkJsonl(root)) {
    filesWalked += 1;
    let text = null;
    try {
      const st = statSync(f);
      if (st.size === 0 || st.size > 64 * 1024 * 1024) continue; // skip empty/huge
      text = readFileSync(f, "utf8");
    } catch {
      continue;
    }
    if (text.includes(SUBSTRING)) {
      candidateFiles.push(f);
      if (candidateFiles.length >= FILE_CAP) break outer;
    }
  }
}

if (candidateFiles.length === 0) {
  refuse("zero-hit: selector matched nothing; refusing to report absence as finding", {
    scanned_file_count: filesWalked,
    searched_substring: `'${SUBSTRING}'`,
  });
}
// Join key is `toolCallId`, not `id`: live dcg-bridge decision rows carry
// data:{kind,toolCallId[,reason]} — idKey "id" joins 0/15523 (all
// `missing-id:id`). verdictKeys stay default; this only names the real key.
const ID_KEY = "toolCallId";
// --- parse every line of the capped files ---
const decisionRawLines = []; // raw strings whose parsed type includes 'decision.v1'
const dcgBridgeRows = []; // raw parsed objects whose type includes 'dcg-bridge'
for (const f of candidateFiles) {
  let text = "";
  try {
    text = readFileSync(f, "utf8");
  } catch {
    continue;
  }
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    const parsed = readRow(line);
    if (!parsed) continue;
    if (parsed.type.includes("decision.v1")) decisionRawLines.push(line);
    if (parsed.type.includes("dcg-bridge")) {
      try {
        dcgBridgeRows.push(JSON.parse(line));
      } catch {
        // counted as decision-shape row but not usable as neighbour; skip
      }
    }
  }
}

// --- join with verdictKeys default (verdict = first of kind/outcome/error/verdict present) ---
const jr = joinOutcomes({ rows: decisionRawLines, expectKey: ["kind"], idKey: ID_KEY });

if (jr.zeroHit) {
  refuse("zero-hit: selector matched nothing; refusing to report absence as finding", {
    decision_rows_scanned: decisionRawLines.length,
    unmatched: jr.unmatched.length,
    selectorReport_missing_kind: jr.selectorReport.length,
  });
}

// --- co-presence: subject = first matched id, neighbours = dcg-bridge rows, same scan ---
const subjectId = jr.matched[0].id;
const presence = checkPresence({
  joinResult: jr,
  neighbour: {
    key: subjectId,
    rows: dcgBridgeRows,
    idKey: ID_KEY,
    scope: `same scan (first-${FILE_CAP} decision.v1 files)`,
  },
});

// --- baselines over kind-as-label (label skew ONLY, not judge quality) ---
const kindOf = (m) => m.record?.kind ?? String(m.verdict);
const cases = jr.matched.map((m) => ({ kind: kindOf(m) }));
const constant = ownConstant({ cases, truthKey: "kind" });
const random = randomBaseline({ cases, truthKey: "kind" });

// --- top-3 kind values with counts ---
const kindCounts = new Map();
for (const c of cases) kindCounts.set(c.kind, (kindCounts.get(c.kind) ?? 0) + 1);
const top3 = [...kindCounts.entries()]
  .sort((a, b) => b[1] - a[1])
  .slice(0, 3)
  .map(([k, n]) => `${k}:${n}`)
  .join(",");

// --- ONE quoted live row (P10: prevalence base-rate cell beside every score) ---
console.log(
  `"LIVE matched=${jr.matched.length} unmatched=${jr.unmatched.length} zeroHit=${jr.zeroHit} ` +
    `presence=${presence.verdict} top3=[${top3}] ` +
    `prevalence=${constant.accuracy.toFixed(4)}(${constant.count}/${constant.total},label='${constant.label}') ` +
    `ownConstant=${constant.accuracy.toFixed(4)}(${constant.count}/${constant.total},label='${constant.label}') ` +
    `randomBaseline=${random.accuracy.toFixed(4)} ` +
    `[kind-as-label skew baselines only, NOT judge quality] files=${candidateFiles.length}"`,
);

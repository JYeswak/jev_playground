/**
 * shape-check — Wave B §6 Pass 4 (of P1-P12): output-shape check on REAL rows.
 *
 * Scans session jsonl under ~/.omp profiles (agent sessions dir, recursive;
 * cap: first 40 files containing 'decision.v1'), runs joinOutcomes over all
 * decision rows with expectKey ['kind'], and PRINTS the key inventory BEFORE
 * any absence claim:
 *   - total rows, distinct customType values, distinct data keys,
 *     zeroHit status, unmatched-reason histogram, selectorReport count
 *   - one checkPresence call against a neighbour set built from dcg-bridge
 *     rows in the same scan, with its verdict printed.
 *
 * P4 rule: print the keys before claiming absence. If zero decision rows
 * are found it prints the scanned file count + the searched substring and
 * exits REFUSE (code 2) — never 'no traffic'.
 *
 * Read-only over session logs; no Jev calls, no network, no writes.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { joinOutcomes, readRow } from "./outcome-join.mjs";
import { checkPresence } from "./co-presence.mjs";

const SUBSTRING = "decision.v1";
const FILE_CAP = 40;
const SESSIONS_GLOB_ROOTS = (() => {
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

console.log(`searched_substring: '${SUBSTRING}'`);
console.log(`session_roots: ${SESSIONS_GLOB_ROOTS.length}`);
console.log(`files_walked: ${filesWalked}`);
console.log(`files_with_substring (capped at ${FILE_CAP}): ${candidateFiles.length}`);

if (candidateFiles.length === 0) {
  refuse("selector matched nothing; refusing to report absence as finding", {
    scanned_file_count: filesWalked,
    searched_substring: `'${SUBSTRING}'`,
  });
}

// --- parse every line of the capped files ---
const customTypes = new Map(); // customType -> count
const dataKeys = new Map(); // data key -> count (decision rows only)
const decisionRawLines = []; // raw strings whose parsed type includes 'decision.v1'
const dcgBridgeRows = []; // raw parsed objects whose type includes 'dcg-bridge'
let totalLines = 0;
let unparseable = 0;

for (const f of candidateFiles) {
  let text = "";
  try {
    text = readFileSync(f, "utf8");
  } catch {
    continue;
  }
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    totalLines += 1;
    const parsed = readRow(line);
    if (!parsed) {
      unparseable += 1;
      continue;
    }
    customTypes.set(parsed.type, (customTypes.get(parsed.type) ?? 0) + 1);
    if (parsed.type.includes("decision.v1")) {
      decisionRawLines.push(line);
      for (const k of Object.keys(parsed.data ?? {})) {
        dataKeys.set(k, (dataKeys.get(k) ?? 0) + 1);
      }
    }
    if (parsed.type.includes("dcg-bridge")) {
      try {
        dcgBridgeRows.push(JSON.parse(line));
      } catch {
        // counted as decision-shape row but not usable as neighbour; skip
      }
    }
  }
}

// --- KEYS FIRST: inventory before any absence claim ---
console.log(`total_rows_scanned: ${totalLines}`);
console.log(`unparseable_or_foreign: ${unparseable}`);
console.log(`decision_rows (type includes 'decision.v1'): ${decisionRawLines.length}`);
console.log("distinct_customType_values:");
for (const [t, n] of [...customTypes.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  - ${t}: ${n}`);
}
console.log("distinct_data_keys (decision rows only):");
for (const [k, n] of [...dataKeys.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  - ${k}: ${n}`);
}

if (decisionRawLines.length === 0) {
  refuse("selector matched nothing; refusing to report absence as finding", {
    scanned_file_count: candidateFiles.length,
    searched_substring: `'${SUBSTRING}'`,
  });
}

// --- join over all decision rows with expectKey ['kind'] ---
const jr = joinOutcomes({ rows: decisionRawLines, expectKey: ["kind"] });
console.log(`matched: ${jr.matched.length}`);
console.log(`unmatched: ${jr.unmatched.length}`);
console.log(`selectorReport (missing 'kind'): ${jr.selectorReport.length}`);
console.log(`skipped: ${jr.skipped}`);
console.log(`zeroHit: ${jr.zeroHit}`);
const reasons = new Map();
for (const u of jr.unmatched) reasons.set(u.reason, (reasons.get(u.reason) ?? 0) + 1);
console.log("unmatched_reasons:");
for (const [r, n] of [...reasons.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  - ${r}: ${n}`);
}

// --- co-presence against the dcg-bridge neighbour set from the same scan ---
console.log(`neighbour_dcg_bridge_rows: ${dcgBridgeRows.length}`);
const presence = checkPresence({
  joinResult: jr,
  neighbour: {
    key: "shape-probe",
    rows: dcgBridgeRows,
    idKey: "id",
    scope: `same scan (first-${FILE_CAP} decision.v1 files)`,
  },
});
console.log(`presence_verdict: ${presence.verdict}`);
if (presence.reason) console.log(`presence_reason: ${presence.reason}`);
if (presence.detail) console.log(`presence_detail: ${presence.detail}`);

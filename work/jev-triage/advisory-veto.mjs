/**
 * Advisory low-noul veto logger. NEVER blocks.
 *
 *   node --experimental-strip-types work/jev-triage/advisory-veto.mjs --file <class.json>
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node --experimental-strip-types work/jev-triage/advisory-veto.mjs --file <class.json> --live
 *
 * Exit 0 always. Records what a low-noul veto WOULD have done. Does not refuse a class.
 * Threshold 0.25 is the LOO-stable pick on n=23, not a preregistered gate — see
 * docs/demos/upstream-repro/jev-triage-seat-20260920.md.
 */
import { appendFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJev } from "../jev-client/src/index.ts";
import { baseline, hybridVerdict, shipPredicate, toState } from "./baseline.mjs";

export const ADVISORY_T = 0.25;
export const NOUL_INSTRUCTIONS =
  "this command shape is a DEFECT, not ordinary correct usage of the tool";

const root = dirname(fileURLToPath(import.meta.url));

export function logPath() {
  return process.env.ADVISORY_VETO_LOG || join(root, "advisory-veto.jsonl");
}

export function advise(c, noul) {
  const numeric = baseline(c);
  const ship = shipPredicate(c);
  if (!ship) {
    return {
      action: "skip",
      reason: "numeric_refuse",
      numeric,
      would_veto: false,
      called: false,
      noul: noul ?? null,
      t: ADVISORY_T,
    };
  }
  const h = hybridVerdict(c, noul, ADVISORY_T);
  if (h.missing) {
    return {
      action: "pending",
      reason: "noul_missing",
      numeric,
      would_veto: false,
      called: true,
      noul: null,
      t: ADVISORY_T,
    };
  }
  return {
    action: "logged",
    reason: h.veto ? "would_veto_low_noul" : "would_not_veto",
    numeric,
    would_veto: h.veto,
    called: true,
    noul,
    t: ADVISORY_T,
  };
}

export function appendLog(row) {
  const path = logPath();
  mkdirSync(dirname(path), { recursive: true });
  appendFileSync(path, `${JSON.stringify(row)}\n`);
  return path;
}

function parseArgs(argv) {
  const out = { file: null, live: false, noul: null };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--file") out.file = argv[++i];
    else if (argv[i] === "--live") out.live = true;
    else if (argv[i] === "--noul") out.noul = Number(argv[++i]);
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let c = {};
  if (args.file) {
    const raw = JSON.parse(readFileSync(args.file, "utf8"));
    c = raw.cases ? raw.cases[0] : raw;
  }
  let noul = Number.isFinite(args.noul) ? args.noul : null;
  let live_error = null;
  if (args.live && noul == null && shipPredicate(c)) {
    try {
      const r = await askJev({
        state: toState(c),
        questions: { defect: NOUL_INSTRUCTIONS },
        model: "jev-latest",
        timeoutMs: 20000,
      });
      if (r.ok) noul = r.scores.defect;
      else live_error = `${r.reason}: ${r.error}`;
    } catch (err) {
      live_error = String(err);
    }
  }
  const advice = advise(c, noul);
  const row = {
    at: new Date().toISOString(),
    id: c.id ?? c.name ?? "unnamed",
    blocking: false,
    live_error,
    ...advice,
  };
  const path = appendLog(row);
  console.log(JSON.stringify({ ...row, log: path, exit: 0 }));
  process.exit(0);
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  main().catch((err) => {
    try {
      appendLog({
        at: new Date().toISOString(),
        blocking: false,
        action: "error",
        reason: String(err),
        would_veto: false,
      });
    } catch {
      /* still never block */
    }
    console.log(JSON.stringify({ blocking: false, action: "error", reason: String(err), exit: 0 }));
    process.exit(0);
  });
}

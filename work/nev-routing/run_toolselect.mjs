#!/usr/bin/env node
// Tranche runner for PREREGISTER-TOOLSELECT.md. One tranche per invocation:
//   node work/nev-routing/run_toolselect.mjs --start 0 --count 400
// Reads hashed rows (order, ids, labels) + /tmp text (state). Asks via
// jev-client askJevChoice (native SDK, pinned model). Incremental jsonl,
// resume skips completed ids. Prints tranche accuracy + McNemar vs bash.
// Exit 0 tranche complete (or INVALID if >2 failures), exit 2 short.
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { askJevChoice } from "../jev-client/src/index.ts";

const HASHED = new URL("./tool-select-hashed.jsonl", import.meta.url).pathname;
const TEXT = "/tmp/tool-select-pairs.jsonl";
const OUT = new URL("./rows-toolselect-jev.jsonl", import.meta.url).pathname;
const MODEL = "jev-1.13.0";
const LABELS12 = ["bash","read","eval","edit","hub","write","grep","yield","glob","todo","web_search","task"];
const INSTR = "Given this prior tool-call context, pick the tool the agent calls next. Answer with exactly one label.";

function args() {
  const m = {};
  for (let i = 2; i < process.argv.length; i += 2) m[process.argv[i].replace(/^--/, "")] = Number(process.argv[i + 1]);
  return { start: m.start ?? 0, count: m.count ?? 400 };
}
function mcnemar(b, c) {
  const n = b + c;
  if (n === 0) return 1.0;
  const lo = Math.min(b, c);
  const comb = (nn, k) => { let r = 1; for (let i = 0; i < k; i++) r = r * (nn - i) / (i + 1); return r; };
  let p = 0;
  for (let k = 0; k <= lo; k++) p += comb(n, k) / 2 ** n;
  return Math.min(1.0, 2 * p);
}
const { start, count } = args();
const hashed = readFileSync(HASHED, "utf8").split("\n").filter(Boolean);
const texts = readFileSync(TEXT, "utf8").split("\n").filter(Boolean);
const done = new Set();
if (existsSync(OUT)) for (const l of readFileSync(OUT, "utf8").split("\n").filter(Boolean)) {
  try { done.add(JSON.parse(l).id); } catch {}
}
const criteria = Object.fromEntries(LABELS12.map((l) => [l, l]));
let ok = 0, fail = 0, jevCorrect = 0, bashCorrect = 0, b = 0, c = 0;
const ids = [];
for (let i = start; i < start + count && i < hashed.length - 1; i++) {
  const id = `ts-${String(i).padStart(5, "0")}`;
  const hrow = JSON.parse(hashed[i + 1]);
  const trow = JSON.parse(texts[i]);
  if (hrow.label !== trow.label) { console.error(`ALIGN BREAK at ${id}`); process.exit(2); }
  ids.push({ id, label: hrow.label, context: trow.context });
}
const pending = ids.filter((r) => !done.has(r.id));
const CONC = 8;
for (let k = 0; k < pending.length; k += CONC) {
  const batch = await Promise.all(pending.slice(k, k + CONC).map(async (r) => {
    const t0 = Date.now();
    try {
      const res = await askJevChoice({ state: { context: r.context }, instructions: INSTR, classes: criteria, model: MODEL, timeoutMs: 20000 });
      return { r, res, ms: Date.now() - t0 };
    } catch (e) { return { r, err: String(e && e.message || e), ms: Date.now() - t0 }; }
  }));
  for (const { r, res, err, ms } of batch) {
    if (!res || !res.ok) { fail++; appendFileSync(OUT, JSON.stringify({ id: r.id, label: r.label, error: err || (res && res.reason) || "unknown", ms }) + "\n"); continue; }
    ok++;
    const choice = res.choice;
    const aJ = choice === r.label, aB = "bash" === r.label;
    jevCorrect += aJ ? 1 : 0; bashCorrect += aB ? 1 : 0;
    if (aJ && !aB) b++; else if (aB && !aJ) c++;
    appendFileSync(OUT, JSON.stringify({ id: r.id, label: r.label, choice, conf: res.confidence ?? null, ms }) + "\n");
  }
}
// NOTE: counts below cover rows decided THIS invocation; resume-skipped rows
// live in OUT. Tranche totals must be aggregated from OUT, not this print.
const n = ok + fail;
console.log(JSON.stringify({ start, count, decided_this_run: ok, failed_this_run: fail, jev_correct_this_run: jevCorrect, bash_correct_this_run: bashCorrect, discordants_this_run: { jev_only: c, bash_only: b }, mcnemar_p_this_run: mcnemar(b, c) }));
process.exit(fail > 2 ? 2 : 0);

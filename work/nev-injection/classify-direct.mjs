/**
 * Direct-Jev bulk classification (judge() backend down; Jev API verified live).
 * Rubric frozen before data; units = 41 verdict rows (header excluded by the
 * verdict-enum filter — the earlier 42-count included the header line).
 * One Choice per candidate: replacement | new_capability | mixed | unclear.
 * Truncates excerpts at 6000 chars with marker; counts truncations.
 * Persists per-row outputs (choice, confidence, probabilities) — R70.
 * Exit 0 (rows may carry errors; they are rows, not failures).
 */
import { askJevChoice } from "../jev-client/src/index.ts";
import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CAP = 6000;
const STATUS = "/Users/josh/Developer/jev/docs/demos/STATUS.tsv";
const VERDICTS = new Set(["CLEARED", "HELD", "RULED_OUT", "UNASKABLE", "PROMOTED", "RECUSED"]);

const INSTRUCTIONS =
  "One gauntlet candidate row with its receipt excerpt. Was the judged task something the lane already does today, or something not attempted at all?";
const CRITERIA = {
  replacement: "The receipt describes a task already performed today by a regex, an existing model call, a shipped rule, or routine hand work (triage, review, routing, compaction, ranking).",
  new_capability: "The receipt describes a task NOT attempted at all today — no existing regex, call, rule, or hand process does it.",
  mixed: "The receipt spans both: part replaces existing practice and part attempts something new.",
  unclear: "The excerpt does not say enough about current practice to decide.",
};

const units = [];
for (const line of readFileSync(STATUS, "utf8").split("\n")) {
  if (!line.trim()) continue;
  const p = line.split("\t");
  if (p.length < 4 || !VERDICTS.has(p[3])) continue;
  const rpath = "/Users/josh/Developer/jev/" + p[5];
  let ex, trunc = false;
  try {
    const txt = readFileSync(rpath, "utf8");
    trunc = txt.length > CAP;
    ex = trunc ? txt.slice(0, CAP) + "\n…[truncated]" : txt;
  } catch (e) {
    ex = "RECEIPT-UNREADABLE: " + String((e && e.message) || e);
  }
  units.push({ id: p[0], verdict: p[3], receipt: p[5], excerpt: ex, truncated: trunc });
}
console.log(`units=${units.length} truncated=${units.filter((u) => u.truncated).length}`);

const out = [];
for (const u of units) {
  const r = await askJevChoice({
    state: { candidate: u.id, verdict: u.verdict, excerpt: u.excerpt },
    instructions: INSTRUCTIONS,
    classes: CRITERIA,
    model: "jev-1.13.0",
    timeoutMs: 30000,
  });
  if (!r.ok) {
    out.push({ id: u.id, error: r.reason + ": " + r.error });
  } else {
    out.push({ id: u.id, choice: r.choice, confidence: r.confidence, probabilities: r.probabilities });
  }
  const done = out.length;
  const c = out[done - 1];
  console.log(`[${done}/${units.length}] ${u.id} -> ${c.error ? "ERROR " + c.error.slice(0, 60) : c.choice + " p=" + c.confidence.toFixed(2)}`);
}
writeFileSync(join(HERE, "classify-rows.jsonl"), out.map((o) => JSON.stringify(o)).join("\n") + "\n");
const errs = out.filter((o) => o.error).length;
console.log(`COMPLETE ${out.length - errs}/${out.length} -> classify-rows.jsonl`);

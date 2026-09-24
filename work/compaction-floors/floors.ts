// Cheap keep-signal floors for compaction (bead jev-al06), on the two labelled development sets
// (jev-x86y and jev-jec6). Definitions are preregistered in
// docs/demos/upstream-repro/compaction-floors-20260924.md. No Jev call. Writes numbers and ids only.
//
//   node --experimental-strip-types work/compaction-floors/floors.ts   # writes features-x86y.jsonl, features-jec6.jsonl
//
// Per prefix call, from the same cut the two readouts used (need.ts cut()):
//   position     the call's 1-based order among the prefix's paired calls (higher = more recent)
//   tool_class   2 read/grep/glob, 1 bash/eval, 0 anything else (write, edit, todo, hub, task, wait)
//   result_chars the result's length in characters
//   later_overlap  distinct identifiers from the call's input that appear in any later PREFIX message
//                  (visible at compaction time)
//   horizon_overlap  the same identifiers appearing in any HORIZON message. A reference only: it reads
//                  the future, so no compactor can use it.
import { createHash, timingSafeEqual } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { Message } from "../../fast-jev-compaction/dist/index.js";
import { cut, load, untilde } from "../compaction-need/need.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const SETS = [
  { name: "x86y", dir: join(ROOT, "work/compaction-need"), excluded: join(ROOT, "work/compaction-need/excluded.json") },
  { name: "jec6", dir: join(ROOT, "work/compaction-keep"), excluded: null },
];
const READS = new Set(["read", "grep", "glob"]);
const RUNS = new Set(["bash", "eval"]);
// An identifier: a run of 6+ path/name characters holding at least one of / . _ (paths, file names, ids).
const IDENT = /[A-Za-z0-9_./-]{6,}/g;

function identifiers(input: unknown): Set<string> {
  const out = new Set<string>();
  for (const m of JSON.stringify(input).matchAll(IDENT)) if (/[/._]/.test(m[0])) out.add(m[0]);
  return out;
}

function messageText(m: Message): string {
  return [m.text ?? "", ...(m.toolUses ?? []).map((u) => JSON.stringify(u.input)), ...(m.toolResults ?? []).map((r) => r.text ?? "")].join("\n");
}

function hits(ids: Set<string>, texts: readonly string[]): number {
  let n = 0;
  for (const id of ids) if (texts.some((t) => t.includes(id))) n += 1;
  return n;
}

for (const set of SETS) {
  const sessions = JSON.parse(readFileSync(join(set.dir, "sessions.json"), "utf8")).sessions;
  const excluded: Record<string, string> = set.excluded ? JSON.parse(readFileSync(set.excluded, "utf8")) : {};
  const rows = [];
  for (const s of sessions) {
    if (s.id in excluded) continue; // never read (jev-x86y amendment A1)
    const bytes = readFileSync(untilde(s.path));
    if (!timingSafeEqual(createHash("sha256").update(bytes).digest(), Buffer.from(s.sha256, "hex"))) {
      throw new Error(`REFUSED: ${s.path} changed since it was sampled`);
    }
    const c = cut(load(untilde(s.path)))!;
    const horizonTexts = c.horizon.map(messageText);
    const results = new Map<string, number>();
    for (const m of c.prefix) for (const r of m.toolResults ?? []) results.set(r.tool_use_id, (r.text ?? "").length);
    c.prefixCalls.forEach((call, k) => {
      const ids = identifiers(call.input);
      const later = c.prefix.slice(call.resultIndex + 1).map(messageText);
      rows.push({
        session: s.id,
        tool_use_id: call.tool_use_id,
        pinned: call.pinned,
        position: k + 1,
        tool_class: READS.has(call.tool) ? 2 : RUNS.has(call.tool) ? 1 : 0,
        result_chars: results.get(call.tool_use_id) ?? 0,
        later_overlap: hits(ids, later),
        horizon_overlap: hits(ids, horizonTexts),
      });
    });
  }
  writeFileSync(join(HERE, `features-${set.name}.jsonl`), rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
  console.log(`${set.name}: ${rows.length} prefix calls`);
}

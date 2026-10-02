// LIVE-120 (bead jev-n4eu, BAR.md): stratified duel confirmation with real Jev.
// 60 planted (recorded-flagged) + 60 clean (recorded-clean), every 5th row.
// Real askJev both sides, temp logs, spend from billed tokens.
import { readFileSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { makeDuelHandler } from "/Users/josh/Developer/jev/.omp/hooks/post/jev-web-duel.ts";
import { useInfisicalKey } from "/Users/josh/Developer/jev/work/jev-client/src/use-infisical-key.ts";

useInfisicalKey();
const sha256 = (t) => createHash("sha256").update(t, "utf8").digest("hex");
const readJSON = (p) => JSON.parse(readFileSync(p, "utf8"));
const clean = readJSON("/Users/josh/Developer/jev/work/jev-injection-flag/tool-results-sample.json").rows;
const attacks = readFileSync("/Users/josh/Developer/jev/work/nev-injection/pairs.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l));
const selected = readJSON("/Users/josh/Developer/jev/work/jev-a9fv/CORPUS.json").selected_attack_indices;
const attacksByIndex = new Map(attacks.map((r, i) => [i, r]));
const texts = [];
for (let i = 0; i < 300; i++) texts.push({ set: "clean", text: clean[i].text });
let seq = 0;
for (const ai of selected) {
  const base = clean[seq++].text;
  const marker = `\n\n[UNTRUSTED TOOL OUTPUT]\n${attacksByIndex.get(ai).text}\n[/UNTRUSTED TOOL OUTPUT]\n`;
  for (const pos of ["start", "middle", "end"]) {
    const at = pos === "start" ? 0 : pos === "middle" ? Math.floor(base.length / 2) : base.length;
    texts.push({ set: "planted", text: base.slice(0, at) + marker + base.slice(at) });
  }
}
const rec = new Map();
for (const line of readFileSync("/Users/josh/Developer/jev/work/jev-a9fv/live-rows.jsonl", "utf8").trim().split("\n")) {
  const r = JSON.parse(line);
  rec.set(r.inputSha256, r);
}
const withRec = texts.map((t) => ({ ...t, rec: rec.get(sha256(t.text)) }));
const planted = withRec.filter((t) => t.set === "planted" && t.rec?.flag).filter((_, i) => i % 5 === 0).slice(0, 60);
const cleanSet = withRec.filter((t) => t.set === "clean" && !t.rec?.flag).filter((_, i) => i % 5 === 0).slice(0, 60);
console.log(JSON.stringify({ planted: planted.length, clean: cleanSet.length }));
const dir = mkdtempSync(join(tmpdir(), "duel-live120-"));
const sample = [...planted, ...cleanSet];
const out = [];
for (let c = 0; c < 6; c++) {
  const injRows = [];
  const duel = makeDuelHandler({ inj: { append: async (_p, line) => injRows.push(JSON.parse(line)) } });
  for (let k = 0; k < 20 && c * 20 + k < sample.length; k++) {
    const t = sample[c * 20 + k];
    const ev = { toolName: "web_search", content: [{ type: "text", text: JSON.stringify({ results: [{ title: `L${c * 20 + k}`, content: t.text }] }) }] };
    const r = await duel(ev);
    out.push({ set: t.set, recFlag: t.rec.flag, withheld: r !== undefined });
  }
  writeFileSync(join(dir, `inj-${c}.jsonl`), injRows.map((r) => JSON.stringify(r)).join("\n"));
}
const pc = out.filter((r) => r.set === "planted" && r.withheld).length;
const cw = out.filter((r) => r.set === "clean" && r.withheld).length;
console.log(JSON.stringify({ catch: `${pc}/60`, cleanWithhold: `${cw}/60`, dir }));

// The two committed corpora for bead jev-qip, as {i, id, label, text} rows in file order.
//   attacks  work/nev-injection/pairs.jsonl (662 public prompt-injection rows, label 1 = attack)
//   toolout  work/jev-injection-flag/tool-results-sample.json (300 real tool results; every row
//            adjudicated clean in work/jev-injection-flag/adjudication.json @ 888efbe, so label 0)
import { readFileSync } from 'node:fs';

export function loadCorpus(name) {
  if (name === 'attacks') {
    const lines = readFileSync(new URL('../nev-injection/pairs.jsonl', import.meta.url), 'utf8').split('\n').filter((l) => l.trim());
    return lines.map((l, i) => {
      const r = JSON.parse(l);
      return { i, id: r.id, label: r.label, text: r.text };
    });
  }
  if (name === 'toolout') {
    const s = JSON.parse(readFileSync(new URL('../jev-injection-flag/tool-results-sample.json', import.meta.url), 'utf8'));
    return s.rows.map((r, i) => ({ i, id: `tool-${i}`, label: 0, text: r.text }));
  }
  throw new Error(`unknown corpus ${name}`);
}

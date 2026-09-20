/**
 * Is the `prose` shape really beyond a cheap rule? Test it instead of asserting it.
 * Offline: no API calls. Reuses the same prose strings arm 2 sent to Jev.
 */
import { readFileSync } from 'node:fs';

const d = JSON.parse(readFileSync('/Users/josh/Developer/jev/work/toolcall-judge-v3/seat-freshness-real.json', 'utf8'));
const prose = d.results.find((r) => r.shape === 'prose');

function parseSemver(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)/.exec(String(v).replace(/^[\^~>=v ]+/, ''));
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
}
function cmp(a, b) {
  for (let i = 0; i < 3; i += 1) {
    if (b[i] > a[i]) return true;
    if (b[i] < a[i]) return false;
  }
  return false;
}

/** The cheap rule: pull every version-ish token out of the prose, in order, compare first two. */
function ruleOnProse(text) {
  const vs = [...text.matchAll(/\bv?(\d+\.\d+\.\d+)\b/g)].map((m) => m[1]);
  if (vs.length < 2) return null;
  const a = parseSemver(vs[0]);
  const b = parseSemver(vs[1]);
  if (!a || !b) return null;
  return cmp(a, b);
}

let decided = 0;
let correct = 0;
let undecided = 0;
const misses = [];
for (const row of prose.rows) {
  const text = `We currently run ${row.name} version ${row.pin}; the registry is publishing ${row.available} as latest.`;
  const said = ruleOnProse(text);
  if (said === null) {
    undecided += 1;
    continue;
  }
  decided += 1;
  if (said === row.behind) correct += 1;
  else misses.push({ name: row.name, pin: row.pin, available: row.available, oracle: row.behind, rule: said });
}
console.log(`cheap prose rule: decided ${decided}/${prose.rows.length}, undecided ${undecided}, correct ${correct}/${decided}`);
for (const m of misses) console.log('  MISS', m);
console.log(`jev on the same prose: correct ${prose.correct}/${prose.asked}, verdict ${prose.verdict}`);

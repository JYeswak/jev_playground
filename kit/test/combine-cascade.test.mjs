import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// combine-cascade.test.mjs — D8 combination/cascade reproduction (jev-b35c.4.1).
//
// Frozen method (advanced-mathops.md T8/T9, Appendix R). No live calls, no
// network, no model loads: pure math over committed paired rows. Verdict
// vocabulary is EXPLORED (reproduction of published numbers), never a win
// claim for either arm.
//
// T8 cascade: Platt GD fit on Jev dev (2000 iters, lr 0.1, init a=1 b=0,
//   logit clamp 1e-4, mirrored from work/local-decision-arms/run.py platt());
//   tau = smallest dev cutoff with cascade dev accuracy >= Clef dev - .01.
//   Exact recomputation pins tau=.7733 (asserted to 4dp below, plus
//   membership in the dev calibrated-score set). Published tau=.75 differs;
//   no inspected source establishes its grid/rounding, so it is recorded
//   here as an unresolved reference discrepancy, NOT absorbed by tolerance.
// T9 stacking: 2-feature Newton logistic (L2 1e-3, 100 iters) on dev logits;
//   held AUCs plus DeLong paired p (structural V10/V01, normal p).
// Row identity: exact id-set joins between arms; any mismatch refuses.

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

const FILES = {
  jevFull: 'work/choice-banking77/rows-full-jev.jsonl',
  clefHeld: 'work/local-decision-arms/rows-clefflash.jsonl',
  clefDev: 'work/local-decision-arms/rows-clefflash-dev.jsonl',
  vendorJev: 'work/vendor-paste/vendor-rows.jsonl',
  vendorSample: 'work/vendor-paste/sample.json',
  vendorClef: 'work/local-decision-arms/vendor-rows-clefflash.jsonl',
  vendorClefDev: 'work/local-decision-arms/vendor-rows-clefflash-dev.jsonl',
};

const FILE_SHA256 = {
  jevFull: '791dc645bfb1a0c99a30dd36e38eff5af9dcfb47d63bb46edfb39b2b418683e3',
  clefHeld: '850fc6f6d6017121e9eb5bc26eb7a92529821c73ca3796c25631b47c4456becb',
  clefDev: '6eed954a8c51fda2303f595c439eec46af2b75bbe72a32b2f8ba9dd8d7681099',
  vendorJev: '00c3346b5ebc4364fba29675c1d77a2409a4b7ed9c82207c5091c42434c2cb38',
  vendorSample: '2a167ed69ebfa5aa41399b278c14c1dae5a40ec630f4de97cfbb7faaa39644ab',
  vendorClef: '6dab05529656568df232de6fe42f9a808c28cbff221f6f158f189d885c12c11a',
  vendorClefDev: 'd7cd03394145a288ec9c808867a8613e2591520c7bd080f9ccf65d145a54c0ab',
};

function readJsonl(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));
}

function logit(p) {
  const c = Math.min(Math.max(Number(p) || 0, 1e-4), 1 - 1e-4);
  return Math.log(c / (1 - c));
}

// Standard normal CDF via Abramowitz-Stegun erf (|eps| <= 1.5e-7),
// with the required z/sqrt(2) scaling: Phi(z) = 0.5*(1+erf(z/sqrt(2))).
function phi(z) {
  const x = z / Math.SQRT2;
  const t = 1 / (1 + 0.3275911 * Math.abs(x));
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
  const erf = 1 - poly * Math.exp(-x * x);
  return 0.5 * (1 + (x < 0 ? -erf : erf));
}

function auc(pos, neg) {
  let c = 0;
  for (const a of pos) for (const b of neg) c += a > b ? 1 : (a === b ? 0.5 : 0);
  return c / (pos.length * neg.length);
}

// Exact two-sided McNemar (binomial) on discordant counts.
function mcnemar(a, b) {
  const n = a + b;
  if (n === 0) return 1;
  const m = Math.min(a, b);
  let s = 0;
  let comb = 1;
  for (let k = 0; k <= m; k++) {
    if (k > 0) comb = (comb * (n - k + 1)) / k;
    s += comb;
  }
  return Math.min(1, (2 * s) / 2 ** n);
}

// DeLong paired AUC comparison: structural V10/V01, paired covariance,
// two-sided normal p (Appendix R).
function delong(ids, labels, s1, s2) {
  const P = ids.filter((i) => labels[i]);
  const N = ids.filter((i) => !labels[i]);
  for (const i of [...P, ...N]) {
    for (const s of [s1, s2]) {
      const v = s(i);
      if (typeof v !== 'number' || !Number.isFinite(v)) throw new Error('DeLong score not finite');
    }
  }
  const m = P.length;
  const n = N.length;
  const V10 = (s, i) => N.reduce((t, j) => t + (s(i) > s(j) ? 1 : (s(i) === s(j) ? 0.5 : 0)), 0) / n;
  const V01 = (s, j) => P.reduce((t, i) => t + (s(i) > s(j) ? 1 : (s(i) === s(j) ? 0.5 : 0)), 0) / m;
  const cov = (a, b) => {
    const ma = a.reduce((t, v) => t + v, 0) / a.length;
    const mb = b.reduce((t, v) => t + v, 0) / b.length;
    return a.reduce((t, v, k) => t + (v - ma) * (b[k] - mb), 0) / (a.length - 1);
  };
  const v10a = P.map((i) => V10(s1, i));
  const v10b = P.map((i) => V10(s2, i));
  const v01a = N.map((j) => V01(s1, j));
  const v01b = N.map((j) => V01(s2, j));
  const v = (cov(v10a, v10a) / m + cov(v01a, v01a) / n)
    + (cov(v10b, v10b) / m + cov(v01b, v01b) / n)
    - 2 * (cov(v10a, v10b) / m + cov(v01a, v01b) / n);
  const a1 = auc(P.map(s1), N.map(s1));
  const a2 = auc(P.map(s2), N.map(s2));
  const delta = a1 - a2;
  if (!Number.isFinite(delta)) throw new Error('DeLong AUC delta not finite');
  if (delta === 0) return 1; // identical rankings: nothing to detect
  if (!Number.isFinite(v) || v < 0) throw new Error('DeLong variance not finite/nonnegative');
  if (v === 0) return 0; // perfect opposite separation: maximally significant
  const z = delta / Math.sqrt(v);
  return 2 * (1 - phi(Math.abs(z)));
}

function plattFit(xs) {
  let a = 1;
  let b = 0;
  for (let iter = 0; iter < 2000; iter++) {
    let ga = 0;
    let gb = 0;
    for (const [x, y] of xs) {
      const p = 1 / (1 + Math.exp(-(a * x + b)));
      ga += (p - y) * x;
      gb += p - y;
    }
    a -= (0.1 * ga) / xs.length;
    b -= (0.1 * gb) / xs.length;
  }
  return [a, b];
}

function newtonLogistic(X, y, lambda, iters) {
  const w = [0, 0, 0];
  for (let iter = 0; iter < iters; iter++) {
    const g = [0, 0, 0];
    const H = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let r = 0; r < X.length; r++) {
      const [x1, x2] = X[r];
      const p = 1 / (1 + Math.exp(-(w[0] + w[1] * x1 + w[2] * x2)));
      const e = p - y[r];
      const f = [1, x1, x2];
      for (let j = 0; j < 3; j++) g[j] += e * f[j];
      for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) H[j][k] += p * (1 - p) * f[j] * f[k];
    }
    for (let j = 0; j < 3; j++) {
      g[j] += lambda * w[j];
      H[j][j] += lambda;
    }
    const M = H.map((row, j) => [...row, g[j]]);
    for (let col = 0; col < 3; col++) {
      let piv = col;
      for (let r = col + 1; r < 3; r++) if (Math.abs(M[r][col]) > Math.abs(M[piv][col])) piv = r;
      [M[col], M[piv]] = [M[piv], M[col]];
      for (let r = 0; r < 3; r++) {
        if (r !== col && M[col][col] !== 0) {
          const f = M[r][col] / M[col][col];
          for (let k = col; k < 4; k++) M[r][k] -= f * M[col][k];
        }
      }
    }
    const d = M.map((row, j) => row[3] / row[j]);
    for (let j = 0; j < 3; j++) w[j] -= d[j];
  }
  return w;
}

function shaFile(rel) {
  return createHash('sha256').update(fs.readFileSync(path.join(ROOT, rel))).digest('hex');
}

function checkBankingJoins(jev, ch, cd) {
  const heldIds = [...ch.keys()].sort((a, b) => a - b);
  const devIds = [...cd.keys()].sort((a, b) => a - b);
  assert.equal(heldIds.length, 600);
  assert.equal(devIds.length, 200);
  for (const i of [...heldIds, ...devIds]) {
    if (!jev.has(i)) throw new Error(`unmatched row id across arms: ${i}`);
  }
  for (const i of devIds) {
    if (ch.has(i)) throw new Error(`dev/held overlap: ${i}`);
  }
  return { heldIds, devIds };
}

function checkVendorJoins(vdevIds, vheldIds, vjev, vclef, vclefDev, lab) {
  assert.equal(vdevIds.length, 120);
  assert.equal(vheldIds.length, 200);
  for (const i of [...vdevIds, ...vheldIds]) {
    if (!vjev.has(i) || lab[i] === undefined) throw new Error(`unmatched vendor id: ${i}`);
  }
  for (const i of vheldIds) {
    if (!vclef.has(i)) throw new Error(`missing vendor held clef row: ${i}`);
  }
  for (const i of vdevIds) {
    if (!vclefDev.has(i)) throw new Error(`missing vendor dev clef row: ${i}`);
  }
}

function loadAll() {
  for (const [key, rel] of Object.entries(FILES)) {
    assert.equal(shaFile(rel), FILE_SHA256[key], `input hash drift: ${rel}`);
  }
  const jev = new Map(readJsonl(FILES.jevFull).map((r) => [r.i, r]));
  const ch = new Map(readJsonl(FILES.clefHeld).map((r) => [r.i, r]));
  const cd = new Map(readJsonl(FILES.clefDev).map((r) => [r.i, r]));
  const { heldIds, devIds } = checkBankingJoins(jev, ch, cd);
  const sample = JSON.parse(fs.readFileSync(path.join(ROOT, FILES.vendorSample), 'utf8'));
  const lab = {};
  for (const r of [...sample.dev, ...sample.held]) {
    lab[r.sample_id] = ['1', 'true', 'vendored', 'pos', 'yes'].includes(String(r.label).toLowerCase());
  }
  const vjev = new Map(readJsonl(FILES.vendorJev).map((r) => [r.sample_id, r.noul]));
  const vclef = new Map(readJsonl(FILES.vendorClef).map((r) => [r.sample_id, r.noul]));
  const vclefDev = new Map(readJsonl(FILES.vendorClefDev).map((r) => [r.sample_id, r.noul]));
  const vdevIds = sample.dev.map((r) => r.sample_id);
  const vheldIds = sample.held.map((r) => r.sample_id);
  checkVendorJoins(vdevIds, vheldIds, vjev, vclef, vclefDev, lab);
  return { jev, ch, cd, heldIds, devIds, lab, vjev, vclef, vclefDev, vdevIds, vheldIds };
}

const pchoice = (r) => (r.probabilities || {})[r.choice];

test('T8 cascade reproduces the published Banking77 outcome as EXPLORED', () => {
  const { jev, ch, cd, heldIds, devIds } = loadAll();
  const xs = devIds.map((i) => [logit(pchoice(jev.get(i))), (jev.get(i).choice === jev.get(i).intent) ? 1 : 0]);
  const [a, b] = plattFit(xs);
  const cal = (i) => 1 / (1 + Math.exp(-(a * logit(pchoice(jev.get(i))) + b)));
  const acc = (ids, arm) => ids.filter((i) => {
    const r = arm === 'jev' ? jev.get(i) : cd.get(i);
    return r.choice === r.intent;
  }).length / ids.length;
  const bar = acc(devIds, 'clef') - 0.01;
  const taus = [...new Set(devIds.map(cal))].sort((x, y) => x - y);
  const good = taus.filter((t) => {
    const n = devIds.filter((i) => (cal(i) >= t ? jev.get(i).choice === jev.get(i).intent : cd.get(i).choice === cd.get(i).intent)).length;
    return n / devIds.length >= bar;
  });
  const tau = Math.min(...good);
  assert.ok(taus.includes(tau), 'tau must be a dev calibrated score');
  assert.equal(tau.toFixed(4), '0.7733');
  const deferred = heldIds.filter((i) => cal(i) < tau).length / heldIds.length;
  let ok = 0;
  let eOnly = 0;
  let cOnly = 0;
  for (const i of heldIds) {
    const cascOk = cal(i) >= tau ? jev.get(i).choice === jev.get(i).intent : ch.get(i).choice === ch.get(i).intent;
    const clefOk = ch.get(i).choice === ch.get(i).intent;
    ok += cascOk ? 1 : 0;
    eOnly += cascOk && !clefOk ? 1 : 0;
    cOnly += !cascOk && clefOk ? 1 : 0;
  }
  assert.ok(Math.abs(deferred - 0.422) < 0.005, `deferred ${deferred}`);
  assert.ok(Math.abs(ok / heldIds.length - 0.942) < 0.005, `accuracy ${ok / heldIds.length}`);
  assert.deepEqual([eOnly, cOnly], [0, 12]);
  assert.ok(Math.abs(mcnemar(eOnly, cOnly) - 0.0005) < 0.0002, `mcnemar ${mcnemar(eOnly, cOnly)}`);
});

test('T9 stacking reproduces the published vendor outcome as EXPLORED', () => {
  const { lab, vjev, vclef, vclefDev, vdevIds, vheldIds } = loadAll();
  const X = vdevIds.map((i) => [logit(vjev.get(i)), logit(vclefDev.get(i))]);
  const y = vdevIds.map((i) => (lab[i] ? 1 : 0));
  const w = newtonLogistic(X, y, 1e-3, 100);
  const sj = (i) => vjev.get(i);
  const sc = (i) => vclef.get(i);
  const ss = (i) => 1 / (1 + Math.exp(-(w[0] + w[1] * logit(vjev.get(i)) + w[2] * logit(vclef.get(i)))));
  const aucOf = (fn) => {
    const pos = vheldIds.filter((i) => lab[i]).map(fn).sort((x, y) => y - x);
    const neg = vheldIds.filter((i) => !lab[i]).map(fn).sort((x, y) => y - x);
    return auc(pos, neg);
  };
  assert.ok(Math.abs(aucOf(sj) - 0.8275) < 0.0005, `jev auc ${aucOf(sj)}`);
  assert.ok(Math.abs(aucOf(sc) - 0.8388) < 0.0005, `clef auc ${aucOf(sc)}`);
  assert.ok(Math.abs(aucOf(ss) - 0.8615) < 0.0005, `stack auc ${aucOf(ss)}`);
  const labels = Object.fromEntries(vheldIds.map((i) => [i, lab[i]]));
  assert.ok(Math.abs(delong(vheldIds, labels, ss, sj) - 0.005) < 0.003, `delong stack/jev ${delong(vheldIds, labels, ss, sj)}`);
  assert.ok(Math.abs(delong(vheldIds, labels, ss, sc) - 0.21) < 0.06, `delong stack/clef ${delong(vheldIds, labels, ss, sc)}`);
});

test('a dropped paired row refuses instead of silently narrowing the denominator', () => {
  const full = loadAll();
  const short = new Map(full.ch);
  short.delete(full.heldIds[0]);
  assert.throws(() => {
    checkBankingJoins(full.jev, short, full.cd);
  }, /600/);
});

test('a flipped label moves the pinned numbers (sensitivity, not self-consistency)', () => {
  const full = loadAll();
  const flipped = new Map([...full.ch.entries()].map(([i, r]) => [i, { ...r }]));
  const victim = full.heldIds.find((i) => full.jev.get(i).choice === full.jev.get(i).intent);
  flipped.get(victim).choice = 'definitely_not_' + flipped.get(victim).choice;
  const acc = full.heldIds.filter((i) => {
    const r = flipped.get(i);
    return r.choice === full.jev.get(i).intent;
  }).length / full.heldIds.length;
  assert.ok(Math.abs(acc - 0.9617) > 0.001, `flipped label left clef accuracy unchanged: ${acc}`);
});

test('math controls: known normal tail and DeLong degenerate cases', () => {
  assert.ok(Math.abs(phi(0) - 0.5) < 1e-6, `phi(0)=${phi(0)}`);
  assert.ok(Math.abs(2 * (1 - phi(1.6448536269514722)) - 0.1) < 1e-4, `tail=${2 * (1 - phi(1.6448536269514722))}`);
  assert.ok(Math.abs(mcnemar(12, 0) - 0.00048828125) < 1e-9, `mcnemar=${mcnemar(12, 0)}`);
  const ids = [0, 1, 2, 3];
  const labels = { 0: true, 1: true, 2: false, 3: false };
  const s = (i) => i;
  assert.equal(delong(ids, labels, s, s), 1);
  const r = (i) => -i;
  assert.equal(delong(ids, labels, s, r), 0);
  const bad = (i) => (i === 0 ? NaN : i);
  assert.throws(() => delong(ids, labels, s, bad), /not finite/);
});

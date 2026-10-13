import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// measurement-calibration.test.mjs — D2 symmetric calibration + D7 rerun spread (jev-b35c.23).
//
// Frozen parameters live in the bead acceptance, fixed before implementation; this file
// reproduces them from committed rows only. No live call, no network, no post-hoc bars.
//
// Method (equal treatment both arms):
// - Id sets: DEV 200 / held 600 are the id sets of the committed Clef files, verified
//   identical to run.py:24-26 SAMPLE (seed 7) / DEV (seed 8) on 2026-10-12
//   (600 held ids == SAMPLE, 200 dev ids == DEV, disjoint, all in full.jsonl 0..3079).
// - Floor (frozen D2 method): EACH full multiclass probability vector is floored at
//   0.005 per entry and renormalised (divide by the floored sum); the held top-1
//   confidence is the renormalised top-1. The floor+renormalise transform is monotone,
//   so the top-1 label is unchanged while its confidence is rescaled. Binding MATH
//   REVIEW .10 and bead AC ("probabilities floored at 0.005 and renormalised").
//   Scalar-only flooring of the top-1 confidence does NOT satisfy the frozen method.
// - Platt: 1-D logistic regression on logit(p), gradient descent mirrored exactly from
//   work/local-decision-arms/run.py platt(): init a=1 b=0, 2000 iters, lr 0.1, logit clamp 1e-4.
// - ECE: 10 equal-width bins mirrored from run.py ece(): bin min(floor(p*10),9), skip empty,
//   weight len(bin)/n. On the held top-1 confidence.
// - Bootstrap: paired by id (Jev minus Clef Platt ECE), 2000 resamples of the 600 held ids
//   with replacement, mulberry32(0); CI = sorted 2.5th/97.5th percentiles (indices 50/1949).
//   RNG streams differ across languages; the precommitted +-0.005 endpoint tolerance covers
//   Monte Carlo jitter (verified: python reference gives [-0.011, +0.037]).
// - McNemar: two-sided exact binomial on discordant counts (b = correct->wrong,
//   c = wrong->correct); r2v3 reproduces the committed p = .0076 as an implementation
//   cross-check. Alarm iff net degradation > envelope AND p < .05.
// - Verdict vocabulary: a CI containing 0 is NO DETECTED DIFFERENCE (never a tie);
//   fewer than 3 committed runs is NOT_CALIBRATED; the envelope is labelled a 3-run
//   envelope, not a tail estimate.

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const B77 = path.join(ROOT, 'work', 'choice-banking77');
const ARMS = path.join(ROOT, 'work', 'local-decision-arms');

const FLOOR = 0.005;
const PLATT_ITERS = 2000;
const PLATT_LR = 0.1;
const BOOT_RESAMPLES = 2000;
const BOOT_SEED = 0;

function readJsonl(p) {
  return fs.readFileSync(p, 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// log-gamma (Lanczos) for exact binomial terms without overflow.
function lgamma(x) {
  const c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
    771.32342877765313, -176.61502916214059, 12.507343278686905,
    -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x);
  x -= 1;
  let a = c[0];
  for (let i = 1; i < 9; i++) a += c[i] / (x + i);
  const t = x + 7.5;
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}
// Two-sided exact McNemar p on discordant counts (b = correct->wrong, c = wrong->correct):
// sum of binomial(n, k)/2^n for k <= min(b,c) and k >= max(b,c), terms via stable recurrence.
function binomTerm(n, k) {
  return Math.exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1) - n * Math.LN2);
}

function mcnemarTwoSided(b, c) {
  const n = b + c;
  if (n === 0) return 1;
  const lo = Math.min(b, c); const hi = Math.max(b, c);
  const stepUp = (k) => (n - k) / (k + 1); // term(k+1)/term(k)
  let p = binomTerm(n, lo);
  for (let down = p, k = lo; k > 0; k--) { down = down / stepUp(k - 1); p += down; }
  if (hi > lo) {
    let up = binomTerm(n, hi);
    p += up;
    for (let k = hi; k < n; k++) { up = up * stepUp(k); p += up; }
  }
  return Math.min(1, p);
}

function logit(p) {
  const c = Math.min(Math.max(p, 1e-4), 1 - 1e-4);
  return Math.log(c / (1 - c));
}

function fitPlatt(xs) {
  let a = 1; let b = 0;
  for (let it = 0; it < PLATT_ITERS; it++) {
    let ga = 0; let gb = 0;
    for (const [x, y] of xs) {
      const p = 1 / (1 + Math.exp(-(a * x + b)));
      ga += (p - y) * x; gb += p - y;
    }
    a -= PLATT_LR * ga / xs.length; b -= PLATT_LR * gb / xs.length;
  }
  return { a, b };
}

function ece(pairs) {
  const bins = Array.from({ length: 10 }, () => []);
  for (const [p, ok] of pairs) bins[Math.min(Math.floor(p * 10), 9)].push([p, ok]);
  const n = pairs.length;
  return bins.filter((bin) => bin.length).reduce((s, bin) =>
    s + (bin.length / n) * Math.abs(
      bin.reduce((t, [p]) => t + p, 0) / bin.length - bin.reduce((t, [, ok]) => t + (ok ? 1 : 0), 0) / bin.length), 0);
}

// ---- Committed rows, loaded once ----

const fullRows = readJsonl(path.join(B77, 'full.jsonl'));
const INTENTS = [...new Set(fullRows.map((r) => r.intent))].sort((a, b) => {
  // Mirrors run.py key=(c.casefold(), c); labels are ASCII snake_case so toLowerCase is exact.
  const al = a.toLowerCase(); const bl = b.toLowerCase();
  if (al < bl) return -1; if (al > bl) return 1;
  return a < b ? -1 : a > b ? 1 : 0;
});
const LABELS = Object.fromEntries(INTENTS.map((c) => [c.replace(/_/g, ' ').toLowerCase(), c]));

const clefHeld = readJsonl(path.join(ARMS, 'rows-clefflash.jsonl'));
const clefDev = readJsonl(path.join(ARMS, 'rows-clefflash-dev.jsonl'));
const SAMP = new Set(clefHeld.map((r) => r.i));
const DEVIDS = new Set(clefDev.map((r) => r.i));

function normChoice(c) { return LABELS[c] ?? c; }

function jevTop1(row) {
  const probs = row.probabilities;
  if (!probs || typeof probs !== 'object') return { status: 'REFUSE', reason: 'missing probabilities' };
  const keys = Object.keys(probs);
  if (keys.length === 0) return { status: 'REFUSE', reason: 'empty probabilities' };
  for (const k of keys) {
    if (!Number.isFinite(Number(probs[k]))) return { status: 'REFUSE', reason: 'non-finite probability' };
  }
  return { status: 'OK', probs };
}

// Scalar floor guard for scalar confidences (Clef p_choice: no vector exists there).
function floorScalar(conf) {
  const f = Math.max(conf, FLOOR);
  return { conf: f, bound: conf < FLOOR };
}

// Frozen D2 vector floor: floor every entry at FLOOR, renormalise by the floored sum.
// Monotone, so the argmax label matches the raw top-1; confidence is rescaled.
function floorRenorm(probs) {
  let sum = 0; let boundEntries = 0; let best = null; let bestF = -1;
  const floored = {};
  for (const [k, v] of Object.entries(probs)) {
    const p = Number(v);
    const f = Math.max(p, FLOOR);
    if (f !== p) boundEntries++;
    sum += f;
    floored[k] = f;
    if (f > bestF) { bestF = f; best = k; }
  }
  return { label: best, conf: bestF / sum, boundEntries, n: Object.keys(floored).length };
}

function loadJevArm(suffix) {
  return readJsonl(path.join(B77, `rows-full-jev${suffix}.jsonl`));
}

// Calibrate one arm: fit Platt on its DEV ids, return held (id -> [conf, correct]) plus fit metadata.
function calibrate(getRows, isJev) {
  const devRows = getRows().filter((r) => DEVIDS.has(r.i));
  const heldRows = getRows().filter((r) => SAMP.has(r.i));
  let flooredCount = 0;
  const toPair = (r) => {
    let label; let conf; let ok;
    if (isJev) {
      const t = jevTop1(r);
      if (t.status !== 'OK') return { status: t.status, reason: t.reason };
      const f = floorRenorm(t.probs);
      if (f.boundEntries > 0) flooredCount++;
      label = normChoice(f.label); conf = f.conf;
      ok = normChoice(r.choice) === r.intent;
    } else {
      if (r.p_choice === undefined || r.p_choice === null) return { status: 'REFUSE', reason: 'missing p_choice' };
      const f = floorScalar(Number(r.p_choice));
      if (f.bound) flooredCount++;
      conf = f.conf;
      ok = r.choice === r.intent;
    }
    return { status: 'OK', conf, ok };
  };
  const devPairs = [];
  for (const r of devRows) {
    const p = toPair(r);
    if (p.status !== 'OK') return { status: p.status, reason: p.reason };
    devPairs.push([logit(p.conf), p.ok ? 1 : 0]);
  }
  const { a, b } = fitPlatt(devPairs);
  const apply = (conf) => 1 / (1 + Math.exp(-(a * logit(conf) + b)));
  const held = new Map();
  for (const r of heldRows) {
    const p = toPair(r);
    if (p.status !== 'OK') return { status: p.status, reason: p.reason };
    held.set(r.i, [apply(p.conf), p.ok]);
  }
  return { status: 'OK', held, a, b, devN: devPairs.length, heldN: held.size, flooredCount };
}

function pairedBootstrapCI(mapA, mapB, ids) {
  const rng = mulberry32(BOOT_SEED);
  const diffs = [];
  for (let s = 0; s < BOOT_RESAMPLES; s++) {
    const sample = [];
    for (let k = 0; k < ids.length; k++) sample.push(ids[Math.floor(rng() * ids.length)]);
    diffs.push(ece(sample.map((i) => mapA.get(i))) - ece(sample.map((i) => mapB.get(i))));
  }
  diffs.sort((x, y) => x - y);
  return { lo: diffs[50], hi: diffs[1949] };
}

function verdictForCI(lo, hi) {
  return (lo <= 0 && 0 <= hi) ? 'NO DETECTED DIFFERENCE' : 'DETECTED DIFFERENCE';
}

// D7: discordants(refRows, candRows) over frozen ids. Degradation direction is
// reference-vs-candidate: cw = ref-ok and candidate-wrong, wc = ref-wrong and
// candidate-ok, net = cw - wc. Envelope pairs use (earlier, later) in the same direction.
function discordants(refRows, candRows) {
  const b = new Map(candRows.map((r) => [r.i, r]));
  let cw = 0; let wc = 0;
  for (const r of refRows) {
    const s = b.get(r.i);
    if (!s || !r.choice || !s.choice) continue;
    const aOk = normChoice(r.choice) === r.intent;
    const bOk = normChoice(s.choice) === s.intent;
    if (aOk && !bOk) cw++;
    if (!aOk && bOk) wc++;
  }
  return { cw, wc, net: cw - wc };
}

function envelopeOf(runs) {
  if (runs.length < 3) return { status: 'NOT_CALIBRATED', kind: 'needs 3 committed runs' };
  const pairs = [];
  for (let i = 0; i < runs.length; i++)
    for (let j = i + 1; j < runs.length; j++)
      pairs.push({ pair: [i, j], ...discordants(runs[i], runs[j]) });
  const top = pairs.reduce((m, p) => (p.net > m.net ? p : m), pairs[0]);
  return { status: 'OK', kind: '3-run envelope', envelope: top.net, pairs };
}

function alarmFor(net, p, envelope) {
  return net > envelope && p < 0.05;
}

// ---- Tests ----

test('id sets reproduce the frozen DEV 200 / held 600 split', () => {
  assert.equal(SAMP.size, 600);
  assert.equal(DEVIDS.size, 200);
  for (const i of DEVIDS) assert.ok(!SAMP.has(i), `dev id ${i} overlaps held`);
  for (const i of [...SAMP, ...DEVIDS]) {
    assert.ok(Number.isInteger(i) && i >= 0 && i < fullRows.length, `id ${i} outside full.jsonl`);
  }
});

test('D2 held ECE after Platt reproduces Jev .0276 within .002', () => {
  const cal = calibrate(() => loadJevArm(''), true);
  assert.equal(cal.status, 'OK');
  assert.equal(cal.devN, 200);
  assert.equal(cal.heldN, 600);
  assert.ok(cal.flooredCount > 0, `vector floor must bind on real rows, got ${cal.flooredCount}`);
  const e = ece([...cal.held.values()]);
  assert.ok(Math.abs(e - 0.0276) <= 0.002, `Jev ECE ${e}`);
});

test('D2 held ECE after Platt reproduces Clef .0246 within .002', () => {
  const cal = calibrate(() => [...clefDev, ...clefHeld], false);
  assert.equal(cal.status, 'OK');
  assert.equal(cal.devN, 200);
  assert.equal(cal.heldN, 600);
  assert.equal(cal.flooredCount, 0);
  const e = ece([...cal.held.values()]);
  assert.ok(Math.abs(e - 0.0246) <= 0.002, `Clef ECE ${e}`);
});

test('paired bootstrap CI reproduces [-.010, +.037] within .005 and reports NO DETECTED DIFFERENCE', () => {
  const jev = calibrate(() => loadJevArm(''), true);
  const clef = calibrate(() => [...clefDev, ...clefHeld], false);
  assert.equal(jev.status, 'OK');
  assert.equal(clef.status, 'OK');
  const ids = [...SAMP].sort((a, b) => a - b);
  const { lo, hi } = pairedBootstrapCI(jev.held, clef.held, ids);
  assert.ok(Math.abs(lo - -0.010) <= 0.005, `CI lo ${lo}`);
  assert.ok(Math.abs(hi - 0.037) <= 0.005, `CI hi ${hi}`);
  assert.equal(verdictForCI(lo, hi), 'NO DETECTED DIFFERENCE');
});

test('D7 three committed runs give envelope 17 on run2 vs run3, McNemar reproduces .0076', () => {
  const runs = [loadJevArm(''), loadJevArm('-run2'), loadJevArm('-run3')];
  for (const r of runs) assert.equal(r.length, 3080);
  const env = envelopeOf(runs);
  assert.equal(env.status, 'OK');
  assert.equal(env.kind, '3-run envelope');
  assert.equal(env.envelope, 17);
  const r2v3 = env.pairs.find((p) => p.pair[0] === 1 && p.pair[1] === 2);
  assert.deepEqual([r2v3.cw, r2v3.wc], [27, 10]);
  const p = mcnemarTwoSided(r2v3.cw, r2v3.wc);
  assert.ok(Math.abs(p - 0.0076) <= 0.0005, `McNemar p ${p}`);
  assert.equal(alarmFor(r2v3.net, p, env.envelope), false);
});

test('fewer than 3 committed runs returns NOT_CALIBRATED', () => {
  const runs = [loadJevArm(''), loadJevArm('-run2')];
  assert.equal(envelopeOf(runs).status, 'NOT_CALIBRATED');
});

test('planted quiet rerun (run3 re-scored against run2) stays quiet', () => {
  const runs = [loadJevArm(''), loadJevArm('-run2'), loadJevArm('-run3')];
  const env = envelopeOf(runs);
  assert.equal(env.status, 'OK');
  // Degradation direction is reference-vs-candidate: cw = ref-ok and candidate-wrong.
  const { cw, wc, net } = discordants(runs[1], runs[2]);
  assert.deepEqual([cw, wc], [27, 10]);
  assert.equal(alarmFor(net, mcnemarTwoSided(cw, wc), env.envelope), false);
});

test('planted 2% shift (62 fixed-seed flips) alarms', () => {
  const runs = [loadJevArm(''), loadJevArm('-run2'), loadJevArm('-run3')];
  const env = envelopeOf(runs);
  assert.equal(env.status, 'OK');
  const ref = runs[1];
  const cand = loadJevArm('-run3');
  const correctIds = cand.filter((r) => r.choice && normChoice(r.choice) === r.intent).map((r) => r.i);
  const rng = mulberry32(99);
  const pool = [...correctIds];
  const flipped = new Set();
  while (flipped.size < 62 && pool.length) flipped.add(pool.splice(Math.floor(rng() * pool.length), 1)[0]);
  assert.equal(flipped.size, 62);
  const shifted = cand.map((r) => {
    if (!flipped.has(r.i)) return r;
    const wrong = INTENTS.find((c) => c !== r.intent);
    return { ...r, choice: wrong };
  });
  const { cw, wc, net } = discordants(ref, shifted);
  const p = mcnemarTwoSided(cw, wc);
  assert.ok(net > env.envelope, `shifted net ${net} must exceed envelope ${env.envelope}`);
  assert.ok(p < 0.05, `shifted p ${p} must be significant`);
  assert.equal(alarmFor(net, p, env.envelope), true);
});

test('missing probabilities refuse instead of looking calibrated', () => {
  assert.deepEqual(jevTop1({ i: 1, choice: 'x' }), { status: 'REFUSE', reason: 'missing probabilities' });
  assert.deepEqual(jevTop1({ i: 1, choice: 'x', probabilities: {} }), { status: 'REFUSE', reason: 'empty probabilities' });
  const devId = [...DEVIDS][0];
  const devBad = calibrate(() => [{ i: devId, intent: INTENTS[0], choice: INTENTS[0] }], true);
  assert.equal(devBad.status, 'REFUSE');
  const heldId = [...SAMP][0];
  const goodDev = loadJevArm('').filter((r) => DEVIDS.has(r.i)).slice(0, 5);
  const heldBad = calibrate(() => [...goodDev, { i: heldId, intent: INTENTS[0], choice: INTENTS[0] }], true);
  assert.equal(heldBad.status, 'REFUSE');
});

test('vector floor+renormalise matches hand-computed values and preserves argmax', () => {
  const f = floorRenorm({ a: 0.9, b: 0.0, c: 0.001 });
  assert.equal(f.label, 'a');
  assert.equal(f.boundEntries, 2);
  assert.equal(f.n, 3);
  assert.ok(Math.abs(f.conf - 0.9 / 0.91) < 1e-12, `renormed top-1 ${f.conf}`);
  const g = floorRenorm({ a: 0.4, b: 0.35, c: 0.0 });
  assert.equal(g.label, 'a');
  assert.ok(Math.abs(g.conf - 0.4 / 0.755) < 1e-12, `renormed top-1 ${g.conf}`);
  assert.equal(floorScalar(0).conf, FLOOR);
  assert.equal(floorScalar(0).bound, true);
  assert.equal(floorScalar(0.25).conf, 0.25);
  assert.equal(floorScalar(0.25).bound, false);
});

test('coin-flip judge ECE exceeds its Bernoulli noise floor and fails the gate', () => {
  const n = 600;
  const noiseFloor = 2 * Math.sqrt(0.25 / n);
  const rng = mulberry32(4242);
  const pairs = [];
  for (let k = 0; k < n; k++) pairs.push([0.85 + 0.1 * rng(), rng() < 0.5]);
  const e = ece(pairs);
  assert.ok(e > noiseFloor, `coin-flip ECE ${e} must exceed noise floor ${noiseFloor}`);
  const jev = calibrate(() => loadJevArm(''), true);
  const clef = calibrate(() => [...clefDev, ...clefHeld], false);
  assert.ok(ece([...jev.held.values()]) < noiseFloor, 'Jev Platt ECE passes the gate');
  assert.ok(ece([...clef.held.values()]) < noiseFloor, 'Clef Platt ECE passes the gate');
});

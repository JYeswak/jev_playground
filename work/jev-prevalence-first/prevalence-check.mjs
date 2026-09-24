/**
 * prevalence-check: the prevalence-first skill's enforcement point (jev-vbh.6, P2).
 *
 * The skill = prevalence cell + near-threshold column printed BEFORE any verdict.
 * Order is enforced in code, not by convention:
 *   pass 1 — near-threshold count, printed FIRST;
 *   pass 2 — own-constant bar (majority share), printed SECOND;
 *   pass 3 — gradeQuestion verdict, computed LAST via measure-kit (never hand-claimed).
 * A drift assertion refuses to print a verdict if local arithmetic ever diverges
 * from the kit again (the drift that already cost this lane one corrected verdict).
 * Four set shapes, one output order (near-threshold, own-constant, verdict):
 *   checkPrevalence  — binary score + boolean truth (the original P2 contract);
 *   checkChoice      — multiclass choice + truth label: the constant is the majority class;
 *   checkLabelsOnly  — labels, no model scores yet: prints the bar to beat BEFORE any spend;
 *   checkUnlabeled   — no labels at all: refuses to print a constant or a verdict.
 *
 * CLI (see usage()): node work/jev-prevalence-first/prevalence-check.mjs <rows.jsonl> --truth <f> ...
 * Exit 0 DISCRIMINATES or DEFERRED, 3 WEAK or DEGENERATE (seat refused), 2 not computable,
 * 64 usage. Pure except for console output and the rows file read. Zero Jev calls.
 */
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { gradeQuestion, DEFAULT_THRESHOLD, NEAR_WINDOW } from '../jev-client/measure-kit.mjs';

export { DEFAULT_THRESHOLD, NEAR_WINDOW };

export function checkPrevalence({ samples, threshold = DEFAULT_THRESHOLD }) {
  const valid = samples.filter((s) => typeof s.score === 'number' && typeof s.truth === 'boolean');

  // Pass 1 FIRST: prevalence cell — near-threshold count before anything else.
  let near = 0;
  for (const s of valid) {
    if (Math.abs(s.score - threshold) < NEAR_WINDOW) near += 1;
  }
  console.log(`near-threshold: ${near}/${valid.length} (window ±${NEAR_WINDOW} around ${threshold})`);

  // Pass 2 SECOND: own-constant bar — what always-answering-the-majority scores.
  const trueCount = valid.filter((s) => s.truth).length;
  const alwaysYes = trueCount;
  const alwaysNo = valid.length - trueCount;
  const best = Math.max(alwaysYes, alwaysNo);
  const majority = alwaysYes >= alwaysNo ? 'yes' : 'no';
  const share = valid.length ? `${((best / valid.length) * 100).toFixed(1)}%` : 'n/a';
  console.log(`own-constant: always-${majority} ${best}/${valid.length} (majority share ${share})`);

  // Pass 3 LAST: the verdict is computed here, after both lines above are printed.
  const g = gradeQuestion(samples, threshold);
  if (g.near !== near) {
    throw new Error(`drift: local near ${near} !== kit near ${g.near} — fix the duplication, print nothing`);
  }
  if (g.best !== best) {
    throw new Error(`drift: local best ${best} !== kit best ${g.best} — fix the duplication, print nothing`);
  }
  console.log(`verdict: ${g.correct}/${g.asked} vs best-constant ${g.best} + near ${g.near} → ${g.verdict}`);
  return g;
}

function share(n, d) {
  return d ? `${((n / d) * 100).toFixed(1)}%` : 'n/a';
}

function majorityOf(labels) {
  const counts = new Map();
  for (const l of labels) counts.set(l, (counts.get(l) ?? 0) + 1);
  let label = null;
  let best = 0;
  for (const [l, c] of counts) if (c > best) [label, best] = [l, c];
  return { label, best, classes: counts.size };
}

/** Multiclass choice: the constant is always answering the majority class. */
export function checkChoice({ pairs }) {
  const valid = pairs.filter((p) => p.choice != null && p.truth != null);
  console.log('near-threshold: n/a (choice question, no threshold)');
  const { label, best, classes } = majorityOf(valid.map((p) => String(p.truth)));
  console.log(`own-constant: always-${label} ${best}/${valid.length} (majority share ${share(best, valid.length)}, ${classes} classes)`);
  const correct = valid.filter((p) => String(p.choice) === String(p.truth)).length;
  const constant = new Set(valid.map((p) => String(p.choice))).size <= 1;
  const verdict = constant ? 'DEGENERATE' : correct > best ? 'DISCRIMINATES' : 'WEAK';
  console.log(`verdict: ${correct}/${valid.length} vs best-constant ${best} → ${verdict}`);
  return { correct, asked: valid.length, best, near: 0, verdict };
}

/** Labels only, no scores: the bar any question on this set must beat, printed before any spend. */
export function checkLabelsOnly({ truths }) {
  const valid = truths.filter((t) => t != null).map(String);
  console.log('near-threshold: n/a (no scores yet)');
  const { label, best } = majorityOf(valid);
  console.log(`own-constant: always-${label} ${best}/${valid.length} (majority share ${share(best, valid.length)})`);
  console.log(`verdict: DEFERRED — no model scores; a question on this set must beat always-${label} ${best}/${valid.length}`);
  return { asked: valid.length, best, near: 0, verdict: 'DEFERRED' };
}

/** No labels: there is no constant to beat, so no verdict may be printed. */
export function checkUnlabeled({ rows, field }) {
  console.log('near-threshold: n/a (no labels)');
  console.log(`own-constant: NOT COMPUTABLE — 0 of ${rows} rows carry '${field}'`);
  console.log('verdict: REFUSED — label a sample of this set before any Jev question is judged on it');
  return { asked: 0, best: null, near: 0, verdict: 'REFUSED' };
}

/** Dotted-path field read: `label.describes` reads row.label.describes. */
export function field(row, path) {
  let v = row;
  for (const k of path.split('.')) {
    if (v == null || typeof v !== 'object') return undefined;
    v = v[k];
  }
  return v;
}

/** Binary truth from a raw label: booleans pass through, `positive` names the true value otherwise. */
export function toBool(raw, positive) {
  if (raw == null) return undefined;
  if (positive !== undefined) return String(raw) === positive;
  if (typeof raw === 'boolean') return raw;
  if (raw === 0 || raw === 1) return raw === 1;
  return undefined;
}

const EXIT = { DISCRIMINATES: 0, DEFERRED: 0, WEAK: 3, DEGENERATE: 3, REFUSED: 2 };

function usage() {
  return [
    'usage: prevalence-check.mjs <rows.jsonl> --truth <field> [--positive <value>]',
    '         [--score <field> [--threshold 0.5] | --choice <field>]',
    '         [--labels <labels.jsonl> --id <field>]',
    '  --score   binary: score >= threshold is "yes"; truth via --positive or a boolean/0-1 field',
    '  --choice  multiclass: constant = majority class of --truth',
    '  neither   labels only: prints the bar to beat before any model call',
    '  --labels  read --truth from a second file joined on --id',
    'exit: 0 DISCRIMINATES/DEFERRED, 3 WEAK/DEGENERATE, 2 not computable, 64 usage',
  ].join('\n');
}

export function parseArgs(argv) {
  const opts = { file: undefined, threshold: DEFAULT_THRESHOLD };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { if (opts.file) throw new Error(`unexpected argument: ${a}`); opts.file = a; continue; }
    const key = a.slice(2);
    const val = argv[++i];
    if (val === undefined) throw new Error(`${a} needs a value`);
    if (!['truth', 'positive', 'score', 'choice', 'labels', 'id', 'threshold'].includes(key)) throw new Error(`unknown flag ${a}`);
    opts[key] = key === 'threshold' ? Number(val) : val;
  }
  if (!opts.file || !opts.truth) throw new Error('rows file and --truth are required');
  if (opts.score && opts.choice) throw new Error('--score and --choice are exclusive');
  if (opts.labels && !opts.id) throw new Error('--labels needs --id');
  return opts;
}

/** Content-sniffed rows: a JSON array (any extension), a JSON object carrying
 * a `records` array (harvest-allowed.mjs output), else JSONL one object per
 * line. Extension-sniffing read a `.jsonl` file holding an array as one
 * unlabelled row (SPEC pass-8 gap, reproduced in-test). */
function readRows(path) {
  const text = readFileSync(path, 'utf8');
  try {
    const parsed = JSON.parse(text);
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.records)) return parsed.records;
  } catch {
    // not whole-file JSON: fall through to JSONL
  }
  return text.split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));
}

/** Run one set through the right check. Returns the result; prints the three lines plus a header. */
export function runSet(opts) {
  const rows = readRows(opts.file);
  let truthOf = (r) => field(r, opts.truth);
  if (opts.labels) {
    const byId = new Map(readRows(opts.labels).map((r) => [String(field(r, opts.id)), field(r, opts.truth)]));
    truthOf = (r) => byId.get(String(field(r, opts.id)));
  }
  const labelled = rows.filter((r) => truthOf(r) != null).length;
  console.log(`set: ${opts.file} rows=${rows.length} labelled=${labelled}`);
  if (labelled === 0) return checkUnlabeled({ rows: rows.length, field: opts.truth });
  if (opts.choice) {
    return checkChoice({ pairs: rows.map((r) => ({ choice: field(r, opts.choice), truth: truthOf(r) })) });
  }
  if (opts.score) {
    const samples = rows.map((r) => ({ score: field(r, opts.score), truth: toBool(truthOf(r), opts.positive) }));
    const usable = samples.filter((s) => typeof s.score === 'number' && typeof s.truth === 'boolean').length;
    if (usable === 0) throw new Error(`no row has both a numeric '${opts.score}' and a binary '${opts.truth}' (pass --positive for non-boolean labels)`);
    return checkPrevalence({ samples, threshold: opts.threshold });
  }
  return checkLabelsOnly({ truths: rows.map(truthOf) });
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (e) {
    console.error(`${e.message}\n${usage()}`);
    process.exit(64);
  }
  try {
    const r = runSet(opts);
    process.exit(EXIT[r.verdict] ?? 2);
  } catch (e) {
    console.error(`prevalence-check: ${e.message}`);
    process.exit(2);
  }
}

#!/usr/bin/env node
/**
 * Bead jev-bmn: what does one Jev answer bill, per question shape?
 * Plan (committed before the first call): docs/demos/upstream-repro/jev-billing-units-20260924.md
 *
 *   node work/jev-billing-units/measure.mjs            re-score the committed rows (no key, no network)
 *   infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node work/jev-billing-units/measure.mjs live      50 live calls per shape, resumable
 *
 * Live calls go through work/jev-client askJevBundle (the lane's only sanctioned caller), one
 * attempt per call, model pinned jev-1.13.0, with the EXACT state and question each unit's
 * runner sent (work/score-sst5/run.py, work/choice-banking77/run.py, work/noul-scifact/run.py),
 * on the first 50 rows of each committed sample. Every attempt is appended to rows-jev.jsonl,
 * failures included, so the spend is the file. Never prints a key.
 */
import { appendFileSync, existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { askJevBundle } from '../jev-client/src/index.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..');
const ROWS = join(HERE, 'rows-jev.jsonl');
const MODEL = 'jev-1.13.0';
const N = 50;
const CONCURRENCY = 4;
const TIMEOUT_MS = 30_000;

const readJsonl = (rel) => readFileSync(join(ROOT, rel), 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));

// Choice labels exactly as work/choice-banking77/run.py builds them: every intent in subset.jsonl,
// sorted by (casefold, name), underscores to spaces, lowercased; criteria {label: null}
// (Choice(criteria={label: None}) serialises to null values).
function bankingCriteria() {
  const intents = [...new Set(readJsonl('work/choice-banking77/subset.jsonl').map((r) => r.intent))]
    .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()) || (a < b ? -1 : a > b ? 1 : 0));
  return Object.fromEntries(intents.map((c) => [c.replace(/_/g, ' ').toLowerCase(), null]));
}

export const SHAPES = {
  score: {
    unit: 'work/score-sst5',
    sample: 'work/score-sst5/sample.jsonl',
    haikuRows: 'work/score-sst5/rows-haiku.jsonl',
    jevRows: 'work/score-sst5/rows-jev.jsonl',
    state: (r) => r.text,
    questions: () => ({
      sentiment: {
        type: 'score',
        instructions: 'How positive is this movie review sentence?',
        criteria: [
          'Very negative: strongly critical, scathing, or contemptuous',
          'Negative: somewhat critical or unfavorable',
          'Neutral: neither positive nor negative, or evenly mixed',
          'Positive: somewhat favorable or approving',
          'Very positive: strongly enthusiastic, glowing, or full of praise',
        ],
      },
    }),
  },
  choice: {
    unit: 'work/choice-banking77',
    sample: 'work/choice-banking77/subset.jsonl',
    haikuRows: 'work/choice-banking77/rows-haiku.jsonl',
    jevRows: 'work/choice-banking77/rows-jev.jsonl',
    state: (r) => ({ customer_message: r.text }),
    questions: () => ({
      intent: { type: 'choice', instructions: 'The primary intent of this customer banking message', criteria: bankingCriteria() },
    }),
  },
  noul: {
    unit: 'work/noul-scifact',
    sample: 'work/noul-scifact/sample.jsonl',
    haikuRows: 'work/noul-scifact/rows-haiku.jsonl',
    jevRows: 'work/noul-scifact/rows-jev.jsonl',
    state: (r) => ({ claim: r.claim, title: r.title, abstract: r.abstract }),
    questions: () => ({
      supports: {
        type: 'noul',
        instructions: 'Does the abstract support the claim?',
        criteria: {
          true: 'The abstract states the claim or directly implies that it is true',
          false: 'The abstract contradicts the claim, or does not address what the claim asserts',
        },
      },
    }),
  },
};

// Prices, read from the mirrored primary sources and refused if the cited line no longer says it.
export const PRICES = {
  jev: { file: 'docs-mirror/typesafe/models.md', line: 13, needle: '\\$42 / \\$0.042', inputPerMTok: 0.042, outputPerMTok: 0,
         note: 'models.md:13 "$42 / $0.042" per Btok / per Mtok for jev-1.13.0; :18 "Charged per input token. Output tokens are free."' },
  // Was line 16; the 2026-09-24 mirror refresh (jev-j5fo, 4f3e295) moved it to 18.
  jevOutputFree: { file: 'docs-mirror/typesafe/models.md', line: 18, needle: 'Charged per input token. Output tokens are free.' },
  haiku: { file: 'docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md', line: 90, needle: '"claude-haiku-4-5": (1.00, 5.00)', inputPerMTok: 1.0, outputPerMTok: 5.0,
           note: 'consistency_choice_cookbook.md:90 "claude-haiku-4-5": (1.00, 5.00), $ per 1M tokens, "prices + model ids as of 2026-07" (:89) — list price, not an invoice' },
};

export const SYNC_DOCS = './scripts/sync-docs.sh';

/**
 * Check each cited price line against the mirror. The mirror is gitignored (only
 * docs-mirror/MANIFEST.tsv is tracked; `./scripts/sync-docs.sh` fetches it), so a fresh clone
 * has none: that is NOT_RUN, never a pass and never a crash. A file that is present but no longer
 * says what we quote is a mismatch, and the scorer fails on it.
 * Returns { status: 'ok' | 'not_run' | 'mismatch', detail }.
 */
export function checkPrices(mirrorRoot = ROOT) {
  const missing = [...new Set(Object.values(PRICES).map((p) => p.file))].filter((f) => !existsSync(join(mirrorRoot, f)));
  if (missing.length) {
    return { status: 'not_run', detail: `price check NOT_RUN: mirror absent (${missing.join(', ')}); fetch it with ${SYNC_DOCS}, then re-score` };
  }
  const moved = [];
  for (const [name, p] of Object.entries(PRICES)) {
    const line = readFileSync(join(mirrorRoot, p.file), 'utf8').split('\n')[p.line - 1] ?? '';
    if (!line.includes(p.needle)) moved.push(`${name} expects ${JSON.stringify(p.needle)} at ${p.file}:${p.line}, found ${JSON.stringify(line)}`);
  }
  return moved.length
    ? { status: 'mismatch', detail: `price source moved: ${moved.join('; ')}` }
    : { status: 'ok', detail: 'price check: every cited price line still reads as quoted' };
}

function priorRows() {
  return existsSync(ROWS) ? readFileSync(ROWS, 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l)) : [];
}

async function live() {
  if (!process.env.TYPESAFE_API_KEY) {
    console.error('unconfigured: TYPESAFE_API_KEY unset, no call made (NOT_RUN)');
    return 2;
  }
  const done = new Set(priorRows().filter((r) => r.ok).map((r) => `${r.shape}:${r.i}`));
  const jobs = [];
  for (const [shape, spec] of Object.entries(SHAPES)) {
    const questions = spec.questions();
    for (const row of readJsonl(spec.sample).slice(0, N)) {
      if (!done.has(`${shape}:${row.i}`)) jobs.push({ shape, row, questions, state: spec.state(row) });
    }
  }
  console.error(`live: ${jobs.length} calls to make, ${done.size} already answered`);
  let ok = 0, failed = 0, next = 0;
  async function worker() {
    while (next < jobs.length) {
      const job = jobs[next++];
      // Tee the wire body so the row records usage exactly as sent, beside the client's reading of it.
      let rawUsage = null;
      const fetchImpl = async (url, init) => {
        const res = await globalThis.fetch(url, init);
        try { rawUsage = JSON.parse(await res.clone().text()).usage ?? null; } catch { rawUsage = null; }
        return res;
      };
      const r = await askJevBundle({ state: job.state, questions: job.questions, model: MODEL, timeoutMs: TIMEOUT_MS, fetchImpl });
      const out = { shape: job.shape, i: job.row.i, ok: r.ok, latencyMs: r.latencyMs, at: new Date().toISOString() };
      if (r.ok) {
        Object.assign(out, { resolvedModel: r.resolvedModel, usage: r.usage ?? null, rawUsage, answers: r.answers });
        ok++;
      } else {
        Object.assign(out, { reason: r.reason, error: r.error, rawUsage });
        failed++;
      }
      appendFileSync(ROWS, JSON.stringify(out) + '\n');
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));
  console.error(`live done: ok=${ok} failed=${failed}`);
  return failed ? 3 : 0;
}

const mean = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN);
const sum = (xs) => xs.reduce((a, b) => a + b, 0);
function quantile(xs, q) {
  const s = [...xs].sort((a, b) => a - b);
  if (!s.length) return NaN;
  const idx = (s.length - 1) * q;
  const lo = Math.floor(idx), hi = Math.ceil(idx);
  return s[lo] + (s[hi] - s[lo]) * (idx - lo);
}
const f = (x, d = 1) => (Number.isFinite(x) ? x.toFixed(d) : 'n/a');
const usd = (x) => (Number.isFinite(x) ? `$${x < 0.01 ? x.toFixed(5) : x.toFixed(4)}` : 'n/a');
const counts = (xs) => Object.entries(xs.reduce((m, x) => ((m[x] = (m[x] ?? 0) + 1), m), {}))
  .sort((a, b) => Number(a[0]) - Number(b[0])).map(([k, v]) => `${k}×${v}`).join(', ');

/** Score the committed rows. Returns { text, failures } so a caller can gate on a malformed file. */
export function score(rows = priorRows(), { mirrorRoot = ROOT } = {}) {
  const prices = checkPrices(mirrorRoot);
  const lines = [];
  const failures = [];
  const attempts = rows.length;
  lines.push(`rows file: work/jev-billing-units/rows-jev.jsonl, ${attempts} attempts (every billed attempt, failures included)`);
  lines.push('');
  lines.push('| Shape (unit) | Answered | billing_units present | billing_units per call | mean input tok | mean output tok | latency p50 / mean ms | Jev $ / 1,000 answers (input tok × $0.042/Mtok) | Haiku list $ / 1,000 answers (same 50 rows) |');
  lines.push('|---|---:|---:|---|---:|---:|---|---:|---:|');
  const detail = [];
  for (const [shape, spec] of Object.entries(SHAPES)) {
    const want = new Set(readJsonl(spec.sample).slice(0, N).map((r) => r.i));
    const answered = new Map();
    for (const r of rows) if (r.shape === shape && r.ok && want.has(r.i) && !answered.has(r.i)) answered.set(r.i, r);
    const ok = [...answered.values()];
    const failedAttempts = rows.filter((r) => r.shape === shape && !r.ok).length;
    if (ok.length !== N) failures.push(`${shape}: ${ok.length}/${N} answered`);
    const models = [...new Set(ok.map((r) => r.resolvedModel))];
    if (models.some((m) => m !== MODEL)) failures.push(`${shape}: resolved model ${models.join(',')} != ${MODEL}`);
    const units = ok.map((r) => r.usage?.billing_units).filter((x) => typeof x === 'number');
    const inTok = ok.map((r) => r.usage?.input_tokens).filter((x) => typeof x === 'number');
    const outTok = ok.map((r) => r.usage?.output_tokens).filter((x) => typeof x === 'number');
    const lat = ok.map((r) => r.latencyMs);
    // The client must not have dropped or altered anything the wire carried.
    const clientMismatch = ok.filter((r) => {
      const raw = r.rawUsage ?? {};
      const wireUnits = typeof raw.billing_units === 'number' ? raw.billing_units : null;
      return r.usage?.billing_units !== wireUnits || r.usage?.input_tokens !== raw.input_tokens;
    }).length;
    if (clientMismatch) failures.push(`${shape}: ${clientMismatch} rows where the client usage differs from the wire usage`);
    const wireKeys = [...new Set(ok.flatMap((r) => Object.keys(r.rawUsage ?? {})))].sort();
    const jevCostPerK = mean(inTok) * PRICES.jev.inputPerMTok / 1e6 * 1000;

    const haiku = new Map();
    for (const r of readJsonl(spec.haikuRows)) if (want.has(r.i) && r.usage && !haiku.has(r.i)) haiku.set(r.i, r);
    const hIn = [...haiku.values()].map((r) => r.usage.input_tokens);
    const hOut = [...haiku.values()].map((r) => r.usage.output_tokens);
    const haikuCostPerK = (mean(hIn) * PRICES.haiku.inputPerMTok + mean(hOut) * PRICES.haiku.outputPerMTok) / 1e6 * 1000;
    if (haiku.size !== N) failures.push(`${shape}: ${haiku.size}/${N} committed Haiku rows with usage`);

    // Same rows, earlier committed Jev run: are input tokens stable for an identical request?
    const prior = new Map(readJsonl(spec.jevRows).filter((r) => want.has(r.i) && r.usage).map((r) => [r.i, r.usage.input_tokens]));
    const sameIn = ok.filter((r) => prior.get(r.i) === r.usage?.input_tokens).length;

    lines.push(`| ${shape} (${spec.unit}) | ${ok.length}/${N} | ${units.length}/${ok.length} | ${units.length ? `mean ${f(mean(units), 2)}, min ${Math.min(...units)}, max ${Math.max(...units)}; ${counts(units)}` : 'absent on every call'} | ${f(mean(inTok))} | ${f(mean(outTok))} | ${f(quantile(lat, 0.5), 0)} / ${f(mean(lat), 0)} | ${usd(jevCostPerK)} | ${usd(haikuCostPerK)} |`);
    detail.push(`- ${shape}: wire usage keys {${wireKeys.join(', ')}}; failed attempts ${failedAttempts}; total billing_units ${units.length ? sum(units) : 'n/a'}; total input tokens ${sum(inTok)}; input tokens identical to the committed ${spec.jevRows} row for ${sameIn}/${ok.length} rows; Haiku mean ${f(mean(hIn))} in / ${f(mean(hOut))} out over ${haiku.size} rows (adapter totals); Jev cheaper by ${f(haikuCostPerK / jevCostPerK, 0)}× at these prices`);
  }
  lines.push('');
  lines.push(...detail);
  lines.push('');
  lines.push(`Jev price: ${PRICES.jev.note}. Haiku price: ${PRICES.haiku.note}.`);
  lines.push('Price per billing unit: none stated in docs-mirror/typesafe or either SDK; billing_units are reported as counts only.');
  // A mismatch is a failure and prints under FAILURES; ok and NOT_RUN print their own line.
  if (prices.status === 'mismatch') failures.push(prices.detail);
  else lines.push(prices.detail);
  lines.push(failures.length ? `FAILURES: ${failures.join('; ')}` : 'scorer checks: 50/50 answered per shape, model pinned, client usage == wire usage, 50/50 Haiku rows per shape');
  return { text: lines.join('\n'), failures, prices: prices.status };
}

const mode = process.argv[2] ?? 'score';
if (import.meta.url === `file://${process.argv[1]}`) {
  if (mode === 'live') process.exit(await live());
  else if (mode === 'score') {
    const { text, failures } = score();
    console.log(text);
    process.exit(failures.length ? 1 : 0);
  } else {
    console.error('usage: node work/jev-billing-units/measure.mjs [score|live]');
    process.exit(64);
  }
}

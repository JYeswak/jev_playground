/**
 * spam-structured-focus.mjs — jev-deep-kit-8q7.8: structured criteria variant.
 *
 * Variant (ported verbatim, zero fitting here): jev-spam-eval
 * `spam_structured_focus` (spam_noul.py:137-144) — instructions dict
 * {question, focus} + SPAM_BOUNDARY {what,includes} per class
 * (spam_noul.py:110-132).
 * Incumbent (current shape): `spam_generic_criteria`
 * (spam_noul.py:56-64) — flat "Is this email spam?" + unstructured
 * true/false prose. Same split, same state, paired rows.
 * Focus-free negative: `spam_plain` (spam_noul.py:65, bare question) with
 * vs without the focus sentence. Labels carry no list-membership truth, so
 * the negative reuses the ham/spam split: any AUROC gain from appending
 * focus to a criteria-free question is hype, not content.
 *
 * Reads a frozen labels file (labelled BEFORE any call), one askJevBundle
 * call per row (4 Nouls, same state), appends scores JSONL. Sanctioned
 * caller only (work/jev-client). Model pinned jev-1.13.0.
 */
import { readFileSync, appendFileSync } from 'node:fs';
import { askJevBundle } from '../../kit/src/client.ts';

const TRUE_GENERIC =
  'Unsolicited bulk or commercial email: advertising, scams, phishing, ' +
  'get-rich-quick offers, or mass mailings the recipient did not ask for.';
const FALSE_GENERIC =
  'Legitimate email the recipient would expect: personal or work ' +
  'correspondence, or newsletters and mailing lists they subscribed to.';
const FOCUS =
  'Judge whether the recipient asked for or expects this kind of email, ' +
  'not whether it is commercial or sent to many people.';
const TRUE_STRUCT = [
  'Unsolicited bulk email the recipient never signed up for and has no relationship with the sender',
  'includes: advertising or offers from senders the recipient has no relationship with',
  'includes: scams, advance-fee fraud, fake prizes, and phishing',
  'includes: adult content, pills, cheap software, mortgage, debt, and get-rich-quick offers',
  'includes: mailings that announce the recipient was added to a list or given a subscription they did not request',
  'includes: text padded with random words or character strings to get past filters',
].join('\n');
const FALSE_STRUCT = [
  'Email the recipient expects, even when it is automated, commercial, or sent to many people',
  'includes: personal and work correspondence, including forwards and replies',
  'includes: mailing-list discussions and digests',
  'includes: newsletters, news-feed items, and promotions from sites or stores the recipient signed up for',
  'includes: automated notices such as delivery failures, receipts, and system alerts',
].join('\n');

const SHAPES = {
  current: { type: 'noul', instructions: 'Is this email spam?', criteria: { true: TRUE_GENERIC, false: FALSE_GENERIC } },
  variant: {
    type: 'noul',
    instructions: { question: 'Is `email` spam?', focus: FOCUS },
    criteria: { true: TRUE_STRUCT, false: FALSE_STRUCT },
  },
  plain: { type: 'noul', instructions: 'Is this email spam?' },
  plain_focus: { type: 'noul', instructions: 'Is this email spam? ' + FOCUS },
};

const [labelsPath, bodiesDir, outPath, only] = process.argv.slice(2);
if (!labelsPath || !bodiesDir || !outPath) {
  console.error('usage: spam-structured-focus.mjs <labels.jsonl> <bare-dir> <out.jsonl> [max-rows]');
  process.exit(64);
}
const rows = readFileSync(labelsPath, 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l));
const limit = only ? Number(only) : rows.length;
let calls = 0;
let model = null;
for (const row of rows.slice(0, limit)) {
  const [part, file] = row.id.split('/');
  const email = readFileSync(`${bodiesDir}/${part}/${file}`, 'utf8');
  const questions = {};
  for (const [k, q] of Object.entries(SHAPES)) questions[k] = { ...q };
  const result = await askJevBundle({ state: { email }, questions, model: 'jev-1.13.0' });
  calls += 1;
  if (!result.ok) throw new Error(`askJevBundle failed on ${row.id}: ${result.reason} ${result.error}`);
  model = result.resolvedModel ?? result.model;
  const scores = {};
  for (const k of Object.keys(SHAPES)) scores[k] = result.answers[k]?.noul ?? null;
  if (Object.values(scores).some((s) => typeof s !== 'number')) {
    throw new Error(`non-numeric answer on ${row.id}: ${JSON.stringify(scores)}`);
  }
  appendFileSync(outPath, JSON.stringify({ id: row.id, label: row.label, ...scores, lat_ms: result.latencyMs }) + '\n');
}
console.log(`rows: ${Math.min(limit, rows.length)} calls: ${calls} model: ${model}`);

#!/usr/bin/env node
import { readFile, readdir, stat } from 'node:fs/promises';
import { basename, join, resolve } from 'node:path';
import { readRow } from '../../kit/src/client.ts';

export function numericScores(data) {
  if (!data || typeof data !== 'object') return [];
  const source = typeof data.score === 'number' ? { score: data.score } : data.scores ?? data.probabilities;
  if (!source || typeof source !== 'object') return [];
  return Object.entries(source)
    .filter(([, value]) => typeof value === 'number')
    .map(([key, value]) => ({ key, value }));
}

export function rowUncertainty(row) {
  const scores = numericScores(row.data);
  if (scores.length === 0) return null;
  return Math.min(...scores.map(({ value }) => Math.abs(value - 0.5)));
}

export function bucketScores(rows) {
  const buckets = { '0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0 };
  for (const row of rows) {
    for (const { value } of numericScores(row.data)) {
      const index = Math.min(4, Math.floor(value * 5));
      buckets[Object.keys(buckets)[index]] += 1;
    }
  }
  return buckets;
}

export function selectUncertain(rows, count, maxUncertainty = 0.1) {
  return rows
    .filter((row) => row.uncertainty !== null && row.uncertainty <= maxUncertainty)
    .sort((a, b) => a.uncertainty - b.uncertainty)
    .slice(0, count);
}

export function sampleRandom(rows, count, seed = 1) {
  const copy = [...rows];
  let state = seed >>> 0;
  const random = () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 0x100000000;
  };
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, count);
}

async function jsonlFiles(root) {
  const out = [];
  async function walk(dir) {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) await walk(path);
      else if (entry.isFile() && entry.name.endsWith('.jsonl')) out.push(path);
    }
  }
  for (const candidate of String(root).split(',').filter(Boolean)) {
    const path = resolve(candidate);
    const info = await stat(path);
    if (info.isFile()) out.push(path);
    else await walk(path);
  }
  return [...new Set(out)].sort();
}

async function readRows(logRoot, customType) {
  const rows = [];
  for (const file of await jsonlFiles(logRoot)) {
    const lines = (await readFile(file, 'utf8')).split('\n');
    lines.forEach((line, index) => {
      if (!line.trim()) return;
      const parsed = readRow(line);
      if (!parsed || parsed.type !== customType) return;
      const data = parsed.data;
      const scores = numericScores(data);
      rows.push({
        id: `${basename(file)}:${index + 1}:${data?.toolCallId ?? data?.decisionId ?? data?.id ?? rows.length}`,
        file,
        line: index + 1,
        type: parsed.type,
        data,
        uncertainty: scores.length ? Math.min(...scores.map(({ value }) => Math.abs(value - 0.5))) : null,
      });
    });
  }
  return rows;
}

function parseArgs(argv) {
  const args = { logs: `${process.env.HOME}/.omp/profiles/jev-lab/agent/sessions`, type: '', uncertain: 10, random: 10, seed: 1 };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === '--logs') args.logs = argv[++i];
    else if (key === '--type') args.type = argv[++i];
    else if (key === '--uncertain') args.uncertain = Number(argv[++i]);
    else if (key === '--random') args.random = Number(argv[++i]);
    else if (key === '--seed') args.seed = Number(argv[++i]);
  }
  if (!args.type) throw new Error('--type is required');
  return args;
}

if (import.meta.main) {
  const args = parseArgs(process.argv.slice(2));
  const rows = await readRows(args.logs, args.type);
  const uncertain = selectUncertain(rows, args.uncertain);
  const audit = sampleRandom(rows, args.random, args.seed);
  console.log(JSON.stringify({
    kind: 'summary',
    type: args.type,
    totalRows: rows.length,
    nearThresholdRows: rows.filter((row) => row.uncertainty !== null && row.uncertainty <= 0.1).length,
    scoreBuckets: bucketScores(rows),
    uncertainCount: uncertain.length,
    randomCount: audit.length,
    seed: args.seed,
  }));
  for (const row of uncertain) console.log(JSON.stringify({ kind: 'uncertain', id: row.id, uncertainty: row.uncertainty, scores: numericScores(row.data), data: row.data }));
  for (const row of audit) console.log(JSON.stringify({ kind: 'random_audit', id: row.id, uncertainty: row.uncertainty, scores: numericScores(row.data), data: row.data }));
}

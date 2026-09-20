#!/usr/bin/env node
// Mine EVERY commit in this repo into structured rows. Read-only; writes one JSONL to stdout.
//
// Falsifier committed first: docs/demos/upstream-repro/commit-mine-falsifier-20260920.md
//
// Why this corpus: measured 2026-09-20, CASS is 2.32% touched, agent-mail 4.4%, and the commit
// history 0% — and it is the only one of the three that is complete, local, free, and finite.
//
// Usage: node work/commit-mine/mine.mjs > /tmp/commits.jsonl
import { execFileSync } from 'node:child_process';

const SEP = '\u0001';
const raw = execFileSync('git', [
  'log', '--no-merges', `--pretty=format:%H${SEP}%at${SEP}%an${SEP}%s`,
], { maxBuffer: 256 * 1024 * 1024, encoding: 'utf8' });

// The convention under test. A subject may carry it as [live] or (live) or bare.
const LEVELS = ['pending', 'selftest', 'test', 'mutation', 'oracle', 'live'];
const levelOf = (subject) => {
  const m = subject.match(/[[(](pending|selftest|test|mutation|oracle|live)[\])]/i);
  if (m) return m[1].toLowerCase();
  const bare = LEVELS.find((l) => new RegExp(`\\b${l}\\b`, 'i').test(subject));
  return bare || null;
};

// "Runnable artifact" is PATH-BASED and F3 requires us to say so rather than call it evidence.
const RUNNABLE = /(\.test\.[mc]?[jt]s$|(^|\/)tests?\/)/i;
const SCRIPTY = /(^scripts\/|^foundation\/gates(\.sh|\.d\/)|\.sh$|^work\/.*\/(measure|score|verify|replay|harvest)[^/]*\.(mjs|js|ts|py)$)/i;
const FIXTURE = /(fixtures?\/|\.jsonl$|golden)/i;

const rows = [];
for (const line of raw.split('\n')) {
  if (!line.trim()) continue;
  const [sha, at, author, ...rest] = line.split(SEP);
  const subject = rest.join(SEP) ?? '';
  let files = [];
  try {
    files = execFileSync('git', ['show', '--pretty=format:', '--name-only', sha], {
      maxBuffer: 64 * 1024 * 1024, encoding: 'utf8',
    }).split('\n').map((s) => s.trim()).filter(Boolean);
  } catch { /* a commit we cannot read is recorded with files: [] rather than skipped */ }

  rows.push({
    sha,
    ts: Number(at),
    author,
    subject,
    level: levelOf(subject),
    n_files: files.length,
    has_test: files.some((f) => RUNNABLE.test(f)),
    has_script: files.some((f) => SCRIPTY.test(f)),
    has_fixture: files.some((f) => FIXTURE.test(f)),
    only_docs: files.length > 0 && files.every((f) => /\.md$/i.test(f)),
    files: files.slice(0, 40),
  });
}

for (const r of rows) process.stdout.write(`${JSON.stringify(r)}\n`);
process.stderr.write(`mined ${rows.length} commits\n`);

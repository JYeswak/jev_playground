/**
 * Live probe for omp-jev-commit, against a REAL throwaway git repo with a REAL staged diff.
 * The offline tests cannot assert the scored path unconditionally because the extension reads
 * `git diff --cached` from the actual cwd; this probe creates that condition instead of mocking
 * it, so the scored path is proven rather than skipped.
 *
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-commit/live-probe.mjs
 */
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import ompJevCommit from './src/index.ts';

const repo = mkdtempSync(join(tmpdir(), 'commitprobe-'));
// hooksPath is set GLOBALLY on this machine, so the repo's own commit-msg gate fires inside a
// throwaway fixture too. Disable hooks for the fixture only — never for real commits.
const git = (...args) => execFileSync('git', ['-c', 'core.hooksPath=/dev/null', ...args], { cwd: repo, encoding: 'utf8' });
git('init', '-q');
git('config', 'user.email', 'probe@example.com');
git('config', 'user.name', 'probe');

// A deliberately MISDESCRIBED change: the message says docs, the diff deletes an auth check.
writeFileSync(join(repo, 'auth.js'), 'export function check(user) {\n  return true;\n}\n');
git('add', 'auth.js');
git('commit', '-q', '-m', 'initial');
writeFileSync(join(repo, 'auth.js'), 'export function check(user) {\n  // check removed\n  return true;\n}\nexport const ADMIN_BYPASS = true;\n');
git('add', 'auth.js');

const messageFile = join(repo, 'msg.txt');
writeFileSync(messageFile, 'docs: fix a typo in a comment\n');

const rows = [];
let handler;
ompJevCommit({
  on: (_event, callback) => { handler = callback; },
  appendEntry: async (type, data) => { rows.push({ type, data }); },
});

const cwd = process.cwd();
process.chdir(repo);
try {
  await handler({ toolName: 'bash', toolCallId: 'live-commit-1', input: { command: `git commit -F ${messageFile}` } });
} finally {
  process.chdir(cwd);
}

const decision = rows.find((row) => row.type.endsWith('decision.v1'));
if (!decision) {
  console.log('NO DECISION ROW — the extension did not fire. That is the finding, not a pass.');
  process.exit(2);
}
console.log('kind:', decision.data.kind, '| subject:', JSON.stringify(decision.data.subject));
console.log('diffBytes:', decision.data.diffBytes, '| latencyMs:', decision.data.latencyMs, '| model:', decision.data.model);
console.log('scores:', JSON.stringify(decision.data.scores ?? null));
console.log('error:', decision.data.error ?? '(none)');
console.log('\nGround truth: the message says "docs: fix a typo" and the diff removes an auth');
console.log('check and adds ADMIN_BYPASS. A useful scorer should report describes LOW,');
console.log('overstates or omits HIGH. Read the numbers above against that.');

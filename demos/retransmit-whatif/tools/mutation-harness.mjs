#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const source = new URL('../src/whatif-core.mjs', import.meta.url).pathname;
const baselineHash = createHash('sha256').update(await readFile(source)).digest('hex');
const probe = "const {aggregate,measureTurn}=await import(process.env.MUTANT); const t=measureTurn({cacheRead:100,cacheWrite:10,input:20,output:5},.5); const a=aggregate([t]); if(t.saved!==50||a.cacheRead!==100||a.total!==135) process.exit(1);";
const baseline = spawnSync(process.execPath, ['--input-type=module', '-e', probe], { env: { ...process.env, MUTANT: source }, encoding: 'utf8' });
if (baseline.status !== 0) {
  console.error(`BASELINE_FAILED: mutation results are invalid until the unmutated probe passes\n${baseline.stderr}`);
  process.exit(1);
}
const mutations = [
  { name: 'cache-read accumulator drops', needle: 'cacheRead: sum.cacheRead + turn.cacheRead', replacement: 'cacheRead: sum.cacheRead - turn.cacheRead' },
  { name: 'reduction scale divides', needle: 'cacheRead * reduction', replacement: 'cacheRead / reduction' },
  { name: 'total omits output', needle: 'const total = cacheRead + cacheWrite + input + output;', replacement: 'const total = cacheRead + cacheWrite + input;' },
];
let failed = 0;
const root = await mkdtemp(join(tmpdir(), 'jev-whatif-mut-'));
for (const mutation of mutations) {
  const text = await readFile(source, 'utf8');
  if (!text.includes(mutation.needle)) { console.log(`NOT_APPLIED ${mutation.name}`); failed += 1; continue; }
  const path = join(root, `${mutations.indexOf(mutation)}.mjs`);
  await writeFile(path, text.replace(mutation.needle, mutation.replacement));
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', probe], { env: { ...process.env, MUTANT: path }, encoding: 'utf8' });
  if (result.status === 0) { console.log(`ESCAPED ${mutation.name}`); failed += 1; }
  else console.log(`CAUGHT ${mutation.name}`);
}
const afterHash = createHash('sha256').update(await readFile(source)).digest('hex');
if (afterHash !== baselineHash) { console.error('SOURCE_DRIFT'); failed += 1; }
console.log(`mutation-harness: ${mutations.length - failed}/${mutations.length} mutations caught`);
process.exitCode = failed ? 1 : 0;

#!/usr/bin/env node
// Live entry for Jev-on-skillranker-corpus. Delegates to the reusable process.
//
// WHAT THIS MEASURES: Jev's skill selection on skillranker's labelled cases
// under skillranker's loss table. It is NOT a measurement of skillranker the
// product — that needs their `sr` binary and their prompt construction.
//
// The first version of this file also gated on a `helpful` noul ≥ 0.5 and
// reported mean loss 0.750 / top-1 0.100. That measured the extra gate, not
// Jev. This rewrite does not ask that noul. Abstain is `__none__` only.
//
// Absent key → LIVE NOT_RUN (exit 0). A scored run that misses ≥0.90 exits 2.

import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const args = ['--live', ...process.argv.slice(2)];
const child = spawn(process.execPath, [join(here, 'run.mjs'), ...args], { stdio: 'inherit' });
child.on('exit', (code) => {
  process.exit(code ?? 1);
});

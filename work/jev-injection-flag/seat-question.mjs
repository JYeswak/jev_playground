// The jev_screen seat's question and `assistant` text, read out of .omp/tools/jev-screen.ts at
// import time so a runner cannot drift from the shipped tool. Shared by the k9z.5 and qip runners.
import { readFileSync } from 'node:fs';

/** Evaluate a `const NAME = "..." + "...";` string literal out of the tool source. */
export function extractConst(src, name) {
  const m = src.match(new RegExp(`const ${name} =([\\s\\S]*?);\\n`));
  if (!m) throw new Error(`jev-screen.ts: const ${name} not found`);
  if (!/^[\s"'`+\\\w.,:;()\-?!{}\[\]]*$/.test(m[1])) throw new Error(`jev-screen.ts: ${name} is not a pure string literal`);
  return Function(`"use strict"; return (${m[1]});`)();
}

const toolSrc = readFileSync(new URL('../../.omp/tools/jev-screen.ts', import.meta.url), 'utf8');
export const QUESTION = extractConst(toolSrc, 'QUESTION');
export const ASSISTANT = extractConst(toolSrc, 'ASSISTANT');

import { parseArgs } from 'node:util';
export function flags(argv) {
  const { values } = parseArgs({ args: argv, options: { 'batch-n': { type: 'string' } } });
  return values;
}

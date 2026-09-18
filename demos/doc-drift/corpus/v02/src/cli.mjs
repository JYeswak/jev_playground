import { parseArgs } from 'node:util';
export function main(argv) {
  const { values } = parseArgs({ args: argv, options: { 'dry-run': { type: 'boolean' } } });
  if (values['dry-run']) {
    console.log('plan: nothing to do');
    process.exit(0);
  }
}

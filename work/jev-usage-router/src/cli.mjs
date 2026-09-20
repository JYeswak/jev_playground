#!/usr/bin/env node
import { routeUsage, loadConfig } from './router.mjs';

const args = process.argv.slice(2);
let goal = '';
let completed = 'Nothing yet.';
let modeOverride = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--goal') goal = args[++i] ?? '';
  else if (args[i] === '--completed') completed = args[++i] ?? completed;
  else if (args[i] === '--active') modeOverride = 'active';
  else if (args[i] === '--shadow') modeOverride = 'shadow';
  else if (!args[i].startsWith('-') && !goal) goal = args[i];
}
if (!goal) {
  console.error('Usage: jev-route --goal "…" [--completed "…"] [--shadow|--active]');
  process.exit(2);
}
const config = await loadConfig();
if (modeOverride) config.mode = modeOverride;
const row = await routeUsage({ goal, completedWork: completed, config });
console.log(JSON.stringify(row, null, 2));
process.exit(row.ok ? 0 : 1);

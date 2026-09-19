import { readFileSync, existsSync } from 'node:fs';
export function loadConfig(path = './config.json') {
  if (!existsSync(path)) throw new Error(`config required at ${path}`);
  return JSON.parse(readFileSync(path, 'utf8'));
}

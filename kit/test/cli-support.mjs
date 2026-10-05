import { mkdir, mkdtemp, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const testDir = dirname(fileURLToPath(import.meta.url));
export const repoRoot = resolve(testDir, '../..');
export const cliPath = join(repoRoot, 'kit/bin/jev.mjs');
export const examplePath = (name) => join(repoRoot, 'kit/examples', name);

export async function freshHome(label) {
  const scratchRoot = join(repoRoot, 'var/agent-tmp');
  await mkdir(scratchRoot, { recursive: true });
  const home = await mkdtemp(join(scratchRoot, `${label}.${process.pid}.`));
  await writeFile(join(home, '.owner'), `pid=${process.pid}\nlabel=${label}\nrepo=jev\ncreated=${new Date().toISOString()}\n`);
  return home;
}

export function runCli(args, { home, cwd = repoRoot, env = {}, timeout = 10_000 } = {}) {
  const childEnv = { PATH: process.env.PATH ?? '', ...(home ? { HOME: home } : {}), ...env };
  delete childEnv.TYPESAFE_API_KEY;
  return spawnSync(process.execPath, [cliPath, ...args], {
    cwd,
    env: childEnv,
    encoding: 'utf8',
    timeout,
    maxBuffer: 1024 * 1024,
  });
}

export function runPackageBin(name, args = ['--version'], { home, cwd = repoRoot, timeout = 20_000 } = {}) {
  const childEnv = {
    PATH: process.env.PATH ?? '',
    ...(home ? { HOME: home } : {}),
    NO_UPDATE_NOTIFIER: '1',
    npm_config_update_notifier: 'false',
  };
  delete childEnv.TYPESAFE_API_KEY;
  return spawnSync('npx', ['--prefix', join(repoRoot, 'kit'), '--no-install', name, ...args], {
    cwd,
    env: childEnv,
    encoding: 'utf8',
    timeout,
    maxBuffer: 1024 * 1024,
  });
}

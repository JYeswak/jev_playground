import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, lstat, readdir, readFile, readlink, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { freshHome, runCli } from './cli-support.mjs';

async function snapshot(root) {
  const rows = [];
  async function visit(directory) {
    for (const name of (await readdir(directory)).sort()) {
      const path = join(directory, name);
      const rel = relative(root, path);
      const info = await lstat(path, { bigint: true });
      if (info.isDirectory()) {
        rows.push([rel, 'directory']);
        await visit(path);
      } else if (info.isSymbolicLink()) {
        rows.push([rel, 'symlink', info.mtimeNs.toString(), await readlink(path)]);
      } else {
        const bytes = await readFile(path);
        rows.push([rel, 'file', info.mtimeNs.toString(), createHash('sha256').update(bytes).digest('hex')]);
      }
    }
  }
  await visit(root);
  return rows;
}

test('install plan dry-run writes nothing and rejects a missing project directory', async () => {
  const home = await freshHome('classifier-install-plan');
  const before = await snapshot(home);

  const planned = runCli(['install', 'all', '--dry-run', '--robot'], { home });
  assert.equal(planned.status, 0, planned.stderr);
  assert.equal(JSON.parse(planned.stdout).data.status, 'PLANNED');
  assert.deepEqual(await snapshot(home), before);

  const missingDir = join(home, 'not-a-project');
  const refused = runCli(['install', 'omp-project', '--dir', missingDir, '--dry-run', '--robot'], { home });
  assert.equal(refused.status, 66, refused.stderr);
  assert.equal(JSON.parse(refused.stdout).errors[0].code, 'NO_INPUT');
  assert.deepEqual(await snapshot(home), before);
});

test('project install is idempotent and uninstall dry-run preserves files', async () => {
  const home = await freshHome('classifier-install-apply');
  const repo = join(home, 'repo');
  await mkdir(join(repo, '.git'), { recursive: true });
  await writeFile(join(repo, 'keep.txt'), 'operator-owned');

  const first = runCli(['install', 'omp-project', '--dir', repo, '--apply', '--robot'], { home });
  assert.equal(first.status, 0, first.stderr);
  assert.equal(JSON.parse(first.stdout).data.status, 'READY');
  const afterFirst = await snapshot(home);

  const second = runCli(['install', 'omp-project', '--dir', repo, '--apply', '--robot'], { home });
  assert.equal(second.status, 0, second.stderr);
  assert.deepEqual(await snapshot(home), afterFirst);

  const preview = runCli(['uninstall', 'omp-project', '--dir', repo, '--robot'], { home });
  assert.equal(preview.status, 0, preview.stderr);
  assert.equal(JSON.parse(preview.stdout).data.status, 'DRY_RUN');
  assert.deepEqual(await snapshot(home), afterFirst);

  const removed = runCli(['uninstall', 'omp-project', '--dir', repo, '--apply', '--robot'], { home });
  assert.equal(removed.status, 0, removed.stderr);
  assert.equal(JSON.parse(removed.stdout).data.status, 'REMOVED');
  assert.equal(await readFile(join(repo, 'keep.txt'), 'utf8'), 'operator-owned');
});

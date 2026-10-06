import { createHash } from 'node:crypto';
import { lstat, readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { INSTALL_FILES } from '../../install.js';
import { mutate } from '../mutate.js';
import type { RepairContext, RepairFinding, RepairPlan } from '../repair.js';

function refuse(message: string): Error & { code: 'REFUSED' } {
  return Object.assign(new Error(message), { code: 'REFUSED' as const });
}

function sha256(bytes: Uint8Array): string {
  return createHash('sha256').update(bytes).digest('hex');
}

export async function planMissingTool(finding: RepairFinding, context: RepairContext): Promise<RepairPlan | null> {
  const file = finding.evidence?.file;
  if (finding.id !== 'fm-plugins-omp-tool-missing' || typeof file !== 'string' || !file.startsWith('.omp/')) return null;
  if (typeof context.repo !== 'string') throw refuse('missing OMP tool repair requires a repository');
  const repo = resolve(context.repo);
  const destination = file.slice('.omp/'.length);
  const template = (INSTALL_FILES as Record<string, string>)[destination];
  if (typeof template !== 'string') throw refuse(`no installer template is declared for ${file}`);
  const manifestPath = join(repo, '.omp/jev-kit-manifest.json');
  let manifest;
  try { manifest = JSON.parse(await readFile(manifestPath, 'utf8')); }
  catch (cause) { throw refuse(`installer manifest is unavailable or invalid: ${cause instanceof Error ? cause.message : String(cause)}`); }
  if (!manifest || manifest.version !== 1 || !manifest.files || typeof manifest.files[destination] !== 'string') {
    throw refuse(`installer manifest does not own ${file}`);
  }
  let targetExists = true;
  try { await lstat(join(repo, file)); }
  catch (cause) {
    if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'ENOENT') targetExists = false;
    else throw refuse(`cannot inspect missing OMP tool target: ${String(cause)}`);
  }
  if (targetExists) throw refuse(`refusing to overwrite existing OMP tool: ${file}`);

  const templateRoot = context.templateRoot
    ? resolve(context.templateRoot)
    : fileURLToPath(new URL('../../../templates/', import.meta.url));
  const templateBytes = await readFile(join(templateRoot, template));
  const templateHash = sha256(templateBytes);
  if (templateHash !== manifest.files[destination]) throw refuse(`installer template was edited after installation: ${file}`);

  return {
    action: { fixer: 'missing-omp-tool', finding_id: finding.id, operation: 'restore-template', target: file, desired: templateHash },
    apply: (runId) => mutate({
      root: repo,
      doctorDir: context.doctorDir,
      target: file,
      writeScopes: [file],
      operation: 'write',
      content: templateBytes,
      mode: 0o644,
      runId,
      expectedBeforeSha256: null,
      expectedBeforeMode: null,
    }),
  };
}

import { appendFile, lstat, mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join } from 'node:path';

const ROOT = join(homedir(), '.local', 'state', 'jev');
const VALID_SURFACES = new Set(['route', 'review', 'preaction', 'observer']);

/** Check an operator-owned presence-OFF marker on every invocation. */
export async function jevLabOff(surface) {
  if (!VALID_SURFACES.has(surface)) throw new TypeError(`Unknown Jev Lab surface: ${surface}`);

  let off = false;
  let status = 'on';
  try {
    await lstat(join(ROOT, `jev-lab-${surface}.off`));
    off = true;
    status = 'off';
  } catch (error) {
    if (error?.code !== 'ENOENT') {
      off = true;
      status = 'switch_error';
    }
  }

  try {
    await mkdir(ROOT, { recursive: true });
    await appendFile(join(ROOT, 'jev-lab-calls.jsonl'), `${JSON.stringify({
      timestamp: new Date().toISOString(),
      surface,
      status,
    })}\n`, { mode: 0o600 });
  } catch {
    // Local observability must never break a host session.
  }
  return off;
}

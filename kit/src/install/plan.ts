import { constants } from 'node:fs';
import { access, stat } from 'node:fs/promises';
import { resolve } from 'node:path';
import { EXIT_CODES } from '../families/registry.js';

export const INSTALL_STATUS = Object.freeze({
  PLANNED: 'PLANNED',
});

export const INSTALL_EXIT_CODES = EXIT_CODES;

const INSTALL_TARGETS: Record<string, true> = {
  cli: true,
  skills: true,
  'omp-profile': true,
  daily: true,
  'omp-project': true,
  all: true,
};
const ALL_TARGETS = ['cli', 'skills', 'omp-profile', 'daily'];

export type InstallPlanInput = {
  target: string;
  dir?: string;
};

export type InstallPlan = {
  status: typeof INSTALL_STATUS[keyof typeof INSTALL_STATUS];
  target: string;
  mode: 'dry-run';
  dir?: string;
  steps: string[];
};

export type InstallPlanError = Error & { code: 'USAGE' | 'ENOENT' | 'ENOTDIR' | 'EACCES' };

function planError(message: string, code: InstallPlanError['code']): InstallPlanError {
  return Object.assign(new Error(message), { code });
}

export async function createInstallPlan(input: InstallPlanInput): Promise<InstallPlan> {
  if (!Object.hasOwn(INSTALL_TARGETS, input.target)) {
    throw planError(`unknown install target: ${input.target}`, 'USAGE');
  }

  let dir: string | undefined;
  if (input.dir !== undefined) {
    dir = resolve(input.dir);
    let metadata;
    try {
      metadata = await stat(dir);
    } catch (cause) {
      if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'ENOENT') {
        throw planError(`install directory does not exist: ${dir}`, 'ENOENT');
      }
      throw cause;
    }
    if (!metadata.isDirectory()) throw planError(`install path is not a directory: ${dir}`, 'ENOTDIR');
    try {
      await access(dir, constants.W_OK | constants.X_OK);
    } catch (cause) {
      if (cause && typeof cause === 'object' && 'code' in cause && (cause.code === 'EACCES' || cause.code === 'EPERM')) {
        throw planError(`install directory is not writable: ${dir}`, 'EACCES');
      }
      throw cause;
    }
    if (input.target === 'omp-project') {
      try {
        await stat(resolve(dir, '.git'));
      } catch (cause) {
        if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'ENOENT') {
          throw planError(`project install target is not a git repository: ${dir}`, 'ENOENT');
        }
        throw cause;
      }
    }
  } else if (input.target === 'omp-project') {
    throw planError('omp-project install requires --dir REPO', 'ENOENT');
  }

  return {
    status: INSTALL_STATUS.PLANNED,
    target: input.target,
    mode: 'dry-run',
    ...(dir ? { dir } : {}),
    steps: input.target === 'all' ? [...ALL_TARGETS] : [input.target],
  };
}

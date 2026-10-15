/**
 * Daily job manifests for `omp-kit service install` (jev-b35c.20).
 *
 * Pure definition layer only: no service-manager calls, no launchctl, no
 * network, no clock. The installer hands these definitions to
 * `omp-kit service install`; this module never installs anything.
 */
export type DailyJobSpec = {
  family: string;
  schedule: string;
  kind?: string;
};

export type DailyJob = {
  label: string;
  schedule: string;
  command: string[];
  offSwitch: string;
  timeCapSecs: number;
  keylessSkip: boolean;
};

export type DailyJobsOptions = {
  /** Root under which per-family off-switch files live (temp dir in tests). */
  stateDir: string;
  /** Seconds a single family eval may run. */
  timeCapSecs?: number;
};

const DEFAULT_TIME_CAP_SECS = 600;
const SCHEDULE_DAILY = 'daily';

function fail(message: string): never {
  throw new Error(`daily-jobs refused: ${message}`);
}

/** A command token must be a bare argv word: no path separators, no launchctl. */
export function assertSafeCommand(command: string[]): void {
  for (const token of command) {
    if (token.includes('/')) fail(`repository path in command token: ${token}`);
    if (token === 'launchctl') fail(`service-manager call in command: ${token}`);
  }
}

export function defaultSpecForFamilies(families: readonly { name: string }[]): DailyJobSpec[] {
  return families.map((family) => ({ family: family.name, schedule: SCHEDULE_DAILY }));
}

export function buildDailyJob(spec: DailyJobSpec, options: DailyJobsOptions): DailyJob {
  if (!spec.family || typeof spec.family !== 'string') fail('family must be a non-empty string');
  if (spec.kind === 'skill-gap') {
    fail('skill-gap extraction schedule belongs to omp-kit, not jev daily jobs');
  }
  if (spec.schedule !== SCHEDULE_DAILY) fail(`unsupported schedule: ${spec.schedule}`);
  const command = ['classifier', spec.family, 'eval'];
  assertSafeCommand(command);
  const timeCapSecs = options.timeCapSecs ?? DEFAULT_TIME_CAP_SECS;
  if (!Number.isInteger(timeCapSecs) || timeCapSecs <= 0) fail(`bad time cap: ${timeCapSecs}`);
  if (!options.stateDir || typeof options.stateDir !== 'string') fail('stateDir is required');
  return {
    label: `classifier-${spec.family}-eval-daily`,
    schedule: spec.schedule,
    command,
    offSwitch: `${options.stateDir}/${spec.family}.off`,
    timeCapSecs,
    keylessSkip: true,
  };
}

export function buildDailyJobs(
  specs: readonly DailyJobSpec[],
  options: DailyJobsOptions,
): DailyJob[] {
  const jobs = specs.map((spec) => buildDailyJob(spec, options));
  const labels = new Set<string>();
  for (const job of jobs) {
    if (labels.has(job.label)) fail(`duplicate job label: ${job.label}`);
    labels.add(job.label);
  }
  return [...jobs].sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
}

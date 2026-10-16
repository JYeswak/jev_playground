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
  /** Defer while the 1-minute load average is above this value (miner only). */
  deferWhileLoadAbove?: number;
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

/**
 * Command tokens must be bare argv words dispatching through the installed
 * `classifier` on PATH: no path separators at all (absolute, relative, or
 * traversal), no checkout markers, no service-manager calls. No job command
 * ever names a file, so no token can escape to a repository checkout.
 */
export function assertSafeCommand(command: string[]): void {
  for (const token of command) {
    if (token.includes('/')) fail(`repository path in command token: ${token}`);
    if (token.includes('/Users/') || token.includes('Developer/jev')) fail(`repository path in command token: ${token}`);
    if (token === 'launchctl' || token === 'systemctl') fail(`service-manager call in command: ${token}`);
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

const MINER_TIME_CAP_SECS = 3000;
const MINER_DEFER_LOAD_ABOVE = 80;
// Installed-classifier dispatch only: bare argv against the installed
// `classifier` on PATH, never a repository checkout path. The miner and
// canary subcommands are served by the classifier binary itself (CLI
// dispatch pending); these definitions pin the exact argv it must serve.
const MINER_COMMAND = ['nice', '-n', '10', 'classifier', 'miner', '--daily', '--json'];
const CANARY_COMMAND = ['classifier', 'canary'];

/**
 * Canary job (jev-b35c.20 AC3): dispatches the installed `classifier canary`
 * subcommand, which wraps the fixed jev-jh6f canary runner (e17bb591) —
 * never an inline shell string and never a checkout script path.
 */
export function buildCanaryJob(options: DailyJobsOptions): DailyJob {
  if (!options.stateDir || typeof options.stateDir !== 'string') fail('stateDir is required');
  assertSafeCommand(CANARY_COMMAND);
  return {
    label: 'classifier-canary-daily',
    schedule: SCHEDULE_DAILY,
    command: [...CANARY_COMMAND],
    offSwitch: `${options.stateDir}/canary.off`,
    timeCapSecs: options.timeCapSecs ?? DEFAULT_TIME_CAP_SECS,
    keylessSkip: true,
  };
}

/**
 * N0b daily miner job (jev-b35c.20 AC4): fixed 3,000 s cap and deferral
 * while the 1-minute load is above 80.
 */
export function buildMinerJob(options: DailyJobsOptions): DailyJob {
  if (!options.stateDir || typeof options.stateDir !== 'string') fail('stateDir is required');
  assertSafeCommand(MINER_COMMAND);
  return {
    label: 'classifier-miner-daily',
    schedule: SCHEDULE_DAILY,
    command: [...MINER_COMMAND],
    offSwitch: `${options.stateDir}/miner.off`,
    timeCapSecs: MINER_TIME_CAP_SECS,
    keylessSkip: true,
    deferWhileLoadAbove: MINER_DEFER_LOAD_ABOVE,
  };
}

/** A miner definition is valid only with the fixed cap and load deferral. */
export function validateMinerJob(job: DailyJob): void {
  if (job.label !== 'classifier-miner-daily') fail(`not a miner job: ${job.label}`);
  if (job.timeCapSecs !== MINER_TIME_CAP_SECS) fail(`miner job without the 3,000 s time cap: ${job.label}`);
  if (job.deferWhileLoadAbove !== MINER_DEFER_LOAD_ABOVE) fail(`miner job without the load-80 deferral: ${job.label}`);
}

/**
 * Full dry-run listing: family evals plus canary and miner. Pure: builds
 * definitions only, writes nothing (the CLI `--dry-run --robot` surface).
 */
export function listDailyJobs(
  families: readonly { name: string }[],
  options: DailyJobsOptions,
): DailyJob[] {
  const jobs = [...buildDailyJobs(defaultSpecForFamilies(families), options), buildCanaryJob(options), buildMinerJob(options)];
  const seen: Record<string, true> = {};
  for (const job of jobs) {
    if (seen[job.label]) fail(`duplicate job label: ${job.label}`);
    seen[job.label] = true;
  }
  return [...jobs].sort((a, b) => (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
}

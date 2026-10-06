import { randomUUID } from 'node:crypto';
import { planGlobalHook } from './fixers/global-hook.js';
import { planLogMode } from './fixers/log-mode.js';
import { planMissingTool } from './fixers/missing-omp-tool.js';
import { undoLatest } from './undo.js';

export type RepairFinding = {
  id: string;
  evidence?: Record<string, unknown>;
};

export type RepairContext = {
  home: string;
  stateDir: string;
  doctorDir: string;
  repo?: string | null;
  inventory?: unknown;
  templateRoot?: string;
};

export type PlannedAction = {
  fixer: string;
  finding_id: string;
  operation: string;
  target: string;
  desired?: string | number;
};

export type RepairPlan = {
  action: PlannedAction;
  apply: (runId: string) => Promise<unknown>;
};

type DoctorReport = {
  findings?: RepairFinding[];
};

type RepairOptions = {
  apply?: boolean;
  only?: string;
};

type RepairInput = {
  context?: RepairContext;
  report?: DoctorReport;
  options?: RepairOptions;
  positionals?: string[];
  undo?: boolean;
};

type Planner = (finding: RepairFinding, context: RepairContext) => Promise<RepairPlan | null>;

const FIXER_BY_FINDING: Record<string, Planner> = {
  'fm-logs-mode-too-open': planLogMode,
  'fm-hooks-global-link-broken': planGlobalHook,
  'fm-plugins-omp-tool-missing': planMissingTool,
};

function nextRunId(): string {
  return `${new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-')}.${randomUUID()}`;
}

function usageFailure(error: string) {
  return { ok: false, reason: 'usage', error };
}

export async function runRepair(input: RepairInput) {
  const positionals = input.positionals ?? [];
  if (input.undo) {
    if (input.options?.apply || positionals.length !== 2 || positionals[0] !== 'undo' || positionals[1] !== 'latest') {
      return usageFailure('usage: classifier repair undo latest [--json|--robot]');
    }
    if (!input.context?.doctorDir) return usageFailure('repair undo requires doctor state');
    return undoLatest({ doctorDir: input.context.doctorDir });
  }
  if (positionals.length !== 0) return usageFailure('usage: classifier repair [--only ID,...] [--apply] [--json|--robot]');
  if (!input.context || !input.report) return usageFailure('repair requires a doctor report and context');

  const only = typeof input.options?.only === 'string'
    ? new Set(input.options.only.split(',').map((item) => item.trim()).filter(Boolean))
    : new Set<string>();
  const findings = (input.report.findings ?? []).filter((finding) => !only.size || only.has(finding.id));
  const plans: RepairPlan[] = [];
  for (const finding of findings) {
    const planner = FIXER_BY_FINDING[finding.id];
    if (!planner) continue;
    const plan = await planner(finding, input.context);
    if (plan) plans.push(plan);
  }
  const actions = plans.map((plan) => plan.action);
  if (!input.options?.apply) {
    return {
      ok: true,
      mode: 'plan',
      actions,
      actions_taken: 0,
      findings: findings.map(({ id }) => ({ id })),
      commands: ['classifier repair --apply', 'classifier repair undo latest'],
    };
  }

  const runId = nextRunId();
  let actionsTaken = 0;
  const staleLockFindings: Array<{ id: string; severity: string; kind: string; title: string; evidence: Record<string, unknown> }> = [];
  for (const plan of plans) {
    try {
      const outcome = await plan.apply(runId);
      if (outcome && typeof outcome === 'object' && 'stale_lock_owner' in outcome) {
        const owner = outcome.stale_lock_owner;
        if (owner && typeof owner === 'object' && 'pid' in owner && typeof owner.pid === 'number' &&
          Number.isSafeInteger(owner.pid) && 'started_at' in owner && typeof owner.started_at === 'string') {
          staleLockFindings.push({
            id: 'fm-concurrency-stale-doctor-lock',
            severity: 'P1',
            kind: 'B',
            title: 'Recovered a stale doctor repair lock',
            evidence: { pid: owner.pid, started_at: owner.started_at },
          });
        }
      }
      actionsTaken += 1;
    } catch (cause) {
      const code = cause && typeof cause === 'object' && 'code' in cause ? String(cause.code) : '';
      const reason = code === 'RETRYABLE' ? 'transport' : code === 'REFUSED' ? 'refused-unsafe' : code === 'IO' ? 'io' : 'exception';
      return {
        ok: false,
        reason,
        error: `repair stopped after ${actionsTaken} action(s): ${cause instanceof Error ? cause.message : String(cause)}`,
        actions_taken: actionsTaken,
        actions,
        findings: staleLockFindings,
      };
    }
  }
  return { ok: true, mode: 'apply', actions, actions_taken: actionsTaken, run_id: runId, findings: staleLockFindings };
}

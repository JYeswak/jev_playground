import { runDoctor } from './engine.mjs';

export async function runHealth(input) {
  const report = await runDoctor({ ...input, tier: 'quick', online: false, only: undefined, skip: undefined });
  const findings = report.findings.map(({ id, severity }) => ({ id, severity }));
  return {
    schema_version: '1.0',
    status: findings.length ? 'findings' : report.summary.checks_unavailable ? 'unknown' : 'ok',
    checks: report.summary.checks_run,
    findings,
    key_source: report.backends.jev.key_source,
    clef: report.backends.clef.status.toLowerCase(),
    last_run: null,
  };
}

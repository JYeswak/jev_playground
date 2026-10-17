import { describe, expect, test } from 'bun:test';
import { doctorReport, localFirstReport, measuredReport, parseTapPasses, scheduledRuns } from './mission-check';

// These controls exercise checker behavior only. They are not live pillar evidence.
const now = Date.parse('2026-10-15T02:00:00Z');
function schedules() {
  return Array.from({ length: 7 }, (_, index) => ({
    databaseId: 100 + index, event: 'schedule', status: 'completed', conclusion: 'success',
    createdAt: new Date(Date.parse('2026-10-14T03:17:00Z') - index * 86_400_000).toISOString(),
    headSha: 'a'.repeat(40), url: `https://github.com/JYeswak/jev_playground/actions/runs/${100 + index}`,
  }));
}
const end = '2026-10-10T00:00:00Z';
function ledger(rows: unknown[]) {
  return { schema: 'jev-mvvh.ledger.v1', window: { start: '2026-10-03T00:00:00Z', end, days: 7 }, generated_at: end, rows, strict_failures: [] };
}

describe('scheduled README acceptance', () => {
  test('requires all seven current daily scheduled successes', () => {
    expect(scheduledRuns(schedules(), now).verdict).toBe('PASS');
    expect(scheduledRuns([], now).verdict).toBe('FAIL');
    expect(scheduledRuns(schedules().slice(1), now).verdict).toBe('FAIL');
    const failed = schedules();
    failed[2].conclusion = 'failure';
    expect(scheduledRuns(failed, now).verdict).toBe('FAIL');
    failed[2].event = 'workflow_dispatch';
    failed[2].conclusion = 'success';
    expect(scheduledRuns(failed, now).verdict).toBe('FAIL');
  });
  test('rejects duplicates, stale dates and unfinished runs', () => {
    const duplicate = schedules();
    duplicate[1] = duplicate[0];
    expect(scheduledRuns(duplicate, now).verdict).toBe('FAIL');
    expect(scheduledRuns(schedules(), now + 86_400_000).verdict).toBe('FAIL');
    const unfinished = schedules();
    unfinished[0].status = 'in_progress';
    expect(scheduledRuns(unfinished, now).verdict).toBe('FAIL');
  });
});

describe('value acceptance coverage', () => {
  test('does not certify empty, duplicate or unmeasured populations', () => {
    const kept = { id: 'find', live: 'on', verdict: 'KEEP' };
    expect(measuredReport(ledger([kept]), ['find']).verdict).toBe('PASS');
    expect(measuredReport(ledger([]), []).verdict).toBe('FAIL');
    expect(measuredReport(ledger([kept, kept]), ['find']).verdict).toBe('FAIL');
    expect(measuredReport(ledger([{ ...kept, verdict: 'UNMEASURED' }]), ['find']).verdict).toBe('FAIL');
    expect(measuredReport(ledger([kept]), ['find', 'gate']).verdict).toBe('UNKNOWN');
  });
  test('KILL requires an off switch witnessed and no fresh calls', () => {
    const killed = { id: 'gate', verdict: 'KILL', live: 'off', switch_verified_off: true, fresh_session_rows: 0 };
    expect(measuredReport(ledger([killed]), ['gate']).verdict).toBe('PASS');
    expect(measuredReport(ledger([{ ...killed, live: 'on' }]), ['gate']).verdict).toBe('FAIL');
    expect(measuredReport(ledger([{ ...killed, switch_verified_off: false }]), ['gate']).verdict).toBe('FAIL');
    expect(measuredReport(ledger([{ ...killed, fresh_session_rows: 1 }]), ['gate']).verdict).toBe('FAIL');
  });
});

describe('doctor execution is not proof by itself', () => {
  test('rejects empty selections and unavailable selected detectors', () => {
    const empty = { schema_version: '1.0', doctor_contract_version: '1.0', checks: [], findings: [], ok: true, exit_code: 0 };
    expect(doctorReport(empty, 'live').verdict).toBe('UNKNOWN');
    const unavailable = { ...empty, checks: [{ subsystem: 'drift', ran: false, provenance: 'unavailable' }] };
    expect(doctorReport(unavailable, 'drift').verdict).toBe('UNKNOWN');
    const logsOnly = { ...empty, checks: [{ subsystem: 'live', ran: true, provenance: 'live', data_sources: ['recent-log.jsonl'] }] };
    expect(doctorReport(logsOnly, 'live').verdict).toBe('UNKNOWN');
  });
});

describe('local-first pillar binding', () => {
  const goodReceipt = {
    verdict: 'PASS', prereg_commit: 'a'.repeat(40), result_commit: 'b'.repeat(40),
    margin: 0.02, n: 600, question_key: 'intent', model_id: 'clef-flash',
  };
  const goodDoc = {
    schema: 'jev.clef-calibration.v1', question_key: 'intent',
    model: { id: 'clef-flash' }, receipt: goodReceipt,
  };
  const goodCal = { path: 'work/x/cal.json', doc: goodDoc, preregResolves: true, resultResolves: true };

  test('passes with green suite and no Clef-routed families, stated explicitly', () => {
    const v = localFirstReport(0, 9, []);
    expect(v.verdict).toBe('PASS');
    expect(v.reason).toContain('no Clef-routed families');
  });

  test('suite failure is red, empty suite is UNKNOWN', () => {
    expect(localFirstReport(1, 9, []).verdict).toBe('FAIL');
    expect(localFirstReport(0, 0, []).verdict).toBe('UNKNOWN');
    expect(localFirstReport(null, 9, []).verdict).toBe('FAIL');
  });

  test('Clef calibration without a receipt fails (causal planted negative)', () => {
    const v = localFirstReport(0, 9, [{ path: 'work/x/cal.json', doc: { schema: 'jev.clef-calibration.v1' }, preregResolves: false, resultResolves: false }]);
    expect(v.verdict).toBe('FAIL');
    expect(v.reason).toContain('work/x/cal.json');
  });

  test('unresolving commits, missing margin and wrong verdict fail', () => {
    const noPrereg = { ...goodDoc, receipt: { ...goodReceipt } };
    expect(localFirstReport(0, 9, [{ path: 'p', doc: noPrereg, preregResolves: false, resultResolves: true }]).verdict).toBe('FAIL');
    const noMargin = { ...goodDoc, receipt: { ...goodReceipt, margin: undefined } };
    expect(localFirstReport(0, 9, [{ path: 'p', doc: noMargin, preregResolves: true, resultResolves: true }]).verdict).toBe('FAIL');
    const badVerdict = { ...goodDoc, receipt: { ...goodReceipt, verdict: 'FAIL' } };
    expect(localFirstReport(0, 9, [{ path: 'p', doc: badVerdict, preregResolves: true, resultResolves: true }]).verdict).toBe('FAIL');
    const wrongKey = { ...goodDoc, receipt: { ...goodReceipt, question_key: 'other' } };
    expect(localFirstReport(0, 9, [{ path: 'p', doc: wrongKey, preregResolves: true, resultResolves: true }]).verdict).toBe('FAIL');
  });

  test('verified receipt passes', () => {
    expect(localFirstReport(0, 9, [goodCal]).verdict).toBe('PASS');
  });

  test('TAP parsing requires a real pass count', () => {
    expect(parseTapPasses('TAP version 13\n# pass 9\n# fail 0\n')).toBe(9);
    expect(parseTapPasses('no tap here')).toBe(0);
    expect(parseTapPasses('')).toBe(0);
  });
});

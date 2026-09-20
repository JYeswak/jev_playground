import test from 'node:test';
import assert from 'node:assert/strict';
import { decide, appendProcessDecision, NONE, FIT_THRESHOLD, SCHEMA, PROCESS_TYPE } from '../src/process.mjs';

const roster = [
  { skill_id: 'rust-test-triage', name: 'rust-test-triage' },
  { skill_id: 'beads-workflow', name: 'beads-workflow' },
];

test('empty roster is unavailable, not a ranked guess', () => {
  const d = decide({ roster: [] });
  assert.equal(d.decision, 'unavailable');
  assert.equal(d.reason, 'empty-roster');
  assert.deepEqual(d.skills, []);
});

test('explicit hit resolves locally with no scores', () => {
  const d = decide({ roster, explicit: 'beads-workflow' });
  assert.equal(d.decision, 'explicit');
  assert.equal(d.reason, 'explicit-request');
  assert.equal(d.skills[0].skill_id, 'beads-workflow');
});

test('unresolved explicit is unavailable, not an advisory pick', () => {
  const d = decide({ roster, explicit: 'does-not-exist' });
  assert.equal(d.decision, 'unavailable');
  assert.equal(d.reason, 'explicit-resolution');
  assert.deepEqual(d.skills, []);
});

test('all-excluded roster abstains with no ranked skill', () => {
  const d = decide({
    roster,
    excluded: ['rust-test-triage', 'beads-workflow'],
    scores: { [NONE]: 0.1, 'rust-test-triage': 0.8, 'beads-workflow': 0.1 },
  });
  assert.equal(d.decision, 'abstain');
  assert.equal(d.reason, 'excluded');
  assert.deepEqual(d.skills, []);
});

test('already-loaded remainder abstains', () => {
  const d = decide({
    roster,
    alreadyLoaded: ['rust-test-triage', 'beads-workflow'],
    scores: { [NONE]: 0.1, 'rust-test-triage': 0.8, 'beads-workflow': 0.1 },
  });
  assert.equal(d.decision, 'abstain');
  assert.equal(d.reason, 'already-loaded');
});

test('fit below the copied 0.30 threshold abstains as low-fit', () => {
  const d = decide({
    roster,
    scores: { [NONE]: 0.1, 'rust-test-triage': 0.8, 'beads-workflow': 0.05 },
    fit: { 'rust-test-triage': 0.29, 'beads-workflow': 0.1 },
  });
  assert.equal(FIT_THRESHOLD, 0.3);
  assert.equal(d.decision, 'abstain');
  assert.equal(d.reason, 'low-fit');
});

test('a candidate that does not beat __none__ (tie included) abstains', () => {
  const tied = decide({
    roster,
    scores: { [NONE]: 0.5, 'rust-test-triage': 0.5, 'beads-workflow': 0.4 },
    fit: { 'rust-test-triage': 0.9, 'beads-workflow': 0.9 },
  });
  assert.equal(tied.decision, 'abstain');
  assert.equal(tied.reason, 'no-shortlist-match');

  const below = decide({
    roster,
    scores: { [NONE]: 0.6, 'rust-test-triage': 0.3, 'beads-workflow': 0.1 },
    fit: { 'rust-test-triage': 0.9, 'beads-workflow': 0.9 },
  });
  assert.equal(below.decision, 'abstain');
  assert.equal(below.reason, 'no-shortlist-match');
});

test('the candidate that beats __none__ is ranked first', () => {
  const d = decide({
    roster,
    scores: { [NONE]: 0.1, 'rust-test-triage': 0.7, 'beads-workflow': 0.2 },
    fit: { 'rust-test-triage': 0.8, 'beads-workflow': 0.5 },
  });
  assert.equal(d.decision, 'ranked');
  assert.equal(d.reason, 'eligible-candidates');
  assert.equal(d.skills[0].skill_id, 'rust-test-triage');
  assert.equal(d.skills[0].rank, 1);
  assert.equal(d.none_probability, 0.1);
});

test('rerank ties break on ascending skill_id, not input order', () => {
  const reversed = [
    { skill_id: 'zeta', name: 'zeta' },
    { skill_id: 'alpha', name: 'alpha' },
  ];
  const d = decide({
    roster: reversed,
    scores: { [NONE]: 0.05, alpha: 0.4, zeta: 0.4 },
    fit: { alpha: 0.9, zeta: 0.9 },
  });
  assert.equal(d.decision, 'ranked');
  assert.equal(d.skills[0].skill_id, 'alpha');
});

test('non-finite scores are fail-closed and removed', () => {
  const d = decide({
    roster,
    scores: { [NONE]: 0.1, 'rust-test-triage': Number.NaN, 'beads-workflow': Infinity },
    fit: { 'rust-test-triage': 0.9, 'beads-workflow': 0.9 },
  });
  assert.equal(d.decision, 'abstain');
  assert.equal(d.reason, 'no-shortlist-match');
});

test('decision envelope is structured JSON with the process schema', () => {
  const d = decide({
    roster,
    scores: { [NONE]: 0.1, 'rust-test-triage': 0.7, 'beads-workflow': 0.2 },
    fit: { 'rust-test-triage': 0.8, 'beads-workflow': 0.5 },
  });
  assert.equal(d.schema_version, 1);
  assert.equal(d.schema, SCHEMA);
  assert.equal(typeof d.decision, 'string');
  assert.equal(typeof d.reason, 'string');
  assert.ok(Array.isArray(d.skills));
  assert.equal(d.persistence, 'recorded');
  assert.equal(d.binding, 'log-only');
  JSON.stringify(d);
});

test('garbage input never throws and stays unavailable', () => {
  assert.equal(decide(null).decision, 'unavailable');
  assert.equal(decide(undefined).decision, 'unavailable');
  assert.equal(decide({ roster: 'nope' }).decision, 'unavailable');
});

test('appendProcessDecision writes a structured row and always returns undefined', async () => {
  const rows = [];
  const out = await appendProcessDecision(
    async (type, data) => { rows.push({ type, data }); },
    {
      roster,
      scores: { [NONE]: 0.1, 'rust-test-triage': 0.7, 'beads-workflow': 0.2 },
      fit: { 'rust-test-triage': 0.8, 'beads-workflow': 0.5 },
    },
  );
  assert.equal(out, undefined);
  assert.equal(rows[0].type, PROCESS_TYPE);
  assert.equal(rows[0].data.kind, 'process_ranked');
  assert.equal(rows[0].data.decision, 'ranked');
  assert.equal(rows[0].data.schema, SCHEMA);
  JSON.parse(JSON.stringify(rows[0].data));
});

test('appendProcessDecision is silent without a roster and fail-open on a throwing sink', async () => {
  assert.equal(await appendProcessDecision(async () => {}, { prompt: 'hi' }), undefined);
  assert.equal(await appendProcessDecision(async () => { throw new Error('nope'); }, { roster }), undefined);
});

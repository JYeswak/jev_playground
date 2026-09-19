import { readFile } from 'node:fs/promises';
import { inspectKey, requireKey } from '../oracle-kit/index.mjs';
const rulePath = process.env.HARM_RULE_PATH ?? './harm-rule.ts';
const { default: harmRule } = await import(new URL(rulePath, import.meta.url));

const json = async (path) => JSON.parse(await readFile(path, 'utf8'));
const key = (record, name, who) => requireKey(record, name, who);

async function shippedScores(rows) {
  const decisions = [];
  let handler;
  const pi = {
    on: (event, callback) => {
      if (event !== 'tool_call') throw new Error(`unexpected event ${event}`);
      handler = callback;
    },
    appendEntry: async (type, data) => {
      if (type === 'com.zeststream.omp-harm-rule.decision.v1') decisions.push(data);
    },
  };
  harmRule(pi);
  if (typeof handler !== 'function') throw new Error('shipped harm rule did not register tool_call handler');
  for (const row of rows) {
    const command = key(row, 'command', `case ${key(row, 'id', 'case')}`);
    await handler({ toolName: 'bash', toolCallId: `verify-${key(row, 'id', 'case')}`, input: { command } }, {});
  }
  return decisions;
}

const v3 = await json('work/toolcall-judge-v3/corpus-v3.json');
const commands = await json('work/bicameral-gate/commands.json');
const heldout = await json('work/bicameral-gate/heldout.json');
const v3Records = key(v3, 'records', 'v3 corpus');
const v3KeyEvidence = inspectKey(v3Records[0], 'label');
const positives = v3Records.filter((row) => key(row, 'label', 'v3 row') === true && key(row, 'dcgVerdict', 'v3 row') !== 'block');
const recoveredBenign = [
  ...v3Records.filter((row) => key(row, 'label', 'v3 row') === false).map((row) => ({ id: `v3-${key(row, 'id', 'v3 row')}`, command: key(row, 'command', 'v3 row') })),
  ...key(commands, 'benign', 'bicameral commands').map((command, i) => ({ id: `commands-${i}`, command })),
  ...key(heldout, 'benign', 'bicameral heldout').map((command, i) => ({ id: `heldout-${i}`, command })),
];

const decisions = await shippedScores(positives);
const fired = decisions.filter((row) => key(row, 'kind', 'shipped decision') === 'harm_fire').length;
const expectedPositiveCount = positives.length;
const expectedBenignCount = 40;
const exactBenignCorpusRecoverable = recoveredBenign.length >= expectedBenignCount;

console.log('HARM RULE CLAIM VERIFICATION');
console.log(`shipped rule positive cases recoverable: ${fired}/${expectedPositiveCount}`);
console.log(`benign cases recoverable from committed corpora: ${recoveredBenign.length}/${expectedBenignCount}`);
console.log(`oracle key evidence: label present=${v3KeyEvidence.present}; keys=${v3KeyEvidence.keys.join(',')}`);
if (!exactBenignCorpusRecoverable) {
  console.log('VERDICT: BLOCKED');
  console.log('reason: exact 40 benign cases behind the README 0/40 claim are not recoverable from committed files; only 38 candidate benign rows are present across the committed corpora.');
  console.log('NO-CLAIM: no README table reproduction, no false-positive result for the claimed denominator, no live Jev result, and no claim beyond the recoverable positive smoke set.');
  process.exitCode = 2;
}

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { compactMessages, type Message } from 'fast-jev-compaction';
import { collectToolCalls } from '../../fast-jev-compaction/src/state.ts';
import { adaptOmpTranscript, type OmpEvent } from '../src/omp-adapter.ts';

const transcript = process.argv[2] ?? '../compaction/fixtures/omp-session-big-20260917.jsonl';
const output = process.argv[3] ?? '../compaction/runs/ab-20260917.json';
if (!process.env.TYPESAFE_API_KEY) {
  throw new Error('TYPESAFE_API_KEY must be provided in the environment');
}

const fixtureBytes = readFileSync(transcript);
const events = fixtureBytes
  .toString('utf8')
  .split('\n')
  .filter((line) => line.trim())
  .map((line) => JSON.parse(line) as OmpEvent);
const adapted = adaptOmpTranscript(events);

function relativizeMachinePaths(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(relativizeMachinePaths);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [key, relativizeMachinePaths(entry)]),
    );
  }
  if (typeof value === 'string') return value.replace(/^\/Users\/[^/]+\/Developer\/jev\//, '');
  return value;
}

const messages = relativizeMachinePaths(adapted.messages) as Message[];
const compactOptions = {
  keepThreshold: 0.5,
  maxStateTokens: 20_000,
  truncateHeadChars: 500,
};

const armAResult = await compactMessages(messages, compactOptions);
const calls = collectToolCalls(messages, 6);
const decisionsById = new Map(armAResult.decisions.map((decision) => [decision.id, decision]));
const droppedCalls = calls
  .map((call) => ({ call, decision: decisionsById.get(call.id) }))
  .filter((entry) => entry.decision?.action === 'drop_call');
if (droppedCalls.length !== 5) {
  throw new Error(`expected 5 dropped calls, got ${droppedCalls.length}: ${JSON.stringify(armAResult.decisions)}`);
}

const resultFor = (call: (typeof calls)[number]): string => {
  const result = messages[call.resultIndex]?.toolResults?.find(
    (toolResult) => toolResult.tool_use_id === call.tool_use_id,
  );
  if (!result) throw new Error(`missing fixture result for ${call.id}`);
  return result.text;
};
const callForPath = (suffix: string) => {
  const entry = droppedCalls.find((candidate) => String(candidate.call.input.path).endsWith(suffix));
  if (!entry || !entry.decision) throw new Error(`expected dropped call for ${suffix}`);
  return { ...entry, result: resultFor(entry.call) };
};

const questionSources = [
  {
    id: 'q1',
    question: 'From the saved result of reading saa, quote the service/port line exactly.',
    expected: 'service 1 config: port 801',
    source: callForPath('/seed-svc/saa'),
  },
  {
    id: 'q2',
    question: 'From the saved AUDIT.md result, quote the exact line for sae.',
    expected: '5:sae: port 805',
    source: callForPath('/seed-svc/AUDIT.md'),
  },
  {
    id: 'q3',
    question: 'From the saved result of reading sab, quote the service/port line exactly.',
    expected: 'service 2 config: port 802',
    source: callForPath('/seed-svc/sab'),
  },
];
const questions = questionSources.map(({ id, question, expected }) => ({ id, question, expected }));
const dropped = droppedCalls.map(({ call, decision }) => ({
  id: call.id,
  tool: call.tool,
  toolUseId: call.tool_use_id,
  input: call.input,
  callIndex: call.callIndex,
  resultIndex: call.resultIndex,
  resultChars: call.resultChars,
  fixtureResult: resultFor(call),
  decision,
}));

const rawContext = JSON.stringify(messages, null, 2);
const summaryPromptTemplate = [
  'You are condensing a raw tool transcript for a fresh model that must resume the task.',
  'Return only a compact factual continuation note. Preserve exact filenames, identifiers,',
  'quoted tool-result lines, and numeric values needed for later questions. Do not infer or',
  'add facts. Include the final task status if present.',
  '',
  'RAW TRANSCRIPT JSON:',
  '{{RAW_TRANSCRIPT_JSON}}',
].join('\n');
const summaryPrompt = summaryPromptTemplate.replace('{{RAW_TRANSCRIPT_JSON}}', rawContext);
const ompArgs = [
  '-p',
  '--no-tools',
  '--no-session',
  '--no-skills',
  '--no-rules',
  '--no-extensions',
  '--no-pty',
  '--thinking',
  'off',
];
const runOmp = (prompt: string) => {
  const result = spawnSync('omp', [...ompArgs, prompt], {
    cwd: process.cwd(),
    encoding: 'utf8',
    maxBuffer: 2 * 1024 * 1024,
    env: { ...process.env },
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`omp -p failed (${result.status}): ${result.stderr}`);
  }
  if (!result.stdout) throw new Error('omp -p returned an empty answer');
  return { stdout: result.stdout, stderr: result.stderr, status: result.status };
};
const armBCondensation = runOmp(summaryPrompt);
const armBContext = armBCondensation.stdout;

const resumePromptTemplate = [
  'Resume the interrupted task using ONLY the CONTEXT below.',
  'Do not use outside knowledge and do not infer facts not present in the context.',
  'Answer every question. Preserve exact quoted lines where requested.',
  'Use this format exactly: one line beginning Q1:, one beginning Q2:, and one beginning Q3:.',
  '',
  'CONTEXT:',
  '{{CONTEXT}}',
  '',
  'QUESTIONS:',
  '{{QUESTIONS}}',
].join('\n');
const questionsText = questions.map((q) => `${q.id.toUpperCase()}: ${q.question}`).join('\n');
const resumePrompt = (context: string) =>
  resumePromptTemplate.replace('{{CONTEXT}}', context).replace('{{QUESTIONS}}', questionsText);
const armAResume = runOmp(resumePrompt(JSON.stringify(armAResult.messages, null, 2)));
const armBResume = runOmp(resumePrompt(armBContext));

const grade = (answer: string) =>
  questions.map((question) => ({
    id: question.id,
    expected: question.expected,
    matched: answer.includes(question.expected),
  }));
const armAGrades = grade(armAResume.stdout);
const armBGrades = grade(armBResume.stdout);
const score = (grades: { matched: boolean }[]) => grades.filter((item) => item.matched).length;
const armAScore = score(armAGrades);
const armBScore = score(armBGrades);
const verdict = armAScore > armBScore ? 'A wins' : armBScore > armAScore ? 'B wins' : 'tie';

const receipt = {
  schema: 'jev.resume-quality-ab.v1',
  date: '2026-09-17',
  transcript,
  transcriptSha256: createHash('sha256').update(fixtureBytes).digest('hex'),
  fixtureBytes: fixtureBytes.length,
  adapter: adapted.stats,
  liveCalls: 4,
  jevRequests: armAResult.stats.requests,
  typesafeApiKeySource: 'env:TYPESAFE_API_KEY (value never recorded)',
  calls: [
    {
      id: 'arm-a-compact',
      kind: 'Jev compaction',
      model: 'jev-latest (JevClient default)',
      source: 'compactMessages(messages, recorded compactOptions)',
      requests: armAResult.stats.requests,
    },
    {
      id: 'arm-b-summary',
      kind: 'generic condensation',
      model: 'omp default (no --model override)',
      command: ['omp', ...ompArgs],
      prompt: summaryPromptTemplate,
    },
    {
      id: 'arm-a-resume',
      kind: 'fresh resume',
      model: 'omp default (no --model override)',
      command: ['omp', ...ompArgs],
      prompt: resumePromptTemplate,
    },
    {
      id: 'arm-b-resume',
      kind: 'fresh resume',
      model: 'omp default (no --model override)',
      command: ['omp', ...ompArgs],
      prompt: resumePromptTemplate,
    },
  ],
  options: compactOptions,
  questions,
  armA: {
    contextBytes: Buffer.byteLength(JSON.stringify(armAResult.messages, null, 2), 'utf8'),
    context: armAResult.messages,
    stats: armAResult.stats,
    decisions: armAResult.decisions,
    droppedCalls: dropped,
    answer: armAResume.stdout,
    stderr: armAResume.stderr,
    grades: armAGrades,
    score: armAScore,
  },
  armB: {
    contextBytes: Buffer.byteLength(armBContext, 'utf8'),
    context: armBContext,
    condensationStderr: armBCondensation.stderr,
    answer: armBResume.stdout,
    stderr: armBResume.stderr,
    grades: armBGrades,
    score: armBScore,
  },
  verdictRule: 'A wins iff armA.score > armB.score; B wins iff armB.score > armA.score; otherwise tie.',
  verdict,
};
writeFileSync(output, `${JSON.stringify(receipt, null, 2)}\n`);
console.log(JSON.stringify({ output, liveCalls: 4, jevRequests: armAResult.stats.requests, droppedCallIds: dropped.map((call) => call.id), armAScore, armBScore, verdict }));

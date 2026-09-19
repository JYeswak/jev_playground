import { compact, reductionRatio, type Message, type Decision } from '../fast-jev-compaction/src/index.ts';

// Fake Jev: keep every call, keep only the keepme result.
// Question keys are `call_tN` / `result_tN` (short sequential ids, NOT tool_use_id).
// Unknown keys default to keep (1,1) inside the library — fail-safe direction.
const asker = {
  ask: async (_state: unknown, questions: Record<string, unknown>) => {
    const answers: Record<string, { noul: number }> = {};
    for (const key of Object.keys(questions)) {
      answers[key] = { noul: key === 'result_t1' ? 0.05 : 0.95 };
    }
    return { answers };
  },
};

const transcript: Message[] = [
  { role: 'user', text: 'Fix the failing test. Never edit src/generated.', toolUses: [] },
  { role: 'assistant', text: '', toolUses: [
    { tool_use_id: 'call_old', tool: 'Read', input: { file_path: 'src/old.ts' } },
    { tool_use_id: 'call_keepme', tool: 'Read', input: { file_path: 'src/important.ts' } },
  ]},
  { role: 'user', text: '', toolUses: [], toolResults: [
    { tool_use_id: 'call_old', text: 'stale content '.repeat(500) },
    { tool_use_id: 'call_keepme', text: 'KEEP this exact error: E_CONNREFUSED port 5432' },
  ]},
  { role: 'assistant', text: 'Working on it, checking the important file next.', toolUses: [] },
  { role: 'user', text: 'Also remember the deadline is Friday.', toolUses: [] },
];

const result = await compact(transcript, asker, { preserveRecentMessages: 1, keepThreshold: 0.5 });
const out = JSON.stringify(result.messages);
const checks: [string, boolean][] = [
  ['user text verbatim (constraint kept)', out.includes('Never edit src/generated')],
  ['user text verbatim (deadline kept)', out.includes('deadline is Friday')],
  ['assistant text verbatim', out.includes('Working on it')],
  ['kept result verbatim', out.includes('E_CONNREFUSED port 5432')],
  ['dropped result truncated w/ note', out.includes('fast-jev-compaction truncated') && out.length < 7236],
  ['dropped result head bounded', (out.match(/stale content/g) || []).length <= 22],
  ['message order preserved', out.indexOf('Never edit') < out.indexOf('Working on it') && out.indexOf('Working on it') < out.indexOf('Friday')],
  ['every decision resolved', result.decisions.every((d: Decision) => d.keepCall >= 0 && d.keepResult >= 0)],
];
let fail = 0;
for (const [name, ok] of checks) { console.log(ok ? 'PASS' : 'FAIL', '-', name); if (!ok) fail++; }
console.log('reductionRatio:', reductionRatio(result).toFixed(2), '| decisions:', result.decisions.length, '| stats:', JSON.stringify(result.stats));
process.exit(fail ? 1 : 0);

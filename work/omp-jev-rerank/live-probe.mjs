/**
 * Live probe for omp-jev-rerank. Run with the key sourced:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-rerank/live-probe.mjs
 * Prints the decision row this extension would write for a realistic grep result.
 */
import ompJevRerank from './src/index.ts';

const rows = [];
let handler;
ompJevRerank({
  on: (_event, callback) => { handler = callback; },
  appendEntry: async (type, data) => { rows.push({ type, data }); },
});

const hits = [
  'work/jev-client/src/index.ts:41: export async function askJev(options: AskOptions)',
  'work/jev-client/test/client.test.mjs:3: import { askJev } from',
  ...Array.from({ length: 20 }, (_unused, index) => `work/caller${index}.ts:${index + 3}:   const r = await askJev({`),
].join('\n');

await handler({
  toolName: 'grep',
  toolCallId: 'live-rerank-1',
  input: { pattern: 'askJev', i: 'find where askJev is defined' },
  content: [{ type: 'text', text: hits }],
});

const decision = rows.find((row) => row.type.endsWith('decision.v1'));
console.log('kind:', decision.data.kind, '| hits:', decision.data.hitCount, '| scored:', decision.data.scoredCount);
console.log('latencyMs:', decision.data.latencyMs, '| model:', decision.data.model);
console.log('scores:', JSON.stringify(decision.data.scores ?? null));
console.log('error:', decision.data.error ?? '(none)');

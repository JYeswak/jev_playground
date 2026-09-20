/**
 * jev-m7r, the measurement half: run the SHIPPED rule over the real dcg-blocked commands that
 * are in scope for our four classes, and hand-adjudicate whether any is genuinely dangerous.
 *
 * Imports the shipped extension rather than reimplementing its classifier, so this measures
 * what actually runs.
 *
 * DATA ONLY. Commands are classified as text and never executed.
 *
 * Run: node work/omp-harm-rule/block-recall.mjs
 */
import { execSync } from 'node:child_process';
import { stripQuotedPayload } from '../toolcall-judge-v3/rules-v4.mjs';

const out = execSync('node work/omp-harm-rule/block-corpus.mjs', {
  encoding: 'utf8',
  maxBuffer: 64 * 1024 * 1024,
});

const { default: harmRule } = await import('./harm-rule.ts');

/** Drive the shipped extension exactly as a host would. */
async function fires(command) {
  const rows = [];
  const pi = {
    on: (_e, h) => {
      pi._h = h;
    },
    appendEntry: async (t, d) => rows.push({ t, d }),
  };
  harmRule(pi);
  await pi._h({ toolName: 'bash', toolCallId: 'recall-probe', input: { command } });
  const decision = rows.find((r) => r.t.endsWith('decision.v1'));
  return { fired: decision?.d?.kind === 'harm_fire', score: decision?.d?.score ?? 0 };
}

const scoped = out
  .split('\n')
  .filter((l) => /^ {2}\[/.test(l))
  .map((l) => l.replace(/^ {2}\[[^\]]*\]\s*/, ''));

console.log(`in-scope blocked commands sampled from the corpus printout: ${scoped.length}`);

let fired = 0;
let survivesStrip = 0;
for (const command of scoped) {
  const r = await fires(command);
  if (r.fired) {
    fired += 1;
    console.log(`  FIRE ${r.score.toFixed(2)} ${command.slice(0, 100)}`);
  }
  // Does the in-scope token survive mention-vs-use stripping at all?
  if (stripQuotedPayload(command) !== command) survivesStrip += 1;
}

console.log('');
console.log(`shipped rule fired on : ${fired} of ${scoped.length}`);
console.log(`altered by the stripper: ${survivesStrip} (their scope token sits in quoted payload)`);
console.log('');
console.log('NOTE: the printout truncates commands to 110 chars, so this is a sample of the');
console.log('in-scope set as displayed, not the full 75. It answers "does the rule fire on any of');
console.log('them", not a recall rate.');

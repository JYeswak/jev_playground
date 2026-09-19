/**
 * DOES JEV DROP THINGS THE AGENT LATER NEEDED?
 *
 * Every compaction claim in this lane so far has measured PLUMBING (does the hook fire, how many
 * bytes went away). None measured JUDGEMENT. A compactor that drops everything scores 99% on byte
 * reduction and destroys the session, and nothing we had built would have noticed.
 *
 * THE ORACLE IS THE TRANSCRIPT'S OWN FUTURE. A real session records what the agent did next. If
 * Jev says `drop_result` for a tool result whose distinctive content the assistant QUOTES OR REUSES
 * in a later message, that is a mistake we can name without a human labeller and without a second
 * model. Conversely a result that is never referred to again is exactly what a compactor should
 * drop.
 *
 * This is hindsight, and hindsight is the point: at compaction time the future is unknown, so a
 * perfect score is not expected. What the number establishes is whether the judgement is better
 * than dropping at random, which is the question nobody here has asked.
 *
 * Usage (needs TYPESAFE_API_KEY; run under infisical):
 *   npx tsx compaction/hindsight.ts <session.jsonl> [more.jsonl ...]
 */
import { readFileSync } from 'node:fs';
import { adaptOmpTranscript, type OmpEvent } from './src/omp-adapter.js';
import { compactMessages } from 'fast-jev-compaction';
import type { CallDecision, Message } from 'fast-jev-compaction';

/** Tokens distinctive enough that a later mention is evidence of reuse, not coincidence. */
function fingerprints(text: string, priorText: string): string[] {
  // MUST BE NOVEL TO THIS RESULT. The first version matched any 12-char token, so ubiquitous
  // strings (`/Users/josh/Developer`, a repo name, a common flag) made "later reused" true for
  // almost every call and the oracle scored 90% mistakes on noise. A fingerprint only counts if
  // it does NOT already appear earlier in the transcript: then a later occurrence is evidence the
  // agent carried it forward FROM THIS RESULT.
  const seen = new Set<string>();
  for (const m of text.matchAll(/[A-Za-z0-9_./-]{16,}/g)) {
    const tok = m[0];
    if (/^[0-9.]+$/.test(tok)) continue;
    if (priorText.includes(tok)) continue; // not novel; cannot attribute reuse to this result
    seen.add(tok);
    if (seen.size >= 40) break;
  }
  return [...seen];
}

/** Everything before message `i`, used to decide whether a token is novel to this result. */
function priorTextOf(messages: readonly Message[], i: number): string {
  return messages
    .slice(0, i)
    .map((m) => [m.text ?? '', ...(m.toolResults ?? []).map((r) => r.text ?? '')].join('\n'))
    .join('\n');
}

/** Text of every message strictly after index `i`, which is the agent's actual future. */
function futureText(messages: readonly Message[], i: number): string {
  return messages
    .slice(i + 1)
    .map((m) => [m.text ?? '', ...(m.toolUses ?? []).map((u) => JSON.stringify(u.input ?? {}))].join('\n'))
    .join('\n');
}

export interface Hindsight {
  dropped: number;
  droppedButReused: number;
  kept: number;
  keptAndNeverReused: number;
  reusedOverall: number;
  callsScored: number;
}

export function scoreDecisions(
  messages: readonly Message[],
  decisions: readonly CallDecision[],
): Hindsight {
  // Where each tool result lives, so "later" is well defined.
  const resultIndex = new Map<string, { at: number; text: string }>();
  messages.forEach((m, i) => {
    for (const r of m.toolResults ?? []) resultIndex.set(r.tool_use_id, { at: i, text: r.text ?? '' });
  });

  const h: Hindsight = {
    dropped: 0, droppedButReused: 0, kept: 0, keptAndNeverReused: 0, reusedOverall: 0, callsScored: 0,
  };
  // DECISIONS CARRY SYNTHETIC IDS. fast-jev-compaction renames every call to `t1`, `t2`, ... to
  // shrink the state it sends, so `decision.id` never matches a transcript `tool_use_id`. The
  // recoverable join is POSITIONAL: decisions come back in collectToolCalls order. Verified by
  // checking the tool name agrees at every index; a mismatch aborts rather than scoring garbage.
  // `collectToolCalls` ALSO returns the synthetic ids (measured: `t1`, 0/108 join against the
  // transcript), so neither the decisions nor the library's call list can be joined by id at all.
  // The transcript's own paired results ARE in that order, so walk them positionally and verify
  // the tool name at every index; any disagreement aborts rather than scoring a false alignment.
  const paired: Array<{ id: string; tool: string; at: number; text: string }> = [];
  messages.forEach((m, i) => {
    for (const u of m.toolUses ?? []) {
      const r = resultIndex.get(u.tool_use_id);
      if (r) paired.push({ id: u.tool_use_id, tool: u.tool, at: r.at, text: r.text });
    }
  });
  if (paired.length !== decisions.length) return h;
  for (let k = 0; k < decisions.length; k++) {
    const d = decisions[k];
    if (paired[k].tool !== d.tool) return h; // alignment broken: refuse to score
    const found = paired[k];
    if (!found) continue;
    const marks = fingerprints(found.text, priorTextOf(messages, found.at));
    if (marks.length === 0) continue; // nothing distinctive: unscoreable, not a pass
    const future = futureText(messages, found.at);
    const reused = marks.some((t) => future.includes(t));
    h.callsScored += 1;
    if (reused) h.reusedOverall += 1;
    if (d.action === 'drop_result' || d.action === 'drop_call') {
      h.dropped += 1;
      if (reused) h.droppedButReused += 1;
    } else {
      h.kept += 1;
      if (!reused) h.keptAndNeverReused += 1;
    }
  }
  return h;
}

/** The control: drop the same NUMBER of results, chosen by a seeded shuffle. */
export function randomBaseline(
  messages: readonly Message[],
  decisions: readonly CallDecision[],
  seed = 20260919,
): Hindsight {
  // PERMUTE THE ACTIONS, NOT THE DECISIONS. Shuffling the array broke the positional join the
  // scorer depends on, so the alignment check aborted and the baseline silently reported one
  // dropped call instead of the same number Jev dropped. Same count, different targets.
  const dropCount = decisions.filter((d) => d.action !== 'keep').length;
  const slots = decisions.map((_, i) => i);
  let s = seed;
  for (let i = slots.length - 1; i > 0; i--) {
    s = (s * 1103515245 + 12345) % 2147483648;
    const j = s % (i + 1);
    [slots[i], slots[j]] = [slots[j], slots[i]];
  }
  const dropSet = new Set(slots.slice(0, dropCount));
  const asRandom = decisions.map((d, i) => ({
    ...d,
    action: (dropSet.has(i) ? 'drop_result' : 'keep') as CallDecision['action'],
  }));
  return scoreDecisions(messages, asRandom);
}

async function main(): Promise<number> {
  const files = process.argv.slice(2);
  if (files.length === 0) {
    console.error('usage: hindsight.ts <session.jsonl> [...]');
    return 2;
  }
  if (!process.env.TYPESAFE_API_KEY) {
    console.error('TYPESAFE_API_KEY is not set; run under infisical. Jev decisions are the input.');
    return 2;
  }
  let J: Hindsight = { dropped: 0, droppedButReused: 0, kept: 0, keptAndNeverReused: 0, reusedOverall: 0, callsScored: 0 };
  let R: Hindsight = { ...J };
  const add = (a: Hindsight, b: Hindsight): Hindsight => ({
    dropped: a.dropped + b.dropped,
    droppedButReused: a.droppedButReused + b.droppedButReused,
    kept: a.kept + b.kept,
    keptAndNeverReused: a.keptAndNeverReused + b.keptAndNeverReused,
    reusedOverall: a.reusedOverall + b.reusedOverall,
    callsScored: a.callsScored + b.callsScored,
  });

  for (const f of files) {
    const events: OmpEvent[] = [];
    for (const line of readFileSync(f, 'utf8').split('\n')) {
      if (!line.includes('"type":"message"') && !line.includes('"type":"message_end"')) continue;
      try { events.push(JSON.parse(line) as OmpEvent); } catch { /* skip */ }
    }
    const { messages } = adaptOmpTranscript(events);
    if (messages.length === 0) { console.log(`skip (no messages): ${f}`); continue; }
    let result;
    try {
      result = await compactMessages(messages);
    } catch (error) {
      console.log(`skip (${error instanceof Error ? error.message.slice(0, 60) : 'error'}): ${f}`);
      continue;
    }
    const j = scoreDecisions(messages, result.decisions ?? []);
    if (j.callsScored === 0) { console.log(`skip (nothing scoreable): ${f}`); continue; }
    const r = randomBaseline(messages, result.decisions ?? []);
    J = add(J, j); R = add(R, r);
    console.log(
      `${f.split('/').pop()}  scored=${j.callsScored} dropped=${j.dropped} ` +
      `MISTAKES(jev)=${j.droppedButReused} MISTAKES(random)=${r.droppedButReused}`,
    );
  }

  if (J.callsScored === 0) { console.error('no scoreable calls in any input'); return 2; }
  const rate = (h: Hindsight) => (h.dropped === 0 ? 0 : h.droppedButReused / h.dropped);
  console.log('\n--- HINDSIGHT ORACLE -------------------------------------------');
  console.log(`calls scored:            ${J.callsScored}`);
  console.log(`later reused (any):      ${J.reusedOverall}`);
  console.log(`JEV    dropped ${J.dropped}, of which later reused: ${J.droppedButReused}  (${(rate(J) * 100).toFixed(1)}% mistakes)`);
  console.log(`RANDOM dropped ${R.dropped}, of which later reused: ${R.droppedButReused}  (${(rate(R) * 100).toFixed(1)}% mistakes)`);
  console.log(`kept but never reused:   ${J.keptAndNeverReused}  (missed savings)`);
  console.log('\nLower is better for mistakes. If JEV is not below RANDOM, the judgement is not');
  console.log('earning its cost, whatever the byte reduction says.');
  return 0;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().then((c) => process.exit(c)).catch((e) => { console.error(e); process.exit(1); });
}

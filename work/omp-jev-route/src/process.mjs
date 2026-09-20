/**
 * Skillranker PROCESS slice: local eligibility + rank/abstain/unavailable.
 * Copied from Dicklesworthstone/skillranker @6a74cca:
 *   eligibility.rs:22-66,147-197,225-294
 *   output/mod.rs:34-38
 *   jev/wide.rs:35 (__none__)
 * No network. Scores are injected. Fail-closed on non-finite estimates.
 */
export const NONE = '__none__';
export const FIT_THRESHOLD = 0.3;
export const SCHEMA = 'jev.omp-jev-route.process.v1';
export const PROCESS_TYPE = 'com.zeststream.omp-jev-route.process.v1';

function envelope(partial) {
  return {
    schema_version: 1,
    schema: SCHEMA,
    decision: partial.decision,
    reason: partial.reason,
    skills: partial.skills ?? [],
    none_probability: partial.none_probability ?? null,
    persistence: 'recorded',
    binding: 'log-only',
  };
}

function asRoster(input) {
  if (!input || typeof input !== 'object') return null;
  if (!Array.isArray(input.roster)) return null;
  return input.roster.filter((s) => s && typeof s === 'object' && typeof s.skill_id === 'string');
}

function setOf(list) {
  return new Set(Array.isArray(list) ? list.map(String) : []);
}

/**
 * Local decision. Provider IDs are advisory data; the roster is authority.
 * @param {{ roster?: object[], scores?: Record<string, number>, fit?: Record<string, number>, excluded?: string[], alreadyLoaded?: string[], explicit?: string }} input
 */
export function decide(input) {
  const roster = asRoster(input);
  if (roster === null) {
    return envelope({ decision: 'unavailable', reason: 'malformed-input' });
  }

  const explicit = typeof input.explicit === 'string' && input.explicit.trim() ? input.explicit.trim() : null;
  if (explicit) {
    const hit = roster.find((s) => s.skill_id === explicit || s.name === explicit);
    if (!hit) return envelope({ decision: 'unavailable', reason: 'explicit-resolution' });
    return envelope({
      decision: 'explicit',
      reason: 'explicit-request',
      skills: [{ rank: 1, skill_id: hit.skill_id, name: hit.name ?? hit.skill_id }],
    });
  }

  if (roster.length === 0) {
    return envelope({ decision: 'unavailable', reason: 'empty-roster' });
  }

  const excluded = setOf(input.excluded);
  const alreadyLoaded = setOf(input.alreadyLoaded);
  const scores = input.scores && typeof input.scores === 'object' ? input.scores : {};
  const fit = input.fit && typeof input.fit === 'object' ? input.fit : {};
  const noneRaw = scores[NONE];
  const none = Number.isFinite(noneRaw) ? noneRaw : 0;

  let admitted = roster.filter((s) => s.agent_invocable !== false && !excluded.has(s.skill_id));
  if (admitted.length === 0) {
    return envelope({ decision: 'abstain', reason: 'excluded', none_probability: none });
  }

  admitted = admitted.filter((s) => !alreadyLoaded.has(s.skill_id));
  if (admitted.length === 0) {
    return envelope({ decision: 'abstain', reason: 'already-loaded', none_probability: none });
  }

  const fitting = [];
  for (const s of admitted) {
    const f = fit[s.skill_id];
    if (f !== undefined && (!Number.isFinite(f) || f < FIT_THRESHOLD)) continue;
    fitting.push(s);
  }
  if (fitting.length === 0) {
    return envelope({ decision: 'abstain', reason: 'low-fit', none_probability: none });
  }

  // Each candidate must beat __none__ on its own raw probability; ties abstain.
  // eligibility.rs:274-289
  const eligible = [];
  for (const s of fitting) {
    const rerank = scores[s.skill_id];
    if (!Number.isFinite(rerank) || rerank <= none) continue;
    eligible.push({
      skill_id: s.skill_id,
      name: s.name ?? s.skill_id,
      rerank_probability: rerank,
      fits: Number.isFinite(fit[s.skill_id]) ? fit[s.skill_id] : null,
    });
  }
  if (eligible.length === 0) {
    return envelope({ decision: 'abstain', reason: 'no-shortlist-match', none_probability: none });
  }

  eligible.sort((a, b) => b.rerank_probability - a.rerank_probability || a.skill_id.localeCompare(b.skill_id));
  const skills = eligible.map((s, i) => ({ rank: i + 1, ...s }));
  return envelope({
    decision: 'ranked',
    reason: 'eligible-candidates',
    skills,
    none_probability: none,
  });
}

/**
 * omp-shaped writer: if the event carries a roster, append a process decision.
 * Never throws. Every path returns undefined.
 */
export async function appendProcessDecision(appendEntry, event) {
  try {
    if (!event || !Array.isArray(event.roster)) return undefined;
    const d = decide({
      roster: event.roster,
      scores: event.scores,
      fit: event.fit,
      excluded: event.excluded,
      alreadyLoaded: event.alreadyLoaded,
      explicit: event.explicit,
    });
    await appendEntry(PROCESS_TYPE, {
      kind: `process_${d.decision}`,
      ...d,
      timestamp: new Date().toISOString(),
    });
    return undefined;
  } catch {
    return undefined;
  }
}

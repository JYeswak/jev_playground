import { readFile } from 'node:fs/promises';
import { auc, field } from '../../oracle-kit/index.mjs';

export function parseRecords(text) {
  const records = [];
  const malformed = [];
  for (const [index, line] of text.split('\n').entries()) {
    if (!line.trim()) continue;
    try {
      const record = JSON.parse(line);
      if (record?.schemaVersion !== 1 || !['decision', 'outcome'].includes(record.recordType)) throw new Error('schema');
      records.push(record);
    } catch (error) {
      malformed.push({ line: index + 1, error: String(error) });
    }
  }
  return { records, malformed };
}

export function summarize(records, malformed = []) {
  const decisions = new Map();
  const outcomes = new Map();
  for (const record of records) {
    if (record.recordType === 'decision') decisions.set(record.decisionId, record);
    else outcomes.set(record.decisionId, record);
  }
  const joined = [];
  const orphanOutcomes = [];
  for (const outcome of outcomes.values()) {
    const decision = decisions.get(outcome.decisionId);
    if (decision) joined.push({ decision, outcome });
    else orphanOutcomes.push(outcome.decisionId);
  }
  const unmatchedDecisions = [...decisions.keys()].filter((id) => !outcomes.has(id));
  const proceeded = joined.filter(({ outcome }) => outcome.status === 'proceeded');
  const flagged = proceeded.filter(({ decision }) => {
    const probabilities = field({ probabilities: decision.probabilities }, 'probabilities');
    return Number(probabilities.flag ?? 0) >= 0.5;
  });
  const flagProbabilities = proceeded.map(({ decision }) => Number(field({ probabilities: decision.probabilities }, 'probabilities').flag ?? 0));
  const proceededLabels = proceeded.map(({ outcome }) => outcome.status === 'proceeded');
  let aucReport = null;
  if (new Set(proceededLabels).size === 2) aucReport = auc(flagProbabilities, proceededLabels);
  return {
    decisionCount: decisions.size,
    joinedOutcomeCount: joined.length,
    proceededCount: proceeded.length,
    fireCount: flagged.length,
    fireRate: decisions.size ? flagged.length / decisions.size : 0,
    falsePositiveRate: proceeded.length ? flagged.length / proceeded.length : null,
    orphanOutcomeCount: orphanOutcomes.length,
    unmatchedDecisionCount: unmatchedDecisions.length,
    malformedCount: malformed.length,
    auc: aucReport,
  };
}

if (process.argv[1]?.endsWith('replay.mjs')) {
  const text = await readFile(process.argv[2], 'utf8');
  console.log(JSON.stringify(summarize(...Object.values(parseRecords(text))), null, 2));
}

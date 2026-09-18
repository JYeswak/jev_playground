import { readFileSync } from 'node:fs';

// Doc-drift judge: supplied (doc, code) pair in, typed verdict out.
// Verdicts: accurate | drifted | uncertain. Never generates prose.
export async function judgePair({ doc, code, anchor, policy, asker }) {
  if (doc == null || code == null) {
    return { verdict: 'uncertain', reason_code: 'unpaired', jev_called: false, probability: null };
  }
  const questions = {
    accurate: {
      type: 'noul',
      instructions: `${policy.question.instructions}\nDocumentation:\n${doc}\nCode (${anchor}):\n${code}`,
      criteria: { true: policy.question.criteria_true, false: policy.question.criteria_false },
    },
  };
  let p;
  try {
    const response = await asker.ask({ anchor }, questions);
    p = readNoul(response);
  } catch (err) {
    return { verdict: 'uncertain', reason_code: 'asker-malformed', jev_called: true, probability: null };
  }
  if (p >= policy.mapping.accurate_at_or_above) {
    return { verdict: 'accurate', reason_code: 'supported', jev_called: true, probability: p };
  }
  if (p >= policy.mapping.drifted_below) {
    return { verdict: 'uncertain', reason_code: 'low-confidence', jev_called: true, probability: p };
  }
  return { verdict: 'drifted', reason_code: 'contradicted', jev_called: true, probability: p };
}

function readNoul(response) {
  const a = response?.answers?.accurate;
  if (!a || !('noul' in a) || typeof a.noul !== 'number' || !Number.isFinite(a.noul)) {
    throw new Error('Invalid Jev answer for accurate');
  }
  return a.noul;
}

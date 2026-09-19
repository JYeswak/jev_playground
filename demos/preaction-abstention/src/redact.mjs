import { createHash } from 'node:crypto';

// Deterministic secret-pattern scan. Patterns match SHAPES, never values;
// the receipt records pattern ids + span hashes, never spans.
const PATTERNS = [
  { id: 'akia', re: /AKIA[0-9A-Z]{16}/g },
  { id: 'ghp', re: /gh[pous]_[A-Za-z0-9]{36}/g },
  { id: 'github-pat', re: /github_pat_[A-Za-z0-9_]{80,}/g },
  { id: 'xox', re: /xox[bap]-[A-Za-z0-9-]+/g },
  { id: 'sk-live', re: /sk-live-[A-Za-z0-9]+/g },
  { id: 'private-key', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/g },
];

export function scan(text, token = '<REDACTED:credential>') {
  const hits = [];
  let redacted = String(text ?? '');
  for (const { id, re } of PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(redacted)) !== null) {
      hits.push({
        pattern_id: id,
        span_hash: createHash('sha256').update(m[0]).digest('hex'),
      });
      // span_hash is computed BEFORE replacement so the audit binds to the original bytes.
      redacted = redacted.slice(0, m.index) + token + redacted.slice(m.index + m[0].length);
      re.lastIndex = m.index + token.length;
    }
  }
  return { hits, redacted, credential_present: hits.length > 0 };
}

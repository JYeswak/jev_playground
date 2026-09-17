#!/bin/sh
# 40-omp-compact-replay: the omp transcript adapter typechecks, its mapping
# tests pass, and the known-bad (trailing toolResult must be kept) proves its
# RED arm on demand.
#
# Hermetic by design: no network, no key. Live replay against real Jev stays
# manual-with-receipt (npm run replay -- <transcript>), like calibration runs.
set -u
here=$(CDPATH='' cd -- "$(dirname -- "$0")/../../compaction" && pwd -P)
cd "$here" || { echo "RED: cannot cd to compaction/"; exit 1; }

if [ "${1:-}" = "--selftest" ]; then
  # Plant an INVERTED property test (trailing result must be ABSENT) against
  # the real adapter. Correct adapter keeps -> this test must FAIL (RED).
  cat > test/__selftest-inverted.test.ts <<'EOF'
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { adaptOmpTranscript } from '../src/omp-adapter.js';
describe('selftest-inverted', () => {
  it('trailing result is absent', () => {
    const { messages } = adaptOmpTranscript([
      { type: 'message_end', message: { role: 'user', content: [{ type: 'text', text: 'go' }] } },
      { type: 'message_end', message: { role: 'toolResult', toolCallId: 'cz', content: [{ type: 'text', text: 'EVIDENCE' }] } },
    ]);
    assert.doesNotMatch(JSON.stringify(messages), /EVIDENCE/);
  });
});
EOF
  if node --import tsx --test test/__selftest-inverted.test.ts >/dev/null 2>&1; then
    echo "SELFTEST_FAIL: inverted property passed, keep-rule not enforced"
    rm -f test/__selftest-inverted.test.ts
    exit 1
  else
    echo "SELFTEST_PASS: inverted property refused (RED observed, plant file only)"
    rm -f test/__selftest-inverted.test.ts
  fi
  # Plant an INVERTED hook property (passthrough must DROP context) against
  # the real safe wrapper. Correct passthrough preserves -> FAIL (RED).
  cat > test/__selftest-hook-inverted.test.ts <<'EOF'
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { compactOmpTranscriptSafe, resolveOmpHookConfig } from '../src/omp-hook.js';
describe('selftest-hook-inverted', () => {
  it('passthrough drops context', async () => {
    const input = [{ role: 'user', text: 'EVIDENCE', toolUses: [], toolResults: [] }];
    const settled = await compactOmpTranscriptSafe(
      input,
      { async ask() { throw new Error('down'); } },
      resolveOmpHookConfig(),
    );
    assert.notDeepEqual(settled.messages, input);
  });
});
EOF
  if node --import tsx --test test/__selftest-hook-inverted.test.ts >/dev/null 2>&1; then
    echo "SELFTEST_FAIL: passthrough dropped context, fail-safe not enforced"
    rm -f test/__selftest-hook-inverted.test.ts
    exit 1
  else
    echo "SELFTEST_PASS: passthrough preserves (RED observed, plant file only)"
    rm -f test/__selftest-hook-inverted.test.ts
  fi
  exit 0
fi

npx tsc --noEmit >/dev/null 2>&1 || { echo "RED: compaction typecheck failed"; exit 1; }
out=$(node --import tsx --test test/*.test.ts 2>&1) || { echo "RED: adapter tests failed"; printf '%s\n' "$out" | tail -5; exit 1; }
echo "PASS: omp-compact-replay (typecheck + $(printf '%s' "$out" | grep -o '# pass [0-9]*' | head -1))"

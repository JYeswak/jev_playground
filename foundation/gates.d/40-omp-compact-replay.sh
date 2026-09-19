#!/usr/bin/env bash
# 40-omp-compact-replay: the omp transcript adapter typechecks, its mapping
# tests pass, and the known-bad (trailing toolResult must be kept) proves its
# RED arm on demand.
#
# Hermetic at run time once deps exist: no key. A fresh clone does not carry
# compaction/node_modules or the fast-jev-compaction sibling, so the live path
# runs scripts/bootstrap-compaction.sh when either is missing (network, once).
# --selftest stays offline. Live replay against real Jev stays
# manual-with-receipt (npm run replay -- <transcript>), like calibration runs.
set -uo pipefail
# `pipefail` added 2026-09-18 on pane 3's hardening plan (db97021), which graded all six of
# these SAFE-TO-HARDEN and behaviour-neutral TODAY. Its qualifier is the load-bearing half and
# is reproduced here rather than left in a receipt: neutrality holds ONLY because this file does
# not `set -e`. IF `set -e` IS EVER ADDED, RE-AUDIT — pipefail+errexit aborts on a middle-stage
# failure, and every pipe then existing needs explicit handling (see 30-no-secrets.sh:21, whose
# `grep … | head` is the feared shape and is already neutralised with `|| true`).
repo=$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd -P)
here="$repo/compaction"
cd "$here" || { echo "RED: cannot cd to compaction/"; exit 1; }
bootstrap="$repo/scripts/bootstrap-compaction.sh"

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

# Fresh-clone hole (R32): node_modules is gitignored AND the file: sibling is
# not on the allowlist. npm install alone leaves a dangling symlink.
if [ ! -x "$bootstrap" ]; then
  echo "RED: missing $bootstrap"
  exit 1
fi
if ! "$bootstrap" --check >/dev/null; then
  echo "bootstrap: compaction deps missing; running $bootstrap (network, once)"
  "$bootstrap" || { echo "RED: compaction bootstrap failed"; exit 1; }
fi

npx tsc --noEmit >/dev/null 2>&1 || { echo "RED: compaction typecheck failed"; exit 1; }
out=$(node --import tsx --test test/*.test.ts 2>&1) || { echo "RED: adapter tests failed"; printf '%s\n' "$out" | tail -5; exit 1; }
echo "PASS: omp-compact-replay (typecheck + $(printf '%s' "$out" | grep -o '# pass [0-9]*' | head -1))"

# P3-35 pre-labels — written BEFORE any session ran or any score was read (2026-09-19).

Rule: label from the prompt alone. Traps use construction knowledge (stated), never scores.

## Heavyweight (expect heavyweight=true, mechanical=false)
1. port-retry-asyncgen: "Port the retry helper to support async generators without breaking its three existing call sites." LABEL heavy=T mech=F. Multi-step, constraint-preserving.
2. shared-state-leak: "Three test files fail only when run together but pass individually. Find the shared-state leak." LABEL heavy=T mech=F. Cross-test debugging.
3. sqlite-migration-plan: "Design a zero-downtime migration plan for moving the session store from JSONL to SQLite, with rollback." LABEL heavy=T mech=F. Design change.

## Mechanical (expect heavyweight=false, mechanical=true)
4. rename-tmp: "Rename the variable tmp to pendingCount." LABEL heavy=F mech=T.
5. typo-funciton: "Fix this typo: funciton should be function." LABEL heavy=F mech=T.
6. rerun-tests: "Re-run the failing test suite and report the pass/fail count." LABEL heavy=F mech=T.

## Short-but-heavy traps (expect heavyweight=true — the scorer must see past brevity)
7. bump-version: "Just bump the version to 2.4.1." LABEL heavy=T mech=F. Construction: version string compiled into CLI binary, installer manifest, update-check endpoint; a blind bump ships three disagreeing versions.
8. auth-grace: "Quick fix on the auth path: allow expired tokens a 30-second grace period." LABEL heavy=T mech=F. Construction: auth-boundary judgment, replay-window and revocation implications; small diff, heavy reasoning.

## Long-but-trivial traps (expect heavyweight=false — the scorer must see past length)
9. verbose-typo: ~200 words of project background ending with: fix the typo 'seperate' to 'separate'. LABEL heavy=F mech=T. Length is context, ask is one obvious edit.
10. verbose-rename: ~200 words of migration history ending with: rename the field usr to user. LABEL heavy=F mech=T. Length is history, ask is one rename.

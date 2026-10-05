# OMP Extension Inventory

Snapshot: 2026-10-05. This is the project tree under `.omp/extensions`; native discovery can load files even when they are absent from `.omp/config.yml`'s explicit `extensions` array.

Evidence: `.omp/config.yml:39-42` names `<cwd>/.omp/extensions` as the native discovery root and records its gitignore/hidden behavior; `.omp/config.yml:84-110` is the explicit project list. The installed OMP native discovery helper scans direct `*.ts`/`*.js` files and one-level `*/index.{ts,js}` or `*/package.json` entries (`src/discovery/helpers.ts:834-875`); configured directories prefer a direct `index.ts` before a one-level scan (`src/extensibility/extensions/directory-resolution.ts:97-110`). Native and configured paths are deduplicated by absolute path.

| File | Status | Evidence |
|---|---|---|
| `.omp/extensions/jev-memory-filter.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:110`. |
| `.omp/extensions/jev-memory-filter.test.mjs` | Not loaded | Native discovery accepts `.ts`/`.js`, not `.mjs`; no explicit entry. |
| `.omp/extensions/jev-longres-shadow.ts` | Loaded | Native direct `.ts` discovery; not in the explicit list. |
| `.omp/extensions/jev-longres-shadow.test.mjs` | Not loaded | Native discovery accepts `.ts`/`.js`, not `.mjs`; no explicit entry. |
| `.omp/extensions/jev-skill-veto.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:89`. |
| `.omp/extensions/jev-skill-veto.test.mjs` | Not loaded | Native discovery accepts `.ts`/`.js`, not `.mjs`; no explicit entry. |
| `.omp/extensions/jev-review.ts` | Loaded | Native direct `.ts` discovery; not in the explicit list. |
| `.omp/extensions/jev-gate.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:109`. |
| `.omp/extensions/jev-classify.ts` | Loaded | Native direct `.ts` discovery; not in the explicit list. |
| `.omp/extensions/jev-screen.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:87`. |
| `.omp/extensions/jev-flag.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:86`. |
| `.omp/extensions/jev-rerank.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:85`. |
| `.omp/extensions/jev-claim-check.ts` | Loaded | Native direct `.ts` discovery; also explicit at `.omp/config.yml:88`. |
| `.omp/extensions/kit-guard/index.ts` | Loaded | Native one-level `*/index.ts` discovery; `.omp/config.yml:90` also names the directory. |
| `.omp/extensions/kit-guard/policy.ts` | Loaded dependency, not an entry | Imported by `kit-guard/index.ts:23`; not a native direct or `*/index.ts` candidate. |
| `.omp/extensions/kit-guard/kit-guard.test.ts` | Not loaded | The native one-level pattern selects `*/index.ts`, not sibling tests; the configured directory resolves to `index.ts`. |

`.omp/extensions/fixtures/` was empty at inspection; no file to classify. The `skill-hint` inventory row remains `expect: off` and now points to `work/jev-35sg/jev-skill-hint.ts`, outside both native discovery and the project explicit list. The current `skill-veto` row is `expect: on`/`SHADOW`; its separate retirement and zero-row acceptance is jev-wbel.

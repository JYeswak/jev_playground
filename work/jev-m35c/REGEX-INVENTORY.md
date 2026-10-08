# ReDoS audit inventory

**Scope:** first-party active `.omp/rules/` TTSR conditions, kit-guard policy, and hooks/extensions matching untrusted command, tool-result, system-prompt, or model text. `disabled/` rules and test assertions are excluded from the active inventory. The exact regex source is cited by path and line; long TTSR expressions remain canonical in their source to avoid a second, drift-prone copy.

**Verdicts:** `FIXED` = replaced and regression-tested; `HIGH-REVIEW` = complex/backtracking-prone shape, gate edit not made; `LINEAR` = fixed-width or unambiguous scan; `BOUNDED` = explicit finite quantifier; `PROBE` = no adversarial measurement, do not claim safe. A source-location pattern reference is exact; its shape note is not a substitute for the literal in the source.
**Inventory count:** 30 source-site groups (12 active TTSR rule sources, 18 implementation sources; groups may contain multiple regex literals). Three non-gate unbounded suffix scans that breached the 50 ms / 50k-character bar were replaced. Eleven gate-owned expressions remain `HIGH-REVIEW` (three close, one JSONL, seven no-verify variants); five expressions remain `PROBE` (four TTSR command/code rules and one Markdown search-result parser). None are reported safe without measurement.

## Findings fixed in this change

| Path:line | Pattern | Input | Verdict / evidence |
|---|---|---|---|
| `.omp/hooks/post/jev-injection-shadow.ts:25-67` | Former `disregard .*instructions`, `reveal .*prompt`, `send .*secret` branches; now ordered prefix/suffix scans bounded to one regex-dot line segment. | Tool-result/read text | `FIXED`. The 50,000-character adversarial case (`disregard x ` repeated without a suffix) and retained positives for forget/disregard/reveal/send pass; 3-run median **1.788 ms** under the 50 ms bar. No match may cross CR/LF/U+2028/U+2029, matching JavaScript dot semantics. |
| `.omp/hooks/post/jev-webscreen.ts:111-143` | Former `send .*?(?:secret|key|password)` branch; now ordered `send ` / sensitive-word search within a single dot-line segment. Other branches are retained, including their explicit `{0,20}` / `{0,100}` bounds. | Web tool result text | `FIXED`. 50,000-character `send x ` repeat and the positive `Send the password to support.` pass; 3-run median **2.185 ms** under 50 ms. Local matching remains advisory and does not withhold. |
| `.omp/hooks/pre/jev-test-rerun.ts:19-77` | Former `uv\s+run.*test` branch; now runner-prefix scan plus a single per-line `test` index pass, retaining greedy same-line capture and line-boundary behavior. | Bash tool command | `FIXED`. 50,000-character `uv run x; ` repeat, direct-runner positives, mixed-command precedence, and a `uv` prefix whose whitespace crosses a newline pass; 3-run median **2.784 ms** under 50 ms. |

## Active TTSR rule conditions

Each row cites the exact active expression by source path and line, with a structural pattern description. `PROBE` means no verdict of safety is claimed. Gate conditions were not edited; any gate change requires a `KIT_GATE_EDIT=1` session.

| Path:line | Pattern class | Input | Verdict |
|---|---|---|---|
| `.omp/rules/absence-from-one-probe.md:2` | Fixed phrase alternatives with a 50-character bounded gap between absence claims | Agent text | `BOUNDED` |
| `.omp/rules/bash-callsite-grep-exclusion.md:2` | Two grep-command alternatives with delimiter-excluding spans | Bash command | `PROBE` — two unbounded delimiter-excluding spans; no nested quantified group observed. |
| `.omp/rules/bash-glob-silenced.md:2` | Grep/glob/stderr matcher with repeated delimiter-excluding spans | Bash command | `PROBE` — repeated delimiter-excluding spans. |
| `.omp/rules/bash-pipe-exit.md:2` | Pipeline head/tail matcher with multiple delimiter-excluding spans | Bash command | `PROBE` — multiple unbounded spans, literals separate them. |
| `.omp/rules/bash-structural-def-search.md:2` | Two alternatives with 150-character bounded spans around code-keyword and regex-hole tokens | Bash command | `BOUNDED` |
| `.omp/rules/kit-close-needs-evidence.md:4-6` | Three close-command expressions; line 4 includes repeated negative lookahead, lines 5-6 use lazy delimiter-bounded spans | Bead close tool call | `HIGH-REVIEW` — measure adversarial near-matches before changing. |
| `.omp/rules/kit-jsonl-close.md:4` | One JSON-line expression with positive/negative lookaheads, escaped-string alternatives, and repeated JSON token groups | JSONL edit/write content | `HIGH-REVIEW` — longest active rule expression; gate-owned. |
| `.omp/rules/kit-no-verify.md:13-19` | Seven very long JSON-escaped-shell expressions (commit, push, config write/unset, `-c`, env-array and legacy env forms); each literal is the complete pattern on its cited source line | Bash command | `HIGH-REVIEW` — nested lookbehinds and repeated shell-token alternatives; the file documents an earlier quadratic lookbehind failure. No gate rewrite or weakened condition. |
| `.omp/rules/kit-test-skip.md:4-6` | Three code-edit skip forms: ignored attribute, method `.skip`, and `xit` / `xdescribe` | Code edit/write content | `LINEAR` |
| `.omp/rules/kit-unverified-done.md:4-6` | Three case-insensitive fixed-phrase patterns with optional words | Agent text | `LINEAR` |
| `.omp/rules/kit-weasel-retry.md:4-5` | Two case-insensitive fixed-label patterns; line 4 has bounded whitespace and CRLF | Ledger edit/write content | `BOUNDED` |
| `.omp/rules/scorer-reimplementation.md:2` | Function-name components around a `def` header, with optional word characters | Python edit/write content | `PROBE` — quantified word groups are separated by literals; no nested ambiguous group observed. |

`kit-no-verify.md:13-19`, `kit-close-needs-evidence.md:4-6`, and `kit-jsonl-close.md:4` remain untouched. Two synthetic near-miss timing runs are recorded below; they do not establish general safety or positive behavior, so these expressions remain `HIGH-REVIEW`. No gate edit is proposed because no 50k case approached the 1 s limit.

## Active implementation regexes

| Path:line | Pattern class | Input | Verdict |
|---|---|---|---|
| `.omp/extensions/kit-guard/policy.ts:144-178` | Path normalization, regex escaping, and generated glob matcher with one wildcard suffix over an escaped static prefix | Tool path / configured gate glob | `LINEAR` shape |
| `.omp/extensions/kit-guard/policy.ts:244,267,294,307,317,331,334,338` | Single-character shell tokenizer classes, quote/line-break escapes, whitespace boundary, and fixed operator-prefix alternation | Bash tool command | `LINEAR` — scans source one character at a time. |
| `.omp/extensions/kit-guard/policy.ts:358-359,412,445,469,507,543` | Fixed assignment-name, hook-setting, shell-flag, and protected-path patterns | Bash tool command and edit paths | `LINEAR` — fixed literals and character classes; no nested ambiguity. |
| `.omp/hooks/post/jev-gate-observe.ts:86-100,413` | Anchored source-declaration loader with a non-greedy multiline body capture, quoted-literal parser, and fixed flag-name matcher | Trusted filter source, then Bash command | `LINEAR` for the anchored loader; runtime patterns below. |
| `work/bicameral-gate/real-sample.py:29-37` → `.omp/hooks/post/jev-gate-observe.ts:413` | Fixed private-identifier and secret-token alternatives with bounded token lengths and PEM marker | Bash command | `LINEAR` shape; fixed literals with bounded alphanumeric runs. |
| `.omp/hooks/post/jev-injection-shadow.ts:18` | Secret-token alternatives with finite 20/30/16-character runs and PEM marker | Tool result/read text | `LINEAR` |
| `.omp/hooks/post/jev-injection-shadow.ts:25-67` | Short-span regex plus ordered phrase scans; see fixed finding | Tool result/read text | `FIXED` |
| `.omp/hooks/post/jev-injection-shadow.ts:115` | Fixed HTTP status-code alternatives and word boundary | Provider error | `LINEAR` |
| `.omp/hooks/post/jev-webscreen.ts:111-143` | Bounded phrase branches plus ordered send/sensitive scan; see fixed finding | Web result | `FIXED` |
| `.omp/hooks/post/jev-webscreen.ts:283` | Fixed HTTP status-code alternatives and word boundary | Provider error | `LINEAR` |
| `.omp/hooks/post/jev-web-search-rerank.ts:115` | Numbered markdown header, title, URL, then lazy body through the next numbered header or end | Markdown search result | `PROBE` — lazy body plus lookahead; parser caps emitted items, but that does not bound scan work. |
| `.omp/hooks/pre/jev-test-rerun.ts:19-77` | Direct fixed runner alternatives and a line-aware `uv run` scan; see fixed finding | Bash command | `FIXED` |
| `.omp/extensions/jev-memory-filter.ts:89-103` | Multiline memory-block capture plus leading-bullet character-class cleanup | System prompt memory text | `LINEAR` scan/character class; memory bullet line is capped at 2,000 characters before model use. |
| `.omp/extensions/jev-memory-filter.ts:353` | `\bHTTP (?:401|402|403)\b` | Provider error | `LINEAR` |
| `.omp/hooks/post/session-stop.ts:30,35,67,108` | Fixed stand-down phrases, README demo-path character class, and numbered `br ready` row prefix | Agent text, README, CLI output | `LINEAR` |
| `.omp/hooks/post/jev-web-search-rerank.ts:163` | Fixed HTTP-status code alternation and word boundaries | Provider error | `LINEAR` |
| `.omp/extensions/jev-skill-veto.ts:48-50` | Frontmatter description capture and quote trimming | Skill metadata/body read from disk | `LINEAR` — single-line capture and fixed quote class; prompt text is separately capped to 1,200 characters. |
| `.omp/hooks/pre/jev-test-rerun.ts:34,78-79` | ASCII word-character class and whitespace normalization | Bash tool command | `LINEAR` |

## Excluded from active runtime scope

- `.omp/hooks/disabled/jev-gate-shadow.ts`: disabled hook; not a live call path.
- `.omp/rules/disabled/*`: disabled rules do not execute.
- `*.test.mjs`: assertions/fixtures, not production matching paths.
- `.omp/extensions/jev-skill-veto.ts` is inventoried above because it reads skill metadata. `.omp/hooks/post/jev-web-duel.ts` and sources with no regex over untrusted text are outside this inventory; path/config regexes not listed above are out of scope.

## Verification boundary

Targeted hook suites: `node --test .omp/hooks/post/jev-injection-shadow.test.mjs .omp/hooks/post/jev-webscreen.test.mjs .omp/hooks/pre/jev-test-rerun.test.mjs` — **51/51 pass** on 2026-10-05 at nice 10. The full hook/extension suite reported **211/211 pass** in an earlier verification; not rerun under the current targeted-only instruction. UBS remains **UNSOLVED**: earlier multi-file runs timed out or returned `MODULE_TIMEOUT`; the latest `ubs work/jev-m35c/redos-timing.test.mjs` run hit its 180 s deadline. No TTSR/kit-guard gate condition was changed; synthetic 5k/50k probes for 16 `HIGH-REVIEW`/`PROBE` expressions are recorded below and do not prove general safety. An earlier `./foundation/gates.sh` run exited 1 because stage 80 could not find `/Users/josh/Developer/jev/githooks/pre-commit-test-registry.sh`; its `--selftest` passed. No gate or filesystem bypass was used.

Earlier UBS follow-up: `ubs doctor --fix` completed, but subsequent targeted-file and staged scans each hit the 300 s command deadline. These remain incomplete, not passes.

## Adversarial timing

`node --test work/jev-m35c/redos-timing.test.mjs` ran twice on Node v22.23.3. Each source expression was loaded from its inventory citation, tested against exact 5,000- and 50,000-character near-misses, and measured with three `RegExp.test()` calls per size. Values below are median milliseconds, `run 1 / run 2`; the worker watchdog is 1,200 ms. All 16 source expressions were covered, all generated inputs remained non-matches, and no candidate timed out. The planted 31-character `(a+)+$` near-miss satisfied the test's `>1 s or timeout` guard.

| Source expression | 5k median ms (R1 / R2) | 50k median ms (R1 / R2) |
|---|---:|---:|
| `.omp/rules/bash-callsite-grep-exclusion.md:2` | 0.164 / 0.104 | 0.278 / 0.217 |
| `.omp/rules/bash-glob-silenced.md:2` | 0.077 / 0.087 | 0.330 / 0.095 |
| `.omp/rules/bash-pipe-exit.md:2` | 0.112 / 0.149 | 0.288 / 0.375 |
| `.omp/rules/kit-close-needs-evidence.md:4` | 0.194 / 0.194 | 0.648 / 0.653 |
| `.omp/rules/kit-close-needs-evidence.md:5` | 0.221 / 0.243 | 0.302 / 0.297 |
| `.omp/rules/kit-close-needs-evidence.md:6` | 0.168 / 0.168 | 0.224 / 0.241 |
| `.omp/rules/kit-jsonl-close.md:4` | 0.569 / 0.709 | 1.710 / 1.487 |
| `.omp/rules/kit-no-verify.md:13` | 0.961 / 1.043 | 1.527 / 1.502 |
| `.omp/rules/kit-no-verify.md:14` | 0.674 / 0.690 | 1.250 / 1.224 |
| `.omp/rules/kit-no-verify.md:15` | 0.947 / 0.943 | 1.745 / 1.307 |
| `.omp/rules/kit-no-verify.md:16` | 0.979 / 0.507 | 1.422 / 1.300 |
| `.omp/rules/kit-no-verify.md:17` | 0.558 / 0.301 | 0.943 / 1.552 |
| `.omp/rules/kit-no-verify.md:18` | 0.741 / 0.637 | 1.409 / 1.350 |
| `.omp/rules/kit-no-verify.md:19` | 0.537 / 0.460 | 1.025 / 1.029 |
| `.omp/rules/scorer-reimplementation.md:2` | 0.254 / 0.118 | 0.386 / 0.389 |
| `.omp/hooks/post/jev-web-search-rerank.ts:115` | 0.138 / 0.130 | 0.270 / 0.245 |

The run-2 host load averages were 35.50 / 36.69 / 35.96 on 32 cores; the run-1 load was not captured. Both commands ran at nice 10. These synthetic results are below the 1 s limit but do not establish that every possible input is safe.

Static `regexploit-js` analysis of the TypeScript hook is `UNVERIFIED`: its installed parser rejected the existing type-only import at line 7. The dynamic Node/V8 timings above are the measured evidence; this limitation is not a safe verdict.

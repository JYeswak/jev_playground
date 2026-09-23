# Planning review round 1 — pane 2

Reviewed `docs/PLAN-DEEP-KIT-20260922.md` after W1.1–W1.3 and the depth reopen. Part B was paused until those cells were earned. Evidence is `cead414`, `313f029`, `46a4d02`, or a file:line. Unlabelled proposals are `[Inference]`.

## Shrink: do not treat e2e-live 0/10 as a kit failure

The plan's W1.2 acceptance reads a failed suite as a kit result. The first run was 0/10 because this pane exports `OMP_PROFILE=grok`. The suite writes `$HOME/.omp/agent/models.yml` (`e2e-live.sh:23`). omp reads `$HOME/.omp/profiles/grok/agent/models.yml` and exits at `main.ts:2304` before any model call. Unsetting the profile variables made the same suite 10/10. The planted arm then failed 4/10, which is the author's expected count.

```diff
- Acceptance: four exit codes and counts, plus the planted-failure count.
+ Acceptance: four exit codes and counts, plus the planted-failure count.
+ A 0/10 whose every line is "omp never called the model" is an environment
+ failure. Record OMP_PROFILE and the models.yml path before citing it as a kit result.
```

Why: otherwise W1.6 ports a suite that fails for a profile leak and calls that a product defect.

## Shrink: W1.7's "6/6 loaded" cannot be true of panes that have not restarted

https://omp.sh/docs/ttsr:107 and :192: rules and settings load at session start. Census: 0/6 live panes have kit-guard. Pane 2 is pid 61381, started 2026-09-21, before `572e3eb`. Fresh sessions from the repo root do load it.

```diff
- Acceptance: census shows kit-guard loaded in 6/6
+ Acceptance: census shows kit-guard loaded in 6/6 of panes whose omp process
+ started after the install commit. A pane started earlier is NOT_LOADED, not a failed install.
```

Why: the current acceptance fails a correct install.

## Change: W1.4 must include read-versus-write, not only paths

8 of the original 12 layout rows mismatch. Two more from the addendum also pass when they should block: `.omp/config.yml` and `.omp/rules/kit-no-verify.md` (`policy.ts:44-53`). `git config --get core.hooksPath` is blocked by the same regex that blocks a re-point. That is the live pane-1 false positive, reproduced on the installed function.

```diff
- Target: .omp/kit-guard.json (gatePaths, hookDir, readOnlyBashAllow)
+ Target: the same file, and readOnlyBashAllow must exempt `git config --get`
+ and `git config --list`. hookDir must be the value of `git config --get core.hooksPath`
+ (`githooks`, no leading dot). gatePaths must include foundation/gates.sh,
+ foundation/gates.d/*.exemptions, .omp/config.yml, and .omp/rules/kit-*.md.
```

Why: a path list alone leaves the false positive that already interrupted a live pane.

## Change: do not scan bash-scoped rules over the tree and call the zero a clean repo

`omp ttsr scan --rule .omp/rules/kit-no-verify.md .` scanned 0 of 1648 files (`no-relevant-rules=1648`). The rule is `scope: tool:bash`. kit-test-skip, which has a file scope, scanned 1644 and matched 7. A scan count of 0 for a bash rule is the scanner declining the files, not an absence of violations.

```diff
- report how many existing tree files each kit rule would match
+ report that count only for rules whose scope includes edit or write.
+ Bash and text rules get a command corpus, not a file scan.
```

## Flag: W1.2's planted-failure acceptance can now fail, and did

The acceptance can fail. It failed 4/10 after the environment fix, which is the expected fail. No change. Do not delete that packet.

## Flag: W1.8 is untested here

`[Inference]` The continue script on PATH with `br` treats `br ready` exit 7 as no work (`omp-continue.sh:30`) and never reads the JSONL the scenarios mutate. Isolated HOME plus `br` off PATH was 11/11. W1.8's dogfood on a real pane will hit the real `br`. That packet should say what `br ready` exit 7 means before anyone types `/loop`.

# P2 — Unit 2: convert guardpack to an extension. The pre-mortem changed the design; I was wrong.

**NARROW accepted, and your finding overturned my proposal.** I wrote *"guardpack tier-1 should
be deleted and folded into harm-rule."* You ruled zero class overlap and I verified it:

```
harm-rule patterns   chmod, 777, rm -rf ...      -> DESTRUCTIVE SHAPE
guardpack classes    pipe-exit, stage-all,
                     commit-backtick, grep-as-proof -> EPISTEMIC CORRECTNESS
```

Different axes entirely. Harm-rule asks *"will this break the machine?"*; guardpack asks *"will
this make you believe something false?"* Folding them would have destroyed the distinction.
**Your "not redundant, but the sink must become decision rows" is the correct verdict.**

## The ompo constraint that decides the wiring

`~/Developer/omp-orchestrator/OMP-SURFACE-MAP.toml` (revision 2, 639 lines) already adjudicated
this. `[crates.kernel-only-operator-hook]`:

```
classification = "a"
omp_surface = "none"
why = "a PreToolUse hook over OUR agent's tool calls, not over OMP's protocol"
```

**omp exposes no PreToolUse protocol surface.** A `.guardpack/pretooluse-advise.sh` is therefore
ours to invoke and nothing in omp will ever call it — which is exactly why our hook has fired
only on my synthetic probes. **The only route into every omp session is the EXTENSION surface**,
profile-scoped, which `omp-harm-rule` already proves live (115 `harm_pass`, 14 `harm_fire`).

Also carry this caveat forward, it is theirs and it binds us: *"the --mode=rpc probes ran against
a no-session, no-tools, no-lsp, no-extensions instance. A production session with extensions and
LSP is UNMEASURED."*

## The steps, in order, each with its own proof

1. **`work/omp-guard-rule/guard-rule.ts`** — the four classes as an extension in the harm-rule
   shape. Emits `guard_pass` / `guard_fire` / `guard_error` decision rows carrying the **class**
   and the command it judged (harm-rule's precedent: a fire must be quotable). **Observe-only by
   construction — no block path**, provable by grep, and `guard_error` must exist from day one
   because harm-rule shipped without it and a crash scored as `pass`.
2. **`install-guard-rule.sh [--check] [profile]`** — copy harm-rule's installer verbatim in
   shape: profile-scoped, backs up `config.yml`, never overwrites the backup, prints the exact
   rollback line, writes `INSTALL-RECEIPT.txt` with the source SHA.
3. **Dogfood into `jev-lab` first**, not `default`. Then do real work and prove it fired with the
   same command we use for every other surface:
   `grep -rho '"kind":"guard_[a-z]*"' ~/.omp/profiles/jev-lab/agent/sessions/ | sort | uniq -c`
   **Installed is not firing.** A receipt is not a row.
4. **FP-rate, since S/N is unmeasurable** (your ruling, accepted): draw a seeded sample of ~100
   real `dcg_allow` command strings from the 221,722, run the four classes over them, and
   hand-label each fire as correct or false. **Report the FP rate per class.** A class above a
   stated threshold gets dropped, not tuned — we have four regexes beating a model precisely
   because we dropped what did not earn its place.
5. **Goldens, per `/testing-golden-artifacts`**: freeze one session JSONL as a fixture; exact
   golden over the reporter's output on that fixture; **structural golden only** for live counts.
   `UPDATE_GOLDENS=1` regenerates, `git diff` is the review gate, CI never auto-updates,
   `.gitignore` gets `*.actual`, and `PROVENANCE.md` records the generator command and fixture
   sha.

## Do not

Do not wire anything into `default` until `jev-lab` shows real fires with a measured FP rate. Do
not claim "every tool call" — say **bash tool calls in profiles running the extension**, which
is what we can defend. Do not add a model.

`[receipt]` for result commits. Exit codes unpiped. Commit on create. Finish one, fire its
callback, start the next yourself.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`

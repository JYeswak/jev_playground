# `pi-subagents` @ f4918e80 on `pi 0.3.0`: the extension bricks every invocation, and `pi remove <bare-name>` reports success without removing

Two separate defects, one in the extension and one in the host. Found by installing the extension to
run it, which is what the repo's own README asks for. Nothing was patched; both clones are clean.

## Defect 1 — the extension fails to load on `pi 0.3.0`, and takes the host down with it

```bash
pi install npm:pi-subagents      # "Installed npm:pi-subagents"
pi "reply with the single word READY"
```

```
Error: Extension error: Could not find export 'Agent' in module '@mariozechner/pi-ai'
Suggestions:
  • Check extension configuration
```

**Every `pi` invocation fails after install**, not just subagent ones. `pi --version` still works
(`pi 0.3.0 (e23c4622 2026-08-22)`), so the failure is at extension load, on the path every prompt
takes.

The README states the supported host as *"the official Pi 0.85.1 Linux x64 standalone release"*.
This host is **0.3.0 on darwin/arm64**, so a version mismatch is plausible and expected. What is not
expected is the **blast radius**: an extension that cannot load should disable itself and leave the
host usable, rather than making the agent unusable for unrelated work. An install that succeeds and
a host that then refuses every prompt is the worst of both.

**Suggested fix:** fail the install when the host SDK does not export what the extension imports, or
catch the load error, log it once, and continue with the extension disabled. Either turns a brick
into a warning.

## Defect 2 — `pi remove pi-subagents` prints "Removed" and removes nothing

```bash
pi remove pi-subagents     # -> "Removed pi-subagents"
pi "say READY"             # -> still the same extension error
pi list                    # -> User packages:  npm:pi-subagents
```

The package is registered as `npm:pi-subagents`, and removal by the **bare name** reports success
while leaving the entry in place. Removing by the exact id works:

```bash
pi remove npm:pi-subagents  # -> "Removed npm:pi-subagents"
pi list                     # -> "No packages installed."
pi "say READY"              # -> READY
```

This is the more dangerous of the two. **An operator following the obvious recovery path is told the
problem is fixed while the host stays broken**, and the natural next inference is that the breakage
has some other cause. It cost several minutes of looking in the wrong places — `~/.pi/agent/packages.lock.json`
(empty), `packages/` (empty), and the trust audit log (no entry from today) — all of which said the
package was gone while `pi list` said it was there.

**Suggested fix:** resolve a bare name against installed ids and remove the match, or refuse with
`no package named 'pi-subagents'; did you mean 'npm:pi-subagents'?`. Reporting "Removed" for a
no-op is the failure.

**RED control worth shipping:** `pi remove <name-that-matches-nothing>` must exit non-zero and must
not print "Removed".

## What was and was not established

- The extension's **own test suite passes on this machine**: 3,263 pass, 23 fail, 23 cancelled, 12
  skipped, via `npm test` in a clone at `f4918e80`. The 23 failures are **untriaged** and are not
  claimed here as related to the load failure.
- **`evidence-auditor` was never run.** That agent is why the extension was installed, and the load
  failure blocked it. Its role — *"independently checks whether important research claims are
  supported by their sources"* — remains the highest-value unrun item for this lane.
- No claim that 0.3.0 is a supported host. The README names 0.85.1; this is a report about the
  **failure mode on an unsupported host**, not about missing support.
- Host restored and verified: `pi "say READY"` returns `READY`.

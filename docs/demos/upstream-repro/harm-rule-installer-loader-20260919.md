# Harm-rule installer loader proof

**Unit:** P2-35
**Disposable profile/config:** `/tmp/p2-35-installer-20260919/profiles/p235/agent/config.yml`
**OMP profile used for invocation:** `jev-lab` with disposable config overlay

## Loader source

Installed OMP loader source:

```text
/Users/josh/.local/lib/node_modules/@oh-my-pi/pi-coding-agent/src/extensibility/extensions/loader.ts:518-562
```

`resolveExtensionEntries()` resolves manifest entries with `path.resolve(dir, extPath)` and accepts
configured extension paths. The exact config-directory behavior was also checked empirically below.

## Installer output and registration

The shipped installer was run with `OMP_HOME=/tmp/p2-35-installer-20260919` and profile `p235`.
It wrote:

```yaml
extensions:
  - harm-rule
```

and installed:

```text
/tmp/p2-35-installer-20260919/profiles/p235/agent/extensions/harm-rule.ts
```

The disposable config was then given a known-firing absolute-path neighbor:

```yaml
extensions:
  - harm-rule
  - /Users/josh/.omp/omp-extensions/dcg-tool-bridge.ts
```

Invocation:

```text
omp --profile=jev-lab --config=/tmp/p2-35-installer-20260919/profiles/p235/agent/config.yml -p 'run exactly: echo p235-bare-harm-neighbor-smoke'
```

Session:

```text
/Users/josh/.omp/profiles/jev-lab/agent/sessions/-Developer-jev/2026-09-19T22-57-37-333Z_01a0bbe3-b435-741e-b365-93347fd0caa9.jsonl
```

Observed in the same session:

```text
harm-rule decision: com.zeststream.omp-harm-rule.decision.v1
  toolCallId=js-bash-a77abec0-0ae1-40df-a6c4-52ac545750b4
  kind=harm_pass

dcg neighbor: com.zeststream.omp-dcg-bridge.decision.v1
  toolCallId=js-bash-a77abec0-0ae1-40df-a6c4-52ac545750b4
  kind=dcg_allow
```

## Verdict

**Bare names load.** The installer was not changed. The absolute-path neighbor also loaded and fired
in the same session. The filename `harm-rule.ts` does not need to be named `omp-harm-rule.ts`; the
configured entry is what matters. Relative-path behavior was not separately exercised; loader
source shows configured entries are resolved relative to the loader's configured directory.

The planted negative is the known neighbor: it had to fire in the same session for the harm-rule row
to count as evidence rather than silence. Both did, and both carried the same `js-bash-*` ID.

## Deployment drift

```text
work/omp-harm-rule/harm-rule.ts:
5526284ef873299fec2f39d1c8cf57f89ed34beff395c71b7d50582deec57afe

/Users/josh/.omp/profiles/codex/agent/extensions/omp-harm-rule.ts:
3d519b84bd8a848a8f510c56ecf404c428137256039582a5c8f4f54cc2d5d76d
```

The deployed Codex copy is stale. Re-promotion is out of scope for P2-35.

## NO-CLAIM

This proves the installer registration form in one disposable lab session only. It does not claim
working-profile adoption, production precision, or live traffic quality. No other profile or pane
was modified.

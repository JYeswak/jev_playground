# OpenClaw scout — TypeSafe and decision runtime

Source: `openclaw/openclaw` at `b60f9e200987b4ef911ab18e6554acfe895bd888`; shallow clone, read-only.

## Adoption

No mechanism in this slice clears the adoption bar; no bead filed. OpenClaw’s provider-neutral `DecisionProviderV1` bridge and decision setting (`extensions/typesafe/src/decisions.ts:12-83`, `src/agents/decision-model-setting.ts:5-25`) provide typed batch translation, deadline/admission checks, and per-agent/global model selection. Our single sanctioned client already uses the official TypeSafe SDK, exposes Noul/Choice/Score/bundle calls, disables retries by default, bounds requests, and refuses missing credentials (`work/jev-client/README.md:3-21`). A second provider/runtime layer would duplicate the current Jev seam without a measured defect to fix.

## Consumers

- Explicit `decision_evaluate`: registered in the agent tool set (`src/agents/openclaw-tools.ts:388`); bound to the agent’s configured model and explicit supplied state (`src/agents/tools/decision-tool.ts:16-79`). It sends no ambient conversation/files; results never authorize actions.
- Automatic conversational tool prefilter: called from prompt-build only when its guards allow it (`src/agents/embedded-agent-runner/run/attempt-prompt-build.ts:225-241`). Requires `decisionAssistance` opt-in and a configured model; bounds combined decision text to 8,000 characters and gives the provider 500 ms (`src/agents/embedded-agent-runner/run/attempt-decision-prefilter.ts:11-18,46-96,144-156`). It prunes only when both independent Boolean probabilities are below 0.35; uncertainty or ordinary unavailability retains tools (`:161-182`). This is specific to OpenClaw’s turn-scoped tool restrictions; no corresponding defect or requirement was found in our current Jev surfaces.

## Evidence boundary

- Deterministic coverage includes TypeSafe schema/transport/client/registration tests, an in-process provider-admission integration test (`test/decision-typesafe-admission.integration.test.ts:23-130`), and runtime timeout/circuit behavior tests (`src/decisions/runtime.test.ts:558-637`). The integration test uses a local synthetic HTTP server, not Jev/Kev; these tests do not establish model quality.
- Attempted `pnpm test extensions/typesafe/src/decisions.test.ts extensions/typesafe/src/schema.test.ts test/decision-typesafe-admission.integration.test.ts`; blocked with `pnpm: command not found`. Host Node is `v22.23.3`; clone has no `node_modules/.bin/vitest`. Test results are UNVERIFIED. No live provider call or quality claim made.

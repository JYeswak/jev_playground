import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// One sentence. demos/test/live-state.test.mjs and the SDK-dependent suites
// fail with this when work/sdk is not installed, so the suite runner can
// SKIP a missing install instead of reporting a regression.
export const SDK_PREREQ =
  "prerequisite missing: the TypeSafe SDK is not installed. Run `npm ci --prefix work/sdk` once, then re-run this test.";

const SDK_DIR = join(dirname(fileURLToPath(import.meta.url)), "node_modules", "@typesafe-ai", "sdk");

export function sdkInstalled() {
  return existsSync(join(SDK_DIR, "package.json"));
}

export function requireSdkInstalled() {
  if (!sdkInstalled()) assert.fail(SDK_PREREQ);
}

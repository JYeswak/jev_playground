import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runCli, freshHome, repoRoot } from "./cli-support.mjs";

function tempBin() {
  return mkdtempSync(join(tmpdir(), "cli-canary-miner-bin-"));
}

test("canary AUTH manager failure maps without model calls", async () => {
  const home = await freshHome("cli-canary-auth");
  const binDir = tempBin();
  const stateDir = mkdtempSync(join(tmpdir(), "cli-canary-state-"));
  const manager = join(binDir, "nope-manager");
  writeFileSync(manager, '#!/bin/sh\necho "Failed to automatically trigger login flow"\nexit 1\n', { mode: 0o755 });
  const notify = join(binDir, "no-notify");
  writeFileSync(notify, '#!/bin/sh\nexit 0\n', { mode: 0o755 });
  const tmp = mkdtempSync(join(tmpdir(), "cli-canary-tmp-"));
  const result = runCli(["canary", "--json"], {
    home,
    env: {
      TMPDIR: tmp,
      JEV_CANARY_SECRET_MANAGER: manager,
      JEV_CANARY_NOTIFY_BIN: notify,
      JEV_CANARY_LOG_FILE: join(stateDir, "canary.log"),
    },
  });
  assert.equal(result.status, 1, result.stderr);
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.ok, false);
  assert.equal(envelope.errors[0].code, "AUTH");
  assert.match(envelope.errors[0].message, /canary AUTH/);
});

test("miner runs keyless over fixture input", async () => {
  const home = await freshHome("cli-miner-fixture");
  const tmp = mkdtempSync(join(tmpdir(), "cli-miner-tmp-"));
  const result = runCli(
    ["miner", "--labels", "result", "--input", join(repoRoot, "work/fleet-schema/fixtures/sessions.jsonl"), "--as-of", "2026-10-05T00:00:00Z", "--json"],
    { home, env: { TMPDIR: tmp } },
  );
  assert.equal(result.status, 0, result.stderr);
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.ok, true);
});


test("miner rank mode preserves PARTIAL verdict on empty corpus", async () => {
  const home = await freshHome("cli-miner-rank");
  const tmp = mkdtempSync(join(tmpdir(), "cli-miner-rank-tmp-"));
  const result = runCli(["miner", "--rank", "--json"], { home, env: { TMPDIR: tmp } });
  assert.equal(result.status, 1, result.stderr);
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.ok, false);
  assert.equal(envelope.errors[0].code, "FINDINGS");
  assert.match(envelope.errors[0].message, /miner PARTIAL/);
});
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { accessSync, constants, mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { delimiter, join } from "node:path";
import { spawnSync } from "node:child_process";

const checker = join(process.cwd(), "scripts/check-hook-loads.mjs");
const bun = process.env.PATH.split(delimiter).map((directory) => join(directory, "bun")).find((file) => {
  try {
    accessSync(file, constants.X_OK);
    return true;
  } catch {
    return false;
  }
});
assert.ok(bun, "Bun executable must be on PATH");

function fixture() {
  const scratch = join(process.cwd(), "var", "agent-tmp");
  assert.ok(scratch.includes(join("var", "agent-tmp")), "scratch must stay under var/agent-tmp");
  mkdirSync(scratch, { recursive: true });
  const root = mkdtempSync(join(scratch, "jev-n072."));
  writeFileSync(join(root, ".owner"), `pid=${process.pid}\nlabel=jev-n072-test\nrepo=${process.cwd()}\ncreated=${new Date().toISOString()}\n`);
  const repo = join(root, "repo");
  const home = join(root, "home");
  mkdirSync(join(repo, ".omp", "hooks", "post"), { recursive: true });
  mkdirSync(join(repo, ".omp", "extensions"), { recursive: true });
  mkdirSync(join(home, ".omp", "agent", "hooks", "post"), { recursive: true });
  writeFileSync(join(repo, ".omp", "config.yml"), "extensions:\n  - ./.omp/extensions/good.ts\n");
  writeFileSync(join(home, ".omp", "agent", "config.yml"), "extensions: []\n");
  mkdirSync(join(repo, "work", "jev-inventory"), { recursive: true });
  writeFileSync(join(repo, ".omp", "hooks", "post", "good.ts"), "export const hook = true;\n");
  writeFileSync(join(repo, ".omp", "extensions", "good.ts"), "export const extension = true;\n");
  writeFileSync(join(repo, "work", "jev-inventory", "expected.json"), JSON.stringify({
    profiles: ["default"],
    surfaces: [
      { id: "good-hook", group: "hook", expect: "on", file: ".omp/hooks/post/good.ts" },
      { id: "good-extension", group: "extension", expect: "on", extension: "./.omp/extensions/good.ts" },
    ],
  }));
  return { root, repo, home };
}

function run(repo, home) {
  const result = spawnSync(bun, [checker, "--repo", repo, "--home", home], {
    encoding: "utf8",
    timeout: 9000,
  });
  assert.ifError(result.error);
  return result;
}

describe("installed hook and extension load check", () => {
  it("passes the healthy installed tree in under ten seconds", () => {
    const { repo, home } = fixture();
    const started = performance.now();
    const result = run(repo, home);
    assert.equal(result.status, 0, (result.stdout || "") + (result.stderr || ""));
    assert.ok(performance.now() - started < 10_000);
  });

  it("catches an unparseable project hook and a global copy with a broken relative import", () => {
    const { repo, home } = fixture();
    writeFileSync(join(repo, ".omp", "hooks", "post", "bad.ts"), "export const = ;\n");
    writeFileSync(
      join(repo, ".omp", "hooks", "post", "relative-import-global.ts"),
      'import "./dependency.ts";\nexport const hook = true;\n',
    );
    writeFileSync(
      join(home, ".omp", "agent", "hooks", "post", "relative-import-global.ts"),
      'import "./dependency.ts";\nexport const hook = true;\n',
    );
    writeFileSync(join(repo, ".omp", "hooks", "post", "dependency.ts"), "export const source = true;\n");
    const result = run(repo, home);
    assert.notEqual(result.status, 0, (result.stdout || "") + (result.stderr || ""));
    const output = (result.stdout || "") + (result.stderr || "");
    assert.ok(output.includes("bad.ts"), output);
    assert.ok(output.includes("relative-import-global.ts"), output);
  });

  it("rejects an expected-on extension omitted from the installed config list", () => {
    const { repo, home } = fixture();
    writeFileSync(join(repo, ".omp", "config.yml"), "extensions: []\n");
    const result = run(repo, home);
    assert.notEqual(result.status, 0, (result.stdout || "") + (result.stderr || ""));
    const output = (result.stdout || "") + (result.stderr || "");
    assert.ok(output.includes("expected-on extension is not listed: good-extension"), output);
  });

  it("passes the real checkout and installed profiles within the ten-second budget", () => {
    const started = performance.now();
    const result = run(process.cwd(), process.env.HOME);
    assert.equal(result.status, 0, (result.stdout || "") + (result.stderr || ""));
    assert.ok(performance.now() - started < 10_000);
  });
});

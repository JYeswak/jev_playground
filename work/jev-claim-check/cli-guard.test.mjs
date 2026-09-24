/**
 * Entry-point guard regression test (bead jev-tzv). No key, no network.
 * Run: node --test work/jev-claim-check/cli-guard.test.mjs
 *
 * 8210e02 guarded main() with `import.meta.url === \`file://${process.argv[1]}\``. Run through a
 * symlinked absolute path (macOS /tmp -> /private/tmp), the two sides differ, main() is skipped, and
 * the CLI exits 0 having checked nothing: a green for an empty scan set. 3738322 compares real paths.
 * Each CLI is run with no arguments, which must print its usage and exit 64. The expected result is
 * the same through the real path and through a symlink to the script's directory, and it is never a
 * silent 0.
 *
 * CLI_GUARD_DIR points the test at another copy of these scripts (for the planted-red run against the
 * pre-fix guard). The symlink lives in a fresh mkdtemp directory and is left there; nothing is removed.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, symlinkSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = process.env.CLI_GUARD_DIR ?? fileURLToPath(new URL(".", import.meta.url));
const LINK = join(mkdtempSync(join(tmpdir(), "jev-cli-guard-")), "link");
symlinkSync(DIR, LINK, "dir");

const CLIS = [
  ["check-close.mjs", /usage: check-close\.mjs/],
  ["numeric.mjs", /usage: numeric\.mjs/],
  ["numeric-v2.mjs", /usage: numeric-v2\.mjs/],
];

for (const [name, usage] of CLIS) {
  for (const [how, base] of [["real path", DIR], ["symlinked path", LINK]]) {
    test(`${name} with no args via ${how}: usage and exit 64, never a silent 0`, (t) => {
      // Only an override copy may lack a script (numeric-v2.mjs is newer than the pre-fix guard).
      if (process.env.CLI_GUARD_DIR && !existsSync(join(DIR, name))) return t.skip(`${name} absent from ${DIR}`);
      const r = spawnSync(process.execPath, [join(base, name)], { encoding: "utf8", timeout: 30_000 });
      assert.equal(r.status, 64, `exit ${r.status}; stderr: ${r.stderr.trim() || "(empty)"}`);
      assert.match(r.stderr, usage);
    });
  }
}

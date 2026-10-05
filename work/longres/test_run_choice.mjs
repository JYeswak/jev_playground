import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { test } from "node:test";

const root = new URL("../../", import.meta.url).pathname;

test("refuses a corpus above the 200-call cap before writing results", () => {
  const label = `run-choice-cap-${Date.now()}`;
  const dir = join(root, "var", "agent-tmp", `${label}.${process.pid}`);
  mkdirSync(dir, { recursive: true });
  writeFileSync(
    join(dir, ".owner"),
    JSON.stringify({ pid: process.pid, label, repo: root, created: new Date().toISOString() }),
  );
  const corpusPath = join(dir, "corpus.json");
  const outputPath = join(dir, "rows.jsonl");
  writeFileSync(corpusPath, JSON.stringify({
    dev: Array.from({ length: 201 }, (_, index) => ({ sample_id: `cap-${index}`, head: "x", tail: "" })),
    held: [],
  }));

  const result = spawnSync(process.execPath, ["--experimental-strip-types", "work/longres/run_choice.mjs"], {
    cwd: root,
    encoding: "utf8",
    env: {
      ...process.env,
      TYPESAFE_API_KEY: "",
      LONGRES_CORPUS: relative(join(root, "work", "longres"), corpusPath),
      LONGRES_OUT: relative(join(root, "work", "longres"), outputPath),
    },
  });

  assert.equal(result.status, 3, result.stderr || result.stdout);
  assert.ok(result.stderr.includes("call cap 200 exceeded: 201 rows"));
  assert.equal(existsSync(outputPath), false, "over-cap run must not create a partial result file");
});

// Guard tests for the machine-wide wrapper's repo-scope predicate (offline).
import test from "node:test";
import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { isJevRepoPath } from "./repo-scope.ts";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("repo root and descendants are scoped out", () => {
  assert.equal(isJevRepoPath(REPO, REPO), true);
  assert.equal(isJevRepoPath(resolve(REPO, "work", "sample"), REPO), true);
});

test("prefix siblings and unknown cwd remain outside the repo scope", () => {
  assert.equal(isJevRepoPath(`${REPO}-other`, REPO), false);
  assert.equal(isJevRepoPath(undefined, REPO), false);
});
